from dataclasses import dataclass, field

from .eventos import CupoAgotado
from .excepciones import GrupoNoAdmiteInscripciones, InscripcionDuplicada
from .value_objects import Cupo


@dataclass
class AsignacionInstructor:
    instructor_id: str
    fecha_inicio: str
    fecha_fin: str = None

@dataclass
class Grupo:
    id: str
    curso_id: str
    instructor_id: str
    capacidad_maxima: int
    estado: str = "Programado"
    cupo: Cupo = field(init=False)
    asignaciones_instructor: list[AsignacionInstructor] = field(default_factory=list)
    _eventos: list = field(default_factory=list, init=False, repr=False, compare=False)
    _estudiantes_activos: set = field(default_factory=set, init=False, repr=False, compare=False)
    
    def __post_init__(self):
        self.cupo = Cupo(self.capacidad_maxima, 0)
        self.asignaciones_instructor.append(
            AsignacionInstructor(self.instructor_id, "2026-01-01")
        )
    
    def admite_inscripciones(self) -> bool:
        return self.estado in ["Programado", "En curso"]
    
    def ocupar_lugar(self, estudiante_id: str) -> None:
        if not self.admite_inscripciones():
            raise GrupoNoAdmiteInscripciones(f"El grupo está {self.estado} y no admite inscripciones")
        if estudiante_id in self._estudiantes_activos:
            raise InscripcionDuplicada(estudiante_id, self.id)  # SUP-12
        self.cupo = self.cupo.ocupar()
        self._estudiantes_activos.add(estudiante_id)
        if not self.cupo.hay_lugar():
            self._eventos.append(CupoAgotado(self.id))

    def recoger_eventos(self) -> list:
        eventos = list(self._eventos)
        self._eventos.clear()
        return eventos
    
    def liberar_lugar(self) -> None:
        self.cupo = self.cupo.liberar()
    
    def es_instructor(self, instructor_id: str) -> bool:
        return self.instructor_id == instructor_id
    
    def sustituir_instructor(self, nuevo_instructor_id: str, fecha: str) -> None:
        for asignacion in self.asignaciones_instructor:
            if asignacion.fecha_fin is None:
                asignacion.fecha_fin = fecha
        self.asignaciones_instructor.append(
            AsignacionInstructor(nuevo_instructor_id, fecha)
        )
        self.instructor_id = nuevo_instructor_id
    
    def cancelar(self) -> None:
        if self.estado == "Finalizado":
            raise ValueError("No se puede cancelar un grupo finalizado")
        self.estado = "Cancelado"
    
    def finalizar(self) -> None:
        if self.estado == "Cancelado":
            raise ValueError("No se puede finalizar un grupo cancelado")
        self.estado = "Finalizado"