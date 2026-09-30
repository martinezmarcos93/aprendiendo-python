"""Boundary HTTP mínima para cuentas adultas; separada del runtime educativo local.

La ruta de cuenta usa la infraestructura server-side de tortuscript.auth.
No activa todavía el despliegue remoto: create_app mantiene el límite localhost.
"""
from pathlib import Path

from flask import Blueprint, current_app, jsonify, make_response, request

from tortuscript.auth import AuthError, AuthRepository
from tortuscript.cuentas import CuentaError, CuentaRepository

bp = Blueprint("cuenta", __name__, url_prefix="/cuenta")


def _repos():
    path = Path(current_app.config["ACCOUNT_DB"])
    cuentas = CuentaRepository(path)
    cuentas.ensure_schema()
    auth = AuthRepository(path)
    auth.ensure_schema()
    return cuentas, auth


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
    # La persistencia del perfil activo requiere el siguiente paso de migración del esquema de sesiones.
    # No se acepta todavía un cambio silencioso mediante cookie/client storage.
    profile_id = (request.get_json(silent=True) or {}).get("perfil_id")
    if not profile_id:
        return jsonify(ok=False, mensaje="Falta perfil_id."), 400
    return jsonify(ok=False, mensaje="La selección persistente de perfil se habilitará con la migración de sesiones."), 501
