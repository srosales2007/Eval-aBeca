"""Módulo de integración: puente entre Python (POO) y Prolog (lógico).

MotorReglas define el contrato que cualquier motor de evaluación debe
cumplir. MotorProlog lo implementa con PySwip: traduce cada Solicitud
a hechos de Prolog, consulta las reglas y convierte las respuestas en
un objeto Dictamen.
"""
from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from pathlib import Path

from pyswip import Prolog

from app.dominio import Dictamen, ResultadoDictamen, Solicitud, TipoBeca
from app.funcional import a_texto, atomos, filas_a_criterios

RUTA_REGLAS = Path(__file__).resolve().parents[2] / "prolog" / "reglas.pl"


class MotorReglas(ABC):
    """Contrato del motor de evaluación (abstracción)."""

    @abstractmethod
    def evaluar(self, solicitud: Solicitud) -> Dictamen: ...

    @abstractmethod
    def criterios_vigentes(self) -> dict: ...


class MotorProlog(MotorReglas):
    """Implementación del motor usando SWI-Prolog mediante PySwip."""

    def __init__(self, ruta_reglas: Path = RUTA_REGLAS) -> None:
        self._prolog = Prolog()
        self._prolog.consult(ruta_reglas.as_posix())
        # El intérprete de SWI-Prolog es único por proceso: se serializan
        # las consultas para que dos solicitudes no mezclen sus hechos.
        self._candado = threading.Lock()

    # -- traducción Python -> Prolog -------------------------------------
    @staticmethod
    def _atomo(texto: str) -> str:
        return "'" + texto.replace("\\", "\\\\").replace("'", "\\'") + "'"

    def _hechos(self, s: Solicitud) -> str:
        condiciones = ",".join(self._atomo(c) for c in s.condiciones)
        return (f"registrar_solicitud({self._atomo(s.id)}, {s.promedio}, "
                f"{s.ingreso_hogar}, {s.miembros_hogar}, {s.materias}, "
                f"[{condiciones}])")

    def _consultar(self, consulta: str) -> list[dict]:
        return list(self._prolog.query(consulta))

    # -- evaluación ----------------------------------------------------------
    def evaluar(self, solicitud: Solicitud) -> Dictamen:
        sid = self._atomo(solicitud.id)
        with self._candado:
            self._consultar(self._hechos(solicitud))
            try:
                dictamen = self._consultar(f"dictamen({sid}, D, T)")[0]
                criterios = self._consultar(f"resultado_criterio({sid}, C, Estado, Valor, Umbral)")
                motivos = self._consultar(f"motivo_tipo({sid}, M)")
                condiciones = self._consultar(f"condicion_aplicada({sid}, Co)")
                periodo = self._consultar("periodo_vigente(P)")
            finally:
                self._consultar(f"limpiar_solicitud({sid})")

        return Dictamen(
            resultado=ResultadoDictamen(atomos([dictamen], "D")[0]),
            tipo_beca=TipoBeca(atomos([dictamen], "T")[0]),
            criterios=filas_a_criterios(criterios),
            motivos_tipo=atomos(motivos, "M"),
            condiciones_aplicadas=atomos(condiciones, "Co"),
            periodo=atomos(periodo, "P")[0],
        )

    def criterios_vigentes(self) -> dict:
        """Lee del archivo criterios.pl los umbrales y condiciones vigentes."""
        with self._candado:
            umbrales = self._consultar("umbral(N, V)")
            condiciones = self._consultar("condicion_especial(C)")
            periodo = self._consultar("periodo_vigente(P)")
        return {
            "periodo": atomos(periodo, "P")[0],
            "umbrales": {a_texto(f["N"]): f["V"] for f in umbrales},
            "condiciones_especiales": atomos(condiciones, "C"),
        }
