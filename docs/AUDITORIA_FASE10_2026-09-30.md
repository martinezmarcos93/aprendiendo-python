# Auditoría Fase 10 — Sistema de producto V1

Fecha: 2026-09-30

## Estado

Fase 10 cerrada en la rama `refactor/auditoria-2026-09-29`.

## Implementado

- Adaptador `contenido/mapa_curricular.json` entre el catálogo curricular y la evidencia operativa.
- `tortuscript/catalogo_producto.py` con:
  - catálogo de unidades;
  - estados de progreso por unidad;
  - competencias derivadas;
  - señal de repaso;
  - prerrequisitos por unidad, competencia, itinerario completo y alternativas de itinerarios;
  - resolución de acceso curricular independiente de pagos;
  - segmentos de producto Gratis, Premium, En desarrollo y Avanzados.
- Endpoint local `GET /api/catalogo-producto` para exponer el contrato reducido a la UI.
- El Nivel 0 está representado como segmento gratuito.
- Python, Web, SQL y proyectos integradores no reciben una asignación Premium automática: su estado comercial queda `por_definir`.
- El itinerario avanzado permanece no publicado.
- Los prerrequisitos se expresan en el catálogo sin depender de Flask ni de un proveedor de pagos.
- Se incorporaron JSON, Git y GitHub al adaptador curricular.
- Se corrigieron regresiones heredadas detectadas por la verificación de CI:
  - plantilla `mapa.html`;
  - consultas predictivas SQL;
  - manejo de preguntas pendientes de `input()`;
  - ayudas adaptativas de proyectos;
  - archivos anidados de proyectos;
  - fixtures curriculares y de UI que habían quedado obsoletos;
  - vocabulario SQL en el resumen de lecciones.

## Contrato de competencias

Una unidad puede estar:

- pendiente;
- en progreso;
- completada.

Una competencia se considera dominada cuando existe al menos una unidad completada que la evidencia. El sistema no inventa porcentajes de dominio.

El repaso se refleja cuando una evidencia de lección tiene una tarjeta cuyo próximo repaso ya venció.

## Acceso

Los estados conceptuales definidos para el producto son:

- gratuito;
- premium;
- prueba;
- bloqueado por prerrequisito;
- no publicado.

La capa curricular calcula bloqueos por prerrequisito y publicación. La decisión comercial concreta permanece separada y `por_definir` para los itinerarios que todavía no tienen una política comercial aprobada.

No se implementaron pagos, suscripciones, paywall, cuentas cloud ni SaaS.

## Verificación

GitHub Actions ejecutó el workflow `Verificación Fase 0` sobre el commit de cierre:

- 526 tests ejecutados;
- 2 tests omitidos;
- conclusión: `success`;
- validador de contenido ejecutado dentro del mismo workflow.

La ejecución final corresponde al commit `e10ba4df23638b424d6adeddf2f35a275700d3fb` de la rama de trabajo.

## Alcance

No se inició Fase 11. La arquitectura comercial futura continúa documentada, no implementada.

## Cierre

La Fase 10 cumple su objetivo de separar catálogo, competencias, progreso y acceso sin convertir el motor pedagógico en un sistema de pagos.
