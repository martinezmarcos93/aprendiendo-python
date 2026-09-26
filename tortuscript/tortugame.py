"""
TortuGame v1: la API de juegos de rol por turnos (docs/TORTUGAME.md, ADR-006/007/008/009).

Esta es la implementación de REFERENCIA, en Python: la usa el servidor para evaluar las lecciones de juegos y el
validador de contenido (el XP lo sigue calculando el servidor). Los juegos se juegan en el navegador con el intérprete
de web/static/js/tortugame/interprete.js, que tiene que dar exactamente el mismo registro de eventos: lo exigen los
tests de conformidad (tests/js/tortugame.test.mjs + tests/test_tortugame.py).

Todo lo que el chico le pide al juego queda en un REGISTRO de eventos (como la tortuga): la página lo anima después.
El azar sale de mulberry32 con semilla, igual en Python y en JS.
"""
import math
import re

from .executor import NecesitaEntrada, ejecutar_codigo
from .translator import TraductorTortuScript, detectar_tipo

LUGARES = ("aldea", "bosque", "cueva", "mazmorra", "castillo")
COLUMNAS, FILAS = 8, 5
MAX_PERSONAJES = 50
MAX_EVENTOS = 2000
MAX_TEXTO = 2000
MAX_NOMBRE = 40
MAX_INVENTARIO = 100
MAX_VIDA = 10000
MAX_FUERZA = 1000
MAX_CARAS = 1000
_M = 0xFFFFFFFF


class ErrorJuego(Exception):
    """Algo que el chico le pidió mal al juego (se explica en lenguaje simple)."""


# ─────────────────────────────── azar (idéntico al de JS) ───────────────────────────────
def _imul(a, b):
    return (a * b) & _M


class Azar:
    """mulberry32: el mismo generador en Python y en JS (misma semilla → mismos números)."""

    def __init__(self, semilla):
        self.estado = int(semilla) & _M

    def siguiente(self):
        self.estado = (self.estado + 0x6D2B79F5) & _M
        a = self.estado
        t = _imul(a ^ (a >> 15), 1 | a)
        t = ((t + _imul(t ^ (t >> 7), 61 | t)) & _M) ^ t
        return ((t ^ (t >> 14)) & _M) / 4294967296

    def dado(self, caras=6):
        return math.floor(self.siguiente() * caras) + 1


# ─────────────────────────────── formato de textos (como print) ───────────────────────────────
def como_texto(valor):
    """Lo que muestra `mostrar` (igual que str() de Python; el JS lo imita)."""
    if isinstance(valor, Personaje):
        return valor._nombre
    return str(valor)


def _es_entero(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _texto(valor, que, maximo=MAX_TEXTO):
    if not isinstance(valor, str):
        raise ErrorJuego(f"{que} tiene que ser un texto, entre comillas.")
    if not valor.strip():
        raise ErrorJuego(f"{que} no puede estar vacío.")
    if len(valor) > maximo:
        raise ErrorJuego(f"{que} es muy largo (máximo {maximo} letras).")
    return valor


def _numero(valor, que, minimo, maximo):
    if not _es_entero(valor):
        raise ErrorJuego(f"{que} tiene que ser un número entero, por ejemplo 10.")
    if not minimo <= valor <= maximo:
        raise ErrorJuego(f"{que} tiene que estar entre {minimo} y {maximo}.")
    return valor


# ─────────────────────────────── personajes ───────────────────────────────
class Personaje:
    """Un personaje del juego. El chico lee nombre, vida, vida_max, fuerza e inventario, y cambia vida, fuerza y
    nombre (cada cambio queda en el registro). Lo interno empieza con _ y el ejecutor no deja tocarlo."""
    __slots__ = ("_partida", "_id", "_tipo", "_nombre", "_vida", "_vida_max", "_fuerza", "_inventario", "_x", "_y")

    def __init__(self, partida, id_, tipo, nombre, vida, fuerza, x, y):
        for campo, valor in (("_partida", partida), ("_id", id_), ("_tipo", tipo), ("_nombre", nombre),
                             ("_vida", vida), ("_vida_max", vida), ("_fuerza", fuerza), ("_inventario", []),
                             ("_x", x), ("_y", y)):
            object.__setattr__(self, campo, valor)

    nombre = property(lambda self: self._nombre)
    vida = property(lambda self: self._vida)
    vida_max = property(lambda self: self._vida_max)
    fuerza = property(lambda self: self._fuerza)
    inventario = property(lambda self: self._inventario)

    def __setattr__(self, campo, valor):
        if campo == "vida":
            valor = _numero(valor, "La vida", 0, MAX_VIDA)
            object.__setattr__(self, "_vida", valor)
            if valor > self._vida_max:
                object.__setattr__(self, "_vida_max", valor)
        elif campo == "fuerza":
            object.__setattr__(self, "_fuerza", _numero(valor, "La fuerza", 0, MAX_FUERZA))
        elif campo == "nombre":
            object.__setattr__(self, "_nombre", _texto(valor, "El nombre", MAX_NOMBRE))
        else:
            raise ErrorJuego(f"Un personaje no tiene «{campo}» para cambiar. Se pueden cambiar vida, fuerza y nombre.")
        self._partida._anotar("cambia", id=self._id, campo=campo, valor=valor)

    def __str__(self):
        return self._nombre

    __repr__ = __str__


# ─────────────────────────────── la partida ───────────────────────────────
class Partida:
    """El registro de un juego. `linea` la actualiza el tracer del ejecutor (callback_linea), como en la tortuga."""

    def __init__(self, semilla, entradas=None, completar_con_vacio=False):
        self.azar = Azar(semilla)
        self.eventos = []
        self.personajes = []
        self.heroe_creado = False
        self.terminado = False
        self.linea = 0
        self._entradas = list(entradas or [])
        self._vacio = completar_con_vacio

    def callback_linea(self, numero):
        self.linea = numero

    def _anotar(self, evento, **datos):
        if self.terminado:
            return
        if len(self.eventos) >= MAX_EVENTOS:
            raise ErrorJuego("Tu juego hizo demasiadas cosas y lo frené. ¿Hay un mientras que no termina?")
        self.eventos.append({"t": evento, **datos, "l": self.linea})

    def _personaje(self, quien, que="Eso"):
        if not isinstance(quien, Personaje):
            raise ErrorJuego(f"{que} tiene que ser un personaje (creado con heroe o enemigo).")
        return quien

    def _crear(self, tipo, nombre, vida, fuerza):
        if len(self.personajes) >= MAX_PERSONAJES:
            raise ErrorJuego(f"Tu juego ya tiene {MAX_PERSONAJES} personajes: no entran más.")
        nombre = _texto(nombre, "El nombre", MAX_NOMBRE)
        vida = _numero(vida, "La vida", 1, MAX_VIDA)
        fuerza = _numero(fuerza, "La fuerza", 0, MAX_FUERZA)
        if tipo == "heroe":
            x, y = 1, 2
        else:
            enemigos = sum(1 for p in self.personajes if p._tipo == "enemigo")
            x, y = COLUMNAS - 2 - (enemigos // FILAS) % (COLUMNAS - 2), (2 + enemigos) % FILAS
        p = Personaje(self, len(self.personajes) + 1, tipo, nombre, vida, fuerza, x, y)
        self.personajes.append(p)
        self._anotar("entra", id=p._id, tipo=tipo, nombre=nombre, vida=vida, fuerza=fuerza, x=x, y=y)
        return p

    def globales(self):
        """Lo que el programa del chico puede usar (y nada más)."""
        def escena(lugar):
            if lugar not in LUGARES:
                raise ErrorJuego(f"No conozco el lugar «{str(lugar)[:20]}». Probá con: {', '.join(LUGARES)}.")
            self._anotar("escena", lugar=lugar)

        def heroe(nombre, vida, fuerza):
            if self.heroe_creado:
                raise ErrorJuego("Ya hay un héroe en este juego: se crea una sola vez.")
            p = self._crear("heroe", nombre, vida, fuerza)
            self.heroe_creado = True
            return p

        def enemigo(nombre, vida, fuerza):
            return self._crear("enemigo", nombre, vida, fuerza)

        def dado(caras=6):
            return self.azar.dado(_numero(caras, "Las caras del dado", 2, MAX_CARAS))

        def atacar(atacante, objetivo):
            a, b = self._personaje(atacante, "Quien ataca"), self._personaje(objetivo, "A quien atacás")
            dano = a._fuerza + self.azar.dado(6)
            object.__setattr__(b, "_vida", max(0, b._vida - dano))
            self._anotar("ataque", de=a._id, a=b._id, dano=dano, vida=b._vida)
            return dano

        def curar(quien, cantidad):
            p = self._personaje(quien, "A quien curás")
            cantidad = _numero(cantidad, "Lo que curás", 0, MAX_VIDA)
            object.__setattr__(p, "_vida", min(p._vida_max, p._vida + cantidad))
            self._anotar("cura", a=p._id, cantidad=cantidad, vida=p._vida)
            return p._vida

        def vivo(quien):
            return self._personaje(quien)._vida > 0

        def decir(quien, texto):
            p = self._personaje(quien, "Quien habla")
            self._anotar("dice", id=p._id, texto=_texto(texto, "Lo que dice"))

        def dar(quien, objeto):
            p = self._personaje(quien, "A quien le das")
            objeto = _texto(objeto, "El objeto", MAX_NOMBRE)
            if len(p._inventario) >= MAX_INVENTARIO:
                raise ErrorJuego(f"El inventario ya tiene {MAX_INVENTARIO} cosas: no entra más.")
            p._inventario.append(objeto)
            self._anotar("objeto", a=p._id, objeto=objeto)

        def tiene(quien, objeto):
            return objeto in self._personaje(quien)._inventario

        def mover(quien, columna, fila):
            p = self._personaje(quien, "A quien movés")
            x = _numero(columna, "La columna", 0, COLUMNAS - 1)
            y = _numero(fila, "La fila", 0, FILAS - 1)
            object.__setattr__(p, "_x", x)
            object.__setattr__(p, "_y", y)
            self._anotar("mueve", id=p._id, x=x, y=y)

        def mision(texto):
            self._anotar("mision", texto=_texto(texto, "La misión"))

        def ganar(texto="¡Ganaste!"):
            self._anotar("fin", gano=True, texto=_texto(texto, "El mensaje"))
            self.terminado = True

        def perder(texto="Perdiste. ¡Probá otra vez!"):
            self._anotar("fin", gano=False, texto=_texto(texto, "El mensaje"))
            self.terminado = True

        def mostrar(*valores, sep=" ", end="\n"):          # reemplaza a print dentro del juego
            texto = sep.join(como_texto(v) for v in valores)
            if len(texto) > MAX_TEXTO:
                raise ErrorJuego(f"Ese texto es muy largo (máximo {MAX_TEXTO} letras).")
            self._anotar("texto", texto=texto)

        def preguntar(pregunta=""):                        # reemplaza a input: la respuesta queda en el registro
            pregunta = str(pregunta)
            if self._entradas:
                respuesta = self._entradas.pop(0)
            elif self._vacio:
                respuesta = ""
            else:
                raise NecesitaEntrada(pregunta)
            self._anotar("responde", pregunta=pregunta, respuesta=respuesta)
            return respuesta

        return {"escena": escena, "heroe": heroe, "enemigo": enemigo, "dado": dado, "atacar": atacar,
                "curar": curar, "vivo": vivo, "decir": decir, "dar": dar, "tiene": tiene, "mover": mover,
                "mision": mision, "ganar": ganar, "perder": perder, "print": mostrar, "input": preguntar}


def sin_lineas(eventos):
    """Los eventos sin el número de línea: lo que se compara al evaluar (dos formas de escribir lo mismo valen)."""
    return [{k: v for k, v in e.items() if k != "l"} for e in eventos]


def correr_juego(fuente, semilla, entradas=None, completar_con_vacio=False):
    """Corre un juego con la implementación de referencia, en el ejecutor educativo (evaluación y validador).
    Devuelve lo mismo que el intérprete JS: {eventos, error, mensaje, linea, pregunta}."""
    partida = Partida(semilla, entradas, completar_con_vacio)
    python = fuente if detectar_tipo(fuente) == "python" else TraductorTortuScript().traducir_codigo(fuente)
    detalles = {}
    _, hay_error, mensaje = ejecutar_codigo(python, extra_globals=partida.globales(), callback_linea=partida.callback_linea,
                                            detalles=detalles, completar_con_vacio=False, semilla=semilla)
    linea = re.search(r"Mirá la línea (\d+)", mensaje or "") if hay_error else None
    return {"eventos": partida.eventos, "error": bool(hay_error), "mensaje": mensaje if hay_error else "",
            "linea": int(linea.group(1)) if linea else None, "pregunta": detalles.get("pregunta_pendiente")}

