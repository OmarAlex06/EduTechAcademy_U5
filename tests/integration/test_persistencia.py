import pytest
from sqlalchemy.exc import IntegrityError

from src.domain.inscripcion import Inscripcion
from src.infrastructure.repositorio_sql import InscripcionRepositorySQL


def test_guardar_y_recuperar_inscripcion(session):
    repo = InscripcionRepositorySQL(session)                  # Arrange
    insc = Inscripcion(id="I1", estudiante_id="E1", grupo_id="G1")
    insc.confirmar_pago(monto=1500, precio_curso=1500)

    repo.guardar(insc)                                        # Act
    session.commit()
    recuperada = repo.buscar("I1")

    assert recuperada.estado == "Confirmada"                  # Assert
    assert recuperada.pago.monto == 1500


def test_rollback_descarta_cambios_no_confirmados(session):
    repo = InscripcionRepositorySQL(session)
    repo.guardar(Inscripcion(id="I2", estudiante_id="E2", grupo_id="G1"))
    session.flush()          # visible solo dentro de la transacción
    session.rollback()       # se revierte
    assert repo.buscar("I2") is None


def test_error_de_restriccion_deja_la_base_consistente(session):
    repo = InscripcionRepositorySQL(session)
    repo.guardar(Inscripcion(id="I3", estudiante_id="E3", grupo_id="G1"))
    session.commit()

    with pytest.raises(IntegrityError):    # SUP-12 también en la BD
        repo.guardar(Inscripcion(id="I4", estudiante_id="E3", grupo_id="G1"))
        session.commit()
    session.rollback()

    assert len(repo.por_estudiante("E3")) == 1