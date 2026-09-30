# ADR-037 — Integración entre TortuScript y Croco-Script

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Decide:** TortuScript y Croco-Script serán aplicaciones separadas con identidad y acceso comercial compartidos.
- **Relacionadas:** ADR-029, ADR-030, ADR-031, ADR-032, ADR-036

## Contexto

Croco-Script será un producto separado, pero no debe sentirse como una cuenta o compra diferente para la familia.

La cuenta adulta de TortuScript ya constituye la raíz de identidad y facturación. Por tanto, Croco-Script debe consumir la misma relación de identidad, perfiles y entitlement en lugar de crear una segunda cuenta.

## Decisión

La arquitectura será:

`Cuenta adulta → Perfiles → Suscripción → Entitlements → TortuScript / Croco-Script`

TortuScript será responsable del ecosistema familiar y de la relación comercial.

Croco-Script será responsable de su experiencia educativa avanzada.

La navegación entre aplicaciones utilizará una sesión/autorización segura. No se enviarán contraseñas ni datos sensibles del alumno a través de URLs.

## Flujo de acceso

1. El adulto crea y verifica su cuenta en TortuScript.
2. El adulto crea uno o más perfiles infantiles.
3. La cuenta adquiere el entitlement de nivel avanzado cuando corresponda.
4. El alumno entra a TortuScript con su perfil.
5. TortuScript comprueba el entitlement server-side.
6. Si el perfil está autorizado, TortuScript inicia una transición autenticada hacia Croco-Script.
7. Croco-Script valida la autorización.
8. Croco-Script identifica al perfil mediante un identificador interno, no mediante información personal innecesaria.
9. El alumno continúa su recorrido avanzado.
10. Al regresar a TortuScript conserva su identidad y perfil.

## Entitlement

El acceso avanzado pertenece a la cuenta familiar mediante el modelo definido en ADR-032.

La decisión de acceso nunca dependerá de:

- una variable JavaScript del navegador;
- un parámetro manipulable de la URL;
- una marca local del perfil;
- una cookie creada por el cliente;
- un código visible en frontend.

La autorización se resolverá en servidor.

## Datos compartidos

El contrato inicial debe limitarse a lo necesario:

- identificador interno de cuenta;
- identificador interno de perfil;
- estado de entitlement;
- versión/compatibilidad del producto;
- identificadores de progreso cuando exista una necesidad real.

No se transferirán datos personales innecesarios.

Croco-Script no debe recibir directamente la contraseña del adulto ni información de pago.

## Progreso

TortuScript y Croco-Script podrán mantener progresos propios, pero compartirán un contrato de identidad común.

El progreso avanzado no debe depender de la implementación interna del frontend de TortuScript.

El contrato deberá permitir:

- progreso por curso;
- progreso por unidad/lección;
- ejercicios completados;
- proyectos;
- evaluaciones;
- versión curricular;
- timestamps necesarios para sincronización.

La migración o modificación del esquema deberá ser versionada.

## Dominios

La forma exacta queda abierta a implementación, pero se favorece una relación de dominio que comunique pertenencia al mismo ecosistema, por ejemplo:

- `tortuscript.com`
- `croco.tortuscript.com`

La elección definitiva deberá considerar seguridad de cookies, aislamiento entre aplicaciones, despliegue y compatibilidad con el proveedor de identidad.

## Seguridad

La integración debe respetar ADR-031.

En particular:

- HTTPS obligatorio;
- sesiones seguras;
- autorización server-side;
- protección contra CSRF cuando corresponda;
- no exponer tokens de larga duración en URLs;
- no colocar secretos en frontend;
- expiración y rotación de credenciales de servicio;
- rate limiting;
- logging mínimo;
- aislamiento entre perfiles;
- validación estricta del audience/issuer de cualquier token de federación.

## Independencia técnica

Croco-Script no debe importar directamente módulos internos de TortuScript.

La comunicación se realizará mediante contratos explícitos, APIs o mecanismos de identidad definidos.

Esto permite que:

- TortuScript evolucione sin romper Croco-Script;
- Croco-Script tenga su propio ciclo de release;
- cada producto pueda escalar de forma independiente;
- los contratos puedan versionarse.

## Roadmap de integración

### Antes de TortuScript V1.0.0

- definir identidad compartida;
- definir entitlement avanzado;
- definir contrato de autorización;
- definir contrato de progreso;
- definir formato curricular compatible;
- crear repositorio inicial de Croco-Script;
- construir un prototipo mínimo de transición autenticada;
- validar aislamiento de perfiles;
- documentar dominios y despliegue.

### Después de TortuScript V1.0.0

- construir experiencia avanzada completa;
- adaptar los tres cursos curriculares;
- implementar proyectos avanzados;
- implementar evaluación;
- completar runtime/sandbox requerido;
- integrar TutorService;
- realizar beta controlada;
- abrir progresivamente el entitlement avanzado.

## Gate

Croco-Script no puede convertirse en requisito para declarar terminado TortuScript V1.0.0.

TortuScript V1.0.0 puede liberarse aunque Croco-Script esté en desarrollo, siempre que los contratos de integración definidos como precondición estén documentados y las piezas críticas de identidad/entitlement no queden diseñadas de forma incompatible con una segunda aplicación.

## Consecuencia principal

El ecosistema pasa a tener dos productos coordinados:

`TortuScript = iniciación y formación infantil`

`Croco-Script = formación técnica avanzada`

La familia mantiene una única cuenta y una única relación comercial, mientras cada producto conserva autonomía técnica y pedagógica.
