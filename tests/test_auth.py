"""Pruebas de las primitivas de autenticación y sesión server-side."""
import shutil
import tempfile
import unittest
from pathlib import Path

from tortuscript.cuentas import CuentaRepository
from tortuscript.auth import AuthError, AuthRepository


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.db = self.tmp / "cuentas.sqlite3"
        self.cuentas = CuentaRepository(self.db)
        self.cuentas.ensure_schema()
        self.auth = AuthRepository(self.db)
        self.auth.ensure_schema()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_password_se_guarda_como_hash_y_exige_verificacion(self):
        cuenta = self.cuentas.crear_account("adulto@example.com")
        self.auth.set_password(cuenta.id, "una-clave-larga-123")
        with self.assertRaises(AuthError):
            self.auth.verify_password("adulto@example.com", "una-clave-larga-123")
        self.auth.marcar_verificada(cuenta.id)
        fila = self.auth.verify_password("adulto@example.com", "una-clave-larga-123")
        self.assertEqual(fila["id"], cuenta.id)
        with self.assertRaises(AuthError):
            self.auth.verify_password("adulto@example.com", "incorrecta")
        with self.auth._db() as db:
            hash_guardado = db.execute("SELECT password_hash FROM accounts WHERE id=?", (cuenta.id,)).fetchone()[0]
        self.assertNotEqual(hash_guardado, "una-clave-larga-123")
        self.assertTrue(hash_guardado.startswith("scrypt:"))

    def test_sesion_expone_token_solo_al_crearla_y_se_revoca(self):
        cuenta = self.cuentas.crear_account("adulto@example.com")
        sesion, csrf, _ = self.auth.create_session(cuenta.id)
        self.assertIsNotNone(self.auth.get_session(sesion))
        self.assertTrue(self.auth.csrf_ok(sesion, csrf))
        self.assertFalse(self.auth.csrf_ok(sesion, "otro-token"))
        self.auth.revoke(sesion)
        self.assertIsNone(self.auth.get_session(sesion))

    def test_el_hash_de_sesion_no_es_el_token(self):
        cuenta = self.cuentas.crear_account("adulto@example.com")
        sesion, _, _ = self.auth.create_session(cuenta.id)
        with self.auth._db() as db:
            guardado = db.execute("SELECT id_hash FROM sessions").fetchone()[0]
        self.assertNotEqual(guardado, sesion)
        self.assertEqual(len(guardado), 64)


if __name__ == "__main__":
    unittest.main()
