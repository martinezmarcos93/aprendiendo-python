"""Adaptador de runtime: permite reutilizar el motor de progreso existente con ChildProfile.

No cambia la implementación educativa de progreso.py. Traduce entre el snapshot comercial
y el diccionario que ya consume el núcleo educativo.
"""
from __future__ import annotations

import copy

from tortuscript.progreso import PROGRESO_INICIAL, _migrar
from tortuscript.progreso_contrato import nuevo_snapshot
from tortuscript.perfil_educativo import PerfilEducativoService, ContextoEducativoError


class RuntimeEducativoChildProfile:
    def __init__(self, educativo: PerfilEducativoService):
        self.educativo = educativo

    def cargar(self, raw_session: str | None) -> dict:
        contexto = self.educativo.contexto(raw_session)
        snapshot = self.educativo.cargar_progreso(raw_session)
        if snapshot is None:
            data = copy.deepcopy(PROGRESO_INICIAL)
        else:
            data = copy.deepcopy(snapshot.data)
        data = _migrar(data)
        # Las funciones heredadas necesitan un propietario interno para impedir que
        # una escritura pueda terminar en otro perfil.
        data["_perfil"] = contexto.perfil.id
        return data

    def guardar(self, raw_session: str | None, data: dict) -> None:
        contexto = self.educativo.contexto(raw_session)
        propietario = data.get("_perfil")
        if propietario != contexto.perfil.id:
            raise ContextoEducativoError("El progreso no pertenece al perfil activo.")
        payload = {k: copy.deepcopy(v) for k, v in data.items() if not k.startswith("_")}
        snapshot = nuevo_snapshot(contexto.perfil.id, payload)
        self.educativo.guardar_progreso(raw_session, snapshot)

    def modificar(self, raw_session: str | None, funcion):
        data = self.cargar(raw_session)
        resultado = funcion(data)
        self.guardar(raw_session, data)
        return resultado