"""Pruebas del acceso comercial por ChildProfile."""
import shutil
import tempfile
import unittest
from pathlib import Path

from tortuscript.acceso import AccesoError, AccesoProducto
from tortuscript.cuentas import CuentaRepository


class AccesoProductoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = CuentaRepository(self.tmp / "cuentas.sqlite3")
        self.repo.ensure_schema()
        cuenta = self.repo.crear_account("adulto@example.com")
        self.ana = self.repo.crear_child_profile(cuenta.id, "Ana")
        self.beto = self.repo.crear_child_profile(cuenta.id, "Beto")
        self.acceso = AccesoProducto(self.repo)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_sin_entitlement_no_hay_acceso(self):
        self.assertFalse(self.acceso.puede_acceder(self.ana.id, "tortuscript-premium"))

    def test_entitlement_del_account_habilita_a_todos_los_perfiles(self):
        cuenta = self.repo.obtener_account(self.ana.account_id)
        self.repo.establecer_entitlement(cuenta.id, "tortuscript-premium", True, "payment")
        self.assertTrue(self.acceso.puede_acceder(self.ana.id, "tortuscript-premium"))
        self.assertTrue(self.acceso.puede_acceder(self.beto.id, "tortuscript-premium"))

    def test_entitlement_de_otro_producto_no_habilita_premium(self):
        cuenta = self.repo.obtener_account(self.ana.account_id)
        self.repo.establecer_entitlement(cuenta.id, "croco-script", True, "payment")
        self.assertFalse(self.acceso.puede_acceder(self.ana.id, "tortuscript-premium"))
        self.assertTrue(self.acceso.puede_acceder(self.ana.id, "croco-script"))

    def test_exigir_acceso_falla_de_forma_explicita(self):
        with self.assertRaises(AccesoError):
            self.acceso.exigir_acceso(self.ana.id, "tortuscript-premium")

    def test_resumen_ignora_entradas_invalidas(self):
        cuenta = self.repo.obtener_account(self.ana.account_id)
        self.repo.establecer_entitlement(cuenta.id, "tortuscript-premium", True, "payment")
        resumen = self.acceso.resumen_acceso(
            self.ana.id,
            ["tortuscript-premium", "croco-script", "", 123],
        )
        self.assertEqual(
            resumen,
            {"tortuscript-premium": True, "croco-script": False},
        )


if __name__ == "__main__":
    unittest.main()
