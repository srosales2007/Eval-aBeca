"""Módulo de validación de entradas (FastAPI + Pydantic).

Los esquemas declaran las restricciones de dominio de cada campo; FastAPI
los aplica antes de que la solicitud llegue al motor de reglas y responde
con HTTP 422 si algún dato es inválido.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from app.funcional import normalizar_condiciones


class CondicionEspecial(str, Enum):
    DISCAPACIDAD = "discapacidad"
    JEFE_DE_HOGAR = "jefe_de_hogar"
    ZONA_VULNERABLE = "zona_vulnerable"
    PRIMERA_GENERACION = "primera_generacion"


class SolicitudEntrada(BaseModel):
    carne: str = Field(..., pattern=r"^[A-Za-z0-9-]{4,15}$", examples=["FI-2026-0145"])
    nombre: str = Field(..., min_length=3, max_length=80, examples=["Ana Mora Solís"])
    carrera: str = Field(..., min_length=3, max_length=80, examples=["Desarrollo de Software"])
    promedio: float = Field(..., ge=0, le=100, description="Promedio ponderado (0-100)")
    ingreso_hogar: float = Field(..., ge=0, le=50_000_000, description="Ingreso mensual del hogar en colones")
    miembros_hogar: int = Field(..., ge=1, le=20)
    materias: int = Field(..., ge=1, le=8, description="Materias matriculadas en el periodo")
    condiciones: list[CondicionEspecial] = Field(default_factory=list)

    @field_validator("nombre", "carrera")
    @classmethod
    def sin_espacios_extra(cls, valor: str) -> str:
        limpio = " ".join(valor.split())
        if len(limpio) < 3:
            raise ValueError("debe tener al menos 3 caracteres")
        return limpio

    @field_validator("condiciones", mode="before")
    @classmethod
    def limpiar_condiciones(cls, valor):
        return normalizar_condiciones(valor) if isinstance(valor, list) else valor

    @model_validator(mode="after")
    def coherencia(self) -> "SolicitudEntrada":
        if self.ingreso_hogar > 0 and self.ingreso_hogar < self.miembros_hogar:
            raise ValueError("el ingreso del hogar no es coherente con la cantidad de miembros")
        return self


class CriterioSalida(BaseModel):
    criterio: str
    etiqueta: str
    cumple: bool
    valor: float
    umbral: float
    explicacion: str


class DictamenSalida(BaseModel):
    resultado: str
    tipo_beca: str
    resumen: str
    periodo: str
    criterios: list[CriterioSalida]
    motivos_tipo: list[str]
    condiciones_aplicadas: list[str]


class SolicitudSalida(BaseModel):
    id: str
    carne: str
    nombre: str
    carrera: str
    promedio: float
    ingreso_hogar: float
    miembros_hogar: int
    materias: int
    condiciones: list[str]
    fecha: datetime
    estado: str
    dictamen: DictamenSalida | None
