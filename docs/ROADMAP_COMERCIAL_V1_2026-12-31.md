
# TortuScript — Roadmap Comercial V1
## Replanificación: 30/09/2026 → 31/12/2026

Este roadmap complementa ROADMAP_V1_2026-12-31.md. Las Fases 0–14 se consideran cerradas según la auditoría actual. Desde el 01/10 comienza la transición de producto local a producto web comercial.

## Dependencias obligatorias

1. Mobile/UX comienza primero y no depende de cloud.
2. Cuenta familiar requiere modelo de datos y privacidad.
3. Autenticación requiere backend cloud.
4. Pagos requieren Account, Subscription y AccessService.
5. Entitlements requieren pagos/webhooks y perfiles.
6. Sandbox remoto puede diseñarse antes, pero su integración requiere API/worker.
7. Tortu-LLM requiere privacidad, cuenta/perfil y política de datos.
8. Fase 15 requiere todos los bloques críticos integrados.
9. Fase 16 es release de software; el lanzamiento publicitario queda sujeto a la puerta de producción.

## Calendario

### 01–05/10 — Bloque A: Auditoría UX + arquitectura comercial
- Auditoría pantalla por pantalla.
- Inventario de endpoints.
- Contratos de servicios.
- ADR-029 a ADR-035.
- Matriz de requisitos de lanzamiento.

### 06–12/10 — Bloque B: Mobile + sistema visual
- Responsive real.
- Editor móvil.
- Touch.
- Accesibilidad.
- Navegación.
- Estados visuales.
- No ampliar todavía la biblioteca de assets.

### 13–19/10 — Bloque C: Cuenta familiar + privacidad aplicada
- Account.
- ChildProfile.
- ConsentRecord.
- Autorización.
- Políticas de eliminación/exportación.
- Migración del perfil local.

### 20/10–02/11 — Bloque D: Backend + autenticación
- Base de datos.
- API.
- Migraciones.
- Sesiones.
- Email verification.
- Recuperación.
- Rate limiting.
- CSRF.
- Autorización.

### 03–09/11 — Bloque E: Pagos + AccessService
- PaymentService.
- Subscription.
- Entitlement.
- Checkout.
- Webhooks.
- Idempotencia.

### 10–23/11 — Bloque F: Sandbox + seguridad de producción
- Worker.
- Sandbox.
- Límites.
- Sin red.
- Secretos.
- Pruebas de abuso.
- Logging.
- Backups.

### 24/11–07/12 — Bloque G: Integración cloud completa
- Cuenta → perfiles.
- Perfil → catálogo.
- Progreso sincronizado.
- Entitlement → contenido.
- Migración.
- Cancelación/recuperación.

### 08–14/12 — Bloque H: Tortu-LLM
- TutorService.
- Pistas.
- Diagnóstico.
- Límites.
- Privacidad.
- Control de costos.

### 15–19/12 — Bloque I: Assets + UX final
- Assets funcionales.
- Estados de Tortu.
- Iconografía.
- Landing.
- Accesibilidad.
- Responsive final.

### 20–22/12 — Bloque J: Beta privada y preproducción
- Beta con cuentas de prueba.
- Compras de prueba.
- Cancelaciones.
- Múltiples perfiles.
- Sandbox.
- Restauración de backup.
- Simulación de incidentes.
- Revisión legal de documentación.

## Fase 15 — 23–28/12 — Release Candidate

No se agregan features.

Checklist:
- tests unitarios/integración;
- contenido;
- evaluación;
- runtime;
- sandbox;
- autenticación;
- autorización;
- pagos;
- webhooks;
- entitlements;
- migraciones;
- backups/restauración;
- responsive;
- accesibilidad;
- privacidad;
- logs;
- dependencias;
- secretos;
- documentación.

Gate:
- 0 vulnerabilidades críticas abiertas;
- 0 vulnerabilidades altas sin tratamiento aceptado;
- 0 fallos de autorización conocidos;
- compra/cancelación/reembolso verificables;
- aislamiento de perfiles verificado;
- sandbox verificado;
- restauración de backup probada;
- recorrido adulto → perfil → curso → premium completo.

## Fase 16 — 29–31/12 — V1.0.0

- Freeze.
- CHANGELOG.
- README.
- ADRs.
- Arquitectura.
- Seguridad.
- Privacidad.
- Versión de catálogo.
- Migraciones versionadas.
- Tag v1.0.0.

La campaña de marketing y el lanzamiento público quedan fuera del acto técnico de crear el tag. El dominio puede comprarse antes por razones operativas, pero no representa autorización de lanzamiento.

## Definición de terminado

TortuScript queda listo para beta pública controlada cuando:
- una cuenta adulta puede registrarse y verificarse;
- puede crear hasta 5 perfiles;
- los perfiles están aislados;
- el progreso se sincroniza;
- el contenido gratuito funciona;
- el premium se desbloquea por entitlement server-side;
- una sola suscripción cubre los perfiles de la cuenta;
- el código remoto se ejecuta únicamente dentro del sandbox;
- Tortu-LLM es opcional;
- la experiencia móvil es usable;
- las políticas están publicadas;
- backups y restauración funcionan;
- las pruebas de seguridad pasan.

## Fuera de alcance

- aplicación móvil nativa;
- comunidad;
- chat social;
- ranking mundial;
- publicidad comportamental;
- marketplace;
- expansión masiva del catálogo avanzado;
- analítica comercial sofisticada.
