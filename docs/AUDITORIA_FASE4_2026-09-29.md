# Auditoría Fase 4 — Consolidación técnica — 29/09/2026

## Alcance

Se revisaron los puntos del núcleo que condicionan la V1:

- traductor TortuScript → Python;
- validación AST;
- ejecución educativa;
- proceso hijo;
- límites de tiempo, CPU, memoria y salida;
- runtime TortuGame;
- evaluación determinista;
- contenido y validador;
- progreso y compatibilidad;
- pruebas de conformidad entre runtimes.

## Hallazgos

### Traductor

El traductor actual conserva una línea de Python por línea de TortuScript, usa tokenize y evita sustituir palabras dentro de strings/comentarios.

La regresión conocida de índices después de listas ya quedó cubierta en tests/test_translator.py.

### Ejecución

El runtime valida el AST antes de ejecutar.

La ejecución web no ocurre dentro del proceso Flask: el servidor delega el pedido a tortuscript.worker mediante tortuscript.proceso.

El worker usa:

- límite de pasos;
- límite de salida;
- builtins restringidos;
- bloqueo de imports;
- bloqueo de nombres y atributos internos;
- límite de tiempo del proceso padre;
- límite de CPU y memoria en Linux/macOS;
- límite de memoria mediante Job Object en Windows.

### TortuGame

TortuGame convierte el programa a un AST JSON propio y aplica la misma validación previa del runtime educativo.

Se añadió tests/test_runtime_conformidad.py para verificar que ambos caminos aceptan un programa básico y rechazan las mismas categorías de construcciones no permitidas.

### Evaluación

La evaluación utiliza SEMILLA_EVALUACION para ejercicios donde el resultado debe ser reproducible. Esto mantiene la equivalencia entre ejecución del alumno y solución oficial.

### Contenido

El contenido sigue siendo dato independiente del código del motor. El validador comprueba estructura, ejecución de ejemplos, soluciones, pistas, dibujos, laberintos y determinismo.

El orden de los ejercicios escribir del curso principal continúa protegido por tests porque sus posiciones forman parte del progreso histórico.

### Progreso

No se modificó el esquema de progreso durante estas fases. Esto evita introducir una migración prematura mientras todavía se está diseñando el nuevo catálogo curricular.

## Riesgos residuales

1. El runtime local no debe considerarse un sandbox para código hostil. Su objetivo es ejecución educativa controlada.
2. En Windows el aislamiento de CPU no equivale al de Linux/macOS; el proceso padre conserva el límite de tiempo.
3. La migración del formato operativo de cursos al nuevo catálogo todavía no debe realizarse.
4. La validación completa mediante GitHub Actions sigue dependiendo de que el entorno exponga los runs; no se inventan resultados ausentes.

## Decisión de consolidación

No se detectó una inconsistencia crítica que justifique cambiar el modelo de ejecución durante Fase 4.

Se conserva la arquitectura actual y se añade cobertura de conformidad donde había riesgo de divergencia entre runtimes.

## Criterio de cierre

Fase 4 queda cerrada cuando:

- el núcleo está auditado;
- las restricciones de seguridad conocidas están documentadas;
- la evaluación determinista está protegida;
- el contenido y progreso existentes conservan sus contratos;
- existe una prueba de conformidad entre runtime educativo y TortuGame;
- no se introducen cambios de producto ni de SaaS en esta fase.
