"""
El árbol propio de TortuGame (ADR-007): TortuScript → Python → ast.parse → LISTA BLANCA → JSON.

El servidor solo ANALIZA (no ejecuta) y le manda al navegador un árbol con los nodos permitidos. El intérprete de
web/static/js/tortugame/interprete.js no conoce otra cosa: lo que no está acá, no existe para el juego.

Formato: cada nodo es {"k": tipo, "l": línea, ...}. Los tipos y sus campos están en `convertir` (fuente de verdad) y el
intérprete JS los vuelve a validar al recibirlos.
"""
import ast

from .executor import CodigoNoPermitido, validar_codigo
from .translator import TraductorTortuScript, detectar_tipo

MAX_ENTERO = 2 ** 53 - 1                    # JS representa enteros exactos hasta acá
MAX_NODOS = 20000
ATRIBUTOS = {"nombre", "vida", "vida_max", "fuerza", "inventario"}            # de un personaje
ATRIBUTOS_CAMBIABLES = {"nombre", "vida", "fuerza"}
METODOS = {"append", "pop"}                                                   # de una lista
OPERADORES = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**"}
COMPARADORES = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
                ast.In: "in", ast.NotIn: "not in"}
UNARIOS = {ast.USub: "-", ast.UAdd: "+", ast.Not: "no"}


class NoPermitido(CodigoNoPermitido):
    """Algo del lenguaje que un juego no puede usar (el mensaje se muestra tal cual)."""


def _no(nodo, que):
    raise NoPermitido(f"En un juego no se puede usar {que}.", getattr(nodo, "lineno", None))


class _Conversor:
    def __init__(self):
        self.nodos = 0
        self.en_funcion = False

    def _contar(self, nodo):
        self.nodos += 1
        if self.nodos > MAX_NODOS:
            raise NoPermitido("Tu juego es demasiado largo.", getattr(nodo, "lineno", None))

    def cuerpo(self, sentencias):
        return [self.sentencia(s) for s in sentencias]

    # ── sentencias ──
    def sentencia(self, n):
        self._contar(n)
        base = {"l": n.lineno}
        if isinstance(n, ast.Expr):
            return {"k": "expr", "e": self.expr(n.value), **base}
        if isinstance(n, ast.Assign):
            if len(n.targets) != 1:
                _no(n, "varias asignaciones en una sola línea")
            return {"k": "asignar", "d": self.destino(n.targets[0]), "e": self.expr(n.value), **base}
        if isinstance(n, ast.AugAssign):
            if type(n.op) not in OPERADORES:
                _no(n, "ese operador")
            return {"k": "asignar_op", "d": self.destino(n.target), "op": OPERADORES[type(n.op)],
                    "e": self.expr(n.value), **base}
        if isinstance(n, ast.If):
            return {"k": "si", "c": self.expr(n.test), "si": self.cuerpo(n.body), "sino": self.cuerpo(n.orelse), **base}
        if isinstance(n, ast.While):
            if n.orelse:
                _no(n, "sino después de mientras")
            return {"k": "mientras", "c": self.expr(n.test), "cuerpo": self.cuerpo(n.body), **base}
        if isinstance(n, ast.For):
            if n.orelse or not isinstance(n.target, ast.Name):
                _no(n, "esa forma de para")
            return {"k": "para", "var": self.nombre(n.target.id, n), "iter": self.expr(n.iter),
                    "cuerpo": self.cuerpo(n.body), **base}
        if isinstance(n, ast.FunctionDef):
            a = n.args
            if n.decorator_list or a.vararg or a.kwarg or a.kwonlyargs or a.posonlyargs or a.defaults:
                _no(n, "esa forma de función")
            if self.en_funcion:
                _no(n, "una función dentro de otra (creala afuera)")
            self.en_funcion = True
            try:
                cuerpo = self.cuerpo(n.body)
            finally:
                self.en_funcion = False
            params = [self.nombre(p.arg, n) for p in a.args]
            return {"k": "funcion", "nombre": self.nombre(n.name, n), "params": params, "cuerpo": cuerpo,
                    "locales": sorted(_asignadas(n.body) | set(params)), **base}
        if isinstance(n, ast.Return):
            return {"k": "devolver", "e": self.expr(n.value) if n.value is not None else None, **base}
        if isinstance(n, ast.Break):
            return {"k": "cortar", **base}
        if isinstance(n, ast.Continue):
            return {"k": "seguir", **base}
        if isinstance(n, ast.Pass):
            return {"k": "nada", **base}
        _no(n, f"«{type(n).__name__}»")

    def destino(self, n):
        if isinstance(n, ast.Name):
            return {"k": "var", "id": self.nombre(n.id, n)}
        if isinstance(n, ast.Attribute):
            if n.attr not in ATRIBUTOS_CAMBIABLES:
                _no(n, f"cambiar «.{n.attr}» (se pueden cambiar vida, fuerza y nombre)")
            return {"k": "attr", "o": self.expr(n.value), "a": n.attr}
        if isinstance(n, ast.Subscript):
            return {"k": "indice", "o": self.expr(n.value), "i": self.expr(n.slice)}
        _no(n, "esa forma de guardar")

    def nombre(self, texto, n):
        if texto.startswith("_") and texto != "_":             # "_" solo: la variable de repetir
            _no(n, f"«{texto}» (los nombres que empiezan con _ son internos)")
        return texto

    # ── expresiones ──
    def expr(self, n):
        self._contar(n)
        base = {"l": getattr(n, "lineno", 0)}
        if isinstance(n, ast.Constant):
            v = n.value
            if isinstance(v, bool) or v is None:
                return {"k": "const", "v": v, **base}
            if isinstance(v, int):
                if abs(v) > MAX_ENTERO:
                    _no(n, "un número tan grande")
                return {"k": "num", "v": v, **base}
            if isinstance(v, float):
                return {"k": "num", "v": v, "f": True, **base}
            if isinstance(v, str):
                return {"k": "texto", "v": v, **base}
            _no(n, "ese tipo de dato")
        if isinstance(n, ast.Name):
            return {"k": "var", "id": self.nombre(n.id, n), **base}
        if isinstance(n, ast.BinOp):
            if type(n.op) not in OPERADORES:
                _no(n, "ese operador")
            return {"k": "op", "op": OPERADORES[type(n.op)], "a": self.expr(n.left), "b": self.expr(n.right), **base}
        if isinstance(n, ast.UnaryOp):
            if type(n.op) not in UNARIOS:
                _no(n, "ese operador")
            return {"k": "unario", "op": UNARIOS[type(n.op)], "a": self.expr(n.operand), **base}
        if isinstance(n, ast.BoolOp):
            return {"k": "logica", "op": "y" if isinstance(n.op, ast.And) else "o",
                    "vs": [self.expr(v) for v in n.values], **base}
        if isinstance(n, ast.Compare):
            if any(type(o) not in COMPARADORES for o in n.ops):
                _no(n, "esa comparación")
            return {"k": "comparar", "ops": [COMPARADORES[type(o)] for o in n.ops],
                    "vs": [self.expr(n.left)] + [self.expr(c) for c in n.comparators], **base}
        if isinstance(n, ast.Call):
            if n.keywords:
                _no(n, "argumentos con nombre")
            if any(isinstance(a, ast.Starred) for a in n.args):
                _no(n, "*")
            if isinstance(n.func, ast.Name):
                return {"k": "llamar", "f": self.nombre(n.func.id, n), "args": [self.expr(a) for a in n.args], **base}
            if isinstance(n.func, ast.Attribute) and n.func.attr in METODOS:
                return {"k": "metodo", "o": self.expr(n.func.value), "m": n.func.attr,
                        "args": [self.expr(a) for a in n.args], **base}
            _no(n, "esa forma de llamar")
        if isinstance(n, ast.Attribute):
            if n.attr not in ATRIBUTOS:
                _no(n, f"«.{n.attr}» (un personaje tiene nombre, vida, vida_max, fuerza e inventario)")
            return {"k": "attr", "o": self.expr(n.value), "a": n.attr, **base}
        if isinstance(n, ast.Subscript):
            if isinstance(n.slice, ast.Slice):
                _no(n, "porciones de listas ([a:b])")
            return {"k": "indice", "o": self.expr(n.value), "i": self.expr(n.slice), **base}
        if isinstance(n, ast.List):
            return {"k": "lista", "vs": [self.expr(e) for e in n.elts], **base}
        if isinstance(n, ast.IfExp):
            return {"k": "si_expr", "c": self.expr(n.test), "si": self.expr(n.body), "sino": self.expr(n.orelse), **base}
        _no(n, f"«{type(n).__name__}»")


def _asignadas(sentencias):
    """Los nombres que una función asigna (en Python son locales en TODA la función, aun antes de asignarlos)."""
    nombres = set()
    for s in sentencias:
        for n in ast.walk(s):
            if isinstance(n, (ast.Assign, ast.AugAssign, ast.For)):
                for destino in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                    if isinstance(destino, ast.Name):
                        nombres.add(destino.id)
    return nombres


def arbol_del_juego(fuente):
    """El árbol JSON de un programa (TortuScript o Python). Levanta SyntaxError o CodigoNoPermitido."""
    python = fuente if detectar_tipo(fuente) == "python" else TraductorTortuScript().traducir_codigo(fuente)
    validar_codigo(python)                                   # las mismas reglas que el ejecutor educativo
    return {"k": "programa", "cuerpo": _Conversor().cuerpo(ast.parse(python).body)}
