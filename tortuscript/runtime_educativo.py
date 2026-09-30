"""Fachada de runtime educativo para el modo autenticado.

Esta capa decide qué almacenamiento usa el runtime sin modificar el runtime local
existente. En modo autenticado, la identidad del progreso es siempre el ChildProfile
activo resuelto por PerfilEducativoService.
"""
from __future__ import annotations

from dataclasses import dataclass

from .perfil_educativo import ContextoEducativo, ContextoEducativoError, PerfilEducativoService
from .progreso_contrato import ProgresoSnapshot


@dataclass(frozen=True)
class RuntimeEducativo:
    service: PerfilEducativoService

    def contexto(self, raw_session: str | None) -> ContextoEducativo:
        return self.service.contexto(raw_session)

    def cargar(self, raw_session: str | None) -> ProgresoSnapshot | None:
        return self.service.cargar_progreso(raw_session)

    def guardar(self, raw_session: str | None, snapshot: ProgresoSnapshot) -> None:
        self.service.guardar_progreso(raw_session, snapshot)

    def exigir_producto(self, raw_session: str | None, producto: str) -> None:
        self.service.exigir_acceso(raw_session, producto)

    def snapshot_publico(self, raw_session: str | None) -> dict:
        contexto = self.contexto(raw_session)
        snapshot = self.cargar(raw_session)
        return {
            "perfil": {
                "id": contexto.perfil.id,
                "nombre": contexto.perfil.display_name,
            },
            "progreso": None if snapshot is None else {
                "contract_version": snapshot.schema_version,
                "profile_id": snapshot.profile_id,
                "updated_at": snapshot.updated_at,
                "data": snapshot.data,
            },
        }
