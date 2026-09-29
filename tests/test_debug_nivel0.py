import unittest
from tortuscript import contenido
from tortuscript.validacion import validar_curso, ERROR

class TestDebugNivel0(unittest.TestCase):
    def test_muestra(self):
        curso=contenido.cargar_curso("alfabetizacion-digital")
        for h in validar_curso(curso):
            if h.nivel == ERROR:
                print("DEBUG_ERROR", h)
        self.assertTrue(False)

if __name__ == "__main__":
    unittest.main()
