# ADR-019 — Estados de acceso independientes del motor pedagógico

- Estado: Propuesta
- Fecha: 2026-09-29

## Contexto
La visión comercial contempla contenido gratuito y contenido de pago. El sistema actual es local y no debe acoplarse prematuramente a una pasarela o proveedor de suscripciones.

## Decisión propuesta
El catálogo curricular podrá declarar un estado de acceso: gratuito, premium, prueba, bloqueado por prerrequisito o no publicado.

El motor pedagógico solamente deberá interpretar si una unidad está disponible. La futura capa comercial decidirá por qué el usuario tiene ese acceso.

## Consecuencia
Se podrá cambiar el modelo comercial sin reescribir las lecciones ni el evaluador.

## Fuera de alcance
Pagos, facturación, cuentas cloud y autorización real se documentarán en ADRs posteriores.