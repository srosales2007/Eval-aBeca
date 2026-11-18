"""Paradigma funcional: funciones puras para transformar datos.

Ninguna función de este módulo modifica sus argumentos ni depende de
estado externo: reciben datos y devuelven datos nuevos. Se usan para
convertir la respuesta del motor Prolog en objetos del dominio y para
limpiar las entradas antes de enviarlas al motor.
"""
from __future__ import annotations

from functools import reduce
from typing import Any, Callable, Iterable

from app.dominio import ResultadoCriterio


def componer(*funciones: Callable) -> Callable:
    """Composición de funciones: componer(f, g, h)(x) == h(g(f(x)))."""
    return lambda valor: reduce(lambda acumulado, f: f(acumulado), funciones, valor)


def a_texto(valor: Any) -> str:
    """Prolog devuelve átomos como bytes o str según la versión de PySwip."""
    return valor.decode() if isinstance(valor, bytes) else str(valor)


def fila_a_criterio(fila: dict) -> ResultadoCriterio:
    """Convierte una solución de resultado_criterio/5 en un objeto."""
    return ResultadoCriterio(
        criterio=a_texto(fila["C"]),
        cumple=a_texto(fila["Estado"]) == "cumple",
        valor=float(fila["Valor"]),
        umbral=float(fila["Umbral"]),
    )


def filas_a_criterios(filas: Iterable[dict]) -> list[ResultadoCriterio]:
    return list(map(fila_a_criterio, filas))


def atomos(filas: Iterable[dict], variable: str) -> list[str]:
    """Extrae los valores de una variable de todas las soluciones, sin repetir."""
    return list(dict.fromkeys(map(lambda f: a_texto(f[variable]), filas)))


normalizar_condiciones: Callable[[Iterable[str]], list[str]] = componer(
    lambda conds: map(str.strip, conds),
    lambda conds: map(str.lower, conds),
    lambda conds: filter(None, conds),
    lambda conds: sorted(set(conds)),
)
"""Limpia la lista de condiciones: sin espacios, minúsculas, sin vacíos ni duplicados."""
