
# ADR-034 — Mobile-first, UX final y sistema visual comercial

- Estado: Aceptada
- Fecha: 2026-09-30
- Decisor: Marcos
- Relacionadas: ADR-017, ADR-027, ADR-029

## Decisión

La experiencia web será mobile-first y responsive. No se desarrollará una aplicación móvil nativa para V1.

Validación mínima:
- 320 px;
- 375 px;
- 390 px;
- 768 px;
- escritorio.

Se validarán navegación, formularios, editor, teclado virtual, Tortuga, juegos, ejercicios, progreso, perfiles, checkout y accesibilidad.

El sistema visual será común a toda la plataforma, con adaptación por edad. Se crearán assets solamente donde mejoren orientación, feedback o identidad.

No se generará una gran biblioteca decorativa antes de validar la UX.

## Roadmap

### 01–05/10
- Auditoría pantalla por pantalla.
- Inventario de componentes.
- Detección de duplicaciones.

### 06–12/10
- Responsive.
- Navegación táctil.
- Editor móvil.
- Accesibilidad base.

### 13–19/10
- Flujo adulto/perfil.
- Jerarquía de navegación.
- Estados gratuito/premium/bloqueado.

### 15–19/12
- Assets finales.
- Estados de Tortu.
- Iconografía.
- Ilustraciones funcionales.

### 20–22/12
- QA visual y accesibilidad.

### 23–28/12 — Fase 15
- Regression visual completa.

### 29–31/12 — Fase 16
- Congelación visual.
