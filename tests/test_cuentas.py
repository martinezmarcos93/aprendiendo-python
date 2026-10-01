"""Pruebas del límite de identidad/comercial, sin autenticar ni cobrar."""
import shutil
import tempfile
import unittest
from pathlib import Path

from tortuscript.cuentas import CuentaError, CuentaRepository, MAX_CHILD_PROFILES


class CuentaRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = CuentaRepository(self.tmp / "cuentas.sqlite3")
        self.repo.ensure_schema()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_crea_cuenta_y_perfiles(self):
        cuenta = self.repo.crear_account(" Adulto@Ejemplo.com ")
        perfiles = [
            self.repo.crear_child_profile(cuenta.id, f"Hijo {i}")
            for i in range(1, 3)
        ]
        self.assertEqual(cuenta.email, "adulto@ejemplo.com")
        self.assertEqual([p.display_name for p in perfiles], ["Hijo 1", "Hijo 2"])
        self.assertEqual(len(self.repo.listar_child_profiles(cuenta.id)), 2)

    def test_un_entitlement_del_account_habilita_a_todos_sus_perfiles(self):
        cuenta = self.repo.crear_account("adulto@example.com")
        ana = self.repo.crear_child_profile(cuenta.id, "Ana")
        beto = self.repo.crear_child_profile(cuenta.id, "Beto")
        self.assertFalse(self.repo.tiene_entitlement_por_perfil(ana.id, "tortuscript-premium"))
        self.repo.establecer_entitlement(cuenta.id, "tortuscript-premium", True, "payment")
        self.assertTrue(self.repo.tiene_entitlement_por_perfil(ana.id, "tortuscript-premium"))
        self.assertTrue(self.repo.tiene_entitlement_por_perfil(beto.id, "tortuscript-premium"))

    def test_no_se_puede_superar_el_limite_de_perfiles(self):
        cuenta = self.repo.crear_account("adulto@example.com")
        for i in range(MAX_CHILD_PROFILES):
            self.repo.crear_child_profile(cuenta.id, f"Perfil {i}")
        with self.assertRaises(CuentaError):
            self.repo.crear_child_profile(cuenta.id, "Perfil extra")

    def test_no_acepta_email_invalido(self):
        with self.assertRaises(CuentaError):
            self.repo.crear_account("no-es-un-email")

    def test_no_duplica_cuenta_ni_nombre_de_perfil(self):
        cuenta = self.repo.crear_account("adulto@example.com")
        with self.assertRaises(CuentaError):
            self.repo.crear_account("ADULTO@example.com")
        self.repo.crear_child_profile(cuenta.id, "Ana")
        with self.assertRaises(CuentaError):
            self.repo.crear_child_profile(cuenta.id, " Ana ")

    def test_esquema_es_reproducible(self):
        self.repo.ensure_schema()
        self.repo.ensure_schema()
        cuenta = self.repo.crear_account("adulto@example.com")
        self.assertIsNotNone(self.repo.obtener_account(cuenta.id))


if __name__ == "__main__":
    unittest.main()
