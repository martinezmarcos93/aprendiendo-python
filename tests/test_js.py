"""Corre los tests de JavaScript (tests/js/*.test.mjs) con el corredor que trae Node. Sin Node, se saltean."""
import shutil
import subprocess
import unittest
from pathlib import Path

CARPETA = Path(__file__).resolve().parent / "js"


@unittest.skipUnless(shutil.which("node"), "Node no está instalado")
class TestJavaScript(unittest.TestCase):
    def test_los_tests_de_js_pasan(self):
        archivos = sorted(str(p) for p in CARPETA.glob("*.test.mjs"))
        self.assertTrue(archivos)
        r = subprocess.run(["node", "--test", *archivos], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])


if __name__ == "__main__":
    unittest.main()
