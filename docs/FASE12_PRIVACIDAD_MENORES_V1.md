# Fase 12 — Privacidad y menores V1

## Base normativa de diseño

Para Argentina, el diseño toma como referencia la Ley 25.326 y material de la AAIP. La AAIP indica que los datos personales requieren una base válida para su tratamiento y que, en contextos de niñas, niños y adolescentes, deben considerarse autonomía progresiva, información comprensible y, cuando corresponda, intervención de quien ejerce la responsabilidad parental. Esto debe validarse jurídicamente antes de un lanzamiento comercial. 

Referencia normativa: Ley 25.326, Decreto 1558/2001 y materiales de AAIP sobre niñez y privacidad.

## Política de minimización

Datos imprescindibles para el servicio futuro:
- cuenta adulta: medio de autenticación y datos estrictamente necesarios para operar la cuenta;
- perfil educativo: identificador técnico, alias opcional, franja de edad, configuración pedagógica;
- progreso: unidades completadas, competencias, resultados mínimos y fechas necesarias;
- consentimiento: versión, fecha, ámbito y estado.

Datos que no se recopilan por defecto:
- domicilio;
- geolocalización;
- contactos;
- fotografías;
- biometría;
- información de salud;
- contenido privado no necesario;
- historial de navegación externo.

## Consentimiento y edad

El sistema debe separar:
1. información clara al menor;
2. asentimiento o participación del menor según corresponda;
3. consentimiento de quien ejerza responsabilidad parental cuando sea jurídicamente necesario;
4. evidencia mínima de la decisión.

No se fija una edad universal dentro del código. La regla debe ser configurable por jurisdicción y revisada legalmente antes de operar.

## Derechos y operaciones

Deben existir procedimientos para:
- acceso;
- rectificación;
- actualización;
- supresión;
- exportación;
- revocación cuando corresponda;
- consulta sobre finalidad y destinatarios.

## Retención

Cada clase de dato debe tener una finalidad y un plazo definido. Al vencerlo, se elimina o anonimiza según corresponda. Los logs deben tener una retención menor que los datos pedagógicos y nunca deben funcionar como copia paralela del perfil.

## Analítica

Por defecto:
- analítica agregada;
- sin publicidad comportamental;
- sin perfilado comercial del menor;
- sin compartir código o texto de ejercicios con terceros;
- eventos de producto limitados a los necesarios para funcionamiento y calidad.

## Terceros

Todo tercero debe quedar registrado con:
- finalidad;
- datos recibidos;
- región de procesamiento;
- contrato/base legal aplicable;
- plazo de retención;
- mecanismo de eliminación.

## Seguridad

Aplicar minimización, control de acceso, separación de perfiles, cifrado en tránsito y reposo cuando exista backend remoto, gestión de secretos y auditoría de accesos.

## Estado

Esta fase define arquitectura y gobernanza, no constituye asesoramiento jurídico ni habilita un lanzamiento comercial.
