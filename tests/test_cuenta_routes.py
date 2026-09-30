"""Pruebas del boundary HTTP de cuenta adulta."""
import shutil
import tempfile
import unittest
from pathlib import Path

from web.app import create_app
from tortuscript.cuentas import CuentaRepository


class CuentaRoutesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.app = create_app(token="test-token")
        self.app.config.update(
            TESTING=True,
            ACCOUNT_DB=self.tmp / "cuentas.sqlite3",
            ACCOUNT_COOKIE_SECURE=False,
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
        repo.marcar_verificada(cuenta.id)

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

        logout = self.client.post("/cuenta/logout", headers={"X-Tortu-CSRF": csrf})
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(self.client.get("/cuenta/me").status_code, 401)


if __name__ == "__main__":
    unittest.main()
