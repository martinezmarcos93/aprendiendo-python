# TortuGame v1 — especificación

Runtime de juegos de TortuScript (ADR-006, 007, 008 y 009, aceptadas). **v1 = juego de rol por turnos.**

## Cómo funciona

```
TortuScript ─► traductor (el de siempre) ─► Python ─► ast.parse ─► lista blanca ─► AST propio (JSON)
                                                     (servidor: solo analiza, no ejecuta)          │
                                                                                                    ▼
                                  página ◄── registro de eventos ◄── intérprete TortuGame (JS, en un Web Worker)
                                  (canvas + texto)
```

- **El navegador nunca recibe código:** recibe un árbol JSON con solo los nodos permitidos. No hay `eval`, `new Function`
  ni JavaScript generado (ADR-007).
- El intérprete corre en un **Web Worker** con su propia CSP (`connect-src 'none'`): no ve la página, el token ni la red.
- El programa corre **hasta el final** y deja un **registro de eventos** que la página anima. Por turnos: no hay bucle de
  animación que programar.
- **Determinista (ADR-009):** el azar sale de un generador propio (mulberry32) igual en JS y en Python. Misma semilla,
  mismo código → mismo registro.
- **Evaluación en el servidor:** para las lecciones, el servidor corre el programa con la implementación de referencia en
  Python (`tortuscript/tortugame.py`) en el ejecutor educativo y compara el registro con el de la solución. Así el XP lo
  sigue calculando el servidor. Tests de conformidad exigen que JS y Python den **el mismo registro**.

## La API (en español)

| Función | Qué hace | Devuelve |
|---|---|---|
| `escena(lugar)` | cambia el fondo: `"aldea"`, `"bosque"`, `"cueva"`, `"mazmorra"` o `"castillo"` | — |
| `heroe(nombre, vida, fuerza)` | crea al héroe (uno solo por juego) | el héroe |
| `enemigo(nombre, vida, fuerza)` | crea un enemigo | el enemigo |
| `atacar(atacante, objetivo)` | el daño es `fuerza + dado(6)`; se resta de la vida del objetivo (nunca baja de 0) | el daño |
| `curar(quien, cantidad)` | suma vida, hasta su vida máxima | la vida nueva |
| `vivo(quien)` | ¿le queda vida? | `verdadero` / `falso` |
| `decir(quien, texto)` | un globo de diálogo | — |
| `dar(quien, objeto)` | agrega un objeto (texto) al inventario | — |
| `tiene(quien, objeto)` | ¿lo lleva en el inventario? | `verdadero` / `falso` |
| `mover(quien, columna, fila)` | lo ubica en el mapa (8 columnas × 5 filas, desde 0) | — |
| `mision(texto)` | muestra el objetivo del juego | — |
| `ganar(texto)` / `perder(texto)` | termina el juego | — |
| `dado(caras)` | un número de 1 a `caras` (6 si no se dice) | el número |
| `mostrar …` | escribe en el registro del juego | — |

Cada personaje tiene `nombre`, `vida`, `vida_max`, `fuerza` e `inventario` (una lista). Se leen con un punto
(`heroe.vida`) y se pueden cambiar `vida`, `fuerza` y `nombre` (`heroe.fuerza es heroe.fuerza + 2`).

El resto del lenguaje es el de siempre: variables, cuentas, `si`/`sino`, `repetir`, `mientras`, `para … en`, funciones,
listas y `preguntar` (el juego se vuelve a correr con las respuestas, como en las lecciones).

## Eventos del registro

`{"t": "escena"|"entra"|"ataque"|"cura"|"dice"|"objeto"|"mueve"|"mision"|"cambia"|"texto"|"fin", …, "l": línea}`.
Los campos de cada uno están en `tortuscript/tortugame.py` (fuente de verdad) y los tests de conformidad los comparan.

## Topes (modelo de amenazas, A7–A9)

| Recurso | Tope |
|---|---|
| Pasos del intérprete | 200.000 |
| Personajes | 50 |
| Elementos por lista | 10.000 |
| Largo de un texto | 2.000 caracteres |
| Profundidad de llamadas | 100 |
| Eventos del registro | 2.000 |
| Tiempo del worker | 3 s (después la página lo termina) |

## Fuera de la v1
Guardado de partidas (tiene que pasar por el servidor con tope y validación: A6), tiempo real, sonido, sprites propios,
Pygame (horizonte, ADR-006).
