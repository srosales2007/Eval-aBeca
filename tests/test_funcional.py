"""Pruebas de las funciones puras del módulo funcional."""
from app.funcional import componer, fila_a_criterio, normalizar_condiciones


def test_componer_aplica_de_izquierda_a_derecha():
    sumar_uno_y_duplicar = componer(lambda x: x + 1, lambda x: x * 2)
    assert sumar_uno_y_duplicar(3) == 8


def test_normalizar_condiciones_limpia_y_no_muta():
    original = [" Discapacidad", "discapacidad", "", "ZONA_VULNERABLE "]
    assert normalizar_condiciones(original) == ["discapacidad", "zona_vulnerable"]
    assert original[0] == " Discapacidad"  # la lista original no cambia


def test_fila_a_criterio_convierte_respuesta_de_prolog():
    c = fila_a_criterio({"C": "promedio", "Estado": "no_cumple", "Valor": 72, "Umbral": 80})
    assert (c.criterio, c.cumple, c.valor, c.umbral) == ("promedio", False, 72.0, 80.0)
