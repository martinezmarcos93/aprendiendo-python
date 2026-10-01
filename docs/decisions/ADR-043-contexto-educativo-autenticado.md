# ADR-043: Contexto educativo autenticado por ChildProfile

Estado: **Aceptada**

## Contexto

La transición comercial ya dispone de cuenta adulta, sesiones server-side, perfiles
infantiles y un adaptador de progreso cuyo propietario es ChildProfile.id. Faltaba
una frontera explícita que uniera esas piezas sin modificar el runtime educativo local.

## Decisión

Toda operación educativa autenticada que dependa de la cuenta comercial debe resolver
el contexto en este orden:

sesión → Account → active ChildProfile → progreso

La identidad del progreso es exclusivamente ChildProfile.id. El email de la cuenta
y el nombre visible del perfil no se utilizan como claves de persistencia.

El acceso a productos se verifica después de resolver el perfil activo mediante
AccesoProducto. El entitlement pertenece al Account y se hereda por sus perfiles;
el bypass administrativo sigue siendo responsabilidad exclusiva de la capa comercial.

El servicio no modifica tortuscript/progreso.py ni migra automáticamente el progreso
local existente.

## Consecuencias

- El cambio de perfil cambia explícitamente el espacio de progreso utilizado.
- Un perfil no puede escribir el progreso de otro perfil mediante el servicio.
- La autorización comercial queda separada de la autenticación.
- El runtime educativo local puede continuar funcionando sin cuenta comercial.
- Una futura implementación remota puede sustituir el almacenamiento del adaptador sin
  cambiar el contrato del servicio.