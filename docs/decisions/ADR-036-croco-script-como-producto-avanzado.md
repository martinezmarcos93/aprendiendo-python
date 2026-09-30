# ADR-036 — Croco-Script como producto avanzado separado

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Decide:** El nivel avanzado de TortuScript se desarrollará como un producto/aplicación separada denominada provisionalmente **Croco-Script**.
- **Relacionadas:** ADR-018, ADR-028, ADR-029, ADR-030, ADR-032, ADR-035

## Contexto

TortuScript V1 tiene como objetivo principal ofrecer una experiencia educativa sólida para niños. El catálogo avanzado existente en repositorios externos incluye tres líneas de profundidad considerable:

1. Python + Datos.
2. Desarrollo de Aplicaciones.
3. Orquestación, streaming y LLM.

Forzar estos tres recorridos dentro del release comercial inicial de TortuScript introduciría complejidad curricular, técnica y de producto que no es necesaria para validar y lanzar el núcleo infantil.

Además, existe una ventana temporal razonable durante la cual la mayoría de los alumnos todavía no necesitará acceder al nivel avanzado.

## Decisión

El nivel avanzado no se llamará TortuScript 2. El producto avanzado se denominará **Croco-Script**, como evolución conceptual de tortuga a cocodrilo.

Croco-Script será una aplicación/repositorio separado, integrado comercialmente con TortuScript.

La separación será de producto y de repositorio, no de identidad de ecosistema. Un alumno con acceso autorizado deberá poder pasar desde TortuScript a Croco-Script sin crear una segunda cuenta.

## Alcance de Croco-Script

Croco-Script incorporará progresivamente:

- Python aplicado a datos.
- Desarrollo de aplicaciones.
- Orquestación y streaming.
- LLM y sistemas de IA.
- Proyectos de mayor complejidad.
- Herramientas y dinámicas pedagógicas adecuadas al nivel avanzado.
- Runtime y sandbox apropiados para los nuevos tipos de proyectos.
- Sistema de progreso y evaluación compatible con el modelo de aprendizaje de TortuScript.

Los tres repositorios curriculares externos siguen siendo fuentes de contenido y diseño curricular. Su incorporación a Croco-Script requerirá adaptación pedagógica, normalización de formatos y validación dentro del nuevo producto.

## Qué entra en TortuScript V1

TortuScript V1 mantiene como núcleo:

- alfabetización digital;
- Python inicial/intermedio;
- HTML/CSS/JavaScript;
- SQL;
- juegos;
- proyectos;
- progresión;
- perfiles familiares;
- contenido gratuito y premium;
- ejecución segura;
- Tortu-LLM como tutor opcional.

Los cursos avanzados no son requisito del gate de V1.0.0.

## Estrategia temporal

Antes de V1.0.0 sí se preparará la infraestructura conceptual y técnica que Croco-Script necesitará para integrarse:

- contrato de identidad;
- modelo de entitlement;
- autorización entre aplicaciones;
- formato curricular;
- contrato de progreso;
- arquitectura del runtime;
- arquitectura del Tutor/LLM;
- estructura inicial del repositorio Croco-Script;
- prototipos técnicos necesarios para reducir riesgo.

No es obligatorio completar los tres cursos avanzados antes del release de TortuScript V1.

Después de estabilizar V1, el desarrollo de Croco-Script podrá acelerarse de forma independiente.

## Principio de experiencia

Croco-Script no será simplemente una copia de TortuScript con cursos más difíciles.

El cambio de tortuga a cocodrilo representa un salto de nivel:

- mayor autonomía;
- problemas más abiertos;
- proyectos más extensos;
- herramientas más cercanas al desarrollo real;
- menor dependencia de ejercicios guiados.

Sin embargo, conserva la filosofía pedagógica del ecosistema: progresión, práctica, diagnóstico, proyectos y asistencia.

## Consecuencias

### Positivas

- V1 puede concentrarse en su público principal.
- Se reduce el riesgo de retrasar el release.
- Croco-Script puede evolucionar con un ciclo propio.
- Los cursos avanzados no contaminan innecesariamente el núcleo infantil.
- Se puede diseñar una experiencia visual y pedagógica distinta para alumnos avanzados.
- La transición comercial puede conservar una única cuenta familiar.

### Costes

- Habrá dos aplicaciones/repositorios que mantener.
- Se necesita un mecanismo sólido de autenticación/autorización entre productos.
- El progreso avanzado debe tener un contrato de datos estable.
- Habrá que definir dominios, despliegues, observabilidad y versionado de ambos productos.

## Criterio de no implementación

No se considera terminado Croco-Script por tener solamente un repositorio creado. La preparación previa a V1 debe limitarse a reducir los riesgos de integración y a construir los componentes cuya reutilización posterior sea clara.

La implementación curricular completa de Croco-Script queda fuera del gate de V1.0.0.

## Resultado esperado

Cuando un alumno alcance el nivel avanzado y su cuenta familiar posea el entitlement correspondiente, TortuScript podrá derivarlo a Croco-Script como parte del mismo ecosistema, sin duplicar su identidad ni su suscripción.
