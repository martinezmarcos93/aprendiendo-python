# ADR-007: Seguridad del runtime de juegos

## Estado: Aceptada (26/09/2026) — decisión de Marcos

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
"Corre en el navegador" no significa "es seguro". **Un Web Worker no es por sí mismo un sandbox suficiente**: por
defecto tiene `fetch`, `WebSocket`, `IndexedDB` e `importScripts`.

## Decisión
```
Código TortuScript → parser → AST propio → validador → intérprete TortuGame → Web Worker → Canvas
```
y **nunca**:
```
TortuScript → JavaScript generado → eval() / new Function()
```
- El código del chico solo puede hacer lo que el intérprete expone mediante la API TortuGame: la seguridad es una
  propiedad del lenguaje/runtime, no de las restricciones del navegador.
- **Permitido:** Canvas (a través del hilo principal), API TortuGame, límites de memoria, tiempo, ticks/instrucciones,
  cantidad de entidades y salida.
- **Prohibido:** red (`fetch`, `XMLHttpRequest`, `WebSocket`), cookies, `localStorage`/`IndexedDB` arbitrarios, DOM,
  sistema de archivos, navegación, `import`/`importScripts`, APIs externas.
- Segunda barrera: CSP estricta para el worker (`connect-src 'none'`, sin `unsafe-eval`).
- Antes de implementar hace falta un **modelo de amenazas** escrito del runtime. Borrador (26/09/2026):
  [`docs/experimental/MODELO_DE_AMENAZAS_RUNTIME_JUEGOS.md`](../experimental/MODELO_DE_AMENAZAS_RUNTIME_JUEGOS.md).

## Consecuencias
+ Superficie de ataque acotada y verificable con tests.
− Escribir un intérprete propio es más trabajo que generar JS.

## Notas de implementación (26/09/2026)
- Árbol propio con lista blanca en el servidor (`juego_ast.py`): sin `import`, nombres internos, lambdas, clases,
  funciones anidadas, porciones, argumentos con nombre ni atributos fuera de `nombre/vida/vida_max/fuerza/inventario`.
- Intérprete sin `eval`/`Function`/red/almacenamiento/DOM; variables en `Map`, personajes sellados; el intérprete revalida
  cada nodo. Topes: 200.000 pasos, 100 de profundidad, 50 personajes, 2.000 eventos, listas de 10.000, textos de 100.000.
- El script del Worker se sirve con `Content-Security-Policy: default-src 'none'; script-src 'self'` (sin red).
- La página termina el Worker a los 3 s. Tests: `tests/js/tortugame.test.mjs` (A1, A2, A5, A7, A8, A9) y
  `tests/test_tortugame.py`. Pendiente del modelo: guardado de partidas (A6), que no está en la v1.
