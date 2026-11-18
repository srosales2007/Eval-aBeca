"""Repositorio de solicitudes: contrato y versión en memoria."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.dominio import Solicitud


class RepositorioSolicitudes(ABC):
    @abstractmethod
    def guardar(self, solicitud: Solicitud) -> None: ...

    @abstractmethod
    def obtener(self, id_solicitud: str) -> Solicitud | None: ...

    @abstractmethod
    def listar(self) -> list[Solicitud]: ...

    @abstractmethod
    def siguiente_id(self) -> str: ...


class RepositorioMemoria(RepositorioSolicitudes):
    """Guarda las solicitudes en un diccionario (útil para pruebas)."""

    def __init__(self) -> None:
        self._datos: dict[str, Solicitud] = {}

    def guardar(self, solicitud: Solicitud) -> None:
        self._datos[solicitud.id] = solicitud

    def obtener(self, id_solicitud: str) -> Solicitud | None:
        return self._datos.get(id_solicitud)

    def listar(self) -> list[Solicitud]:
        return sorted(self._datos.values(), key=lambda s: s.fecha, reverse=True)

    def siguiente_id(self) -> str:
        return f"SOL-{len(self._datos) + 1:04d}"
