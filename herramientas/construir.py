#!/usr/bin/env python3
"""Arma TortuScript instalable para familias, en cualquier sistema, con un solo comando (ADR-015).

Uso:
    python herramientas/construir.py                  # detecta el sistema en el que corre
    python herramientas/construir.py --sistema linux  # o lo elegís (tiene que ser el mismo en el que corre)
    python herramientas/construir.py --salida dist

- Una sola configuración para todos los sistemas: PyInstaller en modo carpeta (`onedir`: arranca rápido y el
  subproceso que corre el código del chico no necesita escribir en disco), con el contenido y la web adentro.
- Lo único que cambia por sistema es el empaquetado y el instalador que va adentro:
    linux   → TortuScript-<fecha>-linux-<arq>.tar.gz   con instalar.sh / desinstalar.sh (menú de aplicaciones)
    windows → TortuScript-<fecha>-windows-<arq>.zip    con instalar.bat / desinstalar.bat (menú Inicio y Escritorio);
              si está Inno Setup (iscc), además un instalador .exe
    macos   → TortuScript-<fecha>-macos-<arq>.zip      con instalar.command (carpeta Aplicaciones del usuario)
  Cada instalador comprueba que el sistema sea el suyo antes de hacer nada.
- PyInstaller arma para el sistema en el que corre: para Windows o macOS, corré este mismo comando allá (o el
  workflow manual de GitHub, .github/workflows/construir.yml).
- Requiere PyInstaller (requirements-dev.txt). Instalado, el progreso va a la carpeta de datos del usuario
  (tortuscript/rutas.py).
"""
import argparse
import hashlib
import io
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from tortuscript import rutas  # noqa: E402

NOMBRE = "TortuScript"
SISTEMAS = ("linux", "windows", "macos")
DATOS = ("contenido", "web/templates", "web/static")          # lo que la app lee del disco


def arquitectura():
    maquina = platform.machine().lower()
    return {"amd64": "x86_64", "x64": "x86_64", "aarch64": "arm64"}.get(maquina, maquina or "desconocida")


def elegir_sistema(pedido=None, actual=None):
    """El sistema a construir: el pedido, si coincide con el actual; si no se pide, el actual."""
    actual = actual or rutas.sistema()
    if pedido is None:
        return actual
    if pedido not in SISTEMAS:
        raise SystemExit(f"❌ Sistema desconocido: {pedido}. Elegí uno de: {', '.join(SISTEMAS)}.")
    if pedido != actual:
        raise SystemExit(f"❌ Estás en {actual} y pediste {pedido}. PyInstaller arma para el sistema en el que corre: "
                         f"corré este comando en {pedido} (o usá el workflow manual de GitHub).")
    return pedido


def argumentos_pyinstaller(trabajo):
    """Los mismos para todos los sistemas (solo cambia el separador de --add-data, que es el del sistema)."""
    args = [str(RAIZ / "iniciar_web.py"), "--name", NOMBRE, "--onedir", "--noconfirm", "--clean", "--console",
            "--distpath", str(trabajo / "dist"), "--workpath", str(trabajo / "build"), "--specpath", str(trabajo),
            "--collect-submodules", "tortuscript", "--collect-submodules", "web",
            "--hidden-import", "tortuscript.worker"]
    for carpeta in DATOS:
        args += ["--add-data", f"{RAIZ / carpeta}{os.pathsep}{carpeta}"]
    return args


# ─────────────────────────── instaladores (uno por sistema) ───────────────────────────
INSTALAR_LINUX = """#!/usr/bin/env sh
# Instala TortuScript para tu usuario (sin contraseña de administrador) y lo agrega al menú de aplicaciones.
set -e
if [ "$(uname -s)" != "Linux" ]; then echo "Este paquete es para Linux. Bajá el de tu sistema."; exit 1; fi
AQUI="$(cd "$(dirname "$0")" && pwd)"
DESTINO="${{XDG_DATA_HOME:-$HOME/.local/share}}/tortuscript-programa"
MENU="${{XDG_DATA_HOME:-$HOME/.local/share}}/applications"
rm -rf "$DESTINO" && mkdir -p "$DESTINO" "$MENU"
cp -R "$AQUI/{nombre}/." "$DESTINO/"
chmod +x "$DESTINO/{nombre}"
cat > "$MENU/tortuscript.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=TortuScript
Comment=Aprendé a programar en español
Exec="$DESTINO/{nombre}"
Icon=$DESTINO/_internal/web/static/img/tortuscript.svg
Terminal=false
Categories=Education;Development;
EOF
echo "Listo: buscá «TortuScript» en el menú de aplicaciones. Tu progreso se guarda en ${{XDG_DATA_HOME:-$HOME/.local/share}}/tortuscript"
"""

DESINSTALAR_LINUX = """#!/usr/bin/env sh
# Saca el programa y el acceso del menú. NO borra el progreso de los chicos.
DATOS="${XDG_DATA_HOME:-$HOME/.local/share}"
rm -rf "$DATOS/tortuscript-programa" "$DATOS/applications/tortuscript.desktop"
echo "Listo. El progreso sigue en $DATOS/tortuscript (borralo a mano si ya no lo querés)."
"""

INSTALAR_WINDOWS = """@echo off
rem Instala TortuScript para tu usuario (sin permisos de administrador): menu Inicio y Escritorio.
if not "%OS%"=="Windows_NT" (echo Este paquete es para Windows. & exit /b 1)
set "DESTINO=%LOCALAPPDATA%\\Programs\\TortuScript"
if exist "%DESTINO%" rmdir /s /q "%DESTINO%"
xcopy /e /i /q "%~dp0{nombre}" "%DESTINO%" >nul || (echo No se pudo copiar el programa. & exit /b 1)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0accesos.ps1" "%DESTINO%\\{nombre}.exe" || (echo No se pudieron crear los accesos. & exit /b 1)
echo Listo: TortuScript esta en el menu Inicio y en el Escritorio. Tu progreso se guarda en %APPDATA%\\TortuScript
"""

ACCESOS_WINDOWS = """# Crea los accesos de TortuScript en el menú Inicio y en el Escritorio (lo llama instalar.bat).
param([string]$Programa)
$shell = New-Object -ComObject WScript.Shell
foreach ($carpeta in @([Environment]::GetFolderPath("Programs"), [Environment]::GetFolderPath("Desktop"))) {
  $acceso = $shell.CreateShortcut((Join-Path $carpeta "TortuScript.lnk"))
  $acceso.TargetPath = $Programa
  $acceso.WorkingDirectory = Split-Path -Parent $Programa
  $acceso.Description = "Aprendé a programar en español"
  $acceso.Save()
}
"""

DESINSTALAR_WINDOWS = """@echo off
rem Saca el programa y los accesos. NO borra el progreso de los chicos.
rmdir /s /q "%LOCALAPPDATA%\\Programs\\TortuScript" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\TortuScript.lnk" 2>nul
powershell -NoProfile -Command "Remove-Item (Join-Path ([Environment]::GetFolderPath('Desktop')) 'TortuScript.lnk') -ErrorAction SilentlyContinue"
echo Listo. El progreso sigue en %APPDATA%\\TortuScript (borralo a mano si ya no lo queres).
"""

INSTALAR_MACOS = """#!/bin/sh
# Instala TortuScript en la carpeta Aplicaciones de tu usuario y deja un acceso para abrirlo.
if [ "$(uname -s)" != "Darwin" ]; then echo "Este paquete es para macOS. Bajá el de tu sistema."; exit 1; fi
AQUI="$(cd "$(dirname "$0")" && pwd)"
DESTINO="$HOME/Applications/TortuScript"
rm -rf "$DESTINO" && mkdir -p "$DESTINO"
cp -R "$AQUI/{nombre}/." "$DESTINO/"
xattr -dr com.apple.quarantine "$DESTINO" 2>/dev/null
printf '#!/bin/sh\\n"%s/{nombre}"\\n' "$DESTINO" > "$HOME/Applications/Abrir TortuScript.command"
chmod +x "$DESTINO/{nombre}" "$HOME/Applications/Abrir TortuScript.command"
echo "Listo: abrí «Abrir TortuScript» en tu carpeta Aplicaciones. El progreso se guarda en ~/Library/Application Support/TortuScript"
"""

INNO_SETUP = """; Instalador de Windows con Inno Setup (lo arma construir.py si encuentra iscc).
[Setup]
AppName=TortuScript
AppVersion={version}
DefaultDirName={{localappdata}}\\Programs\\TortuScript
PrivilegesRequired=lowest
OutputBaseFilename={salida}
DisableProgramGroupPage=yes
[Files]
Source: "{carpeta}\\*"; DestDir: "{{app}}"; Flags: recursesubdirs
[Icons]
Name: "{{userprograms}}\\TortuScript"; Filename: "{{app}}\\{nombre}.exe"
Name: "{{userdesktop}}\\TortuScript"; Filename: "{{app}}\\{nombre}.exe"
[Run]
Filename: "{{app}}\\{nombre}.exe"; Description: "Abrir TortuScript"; Flags: postinstall nowait
"""

LEEME = """TortuScript — aprendé a programar en español
=============================================

Este paquete es para {sistema_legible}. Si tu compu tiene otro sistema, bajá el paquete que corresponde.

Para instalar:
{pasos}

No hace falta internet ni tener Python instalado. Tu progreso se guarda solo en tu compu.
Versión: {version}
"""

PASOS = {
    "linux": "  1. Descomprimí este archivo.\n  2. En la carpeta, abrí una terminal y escribí:  sh instalar.sh\n"
             "  3. Buscá «TortuScript» en el menú de aplicaciones.",
    "windows": "  1. Descomprimí este archivo (clic derecho → Extraer todo).\n  2. Doble clic en instalar.bat\n"
               "  3. Abrí «TortuScript» desde el menú Inicio o el Escritorio.",
    "macos": "  1. Descomprimí este archivo.\n  2. Doble clic en instalar.command (si macOS pregunta, elegí Abrir).\n"
             "  3. Abrí «Abrir TortuScript» en tu carpeta Aplicaciones.",
}
LEGIBLE = {"linux": "Linux", "windows": "Windows", "macos": "macOS"}


def archivos_del_instalador(sistema, version):
    """{nombre de archivo: (contenido, fin de línea)} que van junto al programa en el paquete de ese sistema."""
    comunes = {"LEEME.txt": LEEME.format(sistema_legible=LEGIBLE[sistema], pasos=PASOS[sistema], version=version)}
    if sistema == "linux":
        extras = {"instalar.sh": INSTALAR_LINUX.format(nombre=NOMBRE), "desinstalar.sh": DESINSTALAR_LINUX}
    elif sistema == "windows":
        extras = {"instalar.bat": INSTALAR_WINDOWS.format(nombre=NOMBRE), "desinstalar.bat": DESINSTALAR_WINDOWS,
                  "accesos.ps1": "\ufeff" + ACCESOS_WINDOWS}           # con BOM: PowerShell 5 lee bien las tildes
    else:
        extras = {"instalar.command": INSTALAR_MACOS.format(nombre=NOMBRE)}
    fin = "\r\n" if sistema == "windows" else "\n"
    return {nombre: texto.replace("\r\n", "\n").replace("\n", fin) for nombre, texto in {**comunes, **extras}.items()}


def nombre_del_paquete(sistema, hoy=None):
    extension = "tar.gz" if sistema == "linux" else "zip"
    return f"{NOMBRE}-{(hoy or date.today()):%Y%m%d}-{sistema}-{arquitectura()}.{extension}"


def empaquetar(sistema, carpeta_programa, salida, version, hoy=None):
    """Arma el .tar.gz o .zip con la carpeta del programa y el instalador de ese sistema. Devuelve la ruta."""
    salida.mkdir(parents=True, exist_ok=True)
    destino = salida / nombre_del_paquete(sistema, hoy)
    extras = archivos_del_instalador(sistema, version)
    raiz = f"{NOMBRE}-{sistema}"
    if sistema == "linux":
        with tarfile.open(destino, "w:gz") as tar:
            tar.add(carpeta_programa, arcname=f"{raiz}/{NOMBRE}")
            for nombre, texto in extras.items():
                datos = texto.encode("utf-8")
                info = tarfile.TarInfo(f"{raiz}/{nombre}")
                info.size, info.mode = len(datos), 0o755 if nombre.endswith(".sh") else 0o644
                tar.addfile(info, io.BytesIO(datos))
    else:
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
            for archivo in sorted(Path(carpeta_programa).rglob("*")):
                if archivo.is_file():
                    info = zipfile.ZipInfo.from_file(archivo, f"{raiz}/{NOMBRE}/{archivo.relative_to(carpeta_programa).as_posix()}")
                    with open(archivo, "rb") as f:
                        z.writestr(info, f.read(), zipfile.ZIP_DEFLATED)
            for nombre, texto in extras.items():
                info = zipfile.ZipInfo(f"{raiz}/{nombre}")
                info.external_attr = (0o755 if nombre.endswith(".command") else 0o644) << 16
                z.writestr(info, texto.encode("utf-8"), zipfile.ZIP_DEFLATED)
    Path(str(destino) + ".sha256").write_text(
        f"{hashlib.sha256(destino.read_bytes()).hexdigest()}  {destino.name}\n", encoding="utf-8")
    return destino


def inno_setup(carpeta_programa, salida, version, hoy=None):
    """Si está Inno Setup (iscc), arma además el instalador .exe de Windows. Devuelve su ruta o None."""
    iscc = shutil.which("iscc") or shutil.which("ISCC")
    if not iscc:
        return None
    nombre = nombre_del_paquete("windows", hoy).rsplit(".", 1)[0] + "-instalador"
    iss = Path(carpeta_programa).parent / "tortuscript.iss"
    iss.write_text(INNO_SETUP.format(version=version, salida=nombre, carpeta=carpeta_programa, nombre=NOMBRE),
                   encoding="utf-8")
    subprocess.run([iscc, f"/O{salida}", str(iss)], check=True)
    return salida / f"{nombre}.exe"


def _version():
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(RAIZ), capture_output=True, text=True, timeout=10)
        commit = r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = ""
    return f"{date.today():%d/%m/%Y}" + (f" ({commit})" if commit else "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sistema", choices=SISTEMAS, help="por defecto, el sistema en el que corre")
    ap.add_argument("--salida", default=str(RAIZ / "dist"))
    args = ap.parse_args()
    sistema = elegir_sistema(args.sistema)
    try:
        import PyInstaller.__main__ as pyinstaller
    except ImportError:
        raise SystemExit("❌ Falta PyInstaller:  python -m pip install -r requirements-dev.txt")
    salida, version = Path(args.salida), _version()
    print(f"🔨 Armando TortuScript para {LEGIBLE[sistema]} ({arquitectura()})…", flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        trabajo = Path(tmp)
        pyinstaller.run(argumentos_pyinstaller(trabajo))
        carpeta = trabajo / "dist" / NOMBRE
        paquete = empaquetar(sistema, carpeta, salida, version)
        print(f"📦 {paquete}")
        if sistema == "windows":
            exe = inno_setup(carpeta, salida, version)
            print(f"📦 {exe}" if exe else "   (sin Inno Setup: solo el .zip con instalar.bat)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
