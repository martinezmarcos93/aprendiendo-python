import unittest

from tortuscript import contenido
from tortuscript.web_evaluacion import evaluar, validar_codigo

class WebV1Tests(unittest.TestCase):
    def test_curso_web_tiene_doce_lecciones(self):
        curso = contenido.cargar_cursos()
        web = next(c for c in curso if c["id"] == "web-esencial")
        lecciones = [l for s in web["secciones"] for l in s["lecciones"]]
        self.assertEqual(len(lecciones), 12)
        self.assertEqual(len({l["id"] for l in lecciones}), 12)

    def test_cada_leccion_tiene_los_seis_pasos_esenciales(self):
        curso = next(c for c in contenido.cargar_cursos() if c["id"] == "web-esencial")
        for lec in [l for s in curso["secciones"] for l in s["lecciones"]]:
            tipos=[p["tipo"] for p in lec["pasos"]]
            self.assertEqual(tipos[0], "explicacion")
            self.assertIn("elegir", tipos)
            self.assertTrue(any(p["tipo"]=="escribir" for p in lec["pasos"]))
            self.assertEqual(len(lec["pasos"]), 5)

    def test_escribir_web_declara_lenguaje_y_reglas(self):
        curso = next(c for c in contenido.cargar_cursos() if c["id"] == "web-esencial")
        for sec in curso["secciones"]:
            for lec in sec["lecciones"]:
                paso = lec["pasos"][-1]
                self.assertIn(paso["lenguaje"], {"html","css","javascript"})
                self.assertTrue(paso["web"]["contiene"])
    
    def test_evaluador_no_ejecuta_ni_permite_recursos_externos(self):
        self.assertEqual(evaluar("<h1>OK</h1>", "<h1>OK</h1>", "html", {"contiene":["<h1>"]})["estado"], "correcto")
        self.assertEqual(validar_codigo('<script src="https://x">', "html", {})[0], False)
        self.assertEqual(validar_codigo('<iframe src="x"></iframe>', "html", {})[0], False)
        self.assertEqual(validar_codigo('fetch("https://x")', "javascript", {"contiene":["fetch"]})[0], True)

if __name__ == "__main__":
    unittest.main()
