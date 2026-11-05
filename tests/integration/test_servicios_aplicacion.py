from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.application.asistencia_service import AsistenciaService
from src.application.certificacion_service import CertificacionService
from src.application.inscripcion_service import InscripcionService
from src.domain.curso import Curso
from src.domain.inscripcion import Inscripcion
from src.infrastructure.repositorios_memoria import (
    CursoRepositoryMemoria,
    EstudianteRepositoryMemoria,
    GrupoRepositoryMemoria,
    InscripcionRepositoryMemoria,
)


def _grupo(id_, estado="Programado", instructor="I1", curso_id="C1"):
    return SimpleNamespace(
        id=id_, curso_id=curso_id, estado=estado,
        es_instructor=lambda i: i == instructor,
        ocupar_lugar=Mock(), liberar_lugar=Mock(),
    )


def _confirmada(id_, estudiante_id, grupo_id="G1"):
    insc = Inscripcion(id=id_, estudiante_id=estudiante_id, grupo_id=grupo_id)
    insc.confirmar_pago(monto=1500, precio_curso=1500)
    return insc


@pytest.fixture
def grupo_repo():
    return GrupoRepositoryMemoria()


@pytest.fixture
def insc_repo():
    return InscripcionRepositoryMemoria()


# ---------- AsistenciaService ----------
def test_asistencia_registra_confirmadas_e_ignora_pendientes(grupo_repo, insc_repo):
    grupo_repo.guardar(_grupo("G1"))
    insc_repo.guardar(_confirmada("I1", "E1"))
    insc_repo.guardar(Inscripcion(id="I2", estudiante_id="E2", grupo_id="G1"))
    servicio = AsistenciaService(grupo_repo, insc_repo)

    resultado = servicio.registrar_asistencia("G1", "2026-11-04", ["E1"], "I1")

    assert resultado == {"registradas": ["I1"], "ignoradas": ["I2"]}
    assert insc_repo.buscar("I1").asistencias[0].presente is True


def test_asistencia_marca_ausente_a_quien_no_asistio(grupo_repo, insc_repo):
    grupo_repo.guardar(_grupo("G1"))
    insc_repo.guardar(_confirmada("I1", "E1"))
    servicio = AsistenciaService(grupo_repo, insc_repo)

    servicio.registrar_asistencia("G1", "2026-11-04", [], "I1")

    assert insc_repo.buscar("I1").asistencias[0].presente is False


def test_asistencia_rechaza_instructor_no_asignado(grupo_repo, insc_repo):
    grupo_repo.guardar(_grupo("G1", instructor="I1"))
    servicio = AsistenciaService(grupo_repo, insc_repo)

    with pytest.raises(ValueError, match="no está asignado"):
        servicio.registrar_asistencia("G1", "2026-11-04", [], "I9")


def test_asistencia_rechaza_grupo_inexistente(grupo_repo, insc_repo):
    servicio = AsistenciaService(grupo_repo, insc_repo)
    with pytest.raises(ValueError, match="Grupo no encontrado"):
        servicio.registrar_asistencia("G404", "2026-11-04", [], "I1")


# ---------- CertificacionService ----------
def test_certificacion_rechaza_grupo_inexistente(grupo_repo, insc_repo):
    servicio = CertificacionService(grupo_repo, insc_repo)
    with pytest.raises(ValueError, match="Grupo no encontrado"):
        servicio.validar_certificacion("G404")


def test_certificacion_ignora_inscripciones_pendientes(grupo_repo, insc_repo):
    grupo_repo.guardar(_grupo("G1", estado="Finalizado"))
    insc_repo.guardar(Inscripcion(id="I1", estudiante_id="E1", grupo_id="G1"))
    servicio = CertificacionService(grupo_repo, insc_repo)

    resultado = servicio.validar_certificacion("G1")

    assert resultado == {"elegibles": [], "no_elegibles": []}


def test_emitir_certificado_de_alumno_elegible(grupo_repo, insc_repo):
    grupo_repo.guardar(_grupo("G1", estado="Finalizado"))
    insc = _confirmada("I1", "E1")
    insc.registrar_evaluacion("Final", 90)
    insc.registrar_asistencia("2026-11-04", True)
    insc_repo.guardar(insc)
    servicio = CertificacionService(grupo_repo, insc_repo)

    assert servicio.validar_certificacion("G1")["elegibles"] == ["I1"]
    emitida = servicio.emitir_certificado("I1")

    assert emitida.certificacion.estado == "Emitido"


def test_emitir_certificado_inscripcion_inexistente(grupo_repo, insc_repo):
    servicio = CertificacionService(grupo_repo, insc_repo)
    with pytest.raises(ValueError, match="no encontrada"):
        servicio.emitir_certificado("I404")


def test_emitir_certificado_con_grupo_sin_finalizar(grupo_repo, insc_repo):
    grupo_repo.guardar(_grupo("G1", estado="En curso"))
    insc_repo.guardar(_confirmada("I1", "E1"))
    servicio = CertificacionService(grupo_repo, insc_repo)

    with pytest.raises(ValueError, match="no está finalizado"):
        servicio.emitir_certificado("I1")


# ---------- InscripcionService ----------
@pytest.fixture
def grupos():
    return {"G1": _grupo("G1"), "G2": _grupo("G2")}


@pytest.fixture
def servicio(grupos, insc_repo):
    estudiante_repo = EstudianteRepositoryMemoria()
    estudiante_repo.guardar(SimpleNamespace(id="E1"))
    curso_repo = CursoRepositoryMemoria()
    curso_repo.guardar(Curso(id="C1", nombre="Python", modalidad="En línea",
                             precio=1500.0, requisitos=["Python básico"]))
    grupo_repo = GrupoRepositoryMemoria()
    for g in grupos.values():
        grupo_repo.guardar(g)
    return InscripcionService(estudiante_repo, curso_repo, grupo_repo, insc_repo)


def test_inscribir_estudiante_inexistente(servicio):
    with pytest.raises(ValueError, match="Estudiante no encontrado"):
        servicio.inscribir("E404", "G1")


def test_inscribir_grupo_inexistente(servicio):
    with pytest.raises(ValueError, match="Grupo no encontrado"):
        servicio.inscribir("E1", "G404")


def test_inscribir_deja_pendiente_y_ocupa_lugar(servicio, grupos, insc_repo):
    insc = servicio.inscribir("E1", "G1")

    assert insc.estado == "Pendiente"
    grupos["G1"].ocupar_lugar.assert_called_once_with("E1")
    assert insc_repo.buscar(insc.id) is insc


def test_registrar_pago_de_inscripcion_inexistente(servicio):
    with pytest.raises(ValueError, match="no encontrada"):
        servicio.registrar_pago("INS-404", 1500)


def test_registrar_pago_confirma_la_inscripcion(servicio):
    insc = servicio.inscribir("E1", "G1")

    servicio.registrar_pago(insc.id, 1500)

    assert insc.estado == "Confirmada"


def test_cambiar_grupo_mueve_la_inscripcion(servicio, grupos):
    insc = servicio.inscribir("E1", "G1")

    servicio.cambiar_grupo(insc.id, "G2", "Horario", "CE1")

    grupos["G2"].ocupar_lugar.assert_called_once_with("E1")
    grupos["G1"].liberar_lugar.assert_called_once()
    assert insc.grupo_id == "G2"


def test_cambiar_a_grupo_inexistente_se_rechaza(servicio):
    insc = servicio.inscribir("E1", "G1")
    with pytest.raises(ValueError, match="Grupo destino no encontrado"):
        servicio.cambiar_grupo(insc.id, "G404", "Horario", "CE1")