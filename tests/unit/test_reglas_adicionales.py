import pytest

from src.domain.curso import Curso
from src.domain.inscripcion import Inscripcion
from src.domain.value_objects import Calificacion, Cupo, PorcentajeAsistencia


def _confirmada():
    insc = Inscripcion(id="I1", estudiante_id="E1", grupo_id="G1")
    insc.confirmar_pago(monto=1500, precio_curso=1500)
    return insc


def test_asistencia_requiere_inscripcion_confirmada():
    insc = Inscripcion(id="I1", estudiante_id="E1", grupo_id="G1")
    with pytest.raises(ValueError):
        insc.registrar_asistencia("2026-11-04", True)


def test_evaluacion_requiere_inscripcion_confirmada():
    insc = Inscripcion(id="I1", estudiante_id="E1", grupo_id="G1")
    with pytest.raises(ValueError):
        insc.registrar_evaluacion("Final", 90)


def test_pago_con_monto_incorrecto_se_rechaza():
    insc = Inscripcion(id="I1", estudiante_id="E1", grupo_id="G1")
    with pytest.raises(ValueError):
        insc.confirmar_pago(monto=100, precio_curso=1500)
    assert insc.estado == "Pendiente"


def test_sin_evaluaciones_no_hay_calificacion_final():
    assert _confirmada().calcular_calificacion_final() is None


def test_sin_asistencias_el_porcentaje_es_cero():
    assert _confirmada().calcular_porcentaje_asistencia().valor == 0


def test_certificacion_requiere_grupo_finalizado():
    with pytest.raises(ValueError):
        _confirmada().evaluar_certificacion(grupo_finalizado=False)


def test_no_elegible_por_calificacion_y_asistencia():
    insc = _confirmada()
    insc.registrar_evaluacion("Final", 50)
    insc.registrar_asistencia("2026-11-04", False)

    insc.evaluar_certificacion(grupo_finalizado=True)

    assert insc.certificacion.estado == "No elegible"
    assert insc.certificacion.motivo_no_elegibilidad == "Ambos"


def test_no_elegible_si_no_hay_evaluaciones():
    insc = _confirmada()
    insc.registrar_asistencia("2026-11-04", True)

    insc.evaluar_certificacion(grupo_finalizado=True)

    assert insc.certificacion.estado == "No elegible"
    assert insc.certificacion.motivo_no_elegibilidad == "Calificación"


def test_emitir_certificado_cuando_es_elegible():
    insc = _confirmada()
    insc.registrar_evaluacion("Final", 90)
    insc.registrar_asistencia("2026-11-04", True)
    insc.evaluar_certificacion(grupo_finalizado=True)

    insc.emitir_certificado()

    assert insc.certificacion.estado == "Emitido"


def test_emitir_certificado_sin_ser_elegible_se_rechaza():
    with pytest.raises(ValueError):
        _confirmada().emitir_certificado()


def test_cambiar_grupo_registra_el_cambio():
    insc = _confirmada()

    insc.cambiar_grupo("G2", autorizado_por="CE1", motivo="Horario")

    assert insc.grupo_id == "G2"
    assert len(insc.cambios_grupo) == 1
    assert insc.cambios_grupo[0].grupo_anterior_id == "G1"


@pytest.mark.parametrize("valor", [-1, 100.1])
def test_calificacion_fuera_de_rango_se_rechaza(valor):
    with pytest.raises(ValueError):
        Calificacion(valor)


@pytest.mark.parametrize("valor", [-1, 100.1])
def test_asistencia_fuera_de_rango_se_rechaza(valor):
    with pytest.raises(ValueError):
        PorcentajeAsistencia(valor)


def test_cupo_no_admite_mas_ocupados_que_capacidad():
    with pytest.raises(ValueError):
        Cupo(capacidad_maxima=1, ocupados=2)


def test_cupo_liberar_reduce_ocupados():
    assert Cupo(capacidad_maxima=2, ocupados=1).liberar().ocupados == 0


def test_cupo_liberar_vacio_se_rechaza():
    with pytest.raises(ValueError):
        Cupo(capacidad_maxima=2, ocupados=0).liberar()


def test_curso_con_precio_negativo_se_rechaza():
    with pytest.raises(ValueError):
        Curso(id="C1", nombre="Python", modalidad="En línea",
              precio=-1, requisitos=[])


def test_curso_con_modalidad_invalida_se_rechaza():
    with pytest.raises(ValueError):
        Curso(id="C1", nombre="Python", modalidad="Mixta",
              precio=100, requisitos=[])