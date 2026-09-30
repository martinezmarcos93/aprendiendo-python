"""Fase 9: proyectos integradores adaptativos, persistencia y exportación."""
import base64
import io
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from tortuscript import progreso, proyectos_integradores


class TestProyectosIntegradores(unittest.TestCase):
    def setUp(self):
        self.p = json.loads(json.dumps(progreso.PROGRESO_INICIAL))
        self.p["proyectos_integradores"] = {}

    def completar(self, *prefijos):
        for prefijo in prefijos:
            curso = {"python": "python-real", "web": "web-esencial", "sql": "sql-fundamentos"}[prefijo]
            for i in {
                "python-real": ["py-print"],
                "web-esencial": ["web-html-estructura"],
                "sql-fundamentos": ["sql-tablas"],
            }[curso]:
                self.p["lecciones"][i] = {"pasos": {}, "completada": True, "perfecta": True}

    def test_catalogo_tiene_multiples_proyectos_y_minimo_dos_bloques(self):
        proyectos = proyectos_integradores.cargar_catalogo()
        self.assertGreaterEqual(len(proyectos), 2)
        for proyecto in proyectos:
            self.assertGreaterEqual(len(proyecto["bloques"]), 2)
        self.assertEqual(proyectos_integradores.validar_catalogo(), [])

    def test_proyecto_se_desbloquea_con_dos_bloques(self):
        self.completar("python", "web")
        disponibles = {p["id"]: p for p in proyectos_integradores.disponibles(self.p)}
        self.assertTrue(disponibles["ficha-criatura"]["desbloqueado"])
        self.assertFalse(disponibles["inventario-fantasia"]["desbloqueado"])

    def test_no_puede_saltar_etapas(self):
        self.completar("python", "web")
        pid = proyectos_integradores.iniciar(self.p, "ficha-criatura")
        r = proyectos_integradores.validar_etapa(self.p, pid, "interaccion")
        self.assertFalse(r["ok"])
        self.assertIn("etapa anterior", r["mensaje"])

    def test_adaptacion_por_franja_modifica_ayudas(self):
        self.completar("python", "web")
        self.p["config"]["franja_edad"] = "desarrolladores"
        pid = proyectos_integradores.iniciar(self.p, "ficha-criatura")
        self.assertEqual(proyectos_integradores.estado(self.p, pid)["adaptacion"]["ayudas_maximas"], 4)
        self.p["config"]["franja_edad"] = "constructores"
        self.assertEqual(proyectos_integradores.ayudas(self.p, pid)[0]["desbloqueada"], True)

    def test_iniciar_conserva_archivos_y_no_reinicia(self):
        self.completar("python", "web")
        pid = proyectos_integradores.iniciar(self.p, "ficha-criatura", hoy="2026-09-29")
        estado = proyectos_integradores.estado(self.p, pid)
        self.assertIn("templates/index.html", estado["archivos"])
        self.assertFalse(estado["completado"])
        proyectos_integradores.guardar_archivo(self.p, pid, "templates/index.html", "<h1>Mi criatura</h1>")
        proyectos_integradores.iniciar(self.p, pid)
        self.assertEqual(self.p["proyectos_integradores"][pid]["archivos"]["templates/index.html"], "<h1>Mi criatura</h1>")

    def test_etapas_exigen_criterios_y_el_final_habilita_exportacion(self):
        self.completar("python", "web")
        pid = proyectos_integradores.iniciar(self.p, "ficha-criatura")
        resultado = proyectos_integradores.validar_etapa(self.p, pid, "estructura")
        self.assertFalse(resultado["ok"])
        estado = proyectos_integradores.estado(self.p, pid)
        self.assertFalse(estado["exportable"])

        archivos = self.p["proyectos_integradores"][pid]["archivos"]
        archivos["templates/index.html"] += '<button id="accion">Interactuar</button><p id="estado"></p><script src="app.js"></script>'
        archivos["static/style.css"] += "main { color: white; }"
        archivos["app.js"] = "document.querySelector('#accion').addEventListener('click', () => { document.querySelector('#estado').textContent = 'ok'; });"
        archivos["app.py"] += "\n\ndef descripcion(nombre):\n    return nombre\n"
        for etapa in proyectos_integradores.obtener_proyecto(pid)["etapas"]:
            proyectos_integradores.validar_etapa(self.p, pid, etapa["id"])
        self.assertTrue(self.p["proyectos_integradores"][pid]["completado"])
        datos, nombre = proyectos_integradores.exportar(self.p, pid)
        self.assertEqual(nombre, "ficha-criatura.zip")
        with zipfile.ZipFile(io.BytesIO(datos)) as z:
            self.assertIn("templates/index.html", z.namelist())
            self.assertIn("app.py", z.namelist())

    def test_ayudas_se_desbloquean_por_nivel(self):
        self.completar("python", "web")
        pid = proyectos_integradores.iniciar(self.p, "ficha-criatura")
        self.p["xp_total"] = 0
        self.assertTrue(proyectos_integradores.ayudas(self.p, pid)[0]["desbloqueada"])
        self.p["xp_total"] = 100
        self.assertTrue(proyectos_integradores.ayudas(self.p, pid)[0]["desbloqueada"])
        texto = proyectos_integradores.ver_ayuda(self.p, pid, "estructura-python")
        self.assertIn("Flask", texto)


try:
    import flask
except ImportError:
    flask = None


@unittest.skipIf(flask is None, "Flask no instalado")
class TestWebProyectosIntegradores(unittest.TestCase):
    def setUp(self):
        self._dir = Path(tempfile.mkdtemp())
        self._orig = (progreso.DIRECTORIO, progreso.PERFIL_ACTUAL)
        progreso.DIRECTORIO = self._dir
        progreso.PERFIL_ACTUAL = "default"
        from web.app import create_app
        self.c = create_app(token="t").test_client()
        self.h = {"X-Tortu-Token": "t"}
        p = progreso.cargar_progreso()
        p["config"]["onboarding"] = True
        for i in ("py-print", "web-html-estructura"):
            p["lecciones"][i] = {"pasos": {}, "completada": True, "perfecta": True}
        progreso.guardar_progreso(p)

    def tearDown(self):
        progreso.DIRECTORIO, progreso.PERFIL_ACTUAL = self._orig
        shutil.rmtree(self._dir)

    def post(self, ruta, datos=None):
        return self.c.post(ruta, json=datos or {}, headers=self.h)

    def test_catalogo_y_inicio(self):
        html = self.c.get("/proyectos-integradores").get_data(as_text=True)
        self.assertIn("Ficha interactiva de una criatura", html)
        self.assertIn("Inventario de aventura", html)
        self.assertIn("Aprender VS Code", html)
        self.assertIn("Abrí la carpeta", self.c.get("/proyectos-integradores/vscode").get_data(as_text=True))

    def test_iniciar_editar_validar_y_exportar(self):
        r = self.post("/api/proyectos-integradores/ficha-criatura")
        self.assertTrue(r.get_json()["ok"])
        self.assertEqual(self.c.get("/proyectos-integradores/ficha-criatura").status_code, 200)
        self.post("/api/proyectos-integradores/ficha-criatura/archivo", {
            "nombre": "templates/index.html",
            "codigo": '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'style.css\') }}"><h1>Mi criatura</h1><p id="estado"></p><button id="accion">x</button><script src="{{ url_for(\'static\', filename=\'app.js\') }}"></script>'
        })
        r = self.post("/api/proyectos-integradores/ficha-criatura/etapas/estructura")
        self.assertTrue(r.get_json()["ok"])
        self.assertEqual(self.post("/api/proyectos-integradores/ficha-criatura/exportar").status_code, 400)
        self.assertEqual(self.post("/api/proyectos-integradores/ficha-criatura/ayudas/estructura-python").status_code, 200)

    def test_api_rechaza_sin_token(self):
        self.assertEqual(self.c.post("/api/proyectos-integradores/ficha-criatura", json={}).status_code, 403)


if __name__ == "__main__":
    unittest.main()
