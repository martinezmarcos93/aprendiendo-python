# ADR-041 — Contrato de progreso asociado a ChildProfile

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Decide:** El progreso educativo futuro se identifica y persiste por \`ChildProfile.id\`.
- **Relacionadas:** ADR-030, ADR-038, ADR-040

## Contexto

La cuenta adulta es la raíz de identidad y facturación, pero varios alumnos pueden
pertenecer a la misma cuenta. El progreso no debe quedar asociado al correo de
la cuenta ni al nombre visible del alumno.

El producto local ya tiene un formato de progreso JSON estable. Migrarlo
directamente al nuevo almacenamiento comercial mezclaría dos responsabilidades
y haría más difícil mantener compatibilidad.

## Decisión

Se define \`tortuscript/progreso_contrato.py\` como frontera de persistencia.

El contrato exige:

- \`profile_id\` como identidad del propietario;
- versión explícita del contrato;
- timestamp de actualización;
- objeto de datos de progreso;
- validación antes de importar o persistir;
- aislamiento por perfil.

La primera implementación es deliberadamente un adaptador en memoria para pruebas.
No modifica \`progreso.py\`, no migra \`progreso_<perfil>.json\` y no conecta todavía
la sesión HTTP con el progreso.

## Consecuencias

Esto permite incorporar después un backend SQLite/remoto sin hacer que la capa
educativa conozca cuentas, contraseñas, pagos o sesiones.

La selección persistente de perfil y la asociación efectiva del progreso quedan
como pasos posteriores, después de completar la migración de sesiones y sus
controles de autorización.
