from dataclasses import dataclass


@dataclass
class Estudiante:
    id: str
    nombre: str
    correo: str
    telefono: str = ""