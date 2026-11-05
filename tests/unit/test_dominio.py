import pytest

from src.domain.estados import EstadoCertificacion
from src.domain.eventos import CupoAgotado
from src.domain.excepciones import CupoAgotadoException
from src.domain.grupo import Grupo
from src.domain.value_objects import Calificacion, Cupo, PorcentajeAsistencia

# ---------- Value Objects: umbrales ----------

@pytest.mark.parametrize("valor, esperado",
                         [(0, False), (69.9, False), (70, True), (100, True)])
def test_calificacion_aprueba_en_el_umbral(valor, esperado):  # RB-07
    calificacion = Calificacion(valor)       # Arrange
    resultado = calificacion.aprueba()       # Act
    assert resultado is esperado             # Assert


@pytest.mark.parametrize("valor, esperado",
                         [(0, False), (79.9, False), (80, True), (100, True)])
def test_asistencia_cumple_minimo_en_el_umbral(valor, esperado):  # RB-06
    assert PorcentajeAsistencia(valor).cumple_minimo() is esperado


# ---------- Cupo (RB-02) ----------

def test_inscribir_con_cupo_disminuye_lugares():  # TC-CUPO-01
    grupo = Grupo("G1", "CUR-01", "I1", 3)
    grupo.ocupar_lugar("E1")
    assert grupo.cupo.ocupados == 1
    assert grupo.cupo.hay_lugar()


def test_cupo_no_excede_capacidad():  # TC-CUPO-02
    cupo = Cupo(capacidad_maxima=1, ocupados=1)
    with pytest.raises(CupoAgotadoException):
        cupo.ocupar()


def test_ultimo_lugar_publica_cupo_agotado():  # TC-CUPO-03
    grupo = Grupo("G9", "CUR-01", "I1", 2)
    grupo.ocupar_lugar("E1")
    grupo.ocupar_lugar("E2")                 # toma el último lugar
    assert grupo.recoger_eventos() == [CupoAgotado("G9")]
    assert not grupo.cupo.hay_lugar()


# ---------- Certificación (RB-06, RB-07, RB-08) ----------

def test_elegible_con_90_y_100_por_ciento(crear_inscripcion):  # TC-CERT-01
    insc = crear_inscripcion(calificaciones=[90], asistencias=[1, 1, 1, 1, 1])
    insc.evaluar_certificacion(grupo_finalizado=True)
    assert insc.certificacion.estado == EstadoCertificacion.ELEGIBLE


def test_no_elegible_con_69_y_100_por_ciento(crear_inscripcion):  # TC-CERT-02
    insc = crear_inscripcion(calificaciones=[69], asistencias=[1, 1, 1, 1, 1])
    insc.evaluar_certificacion(grupo_finalizado=True)
    assert insc.certificacion.estado == EstadoCertificacion.NO_ELEGIBLE
    assert insc.certificacion.motivo_no_elegibilidad == "Calificación"


def test_no_elegible_con_75_por_ciento_de_asistencia(crear_inscripcion):  # TC-CERT-02 (variante)
    insc = crear_inscripcion(calificaciones=[100], asistencias=[1, 1, 1, 0])
    insc.evaluar_certificacion(grupo_finalizado=True)
    assert insc.certificacion.estado == EstadoCertificacion.NO_ELEGIBLE
    assert insc.certificacion.motivo_no_elegibilidad == "Asistencia"


def test_elegible_con_70_y_80_por_ciento(crear_inscripcion):  # TC-CERT-03
    insc = crear_inscripcion(calificaciones=[70], asistencias=[1, 1, 1, 1, 0])
    insc.evaluar_certificacion(grupo_finalizado=True)
    assert insc.certificacion.estado == EstadoCertificacion.ELEGIBLE