# Prueba SIMULADA con chicos — 2026-09-26

> ⚠️ **Simulación, no chicos reales.** 8 perfiles sintéticos jugaron por la interfaz real (Chromium) con
> `herramientas/simular_chicos.py`, equivocándose con probabilidades fijas y reproducibles. Mide la **robustez** del
> producto (que nadie quede trabado, que la interfaz no falle, que las ayudas destraben, que se vea bien en cada
> pantalla y con cada ajuste). **No mide** si a un chico le gusta, si vuelve al día siguiente ni si aprende: la
> Puerta 1 del roadmap sigue necesitando chicos reales.

## Perfiles y resultados

| Chico | Experiencia | Pantalla / ajustes | Comportamiento | Lecciones jugadas | Hechas (total) | XP | Al primer intento | Pistas / respuestas vistas |
|---|---|---|---|---|---|---|---|---|
| Sofi (10) | nunca | 360px | usa pistas · error 35% | 8 | 8 | 343 | 82% | 4 / 0 |
| Tomi (12) | poquito → tu-primera-variable | 1280px | normal · error 15% | 8 | 8 | 383 | 84% | 0 / 0 |
| Juli (11) | nunca | 1280px, tam=enorme, contraste=alto | normal · error 25% | 6 | 6 | 283 | 79% | 0 / 0 |
| Mati (13) | bastante → si-es-grande | 1280px | solo teclado · error 10% | 8 | 8 | 400 | 100% | 0 / 0 |
| Cami (10) | nunca | 414px, movimiento=reducido, letra=legible | se rinde rápido · error 45% | 6 | 6 | 276 | 77% | 0 / 2 |
| Leo (14) | bastante | 1280px | rápido · error 5% | 10 | 10 | 490 | 97% | 0 / 0 |
| Vale (11) | nunca | 768px, tam=grande | usa pistas · error 30% | 7 | 7 | 308 | 70% | 1 / 0 |
| Nico (12) | nunca | 1280px | normal · error 20% | 9 | 9 | 420 | 85% | 0 / 0 |

Total: 62 lecciones y 363 pasos jugados en 249 s.

## Robustez (lo que sí mide)

- Errores de consola (incluye violaciones de CSP): **0**
- Callejones sin salida y pantallas desbordadas: **0**
- Todos los pasos con error se destrabaron con reintento, pista o "ver respuesta": **sí**.

## Dónde se equivocaron (simulado)

Los errores de la simulación son al azar: esta lista muestra **dónde se probó** la recuperación, no qué es difícil.

- dos-variables#2 (predecir): 6 error(es)
- texto-o-cuenta#3 (predecir): 5 error(es)
- dos-lineas#5 (escribir): 5 error(es)
- hola-mundo#6 (escribir): 4 error(es)
- texto-o-cuenta#4 (elegir): 4 error(es)
- variable-de-texto#2 (elegir): 4 error(es)
- dos-variables#3 (predecir): 3 error(es)
- tu-primera-variable#3 (predecir): 2 error(es)
- pedir-el-nombre#3 (predecir): 2 error(es)
- tu-primera-variable#6 (escribir): 2 error(es)

## Señales objetivas en el contenido (no dependen de la simulación)

- Pasos de elegir/predecir/completar/ordenar **sin pista propia** (usan la genérica): **137**.
  Primeros: hola-mundo#3, hola-mundo#4, texto-o-cuenta#4, texto-o-cuenta#5, dos-lineas#2, dos-lineas#3, dos-lineas#4, tu-primera-variable#2, tu-primera-variable#5, variable-de-texto#2, variable-de-texto#3, variable-de-texto#4 …
- Consignas de más de 160 caracteres: **1** → proyecto-casa#3 (166)

## Veredicto de la Puerta 1 (simulada)

- **Robustez: PASA.** Ningún perfil quedó trabado, sin errores de interfaz ni desbordes.
- **Retención y gusto: SIN RESPUESTA.** Una simulación no puede contestarlo. Se toma la decisión de Marcos (26/09/2026)
  de seguir con la Fase 2 usando esta prueba como sustituto provisorio, y queda pendiente probar con chicos reales.
