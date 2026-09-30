# Auditoría Fase 7 — Web esencial
## 2026-09-30

Estado: implementación en rama de consolidación; pendiente validación final de CI y validación local.

### Alcance implementado

Fase 7 incorpora un itinerario Web esencial de 12 lecciones:

- HTML: estructura, contenido/atributos y reparación.
- CSS: selectores, clases/espacio y reparación.
- JavaScript: variables, eventos y DOM.
- Mini productos: ficha de criatura, botón interactivo y reto de reparación.

El objetivo sigue la ADR-020 aceptada: comprender, leer, modificar y depurar interfaces pequeñas, sin convertir Web en un segundo itinerario con la profundidad de Python.

### Arquitectura

Los ejercicios Web usan el mismo motor de lecciones y progreso existente.

El código Web del alumno no se ejecuta en Flask ni en un proceso Python del servidor. La página crea una previsualización en un iframe con sandbox="allow-scripts" y una CSP interna sin conexiones de red. El servidor solamente realiza validación declarativa del texto: tamaño, recursos externos bloqueados y fragmentos requeridos por cada ejercicio.

La evaluación declarativa está en tortuscript/web_evaluacion.py.

### Currículo

El curso se incorpora al camino después de py-problemas. El catálogo curricular registra las competencias leer_html, modificar_css y responder_a_eventos_js, además de actividades de integración y depuración.

### Seguridad

No se aceptan iframes, object/embed, formularios, esquemas javascript:, scripts externos ni imports CSS externos en el código enviado al servidor.

La previsualización está aislada del documento principal mediante sandbox y no recibe acceso al mismo origen. La CSP de la previsualización bloquea conexiones de red.

### Verificación

Se añadieron pruebas estructurales del curso y del evaluador declarativo. La ejecución final de GitHub Actions se considera requisito para cerrar formalmente la fase.

No se inicia Fase 8 como parte de este trabajo.
