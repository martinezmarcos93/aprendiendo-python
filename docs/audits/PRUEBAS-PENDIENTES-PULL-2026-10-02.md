# Pruebas pendientes tras el pull — TortuScript

**Fecha de preparación:** 2026-10-02  
**Rama:** `sweep/consolidacion-ux-v1`  
**Objetivo:** ejecutar estas comprobaciones en el entorno local de Marcos después de hacer pull. No hacer merge a `main` hasta revisar resultados.

## Antes de probar

- [ ] Confirmar rama: `git branch --show-current` → `sweep/consolidacion-ux-v1`.
- [ ] Confirmar último commit: `git log -1 --oneline`.
- [ ] Guardar copia de la carpeta de datos/progreso antes de probar.
- [ ] Usar una cuenta de prueba y perfiles infantiles ficticios; no borrar datos reales.
- [ ] Arrancar siguiendo las instrucciones actuales del README y guardar el log de arranque.

## Pruebas funcionales manuales

| ID | Área | Acción | Resultado esperado | Estado/evidencia |
|---|---|---|---|---|
| M01 | Arranque | Iniciar el servidor desde cero | Arranca sin traceback ni error de configuración | Pendiente |
| M02 | Cuenta | Abrir la app sin sesión | Muestra login; no muestra datos educativos | Pendiente |
| M03 | Registro | Registrar cuenta de prueba | Queda pendiente de verificación, sin permitir acceso educativo prematuro | Pendiente |
| M04 | Login | Iniciar sesión con cuenta verificada | Cookie de sesión emitida y acceso a selección/creación de perfil | Pendiente |
| M05 | Sesión | Recargar y navegar entre páginas | Sesión se mantiene de forma consistente | Pendiente |
| M06 | Perfiles | Crear dos perfiles infantiles | Ambos aparecen y pueden seleccionarse | Pendiente |
| M07 | Aislamiento | Cambiar de perfil A a B | Nombre, onboarding, XP, lecciones y proyectos no se mezclan | Pendiente |
| M08 | Onboarding | Entrar con perfil nuevo | Redirige a bienvenida antes del contenido educativo | Pendiente |
| M09 | Onboarding | Completar bienvenida y volver a entrar | No repite bienvenida para ese perfil | Pendiente |
| M10 | Lecciones | Completar un paso correctamente | Se refleja feedback, XP/estrellas y avance esperados | Pendiente |
| M11 | Persistencia | Recargar la lección y reiniciar el servidor | El progreso completado persiste | Pendiente |
| M12 | Sesión | Cerrar sesión y volver a una URL educativa | Se solicita login; no se filtran datos previos | Pendiente |
| M13 | API | Solicitar endpoint API sin token local | Rechazo 403 antes de resolver identidad educativa | Pendiente |
| M14 | API | Enviar token local válido sin sesión educativa | Rechazo 401 por ausencia de sesión | Pendiente |
| M15 | API | Enviar token, sesión y perfil activo | Endpoint permitido y funcional | Pendiente |
| M16 | Proyectos | Crear/editar/guardar un proyecto de prueba | Cambios persisten al recargar | Pendiente |
| M17 | Integrador | Abrir un proyecto integrador, editar y guardar | Estado y archivos se guardan en el perfil correcto | Pendiente |
| M18 | Migración | Revisar flujo de importación de progreso local | Solo ocurre por acción explícita; no reemplaza progreso comercial sin confirmación | Pendiente |
| M19 | Responsive | Probar login, mapa, lección y proyectos en ventana angosta/móvil | Sin scroll horizontal ni botones inaccesibles | Pendiente |
| M20 | Cierre | Cerrar la app normalmente y volver a abrir | No se pierde progreso; el comportamiento de sesión es coherente | Pendiente |
| M21 | Alias de perfil | Intentar crear `Ana` y luego `ANA` en la misma cuenta | El segundo alias se rechaza como duplicado sin error 500 ni colisión de ID | Pendiente |
| M22 | Migración de esquema | Con copia de seguridad previa, arrancar usando una base creada por la versión anterior | El esquema migra a v3 o informa claramente de duplicados históricos; no desaparecen perfiles ni progreso | Pendiente |
| M23 | Aislamiento persistente | Guardar progreso en perfil A, cambiar a B, guardar otro avance, volver a A y reiniciar el servidor | Cada perfil recupera exactamente su propio progreso | Pendiente |

## Estado de verificación automática

- [ ] Confirmar el CI completo del último commit de `sweep/consolidacion-ux-v1` en Python 3.9 y 3.12.
- [ ] Confirmar que la verificación de correo no consume el token al abrir el enlace (GET) y solo verifica tras confirmar por POST.
- [ ] Confirmar que las regresiones de `tests/test_cuentas.py` pasen: ID opaco, alias equivalentes por mayúsculas/Unicode NFKC y migración de esquema v2 → v3.
- [ ] Revisar los logs de migración del esquema v2 → v3; comprobar que los duplicados históricos abortan antes de alterar el esquema y no eliminan ni modifican perfiles.
- [ ] Confirmar la prueba HTTP de cambio entre dos perfiles de una misma cuenta: cada perfil debe recuperar su propio XP tras alternar varias veces.
- [ ] Confirmar que el validador de contenido no tiene errores bloqueantes. Los tres avisos de ordenamientos equivalentes están explicados y cubiertos por `test_tres_ordenamientos_equivalentes_del_curso_se_aceptan`; revisar si las consignas deberían precisar mejor el objetivo pedagógico.
- [ ] No fusionar a `main` hasta que CI esté verde, se revise el diff completo y Marcos complete las pruebas manuales relevantes.


## Registro de resultados

Anotar por prueba: **OK / FALLA / BLOQUEADA**, commit probado, pasos exactos, resultado observado y captura/log si corresponde. No poner solo “anda/no anda”: especificar URL, código HTTP, perfil usado y si el resultado persistió tras recarga.

## Regla de seguridad

No desactivar autenticación, token local, aislamiento por perfil ni protección CSRF para conseguir que pasen tests antiguos. Si una expectativa de test contradice el contrato vigente, actualizar el fixture o documentar la incompatibilidad después de verificar el comportamiento esperado.
