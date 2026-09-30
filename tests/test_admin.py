"""Pruebas de la cuenta administrativa y su bypass comercial explícito."""
import shutil
import tempfile
import unittest
from pathlib import Path

from tortuscript.acceso import AccesoProducto
from tortuscript.auth import AuthRepository
from tortuscript.cuentas import CuentaRepository


class AdminAccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.db = self.tmp / "cuentas.sqlite3"
        self.cuentas = CuentaRepository(self.db)
        self.cuentas.ensure_schema()
        self.auth = AuthRepository(self.db)
        self.auth.ensure_schema()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_admin_verificado_y_con_acceso_comercial_total(self):
        cuenta = self.cuentas.crear_account("admin@example.com")
        self.cuentas.establecer_role(cuenta.id, "admin")
        self.auth.set_password(cuenta.id, "una-clave-larga-123")
        self.auth.marcar_verificada(cuenta.id)
        perfil = self.cuentas.crear_child_profile(cuenta.id, "Admin")

        fila = self.auth.verify_password("admin@example.com", "una-clave-larga-123")
        self.assertEqual(fila["id"], cuenta.id)
        self.assertEqual(fila["role"], "admin")

        acceso = AccesoProducto(self.cuentas)
        self.assertTrue(acceso.puede_acceder(perfil.id, "tortuscript-premium"))
        self.assertTrue(acceso.puede_acceder(perfil.id, "croco-script"))
        self.assertTrue(acceso.puede_acceder(perfil.id, "producto-futuro"))

    def test_cuenta_adulta_normal_no_recibe_bypass(self):
        cuenta = self.cuentas.crear_account("adulto@example.com")
        perfil = self.cuentas.crear_child_profile(cuenta.id, "Alumno")
        acceso = AccesoProducto(self.cuentas)
        self.assertFalse(acceso.puede_acceder(perfil.id, "tortuscript-premium"))


if __name__ == "__main__":
    unittest.main()
