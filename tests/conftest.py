import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.domain.grupo import Grupo
from src.domain.inscripcion import Inscripcion
from src.infrastructure.orm import Base


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
        s.rollback()
    engine.dispose()

@pytest.fixture
def grupo():
    """Grupo Programado con capacidad para 5 estudiantes."""
    return Grupo("G1", "CUR-01", "INST-01", 5)


@pytest.fixture
def crear_inscripcion():
    """Devuelve una función que arma una inscripción Confirmada con
    las calificaciones y asistencias indicadas (1 = presente, 0 = falta)."""

    def _crear(calificaciones=(), asistencias=()):
        insc = Inscripcion("INS-1", "E1", "G1")
        insc.confirmar_pago(monto=1000.0, precio_curso=1000.0)
        for i, valor in enumerate(calificaciones, start=1):
            insc.registrar_evaluacion(f"Evaluación {i}", valor)
        for i, presente in enumerate(asistencias, start=1):
            insc.registrar_asistencia(f"2026-01-{i:02d}", bool(presente))
        return insc

    return _crear