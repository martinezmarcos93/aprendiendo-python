# ADR-023 — Recorridos iniciales después de Nivel 0

- Estado: Aceptada
- Fecha: 2026-09-29

## Contexto

Después de la alfabetización digital, el alumno no debe quedar atado a un único camino lineal. La plataforma necesita presentar las tres áreas iniciales que forman el producto: Web (HTML + CSS + JavaScript), Python y SQL.

## Decisión

Al completar Nivel 0, Tortu presenta una elección de recorrido:

1. HTML + CSS + JavaScript.
2. Python.
3. SQL.

HTML + CSS + JavaScript y Python quedan disponibles inmediatamente después de Nivel 0.

SQL queda visible desde el inicio, pero bloqueado hasta que el alumno complete uno de los dos recorridos iniciales: Web o Python.

La elección inicial se guarda en el progreso local y puede cambiarse posteriormente desde el Mapa de progreso.

El Mapa de progreso muestra siempre el mapa de cada curso, incluso cuando el curso está bloqueado. Un curso bloqueado muestra su condición de acceso en lugar de desaparecer.

## Alcance

Esta decisión modifica navegación, persistencia del recorrido y visualización del mapa. No implementa todavía el contenido pedagógico de SQL.

## Regla de producto

La elección de recorrido orienta el siguiente paso del alumno, pero no convierte el recorrido elegido en una restricción irreversible.
