from dataclasses import dataclass

from .excepciones import CupoAgotadoException


@dataclass(frozen=True)
class Calificacion:
    valor: float
    
    def __post_init__(self):
        if not (0 <= self.valor <= 100):
            raise ValueError("La calificación debe estar entre 0 y 100")
    
    def aprueba(self) -> bool:
        return self.valor >= 75

@dataclass(frozen=True)
class PorcentajeAsistencia:
    valor: float
    
    def __post_init__(self):
        if not (0 <= self.valor <= 100):
            raise ValueError("El porcentaje debe estar entre 0 y 100")
    
    def cumple_minimo(self) -> bool:
        return self.valor >= 80

@dataclass(frozen=True)
class Cupo:
    capacidad_maxima: int
    ocupados: int
    
    def __post_init__(self):
        if self.ocupados > self.capacidad_maxima:
            raise ValueError("Los ocupados no pueden superar la capacidad")
    
    def hay_lugar(self) -> bool:
        return self.ocupados < self.capacidad_maxima
    
    def ocupar(self) -> "Cupo":
        if not self.hay_lugar():
            raise CupoAgotadoException("No hay cupo disponible")
        return Cupo(self.capacidad_maxima, self.ocupados + 1)
    
    def liberar(self) -> "Cupo":
        if self.ocupados <= 0:
            raise ValueError("No hay lugares ocupados que liberar")
        return Cupo(self.capacidad_maxima, self.ocupados - 1)