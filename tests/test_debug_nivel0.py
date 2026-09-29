import unittest
from tortuscript import contenido
from tortuscript.validacion import validar_curso, ERROR
from tortuscript.translator import TraductorTortuScript

class TestDebugNivel0(unittest.TestCase):
    def test_debug(self):
        curso=contenido.cargar_curso("alfabetizacion-digital")
        paso=curso["secciones"][0]["lecciones"][0]["pasos"][2]
        print("DEBUG_CODE",repr(paso["codigo"]))
        print("DEBUG_PY",repr(TraductorTortuScript().traducir_codigo(paso["codigo"])))
        for h in validar_curso(curso):
            if h.nivel == ERROR: print("DEBUG_ERROR",h)
        self.assertTrue(False)
