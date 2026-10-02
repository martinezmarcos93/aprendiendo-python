"""Pruebas del boundary HTTP de cuenta adulta."""
import shutil
import tempfile
import unittest
from pathlib import Path

from web.app import create_app
from tortuscript.auth import AuthRepository
from tortuscript.cuentas import CuentaRepository


class CuentaRoutesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.app = create_app(token="test-token")
        self.app.config.update(
            TESTING=True,
            ACCOUNT_DB=self.tmp / "cuentas.sqlite3",
            ACCOUNT_COOKIE_SECURE=False,
            PROGRESS_DIR=self.tmp / "progreso_perfiles",
        )
        self.emails = []
        self.app.config["ACCOUNT_EMAIL_SENDER"] = lambda **payload: self.emails.append(payload)
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_api_valida_token_antes_de_resolver_la_sesion_educativa(self):
        # El token de la app local y la sesión de cuenta son controles distintos.
        # Sin token, la petición debe rechazarse por el gateway; con token pero sin
        # sesión, debe rechazarse por identidad educativa.
        sin_token = self.client.get("/api/estado")
        self.assertEqual(sin_token.status_code, 403)

        con_token_sin_sesion = self.client.get(
            "/api/estado", headers={"X-Tortu-Token": "test-token"}
        )
        self.assertEqual(con_token_sin_sesion.status_code, 401)

    def test_gateway_web_redirige_al_login_y_perfil(self):
        inicio = self.client.get("/", follow_redirects=False)
        self.assertEqual(inicio.status_code, 302)
        self.assertIn("/cuenta/ingresar", inicio.headers["Location"])

        login_page = self.client.get("/cuenta/ingresar")
        self.assertEqual(login_page.status_code, 200)
        self.assertIn("Ingresar a TortuScript", login_page.get_data(as_text=True))

        registro_page = self.client.get("/cuenta/registrar")
        self.assertEqual(registro_page.status_code, 200)
        self.assertIn("Crear cuenta adulta", registro_page.get_data(as_text=True))

    def test_registro_queda_pendiente_de_verificacion(self):
        r = self.client.post("/cuenta/registro", json={
            "email": "adulto@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(r.status_code, 202)
        self.assertEqual(r.json["estado"], "pendiente_verificacion")

        login = self.client.post("/cuenta/login", json={
            "email": "adulto@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(login.status_code, 401)

    def test_login_cookie_me_csrf_perfil_y_logout(self):
        self.client.post("/cuenta/registro", json={
            "email": "adulto@example.com",
            "password": "una-clave-larga-123",
        })
        repo = CuentaRepository(self.tmp / "cuentas.sqlite3")
        repo.ensure_schema()
        cuenta = repo.obtener_account("acc_" + __import__("hashlib").sha256("adulto@example.com".encode()).hexdigest()[:24])
        AuthRepository(self.tmp / "cuentas.sqlite3").marcar_verificada(cuenta.id)

        login = self.client.post("/cuenta/login", json={
            "email": "adulto@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(login.status_code, 200)
        csrf = login.json["csrf"]
        cookies = "\\n".join(login.headers.getlist("Set-Cookie"))
        self.assertIn("tortu_session=", cookies)
        self.assertIn("tortu_csrf=", cookies)

        me = self.client.get("/cuenta/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json["cuenta"]["email"], "adulto@example.com")
        self.assertEqual(me.json["perfiles"], [])

        bad = self.client.post("/cuenta/perfiles", json={"nombre": "Ana"})
        self.assertEqual(bad.status_code, 403)

        created = self.client.post(
            "/cuenta/perfiles",
            json={"nombre": "Ana"},
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json["perfil"]["nombre"], "Ana")

        me2 = self.client.get("/cuenta/me")
        self.assertEqual([p["nombre"] for p in me2.json["perfiles"]], ["Ana"])

        selected = self.client.post(
            "/cuenta/perfil",
            json={"perfil_id": created.json["perfil"]["id"]},
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(selected.status_code, 200)
        self.assertEqual(selected.json["perfil_activo"], created.json["perfil"]["id"])

        perfiles_api = self.client.get("/api/perfiles", headers={"X-Tortu-Token": "test-token"})
        self.assertEqual(perfiles_api.status_code, 200)
        self.assertEqual(perfiles_api.json["modo"], "cuenta")
        self.assertEqual(perfiles_api.json["perfiles"][0]["id"], created.json["perfil"]["id"])

        me3 = self.client.get("/cuenta/me")
        self.assertEqual(me3.json["perfil_activo"], created.json["perfil"]["id"])

        progress = {
            "contract_version": 1,
            "profile_id": created.json["perfil"]["id"],
            "updated_at": "2026-09-30T12:00:00+00:00",
            "data": {"xp_total": 25},
        }
        saved = self.client.put(
            "/cuenta/progreso",
            json=progress,
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(saved.status_code, 200)

        loaded = self.client.get("/cuenta/progreso")
        self.assertEqual(loaded.status_code, 200)
        self.assertEqual(loaded.json["progreso"]["data"]["xp_total"], 25)

        acceso = self.client.get("/cuenta/acceso?producto=tortuscript-premium")
        self.assertEqual(acceso.status_code, 200)
        self.assertFalse(acceso.json["permitido"])

        repo.establecer_entitlement(cuenta.id, "tortuscript-premium", True, "payment")
        acceso2 = self.client.get("/cuenta/acceso?producto=tortuscript-premium")
        self.assertTrue(acceso2.json["permitido"])

        # Un snapshot de otro perfil no puede escribirse sobre el perfil activo.
        otro = self.client.post(
            "/cuenta/perfiles",
            json={"nombre": "Beto"},
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(otro.status_code, 201)
        bad_progress = dict(progress, profile_id=otro.json["perfil"]["id"])
        rejected = self.client.put(
            "/cuenta/progreso",
            json=bad_progress,
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(rejected.status_code, 400)

        logout = self.client.post("/cuenta/logout", headers={"X-Tortu-CSRF": csrf})
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(self.client.get("/cuenta/me").status_code, 401)



    def test_cuenta_perfil_activo_abre_onboarding_y_progreso_persiste(self):
        # Recorrido integrado mínimo del producto actual: cuenta adulta, perfil,
        # sesión educativa, primera página y persistencia asociada al perfil.
        registro = self.client.post("/cuenta/registro", json={
            "email": "flujo@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(registro.status_code, 202)

        repo = CuentaRepository(self.tmp / "cuentas.sqlite3")
        repo.ensure_schema()
        cuenta_id = "acc_" + __import__("hashlib").sha256(
            "flujo@example.com".encode()
        ).hexdigest()[:24]
        AuthRepository(self.tmp / "cuentas.sqlite3").marcar_verificada(cuenta_id)

        login = self.client.post("/cuenta/login", json={
            "email": "flujo@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(login.status_code, 200)
        csrf = login.json["csrf"]

        creado = self.client.post(
            "/cuenta/perfiles",
            json={"nombre": "Perfil de prueba"},
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(creado.status_code, 201)
        perfil_id = creado.json["perfil"]["id"]

        seleccionado = self.client.post(
            "/cuenta/perfil",
            json={"perfil_id": perfil_id},
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(seleccionado.status_code, 200)

        inicio = self.client.get("/", follow_redirects=False)
        self.assertEqual(inicio.status_code, 302)
        self.assertIn("/bienvenida", inicio.headers["Location"])
        bienvenida = self.client.get("/bienvenida")
        self.assertEqual(bienvenida.status_code, 200)

        guardado = self.client.put(
            "/cuenta/progreso",
            json={
                "contract_version": 1,
                "profile_id": perfil_id,
                "updated_at": "2026-10-02T12:00:00+00:00",
                "data": {"xp_total": 37},
            },
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(guardado.status_code, 200)

        recuperado = self.client.get("/cuenta/progreso")
        self.assertEqual(recuperado.status_code, 200)
        self.assertEqual(recuperado.json["perfil"]["id"], perfil_id)
        self.assertEqual(recuperado.json["progreso"]["data"]["xp_total"], 37)

    def test_aislamiento_entre_cuentas_para_perfiles_y_progreso(self):
        for email in ("a@example.com", "b@example.com"):
            respuesta = self.client.post("/cuenta/registro", json={
                "email": email,
                "password": "una-clave-larga-123",
            })
            self.assertEqual(respuesta.status_code, 202)

        repo = CuentaRepository(self.tmp / "cuentas.sqlite3")
        repo.ensure_schema()
        auth = AuthRepository(self.tmp / "cuentas.sqlite3")
        for email in ("a@example.com", "b@example.com"):
            cuenta = repo.obtener_account(
                "acc_" + __import__("hashlib").sha256(email.encode()).hexdigest()[:24]
            )
            auth.marcar_verificada(cuenta.id)

        cliente_a = self.app.test_client()
        cliente_b = self.app.test_client()
        login_a = cliente_a.post("/cuenta/login", json={
            "email": "a@example.com",
            "password": "una-clave-larga-123",
        })
        login_b = cliente_b.post("/cuenta/login", json={
            "email": "b@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(login_a.status_code, 200)
        self.assertEqual(login_b.status_code, 200)
        csrf_a = login_a.json["csrf"]
        csrf_b = login_b.json["csrf"]

        perfil_a = cliente_a.post(
            "/cuenta/perfiles",
            json={"nombre": "Perfil A"},
            headers={"X-Tortu-CSRF": csrf_a},
        )
        perfil_b = cliente_b.post(
            "/cuenta/perfiles",
            json={"nombre": "Perfil B"},
            headers={"X-Tortu-CSRF": csrf_b},
        )
        self.assertEqual(perfil_a.status_code, 201)
        self.assertEqual(perfil_b.status_code, 201)
        pid_a = perfil_a.json["perfil"]["id"]
        pid_b = perfil_b.json["perfil"]["id"]

        seleccionado_b = cliente_b.post(
            "/cuenta/perfil",
            json={"perfil_id": pid_b},
            headers={"X-Tortu-CSRF": csrf_b},
        )
        self.assertEqual(seleccionado_b.status_code, 200)

        seleccionado_a = cliente_a.post(
            "/cuenta/perfil",
            json={"perfil_id": pid_a},
            headers={"X-Tortu-CSRF": csrf_a},
        )
        self.assertEqual(seleccionado_a.status_code, 200)

        cruzado = cliente_a.post(
            "/cuenta/perfil",
            json={"perfil_id": pid_b},
            headers={"X-Tortu-CSRF": csrf_a},
        )
        self.assertEqual(cruzado.status_code, 403)

        snapshot = {
            "contract_version": 1,
            "profile_id": pid_b,
            "updated_at": "2026-09-30T12:00:00+00:00",
            "data": {"xp_total": 999},
        }
        escritura_cruzada = cliente_a.put(
            "/cuenta/progreso",
            json=snapshot,
            headers={"X-Tortu-CSRF": csrf_a},
        )
        self.assertEqual(escritura_cruzada.status_code, 400)

        acceso_b = cliente_b.get("/cuenta/acceso?producto=tortuscript-premium")
        self.assertEqual(acceso_b.status_code, 200)
        self.assertFalse(acceso_b.json["permitido"])

        repo.establecer_entitlement(
            "acc_" + __import__("hashlib").sha256("b@example.com".encode()).hexdigest()[:24],
            "tortuscript-premium",
            True,
            "payment",
        )
        acceso_b_premium = cliente_b.get("/cuenta/acceso?producto=tortuscript-premium")
        self.assertTrue(acceso_b_premium.json["permitido"])

        # La sesión de A no puede observar el entitlement de B porque no puede seleccionar su perfil.
        acceso_a = cliente_a.get("/cuenta/acceso?producto=tortuscript-premium")
        self.assertFalse(acceso_a.json["permitido"])

    def test_runtime_educativo_registra_xp_leccion_practica_y_proyecto(self):
        self.client.post("/cuenta/registro", json={
            "email": "runtime@example.com",
            "password": "una-clave-larga-123",
        })
        repo = CuentaRepository(self.tmp / "cuentas.sqlite3")
        repo.ensure_schema()
        cuenta = repo.obtener_account("acc_" + __import__("hashlib").sha256("runtime@example.com".encode()).hexdigest()[:24])
        AuthRepository(self.tmp / "cuentas.sqlite3").marcar_verificada(cuenta.id)
        login = self.client.post("/cuenta/login", json={
            "email": "runtime@example.com",
            "password": "una-clave-larga-123",
        })
        csrf = login.json["csrf"]
        perfil = self.client.post("/cuenta/perfiles", json={"nombre": "Ana"}, headers={"X-Tortu-CSRF": csrf})
        pid = perfil.json["perfil"]["id"]
        self.client.post("/cuenta/perfil", json={"perfil_id": pid}, headers={"X-Tortu-CSRF": csrf})

        ejercicio = self.client.post("/cuenta/runtime/ejercicio", json={
            "indice": 0, "estrellas": 3, "xp_ganado": 10
        }, headers={"X-Tortu-CSRF": csrf})
        self.assertEqual(ejercicio.status_code, 200)

        leccion = self.client.post("/cuenta/runtime/leccion/paso", json={
            "leccion_id": "leccion-runtime", "indice": 0, "xp": 5,
            "perfecto": True, "total_pasos": 1, "estrellas": 3
        }, headers={"X-Tortu-CSRF": csrf})
        self.assertEqual(leccion.status_code, 200)
        self.assertTrue(leccion.json["resultado"]["completa"])

        practica = self.client.post("/cuenta/runtime/practica", json={
            "leccion_id": "leccion-runtime", "paso": 0, "acierto": True
        }, headers={"X-Tortu-CSRF": csrf})
        self.assertEqual(practica.status_code, 200)

        proyecto = self.client.post("/cuenta/runtime/proyectos", json={
            "nombre": "Mi proyecto", "tipo": "experimentar", "codigo": "print('hola')"
        }, headers={"X-Tortu-CSRF": csrf})
        self.assertEqual(proyecto.status_code, 200)

        listado = self.client.get("/cuenta/runtime/proyectos")
        self.assertEqual(listado.status_code, 200)
        self.assertEqual(len(listado.json["proyectos"]), 1)

        progreso = self.client.get("/cuenta/runtime/progreso")
        self.assertEqual(progreso.status_code, 200)
        self.assertGreater(progreso.json["progreso"]["data"]["xp_total"], 0)
        self.assertIn("leccion-runtime", progreso.json["progreso"]["data"]["lecciones"])
        self.assertEqual(len(progreso.json["progreso"]["data"]["proyectos"]), 1)


    def test_pantallas_educativas_usan_childprofile_activo(self):
        self.client.post("/cuenta/registro", json={
            "email": "pantallas@example.com",
            "password": "una-clave-larga-123",
        })
        repo = CuentaRepository(self.tmp / "cuentas.sqlite3")
        repo.ensure_schema()
        cuenta = repo.obtener_account("acc_" + __import__("hashlib").sha256(
            "pantallas@example.com".encode()
        ).hexdigest()[:24])
        AuthRepository(self.tmp / "cuentas.sqlite3").marcar_verificada(cuenta.id)

        login = self.client.post("/cuenta/login", json={
            "email": "pantallas@example.com",
            "password": "una-clave-larga-123",
        })
        csrf = login.json["csrf"]
        perfil = self.client.post(
            "/cuenta/perfiles", json={"nombre": "Ana"},
            headers={"X-Tortu-CSRF": csrf},
        )
        pid = perfil.json["perfil"]["id"]
        self.client.post(
            "/cuenta/perfil", json={"perfil_id": pid},
            headers={"X-Tortu-CSRF": csrf},
        )

        api_headers = {"X-Tortu-Token": "test-token"}
        estado = self.client.get("/api/estado", headers=api_headers)
        self.assertEqual(estado.status_code, 200)
        self.assertEqual(estado.json["nombre"], "Ana")

        proyecto = self.client.post(
            "/api/proyectos",
            json={"nombre": "Proyecto UI", "tipo": "experimentar", "codigo": "print(1)"},
            headers=api_headers,
        )
        self.assertEqual(proyecto.status_code, 200)

        snapshot = self.client.get("/cuenta/progreso")
        self.assertEqual(snapshot.status_code, 200)
        data = snapshot.json["progreso"]["data"]
        self.assertEqual(data["config"]["nombre"], "Ana")
        self.assertEqual(len(data["proyectos"]), 1)

        archivos = list((self.tmp / "progreso_perfiles").glob("progreso_*.json"))
        self.assertEqual(len(archivos), 1)
        self.assertIn(pid, archivos[0].name)


    def test_gateway_educativo_llega_a_bienvenida_despues_de_seleccionar_perfil(self):
        self.client.post("/cuenta/registro", json={
            "email": "gateway@example.com",
            "password": "una-clave-larga-123",
        })
        repo = CuentaRepository(self.tmp / "cuentas.sqlite3")
        repo.ensure_schema()
        cuenta = repo.obtener_account("acc_" + __import__("hashlib").sha256(
            "gateway@example.com".encode()
        ).hexdigest()[:24])
        AuthRepository(self.tmp / "cuentas.sqlite3").marcar_verificada(cuenta.id)

        login = self.client.post("/cuenta/login", json={
            "email": "gateway@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(login.status_code, 200)
        csrf = login.json["csrf"]

        perfil = self.client.post(
            "/cuenta/perfiles",
            json={"nombre": "Ana"},
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(perfil.status_code, 201)

        selected = self.client.post(
            "/cuenta/perfil",
            json={"perfil_id": perfil.json["perfil"]["id"]},
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(selected.status_code, 200)

        inicio = self.client.get("/", follow_redirects=False)
        self.assertEqual(inicio.status_code, 302)
        self.assertIn("/bienvenida", inicio.headers["Location"])


    def test_onboarding_web_persiste_en_el_childprofile_activo(self):
        self.client.post("/cuenta/registro", json={
            "email": "onboarding@example.com",
            "password": "una-clave-larga-123",
        })
        repo = CuentaRepository(self.tmp / "cuentas.sqlite3")
        repo.ensure_schema()
        cuenta = repo.obtener_account("acc_" + __import__("hashlib").sha256(
            "onboarding@example.com".encode()
        ).hexdigest()[:24])
        AuthRepository(self.tmp / "cuentas.sqlite3").marcar_verificada(cuenta.id)

        login = self.client.post("/cuenta/login", json={
            "email": "onboarding@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(login.status_code, 200)
        csrf = login.json["csrf"]

        perfil = self.client.post(
            "/cuenta/perfiles",
            json={"nombre": "Ana"},
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(perfil.status_code, 201)
        pid = perfil.json["perfil"]["id"]

        selected = self.client.post(
            "/cuenta/perfil",
            json={"perfil_id": pid},
            headers={"X-Tortu-CSRF": csrf},
        )
        self.assertEqual(selected.status_code, 200)

        onboarding = self.client.post(
            "/api/onboarding",
            json={"nombre": "Marcos", "experiencia": "nunca", "meta_min": 5},
            headers={"X-Tortu-Token": "test-token"},
        )
        self.assertEqual(onboarding.status_code, 200, onboarding.get_data(as_text=True))
        self.assertTrue(onboarding.json["ok"])

        progreso = self.client.get("/cuenta/progreso")
        self.assertEqual(progreso.status_code, 200)
        data = progreso.json["progreso"]["data"]
        self.assertTrue(data["config"]["onboarding"])
        self.assertEqual(data["config"]["nombre"], "Marcos")
        self.assertEqual(data["config"]["experiencia"], "nunca")
        self.assertEqual(data["config"]["meta_min"], 5)

        inicio = self.client.get("/")
        self.assertEqual(inicio.status_code, 200)


    def test_verificacion_y_recuperacion_http_no_exponen_token(self):
        registro = self.client.post("/cuenta/registro", json={
            "email": "seguridad@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(registro.status_code, 202)
        self.assertNotIn("token", registro.json)
        self.assertEqual(self.emails[0]["tipo"], "verification")
        token = self.emails[0]["token"]

        verificado = self.client.get("/cuenta/verificar-email", query_string={"token": token})
        self.assertEqual(verificado.status_code, 200)

        login = self.client.post("/cuenta/login", json={
            "email": "seguridad@example.com",
            "password": "una-clave-larga-123",
        })
        self.assertEqual(login.status_code, 200)

        recovery = self.client.post("/cuenta/recuperar", json={"email": "seguridad@example.com"})
        self.assertEqual(recovery.status_code, 202)
        self.assertEqual(self.emails[-1]["tipo"], "recovery")
        recovery_token = self.emails[-1]["token"]

        reset = self.client.post("/cuenta/restablecer-password", json={
            "token": recovery_token,
            "password": "otra-clave-larga-456",
        })
        self.assertEqual(reset.status_code, 200)

        login2 = self.client.post("/cuenta/login", json={
            "email": "seguridad@example.com",
            "password": "otra-clave-larga-456",
        })
        self.assertEqual(login2.status_code, 200)

        reused = self.client.post("/cuenta/restablecer-password", json={
            "token": recovery_token,
            "password": "tercera-clave-larga-789",
        })
        self.assertEqual(reused.status_code, 400)


    def test_login_aplica_rate_limit_y_devuelve_retry_after(self):
        self.client.post("/cuenta/registro", json={
            "email": "limit@example.com",
            "password": "una-clave-larga-123",
        })
        for _ in range(10):
            respuesta = self.client.post("/cuenta/login", json={
                "email": "limit@example.com",
                "password": "incorrecta-larga",
            })
            self.assertEqual(respuesta.status_code, 401)
        bloqueado = self.client.post("/cuenta/login", json={
            "email": "limit@example.com",
            "password": "incorrecta-larga",
        })
        self.assertEqual(bloqueado.status_code, 429)
        self.assertIn("Retry-After", bloqueado.headers)

if __name__ == "__main__":
    unittest.main()
