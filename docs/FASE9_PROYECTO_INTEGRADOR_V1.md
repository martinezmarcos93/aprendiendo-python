# Fase 9 — Proyecto integrador V1

Fecha de implementación inicial: 2026-09-29.

La Fase 9 introduce proyectos integradores múltiples, adaptativos y exportables, conforme a ADR-024.

## Alcance implementado

- Catálogo declarativo en `contenido/proyectos/catalogo.json`.
- Dos proyectos iniciales:
  - Ficha interactiva de una criatura: Web + Python.
  - Inventario de aventura: Python + SQL.
- Regla de desbloqueo: el alumno debe haber completado los dos bloques declarados por el proyecto.
- Estado persistente por perfil en `proyectos_integradores`.
- Archivos editables dentro del proyecto.
- Etapas con criterios verificables.
- Ayudas desbloqueables según el nivel actual.
- Exportación ZIP cuando todas las etapas están completas.
- Mapa y menú con acceso a proyectos integradores.
- Guía práctica de VS Code.
- Nivel 0 ampliado con JSON, Git y GitHub.

## Adaptación

El motor ya conserva contexto de:

- bloques completados;
- XP/nivel;
- experiencia declarada en el perfil;
- franja de edad cuando exista.

La edad todavía no es un dato obligatorio del onboarding, por lo que no se usa como requisito rígido. Esto deja preparado el motor para la posterior definición curricular por edades.

## Seguridad

La validación de etapas no ejecuta los archivos del proyecto dentro del servidor Flask. Se comprueban criterios declarados y sintaxis Python cuando corresponde.

La exportación genera un ZIP en memoria y nunca ejecuta sus archivos.

## Próximos incrementos de Fase 9

La infraestructura queda preparada para:

- más tipos de proyecto;
- más variantes por edad;
- criterios funcionales más ricos;
- ayudas adaptativas más precisas;
- persistencia SQL controlada en proyectos;
- mejoras de editor;
- validación funcional de aplicaciones exportadas.
