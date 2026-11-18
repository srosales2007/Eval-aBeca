"""Módulo de gestión de solicitudes (capa de negocio, POO).

GestorSolicitudes coordina el flujo completo: crea los objetos del
dominio a partir de la entrada validada, pide la evaluación al motor de
reglas y guarda el resultado en el repositorio. No conoce Prolog ni la
base de datos: depende solo de las abstracciones MotorReglas y
RepositorioSolicitudes (inyección de dependencias).
"""
from __future__ import annotations

from app.dominio import Estudiante, Solicitud
from app.funcional.estadisticas import calcular_estadisticas, filtrar_historial
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

    def historial(self, resultado: str | None = None, tipo: str | None = None,
                  texto: str | None = None) -> list[Solicitud]:
        return filtrar_historial(self._repositorio.listar(), resultado, tipo, texto)

    def estadisticas(self) -> dict:
        return calcular_estadisticas(self._repositorio.listar())

    def criterios(self) -> dict:
        return self._motor.criterios_vigentes()
