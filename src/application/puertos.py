from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ResultadoCobro:
    aprobado: bool


class PasarelaPagos(Protocol):
    def cobrar(self, inscripcion_id: str, monto: float) -> ResultadoCobro: ...


class Publicador(Protocol):
    def publicar(self, evento) -> None: ...