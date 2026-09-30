# Acceso administrativo local

TortuScript dispone de un bootstrap administrativo únicamente para desarrollo y
validación local.

## Crear o actualizar el Admin

Desde la raíz del repositorio:

\`\`\`bash
python herramientas/crear_admin.py
\`\`\`

El script solicita el correo y la contraseña mediante entrada interactiva. La
contraseña no se acepta como argumento, no se imprime y no se escribe en ningún
archivo del repositorio. En SQLite se almacena solamente mediante el hash de
contraseña que utiliza \`AuthRepository\`.

Por defecto, la cuenta es:

\`\`\`
admin@tortuscript.local
\`\`\`

La cuenta queda verificada, recibe el rol \`admin\` y se crea un perfil infantil
\`Admin\` si todavía no tiene perfiles.

## Alcance del rol Admin

El rol \`admin\` tiene bypass explícito de la autorización comercial: puede
consultar productos aunque no exista un entitlement de pago. Esto permite probar
TortuScript Premium, Croco-Script y productos futuros sin fabricar pagos.

No se desactivan todavía los prerrequisitos curriculares ni se mezcla esta cuenta
con el progreso educativo local. La integración de cuenta/perfil/progreso sigue
siendo el siguiente bloque de trabajo.

## Seguridad

No introducir contraseñas administrativas en código, fixtures, documentación,
commits, comandos reproducibles ni archivos de configuración versionados.
El bootstrap debe ejecutarse sobre la base SQLite local que usa la aplicación.
