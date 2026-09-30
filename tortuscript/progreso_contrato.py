"""Contrato de persistencia de progreso por ChildProfile.

Este módulo define la frontera futura entre identidad comercial y progreso
educativo. No cambia el almacenamiento local existente (progreso_<perfil>.json)
ni realiza una migración automática.

La unidad de identidad del progreso futuro es ChildProfile.id, no el nombre
visible del alumno ni Account.email.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


PROGRESS_CONTRACT_VERSION = 1


class ProgresoContratoError(ValueError):
    """Error de validación del contrato de progreso."""


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _validar_profile_id(profile_id: str) -> str:
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise ProgresoContratoError("profile_id es obligatorio.")
    return profile_id.strip()


@dataclass(frozen=True)
class ProgresoSnapshot:
    """Snapshot portable; no conoce SQLite, Flask ni el formato local actual."""

    profile_id: str
    schema_version: int
    updated_at: str
    data: dict[str, Any]

    def validar(self) -> "ProgresoSnapshot":
        _validar_profile_id(self.profile_id)
        if self.schema_version != PROGRESS_CONTRACT_VERSION:
            raise ProgresoContratoError("Versión de contrato de progreso no compatible.")
        if not isinstance(self.data, dict):
            raise ProgresoContratoError("data debe ser un objeto JSON.")
        return self


class ProgresoStore(Protocol):
    """Backend futuro de progreso; la implementación puede ser local o remota."""

    def cargar(self, profile_id: str) -> ProgresoSnapshot | None:
        ...

    def guardar(self, snapshot: ProgresoSnapshot) -> None:
        ...


class MemoriaProgresoStore:
    """Adaptador mínimo para pruebas del contrato, no para producción."""

    def __init__(self):
        self._items: dict[str, ProgresoSnapshot] = {}

    def cargar(self, profile_id: str) -> ProgresoSnapshot | None:
        profile_id = _validar_profile_id(profile_id)
        snapshot = self._items.get(profile_id)
        return deepcopy(snapshot) if snapshot else None

    def guardar(self, snapshot: ProgresoSnapshot) -> None:
        snapshot.validar()
        self._items[snapshot.profile_id] = deepcopy(snapshot)


def nuevo_snapshot(profile_id: str, data: dict[str, Any]) -> ProgresoSnapshot:
    profile_id = _validar_profile_id(profile_id)
    if not isinstance(data, dict):
        raise ProgresoContratoError("data debe ser un objeto JSON.")
    return ProgresoSnapshot(
        profile_id=profile_id,
        schema_version=PROGRESS_CONTRACT_VERSION,
        updated_at=_ahora(),
        data=deepcopy(data),
    ).validar()


def exportar_snapshot(profile_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Genera el documento de frontera sin mutar el progreso original."""
    snapshot = nuevo_snapshot(profile_id, data)
    return {
        "contract_version": PROGRESS_CONTRACT_VERSION,
        "profile_id": snapshot.profile_id,
        "updated_at": snapshot.updated_at,
        "data": deepcopy(snapshot.data),
    }


def importar_snapshot(documento: dict[str, Any]) -> ProgresoSnapshot:
    """Valida un documento recibido antes de entregarlo a otra capa."""
    if not isinstance(documento, dict):
        raise ProgresoContratoError("El documento de progreso no es válido.")
    if documento.get("contract_version") != PROGRESS_CONTRACT_VERSION:
        raise ProgresoContratoError("Versión de contrato de progreso no compatible.")
    return ProgresoSnapshot(
        profile_id=_validar_profile_id(documento.get("profile_id")),
        schema_version=PROGRESS_CONTRACT_VERSION,
        updated_at=str(documento.get("updated_at") or ""),
        data=deepcopy(documento.get("data")),
    ).validar()
