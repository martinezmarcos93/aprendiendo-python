# Fase 11 — Arquitectura web/comercial futura V1

## Principio

La plataforma debe separar identidad adulta, perfiles educativos, currículo, progreso y acceso comercial. La V1 actual sigue siendo local-first; este documento define la futura arquitectura sin convertirla todavía en SaaS.

## Componentes

- Cuenta adulta: identidad, autenticación, consentimiento y relación con perfiles.
- Perfil educativo: alias, franja pedagógica, progreso y preferencias. No necesita publicar datos identificatorios.
- Catálogo: unidades, competencias, prerrequisitos y versiones.
- Progreso sincronizado: eventos mínimos de aprendizaje o snapshots verificables.
- Acceso: regla pedagógica + estado comercial. Un paywall nunca debe decidir si una competencia existe.
- Suscripción: proveedor externo aislado detrás de una interfaz de acceso.
- Exportación/eliminación: operaciones explícitas sobre los datos del adulto y de cada perfil.

## Flujo futuro

1. La persona adulta crea o accede a su cuenta.
2. Acepta las condiciones y, cuando corresponda, el consentimiento de tratamiento.
3. Crea un perfil educativo.
4. El perfil recibe una configuración pedagógica, no una identidad pública.
5. El catálogo calcula qué contenido corresponde.
6. El motor registra progreso mínimo.
7. La capa de acceso resuelve disponibilidad pedagógica y comercial por separado.
8. La interfaz muestra solamente el contenido autorizado.
9. Exportación y eliminación operan sobre datos asociados a la cuenta.

## Separaciones obligatorias

La futura aplicación no debe:

- guardar datos de menores en logs de aplicación innecesarios;
- usar el nombre real del menor como identificador técnico;
- mezclar pagos con el motor de evaluación;
- enviar código de estudiantes a servicios analíticos por defecto;
- usar publicidad comportamental en perfiles infantiles;
- hacer depender el progreso de un proveedor de pagos.

## Contratos futuros

`AccountService`, `ProfileService`, `CurriculumService`, `ProgressService`, `AccessService` y `ConsentService` serán límites lógicos, aunque inicialmente puedan vivir en un mismo proceso.

## No implementado en Fase 11

Autenticación remota, base de datos cloud, pagos, suscripciones, sincronización online, recuperación de contraseña, correo transaccional y panel comercial.
