"""Pruebas del adaptador que conecta el runtime educativo con ChildProfile."""
import shutil
import tempfile
import unittest
from pathlib import Path

from tortuscript.acceso import AccesoProducto
from tortuscript.auth import AuthRepository
from tortuscript.cuentas import CuentaRepository
from tortuscript.perfil_educativo import PerfilEducativoService, ContextoEducativoError
from tortuscript.progreso_runtime import RuntimeEducativoChildProfile
from tortuscript.progreso_childprofile import ProgresoChildProfile

class RuntimeEducativoChildProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=Path(tempfile.mkdtemp())
        self.db=self.tmp/"cuentas.sqlite3"
        self.cuentas=CuentaRepository(self.db); self.cuentas.ensure_schema()
        self.auth=AuthRepository(self.db); self.auth.ensure_schema()
        self.cuenta=self.cuentas.crear_account("adulto@example.com")
        self.auth.set_password(self.cuenta.id,"una-clave-larga-123")
        self.auth.marcar_verificada(self.cuenta.id)
        self.ana=self.cuentas.crear_child_profile(self.cuenta.id,"Ana")
        self.beto=self.cuentas.crear_child_profile(self.cuenta.id,"Beto")
        self.session,_,_=self.auth.create_session(self.cuenta.id)
        self.auth.select_profile(self.session,self.ana.id)
        service=PerfilEducativoService(self.cuentas,self.auth,ProgresoChildProfile(self.tmp/"progreso"),AccesoProducto(self.cuentas))
        self.runtime=RuntimeEducativoChildProfile(service)

    def tearDown(self): shutil.rmtree(self.tmp)

    def test_runtime_nuevo_arranca_con_esquema_educativo(self):
        data=self.runtime.cargar(self.session)
        self.assertEqual(data["version"],11)
        self.assertEqual(data["_perfil"],self.ana.id)

    def test_runtime_guarda_y_recupera_usando_childprofile(self):
        data=self.runtime.cargar(self.session)
        data["xp_total"]=42
        self.runtime.guardar(self.session,data)
        data2=self.runtime.cargar(self.session)
        self.assertEqual(data2["xp_total"],42)

    def test_no_puede_guardar_con_otro_propietario(self):
        data=self.runtime.cargar(self.session)
        data["_perfil"]=self.beto.id
        with self.assertRaises(ContextoEducativoError): self.runtime.guardar(self.session,data)

    def test_perfiles_quedan_aislados(self):
        data=self.runtime.cargar(self.session); data["xp_total"]=10; self.runtime.guardar(self.session,data)
        self.auth.select_profile(self.session,self.beto.id)
        data=self.runtime.cargar(self.session); self.assertEqual(data["xp_total"],0)
        data["xp_total"]=90; self.runtime.guardar(self.session,data)
        self.auth.select_profile(self.session,self.ana.id)
        self.assertEqual(self.runtime.cargar(self.session)["xp_total"],10)

if __name__=="__main__": unittest.main()