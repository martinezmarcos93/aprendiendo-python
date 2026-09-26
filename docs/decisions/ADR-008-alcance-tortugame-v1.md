# ADR-008: Alcance inicial de TortuGame

## Estado: Aceptada (26/09/2026) — decisión de Marcos

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Decisión
**TortuGame v1 = RPG por turnos.** Entidades acotadas: personaje, enemigos, estadísticas, combate, inventario, objetos,
escenas, diálogos, mapa, misiones, estado y guardado.

**Fuera de alcance:** Pygame, multijugador, red, física compleja, 3D, editor libre de niveles, otros géneros.

## Consecuencias
+ Un sistema chico que el chico puede entender entero, y que se puede probar con evaluación determinista ([ADR-009](ADR-009-determinismo.md)).
− Otros géneros (estrategia, plataformas) esperan a que el RPG demuestre tracción (Puerta 2).

## Notas de implementación (26/09/2026)
Implementado: escenas, héroe y enemigos con estadísticas, combate con dados, curar, diálogos, inventario, mapa de 8×5,
misiones, ganar/perder y `preguntar`. **Pendiente:** guardado de partidas (tiene que pasar por el servidor con topes, A6).
