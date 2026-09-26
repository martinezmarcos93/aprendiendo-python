# Modelo de amenazas: runtime de juegos (TortuGame)

> **Estado: EXPERIMENTAL — diseño en papel, sin implementación.** Es el requisito previo que pide
> [ADR-007](../decisions/ADR-007-seguridad-runtime-de-juegos.md) antes de construir la Fase 3. ADR-006, 007 y 008 siguen en
> *Propuesta*: este documento no autoriza implementar nada. Sirve para que Marcos decida si las acepta. 26/09/2026.

## 1. Qué se protege

| Activo | Por qué importa |
|---|---|
| La compu del chico | el código lo escribe un chico (o lo copia de internet): no puede tocar archivos, red ni otras apps |
| El progreso y los proyectos del perfil | no pueden borrarse ni alterarse desde un juego |
| Los otros perfiles de la misma compu | un juego de un hermano no puede leer ni cambiar el progreso de otro |
| La página de TortuScript | un juego no puede cambiar la interfaz, engañar al chico ni robar el token de la sesión |
| La disponibilidad | un juego trabado no puede colgar la pestaña ni la compu |

## 2. Quién puede hacer daño (sin mala intención, casi siempre)

1. **El chico que se equivoca:** bucles infinitos, listas enormes, recursión sin fin.
2. **El chico curioso:** prueba cosas que vio en internet (`fetch`, `document`, `localStorage`, `eval`).
3. **Código copiado de afuera:** un "truco" pegado de un video o foro que intenta algo más.
4. **Un proyecto compartido:** hoy no existe (ADR-010/011), pero si algún día se comparten juegos, el código de otro
   pasa a ser una entrada no confiable.

El contenido de las lecciones (`contenido/cursos/*.json`) es **confiable**: lo escribe el equipo y lo revisa el validador.

## 3. Arquitectura que se asume (de ADR-006/007)

```
Código TortuScript → parser → AST propio → validador → intérprete TortuGame (en un Web Worker)
                                                              │ mensajes (postMessage: datos, nunca código)
                                                              ▼
                                               hilo principal: dibuja en <canvas>
```

- **Nunca** se genera JavaScript para ejecutarlo (`eval`, `new Function`, `setTimeout("…")`, `<script>` armado).
- El intérprete solo expone la API TortuGame; lo que no está en la API, no existe para el programa del chico.

## 4. Amenazas y defensas

| # | Amenaza | Ejemplo | Defensa principal | Segunda barrera | Cómo se prueba |
|---|---|---|---|---|---|
| A1 | Ejecutar JS arbitrario | el chico escribe `eval("…")` o `constructor.constructor` | el intérprete no traduce a JS: `eval`, `constructor`, `__proto__`, `prototype` no son nombres válidos del lenguaje | CSP sin `unsafe-eval` en la página y en el worker | test: el validador rechaza esos nombres; test: la CSP no incluye `unsafe-eval` |
| A2 | Contaminar prototipos del intérprete | un objeto del juego con clave `__proto__` | los objetos del juego viven en `Map` o en objetos sin prototipo (`Object.create(null)`) | nombres con `__` prohibidos (como hoy en el ejecutor de Python) | test con claves `__proto__`, `constructor`, `toString` |
| A3 | Red y exfiltración | `fetch`, `WebSocket`, `XMLHttpRequest`, `importScripts` | la API no los expone | CSP del worker: `connect-src 'none'`, `script-src 'self'` sin `blob:` | test: el worker no puede abrir ninguna conexión (se verifica en el navegador con Playwright) |
| A4 | Tocar la página (DOM, token) | leer `document.cookie` o el token de la API | el worker no tiene DOM; el token nunca se le pasa | los mensajes hacia la página son datos validados (tipo de orden, números, textos cortos) | test: mensajes con campos de más o tipos raros se descartan |
| A5 | XSS por los textos del juego | un personaje llamado `<img onerror=…>` | la página pinta textos con `textContent` o en el canvas, nunca con `innerHTML` | CSP estricta ya vigente (`script-src 'self'`) | test: nombres con `<script>` se ven como texto |
| A6 | Leer o romper el progreso | `localStorage`, `IndexedDB` o la API de progreso | la API TortuGame no los expone; el guardado de partidas (si existe) es un espacio propio por perfil y proyecto, con tamaño máximo | el servidor valida todo lo que se guarda (como hoy con los proyectos) | test: guardar de más o con claves raras se rechaza |
| A7 | Colgar la pestaña (CPU) | `mientras verdadero:` sin nada adentro | tope de instrucciones por cuadro y total, y tope de tiempo; al pasarse, el juego se frena con un mensaje amable | el worker se puede terminar (`terminate`) desde la página sin trabarla | test: un bucle infinito se frena en menos de X segundos |
| A8 | Agotar la memoria | listas o textos gigantes, recursión sin fin | topes de tamaño de listas, de largo de textos y de profundidad de llamadas | `terminate()` del worker si deja de responder | test por cada tope |
| A9 | Saturar el dibujo | miles de entidades o de órdenes por cuadro | tope de entidades y de órdenes de dibujo por cuadro | el hilo principal ignora lo que pase del tope | test con 10.000 entidades |
| A10 | Engañar al chico | un juego que imita la pantalla de TortuScript ("ingresá tu contraseña") | el juego solo dibuja dentro de su canvas, con marco propio; no hay campos de texto libres fuera de `preguntar` | no hay cuentas ni contraseñas en la app (ADR-003) | revisión manual de la interfaz |
| A11 | Evaluación manipulable | el programa detecta que lo están evaluando y hace trampa | evaluación determinista con semilla (ADR-009), sin decirle al programa si es una evaluación | el resultado lo calcula quien evalúa, no el juego | test: mismo código y semilla dan el mismo resultado |
| A12 | Código compartido de otros (futuro) | un juego ajeno con algo de A1–A10 | todo lo anterior aplica igual: el runtime no confía en ningún código | compartir queda fuera de la V1 (ADR-010/011) | — |

## 5. Topes iniciales propuestos (a calibrar con juegos reales)

| Recurso | Tope | Referencia |
|---|---|---|
| Instrucciones por cuadro | 50.000 | el ejecutor de Python usa 50.000 pasos en total |
| Tiempo sin ceder el control | 200 ms | para que la animación no se trabe |
| Entidades vivas | 500 | un RPG por turnos chico usa decenas |
| Elementos por lista | 10.000 | |
| Largo de un texto | 2.000 caracteres | |
| Profundidad de llamadas | 200 | |
| Tamaño de una partida guardada | 50 KB | |

## 6. Lo que queda fuera de este modelo

- **Pygame o Python real en el navegador** (ADR-006: horizonte, no arquitectura inicial).
- **Ejecutar código de chicos en un servidor remoto** (ADR-014: requiere su propia ADR).
- **Multijugador y red** (ADR-008: fuera del alcance de la v1).

## 7. Qué haría falta para aceptar ADR-006/007/008

1. Que Marcos acepte este modelo (o lo corrija).
2. Una especificación de la API TortuGame v1 (RPG por turnos, ADR-008) en español, con cada función y sus topes.
3. Un prototipo del intérprete **solo con tests**, antes de cualquier pantalla, que pase los tests de A1–A9.
