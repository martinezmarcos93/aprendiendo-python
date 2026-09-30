"""Boundary HTTP mínima para cuentas adultas; separada del runtime educativo local.

La ruta de cuenta usa la infraestructura server-side de tortuscript.auth.
No activa todavía el despliegue remoto: create_app mantiene el límite localhost.
"""
from pathlib import Path

from flask import Blueprint, current_app, jsonify, make_response, request

from tortuscript.acceso import AccesoProducto
from tortuscript.auth import AuthError, AuthRepository
from tortuscript.cuentas import CuentaError, CuentaRepository
from tortuscript.migracion_progreso import MigracionProgresoError, MigracionProgresoLocal
from tortuscript.perfil_educativo import ContextoEducativoError, PerfilEducativoService
from tortuscript.progreso_childprofile import ProgresoChildProfile
from tortuscript.progreso_contrato import importar_snapshot
from tortuscript.runtime_educativo import RuntimeEducativo

bp = Blueprint("cuenta", __name__, url_prefix="/cuenta")


def _repos():
    path = Path(current_app.config["ACCOUNT_DB"])
    cuentas = CuentaRepository(path)
    cuentas.ensure_schema()
    auth = AuthRepository(path)
    auth.ensure_schema()
    return cuentas, auth


def _educativo():
    cuentas, auth = _repos()
    progreso_dir = Path(current_app.config.get("PROGRESS_DIR", Path(current_app.instance_path) / "progreso_perfiles"))
    store = ProgresoChildProfile(progreso_dir)
    acceso = AccesoProducto(cuentas)
    return PerfilEducativoService(cuentas, auth, store, acceso)


def _cookie_config():
    return {
        "httponly": True,
        "secure": bool(current_app.config.get("ACCOUNT_COOKIE_SECURE", False)),
        "samesite": current_app.config.get("ACCOUNT_COOKIE_SAMESITE", "Lax"),
        "path": "/",
        "max_age": 12 * 60 * 60,
    }


def _session():
    raw = request.cookies.get("tortu_session")
    if not raw:
        return None, None, None
    cuentas, auth = _repos()
    row = auth.get_session(raw)
    return cuentas, auth, row


def _require_session():
    cuentas, auth, row = _session()
    if not row:
        return None
    return cuentas, auth, row


def _require_csrf(auth, raw_session):
    csrf = request.headers.get("X-Tortu-CSRF", "")
    if not auth.csrf_ok(raw_session, csrf):
        return False
    return True


@bp.post("/registro")
def registro():
    datos = request.get_json(silent=True) or {}
    email = datos.get("email")
    password = datos.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify(ok=False, mensaje="Correo y contraseña son obligatorios."), 400
    cuentas, auth = _repos()
    try:
        cuenta = cuentas.crear_account(email)
        auth.set_password(cuenta.id, password)
    except CuentaError as exc:
        return jsonify(ok=False, mensaje=str(exc)), 400
    except AuthError as exc:
        return jsonify(ok=False, mensaje=str(exc)), 400
    return jsonify(ok=True, estado="pendiente_verificacion", email=cuenta.email), 202


@bp.post("/login")
def login():
    datos = request.get_json(silent=True) or {}
    email = datos.get("email")
    password = datos.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify(ok=False, mensaje="Correo o contraseña incorrectos."), 401
    _, auth = _repos()
    try:
        cuenta = auth.verify_password(email, password)
        raw_session, csrf, expires = auth.create_session(cuenta["id"])
    except AuthError:
        return jsonify(ok=False, mensaje="Correo o contraseña incorrectos o cuenta sin verificar."), 401
    respuesta = make_response(jsonify(ok=True, cuenta={"id": cuenta["id"], "email": cuenta["email"], "role": cuenta["role"]},
                                      csrf=csrf, expira=expires.isoformat()))
    respuesta.set_cookie("tortu_session", raw_session, **_cookie_config())
    return respuesta


@bp.get("/me")
def me():
    resultado = _require_session()
    if not resultado:
        return jsonify(autenticado=False), 401
    cuentas, auth, row = resultado
    cuenta = cuentas.obtener_account(row["account_id"])
    perfiles = cuentas.listar_child_profiles(row["account_id"])
    return jsonify(
        autenticado=True,
        cuenta={"id": cuenta.id, "email": cuenta.email, "role": cuenta.role},
        perfiles=[{"id": p.id, "nombre": p.display_name} for p in perfiles],
        perfil_activo=row["active_profile_id"] if "active_profile_id" in row.keys() else None,
    )


@bp.get("/csrf")
def csrf():
    resultado = _require_session()
    if not resultado:
        return jsonify(autenticado=False), 401
    return jsonify(autenticado=True, requiere_csrf=True)


@bp.post("/logout")
def logout():
    raw = request.cookies.get("tortu_session")
    if not raw:
        return jsonify(ok=True)
    resultado = _session()
    if resultado:
        _, auth, _ = resultado
        if not _require_csrf(auth, raw):
            return jsonify(ok=False, mensaje="Falta una protección CSRF válida."), 403
        auth.revoke(raw)
    respuesta = make_response(jsonify(ok=True))
    respuesta.delete_cookie("tortu_session", path="/")
    return respuesta


@bp.post("/perfiles")
def crear_perfil():
    raw = request.cookies.get("tortu_session")
    resultado = _require_session()
    if not resultado:
        return jsonify(ok=False, mensaje="Sesión requerida."), 401
    cuentas, auth, row = resultado
    if not _require_csrf(auth, raw):
        return jsonify(ok=False, mensaje="Falta una protección CSRF válida."), 403
    nombre = (request.get_json(silent=True) or {}).get("nombre")
    try:
        perfil = cuentas.crear_child_profile(row["account_id"], nombre)
    except CuentaError as exc:
        return jsonify(ok=False, mensaje=str(exc)), 400
    return jsonify(ok=True, perfil={"id": perfil.id, "nombre": perfil.display_name}), 201


@bp.post("/perfil")
def seleccionar_perfil():
    raw = request.cookies.get("tortu_session")
    resultado = _require_session()
    if not resultado:
        return jsonify(ok=False, mensaje="Sesión requerida."), 401
    _, auth, row = resultado
    if not _require_csrf(auth, raw):
        return jsonify(ok=False, mensaje="Falta una protección CSRF válida."), 403
    profile_id = (request.get_json(silent=True) or {}).get("perfil_id")
    if not profile_id:
        return jsonify(ok=False, mensaje="Falta perfil_id."), 400
    try:
        auth.select_profile(raw, profile_id)
    except AuthError as exc:
        return jsonify(ok=False, mensaje=str(exc)), 403
    return jsonify(ok=True, perfil_activo=profile_id)


@bp.get("/progreso")
def obtener_progreso():
    raw = request.cookies.get("tortu_session")
    try:
        service = _educativo()
        contexto = service.contexto(raw)
        snapshot = service.cargar_progreso(raw)
    except ContextoEducativoError as exc:
        return jsonify(ok=False, mensaje=str(exc)), 401
    return jsonify(
        ok=True,
        perfil={"id": contexto.perfil.id, "nombre": contexto.perfil.display_name},
        progreso=None if snapshot is None else {
            "contract_version": snapshot.schema_version,
            "profile_id": snapshot.profile_id,
            "updated_at": snapshot.updated_at,
            "data": snapshot.data,
        },
    )


@bp.put("/progreso")
def guardar_progreso():
    raw = request.cookies.get("tortu_session")
    resultado = _require_session()
    if not resultado:
        return jsonify(ok=False, mensaje="Sesión requerida."), 401
    _, auth, _ = resultado
    if not _require_csrf(auth, raw):
        return jsonify(ok=False, mensaje="Falta una protección CSRF válida."), 403
    documento = request.get_json(silent=True)
    try:
        snapshot = importar_snapshot(documento)
        _educativo().guardar_progreso(raw, snapshot)
    except (ContextoEducativoError, ValueError) as exc:
        return jsonify(ok=False, mensaje=str(exc)), 400
    return jsonify(ok=True, profile_id=snapshot.profile_id, updated_at=snapshot.updated_at)


@bp.get("/acceso")
def acceso_producto():
    raw = request.cookies.get("tortu_session")
    producto = request.args.get("producto", "")
    try:
        service = _educativo()
        contexto = service.contexto(raw)
        acceso = service.resumen_acceso(raw, [producto])
    except ContextoEducativoError as exc:
        return jsonify(ok=False, mensaje=str(exc)), 401
    return jsonify(
        ok=True,
        perfil_id=contexto.perfil.id,
        producto=producto,
        permitido=acceso.get(producto, False),
    )


@bp.get("/progreso/locales")
def listar_progresos_locales():
    raw = request.cookies.get("tortu_session")
    try:
        locales = MigracionProgresoLocal(_educativo()).listar_locales(raw)
    except (ContextoEducativoError, MigracionProgresoError) as exc:
        return jsonify(ok=False, mensaje=str(exc)), 401
    return jsonify(ok=True, perfiles=locales)


@bp.post("/progreso/importar-local")
def importar_progreso_local():
    raw = request.cookies.get("tortu_session")
    resultado = _require_session()
    if not resultado:
        return jsonify(ok=False, mensaje="Sesión requerida."), 401
    _, auth, _ = resultado
    if not _require_csrf(auth, raw):
        return jsonify(ok=False, mensaje="Falta una protección CSRF válida."), 403
    datos = request.get_json(silent=True) or {}
    nombre = datos.get("perfil_local")
    reemplazar = datos.get("reemplazar") is True
    try:
        snapshot = MigracionProgresoLocal(_educativo()).importar_local(raw, nombre, reemplazar=reemplazar)
    except (ContextoEducativoError, MigracionProgresoError) as exc:
        return jsonify(ok=False, mensaje=str(exc)), 400
    return jsonify(
        ok=True,
        profile_id=snapshot.profile_id,
        updated_at=snapshot.updated_at,
        progreso=snapshot.data,
    )


@bp.get("/runtime/progreso")
def runtime_progreso():
    """Primer punto de entrada del runtime educativo autenticado, aún separado del runtime local."""
    raw = request.cookies.get("tortu_session")
    try:
        runtime = RuntimeEducativo(_educativo())
        return jsonify(ok=True, **runtime.snapshot_publico(raw))
    except ContextoEducativoError as exc:
        return jsonify(ok=False, mensaje=str(exc)), 401


@bp.post("/runtime/ejercicio")
def runtime_registrar_ejercicio():
    raw = request.cookies.get("tortu_session")
    resultado = _require_session()
    if not resultado:
        return jsonify(ok=False, mensaje="Sesión requerida."), 401
    _, auth, _ = resultado
    if not _require_csrf(auth, raw):
        return jsonify(ok=False, mensaje="Falta una protección CSRF válida."), 403
    datos = request.get_json(silent=True) or {}
    try:
        runtime = RuntimeEducativo(_educativo())
        mejora = runtime.registrar_ejercicio(raw, int(datos["indice"]), int(datos["estrellas"]), int(datos["xp_ganado"]))
    except (ContextoEducativoError, ValueError, KeyError) as exc:
        return jsonify(ok=False, mensaje=str(exc)), 400
    return jsonify(ok=True, mejora=mejora)


@bp.post("/runtime/leccion/paso")
def runtime_registrar_paso():
    raw = request.cookies.get("tortu_session")
    resultado = _require_session()
    if not resultado:
        return jsonify(ok=False, mensaje="Sesión requerida."), 401
    _, auth, _ = resultado
    if not _require_csrf(auth, raw):
        return jsonify(ok=False, mensaje="Falta una protección CSRF válida."), 403
    datos = request.get_json(silent=True) or {}
    try:
        runtime = RuntimeEducativo(_educativo())
        info = runtime.registrar_paso_leccion(
            raw, str(datos["leccion_id"]), int(datos["indice"]), int(datos["xp"]),
            bool(datos["perfecto"]), int(datos["total_pasos"]), datos.get("estrellas"))
    except (ContextoEducativoError, ValueError, KeyError) as exc:
        return jsonify(ok=False, mensaje=str(exc)), 400
    return jsonify(ok=True, resultado=info)


@bp.post("/runtime/practica")
def runtime_registrar_practica():
    raw = request.cookies.get("tortu_session")
    resultado = _require_session()
    if not resultado:
        return jsonify(ok=False, mensaje="Sesión requerida."), 401
    _, auth, _ = resultado
    if not _require_csrf(auth, raw):
        return jsonify(ok=False, mensaje="Falta una protección CSRF válida."), 403
    datos = request.get_json(silent=True) or {}
    try:
        runtime = RuntimeEducativo(_educativo())
        ganado = runtime.registrar_practica(raw, str(datos["leccion_id"]), int(datos["paso"]), bool(datos["acierto"]))
    except (ContextoEducativoError, ValueError, KeyError) as exc:
        return jsonify(ok=False, mensaje=str(exc)), 400
    return jsonify(ok=True, xp_ganado=ganado)


@bp.get("/runtime/proyectos")
def runtime_listar_proyectos():
    raw = request.cookies.get("tortu_session")
    try:
        proyectos = RuntimeEducativo(_educativo()).listar_proyectos(raw)
    except ContextoEducativoError as exc:
        return jsonify(ok=False, mensaje=str(exc)), 401
    return jsonify(ok=True, proyectos=proyectos)


@bp.post("/runtime/proyectos")
def runtime_guardar_proyecto():
    raw = request.cookies.get("tortu_session")
    resultado = _require_session()
    if not resultado:
        return jsonify(ok=False, mensaje="Sesión requerida."), 401
    _, auth, _ = resultado
    if not _require_csrf(auth, raw):
        return jsonify(ok=False, mensaje="Falta una protección CSRF válida."), 403
    datos = request.get_json(silent=True) or {}
    try:
        proyecto_id = RuntimeEducativo(_educativo()).guardar_proyecto(
            raw, datos.get("nombre"), datos.get("tipo"), datos.get("codigo"), datos.get("proyecto_id"))
    except (ContextoEducativoError, ValueError, KeyError) as exc:
        return jsonify(ok=False, mensaje=str(exc)), 400
    return jsonify(ok=True, proyecto_id=proyecto_id)
