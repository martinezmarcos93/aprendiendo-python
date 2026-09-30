"""Puente explícito entre progreso local legado y progreso por ChildProfile.

No se ejecuta automáticamente. Una cuenta autenticada debe solicitar la importación
de un perfil local concreto y el servicio copia sus datos al ChildProfile activo.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from tortuscript.perfil_educativo import PerfilEducativoService, ContextoEducativoError
from tortuscript.progreso import cargar_progreso, sanitizar_perfil
from tortuscript.progreso_contrato import nuevo_snapshot


class MigracionProgresoError(ValueError):
    """La migración explícita de progreso no puede realizarse."""


class MigracionProgresoLocal:
    def __init__(self, educativo: PerfilEducativoService):
        self.educativo = educativo

    def importar_local(self, raw_session: str | None, perfil_local: str, reemplazar: bool = False):
        nombre = sanitizar_perfil(perfil_local)
        if not nombre or nombre != perfil_local.strip().lower().replace(" ", "_"):
            raise MigracionProgresoError("El nombre del perfil local no es válido.")
        contexto = self.educativo.contexto(raw_session)
        actual = self.educativo.cargar_progreso(raw_session)
        if actual is not None and not reemplazar:
            raise MigracionProgresoError("El perfil comercial ya tiene progreso; se requiere reemplazo explícito.")
        datos = cargar_progreso(nombre)
        datos.pop("_perfil", None)
        snapshot = nuevo_snapshot(contexto.perfil.id, deepcopy(datos))
        self.educativo.guardar_progreso(raw_session, snapshot)
        return snapshot

    def listar_locales(self, raw_session: str | None) -> list[str]:
        self.educativo.contexto(raw_session)
        from tortuscript import progreso
        return progreso.obtener_perfiles()