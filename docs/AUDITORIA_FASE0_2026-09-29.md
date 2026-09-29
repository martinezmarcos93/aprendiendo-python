# Fase 0 — Auditoría de consolidación — 29/09/2026

## Alcance

Auditoría inicial de `refactor/auditoria-2026-09-29` contra `main`, el handoff del 26/09, la auditoría del 24/09, las ADR 001–015 y la documentación experimental existente.

No se ejecutaron tests localmente desde este entorno: el runtime disponible no tiene acceso de red para clonar el repositorio. Tampoco hay ejecuciones de GitHub Actions asociadas a esta rama. Por lo tanto, los resultados de ejecución histórica se consideran antecedentes, no una verificación actual.

## Estado de la rama

- Rama de trabajo: `refactor/auditoria-2026-09-29`.
- Base: `main` en `a572e85b28b76052f3f261d6c839a5ecdc56b7ab`.
- La rama estaba 12 commits adelante y 0 atrás antes de esta auditoría; ahora contiene además las correcciones documentales de esta Fase 0.
- `main` no fue modificada.
- `backup/main-2026-09-26` no fue modificada.

## Hallazgos

### Cerrado / coherente

- ADR-001 a ADR-015 figuran como Aceptadas en el índice actual.
- ADR-003 mantiene la condición de no implementar cuentas/cloud hasta validar demanda y requisitos.
- ADR-006/007 separan correctamente runtime educativo y TortuGame.
- ADR-010 mantiene V1 sin comunidad.
- ADR-011 mantiene proyectos privados.
- ADR-012/013 definen la futura capa adulta/cloud sin hacerla dependencia del Desktop.
- ADR-014 prohíbe ejecutar código arbitrario del alumno en servidores remotos.
- La documentación actual ya refleja la separación entre proceso Flask y proceso hijo controlado, salvo la frase corregida en README durante esta Fase 0.
- El README ya apunta al nuevo roadmap V1; el roadmap Mimo queda identificado como histórico.
- Se corrigió el enlace defectuoso de ADR-022.

### Pendiente P0 — debe verificarse antes de declarar estable el núcleo

1. Ejecutar la batería real de tests Python.
2. Ejecutar los tests JavaScript de TortuGame cuando Node esté disponible.
3. Ejecutar el validador de contenido.
4. Ejecutar, si el entorno de desarrollo lo permite, jugador de cursos, contraste, responsive y simulación.
5. Confirmar la conformidad Python/JavaScript de TortuGame indicada por ADR-006.
6. Revisar de forma reproducible el caso conocido del traductor `mostrar [1, 2][0]`.

### Pendiente P1 — importante para V1, pero no bloquea la definición curricular

1. Probar instaladores en los sistemas realmente soportados. El workflow actual permite Ubuntu, Windows y macOS, pero es manual.
2. Verificar que la documentación de ADR-015, workflow e instaladores coincide con el soporte que se quiere declarar.
3. Decidir si el guardado persistente de partidas de TortuGame sigue fuera de V1.
4. Verificar la protección remota de `backup/*`; el handoff histórico la deja como tarea de administración de GitHub, no de código.

### P2 — mejoras / deuda documental

1. Revisar y marcar explícitamente como históricos los documentos experimentales que describen el producto anterior.
2. Actualizar el handoff anterior con referencias al nuevo roadmap cuando corresponda.
3. Mantener un único documento de estado operativo por etapa para evitar que los handoffs históricos parezcan tareas actuales.
4. Incorporar una verificación CI real si se decide que debe ser criterio obligatorio de release.

## Discrepancias históricas importantes

El handoff del 26/09 registra 472 tests Python + 15 tests JS al cierre de esa sesión, mientras README contiene todavía una referencia histórica de 438 tests. Durante esta auditoría se eliminó el número fijo del comando del README para no seguir propagando un dato no verificado.

El árbol actual contiene 29 módulos Python bajo `tests/` y 3 archivos JavaScript de prueba/ejecución. Esto no equivale al número de casos `test_*` y no debe presentarse como tal.

## Alcance de la nueva V1

Los siguientes elementos pasan a ser trabajo futuro o quedan fuera de V1 salvo que una decisión posterior cambie el alcance:

- pagos reales;
- SaaS completo;
- sincronización cloud definitiva;
- aplicación móvil;
- comunidad;
- tutor IA completo;
- todos los cursos avanzados;
- ranking mundial;
- analítica comercial sofisticada;
- internacionalización completa.

## Conclusión provisional

No aparece una contradicción arquitectónica crítica entre ADR-001…015 y la visión V1 documentada en ADR-016…022.

La Fase 0 debe continuar con la verificación ejecutable del núcleo. No conviene iniciar la implementación curricular antes de registrar esos resultados y decidir qué pendientes heredados entran realmente en V1.
