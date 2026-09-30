# Matriz de validación móvil UX V1

Fecha: 2026-09-30
Rama: audit/ux-v1-2026-09-30

Objetivo: convertir los hallazgos estáticos de UX-V1-AUDIT-2026-09-30 en una batería reproducible antes de cerrar el bloque mobile.

## Viewports obligatorios

- 320 × 800
- 375 × 812
- 390 × 844
- 768 × 1024
- escritorio de referencia: 1280 × 800

## Rutas críticas

1. /
2. /bienvenida
3. /aprender
4. /leccion/<id>
5. /ejercicios/1
6. /experimentar
7. /tortuga
8. /juego
9. /proyectos
10. /proyectos-integradores

## Matriz

| Área | 320 | 375 | 390 | 768 | Criterio |
|---|---|---|---|---|---|
| Header | ☐ | ☐ | ☐ | ☐ | No overflow horizontal; menú accesible |
| Navegación | ☐ | ☐ | ☐ | ☐ | Cada destino alcanzable con touch |
| Inicio | ☐ | ☐ | ☐ | ☐ | Acción principal identificable |
| Onboarding | ☐ | ☐ | ☐ | ☐ | Teclado no tapa input/botón |
| Lección | ☐ | ☐ | ☐ | ☐ | Pie fijo no tapa contenido |
| Ejercicio | ☐ | ☐ | ☐ | ☐ | Editor usable con teclado virtual |
| Experimentar | ☐ | ☐ | ☐ | ☐ | Ejecutar/limpiar/guardar alcanzables |
| Tortuga | ☐ | ☐ | ☐ | ☐ | Canvas visible y controles utilizables |
| Juego | ☐ | ☐ | ☐ | ☐ | Escena y registro comprensibles |
| Proyectos | ☐ | ☐ | ☐ | ☐ | Cards y acciones sin colisión |
| Integradores | ☐ | ☐ | ☐ | ☐ | Etapas/archivos editables |
| Modales | ☐ | ☐ | ☐ | ☐ | Foco, cierre, teclado y scroll correctos |
| Accesibilidad | ☐ | ☐ | ☐ | ☐ | Contraste, foco y texto configurables |
| Orientación | ☐ | ☐ | ☐ | ☐ | Vertical usable |
| Teclado virtual | ☐ | ☐ | ☐ | ☐ | Ningún control crítico queda oculto |

## Pruebas táctiles

Cada superficie debe comprobar:

- botón primario accionable con dedo;
- botones secundarios separados;
- enlaces no demasiado próximos;
- scroll vertical sin bloqueo;
- no depender de hover;
- sliders utilizables;
- canvas sin exigir precisión excesiva;
- editor permite colocar cursor y seleccionar texto;
- acciones inferiores permanecen accesibles cuando aparece el teclado.

## Pruebas de teclado

- Tab recorre controles en orden lógico.
- Enter activa el control esperado.
- Escape sale de editor/modales cuando corresponde.
- Ctrl/Cmd+Enter ejecuta cuando el foco está en editor.
- No existen trampas de foco fuera de modales.

## Criterios de cierre P0

Un viewport/ruta no se marca como aprobado si existe:

- overflow horizontal involuntario;
- botón primario fuera de pantalla;
- teclado virtual ocultando la acción principal;
- editor inutilizable;
- canvas cortado de forma que impida la actividad;
- modal que no permite cerrar;
- pérdida de foco sin explicación;
- control que depende exclusivamente de hover;
- texto esencial ilegible;
- progreso/resultado que desaparece al cambiar de paso.

## Siguiente implementación

Después de ejecutar esta matriz, corregir únicamente fallos reproducibles P0/P1. No rediseñar componentes que todavía no presenten un problema comprobado.
