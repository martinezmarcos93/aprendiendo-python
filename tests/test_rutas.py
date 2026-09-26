"""Carpetas por sistema y ejecutable instalado (ADR-015): nada del chico se pierde ni se pisa."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tortuscript import proceso, rutas

RAIZ = Path(__file__).resolve().parent.parent


class TestCarpetas(unittest.TestCase):
    def test_carpeta_de_usuario_por_sistema(self):
        casa = Path("/casa/lua")
        self.assertEqual(rutas.carpeta_de_usuario("windows", {"APPDATA": r"C:\Users\Lua\AppData\Roaming"}, casa),
                         Path(r"C:\Users\Lua\AppData\Roaming") / "TortuScript")
        self.assertEqual(rutas.carpeta_de_usuario("macos", {}, casa), casa / "Library/Application Support/TortuScript")
        self.assertEqual(rutas.carpeta_de_usuario("linux", {}, casa), casa / ".local/share/tortuscript")
        self.assertEqual(rutas.carpeta_de_usuario("linux", {"XDG_DATA_HOME": "/datos"}, casa), Path("/datos/tortuscript"))

    def test_desde_el_codigo_fuente_todo_sigue_junto_al_programa(self):
        with mock.patch.object(sys, "frozen", False, create=True):
            self.assertEqual(rutas.carpeta_de_datos({}), rutas.RAIZ)

    def test_instalado_usa_la_carpeta_del_usuario_y_la_variable_manda(self):
        with mock.patch.object(sys, "frozen", True, create=True):
            self.assertEqual(rutas.carpeta_de_datos({"XDG_DATA_HOME": "/datos"}),
                             rutas.carpeta_de_usuario(entorno={"XDG_DATA_HOME": "/datos"}))
            self.assertEqual(rutas.carpeta_de_datos({"TORTUSCRIPT_DATOS": "/portatil"}), Path("/portatil"))

    def test_sistema_devuelve_uno_conocido(self):
        self.assertIn(rutas.sistema(), ("linux", "windows", "macos"))
        with mock.patch("platform.system", return_value="Darwin"):
            self.assertEqual(rutas.sistema(), "macos")
        with mock.patch("platform.system", return_value="FreeBSD"):
            self.assertEqual(rutas.sistema(), "linux")


class TestCopiarDatosViejos(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.origen, self.destino = base / "programa", base / "datos"
        self.origen.mkdir(); self.destino.mkdir()
        for nombre in ("progreso_lua.json", "progreso_lua.json.bak", "config_tortuscript.json", "otro.txt"):
            (self.origen / nombre).write_text(nombre, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_copia_solo_lo_del_chico_y_no_borra_el_original(self):
        copiados = rutas.copiar_datos_viejos(self.origen, self.destino)
        self.assertEqual(copiados, ["config_tortuscript.json", "progreso_lua.json", "progreso_lua.json.bak"])
        self.assertTrue((self.origen / "progreso_lua.json").exists())
        self.assertFalse((self.destino / "otro.txt").exists())

    def test_nunca_pisa_un_progreso_que_ya_esta(self):
        (self.destino / "progreso_tomi.json").write_text("mío", encoding="utf-8")
        self.assertEqual(rutas.copiar_datos_viejos(self.origen, self.destino), [])
        self.assertFalse((self.destino / "progreso_lua.json").exists())

    def test_misma_carpeta_no_hace_nada(self):
        self.assertEqual(rutas.copiar_datos_viejos(self.origen, self.origen), [])


class TestWorkerInstalado(unittest.TestCase):
    def test_comando_del_worker(self):
        with mock.patch.object(sys, "frozen", False, create=True):
            self.assertEqual(proceso.comando_worker(), [sys.executable, "-m", "tortuscript.worker"])
        with mock.patch.object(sys, "frozen", True, create=True):
            self.assertEqual(proceso.comando_worker(), [sys.executable, "--worker"])

    def test_el_lanzador_atiende_worker_sin_abrir_el_servidor(self):
        r = subprocess.run([sys.executable, str(RAIZ / "iniciar_web.py"), "--worker"],
                           input=json.dumps({"op": "ejecutar", "fuente": 'mostrar "hola"'}),
                           capture_output=True, text=True, encoding="utf-8", timeout=30, cwd=str(RAIZ))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["salida_programa"], "hola\n")


if __name__ == "__main__":
    unittest.main()
