# Fase 10 — Sistema de producto V1

## Objetivo

Separar cuatro conceptos que antes estaban mezclados o solo documentados:

1. catálogo curricular;
2. competencias;
3. progreso curricular;
4. acceso al contenido.

La capa de producto no implementa pagos, suscripciones, cuentas cloud ni SaaS.

## Catálogo

El catálogo conceptual sigue en `docs/catalogo_curricular_v1.json`. La nueva capa usa `contenido/mapa_curricular.json` como adaptador: allí se declara qué evidencia operativa demuestra cada unidad curricular.

Esto evita que el modelo curricular dependa directamente del Flask, de una plantilla HTML o de una implementación concreta del motor.

## Competencias y progreso

Las competencias se derivan del avance real del perfil:

- `pendiente`: no existe evidencia de estudio;
- `en_progreso`: existe avance en alguna evidencia;
- `completada`: toda la evidencia declarada de la unidad está terminada;
- `dominada`: una competencia tiene al menos una unidad completada;
- `repasar`: la evidencia tiene una tarjeta de repaso vencida.

No se inventa un porcentaje de dominio que el motor no pueda justificar. El modelo permite ampliar posteriormente la evidencia con intentos, evaluaciones y otros instrumentos.

## Acceso

Se mantienen los estados conceptuales definidos anteriormente:

- `gratuito`
- `premium`
- `prueba`
- `bloqueado_por_prerrequisito`
- `no_publicado`

El estado comercial por defecto continúa siendo `por_definir`. Esto es deliberado: Fase 10 no decide qué curso debe ser premium.

`bloqueado_por_prerrequisito` sí es una decisión pedagógica y puede calcularse sin conocer ningún sistema de pagos.

El segmento de producto se representa separadamente como:

- Gratis
- Premium
- En desarrollo
- Avanzados

Los segmentos Premium y En desarrollo no reciben itinerarios comerciales concretos en esta fase. Avanzados apunta al itinerario curricular futuro y permanece no publicado.

## Contrato operativo

`tortuscript.catalogo_producto.resumen(progreso)` devuelve:

- segmentos de producto;
- estado comercial;
- unidades con estado de progreso;
- competencias;
- estado de acceso.

`progreso_para_mostrar(progreso)` devuelve una versión reducida para UI.

## No incluido

- pagos;
- Stripe/Mercado Pago;
- cuentas adultas;
- perfiles cloud;
- sincronización;
- suscripciones;
- paywall;
- analítica comercial.

## Criterio de cierre

La Fase 10 queda técnicamente cerrada cuando el modelo curricular tiene un adaptador verificable, las competencias se pueden derivar del progreso real, el repaso puede reflejarse en competencias, los prerrequisitos bloquean independientemente de lo comercial, y los segmentos de producto existen sin fijar una política premium.
