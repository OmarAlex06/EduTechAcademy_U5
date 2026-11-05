from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.application.asistencia_service import AsistenciaService
from src.application.autorizacion import Actor, ServicioAutorizado
from src.application.certificacion_service import CertificacionService
from src.application.errores import PermisoDenegado
from src.application.inscripcion_service import InscripcionService
from src.infrastructure.repositorios_memoria import GrupoRepositoryMemoria

ACTORES = {
    "estudiante": Actor("E1", "estudiante"),
    "instructor": Actor("I1", "instructor"),            # asignado a G1
    "instructor_ajeno": Actor("I2", "instructor"),      # no asignado a G1
    "control_escolar": Actor("CE1", "control_escolar"),
}


@pytest.fixture
def servicios():
    grupo_repo = GrupoRepositoryMemoria()
    grupo_repo.guardar(SimpleNamespace(id="G1", es_instructor=lambda i: i == "I1"))

    inscripcion = Mock(spec=InscripcionService)
    asistencia = Mock(spec=AsistenciaService)
    certificacion = Mock(spec=CertificacionService)
    auth = ServicioAutorizado(inscripcion, asistencia, certificacion, grupo_repo)
    return SimpleNamespace(auth=auth, inscripcion=inscripcion,
                           asistencia=asistencia, certificacion=certificacion)


def _llamadas(s):
    return (len(s.inscripcion.method_calls) + len(s.asistencia.method_calls)
            + len(s.certificacion.method_calls))


def ejecutar(s, actor, operacion):
    a = ACTORES[actor]
    if operacion == "inscribirse_a_si_mismo":
        return s.auth.inscribir(a, "E1", "G1")
    if operacion == "inscribir_a_otro":
        return s.auth.inscribir(a, "E2", "G1")
    if operacion == "registrar_asistencia":
        return s.auth.registrar_asistencia(a, "G1", "2026-11-04", ["E1"])
    if operacion == "emitir_certificado":
        return s.auth.emitir_certificado(a, "INS-E1-G1")
    raise ValueError(operacion)


@pytest.mark.parametrize("actor, operacion, permitido", [
    ("estudiante",       "inscribirse_a_si_mismo", True),
    ("estudiante",       "inscribir_a_otro",       False),
    ("estudiante",       "registrar_asistencia",   False),
    ("estudiante",       "emitir_certificado",     False),
    ("instructor",       "registrar_asistencia",   True),   # grupo propio
    ("instructor_ajeno", "registrar_asistencia",   False),  # grupo ajeno
    ("instructor",       "inscribir_a_otro",       False),
    ("instructor",       "emitir_certificado",     False),
    ("control_escolar",  "inscribir_a_otro",       True),
    ("control_escolar",  "emitir_certificado",     True),
    ("control_escolar",  "registrar_asistencia",   False),
])
def test_permisos_por_rol(servicios, actor, operacion, permitido):  # RB-14
    if permitido:
        ejecutar(servicios, actor, operacion)       # no lanza error
        assert _llamadas(servicios) == 1            # delegó en el servicio
    else:
        with pytest.raises(PermisoDenegado):
            ejecutar(servicios, actor, operacion)
        assert _llamadas(servicios) == 0            # nada se ejecutó