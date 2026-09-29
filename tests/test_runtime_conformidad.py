"""Conformidad mínima entre el runtime educativo y el runtime AST de TortuGame."""
import unittest

from tortuscript.executor import CodigoNoPermitido, validar_codigo
from tortuscript.juego_ast import arbol_del_juego


class TestConformidadRuntime(unittest.TestCase):
    def test_ambos_runtimes_aceptan_programa_basico(self):
        fuente = "x = 2\nprint(x)"
        validar_codigo(fuente)
        arbol = arbol_del_juego(fuente)
        self.assertEqual(arbol["k"], "programa")

    def test_ambos_runtimes_rechazan_importacion(self):
        fuente = "import math"
        with self.assertRaises(CodigoNoPermitido):
            validar_codigo(fuente)
        with self.assertRaises(CodigoNoPermitido):
            arbol_del_juego(fuente)

    def test_ambos_runtimes_rechazan_atributo_interno(self):
        fuente = "x = ()" + ".__class__"
        with self.assertRaises(CodigoNoPermitido):
            validar_codigo(fuente)
        with self.assertRaises(CodigoNoPermitido):
            arbol_del_juego(fuente)

    def test_ambos_runtimes_rechazan_nombre_interno(self):
        fuente = "_" + "_secreto = 1"
        with self.assertRaises(CodigoNoPermitido):
            validar_codigo(fuente)
        with self.assertRaises(CodigoNoPermitido):
            arbol_del_juego(fuente)


if __name__ == "__main__":
    unittest.main()
