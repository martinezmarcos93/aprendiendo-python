"""herramientas/construir.py: una sola configuración, detección o elección del sistema y un instalador por sistema.
(La construcción real con PyInstaller se prueba a mano: tarda y necesita el entorno de desarrollo.)"""
import os
import sys
import tarfile
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "herramientas"))
import construir  # noqa: E402


class TestElegirSistema(unittest.TestCase):
    def test_detecta_o_acepta_el_mismo(self):
        self.assertEqual(construir.elegir_sistema(None, "linux"), "linux")
        self.assertEqual(construir.elegir_sistema("windows", "windows"), "windows")

    def test_explica_si_se_pide_otro_sistema_o_uno_desconocido(self):
        with self.assertRaises(SystemExit) as ctx:
            construir.elegir_sistema("windows", "linux")
        self.assertIn("corré este comando en windows", str(ctx.exception))
        with self.assertRaises(SystemExit):
            construir.elegir_sistema("amiga", "linux")


class TestConfiguracionUnica(unittest.TestCase):
    def test_mismos_argumentos_en_todos_los_sistemas_salvo_el_separador(self):
        args = construir.argumentos_pyinstaller(Path("/tmp/trabajo"))
        for esperado in ("--onedir", "--console", "--noconfirm", "tortuscript.worker"):
            self.assertIn(esperado, args)
        self.assertNotIn("--onefile", args)            # el worker no puede escribir en disco: nada que descomprimir
        datos = [args[i + 1] for i, a in enumerate(args) if a == "--add-data"]
        self.assertEqual(len(datos), len(construir.DATOS))
        self.assertTrue(all(os.pathsep in d for d in datos))


class TestInstaladores(unittest.TestCase):
    def test_cada_sistema_trae_su_instalador_que_comprueba_el_sistema(self):
        linux = construir.archivos_del_instalador("linux", "v")
        self.assertIn('uname -s)" != "Linux"', linux["instalar.sh"])
        self.assertIn("NO borra el progreso", linux["desinstalar.sh"])
        windows = construir.archivos_del_instalador("windows", "v")
        self.assertIn("Windows_NT", windows["instalar.bat"])
        self.assertIn("\r\n", windows["instalar.bat"])
        self.assertTrue(windows["accesos.ps1"].startswith("﻿"))
        self.assertIn('uname -s)" != "Darwin"', construir.archivos_del_instalador("macos", "v")["instalar.command"])
        for sistema in construir.SISTEMAS:
            self.assertIn("No hace falta internet", construir.archivos_del_instalador(sistema, "v")["LEEME.txt"])
            self.assertNotIn("\r", construir.archivos_del_instalador("linux", "v")["instalar.sh"])

    def test_nombre_del_paquete(self):
        with mock.patch.object(construir, "arquitectura", return_value="x86_64"):
            self.assertEqual(construir.nombre_del_paquete("linux", date(2026, 9, 26)), "TortuScript-20260926-linux-x86_64.tar.gz")
            self.assertEqual(construir.nombre_del_paquete("windows", date(2026, 9, 26)), "TortuScript-20260926-windows-x86_64.zip")


class TestEmpaquetar(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.programa = base / "TortuScript"
        (self.programa / "_internal").mkdir(parents=True)
        (self.programa / "TortuScript").write_text("binario", encoding="utf-8")
        (self.programa / "_internal" / "dato.txt").write_text("x", encoding="utf-8")
        self.salida = base / "salida"

    def tearDown(self):
        self._tmp.cleanup()

    def test_linux_tar_con_instalador_ejecutable_y_sha256(self):
        ruta = construir.empaquetar("linux", self.programa, self.salida, "v", date(2026, 9, 26))
        with tarfile.open(ruta) as tar:
            nombres = tar.getnames()
            self.assertEqual(tar.getmember("TortuScript-linux/instalar.sh").mode & 0o111, 0o111)
        self.assertIn("TortuScript-linux/TortuScript/_internal/dato.txt", nombres)
        self.assertTrue(Path(str(ruta) + ".sha256").read_text(encoding="utf-8").endswith(f"{ruta.name}\n"))

    def test_windows_y_macos_zip(self):
        for sistema, instalador in (("windows", "instalar.bat"), ("macos", "instalar.command")):
            with zipfile.ZipFile(construir.empaquetar(sistema, self.programa, self.salida, "v", date(2026, 9, 26))) as z:
                self.assertIn(f"TortuScript-{sistema}/{instalador}", z.namelist())
                self.assertIn(f"TortuScript-{sistema}/TortuScript/TortuScript", z.namelist())


if __name__ == "__main__":
    unittest.main()
