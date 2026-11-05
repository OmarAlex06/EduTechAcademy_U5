from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.application.errores import PagoYaConfirmado, PasarelaNoDisponible
from src.application.pago_service import PagoService
from src.application.puertos import PasarelaPagos, Publicador, ResultadoCobro
from src.domain.curso import Curso
from src.domain.eventos import PagoRecibido
from src.domain.inscripcion import Inscripcion
from src.infrastructure.repositorios_memoria import (
    CursoRepositoryMemoria,
    GrupoRepositoryMemoria,
    InscripcionRepositoryMemoria,
)

PRECIO = 1500.0


@pytest.fixture
def curso_repo():
    repo = CursoRepositoryMemoria()
    repo.guardar(Curso(id="C1", nombre="Python", modalidad="En línea",
                       precio=PRECIO, requisitos=[]))
    repo.guardar(Curso(id="C0", nombre="Intro gratis", modalidad="En línea",
                       precio=0.0, requisitos=[]))
    return repo


@pytest.fixture
def grupo_repo():
    repo = GrupoRepositoryMemoria()
    repo.guardar(SimpleNamespace(id="G1", curso_id="C1"))
    repo.guardar(SimpleNamespace(id="G0", curso_id="C0"))
    return repo


@pytest.fixture
def repo():
    return InscripcionRepositoryMemoria()


@pytest.fixture
def insc(repo):
    inscripcion = Inscripcion(id="I1", estudiante_id="E1", grupo_id="G1")
    repo.guardar(inscripcion)
    return inscripcion


@pytest.fixture
def pasarela():
    return Mock(spec=PasarelaPagos)


@pytest.fixture
def publicador():
    return Mock(spec=Publicador)


@pytest.fixture
def servicio(pasarela, repo, grupo_repo, curso_repo, publicador):
    return PagoService(pasarela, repo, grupo_repo, curso_repo, publicador)


# TC-PAGO-01
def test_pago_aprobado_confirma(servicio, insc, repo, pasarela, publicador):
    pasarela.cobrar.return_value = ResultadoCobro(aprobado=True)   # Arrange

    servicio.registrar_pago(insc.id, monto=PRECIO)                 # Act

    pasarela.cobrar.assert_called_once_with(insc.id, PRECIO)       # Assert
    assert repo.buscar(insc.id).estado == "Confirmada"
    publicador.publicar.assert_called_once_with(
        PagoRecibido(inscripcion_id=insc.id, monto=PRECIO))


# TC-PAGO-02
def test_pago_rechazado_deja_pendiente(servicio, insc, repo, pasarela, publicador):
    pasarela.cobrar.return_value = ResultadoCobro(aprobado=False)

    servicio.registrar_pago(insc.id, monto=PRECIO)

    assert repo.buscar(insc.id).estado == "Pendiente"
    publicador.publicar.assert_not_called()


def test_timeout_no_confirma(servicio, insc, repo, pasarela, publicador):
    pasarela.cobrar.side_effect = TimeoutError

    with pytest.raises(PasarelaNoDisponible):
        servicio.registrar_pago(insc.id, monto=PRECIO)

    assert repo.buscar(insc.id).estado == "Pendiente"
    publicador.publicar.assert_not_called()


# TC-PAGO-03
def test_curso_gratuito_omite_el_cobro(servicio, repo, pasarela):
    gratis = Inscripcion(id="I0", estudiante_id="E1", grupo_id="G0")
    repo.guardar(gratis)

    servicio.registrar_pago(gratis.id, monto=0.0)

    pasarela.cobrar.assert_not_called()
    assert repo.buscar("I0").estado == "Confirmada"


def test_monto_distinto_se_rechaza_antes_de_cobrar(servicio, insc, pasarela):
    with pytest.raises(ValueError):
        servicio.registrar_pago(insc.id, monto=PRECIO - 100)

    pasarela.cobrar.assert_not_called()


def test_segundo_pago_no_cobra_dos_veces(servicio, insc, pasarela):
    pasarela.cobrar.return_value = ResultadoCobro(aprobado=True)
    servicio.registrar_pago(insc.id, monto=PRECIO)

    with pytest.raises(PagoYaConfirmado):
        servicio.registrar_pago(insc.id, monto=PRECIO)

    pasarela.cobrar.assert_called_once()