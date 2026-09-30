# ADR-045: Adaptador del runtime educativo para ChildProfile

Estado: **Aceptada**

## Decisión

El núcleo educativo existente seguirá operando con su estructura de diccionario.
Un adaptador traducirá ese diccionario al `ProgresoSnapshot` asociado al
`ChildProfile` activo.

El adaptador no modifica `progreso.py` ni cambia el modo local. Antes de guardar
verifica que `_perfil` coincida con el `ChildProfile.id` de la sesión.

## Consecuencia

Podemos reutilizar progresivamente las operaciones educativas existentes —XP,
racha, lecciones, práctica y proyectos— sobre persistencia por ChildProfile,
sin hacer una migración masiva ni duplicar el motor educativo.