# ADR-006: Separación del runtime educativo y el runtime de juegos

## Estado: Aceptada (26/09/2026) — decisión de Marcos

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
Hoy TortuScript se traduce a Python y corre en un subproceso local controlado (AST validado, sin `import`, builtins
limitados, límites de tiempo, memoria, pasos y salida). La academia de juegos propone una API propia (TortuGame) que
corre en el navegador. Eso convierte a TortuScript en un lenguaje educativo con **dos destinos**, no en un simple
pseudolenguaje traducido a Python.

## Decisión
```
Runtime educativo:  TortuScript → Python → subproceso local controlado     (se mantiene)
Runtime de juegos:  TortuScript → TortuGame → intérprete propio → Canvas    (sistema aparte)
```
- Son dos sistemas distintos. **No** se reutiliza el ejecutor educativo para juegos solo porque "ya tiene sandbox".
- `TortuGame → Python/Pygame` queda como **horizonte pedagógico**, no como parte de la arquitectura inicial: no se diseña
  una abstracción que tenga que funcionar igual sobre Python, JS y Pygame.
- El curso piloto "Tortuaria" (RPG por consola) usa el **runtime educativo** y no depende de esta ADR.

## Consecuencias
+ Cada runtime tiene un modelo de seguridad simple y propio.
− El traductor actual solo produce Python: el runtime de juegos necesita su propio parser/intérprete.

## Notas de implementación (26/09/2026)
- Runtime de juegos: `web/static/js/tortugame/interprete.js` (Web Worker) sobre el árbol JSON de `tortuscript/juego_ast.py`.
  Página 🎮 Juegos (`/juego`) y tipo de proyecto `juego`.
- **Para Marcos (confirmar):** las **lecciones** de juegos se evalúan en el servidor con una implementación de
  referencia en Python (`tortuscript/tortugame.py`) que corre en el ejecutor educativo. Motivo: que el XP lo siga
  calculando el servidor (integridad de la gamificación, §20 de seguridad) y que el validador pueda revisar el contenido.
  No reemplaza al runtime de juegos: el juego se **juega** en el intérprete JS. Tests de conformidad
  (`tests/test_tortugame.py`) exigen que las dos den el mismo registro de eventos.
- Diferencias conocidas y documentadas: después de que una función devuelve, JS marca la línea que la llamó y Python la
  última de adentro (solo afecta el resaltado); números enteros más allá de 2^53 dan error en JS; `range` se muestra como
  lista en JS.
