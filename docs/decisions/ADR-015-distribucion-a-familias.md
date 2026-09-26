# ADR-015: Cómo llega TortuScript a las familias (instaladores)

## Estado: Aceptada (26/09/2026) — decisión de Marcos: **el sistema se detecta solo o lo elige el usuario, y la
construcción es lo más agnóstica posible** (un solo comando para todos los sistemas)

> Ver la regla de gobernanza en el [índice](README.md). Origen: pendiente "instalador nativo por sistema operativo"
> (`docs/ROADMAP_MIMO_KIDS.md`) y la regla del vault: Windows → PyInstaller + Inno Setup; Linux → evaluar
> .deb / AppImage / Flatpak y documentar el primero que se use.

## Contexto
- Hoy se distribuye un `.zip` (`herramientas/crear_paquete.py`) con `instalar.bat` / `instalar.sh`, que crean un entorno
  de Python e instalan Flask (o lo toman de las ruedas incluidas con `--con-ruedas`). **Exige tener Python instalado**:
  es una barrera para una familia que no programa.
- La app es web local: un servidor Flask en `127.0.0.1` que abre el navegador. No hay ventana propia.
- **El código del chico corre en un subproceso** lanzado como `[sys.executable, "-m", "tortuscript.worker"]`
  (`tortuscript/proceso.py`), con límites de memoria y tiempo (`resource` en Linux/macOS, Job Object en Windows).
- Falta un dato que es de producto, no técnico: **qué sistema operativo usan las familias y escuelas** a las que apunta
  TortuScript (Fase 0 del roadmap maestro).

## Opciones

| Opción | Para quién | + | − |
|---|---|---|---|
| **A. Windows: PyInstaller + Inno Setup** (patrón del vault) | la mayoría de las compus hogareñas | instalador "Siguiente → Siguiente → Finalizar", ícono en el menú, sin Python instalado | hay que adaptar el subproceso (ver abajo); firma de código para evitar el aviso de SmartScreen (costo) |
| **B. Linux: AppImage** | cualquier distro | un solo archivo, sin root, no toca el sistema | hay que marcarlo como ejecutable (un paso raro para una familia); ~40–60 MB con Python adentro |
| **C. Linux: .deb** | Ubuntu/Debian (escuelas con Linux) | se instala con doble clic en el centro de software; menú y desinstalación normales | solo familia Debian; pide contraseña de administrador |
| **D. Linux: Flatpak** | cualquier distro | sandbox del sistema, actualizaciones por Flathub | cadena de construcción y publicación más pesada; revisión de Flathub |
| **E. Seguir con el .zip** | quien ya tiene Python | ya existe | no sirve para familias no técnicas |

## Decisión
1. **Primero, que Marcos defina el sistema objetivo** (dato de la Fase 0). Sin eso no se construye ningún instalador.
2. Si es **Windows**: opción A, siguiendo `instaladores/distribucion-windows.md` del vault.
3. Si es **Linux**: **AppImage** (B) como primer formato, por ser el de menor complejidad, sin root y para cualquier
   distro. Si aparece una escuela con Ubuntu administrado, sumar .deb (C). Flatpak (D) solo si se decide publicar en
   Flathub.
4. El `.zip` (E) queda para desarrolladores y para quien ya tiene Python.

## Cambios técnicos que haría falta (en cualquier opción empaquetada)
- **Subproceso del worker:** con PyInstaller (y en un AppImage con Python embebido), `sys.executable` puede no ser un
  intérprete de Python normal. `proceso.py` tiene que detectar si la app está "congelada" (`getattr(sys, "frozen", False)`)
  y lanzar el mismo ejecutable con una marca (p. ej. `TortuScript.exe --worker`) en lugar de `-m tortuscript.worker`.
  Los límites (Job Object / `resource`) se mantienen igual.
- **Dónde se guarda el progreso:** hoy `progreso_*.json` vive junto al programa. Instalado en `Program Files` o dentro de
  un AppImage (solo lectura), no se puede escribir ahí: hay que usar la carpeta de datos del usuario
  (`%APPDATA%\TortuScript`, `~/.local/share/tortuscript`) y **migrar** lo que haya junto al programa sin perder nada
  (el progreso solo crece, ADR-002).
- **Logs:** mismo criterio que el progreso (carpeta del usuario).
- **Pruebas:** el jugador de cursos y la simulación tienen que correr también contra la app empaquetada.

## Consecuencias
+ Una familia no técnica puede instalar y abrir TortuScript sin saber qué es Python.
− Cada formato suma una cadena de construcción que mantener, y en Windows posiblemente un certificado de firma.
− El cambio de carpeta de datos toca el guardado del progreso: requiere migración cuidadosa y tests.

## Notas de implementación (26/09/2026)
- `herramientas/construir.py`: **un solo comando** que detecta el sistema (o recibe `--sistema`, que tiene que coincidir:
  PyInstaller arma para el sistema en el que corre) y usa **una sola configuración** de PyInstaller (`onedir`, consola).
  Lo único distinto por sistema es el empaquetado y su instalador (`instalar.sh`, `instalar.bat` + `accesos.ps1`,
  `instalar.command`), que comprueba el sistema antes de hacer nada, no pide administrador y nunca borra el progreso.
- `tortuscript/rutas.py`: carpeta de datos por sistema cuando está instalado; desde el código fuente, igual que antes. Copia
  (no mueve) el progreso que hubiera junto al programa. `TORTUSCRIPT_DATOS` fuerza otra carpeta.
- Worker instalado: `TortuScript --worker` (`proceso.comando_worker`), atendido antes de importar Flask.
- `.github/workflows/construir.yml`: arma los tres sistemas, **solo a mano** (`workflow_dispatch`).
- **Probado en Linux x86_64** de punta a punta (paquete de 12 MB, instalación en un HOME aislado, código del chico por el
  worker instalado, tortuga en Chromium, datos en la carpeta del usuario, desinstalar sin perder progreso).
  **Windows y macOS todavía no se construyeron ni probaron**: hace falta correr el comando allá o el workflow.
- Sin ícono propio en el ejecutable (PyInstaller necesita .ico/.icns; el acceso de Linux usa el SVG de la app).

