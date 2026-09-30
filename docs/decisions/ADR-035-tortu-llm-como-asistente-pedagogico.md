
# ADR-035 — Tortu-LLM como asistente pedagógico

- Estado: Aceptada
- Fecha: 2026-09-30
- Decisor: Marcos
- Relacionadas: ADR-026, ADR-029, ADR-031, ADR-034

## Decisión

Tortu-LLM será un servicio opcional y desacoplado del núcleo educativo.

Su objetivo será ayudar a pensar, no entregar directamente la solución.

Niveles:
1. pista conceptual;
2. pregunta orientadora;
3. diagnóstico de error;
4. ejemplo parcial;
5. solución explicada solamente cuando la política del ejercicio lo permita.

El servicio recibirá el mínimo contexto necesario. No se enviará por defecto información identificatoria del menor.

Tendrá límites de uso, control de costos, logging mínimo, filtros de datos, política de retención y fallback cuando no esté disponible.

No será requisito para completar el recorrido principal.

## Roadmap

### 08–14/12
- Contrato TutorService.
- Prompts pedagógicos.
- Contexto permitido.
- Límites.

### 15–19/12
- Integración con ejercicios.
- Pistas.
- Diagnóstico.
- Control de revelación.

### 20–22/12
- Pruebas de privacidad.
- Pruebas de alucinación.
- Pruebas de respuestas que resuelven demasiado.
- Límites de costo.

### 23–28/12 — Fase 15
- Beta controlada.
- Sin dependencia para aprobar ejercicios.

### 29–31/12 — Fase 16
- Release como feature opcional si supera las pruebas.
