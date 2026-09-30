"""Cobertura curricular de Fase 6 — Python V1."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURSO = ROOT / "contenido" / "cursos" / "python-real.json"


class TestPythonV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curso = json.loads(CURSO.read_text(encoding="utf-8"))
        cls.lecciones = [l for s in cls.curso["secciones"] for l in s["lecciones"]]

    def test_itinerario_python_tiene_los_bloques_fundamentales(self):
        ids = {l["id"] for l in self.lecciones}
        self.assertTrue({"py-print", "py-input", "py-if", "py-for", "py-def", "py-final",
                         "py-datos", "py-listas", "py-problemas"} <= ids)

    def test_cada_leccion_tiene_explicacion_y_actividad_de_codigo(self):
        for leccion in self.lecciones:
            tipos = {p["tipo"] for p in leccion["pasos"]}
            self.assertIn("explicacion", tipos, leccion["id"])
            self.assertIn("escribir", tipos, leccion["id"])

    def test_nuevas_unidades_cubren_datos_listas_y_resolucion(self):
        por_id = {l["id"]: l for l in self.lecciones}
        self.assertIn("tipo de dato", por_id["py-datos"]["pasos"][0]["texto"].lower())
        self.assertIn("lista", por_id["py-listas"]["pasos"][0]["texto"].lower())
        self.assertIn("problema", por_id["py-problemas"]["pasos"][0]["texto"].lower())

    def test_nuevas_unidades_validan_sin_errores_detallados(self):
        from tortuscript.validacion import ERROR, validar_curso
        errores = [h for h in validar_curso(self.curso) if h.nivel == ERROR]
        self.assertEqual(errores, [], "\n".join(str(h) for h in errores))

    def test_ejercicios_python_declarados_como_python(self):
        for leccion in self.lecciones:
            for paso in leccion["pasos"]:
                if paso["tipo"] == "escribir":
                    self.assertEqual(paso.get("lenguaje"), "python", leccion["id"])

    def test_runtime_reconoce_python_real_nuevo(self):
        from tortuscript.translator import detectar_tipo
        from tortuscript.validacion import _correr
        codigo = 'edad = 12\nnombre = "Luna"\nes_mayor = edad >= 18\nprint(es_mayor)'
        self.assertEqual(detectar_tipo(codigo), "python")
        ejemplos = [
            'frutas = ["manzana", "pera", "banana"]\nprint(frutas[0])',
            'numeros = [3, 8, 5]\nmayores = 0\nfor n in numeros:\n    if n >= 5:\n        mayores = mayores + 1\nprint(mayores)',
        ]
        for ejemplo in ejemplos:
            self.assertEqual(detectar_tipo(ejemplo), "python", ejemplo)
            salida, error, _ = _correr(ejemplo)
            self.assertEqual(error, "", error)
        salida, error, _ = _correr(codigo)
        self.assertEqual(error, "", error)
        self.assertEqual(salida.strip(), "False")
        from tortuscript import contenido
        cargado = contenido.cargar_curso("python-real")
        py_datos = next(l for sec in cargado["secciones"] for l in sec["lecciones"] if l["id"] == "py-datos")
        self.assertEqual(py_datos["pasos"][0]["codigo"], self.lecciones[[l["id"] for l in self.lecciones].index("py-datos")]["pasos"][0]["codigo"])
        from tortuscript.validacion import validar_curso
        errores = [h for h in validar_curso(cargado) if h.nivel == "error"]
        self.assertEqual(errores, [], "\n".join(str(h) for h in errores))

    def test_todo_codigo_de_las_nuevas_unidades_se_puede_ejecutar(self):
        from tortuscript.validacion import _correr
        for leccion in self.lecciones:
            if leccion["id"] not in {"py-datos", "py-listas", "py-problemas"}:
                continue
            for paso in leccion["pasos"]:
                codigo = paso.get("codigo") or paso.get("solucion") or ""
                if paso["tipo"] == "completar":
                    codigo = paso["codigo"]
                    for r in paso.get("respuesta", []):
                        codigo = codigo.replace("___", r, 1)
                elif paso["tipo"] == "ordenar":
                    codigo = "\n".join(paso.get("lineas", []))
                if not codigo.strip():
                    continue
                salida, error, _ = _correr(codigo, paso.get("entradas_prueba"))
                self.assertEqual(error, "", f"{leccion['id']} / {paso['tipo']}: {error} | {codigo!r}")
    def test_nuevos_retos_tienen_soluciones_completas(self):
        for lesson_id in ("py-datos", "py-listas", "py-problemas"):
            leccion = next(l for l in self.lecciones if l["id"] == lesson_id)
            escribir = [p for p in leccion["pasos"] if p["tipo"] == "escribir"]
            self.assertTrue(escribir)
            for paso in escribir:
                self.assertTrue(paso.get("solucion"), lesson_id)


if __name__ == "__main__":
    unittest.main()
