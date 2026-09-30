# ADR-044: Migración explícita de progreso local a ChildProfile

Estado: **Aceptada**

## Decisión

El progreso local existente no se migra automáticamente al sistema comercial.
La migración requiere una acción explícita de una sesión autenticada con un
ChildProfile activo y nombra el perfil local que se desea importar.

Si el ChildProfile ya posee progreso, la operación se rechaza salvo que el
cliente indique expresamente que desea reemplazarlo.

El destino siempre es ChildProfile.id. El nombre del perfil local solo identifica
el archivo de origen y nunca se convierte en identidad comercial.

## Consecuencias

- Se conserva intacto el runtime local existente.
- No hay migraciones silenciosas ni asociación automática entre nombres locales y cuentas.
- La futura sincronización remota puede reemplazar este puente sin cambiar la identidad.