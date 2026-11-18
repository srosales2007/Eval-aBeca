"""Convierte objetos del dominio en esquemas de respuesta de la API."""
from __future__ import annotations

from app.dominio import Dictamen, Solicitud
from app.validacion.esquemas import CriterioSalida, DictamenSalida, SolicitudSalida


def dictamen_a_salida(d: Dictamen) -> DictamenSalida:
    return DictamenSalida(
        resultado=d.resultado.value,
        tipo_beca=d.tipo_beca.value,
        resumen=d.resumen(),
        periodo=d.periodo,
        criterios=[CriterioSalida(criterio=c.criterio, etiqueta=c.etiqueta, cumple=c.cumple,
                                  valor=c.valor, umbral=c.umbral, explicacion=c.explicacion())
                   for c in d.criterios],
        motivos_tipo=d.motivos_tipo,
        condiciones_aplicadas=d.condiciones_aplicadas,
    )


def solicitud_a_salida(s: Solicitud) -> SolicitudSalida:
    return SolicitudSalida(
        id=s.id, carne=s.estudiante.carne, nombre=s.estudiante.nombre,
        carrera=s.estudiante.carrera, promedio=s.promedio, ingreso_hogar=s.ingreso_hogar,
        miembros_hogar=s.miembros_hogar, materias=s.materias, condiciones=s.condiciones,
        fecha=s.fecha, estado=s.estado.value,
        dictamen=dictamen_a_salida(s.dictamen) if s.dictamen else None,
    )
