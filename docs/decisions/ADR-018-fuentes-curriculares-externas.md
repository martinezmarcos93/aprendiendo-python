# ADR-018 — Repositorios avanzados como fuentes curriculares externas

- Estado: Propuesta
- Fecha: 2026-09-29

## Contexto
Los repositorios curso-python-datos, curso-desarrollo-aplicaciones y curso-orquestacion-streaming-llm contienen material técnico de mayor profundidad y no comparten necesariamente el formato pedagógico de TortuScript.

## Decisión propuesta
No se incorporarán como subdirectorios ni dependencias de ejecución de TortuScript. Se utilizarán como fuentes de conceptos, prerrequisitos, ejercicios, proyectos y herramientas.

Cada adaptación de TortuScript tendrá trazabilidad a su fuente curricular y será un artefacto independiente.

## Consecuencia
Los repositorios fuente podrán evolucionar sin romper automáticamente la plataforma y un mismo conocimiento podrá adaptarse a varias edades.