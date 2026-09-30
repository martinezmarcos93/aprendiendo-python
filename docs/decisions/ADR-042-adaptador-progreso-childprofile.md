# ADR-042 — Adaptador de progreso por ChildProfile

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Decide:** Los perfiles de cuenta comercial dispondrán de un almacenamiento de progreso cuyo propietario técnico sea `ChildProfile.id`.
- **Relacionadas:** ADR-038, ADR-040, ADR-041

## Decisión

Se incorpora `tortuscript/progreso_childprofile.py`.

El adaptador:

- valida que el identificador tenga el formato interno de ChildProfile;
- almacena snapshots bajo ese identificador;
- mantiene aislamiento entre perfiles;
- utiliza escritura atómica y respaldo `.bak`;
- no utiliza el nombre visible ni el correo como clave;
- no modifica los archivos de progreso locales existentes;
- no se conecta todavía al flujo HTTP.

La migración de progreso existente queda explícitamente separada. Cuando se active la cuenta comercial, deberá existir una estrategia explícita de migración o importación para evitar atribuir accidentalmente el progreso de un perfil local a otro ChildProfile.

## Consecuencia

La identidad, la autorización comercial y el progreso tienen ahora una frontera clara. El siguiente paso será definir la transición entre este adaptador y el runtime educativo, con controles de autorización antes de leer o escribir.