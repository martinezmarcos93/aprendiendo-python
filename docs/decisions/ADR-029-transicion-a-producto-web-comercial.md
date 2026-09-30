
# ADR-029 — Transición de TortuScript local a producto web comercial

- Estado: Aceptada
- Fecha: 2026-09-30
- Decisor: Marcos
- Relacionadas: ADR-012, ADR-013, ADR-014, ADR-022, ADR-025, ADR-026, ADR-027, ADR-028

## Contexto

El núcleo educativo de TortuScript ya dispone de cursos, motor, progreso, gamificación, evaluación y modelo de acceso conceptual. La siguiente etapa es convertir el producto local en una plataforma web comercial para familias.

La arquitectura debe evitar convertir el núcleo educativo en un SaaS monolítico. El runtime educativo debe seguir siendo reutilizable y la identidad, sincronización, acceso comercial y servicios remotos deben vivir en una capa de plataforma.

## Decisión

TortuScript tendrá dos capas:

1. Núcleo educativo: cursos, catálogo, evaluación, runtime, proyectos, progreso y gamificación.
2. Plataforma comercial: cuenta adulta, perfiles infantiles, autenticación, consentimiento, sincronización, acceso/entitlements, pagos, observabilidad y servicios IA.

La cuenta adulta será la raíz de identidad y facturación. Los perfiles infantiles serán entidades educativas subordinadas.

El lanzamiento comercial queda bloqueado hasta superar la puerta de seguridad, privacidad, pagos, sandbox y release candidate definida en el roadmap.

## Roadmap

### 01–05/10 — Diseño de transición
- Consolidar ADR-029 a ADR-035.
- Auditar frontend pantalla por pantalla.
- Definir AccountService, ProfileService, CurriculumService, ProgressService, AccessService y ConsentService.
- Inventariar endpoints y separar superficie local de superficie pública.

### 06–12/10 — Mobile + UX base
- Validar 320/375/390/768 px.
- Revisar navegación táctil, editor, Tortuga, juegos y formularios.
- Definir sistema visual comercial mínimo.

### 13–19/10 — Identidad y datos
- Implementar Account + ChildProfile.
- Definir migración del progreso local.
- Implementar autorización por propietario.
- Preparar consentimiento y privacidad.

### 20/10–02/11 — Backend cloud
- Base de datos remota.
- API autenticada.
- Persistencia de progreso.
- Migraciones.
- Backups y recuperación.
- Observabilidad mínima.

### 03–09/11 — Acceso comercial
- Entitlements.
- Suscripción.
- Webhooks.
- Estados de pago.
- Bloqueo/desbloqueo server-side.

### 10–23/11 — Seguridad y sandbox
- Autenticación endurecida.
- CSRF/XSS/CORS/rate limiting.
- Gestión de secretos.
- Sandbox remoto para ejecución.
- Pruebas de abuso.

### 24/11–07/12 — Integración end-to-end
- Cuenta → perfil → curso → progreso → entitlement.
- Pruebas de migración.
- Pruebas de cancelación y recuperación de acceso.

### 08–14/12 — Tortu-LLM
- Integración opcional y aislada.
- Límites de uso.
- Política de datos.
- Tutor pedagógico, no solucionador automático.

### 15–19/12 — Pulido
- Assets finales.
- Landing.
- Accesibilidad.
- Responsive.
- UX final.

### 20–22/12 — Pre-RC
- Beta privada.
- Revisión legal.
- Restauración de backups.
- Simulación de incidentes.
- Verificación operativa.

### 23–28/12 — Fase 15: Release Candidate
Freeze de features y auditoría integral.

### 29–31/12 — Fase 16: V1.0.0
Release técnica. El lanzamiento comercial público queda condicionado a la puerta de producción.

## Criterio de aceptación

No existe dependencia entre el núcleo educativo y un proveedor de pagos. El fallo del proveedor comercial no puede destruir ni alterar el progreso educativo.
