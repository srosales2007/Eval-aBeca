"""EvalúaBeca - API REST (FastAPI).

Ejecutar:  uvicorn app.main:app --reload
Documentación interactiva:  http://127.0.0.1:8000/docs
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.integracion.motor import MotorProlog
from app.repositorio.sqlite import RepositorioSQLite
from app.servicios.gestor import GestorSolicitudes, SolicitudNoEncontrada
from app.servicios.presentador import solicitud_a_salida
from app.validacion.esquemas import (CriteriosSalida, EstadisticasSalida,
                                     SolicitudEntrada, SolicitudSalida)

WEB = Path(__file__).resolve().parents[1] / "web"
RUTA_BD = os.getenv("EVALUABECA_DB", "evaluabeca.db")

app = FastAPI(
    title="EvalúaBeca API",
    description="Motor híbrido de evaluación de solicitudes de beca (Python + Prolog).",
    version="1.0.0",
)

gestor = GestorSolicitudes(MotorProlog(), RepositorioSQLite(RUTA_BD))

# Nota: los endpoints son "async def" para que las consultas a Prolog se
# ejecuten en el hilo del bucle de eventos. El motor además usa un candado
# porque el intérprete de SWI-Prolog es único por proceso.


@app.post("/api/solicitudes", response_model=SolicitudSalida, status_code=201,
          tags=["Solicitudes"], summary="Registrar y evaluar una solicitud")
async def crear_solicitud(entrada: SolicitudEntrada):
    return solicitud_a_salida(gestor.registrar_y_evaluar(entrada))


@app.get("/api/solicitudes", response_model=list[SolicitudSalida],
         tags=["Solicitudes"], summary="Historial de solicitudes (con filtros)")
async def listar_solicitudes(
    resultado: Literal["aprobada", "rechazada"] | None = Query(None),
    tipo: Literal["total", "parcial", "ninguna"] | None = Query(None),
    buscar: str | None = Query(None, max_length=60, description="ID, nombre o carné"),
):
    return [solicitud_a_salida(s) for s in gestor.historial(resultado, tipo, buscar)]


@app.get("/api/solicitudes/{id_solicitud}", response_model=SolicitudSalida,
         tags=["Solicitudes"], summary="Consultar una solicitud")
async def obtener_solicitud(id_solicitud: str):
    try:
        return solicitud_a_salida(gestor.obtener(id_solicitud))
    except SolicitudNoEncontrada:
        raise HTTPException(404, f"No existe la solicitud {id_solicitud}")


@app.get("/api/estadisticas", response_model=EstadisticasSalida,
         tags=["Resultados"], summary="Estadísticas del historial")
async def estadisticas():
    return gestor.estadisticas()


@app.get("/api/criterios", response_model=CriteriosSalida,
         tags=["Resultados"], summary="Criterios vigentes leídos de la base de conocimiento")
async def criterios():
    return gestor.criterios()


app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.get("/", include_in_schema=False)
async def inicio():
    return FileResponse(WEB / "index.html")
