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
    def ejecutar(self, raw_session: str | None, operacion) -> object:
        """Carga, ejecuta una operación educativa sobre el progreso autenticado y persiste."""
        contexto = self.contexto(raw_session)
        snapshot = self.cargar(raw_session)
        from copy import deepcopy
        from tortuscript import progreso as legado
        data = deepcopy(snapshot.data if snapshot is not None else legado.PROGRESO_INICIAL)
        data["_perfil"] = contexto.perfil.id
        resultado = operacion(data)
        payload = {k: deepcopy(v) for k, v in data.items() if not k.startswith("_")}
        self.guardar(raw_session, ProgresoSnapshot(
            profile_id=contexto.perfil.id,
            schema_version=1,
            updated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            data=payload,
        ))
        return resultado

    def registrar_ejercicio(self, raw_session: str | None, indice: int, estrellas: int, xp_ganado: int) -> bool:
        from tortuscript import progreso as legado
        return self.ejecutar(raw_session, lambda p: legado.registrar_ejercicio(p, indice, estrellas, xp_ganado))

    def registrar_paso_leccion(self, raw_session: str | None, leccion_id: str, indice: int, xp: int,
                               perfecto: bool, total_pasos: int, estrellas=None) -> dict:
        from tortuscript import progreso as legado
        return self.ejecutar(raw_session, lambda p: legado.registrar_paso_leccion(
            p, leccion_id, indice, xp, perfecto, total_pasos, estrellas))

    def registrar_practica(self, raw_session: str | None, leccion_id: str, paso: int, acierto: bool) -> int:
        from tortuscript import progreso as legado
        return self.ejecutar(raw_session, lambda p: legado.registrar_practica(p, leccion_id, paso, acierto))

    def guardar_proyecto(self, raw_session: str | None, nombre: str, tipo: str, codigo: str, proyecto_id=None) -> str:
        from tortuscript import proyectos
        return self.ejecutar(raw_session, lambda p: proyectos.guardar(
            p, nombre, tipo, codigo, proyecto_id=proyecto_id))

    def listar_proyectos(self, raw_session: str | None) -> list[dict]:
        from tortuscript import proyectos
        snapshot = self.cargar(raw_session)
        return [] if snapshot is None else proyectos.listar(snapshot.data)

