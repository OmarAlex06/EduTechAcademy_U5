from enum import Enum


class EstadoInscripcion(str, Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    GRUPO_CANCELADO = "GrupoCancelado"
    CANCELADA = "Cancelada"


class EstadoCertificacion(str, Enum):
    PENDIENTE = "Pendiente"
    ELEGIBLE = "Elegible"
    NO_ELEGIBLE = "No elegible"
    EMITIDO = "Emitido"