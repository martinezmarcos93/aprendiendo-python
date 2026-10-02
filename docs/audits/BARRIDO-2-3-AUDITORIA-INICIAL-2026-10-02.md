# Barrido 2 + 3 — auditoría inicial de runtime educativo, cuentas y privacidad

**Fecha:** 2026-10-02  
**Rama:** `sweep/consolidacion-ux-v1`  
**Base de trabajo:** HEAD de la rama tras cerrar los barridos 0 + 1.  
**Estado:** auditoría en curso; no autoriza merge a `main`.

## Objetivo

Auditar en paralelo el recorrido educativo autenticado (B2) y los límites de identidad, perfiles, progreso y acceso comercial (B3). La auditoría distingue defectos actuales, riesgos de diseño para la siguiente etapa y funciones que la documentación declara explícitamente fuera del alcance local-first.

## Hallazgos confirmados

### B3-01 — Identificador de ChildProfile determinista y derivado del nombre visible
**Severidad:** alta para el ciclo de vida futuro; media en el modo actual.

En la versión auditada, `crear_child_profile` derivaba el ID mediante `SHA-256(account_id + display_name.lower())`. El identificador interno dependía del nombre visible, por lo que una futura eliminación y recreación con el mismo correo y alias podía volver a asociar progreso huérfano. La API de borrado aún no está implementada.

**Corrección aplicada en la rama:** los nuevos perfiles reciben IDs opacos aleatorios (`child_<24 hex>`), independientes del alias. Se agregaron pruebas para validar formato y unicidad. La corrección queda pendiente del CI de la revisión actual; todavía no se afirma que esté verificada por CI. Antes de exponer el borrado sigue siendo necesaria una política de eliminación/retención de los archivos de progreso.

### B3-02 — La unicidad de nombres no coincide con la generación de IDs
**Severidad:** media; reproducible por inspección del contrato SQLite.

La tabla original usaba `UNIQUE(account_id, display_name)`, sensible a mayúsculas, mientras el ID se calculaba con el nombre en minúsculas. Esto permitía una colisión de ID para `Ana` y `ANA`.

**Corrección aplicada en la rama:** el esquema sube a versión 3, agrega `display_name_key` con normalización `casefold()` y una restricción única por cuenta. La migración revisa duplicados históricos antes de imponer el índice y falla con un mensaje accionable en vez de elegir silenciosamente qué perfil conservar. Se agregó una regresión para el alias duplicado con mayúsculas. Pendiente de CI y revisión del comportamiento de migración con una base local real.

### B2-01 — Cobertura insuficiente del ciclo de vida completo en un único contrato de integración
**Severidad:** media; brecha de verificación.

Hay pruebas unitarias separadas para cuenta, autenticación, selección de perfil, persistencia por ChildProfile, acceso y runtime. La suite también incluye una prueba de rutas de cuenta. Aun así, los contratos distribuidos entre servicios deben verificarse juntos: sesión válida → selección de perfil → carga de progreso → escritura educativa → cambio de perfil → confirmación de aislamiento → reanudación de sesión. Las pruebas existentes no deben considerarse sustituto de esa prueba de recorrido cruzado hasta confirmar qué cubre la suite de integración actual.

**Acción:** inspeccionar la cobertura de rutas y añadir una regresión de recorrido integral solo para los pasos que hoy no estén cubiertos, evitando duplicar pruebas ya existentes.

## Riesgos de arquitectura y límites de alcance

1. **Privacidad/consentimiento:** `docs/FASE12_PRIVACIDAD_MENORES_V1.md` define minimización, consentimiento, retención y derechos, pero declara que es una base de diseño, no una habilitación legal ni una implementación completa. Antes de cualquier despliegue comercial hay que traducir cada requisito a flujos, persistencia, pruebas y revisión jurídica argentina.
2. **Exportación y supresión:** los documentos de arquitectura futura enumeran estas operaciones; no se encontraron implementaciones en los módulos de identidad revisados. Se mantienen como trabajo futuro explícito, no como regresión del modo local actual. No habilitar borrado de perfiles sin resolver progreso huérfano y retención.
3. **Pagos y suscripciones:** el esquema reserva tablas para suscripciones y derechos, pero el producto sigue local-first y la documentación excluye pagos, SaaS y sincronización. No conectar un proveedor ni presentar el estado de entitlement como prueba de pago hasta definir la autoridad que lo modifica y verificar webhooks/autenticidad en la fase comercial.
4. **Concurrencia:** el runtime web serializa las operaciones en el proceso actual. Esto no constituye coordinación entre múltiples procesos o instancias; la sincronización remota requerirá un contrato transaccional y resolución de conflictos explícitos.
5. **Borrado y restauración:** el adaptador de progreso crea una copia `.bak` antes de reemplazar un archivo. Debe documentarse su ciclo de vida y considerar su eliminación/exportación junto con el archivo principal al implementar derechos de datos.

## Secuencia propuesta

1. **En curso:** validar por CI las correcciones B3-01/B3-02 y sus pruebas de regresión.
2. Revisar la cobertura de integración B2 y agregar únicamente los pasos del recorrido cuenta → perfil → progreso → cambio de perfil que no estén cubiertos.
3. Ejecutar el CI completo en Python 3.9 y 3.12 y revisar la migración de esquema v2 → v3.
4. Mantener consentimiento, exportación/supresión, retención y operación comercial como bloqueadores de un futuro lanzamiento remoto; no simular que están implementados.
5. Actualizar el checklist de pruebas manuales sin pedir al usuario un pull antes de su ventana disponible.

## Seguridad y control de cambios

- No se modifica `main`.
- No se habilitan pagos, despliegue remoto ni sincronización.
- No se relajan autenticación, CSRF, rate limiting ni aislamiento de perfiles.
- Todo cambio de persistencia debe incluir prueba de migración/esquema y regresión.
