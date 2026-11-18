"""Módulo de gestión de solicitudes (capa de negocio, POO).

GestorSolicitudes coordina el flujo completo: crea los objetos del
dominio a partir de la entrada validada, pide la evaluación al motor de
reglas y guarda el resultado en el repositorio. No conoce Prolog ni la
base de datos: depende solo de las abstracciones MotorReglas y
RepositorioSolicitudes (inyección de dependencias).
"""
from __future__ import annotations

from app.dominio import Estudiante, Solicitud
from app.integracion.motor import MotorReglas
from app.repositorio.base import RepositorioSolicitudes
from app.validacion.esquemas import SolicitudEntrada


class SolicitudNoEncontrada(Exception):
    pass


class GestorSolicitudes:
    def __init__(self, motor: MotorReglas, repositorio: RepositorioSolicitudes) -> None:
        self._motor = motor
        self._repositorio = repositorio

    def registrar_y_evaluar(self, entrada: SolicitudEntrada) -> Solicitud:
        estudiante = Estudiante(entrada.carne, entrada.nombre, entrada.carrera)
        solicitud = Solicitud(
            id=self._repositorio.siguiente_id(),
            estudiante=estudiante,
            promedio=entrada.promedio,
            ingreso_hogar=entrada.ingreso_hogar,
            miembros_hogar=entrada.miembros_hogar,
            materias=entrada.materias,
            condiciones=[c.value for c in entrada.condiciones],
        )
        solicitud.registrar_dictamen(self._motor.evaluar(solicitud))
        self._repositorio.guardar(solicitud)
        return solicitud

    def obtener(self, id_solicitud: str) -> Solicitud:
        solicitud = self._repositorio.obtener(id_solicitud)
        if solicitud is None:
            raise SolicitudNoEncontrada(id_solicitud)
        return solicitud

    def historial(self) -> list[Solicitud]:
        return self._repositorio.listar()
