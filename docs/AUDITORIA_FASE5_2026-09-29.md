# Fase 5 — Nivel 0: alfabetización tecnológica

## Estado

Fase 5 implementada sobre la rama de trabajo el 29/09/2026.

## Objetivo

Crear un primer nivel breve e interactivo que dé al alumno un mapa mental del mundo digital antes de profundizar en programación.

## Contenido

Se agregó el curso `alfabetizacion-digital` con 13 lecciones:

1. programa;
2. lenguaje de programación;
3. código;
4. navegador;
5. Internet y redes;
6. servidor;
7. frontend;
8. backend;
9. datos;
10. base de datos;
11. API;
12. seguridad digital;
13. integración de una aplicación.

El contenido se divide en dos secciones: piezas del mundo digital y datos/servicios/seguridad.

## Diseño pedagógico

El curso no introduce una asignatura teórica extensa. Cada lección parte de una explicación breve y utiliza desafíos de reconocimiento, predicción u ordenamiento.

Las actividades usan exclusivamente los tipos de paso ya soportados por el motor. No se agregó lógica especial al runtime.

La última lección integra el mapa mental: persona → frontend → backend → datos → respuesta → frontend.

## Integración

El nuevo curso se incorpora al inicio de `ORDEN_CURSOS`, sin cambiar `CURSO_PRINCIPAL`. Esto preserva la compatibilidad del sistema de ejercicios históricos de `primeros-pasos`.

Se agregó cobertura en `tests/test_contenido.py` para:

- existencia del curso;
- sus 13 lecciones;
- conceptos obligatorios;
- estructura mínima de las lecciones;
- pistas propias de los pasos interactivos.

El catálogo curricular también registra las unidades y competencias del Nivel 0.

## Decisiones de alcance

No se implementaron:

- nuevas pantallas;
- nuevos tipos de paso;
- cambios en el runtime;
- Python V1;
- HTML/CSS/JS;
- SQL;
- acceso premium;
- cuentas o cloud.

La Fase 5 queda limitada al contenido y su integración con el camino existente.

## Verificación

El workflow de GitHub Actions asociado al commit de cierre ejecutó correctamente 478 tests Python/JavaScript y el validador de contenido. El Nivel 0 reportó 52 pasos revisados, 0 errores y 0 avisos. El resto del contenido mantiene 3 avisos históricos de equivalencia en pasos `ordenar`, sin errores.

Durante la verificación también se corrigió una regresión pendiente del traductor: `mostrar` ahora se reconoce correctamente cuando recibe una expresión indexada como una lista.

## Criterio de cierre

Fase 5 queda cerrada cuando el curso nuevo pasa el validador de contenido y la suite de tests, y el camino conserva la compatibilidad con el progreso histórico.

La ejecución automática queda delegada a GitHub Actions; su resultado se registra cuando termine el run correspondiente.
