"""Configuración común: las pruebas usan una base SQLite en memoria."""
import os

os.environ["EVALUABECA_DB"] = ":memory:"
