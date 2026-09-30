# ADR-016 — TortuScript como plataforma curricular progresiva

- Estado: Propuesta
- Fecha: 2026-09-29

## Contexto
El repositorio nació como una aplicación local para enseñar Python. La visión actual incluye alfabetización tecnológica, Python, Web esencial, SQL y posteriormente formación avanzada en desarrollo de aplicaciones, datos, infraestructura e IA.

## Decisión propuesta
TortuScript debe modelarse como plataforma y no como un único curso. El catálogo debe ser independiente del motor de ejecución y permitir nivel, edad, competencias, prerrequisitos, proyectos y estado de acceso.

Los repositorios avanzados permanecen externos y se utilizan como fuentes curriculares adaptables.

## Consecuencias
Positivas: crecimiento a múltiples áreas, adaptación por edad, reutilización curricular y futura separación entre contenido, identidad, progreso y acceso.

Costes: mayor complejidad documental y necesidad de versionar el modelo curricular.

## Fuera de alcance
Esta ADR no autoriza pagos, cuentas cloud, sincronización online, autenticación infantil ni migración del runtime local. Cada tema requiere su propia decisión.