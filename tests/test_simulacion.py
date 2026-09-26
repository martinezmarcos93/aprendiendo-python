"""Partes puras de herramientas/simular_chicos.py (la simulación en sí necesita Playwright y un servidor)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "herramientas"))
try:
    import simular_chicos as sim
except ImportError:                      # jugar_cursos importa playwright recién al ejecutar: esto no debería pasar
    sim = None


@unittest.skipIf(sim is None, "no se pudo importar el simulador")
class TestSimulador(unittest.TestCase):
    def test_los_errores_tipicos_cambian_la_solucion(self):
        self.assertEqual(sim.con_error('mostrar "Hola"'), 'mostrar Hola"')          # comillas sin abrir
        self.assertEqual(sim.con_error("avanzar 100"), "avanzar 101")               # un número cambiado
        self.assertEqual(sim.con_error("mostrar x"), "mostar x")                    # palabra mal escrita

    def test_los_perfiles_son_variados_y_validos(self):
        from tortuscript import progreso
        self.assertGreaterEqual(len(sim.PERFILES), 5)
        self.assertLessEqual(len(sim.PERFILES), 10)
        for p in sim.PERFILES:
            self.assertIn(p["experiencia"], progreso.EXPERIENCIAS)
            self.assertIn(p["entrada"], (None, progreso.PUNTOS_DE_ENTRADA.get(p["experiencia"])))
            for ajuste, valor in p["ajustes"].items():
                self.assertIn(valor, progreso.AJUSTES[ajuste])
        self.assertTrue({"solo teclado", "se rinde rápido", "usa pistas"} <= {p["estilo"] for p in sim.PERFILES})

    def test_la_auditoria_de_contenido_devuelve_listas(self):
        sin_pista, largos = sim.auditar_contenido()
        self.assertIsInstance(sin_pista, list)
        self.assertIsInstance(largos, list)


if __name__ == "__main__":
    unittest.main()
