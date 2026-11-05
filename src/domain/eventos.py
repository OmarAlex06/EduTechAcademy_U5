from dataclasses import dataclass


@dataclass(frozen=True)
class CupoAgotado:
    grupo_id: str


@dataclass(frozen=True)
class PagoRecibido:
    inscripcion_id: str
    monto: float
    