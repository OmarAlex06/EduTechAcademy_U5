from dataclasses import dataclass


@dataclass
class Curso:
    id: str
    nombre: str
    modalidad: str
    precio: float
    requisitos: list[str]
    
    def __post_init__(self):
        if self.precio < 0:
            raise ValueError("El precio no puede ser negativo")
        if self.modalidad not in ["Presencial", "En línea"]:
            raise ValueError("Modalidad debe ser Presencial o En línea")