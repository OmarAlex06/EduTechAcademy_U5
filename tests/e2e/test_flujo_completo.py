from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.application.asistencia_service import AsistenciaService
from src.application.certificacion_service import CertificacionService
from src.application.inscripcion_service import InscripcionService
from src.application.pago_service import PagoService
from src.application.puertos import PasarelaPagos, Publicador, ResultadoCobro
from src.domain.curso import Curso
from src.domain.estudiante import Estudiante
from src.domain.grupo import Grupo
from src.infrastructure.repositorios_memoria import (
    CursoRepositoryMemoria,
    EstudianteRepositoryMemoria,
    GrupoRepositoryMemoria,
    InscripcionRepositoryMemoria,
)

ID_INSC = "INS-E1-G1"
PRECIO = 1500.0


@pytest.fixture
def servicios():
    estudiante_repo = EstudianteRepositoryMemoria()
    curso_repo = CursoRepositoryMemoria()
    grupo_repo = GrupoRepositoryMemoria()
    insc_repo = InscripcionRepositoryMemoria()

    estudiante_repo.guardar(Estudiante(id="E1", nombre="Ana", correo="ana@ejemplo.com"))
    curso_repo.guardar(Curso(id="C1", nombre="Python", modalidad="En línea",
                             precio=PRECIO, requisitos=[]))
    grupo_repo.guardar(Grupo(id="G1", curso_id="C1", instructor_id="I1",
                             capacidad_maxima=30))

    pasarela = Mock(spec=PasarelaPagos)
    publicador = Mock(spec=Publicador)
    return SimpleNamespace(
        pasarela=pasarela,
        publicador=publicador,
        grupo_repo=grupo_repo,
        insc_repo=insc_repo,
        inscripcion=InscripcionService(estudiante_repo, curso_repo, grupo_repo, insc_repo),
        pago=PagoService(pasarela, insc_repo, grupo_repo, curso_repo, publicador),
        asistencia=AsistenciaService(grupo_repo, insc_repo),
        certificacion=CertificacionService(grupo_repo, insc_repo),
    )


def test_alumno_cumple_todo_y_queda_elegible(servicios):
    servicios.pasarela.cobrar.return_value = ResultadoCobro(aprobado=True)

    # 1) Se inscribe -> queda Pendiente
    insc = servicios.inscripcion.inscribir("E1", "G1")
    assert insc.id == ID_INSC
    assert insc.estado == "Pendiente"

    # 2) Paga -> la pasarela aprueba, se Confirma y se publica PagoRecibido
    servicios.pago.registrar_pago(insc.id, PRECIO)
    assert insc.estado == "Confirmada"
    servicios.publicador.publicar.assert_called_once()

    # 3) El instructor registra 5 sesiones (4 asistencias = 80 %) y una nota de 70
    sesiones = [("2026-11-01", ["E1"]), ("2026-11-02", ["E1"]), ("2026-11-03", ["E1"]),
                ("2026-11-04", ["E1"]), ("2026-11-05", [])]
    for fecha, asistentes in sesiones:
        servicios.asistencia.registrar_asistencia("G1", fecha, asistentes, "I1")
    insc.registrar_evaluacion("Final", 70)

    # 4) El grupo finaliza y se valida la certificación
    servicios.grupo_repo.buscar("G1").finalizar()
    resultado = servicios.certificacion.validar_certificacion("G1")

    # 5) Justo en los umbrales (70/100 y 80 %) queda Elegible
    assert resultado["elegibles"] == [ID_INSC]
    assert insc.certificacion.estado == "Elegible"


def test_pago_rechazado_impide_registrar_asistencia(servicios):  # RB-04
    servicios.pasarela.cobrar.return_value = ResultadoCobro(aprobado=False)
    insc = servicios.inscripcion.inscribir("E1", "G1")

    servicios.pago.registrar_pago(insc.id, PRECIO)
    resultado = servicios.asistencia.registrar_asistencia("G1", "2026-11-01", ["E1"], "I1")

    assert insc.estado == "Pendiente"
    servicios.publicador.publicar.assert_not_called()
    assert resultado == {"registradas": [], "ignoradas": [ID_INSC]}
    assert insc.asistencias == []