"""Prueba de nivel del diagnóstico (ADR-004, v2): contenido válido, corrección en el servidor y entradas permitidas."""
import unittest

from tortuscript import diagnostico
from tortuscript.evaluacion import normalizar_salida
from tortuscript.executor import ejecutar_codigo
from tortuscript.translator import TraductorTortuScript
from tortuscript.validacion import _revisar_texto


def correctas():
    return [p["opciones"][p["correcta"]] for p in diagnostico.cargar()["preguntas"]]


class TestContenidoDeLaPrueba(unittest.TestCase):
    def test_cada_pregunta_es_de_una_seccion_distinta_y_en_orden(self):
        inicios = diagnostico.inicios_de_seccion()
        secciones = [p["seccion"] for p in diagnostico.cargar()["preguntas"]]
        self.assertEqual(len(set(secciones)), len(secciones))
        self.assertEqual(secciones, sorted(secciones, key=inicios.index))
        self.assertIn(diagnostico.cargar()["si_acierta_todo"], inicios)

    def test_la_opcion_correcta_es_lo_que_muestra_el_codigo_y_ninguna_otra(self):
        for p in diagnostico.cargar()["preguntas"]:
            if not p.get("codigo"):
                continue
            salida, error, _ = ejecutar_codigo(TraductorTortuScript().traducir_codigo(p["codigo"]))
            self.assertFalse(error, p["codigo"])
            real = normalizar_salida(salida)
            self.assertEqual(normalizar_salida(p["opciones"][p["correcta"]]), real)
            self.assertEqual(sum(normalizar_salida(o) == real for o in p["opciones"]), 1)

    def test_textos_escritos_para_chicos(self):
        hallazgos = []
        for texto in [diagnostico.cargar()["intro"]] + [p["pregunta"] for p in diagnostico.cargar()["preguntas"]]:
            _revisar_texto(texto, "diagnóstico", hallazgos)
        self.assertEqual([h.mensaje for h in hallazgos], [])


class TestRecomendar(unittest.TestCase):
    def test_todo_bien_va_a_desafios_y_el_primer_error_marca_la_entrada(self):
        buenas = correctas()
        self.assertEqual(diagnostico.recomendar(buenas), "saludo-repetido")
        preguntas = diagnostico.cargar()["preguntas"]
        for i, p in enumerate(preguntas):
            respuestas = list(buenas)
            respuestas[i] = next(o for o in p["opciones"] if o != buenas[i])
            self.assertEqual(diagnostico.recomendar(respuestas), p["seccion"])

    def test_respuestas_incompletas(self):
        for mal in (None, [], correctas()[:-1], "7"):
            with self.assertRaises(ValueError):
                diagnostico.recomendar(mal)

    def test_el_navegador_no_recibe_las_correctas(self):
        publicas = diagnostico.preguntas_publicas()
        self.assertNotIn("correcta", str(publicas))
        for pub, orig in zip(publicas["preguntas"], diagnostico.cargar()["preguntas"]):
            self.assertEqual(sorted(pub["opciones"]), sorted(orig["opciones"]))

    def test_entradas_permitidas_por_experiencia(self):
        self.assertEqual(diagnostico.entradas_permitidas("nunca"), set())
        self.assertEqual(diagnostico.entradas_permitidas("poquito"), {"tu-primera-variable"})
        bastante = diagnostico.entradas_permitidas("bastante")
        self.assertNotIn("hola-mundo", bastante)
        self.assertTrue({"si-es-grande", "tu-primera-funcion", "saludo-repetido"} <= bastante)


if __name__ == "__main__":
    unittest.main()
