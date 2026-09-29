import unittest
from tortuscript.translator import TraductorTortuScript
from tortuscript.executor import ejecutar_codigo

class TestDebugNivel0(unittest.TestCase):
    def test_muestra(self):
        fuente='programa es "calculadora"\\nmostrar programa'
        py=TraductorTortuScript().traducir_codigo(fuente)
        print("DEBUG_NIVEL0_PY",repr(py))
        print("DEBUG_NIVEL0_EXEC",repr(ejecutar_codigo(py)))
        self.assertTrue(False)

if __name__ == "__main__":
    unittest.main()
