"""Paradigma funcional: filtros del historial y estadísticas.

El historial se procesa con funciones puras: los filtros se construyen
como predicados que se combinan entre sí, y las estadísticas se obtienen
con map, filter y reduce sin modificar la lista original.
"""
from __future__ import annotations

from collections import Counter
from functools import reduce
from typing import Callable, Iterable

from app.dominio import Solicitud

Predicado = Callable[[Solicitud], bool]


# ---- filtros (funciones de orden superior) -------------------------------------
def por_resultado(resultado: str | None) -> Predicado:
    return lambda s: resultado is None or s.dictamen.resultado.value == resultado


def por_tipo(tipo: str | None) -> Predicado:
    return lambda s: tipo is None or s.dictamen.tipo_beca.value == tipo


def por_texto(texto: str | None) -> Predicado:
    buscado = (texto or "").strip().lower()
    return lambda s: not buscado or buscado in f"{s.id} {s.estudiante.nombre} {s.estudiante.carne}".lower()


def todos(*predicados: Predicado) -> Predicado:
    """Combina varios predicados: la solicitud debe cumplirlos todos."""
    return lambda s: all(p(s) for p in predicados)


def filtrar_historial(solicitudes: Iterable[Solicitud], resultado: str | None = None,
                      tipo: str | None = None, texto: str | None = None) -> list[Solicitud]:
    evaluadas = filter(lambda s: s.dictamen is not None, solicitudes)
    return list(filter(todos(por_resultado(resultado), por_tipo(tipo), por_texto(texto)), evaluadas))


# ---- estadísticas (map / filter / reduce) ------------------------------------
def _acumular(acumulado: dict, s: Solicitud) -> dict:
    """Función reductora: devuelve un diccionario NUEVO en cada paso."""
    incumplidos = [c.criterio for c in s.dictamen.criterios_incumplidos()]
    return {
        "total": acumulado["total"] + 1,
        "suma_promedios": acumulado["suma_promedios"] + s.promedio,
        "resultados": acumulado["resultados"] + Counter([s.dictamen.resultado.value]),
        "tipos": acumulado["tipos"] + Counter([s.dictamen.tipo_beca.value]),
        "incumplidos": acumulado["incumplidos"] + Counter(incumplidos),
        "carreras": acumulado["carreras"] + Counter([s.estudiante.carrera]),
    }


INICIAL = {"total": 0, "suma_promedios": 0.0, "resultados": Counter(), "tipos": Counter(),
           "incumplidos": Counter(), "carreras": Counter()}


def calcular_estadisticas(solicitudes: Iterable[Solicitud]) -> dict:
    evaluadas = list(filter(lambda s: s.dictamen is not None, solicitudes))
    a = reduce(_acumular, evaluadas, INICIAL)
    total = a["total"]
    aprobadas = a["resultados"]["aprobada"]
    return {
        "total": total,
        "aprobadas": aprobadas,
        "rechazadas": a["resultados"]["rechazada"],
        "tasa_aprobacion": round(aprobadas / total * 100, 1) if total else 0.0,
        "promedio_general": round(a["suma_promedios"] / total, 2) if total else 0.0,
        "por_tipo": {t: a["tipos"][t] for t in ("total", "parcial")},
        "criterios_incumplidos": dict(a["incumplidos"].most_common()),
        "por_carrera": dict(a["carreras"].most_common()),
    }
