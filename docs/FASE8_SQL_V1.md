# Fase 8 — SQL V1

Fecha: 2026-09-29

## Alcance
Se implementa la primera unidad curricular de SQL prevista por ADR-021.

Incluye:
- tablas, filas y columnas;
- SELECT;
- WHERE;
- ORDER BY y LIMIT;
- agregaciones;
- GROUP BY;
- JOIN y relaciones;
- seguridad básica y consultas de solo lectura.

El curso contiene 8 lecciones y 40 pasos.

## Evaluación
SQL se ejecuta sobre SQLite en memoria con datasets declarados como archivos de contenido. La consulta del alumno se compara contra la consulta oficial sobre el mismo dataset.

El evaluador:
- acepta consultas de lectura SELECT y WITH;
- bloquea operaciones de escritura y administración;
- bloquea ATTACH, PRAGMA, extensiones y funciones de acceso a archivos;
- rechaza múltiples consultas en un mismo ejercicio;
- limita longitud, cantidad de filas y operaciones de ejecución;
- no abre la base de datos persistente de TortuScript.

## Integración
El curso aparece en el orden curricular después de Web esencial y queda desbloqueado cuando el alumno completa Python V1 o Web esencial, según ADR-023.

El editor de la lección muestra el resultado de la consulta en una tabla. El servidor nunca ejecuta la consulta sobre una base real del producto.

## Fuera de alcance
No se implementan todavía:
- INSERT/UPDATE/DELETE como ejercicios;
- diseño avanzado de esquemas;
- índices y optimización;
- transacciones;
- administración de bases;
- conexión a bases externas;
- proyecto integrador.

## Verificación
La cobertura específica de la fase está en tests/test_fase8_sql.py.
