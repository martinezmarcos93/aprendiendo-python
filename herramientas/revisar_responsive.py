#!/usr/bin/env python3
"""Comprueba responsive y navegación mobile sobre un servidor de prueba.

Requiere Playwright:
    .venv/bin/python -m pip install -r requirements-dev.txt
    .venv/bin/python -m playwright install chromium

El servidor debe arrancarse con:
    python herramientas/servidor_de_prueba.py --cuenta-prueba

Prueba 320, 375, 390, 768 y 1280 px sobre las rutas críticas. Antes de recorrerlas
crea una sesión adulta, selecciona el ChildProfile de prueba y completa el onboarding
mínimo. Sale con código 1 ante overflow horizontal o elementos fuera de viewport.
"""
import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "herramientas"))

ANCHOS = (320, 375, 390, 768, 1280)
RUTAS = [
    "/", "/bienvenida", "/aprender", "/leccion/hola-mundo", "/ejercicios/1",
    "/experimentar", "/tortuga", "/juego", "/proyectos", "/proyectos-integradores",
]
EMAIL = "mobile-test@tortuscript.local"
PASSWORD = "TortuMobileTest!2026"

JS_DESBORDE = r"""
() => {
  const ancho = document.documentElement.clientWidth, malos = [];
  for (const el of document.querySelectorAll("body *")) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0 || getComputedStyle(el).position === "fixed") continue;
    if (el.closest(".CodeMirror, pre, [hidden], details:not([open]) .mas-lista") || el.matches(".mas-lista")) continue;
    if (r.right > ancho + 1 || r.left < -1) {
      malos.push(String(el.className || el.tagName).slice(0, 60) + " (" + Math.round(r.left) + ".." + Math.round(r.right) + ")");
    }
  }
  return {scroll: document.documentElement.scrollWidth - ancho, malos: malos.slice(0, 10)};
}
"""


def autenticar(pg, token):
    """Login JSON + selección del primer perfil, usando la misma superficie HTTP que la UI."""
    pg.goto(pg.url.rstrip("/") + "/cuenta/ingresar" if pg.url else "http://127.0.0.1:5077/cuenta/ingresar")
    resultado = pg.evaluate(
        """async ({email, password}) => {
          const r = await fetch('/cuenta/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
          });
          return {status: r.status, body: await r.json()};
        }""",
        {"email": EMAIL, "password": PASSWORD},
    )
    if resultado["status"] != 200:
        raise RuntimeError(f"Login E2E falló: {resultado}")
    me = pg.evaluate("""async () => (await fetch('/cuenta/me')).json()""")
    if not me.get("autenticado") or not me.get("perfiles"):
        raise RuntimeError(f"La cuenta E2E no tiene perfil seleccionable: {me}")
    perfil = me["perfiles"][0]["id"]
    csrf = pg.evaluate("""() => document.cookie.split('; ').find(x => x.startsWith('tortu_csrf='))?.split('=')[1] || ''""")
    seleccionado = pg.evaluate(
        """async ({perfil, csrf}) => {
          const r = await fetch('/cuenta/perfil', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-Tortu-CSRF': csrf},
            body: JSON.stringify({perfil_id: perfil})
          });
          return {status: r.status, body: await r.json()};
        }""",
        {"perfil": perfil, "csrf": csrf},
    )
    if seleccionado["status"] != 200:
        raise RuntimeError(f"Selección de ChildProfile falló: {seleccionado}")

    # El onboarding se completa por la API educativa existente, no tocando SQLite a mano.
    onboarding = pg.evaluate(
        """async ({token}) => {
          const r = await fetch('/api/onboarding', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-Tortu-Token': token},
            body: JSON.stringify({meta_min: 10})
          });
          return {status: r.status, text: await r.text()};
        }""",
        {"token": token},
    )
    if onboarding["status"] not in (200, 201):
        raise RuntimeError(f"Onboarding E2E falló: {onboarding}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:5077")
    ap.add_argument("--capturas", default=None)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    problemas = 0
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pg = navegador.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(args.url + "/cuenta/ingresar")
        autenticar(pg, "prueba")

        for ancho in ANCHOS:
            pg.set_viewport_size({"width": ancho, "height": 800 if ancho != 375 else 812})
            for ruta in RUTAS:
                pg.goto(args.url + ruta)
                pg.wait_for_timeout(200)
                r = pg.evaluate(JS_DESBORDE)
                if r["scroll"] > 1 or r["malos"]:
                    problemas += 1
                    print(f"[{ancho}px] {ruta}: se desborda {r['scroll']}px → {r['malos']}")
                    if args.capturas:
                        Path(args.capturas).mkdir(parents=True, exist_ok=True)
                        pg.screenshot(path=str(Path(args.capturas) / f"desborde_{ancho}_{ruta.strip('/').replace('/', '_') or 'inicio'}.png"))

        navegador.close()

    print("Responsive: sin desbordes" if not problemas else f"Responsive: {problemas} páginas con desborde")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
