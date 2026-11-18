"""Pruebas del procesamiento funcional del historial."""
from app.dominio import (Dictamen, Estudiante, ResultadoCriterio, ResultadoDictamen,
                         Solicitud, TipoBeca)
from app.funcional.estadisticas import calcular_estadisticas, filtrar_historial


def solicitud(id_, nombre, promedio, resultado, tipo, incumple=()):
    criterios = [ResultadoCriterio(c, c not in incumple, 0, 0)
                 for c in ("promedio", "ingreso", "carga_academica")]
    s = Solicitud(id_, Estudiante("FI-" + id_, nombre, "Software"), promedio, 1, 1, 4)
    s.registrar_dictamen(Dictamen(ResultadoDictamen(resultado), TipoBeca(tipo), criterios))
    return s


HISTORIAL = [
    solicitud("1", "Ana", 90, "aprobada", "total"),
    solicitud("2", "Luis", 85, "aprobada", "parcial"),
    solicitud("3", "José", 70, "rechazada", "ninguna", incumple=("promedio", "ingreso")),
    solicitud("4", "Eva", 75, "rechazada", "ninguna", incumple=("promedio",)),
]


def test_estadisticas_con_reduce():
    e = calcular_estadisticas(HISTORIAL)
    assert (e["total"], e["aprobadas"], e["rechazadas"]) == (4, 2, 2)
    assert e["tasa_aprobacion"] == 50.0
    assert e["promedio_general"] == 80.0
    assert e["por_tipo"] == {"total": 1, "parcial": 1}
    assert list(e["criterios_incumplidos"]) == ["promedio", "ingreso"]


def test_estadisticas_de_historial_vacio():
    assert calcular_estadisticas([])["tasa_aprobacion"] == 0.0


def test_filtros_combinados():
    assert [s.id for s in filtrar_historial(HISTORIAL, resultado="rechazada")] == ["3", "4"]
    assert [s.id for s in filtrar_historial(HISTORIAL, tipo="total")] == ["1"]
    assert [s.id for s in filtrar_historial(HISTORIAL, resultado="aprobada", texto="lu")] == ["2"]


def test_las_funciones_no_modifican_el_historial():
    copia = list(HISTORIAL)
    filtrar_historial(HISTORIAL, resultado="aprobada")
    calcular_estadisticas(HISTORIAL)
    assert HISTORIAL == copia
