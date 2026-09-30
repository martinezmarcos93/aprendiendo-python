# TortuScript — Modelo curricular V1

## Propósito

Fase 2 convierte la definición de producto en un contrato curricular independiente del motor actual.

El motor de lecciones existente seguirá consumiendo su formato operativo. Este modelo describe qué debe significar una unidad curricular, no cómo se renderiza ni cómo se ejecuta.

## Entidades

### Itinerario

Agrupa una secuencia o conjunto coherente de competencias.

Campos mínimos:

- `id`
- `titulo`
- `descripcion`
- `orden`
- `profundidad`
- `unidades`

### Unidad

Es la unidad curricular reutilizable.

Campos:

- `id`
- `titulo`
- `descripcion`
- `franja_edad`
- `nivel`
- `dificultad`
- `competencias`
- `prerrequisitos`
- `duracion_estimada_min`
- `lenguaje`
- `tipo_actividad`
- `proyecto`
- `fuente_curricular`
- `modulo_fuente`
- `estado_acceso`
- `version`

### Competencia

Una capacidad observable que el alumno puede demostrar.

Ejemplos:

- reconocer_entrada_salida;
- usar_variables;
- construir_condicionales;
- usar_repeticion;
- definir_funciones;
- depurar_programas;
- leer_html;
- modificar_css;
- responder_a_eventos_js;
- consultar_datos_sql;
- relacionar_tablas;
- integrar_interfaz_logica_datos.

Una competencia no debe codificar una edad ni una dificultad.

### Prerrequisito

Referencia a una competencia o unidad necesaria.

Formato conceptual:

`{ "tipo": "competencia|unidad", "id": "...", "minimo": "introduccion|funcional|dominio" }`

### Fuente curricular

Permite trazabilidad hacia contenido externo sin convertirlo en dependencia de ejecución.

Campos:

- `repositorio`
- `modulo`
- `referencia`
- `version_fuente`

## Dimensiones independientes

### Edad

Indica para quién está diseñado el tratamiento pedagógico.

### Nivel

Indica posición dentro del itinerario.

Valores conceptuales:

- introduccion;
- fundamentos;
- intermedio;
- avanzado.

### Dificultad

Indica esfuerzo cognitivo/técnico de la actividad concreta.

Valores conceptuales:

- baja;
- media;
- alta;
- desafio.

Una unidad puede ser de fundamentos y tener dificultad alta.

### Duración

Es tiempo estimado de trabajo, no una duración obligatoria.

### Acceso

El estado de acceso es independiente del contenido.

Valores:

- gratuito;
- premium;
- prueba;
- bloqueado_por_prerrequisito;
- no_publicado.

El catálogo puede usar `por_definir` únicamente como metadato documental mientras no exista una decisión comercial.

## Tipos de actividad

El modelo no limita la actividad al motor actual.

Puede representar:

- explicar;
- reconocer;
- predecir;
- completar;
- ordenar;
- escribir;
- modificar;
- depurar;
- investigar;
- proyecto;
- revisar;
- integrar.

El motor actual puede mapear varias de estas actividades a sus seis tipos de paso.

## Principios de compatibilidad

1. El catálogo no debe depender de Flask.
2. El catálogo no debe depender de JavaScript.
3. El catálogo no debe asumir TortuScript como único lenguaje.
4. El progreso debe poder referenciar unidades y competencias mediante IDs estables.
5. Agregar metadatos no debe invalidar contenido existente.
6. Una unidad puede tener diferentes experiencias por edad sin duplicar la competencia.
7. La evaluación debe poder expresar competencia demostrada, no solo paso completado.
8. Las fuentes externas son referencias, no imports de ejecución.

## Contrato conceptual

```json
{
  "id": "python-condicionales-01",
  "titulo": "Tomar decisiones",
  "franja_edad": "constructores",
  "nivel": "fundamentos",
  "dificultad": "media",
  "competencias": ["construir_condicionales"],
  "prerrequisitos": [
    {"tipo": "competencia", "id": "usar_variables", "minimo": "funcional"}
  ],
  "duracion_estimada_min": 20,
  "lenguaje": "python",
  "tipo_actividad": ["explicar", "predecir", "escribir", "depurar"],
  "proyecto": null,
  "fuente_curricular": null,
  "modulo_fuente": null,
  "estado_acceso": "gratuito",
  "version": 1
}
```

Este contrato es conceptual en Fase 2. La implementación del esquema operativo queda fuera de esta fase y se realizará cuando corresponda estabilizar el catálogo.

## Relación con el motor actual

El formato JSON actual de `contenido/cursos/` sigue siendo válido.

La migración futura deberá ser gradual:

`catálogo curricular` → `adaptador de contenido` → `motor actual`

No se reemplaza el formato operativo sin pruebas de compatibilidad y sin proteger el progreso existente.

## Criterios de aceptación de Fase 2

- Edad, nivel y dificultad son dimensiones separadas.
- Competencias tienen identidad propia.
- Prerrequisitos pueden apuntar a unidades o competencias.
- Las fuentes curriculares externas tienen trazabilidad.
- Acceso está separado del contenido.
- El modelo no depende del runtime.
- Existe una ruta de adaptación hacia el motor actual sin migración destructiva.
