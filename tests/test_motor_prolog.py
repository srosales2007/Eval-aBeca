"""Pruebas del motor de reglas en Prolog a través del módulo de integración."""
import pytest

from app.dominio import Estudiante, Solicitud
from app.integracion.motor import MotorProlog


@pytest.fixture(scope="module")
def motor():
    return MotorProlog()


def nueva(promedio, ingreso, miembros, materias, condiciones=()):
    return Solicitud("SOL-T", Estudiante("FI-0001", "Prueba", "Software"),
                     promedio, ingreso, miembros, materias, list(condiciones))


def test_aprobada_beca_total_por_ingreso_prioritario(motor):
    d = motor.evaluar(nueva(88, 300_000, 3, 5))
    assert d.resultado.value == "aprobada"
    assert d.tipo_beca.value == "total"
    assert "ingreso_prioritario" in d.motivos_tipo


def test_aprobada_beca_parcial(motor):
    d = motor.evaluar(nueva(85, 600_000, 3, 4))
    assert (d.resultado.value, d.tipo_beca.value) == ("aprobada", "parcial")


def test_condicion_especial_baja_el_promedio_requerido(motor):
    sin_condicion = motor.evaluar(nueva(77, 700_000, 4, 4))
    con_condicion = motor.evaluar(nueva(77, 700_000, 4, 4, ["jefe_de_hogar"]))
    assert sin_condicion.resultado.value == "rechazada"
    assert con_condicion.resultado.value == "aprobada"
    assert con_condicion.condiciones_aplicadas == ["jefe_de_hogar"]


def test_rechazada_explica_cada_criterio_incumplido(motor):
    d = motor.evaluar(nueva(72, 900_000, 3, 2))
    assert d.resultado.value == "rechazada"
    incumplidos = {c.criterio for c in d.criterios_incumplidos()}
    assert incumplidos == {"promedio", "ingreso", "carga_academica"}


def test_valores_limite_cumplen(motor):
    # Promedio exactamente 80, ingreso per cápita exactamente 250 000 y 3 materias
    d = motor.evaluar(nueva(80, 750_000, 3, 3))
    assert all(c.cumple for c in d.criterios)


def test_no_quedan_hechos_despues_de_evaluar(motor):
    motor.evaluar(nueva(90, 100_000, 2, 5))
    assert list(motor._prolog.query("promedio(_, _)")) == []
