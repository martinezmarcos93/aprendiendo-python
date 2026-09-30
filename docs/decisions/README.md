# Decisiones de arquitectura (ADR)

## Regla de gobernanza

> **Propuesta ≠ decisión aprobada.** Una ADR en estado *Propuesta* puede orientar el diseño, pero **no autoriza implementación**. Solo una ADR *Aceptada* puede usarse como fundamento para modificar la arquitectura o el comportamiento. Si una implementación contradice una ADR Aceptada, primero se modifica la ADR y después el código.
>
> Solo Marcos cambia el estado de una ADR. Los documentos de `docs/experimental/` son ideas, no decisiones: nada de lo que dicen se implementa sin una ADR Aceptada que lo cubra.

Las medidas de endurecimiento que no condicionan el modelo de producto, por ejemplo security headers/CSP, no necesitan ADR.

## Tablero

| ADR | Tema | Estado |
|-----|------|--------|
| [ADR-001](ADR-001-migracion-a-web.md) | Migración a web (Flask local) | Aceptada |
| [ADR-002](ADR-002-cursos-como-datos-y-progreso-aditivo.md) | Cursos como datos / progreso aditivo | Aceptada |
| [ADR-003](ADR-003-producto-local-y-validacion.md) | Producto local y validación antes de crecer | Aceptada |
| [ADR-004](ADR-004-diagnostico-y-continuidad.md) | Diagnóstico y continuidad del camino | Aceptada |
| [ADR-005](ADR-005-intereses-locales.md) | Intereses y feedback locales | Aceptada |
| [ADR-006](ADR-006-runtime-educativo-y-de-juegos.md) | Runtime educativo / runtime de juegos | Aceptada |
| [ADR-007](ADR-007-seguridad-runtime-de-juegos.md) | Seguridad del runtime de juegos | Aceptada |
| [ADR-008](ADR-008-alcance-tortugame-v1.md) | Alcance de TortuGame v1 (RPG por turnos) | Aceptada |
| [ADR-009](ADR-009-determinismo.md) | Determinismo y azar controlado (dado) | Aceptada |
| [ADR-010](ADR-010-sin-comunidad-v1.md) | Sin comunidad en la V1 | Aceptada |
| [ADR-011](ADR-011-proyectos-privados.md) | Proyectos privados por defecto | Aceptada |
| [ADR-012](ADR-012-cuenta-adulto-perfiles-hijo.md) | Cuenta adulta → perfiles hijo | Aceptada (implementación condicionada por ADR-003) |
| [ADR-013](ADR-013-desktop-y-cloud.md) | TortuScript Desktop / Cloud | Aceptada |
| [ADR-014](ADR-014-ejecucion-de-codigo-del-alumno.md) | Ejecución del código del alumno | Aceptada |
| [ADR-015](ADR-015-distribucion-a-familias.md) | Instaladores para las familias (Windows / Linux) | Aceptada |
| [ADR-016](ADR-016-vision-plataforma.md) | TortuScript como plataforma curricular progresiva | Propuesta |
| [ADR-017](ADR-017-modelo-curricular-por-edades.md) | Edad y nivel como dimensiones curriculares | Propuesta |
| [ADR-018](ADR-018-fuentes-curriculares-externas.md) | Repositorios avanzados como fuentes curriculares | Propuesta |
| [ADR-019](ADR-019-estados-de-acceso.md) | Estados de acceso independientes del motor | Propuesta |
| [ADR-020](ADR-020-nivel-web-esencial.md) | HTML/CSS/JS como alfabetización web | Aceptada |
| [ADR-021](ADR-021-nivel-sql.md) | SQL como segundo bloque de datos | Aceptada |
| [ADR-022](ADR-022-preparacion-saas-sin-implementacion.md) | Preparación comercial sin SaaS en V1 | Propuesta |
| [ADR-023](ADR-023-recorridos-iniciales.md) | Recorridos iniciales después de Nivel 0 | Aceptada |

## Documentos de producto

- [PRODUCTO_V1](../PRODUCTO_V1.md)
- [ROADMAP V1 hasta 31/12/2026](../ROADMAP_V1_2026-12-31.md)
- [Catálogo curricular V1](../catalogo_curricular_v1.json)
