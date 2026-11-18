"""Pruebas de la API (FastAPI) y del módulo de validación."""
from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)

VALIDA = dict(carne="FI-2026-0145", nombre="Ana Mora Solís", carrera="Desarrollo de Software",
              promedio=88, ingreso_hogar=300000, miembros_hogar=3, materias=5, condiciones=[])


def test_crear_solicitud_devuelve_dictamen():
    r = cliente.post("/api/solicitudes", json=VALIDA)
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["estado"] == "evaluada"
    assert cuerpo["dictamen"]["resultado"] == "aprobada"
    assert len(cuerpo["dictamen"]["criterios"]) == 3


def test_validacion_rechaza_datos_fuera_de_rango():
    r = cliente.post("/api/solicitudes", json={**VALIDA, "promedio": 120, "materias": 0})
    assert r.status_code == 422
    campos = {e["loc"][-1] for e in r.json()["detail"]}
    assert {"promedio", "materias"} <= campos


def test_validacion_rechaza_condicion_desconocida():
    r = cliente.post("/api/solicitudes", json={**VALIDA, "condiciones": ["vip"]})
    assert r.status_code == 422


def test_historial_y_consulta_por_id():
    creada = cliente.post("/api/solicitudes", json=VALIDA).json()
    assert any(s["id"] == creada["id"] for s in cliente.get("/api/solicitudes").json())
    assert cliente.get(f"/api/solicitudes/{creada['id']}").status_code == 200
    assert cliente.get("/api/solicitudes/NO-EXISTE").status_code == 404
