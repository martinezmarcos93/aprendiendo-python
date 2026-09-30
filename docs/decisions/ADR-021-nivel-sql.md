# ADR-021 — SQL como segundo bloque de datos

- Estado: Aceptada
- Fecha: 2026-09-29

## Contexto
SQL debe formar parte del itinerario inicial y tener más profundidad que la alfabetización Web, pero menos que Python.

## Decisión
El bloque inicial cubrirá tablas, filas, columnas, claves, SELECT, filtros, orden, agregaciones, JOIN, relaciones y seguridad básica.

Los ejercicios utilizarán bases pequeñas y contextos narrativos o de juego antes de introducir optimización o teoría avanzada.

## Consecuencia
SQL se convierte en una competencia funcional y puente hacia el nivel avanzado de datos.

La evaluación V1 se ejecutará únicamente sobre bases SQLite en memoria construidas desde datos declarados por la lección. El alumno solo podrá ejecutar consultas de lectura (`SELECT` y consultas equivalentes de lectura); se rechazarán operaciones de escritura, administración de la base, acceso a archivos, extensiones y conexiones externas. Las consultas tendrán límites de tamaño y pasos de ejecución.