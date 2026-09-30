# ADR-022 — Preparar la arquitectura comercial sin implementar el SaaS en V1

- Estado: Propuesta
- Fecha: 2026-09-29

## Contexto
El objetivo de largo plazo incluye publicar TortuScript en un dominio, operar infraestructura propia, ofrecer contenido gratuito y premium y utilizar suscripciones. El plazo de V1 no permite ni necesita implementar todo el SaaS.

## Decisión propuesta
La V1 documentará interfaces y límites entre motor educativo, catálogo, identidad, progreso, acceso, sincronización y futura facturación, pero mantendrá el runtime local como implementación principal.

## Consecuencia
El producto puede evolucionar hacia cloud sin convertir el prototipo local en un sistema distribuido prematuramente.

## Regla
Ninguna infraestructura cloud se incorporará únicamente por anticipación. Cada componente futuro deberá justificar una necesidad concreta de producto u operación.