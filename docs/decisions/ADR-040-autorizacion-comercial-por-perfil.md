# ADR-040 — Servicio de autorización comercial por perfil

- Estado: Aceptada
- Fecha: 2026-09-30
- Contexto: ADR-030, ADR-032, ADR-037

## Decisión

La autorización comercial se consulta siempre en la frontera:

Account → Entitlement → ChildProfile.

Se incorpora `tortuscript.acceso.AccesoProducto` como servicio de dominio. Recibe un `CuentaRepository` y permite consultar o exigir acceso a un producto para un ChildProfile.

El servicio:

- no autentica;
- no crea sesiones;
- no procesa pagos;
- no modifica progreso;
- no decide acceso basándose en datos enviados por el navegador;
- consulta el entitlement persistido asociado al Account propietario del perfil.

Un entitlement activo de la cuenta habilita el producto correspondiente para todos sus ChildProfiles activos, de acuerdo con ADR-030 y ADR-032.

## Consecuencia

Las futuras rutas educativas premium no deberán implementar consultas SQL de entitlements por su cuenta. Deberán depender de esta frontera de dominio o de un servicio superior que la utilice.

La integración HTTP queda pendiente hasta cerrar correctamente la verificación de correo y la selección persistente del ChildProfile.
