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
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.tmp)

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
        self.assertIn("tortu_session=", login.headers.get("Set-Cookie", ""))

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


if __name__ == "__main__":
    unittest.main()
