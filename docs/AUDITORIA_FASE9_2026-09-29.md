# Auditoría Fase 9 — Proyecto integrador V1

Fecha: 2026-09-29

## Estado

**Fase 9 cerrada en la rama de trabajo.**

La fase implementa la transición desde ejercicios curriculares aislados hacia proyectos propios, persistentes, verificables y exportables.

## Criterios de cierre

- [x] ADR-024 aceptada.
- [x] Catálogo independiente del núcleo del motor.
- [x] Más de un proyecto disponible.
- [x] Cada proyecto integra al menos dos bloques entre Python, Web y SQL.
- [x] Desbloqueo basado en competencias/cursos completados.
- [x] Estado persistente por perfil.
- [x] Archivos iniciales y edición del proyecto.
- [x] Etapas secuenciales.
- [x] Criterios automáticos por etapa.
- [x] Validación de sintaxis Python cuando corresponde.
- [x] Validación estructural del catálogo.
- [x] Adaptación por franja pedagógica cuando el perfil la declara.
- [x] Ayudas graduadas.
- [x] Exportación ZIP sin ejecutar código en Flask.
- [x] Guía práctica de VS Code.
- [x] Nivel 0 actualizado con JSON, Git y GitHub.
- [x] Acceso desde menú y mapa.
- [x] Tests específicos de Fase 9.
- [x] Documentación de fase y handoff actualizados.
- [x] No se incorporó un LLM como dependencia.
- [x] No se avanzó a Fase 10.

## Seguridad

El servidor no ejecuta los archivos del proyecto del alumno para validarlos. Los criterios se comprueban sobre artefactos declarados y, para Python, mediante ast.parse.

Los nombres de archivos se normalizan y se rechazan rutas de escape. Se limita el número de archivos y el tamaño individual.

La exportación genera el ZIP en memoria y no ejecuta sus contenidos.

## Verificación

La rama mantiene el workflow Verificación Fase 0, configurado para ejecutar instalación con requirements.lock, tests Python/JavaScript y el validador de contenido.

La API de GitHub disponible durante esta sesión no devolvió ejecuciones asociadas a los commits recientes, por lo que CI remoto no queda declarado como verde. Esto es una limitación de verificación, no una afirmación de fallo del código.

Además, el entorno de trabajo de esta sesión no dispone de resolución de red para clonar el repositorio y ejecutar la suite localmente.

## Estado Git

La rama refactor/auditoria-2026-09-29 permanece 0 commits detrás de main, con PR #2 abierto y en borrador, sin merge a main.

El PR no se fusiona automáticamente: el cierre de la fase y el merge siguen siendo decisiones separadas.

## Fuera de alcance

Quedan fuera de esta fase: Tortu como asistente LLM, cuentas y sincronización cloud, marketplace, comunidad, analítica comercial y Fase 10.
