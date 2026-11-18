"""EvalúaBeca - API REST (FastAPI).

Ejecutar:  uvicorn app.main:app --reload
Documentación interactiva:  http://127.0.0.1:8000/docs
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.integracion.motor import MotorProlog
from app.repositorio.base import RepositorioMemoria
from app.servicios.gestor import GestorSolicitudes, SolicitudNoEncontrada
from app.servicios.presentador import solicitud_a_salida
from app.validacion.esquemas import SolicitudEntrada, SolicitudSalida

WEB = Path(__file__).resolve().parents[1] / "web"

app = FastAPI(
    title="EvalúaBeca API",
    description="Motor híbrido de evaluación de solicitudes de beca (Python + Prolog).",
    version="0.2.0",
)

gestor = GestorSolicitudes(MotorProlog(), RepositorioMemoria())

# Nota: los endpoints son "async def" para que todas las consultas a
# Prolog ocurran en el hilo del bucle de eventos, el mismo hilo donde se
# inicializó el intérprete (PySwip no admite llamadas desde otros hilos).


@app.post("/api/solicitudes", response_model=SolicitudSalida, status_code=201,
          tags=["Solicitudes"], summary="Registrar y evaluar una solicitud")
async def crear_solicitud(entrada: SolicitudEntrada):
    return solicitud_a_salida(gestor.registrar_y_evaluar(entrada))


@app.get("/api/solicitudes", response_model=list[SolicitudSalida],
         tags=["Solicitudes"], summary="Historial de solicitudes evaluadas")
async def listar_solicitudes():
    return [solicitud_a_salida(s) for s in gestor.historial()]


@app.get("/api/solicitudes/{id_solicitud}", response_model=SolicitudSalida,
         tags=["Solicitudes"], summary="Consultar una solicitud")
async def obtener_solicitud(id_solicitud: str):
    try:
        return solicitud_a_salida(gestor.obtener(id_solicitud))
    except SolicitudNoEncontrada:
        raise HTTPException(404, f"No existe la solicitud {id_solicitud}")


app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.get("/", include_in_schema=False)
async def inicio():
    return FileResponse(WEB / "index.html")
