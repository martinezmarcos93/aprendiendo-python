import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class Fases11a14Tests(unittest.TestCase):
    def test_privacidad_es_minimalista_y_explicitamente_no_comercial(self):
        data = json.loads((ROOT / "docs/PRIVACIDAD_DATOS_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(data["jurisdiccion_inicial"], "Argentina")
        self.assertIn("minimizacion", data["principios"])
        self.assertIn("publicidad_comportamental", data["prohibidos_por_defecto"])
        self.assertTrue(data["terceros_requieren_registro"])

    def test_franjas_no_alteran_criterios(self):
        data = json.loads((ROOT / "contenido/franjas_edad.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["franjas"]), 4)
        self.assertIn("no altera silenciosamente", data["regla"])

    def test_catalogo_avanzado_mantiene_fuentes_externas(self):
        data = json.loads((ROOT / "docs/catalogo_avanzado_v1.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["fuentes"]), 3)
        self.assertTrue(all("repositorio" in f for f in data["fuentes"]))
        self.assertIn("No copiar", data["regla"])

    def test_documentacion_de_fases_existe(self):
        for nombre in (
            "FASE11_ARQUITECTURA_WEB_COMERCIAL_V1.md",
            "FASE12_PRIVACIDAD_MENORES_V1.md",
            "FASE13_UX_EDADES_V1.md",
            "FASE14_NIVEL_AVANZADO_V1.md",
        ):
            self.assertTrue((ROOT / "docs" / nombre).exists())


if __name__ == "__main__":
    unittest.main()
