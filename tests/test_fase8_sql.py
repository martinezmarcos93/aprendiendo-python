"""Cobertura curricular y de seguridad de Fase 8 — SQL V1."""

import json
import unittest
from pathlib import Path

from tortuscript.sql_evaluacion import evaluar, ejecutar, validar_consulta
from tortuscript.validacion import ERROR, validar_curso


ROOT = Path(__file__).resolve().parents[1]
CURSO = ROOT / "contenido" / "cursos" / "sql-fundamentos.json"
DATASET = "mundo-fantasia"


class TestSQLV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curso = json.loads(CURSO.read_text(encoding="utf-8"))
        cls.lecciones = [l for s in cls.curso["secciones"] for l in s["lecciones"]]

    def test_curso_tiene_ocho_lecciones_y_cubre_adr(self):
        self.assertEqual(len(cls.lecciones), 8)
        texto = " ".join(p.get("texto", "") for l in self.lecciones for p in l["pasos"])
        texto += " " .join(l["titulo"] for l in self.lecciones)
        self.assertIn("tablas", texto.lower())
        self.assertTrue(any("JOIN" in p.get("codigo", "") for l in self.lecciones for p in l["pasos"]))
        self.assertTrue(any("GROUP BY" in p.get("codigo", "") for l in self.lecciones for p in l["pasos"]))

    def test_todos_los_ejercicios_de_escritura_son_sql(self):
        ejercicios = [p for l in self.lecciones for p in l["pasos"] if p["tipo"] == "escribir"]
        self.assertEqual(len(ejercicios), 8)
        for paso in ejercicios:
            self.assertEqual(paso["lenguaje"], "sql")
            self.assertEqual(paso["sql_dataset"], DATASET)
            self.assertTrue(paso["solucion"])

    def test_validador_de_contenido_no_encuentra_errores(self):
        errores = [h for h in validar_curso(self.curso) if h.nivel == ERROR]
        self.assertEqual(errores, [], "\n".join(str(h) for h in errores))

    def test_consultas_basicas(self):
        r = ejecutar("SELECT nombre FROM criaturas WHERE reino = 'Bosque' ORDER BY nombre;", DATASET)
        self.assertTrue(r["ok"], r["mensaje"])
        self.assertEqual(r["columnas"], ["nombre"])
        self.assertEqual(r["filas"], [["Lobo"], ["Zorro"]])

    def test_join_y_agregacion(self):
        join = ejecutar(
            "SELECT criaturas.nombre, guardianes.guarida "
            "FROM criaturas JOIN guardianes ON criaturas.id = guardianes.criatura_id "
            "ORDER BY criaturas.id;",
            DATASET,
        )
        self.assertTrue(join["ok"], join["mensaje"])
        self.assertEqual(join["filas"], [["Lobo", "Bosque Norte"], ["Dragón", "Cima Roja"], ["Sirena", "Bahía Azul"]])
        agg = ejecutar("SELECT reino, COUNT(*) AS cantidad FROM criaturas GROUP BY reino ORDER BY reino;", DATASET)
        self.assertTrue(agg["ok"], agg["mensaje"])
        self.assertEqual(agg["filas"], [["Bosque", 2], ["Mar", 1], ["Montaña", 2]])

    def test_evaluacion_compara_resultados_y_no_texto(self):
        r = evaluar(
            "SELECT nombre FROM criaturas WHERE nivel >= 4 ORDER BY nombre;",
            "SELECT nombre FROM criaturas WHERE nivel >= 4 ORDER BY nombre;",
            DATASET,
        )
        self.assertEqual(r["estado"], "correcto")
        r = evaluar(
            "SELECT nombre FROM criaturas WHERE nivel >= 4;",
            "SELECT nombre FROM criaturas WHERE nivel >= 4 ORDER BY nombre;",
            DATASET,
        )
        self.assertNotEqual(r["estado"], "correcto")

    def test_sql_solo_lectura_y_sin_recursos_externos(self):
        bloqueadas = [
            "INSERT INTO criaturas VALUES (9, 'X', 'X', 9);",
            "UPDATE criaturas SET nivel = 99;",
            "DELETE FROM criaturas;",
            "DROP TABLE criaturas;",
            "ATTACH DATABASE 'x.db' AS x;",
            "PRAGMA database_list;",
            "SELECT readfile('/etc/passwd');",
        ]
        for codigo in bloqueadas:
            ok, mensaje = validar_consulta(codigo, DATASET)
            self.assertFalse(ok, codigo)
            self.assertTrue(mensaje)

    def test_consulta_multiple_no_permitida(self):
        ok, mensaje = validar_consulta("SELECT nombre FROM criaturas; SELECT nivel FROM criaturas;", DATASET)
        self.assertFalse(ok)
        self.assertIn("una sola", mensaje.lower())


if __name__ == "__main__":
    unittest.main()
