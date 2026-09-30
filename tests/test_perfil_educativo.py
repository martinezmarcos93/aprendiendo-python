"""Pruebas de la frontera sesión -> perfil -> progreso -> acceso."""
import shutil
import tempfile
import unittest
from pathlib import Path

from tortuscript.acceso import AccesoProducto
from tortuscript.auth import AuthRepository
from tortuscript.cuentas import CuentaRepository
from tortuscript.perfil_educativo import ContextoEducativoError, PerfilEducativoService
from tortuscript.progreso_childprofile import ProgresoChildProfile
from tortuscript.progreso_contrato import nuevo_snapshot


class PerfilEducativoServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.db = self.tmp / "cuentas.sqlite3"
        self.cuentas = CuentaRepository(self.db)
        self.cuentas.ensure_schema()
        self.auth = AuthRepository(self.db)
        self.auth.ensure_schema()
        self.store = ProgresoChildProfile(self.tmp / "progreso")
        self.acceso = AccesoProducto(self.cuentas)
        self.service = PerfilEducativoService(self.cuentas, self.auth, self.store, self.acceso)
        self.cuenta = self.cuentas.crear_account("adulto@example.com")
        self.auth.set_password(self.cuenta.id, "una-clave-larga-123")
        self.auth.marcar_verificada(self.cuenta.id)
        self.ana = self.cuentas.crear_child_profile(self.cuenta.id, "Ana")
        self.beto = self.cuentas.crear_child_profile(self.cuenta.id, "Beto")
        self.session, self.csrf, _ = self.auth.create_session(self.cuenta.id)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _seleccionar(self, perfil):
        self.auth.select_profile(self.session, perfil.id)

    def test_sin_perfil_activo_rechaza_contexto(self):
        with self.assertRaises(ContextoEducativoError):
            self.service.contexto(self.session)

    def test_contexto_usa_el_perfil_seleccionado(self):
        self._seleccionar(self.ana)
        contexto = self.service.contexto(self.session)
        self.assertEqual(contexto.cuenta.id, self.cuenta.id)
        self.assertEqual(contexto.perfil.id, self.ana.id)

    def test_progreso_queda_aislado_por_perfil(self):
        self._seleccionar(self.ana)
        self.service.guardar_progreso(self.session, nuevo_snapshot(self.ana.id, {"xp_total": 10}))
        self._seleccionar(self.beto)
        self.service.guardar_progreso(self.session, nuevo_snapshot(self.beto.id, {"xp_total": 90}))
        self.assertEqual(self.service.cargar_progreso(self.session).data["xp_total"], 90)
        self._seleccionar(self.ana)
        self.assertEqual(self.service.cargar_progreso(self.session).data["xp_total"], 10)

    def test_no_permite_guardar_progreso_de_otro_perfil(self):
        self._seleccionar(self.ana)
        with self.assertRaises(ContextoEducativoError):
            self.service.guardar_progreso(self.session, nuevo_snapshot(self.beto.id, {"xp_total": 999}))

    def test_premium_requiere_entitlement(self):
        self._seleccionar(self.ana)
        with self.assertRaises(ContextoEducativoError):
            self.service.exigir_acceso(self.session, "tortuscript-premium")
        self.cuentas.establecer_entitlement(self.cuenta.id, "tortuscript-premium", True, "payment")
        contexto = self.service.exigir_acceso(self.session, "tortuscript-premium")
        self.assertEqual(contexto.perfil.id, self.ana.id)

    def test_admin_con_perfil_activo_puede_acceder(self):
        self.cuentas.establecer_role(self.cuenta.id, "admin")
        self._seleccionar(self.ana)
        contexto = self.service.exigir_acceso(self.session, "producto-futuro")
        self.assertEqual(contexto.cuenta.role, "admin")

    def test_sesion_invalida_rechaza_contexto(self):
        with self.assertRaises(ContextoEducativoError):
            self.service.contexto("sesion-inexistente")


if __name__ == "__main__":
    unittest.main()