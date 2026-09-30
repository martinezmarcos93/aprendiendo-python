# ADR-024 — Proyecto integrador adaptativo y exportable

- Estado: Aceptada
- Fecha: 2026-09-29

## Contexto

TortuScript necesita una etapa en la que el alumno deje de trabajar únicamente con ejercicios aislados y construya un producto funcional propio.

La Fase 9 debe integrar las competencias desarrolladas en Python, Web y SQL sin imponer que todos los proyectos utilicen los tres bloques. El proyecto debe poder adaptarse a la edad, conocimientos, progreso y recorrido previo de cada alumno.

La plataforma tampoco debe quedar atada a un único proyecto. Se necesita una infraestructura curricular que permita incorporar nuevos tipos de proyecto sin rediseñar el motor.

## Decisión propuesta

La Fase 9 se implementará como un sistema de **proyectos integradores múltiples, adaptativos y exportables**.

### 1. Catálogo de proyectos

El sistema soportará múltiples proyectos integradores, organizados como recursos curriculares independientes.

Un proyecto podrá definir:

- objetivo funcional;
- competencias requeridas;
- bloques técnicos involucrados;
- edad o franjas pedagógicas compatibles;
- nivel de dificultad;
- prerrequisitos;
- etapas/desafíos;
- criterios de evaluación;
- ayudas desbloqueables;
- archivos iniciales;
- archivos exportables;
- reglas de finalización.

La infraestructura no dependerá de un único archivo o proyecto fijo.

### 2. Integración técnica mínima

Cada proyecto deberá integrar **como mínimo dos de los tres bloques**:

- Python;
- Web (HTML/CSS/JavaScript);
- SQL.

No será obligatorio utilizar los tres.

JavaScript será obligatorio cuando el proyecto incluya el bloque Web. Su enseñanza y evaluación deberán buscar comprensión real del comportamiento de la interfaz, eventos, errores y consecuencias de las modificaciones, no solamente reproducción de fragmentos de código.

### 3. Alumno como autor

El alumno será quien construya el código del proyecto.

Tortu podrá proporcionar:

- pistas;
- ejemplos;
- fragmentos parciales;
- explicaciones;
- estructuras iniciales;
- ayudas desbloqueables.

La cantidad de ayuda disponible será adaptativa y podrá depender de:

- edad/franja pedagógica;
- conocimientos demostrados;
- progreso;
- competencias ya adquiridas;
- errores y dificultades observadas;
- recorrido curricular previo.

El sistema no deberá sustituir sistemáticamente el trabajo del alumno por una solución completa.

### 4. Proyecto adaptativo

Las consignas, etapas, dificultad, cantidad de ayuda y alcance podrán variar según el perfil curricular del alumno.

La arquitectura deberá permitir que un mismo tipo de proyecto tenga variantes pedagógicas para diferentes franjas de edad.

Las franjas de edad actuales siguen siendo hipótesis operativas y no se consideran límites rígidos.

### 5. Evaluación

La evaluación combinará:

1. objetivos funcionales por etapas;
2. desafíos verificables;
3. evaluación automática;
4. rúbrica pedagógica;
5. comprobación funcional del producto.

El criterio fundamental de finalización será funcional:

> Un proyecto se considera completado cuando efectivamente realiza aquello para lo que fue construido y satisface sus criterios de aceptación.

No se definirá como criterio suficiente la mera coincidencia textual con una solución de referencia.

### 6. Persistencia y exportación

El alumno podrá conservar su trabajo y descargar los archivos del proyecto.

El proyecto terminado deberá poder exportarse para ejecutarse localmente fuera de TortuScript.

La exportación deberá estar diseñada para facilitar una transición progresiva hacia herramientas reales de desarrollo.

### 7. VS Code

La Fase 9 incluirá una introducción práctica a Visual Studio Code como herramienta de desarrollo.

El objetivo será que el alumno comprenda, como mínimo:

- qué es un editor de código;
- cómo abrir una carpeta de proyecto;
- cómo identificar archivos;
- cómo editar y guardar;
- cómo abrir una terminal;
- cómo ejecutar el proyecto;
- cómo reconocer errores básicos.

No se pretende convertir VS Code en un curso independiente.

### 8. SQL en proyectos

La restricción read-only de SQL V1 se mantiene para los ejercicios del curso de SQL.

Los proyectos integradores podrán utilizar persistencia y operaciones de escritura cuando el proyecto lo requiera, incluyendo operaciones equivalentes a:

- INSERT;
- UPDATE;
- DELETE.

Estas operaciones deberán ejecutarse dentro de un entorno controlado y apropiado para el proyecto y su nivel pedagógico.

La habilitación de escritura en proyectos no modifica retroactivamente las reglas de evaluación de la Fase 8.

### 9. Arquitectura de ejecución

La arquitectura interna de Flask/Python/SQLite podrá permanecer oculta para el alumno.

La interfaz educativa será simplificada y adaptada al nivel pedagógico.

La Fase 9 no exige enseñar explícitamente la arquitectura:

HTML/CSS/JS → Flask → Python → SQLite

aunque podrá introducir progresivamente conceptos necesarios para comprender qué ocurre dentro del proyecto.

### 10. Estado del proyecto

La infraestructura deberá poder representar, como mínimo:

- proyecto disponible;
- proyecto bloqueado;
- proyecto iniciado;
- etapa en progreso;
- etapa completada;
- proyecto completado;
- proyecto exportable.

Los estados curriculares y los criterios de acceso deberán permanecer separados de la disponibilidad comercial.

### 11. Preparación para futuros proyectos

La implementación deberá permitir agregar nuevos proyectos sin modificar el núcleo del motor cuando el proyecto utilice capacidades ya soportadas.

Los proyectos deberán poder declararse como datos curriculares siempre que sea técnicamente viable.

La Fase 9 no se limitará a un único proyecto demostrativo.

## Fuera de alcance

Esta ADR no incorpora todavía:

- un LLM como asistente permanente;
- cuentas cloud;
- sincronización remota;
- marketplace de proyectos;
- comunidad;
- publicación pública de proyectos;
- analítica comercial avanzada.

## Tortu como asistente

El concepto de Tortu como asistente educativo queda reconocido como una línea futura del producto, pero **no forma parte de la implementación obligatoria de la Fase 9**.

Su diseño podrá comenzar en una fase posterior y no tendrá una posición fija dentro del roadmap. Se priorizará después de completar el núcleo curricular restante.

Cuando se implemente, deberá contemplar desde el diseño la adaptación por edad, contexto curricular y protección de alumnos menores.

## Actualización inmediata de Nivel 0

Antes de considerar cerrada la transición hacia el proyecto integrador, Nivel 0 deberá incorporar conceptos fundamentales que el producto necesita para que el alumno pueda comprender y utilizar proyectos reales:

- JSON;
- Git;
- GitHub.

Estos contenidos serán conceptuales y prácticos, adaptados por edad, y deberán permitir que el alumno entienda qué son, para qué sirven y cómo se relacionan con un proyecto de software.

La incorporación de estos contenidos no implica enseñar Git/GitHub profesionalmente en profundidad.

## Consecuencias

La Fase 9 se convierte en una transición explícita desde el aprendizaje guiado hacia la creación de software funcional.

El alumno podrá elegir proyectos diferentes, construirlos con asistencia graduada, demostrar que funcionan y llevárselos a su computadora.

La plataforma deberá disponer de una infraestructura de proyectos suficientemente genérica para soportar nuevas experiencias sin duplicar el motor educativo.

La separación entre SQL V1 y SQL utilizado por proyectos evita ampliar retrospectivamente el alcance de la Fase 8.

La arquitectura también queda preparada para incorporar posteriormente un asistente educativo llamado Tortu sin convertir el LLM en una dependencia del proyecto integrador.
