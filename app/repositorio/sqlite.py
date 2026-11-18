"""Repositorio persistente en SQLite (historial de solicitudes).

Implementa el mismo contrato que RepositorioMemoria, por lo que el
GestorSolicitudes funciona igual con cualquiera de los dos
(polimorfismo). El dictamen se guarda serializado en JSON.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import asdict
from datetime import datetime

from app.dominio import (Dictamen, EstadoSolicitud, Estudiante, ResultadoCriterio,
                         ResultadoDictamen, Solicitud, TipoBeca)
from app.repositorio.base import RepositorioSolicitudes

ESQUEMA = """
CREATE TABLE IF NOT EXISTS solicitudes (
    id              TEXT PRIMARY KEY,
    carne           TEXT NOT NULL,
    nombre          TEXT NOT NULL,
    carrera         TEXT NOT NULL,
    promedio        REAL NOT NULL,
    ingreso_hogar   REAL NOT NULL,
    miembros_hogar  INTEGER NOT NULL,
    materias        INTEGER NOT NULL,
    condiciones     TEXT NOT NULL,
    fecha           TEXT NOT NULL,
    estado          TEXT NOT NULL,
    dictamen        TEXT
)"""


class RepositorioSQLite(RepositorioSolicitudes):
    def __init__(self, ruta: str = "evaluabeca.db") -> None:
        self._conexion = sqlite3.connect(ruta, check_same_thread=False)
        self._conexion.row_factory = sqlite3.Row
        self._candado = threading.Lock()
        with self._conexion:
            self._conexion.execute(ESQUEMA)

    # -- serialización ---------------------------------------------------------
    @staticmethod
    def _dictamen_a_json(d: Dictamen | None) -> str | None:
        if d is None:
            return None
        datos = asdict(d)
        datos["resultado"] = d.resultado.value
        datos["tipo_beca"] = d.tipo_beca.value
        return json.dumps(datos, ensure_ascii=False)

    @staticmethod
    def _json_a_dictamen(texto: str | None) -> Dictamen | None:
        if not texto:
            return None
        datos = json.loads(texto)
        return Dictamen(
            resultado=ResultadoDictamen(datos["resultado"]),
            tipo_beca=TipoBeca(datos["tipo_beca"]),
            criterios=[ResultadoCriterio(**c) for c in datos["criterios"]],
            motivos_tipo=datos["motivos_tipo"],
            condiciones_aplicadas=datos["condiciones_aplicadas"],
            periodo=datos["periodo"],
        )

    def _fila_a_solicitud(self, fila: sqlite3.Row) -> Solicitud:
        return Solicitud(
            id=fila["id"],
            estudiante=Estudiante(fila["carne"], fila["nombre"], fila["carrera"]),
            promedio=fila["promedio"],
            ingreso_hogar=fila["ingreso_hogar"],
            miembros_hogar=fila["miembros_hogar"],
            materias=fila["materias"],
            condiciones=json.loads(fila["condiciones"]),
            fecha=datetime.fromisoformat(fila["fecha"]),
            estado=EstadoSolicitud(fila["estado"]),
            dictamen=self._json_a_dictamen(fila["dictamen"]),
        )

    # -- contrato ----------------------------------------------------------------
    def guardar(self, s: Solicitud) -> None:
        with self._candado, self._conexion:
            self._conexion.execute(
                "INSERT OR REPLACE INTO solicitudes VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (s.id, s.estudiante.carne, s.estudiante.nombre, s.estudiante.carrera,
                 s.promedio, s.ingreso_hogar, s.miembros_hogar, s.materias,
                 json.dumps(s.condiciones), s.fecha.isoformat(), s.estado.value,
                 self._dictamen_a_json(s.dictamen)))

    def obtener(self, id_solicitud: str) -> Solicitud | None:
        with self._candado:
            fila = self._conexion.execute(
                "SELECT * FROM solicitudes WHERE id = ?", (id_solicitud,)).fetchone()
        return self._fila_a_solicitud(fila) if fila else None

    def listar(self) -> list[Solicitud]:
        with self._candado:
            filas = self._conexion.execute(
                "SELECT * FROM solicitudes ORDER BY fecha DESC").fetchall()
        return [self._fila_a_solicitud(f) for f in filas]

    def siguiente_id(self) -> str:
        with self._candado:
            total = self._conexion.execute("SELECT COUNT(*) FROM solicitudes").fetchone()[0]
        return f"SOL-{total + 1:04d}"
