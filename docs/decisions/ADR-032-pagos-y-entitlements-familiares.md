
# ADR-032 — Pagos y entitlements familiares

- Estado: Aceptada
- Fecha: 2026-09-30
- Decisor: Marcos
- Relacionadas: ADR-019, ADR-025, ADR-029, ADR-030

## Decisión

El proveedor de pagos será externo detrás de PaymentService. TortuScript no almacenará datos de tarjeta.

El estado comercial será independiente del catálogo educativo.

Modelo:

Account
→ Subscription
→ Entitlement
→ ChildProfiles

El navegador nunca podrá decidir que un usuario es premium. El servidor resolverá el entitlement.

Eventos:
- checkout completed;
- payment succeeded;
- payment failed;
- subscription updated;
- subscription canceled;
- refund/reversal cuando corresponda.

Una suscripción activa desbloquea premium para todos los perfiles de la cuenta.

La cancelación no elimina el progreso.

## Roadmap

### 03–09/11 — Modelo
- PaymentService.
- Subscription.
- Entitlement.
- Estados.
- Idempotencia.

### 10–16/11 — Checkout
- Proveedor externo.
- Checkout.
- Retorno seguro.
- No manejar tarjetas.

### 17–23/11 — Webhooks
- Firma/verificación.
- Idempotencia.
- Reconciliación.
- Estados fallidos.

### 24–30/11 — Paywall
- AccessService.
- Premium server-side.
- Herencia a todos los ChildProfiles.

### 01–07/12 — Casos extremos
- Pago duplicado.
- Webhook repetido.
- Cancelación.
- Renovación.
- Pago rechazado.
- Reembolso.
- Caída temporal del proveedor.

### 23–28/12 — Fase 15
- Pruebas completas de compra, cancelación y restauración.

### 29–31/12 — Fase 16
- Congelación del contrato comercial.
