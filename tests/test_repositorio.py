"""Pruebas de persistencia: el repositorio SQLite conserva el dictamen completo."""
from app.dominio import Estudiante, Solicitud
from app.integracion.motor import MotorProlog
from app.repositorio.base import RepositorioMemoria
from app.repositorio.sqlite import RepositorioSQLite


def test_sqlite_guarda_y_recupera_el_dictamen(tmp_path):
    repo = RepositorioSQLite(str(tmp_path / "prueba.db"))
    s = Solicitud(repo.siguiente_id(), Estudiante("FI-0001", "Ana", "Software"),
                  77, 700_000, 4, 4, ["jefe_de_hogar"])
    s.registrar_dictamen(MotorProlog().evaluar(s))
    repo.guardar(s)

    recuperada = RepositorioSQLite(str(tmp_path / "prueba.db")).obtener(s.id)
    assert recuperada.dictamen.resultado.value == "aprobada"
    assert recuperada.dictamen.condiciones_aplicadas == ["jefe_de_hogar"]
    assert [c.criterio for c in recuperada.dictamen.criterios] == ["promedio", "ingreso", "carga_academica"]
    assert repo.siguiente_id() == "SOL-0002"


def test_ambos_repositorios_cumplen_el_mismo_contrato():
    for repo in (RepositorioMemoria(), RepositorioSQLite(":memory:")):
        s = Solicitud(repo.siguiente_id(), Estudiante("FI-0002", "Luis", "Software"), 85, 600_000, 3, 4)
        repo.guardar(s)
        assert repo.obtener(s.id).estudiante.nombre == "Luis"
        assert len(repo.listar()) == 1
