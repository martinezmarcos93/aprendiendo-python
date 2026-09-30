"""Evaluador seguro de SQL educativo.

Las consultas del alumno se ejecutan únicamente contra una base SQLite en memoria
construida desde el dataset declarado por la lección. La V1 es de solo lectura.
No se abre ningún archivo ni se permite ATTACH, PRAGMA, DDL, DML o extensiones.
"""

import json
import re
import sqlite3
from pathlib import Path

MAX_CODIGO_SQL = 4000
MAX_FILAS = 100
MAX_CELDAS = 1000
MAX_OPS = 100_000

_RE_INICIO = re.compile(r"^\s*(?:--[^\n]*\n|/\*.*?\*/\s*)*(SELECT|WITH)\\b", re.I | re.S)
_BLOQUEADOS = re.compile(
    r"\b(?:INSERT|UPDATE|DELETE|REPLACE|UPSERT|DROP|ALTER|CREATE|ATTACH|DETACH|VACUUM|"
    r"PRAGMA|REINDEX|ANALYZE|SAVEPOINT|RELEASE|ROLLBACK|COMMIT)\\b|"
    r"load_extension\s*\(|readfile\s*\(|writefile\s*\(",
    re.I,
)

def _normalizar(codigo):
    return str(codigo or "").replace("\r\n", "\n").replace("\r", "\n").strip()

def _dataset(datos):
    datos = datos or {}
    if isinstance(datos, str):
        ruta = Path(__file__).resolve().parent.parent / "contenido" / "datos" / "sql" / f"{datos}.json"
        with ruta.open(encoding="utf-8") as f:
            datos = json.load(f)
    return datos.get("tablas") or {}

def _construir(datos):
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys=OFF")
    tablas = _dataset(datos)
    if not isinstance(tablas, dict) or not tablas:
        con.close()
        raise ValueError("La lección no tiene un dataset SQL válido.")
    for nombre, tabla in tablas.items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(nombre)):
            raise ValueError("Nombre de tabla no válido en el dataset.")
        columnas = tabla.get("columnas") or []
        filas = tabla.get("filas") or []
        if not columnas or not all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(c)) for c in columnas):
            raise ValueError("Columnas SQL no válidas en el dataset.")
        if len(filas) > MAX_FILAS or len(columnas) * len(filas) > MAX_CELDAS:
            raise ValueError("Dataset SQL demasiado grande.")
        if len(set(columnas)) != len(columnas):
            raise ValueError("Hay columnas SQL repetidas.")
        tipos = tabla.get("tipos") or ["TEXT"] * len(columnas)
        if len(tipos) != len(columnas):
            raise ValueError("La cantidad de tipos no coincide con las columnas.")
        definicion = ", ".join(f'"{c}" {t}' for c, t in zip(columnas, tipos))
        con.execute(f'CREATE TABLE "{nombre}" ({definicion})')
        marcadores = ",".join("?" for _ in columnas)
        for fila in filas:
            if len(fila) != len(columnas):
                raise ValueError(f"Una fila de {nombre} no coincide con sus columnas.")
            con.execute(f'INSERT INTO "{nombre}" VALUES ({marcadores})', tuple(fila))
    con.commit()
    return con

def _autorizar(accion, *_args):
    permitidas = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
    }
    return sqlite3.SQLITE_OK if accion in permitidas else sqlite3.SQLITE_DENY

def _preparar(codigo):
    codigo = _normalizar(codigo)
    if not codigo:
        return None, "Escribí una consulta SQL."
    if len(codigo) > MAX_CODIGO_SQL:
        return None, "La consulta es demasiado larga para este ejercicio."
    if not _RE_INICIO.match(codigo):
        return None, "En SQL V1 solo se permiten consultas de lectura que empiecen con SELECT o WITH."
    sin_final = codigo[:-1].rstrip() if codigo.endswith(";") else codigo
    if ";" in sin_final:
        return None, "Usá una sola consulta por ejercicio."
    if _BLOQUEADOS.search(codigo):
        return None, "Esta operación no está permitida en el laboratorio SQL."
    return codigo, None

def ejecutar(codigo, datos=None):
    """Ejecuta una consulta de lectura y devuelve columnas, filas y texto visible."""
    codigo, mensaje = _preparar(codigo)
    if mensaje:
        return {"ok": False, "mensaje": mensaje, "columnas": [], "filas": [], "salida": ""}
    try:
        con = _construir(datos)
        con.set_authorizer(_autorizar)
        operaciones = {"n": 0}
        def limite():
            operaciones["n"] += 1000
            return 1 if operaciones["n"] > MAX_OPS else 0
        con.set_progress_handler(limite, 1000)
        cur = con.execute(codigo)
        filas = cur.fetchmany(MAX_FILAS + 1)
        if len(filas) > MAX_FILAS:
            return {"ok": False, "mensaje": "La consulta devuelve demasiadas filas.", "columnas": [], "filas": [], "salida": ""}
        columnas = [d[0] for d in cur.description or []]
        con.close()
        salida = "\n".join(" | ".join("" if v is None else str(v) for v in fila) for fila in filas)
        return {"ok": True, "mensaje": None, "columnas": columnas, "filas": [list(f) for f in filas], "salida": salida}
    except sqlite3.Error as e:
        return {"ok": False, "mensaje": f"Consulta no válida: {e}", "columnas": [], "filas": [], "salida": ""}
    except ValueError as e:
        return {"ok": False, "mensaje": str(e), "columnas": [], "filas": [], "salida": ""}

def evaluar(codigo, solucion, datos=None, reglas=None):
    reglas = reglas or {}
    alumno = ejecutar(codigo, datos)
    if not alumno["ok"]:
        return {"estado": "incorrecto", "mensaje": alumno["mensaje"], "obtenido": alumno}
    esperado = ejecutar(solucion, datos)
    if not esperado["ok"]:
        return {"estado": "error_contenido", "mensaje": f"La solución oficial no es válida: {esperado['mensaje']}", "obtenido": alumno}
    filas_a = alumno["filas"]
    filas_e = esperado["filas"]
    if not reglas.get("orden_importa", True):
        filas_a = sorted(filas_a, key=repr)
        filas_e = sorted(filas_e, key=repr)
    correcto = alumno["columnas"] == esperado["columnas"] and filas_a == filas_e
    if correcto:
        return {"estado": "correcto", "obtenido": alumno}
    return {"estado": "incorrecto", "mensaje": "La consulta funciona, pero todavía devuelve datos distintos de los esperados.", "obtenido": alumno}

def validar_consulta(codigo, datos=None):
    r = ejecutar(codigo, datos)
    return (True, None) if r["ok"] else (False, r["mensaje"])
