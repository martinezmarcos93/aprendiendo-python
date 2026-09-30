
# ADR-033 — Sandbox remoto para ejecución de código

- Estado: Aceptada
- Fecha: 2026-09-30
- Decisor: Marcos
- Relacionadas: ADR-007, ADR-014, ADR-029, ADR-031

## Decisión

El runtime educativo no se expondrá directamente al tráfico público.

Flujo:

Web/API
→ Job/Worker
→ Sandbox efímero
→ Resultado mínimo
→ Usuario

El sandbox deberá:
- no tener acceso a la red;
- no contener secretos;
- usar filesystem efímero;
- tener límites de CPU;
- tener límites de memoria;
- tener timeout;
- tener límite de salida;
- ejecutarse con privilegios mínimos;
- ser destruido al terminar;
- impedir acceso al host;
- impedir acceso a otros trabajos.

No se aceptarán uploads arbitrarios como mecanismo inicial de ejecución.

La evaluación debe preferir análisis estático y ejecución controlada.

## Roadmap

### 10–23/11
- Worker.
- Contrato de job.
- Aislamiento.
- Límites CPU/RAM/tiempo.
- Sin red.
- Filesystem efímero.

### 24–30/11
- Pruebas de loops.
- Memoria.
- Procesos hijos.
- Filesystem.
- Red.
- Salida excesiva.
- Escape del aislamiento.

### 01–07/12
- Integración con ejercicios.
- Colas.
- Reintentos.
- Observabilidad.
- Eliminación de artefactos.

### 20–22/12
- Pruebas de carga controlada.
- Revisión de configuración de producción.

### 23–28/12 — Fase 15
- Sandbox incluido en security regression.

### 29–31/12 — Fase 16
- Producción solo si el aislamiento está validado.
