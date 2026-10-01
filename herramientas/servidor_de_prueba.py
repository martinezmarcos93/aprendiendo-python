#!/usr/bin/env python3
"""Servidor de PRUEBA: la app web con almacenamiento temporal.

Lo usan jugar_cursos.py, revisar_contraste.py y revisar_responsive.py.
Uso:
  python herramientas/servidor_de_prueba.py [puerto] [--todo-desbloqueado] [--cuenta-prueba] [--abrir]

--cuenta-prueba crea una cuenta adulta verificada y un ChildProfile temporal para
que los harness de navegador puedan atravesar el flujo comercial local sin depender
de datos persistentes de la máquina.
"""
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from tortuscript import persistencia_local, progreso  # noqa: E402

TOKEN = "prueba"
CUENTA_PRUEBA_EMAIL = "mobile-test@tortuscript.local"
CUENTA_PRUEBA_PASSWORD = "TortuMobileTest!2026"


def desbloquear_todo():
    """Marca todas las lecciones y ejercicios como abiertos (sin XP) en el progreso temporal."""
    from tortuscript import contenido
    p = persistencia_local.cargar_progreso()
    progreso.guardar_config(p, onboarding=True, nombre="Prueba")
    for curso in contenido.todos_los_cursos():
        for _, lec in contenido.lecciones(curso):
            p.setdefault("lecciones", {})[lec["id"]] = {"pasos": {}, "completada": True, "perfecta": False}
    for i in range(len(contenido.ejercicios())):
        p["ejercicios"][str(i)] = {"completado": True, "estrellas": 1, "xp": 0}
    persistencia_local.guardar_progreso(p)


def preparar_cuenta_prueba(app):
    """Configura una cuenta verificada + un perfil para pruebas browser E2E."""
    from tortuscript.auth import AuthRepository
    from tortuscript.cuentas import CuentaRepository

    db = Path(tempfile.mkdtemp(prefix="tortu_cuentas_prueba_")) / "cuentas.sqlite3"
    app.config["ACCOUNT_DB"] = db
    cuentas = CuentaRepository(db)
    cuentas.ensure_schema()
    auth = AuthRepository(db)
    auth.ensure_schema()

    cuenta = cuentas.obtener_account_por_email(CUENTA_PRUEBA_EMAIL)
    if cuenta is None:
        cuenta = cuentas.crear_account(CUENTA_PRUEBA_EMAIL)
    auth.set_password(cuenta.id, CUENTA_PRUEBA_PASSWORD)
    auth.marcar_verificada(cuenta.id)
    perfiles = cuentas.listar_child_profiles(cuenta.id)
    if not perfiles:
        cuentas.crear_child_profile(cuenta.id, "Mobile")
    return db


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    puerto = int(args[0]) if args else 5077
    persistencia_local.DIRECTORIO = Path(tempfile.mkdtemp(prefix="tortu_prueba_"))
    if "--todo-desbloqueado" in sys.argv:
        desbloquear_todo()

    from iniciar_web import crear_servidor
    from web.app import create_app

    app = create_app(token=TOKEN)
    if "--cuenta-prueba" in sys.argv:
        db = preparar_cuenta_prueba(app)
        print(f"Cuenta E2E: {CUENTA_PRUEBA_EMAIL} / {CUENTA_PRUEBA_PASSWORD}")
        print(f"SQLite de cuentas temporal: {db}")

    print(f"Servidor de prueba en http://127.0.0.1:{puerto} (progreso temporal en {persistencia_local.DIRECTORIO})")
    if "--abrir" in sys.argv:
        import threading
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{puerto}/")).start()
    crear_servidor(puerto, app).serve_forever()


if __name__ == "__main__":
    main()
