"""Modelo de dominio de EvalúaBeca (paradigma orientado a objetos).

Clases que representan las entidades del problema: el estudiante,
su solicitud y el dictamen que devuelve el motor de reglas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EstadoSolicitud(str, Enum):
    REGISTRADA = "registrada"
    EVALUADA = "evaluada"


class ResultadoDictamen(str, Enum):
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"


class TipoBeca(str, Enum):
    TOTAL = "total"
    PARCIAL = "parcial"
    NINGUNA = "ninguna"


@dataclass
class Estudiante:
    carne: str
    nombre: str
    carrera: str

    def __str__(self) -> str:
        return f"{self.nombre} ({self.carne})"


@dataclass
class ResultadoCriterio:
    """Resultado de un criterio individual, tal como lo dedujo Prolog."""

    criterio: str
    cumple: bool
    valor: float
    umbral: float

    ETIQUETAS = {
        "promedio": "Promedio académico",
        "ingreso": "Ingreso per cápita del hogar",
        "carga_academica": "Carga académica (materias)",
    }

    @property
    def etiqueta(self) -> str:
        return self.ETIQUETAS.get(self.criterio, self.criterio)

    def explicacion(self) -> str:
        if self.criterio == "ingreso":
            comparacion = "≤" if self.cumple else ">"
            return (f"{self.etiqueta}: ₡{self.valor:,.0f} {comparacion} "
                    f"máximo ₡{self.umbral:,.0f}")
        comparacion = "≥" if self.cumple else "<"
        return (f"{self.etiqueta}: {self.valor:g} {comparacion} "
                f"mínimo {self.umbral:g}")


@dataclass
class Dictamen:
    resultado: ResultadoDictamen
    tipo_beca: TipoBeca
    criterios: list[ResultadoCriterio]
    motivos_tipo: list[str] = field(default_factory=list)
    condiciones_aplicadas: list[str] = field(default_factory=list)
    periodo: str = ""

    @property
    def aprobada(self) -> bool:
        return self.resultado is ResultadoDictamen.APROBADA

    def criterios_incumplidos(self) -> list[ResultadoCriterio]:
        return [c for c in self.criterios if not c.cumple]

    def resumen(self) -> str:
        if self.aprobada:
            return f"Solicitud aprobada: beca {self.tipo_beca.value}."
        faltantes = ", ".join(c.etiqueta.lower() for c in self.criterios_incumplidos())
        return f"Solicitud rechazada. No cumple: {faltantes}."


@dataclass
class Solicitud:
    id: str
    estudiante: Estudiante
    promedio: float
    ingreso_hogar: float
    miembros_hogar: int
    materias: int
    condiciones: list[str] = field(default_factory=list)
    fecha: datetime = field(default_factory=datetime.now)
    estado: EstadoSolicitud = EstadoSolicitud.REGISTRADA
    dictamen: Dictamen | None = None

    def ingreso_per_capita(self) -> float:
        return self.ingreso_hogar / self.miembros_hogar

    def registrar_dictamen(self, dictamen: Dictamen) -> None:
        self.dictamen = dictamen
        self.estado = EstadoSolicitud.EVALUADA
