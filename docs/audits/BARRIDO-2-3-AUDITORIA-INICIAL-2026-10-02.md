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

**Corrección aplicada en la rama:** los nuevos perfiles reciben IDs opacos aleatorios (`child_<24 hex>`), independientes del alias. Se agregaron pruebas para validar formato y unicidad. CI del commit de código `b5d9a8be48ce5c5f4a55a3b6a0a7128886ee3cec` pasó en Python 3.9 y 3.12 (589 tests, 2 omitidos por versión; 0 fallos/errores). Ejecución: [37046712403](https://github.com/martinezmarcos93/tortuscript/actions/runs/37046712403). Antes de exponer el borrado sigue siendo necesaria una política de eliminación/retención de los archivos de progreso.

### B3-02 — La unicidad de nombres no coincide con la generación de IDs
**Severidad:** media; reproducible por inspección del contrato SQLite.

La tabla original usaba `UNIQUE(account_id, display_name)`, sensible a mayúsculas, mientras el ID se calculaba con el nombre en minúsculas. Esto permitía una colisión de ID para `Ana` y `ANA`.

**Corrección aplicada en la rama:** el esquema sube a versión 3, agrega `display_name_key` con una clave canónica `NFKC + casefold()` y una restricción única por cuenta. La migración revisa duplicados históricos antes de imponer el índice y falla con un mensaje accionable en vez de elegir silenciosamente qué perfil conservar. Se agregó una regresión para el alias duplicado con mayúsculas. CI del commit de código `b5d9a8be48ce5c5f4a55a3b6a0a7128886ee3cec` completó correctamente en Python 3.9 y 3.12 (589 tests, 2 omitidos por versión; 0 fallos/errores). Ejecución: [37046712403](https://github.com/martinezmarcos93/tortuscript/actions/runs/37046712403). Se agregó una prueba automatizada de migración desde una base v2 sintética con conservación del perfil y verificación del índice. Sigue pendiente validar la migración con una copia de una base local real, porque los fixtures automatizados no sustituyen esa comprobación.

### B3-06 — El inicializador podía modificar un esquema de versión futura antes de rechazarlo
**Severidad:** media; riesgo de alterar una base incompatible.

`ensure_schema` comprobaba la versión guardada después de crear tablas e índices y aplicar migraciones. Si una versión más nueva de TortuScript había creado la base, la versión antigua podía modificarla antes de emitir el error de incompatibilidad. Ahora la versión se comprueba antes de ejecutar cambios de esquema; una regresión verifica que una base v4 sea rechazada sin añadir columnas ni tablas. Verificado en CI.

### B3-05 — Entradas inválidas podían inutilizar la recuperación o reservar una cuenta
**Severidad:** media; fallos de consistencia y recuperación ante errores de entrada.

`reset_password` consumía el token antes de validar la longitud de la nueva contraseña; un error de validación dejaba al usuario sin poder reutilizar el enlace. Además, el registro creaba la cuenta antes de validar la política de contraseña, por lo que un intento inválido podía reservar el correo y bloquear un reintento. Ahora la validación ocurre antes de consumir el token o crear la cuenta. Se agregaron pruebas para ambos recorridos; CI confirmó el comportamiento.

### B3-04 — La verificación de correo consumía el token mediante GET
**Severidad:** media; riesgo de activación accidental por escáneres automáticos de enlaces.

La ruta `GET /cuenta/verificar-email` consumía el token de un solo uso. Algunos clientes de correo y filtros de seguridad visitan enlaces automáticamente, por lo que podían verificar la cuenta sin una acción explícita del usuario. La ruta GET ahora solo presenta la confirmación y el consumo se realiza mediante POST; se agregó una regresión que simula el GET y verifica que la cuenta siga sin verificar hasta el POST. Verificado en CI.

### B3-03 — La migración podía dejar una columna nueva tras detectar duplicados
**Severidad:** media; defecto de consistencia del esquema ante una base histórica conflictiva.

La prueba de regresión para alias históricos equivalentes detectó que `ALTER TABLE` podía persistir antes de que la migración arrojara `CuentaError`. Los perfiles no se perdían, pero quedaba un esquema parcialmente alterado. La migración ahora calcula y valida todas las claves históricas antes de añadir la columna; la prueba comprueba que se conservan las dos filas y que la columna no se agrega cuando la migración debe abortar. La corrección quedó verificada en CI.

### B2-01 — Cobertura insuficiente del ciclo de vida completo en un único contrato de integración
**Severidad:** media; brecha de verificación.

Hay pruebas unitarias separadas para cuenta, autenticación, selección de perfil, persistencia por ChildProfile, acceso y runtime. La suite también incluye una prueba de rutas de cuenta. Aun así, los contratos distribuidos entre servicios deben verificarse juntos: sesión válida → selección de perfil → carga de progreso → escritura educativa → cambio de perfil → confirmación de aislamiento → reanudación de sesión. La prueba de rutas ahora cubre el cambio entre dos perfiles de una misma cuenta, la escritura de snapshots distintos y la recuperación de los valores correctos al volver a cada perfil.

**Acción:** inspeccionar la cobertura de rutas y añadir una regresión de recorrido integral solo para los pasos que hoy no estén cubiertos, evitando duplicar pruebas ya existentes.

### B2-02 — Permutaciones de líneas con salida equivalente en tres ejercicios
**Severidad:** baja; aviso editorial no bloqueante, con riesgo de evaluación demasiado estricta si el contrato no se prueba.

El validador detecta permutaciones que producen la misma salida en «Dos variables», «Tabla del 2» y «Solo los pares». La lógica de lecciones ya admite ordenamientos alternativos cuando la ejecución genera la salida esperada; agregué una regresión que comprueba esos tres casos con el motor real. Los tres avisos del validador siguen siendo intencionales: informan al autor de que la consigna puede admitir más de un orden correcto, no indican un fallo de validación del curso.

### B3-07 — El envío de correo depende de una integración opcional
**Severidad:** bloqueante para un lanzamiento remoto; no bloqueante para pruebas locales.

`_emitir_email` no falla si `ACCOUNT_EMAIL_SENDER` no está configurado: registro y recuperación pueden responder como aceptados sin entregar ningún enlace. La integración de correo no está configurada por defecto en el servidor local y no debe darse por operativa en producción. Antes del despliegue hay que incorporar un proveedor de correo, comprobar fallos de entrega, definir reintentos y verificar que los enlaces lleven a la nueva confirmación explícita por POST. No se simula ni se inventa un proveedor dentro de esta auditoría.

## Riesgos de arquitectura y límites de alcance

1. **Privacidad/consentimiento:** `docs/FASE12_PRIVACIDAD_MENORES_V1.md` define minimización, consentimiento, retención y derechos, pero declara que es una base de diseño, no una habilitación legal ni una implementación completa. Antes de cualquier despliegue comercial hay que traducir cada requisito a flujos, persistencia, pruebas y revisión jurídica argentina.
2. **Exportación y supresión:** los documentos de arquitectura futura enumeran estas operaciones; no se encontraron implementaciones en los módulos de identidad revisados. Se mantienen como trabajo futuro explícito, no como regresión del modo local actual. No habilitar borrado de perfiles sin resolver progreso huérfano y retención.
3. **Pagos y suscripciones:** el esquema reserva tablas para suscripciones y derechos, pero el producto sigue local-first y la documentación excluye pagos, SaaS y sincronización. No conectar un proveedor ni presentar el estado de entitlement como prueba de pago hasta definir la autoridad que lo modifica y verificar webhooks/autenticidad en la fase comercial.
4. **Concurrencia:** el runtime web serializa las operaciones en el proceso actual. Esto no constituye coordinación entre múltiples procesos o instancias; la sincronización remota requerirá un contrato transaccional y resolución de conflictos explícitos.
5. **Correo transaccional:** la configuración `ACCOUNT_EMAIL_SENDER` es opcional y no existe proveedor por defecto; ver B3-07. Registro y recuperación no están listos para uso remoto hasta configurar y probar entrega real.
6. **Borrado y restauración:** el adaptador de progreso crea una copia `.bak` antes de reemplazar un archivo. Debe documentarse su ciclo de vida y considerar su eliminación/exportación junto con el archivo principal al implementar derechos de datos.

## Secuencia propuesta

1. **CI previo verificado:** el commit `b5d9a8be48ce5c5f4a55a3b6a0a7128886ee3cec` pasó en Python 3.9 y 3.12 (589 tests, 2 omitidos por versión). La cobertura NFKC, migración v2 → v3, cambio de perfil y ordenamientos equivalentes pasó en Python 3.9 y 3.12 en el commit `3fe66f208424bfe9bbaf35f2317455ad482986c0` (593 tests, 2 omitidos por versión). CI del HEAD `22a3d697fbe28b29cc5190069b2118db058fb8e1` pasó en Python 3.9 y 3.12: 597 tests, 2 omitidos por versión, sin fallos ni errores. Incluye las regresiones de migración parcial, rechazo de esquema futuro, contraseña inválida y verificación explícita de correo. [Ejecución](https://github.com/martinezmarcos93/tortuscript/actions/runs/37051187720).
2. **CI actual verificado:** Python 3.9 y 3.12 pasan en el HEAD `22a3d697fbe28b29cc5190069b2118db058fb8e1` (597 tests, 2 omitidos por versión).
3. Validar la migración v2 → v3 con una copia local real, sin tocar la base original.
4. Mantener consentimiento, exportación/supresión, retención y operación comercial como bloqueadores de un futuro lanzamiento remoto; no simular que están implementados.
5. Actualizar el checklist de pruebas manuales sin pedir al usuario un pull antes de su ventana disponible.

## Seguridad y control de cambios

- No se modifica `main`.
- No se habilitan pagos, despliegue remoto ni sincronización.
- No se relajan autenticación, CSRF, rate limiting ni aislamiento de perfiles.
- Todo cambio de persistencia debe incluir prueba de migración/esquema y regresión.
