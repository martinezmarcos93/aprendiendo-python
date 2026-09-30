
# ADR-031 — Autenticación, sesiones y seguridad web

- Estado: Aceptada
- Fecha: 2026-09-30
- Decisor: Marcos
- Relacionadas: ADR-026, ADR-029, ADR-030, ADR-033

## Decisión

La autenticación remota será exclusivamente de la cuenta adulta.

Requisitos mínimos:
- email verificado;
- contraseña almacenada con Argon2id o equivalente aceptable;
- recuperación segura;
- sesiones con tokens aleatorios y rotación al autenticarse o elevar privilegios;
- cookies Secure + HttpOnly + SameSite;
- HTTPS obligatorio;
- CSRF para operaciones con sesión;
- autorización server-side en cada recurso;
- rate limiting y protección contra credential stuffing;
- reautenticación para operaciones sensibles;
- secretos fuera del repositorio;
- logs de seguridad sin contraseñas, tokens, datos de pago ni contenido innecesario de menores;
- CSP, HSTS y cabeceras de seguridad;
- validación de entrada y salida;
- protección XSS;
- CORS explícito y mínimo.

Se adoptará OWASP ASVS como referencia de verificación.

No se almacenarán contraseñas en texto plano ni tokens de sesión en localStorage.

## Roadmap

### 20/10–02/11 — Fundación
- Modelo de autenticación.
- Hashing.
- Sesiones.
- Email verification.
- Recuperación.

### 03–09/11 — Endurecimiento
- CSRF.
- Rate limiting.
- CORS.
- Autorización.
- Reautenticación.
- Auditoría de eventos.

### 10–23/11 — Seguridad aplicada
- Tests de XSS.
- Autorización horizontal/vertical.
- Abuso de endpoints.
- Pruebas de sesión.
- Secretos y configuración.

### 24/11–07/12 — Observabilidad
- Alertas.
- Auditoría de accesos.
- Backups.
- Restauración.

### 20–22/12
- Checklist ASVS.
- Revisión independiente cuando sea posible.

### 23–28/12 — Fase 15
- Security regression.
- Pruebas de abuso.
- Freeze.

### 29–31/12 — Fase 16
- Release solamente sin vulnerabilidades críticas/altas sin tratamiento aceptado.

## Referencias

OWASP ASVS 5.0 y OWASP Session Management, Password Storage y CSRF Cheat Sheets.
