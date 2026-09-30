"""Evaluación declarativa y segura de ejercicios Web.

El servidor NO ejecuta HTML/CSS/JavaScript del alumno. Solo inspecciona texto
normalizado y comprueba requisitos declarados por el contenido.
"""
import re

MAX_CODIGO_WEB = 12000
BLOQUEADOS = (
    r"<iframe\\b", r"<object\\b", r"<embed\\b", r"<form\\b",
    r"javascript\\s*:", r"<script[^>]+src\\s*=", r"@import\\s+url\\s*\\(",
)

def _normalizar(codigo):
    return str(codigo or "").replace("\r\n", "\n").replace("\r", "\n").strip()

def validar_codigo(codigo, lenguaje, reglas=None):
    codigo = _normalizar(codigo)
    reglas = reglas or {}
    if not codigo:
        return False, "Escribí algo antes de probarlo."
    if len(codigo) > MAX_CODIGO_WEB:
        return False, "El código es demasiado largo para este ejercicio."
    bajo = codigo.lower()
    for patron in BLOQUEADOS:
        if re.search(patron, bajo):
            return False, "Ese recurso externo no está permitido en el laboratorio Web."
    if lenguaje == "html":
        if "<" not in codigo or ">" not in codigo:
            return False, "Esto parece necesitar al menos un elemento HTML."
    elif lenguaje == "css":
        if "{" not in codigo or "}" not in codigo:
            return False, "El CSS necesita una regla con llaves."
    elif lenguaje == "javascript":
        if not re.search(r"\\b(function|const|let|var)\\b", codigo):
            return False, "Escribí al menos una variable o función de JavaScript."
    requeridos = reglas.get("contiene", [])
    for texto in requeridos:
        if str(texto).lower() not in bajo:
            return False, f"Falta usar «{texto}»."
    return True, None

def evaluar(codigo, solucion, lenguaje, reglas=None):
    ok, mensaje = validar_codigo(codigo, lenguaje, reglas)
    if not ok:
        return {"estado": "incorrecto", "mensaje": mensaje}
    esperado = _normalizar(solucion)
    actual = _normalizar(codigo)
    if actual == esperado:
        return {"estado": "correcto"}
    if reglas and reglas.get("contiene"):
        return {"estado": "correcto"}
    return {"estado": "incorrecto", "mensaje": "La página funciona como código Web, pero todavía no cumple la consigna."}
