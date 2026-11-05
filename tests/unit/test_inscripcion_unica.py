import pytest

from src.domain.excepciones import InscripcionDuplicada


def test_rechaza_segunda_inscripcion_activa(grupo):  # SUP-12
    grupo.ocupar_lugar("E1")                    # Arrange: primera inscripción
    with pytest.raises(InscripcionDuplicada):   # Assert: debe rechazarse
        grupo.ocupar_lugar("E1")                # Act: segunda inscripción