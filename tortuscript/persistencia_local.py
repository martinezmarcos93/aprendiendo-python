"""Persistencia local heredada de TortuScript.

Este módulo contiene exclusivamente la infraestructura de la versión local:
archivos JSON, perfiles locales y configuración recordada. La aplicación web
comercial no utiliza este módulo; su progreso vive en ChildProfile.
"""
import copy
import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from . import progreso

logger = logging.getLogger("tortuscript.persistencia_local")

DIRECTORIO = Path(__file__).resolve().parent.parent
PERFIL_ACTUAL = "default"


# ─────────────────────────────────────────
# PERFILES LOCALES
# ─────────────────────────────────────────
# ─────────────────────────────────────────
# PERFILES
# ─────────────────────────────────────────
def sanitizar_perfil(nombre):
    """Minúsculas, solo letras/números/_/- (con tildes y ñ), máximo 30 caracteres."""
    nombre = (nombre or "").strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9ñáéíóúü_-]", "", nombre)[:30]


def set_perfil(nombre):
    global PERFIL_ACTUAL
    limpio = sanitizar_perfil(nombre)
    if limpio:
        PERFIL_ACTUAL = limpio
    return PERFIL_ACTUAL


def _archivo_config():
    return DIRECTORIO / "config_tortuscript.json"


def recordar_perfil(nombre):
    """Guarda cuál fue el último perfil usado, para abrir con ese la próxima vez."""
    try:
        _archivo_config().write_text(json.dumps({"ultimo_perfil": nombre}), encoding="utf-8")
    except OSError as e:
        logger.error("No se pudo recordar el perfil: %s", e, exc_info=True)


def perfil_recordado():
    try:
        nombre = json.loads(_archivo_config().read_text(encoding="utf-8")).get("ultimo_perfil")
    except (OSError, ValueError, AttributeError):
        return "default"
    return sanitizar_perfil(nombre) or "default"


def get_archivo_progreso(perfil=None):
    return DIRECTORIO / f"progreso_{perfil or PERFIL_ACTUAL}.json"


def obtener_perfiles():
    perfiles = {p.name[len("progreso_"):-len(".json")] for p in DIRECTORIO.glob("progreso_*.json")}
    perfiles.add("default")
    return sorted(perfiles)


def leer_otros_perfiles(actual=None):
    """{nombre que se ve: XP por día} de los demás perfiles de esta PC (solo lectura; sirve a la liga)."""
    actual = actual or PERFIL_ACTUAL
    salida = {}
    for nombre in obtener_perfiles():
        if nombre == actual:
            continue
        try:
            datos = _leer(get_archivo_progreso(nombre))
        except (OSError, ValueError):
            continue                                    # perfil sin archivo o dañado: no participa
        visible = (datos.get("config") or {}).get("nombre") or nombre
        salida[visible] = datos.get("xp_por_dia") or {}
    return salida



# ─────────────────────────────────────────
# CARGA / GUARDADO LOCAL
# ─────────────────────────────────────────
# ─────────────────────────────────────────
# CARGA / GUARDADO
# ─────────────────────────────────────────
def _leer(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("ejercicios", {}), dict):
        raise ValueError("estructura de progreso inválida")
    return data


def progreso._migrar(data):
    for campo, valor in progreso.PROGRESO_INICIAL.items():
        if campo not in data:
            data[campo] = copy.deepcopy(valor)
    for clave, valor in PROGRESO_INICIAL["config"].items():      # config de versiones anteriores, a medias
        data["config"].setdefault(clave, copy.deepcopy(valor))
    for clave, valor in PROGRESO_INICIAL["config"]["ajustes"].items():
        data["config"]["ajustes"].setdefault(clave, valor)
    data["version"] = progreso.VERSION_ESQUEMA
    return data


def cargar_progreso(perfil=None):
    perfil = perfil or PERFIL_ACTUAL
    archivo = get_archivo_progreso(perfil)
    data = None
    if archivo.exists():
        try:
            data = _leer(archivo)
        except (OSError, ValueError) as e:
            marca = datetime.now().strftime("%Y%m%d-%H%M%S")
            apartado = archivo.with_name(f"{archivo.name}.corrupto-{marca}")
            logger.error("Progreso dañado en %s: %s — se aparta como %s", archivo, e, apartado.name)
            try:
                os.replace(archivo, apartado)
            except OSError as e2:
                logger.error("No se pudo apartar el progreso dañado: %s", e2, exc_info=True)
            respaldo = archivo.with_name(archivo.name + ".bak")
            if respaldo.exists():
                try:
                    data = _leer(respaldo)
                    logger.warning("Progreso recuperado desde %s", respaldo.name)
                except (OSError, ValueError) as e3:
                    logger.error("El respaldo también está dañado: %s", e3)
    data = _migrar(data) if data is not None else copy.deepcopy(PROGRESO_INICIAL)
    data["_perfil"] = perfil
    return data


def guardar_progreso(progreso):
    """Guarda de forma atómica. Devuelve True si pudo guardar."""
    perfil = progreso.get("_perfil") or PERFIL_ACTUAL
    archivo = get_archivo_progreso(perfil)
    datos = {k: v for k, v in progreso.items() if not k.startswith("_")}
    tmp = None
    try:
        archivo.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".progreso_", suffix=".tmp", dir=str(archivo.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        if archivo.exists():
            shutil.copy2(archivo, archivo.with_name(archivo.name + ".bak"))
        os.replace(tmp, archivo)
        return True
    except OSError as e:
        logger.error("No se pudo guardar el progreso en %s: %s", archivo, e, exc_info=True)
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
        return False

