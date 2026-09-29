import unittest
from tortuscript.translator import TraductorTortuScript

class TestDebugNivel0(unittest.TestCase):
    def test_muestra(self):
        fuente='programa es "calculadora"\nmostrar programa'
        print("DEBUG_NIVEL0", repr(TraductorTortuScript().traducir_codigo(fuente)))
        self.assertTrue(False)

if __name__ == "__main__":
    unittest.main()
