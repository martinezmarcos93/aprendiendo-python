import json
import unittest
from datetime import date
from pathlib import Path

from tortuscript import catalogo_producto


class Fase10ProductoTests(unittest.TestCase):
    def setUp(self):
        self.p = {
            "lecciones": {},
            "repaso": {},
            "proyectos_integradores": {},
            "xp_total": 0,
        }

    def test_modelo_curricular_tiene_adaptador_para_todas_las_unidades(self):
        self.assertTrue(catalogo_producto.validar_modelo())

    def test_segmentos_no_fijan_premium(self):
        segmentos = catalogo_producto.SEGMENTOS_PRODUCTO
        self.assertEqual(segmentos["premium"]["itinerarios"], [])
        self.assertEqual(catalogo_producto.ESTADO_COMERCIAL_POR_DEFINIR, "por_definir")

    def test_comercial_no_fija_premium(self):
        self.assertEqual(
            catalogo_producto.estado_acceso("python-datos", self.p),
            "por_definir",
        )
        self.assertEqual(
            catalogo_producto.estado_acceso("python-puente", self.p),
            "bloqueado_por_prerrequisito",
        )
        self.assertEqual(
            catalogo_producto.estado_acceso("integrador-ficha-criatura", self.p),
            "bloqueado_por_prerrequisito",
        )

    def test_unidad_puede_pasar_de_pendiente_a_completada(self):
        self.assertEqual(catalogo_producto.estado_unidad("nivel0-programa", self.p)["estado"], "pendiente")
        self.p["lecciones"]["nivel0-programa"] = {"completada": True}
        estado = catalogo_producto.estado_unidad("nivel0-programa", self.p)
        self.assertEqual(estado["estado"], "completada")
        self.assertTrue(estado["estudiada"])

    def test_competencia_se_deriva_del_progreso(self):
        self.p["lecciones"]["nivel0-programa"] = {"completada": True}
        competencias = catalogo_producto.competencias(self.p)
        self.assertTrue(competencias["reconocer_programas"]["dominada"])

    def test_repaso_se_refleja_en_competencia(self):
        self.p["lecciones"]["nivel0-programa"] = {"completada": True}
        self.p["repaso"]["alfabetizacion-digital:nivel0-programa"] = {
            "proximo": str(date.today())
        }
        competencias = catalogo_producto.competencias(self.p)
        self.assertTrue(competencias["reconocer_programas"]["repasar"])

    def test_prerrequisito_bloquea_sin_decision_comercial(self):
        catalogo = catalogo_producto.cargar_catalogo()
        unidad = next(u for i in catalogo["itinerarios"] for u in i.get("unidades", []) if u["id"] == "python-puente")
        unidad["prerrequisitos"] = ["nivel0-programa"]
        # El contrato de catálogo se comprueba en la función sin mutar el archivo.
        indice = catalogo_producto._indice_unidades()
        indice["python-puente"] = {**indice["python-puente"], "prerrequisitos": ["nivel0-programa"]}
        self.assertEqual(
            catalogo_producto.estado_acceso("python-puente", self.p, indice),
            "bloqueado_por_prerrequisito",
        )


if __name__ == "__main__":
    unittest.main()
