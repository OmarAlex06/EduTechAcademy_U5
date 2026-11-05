from dataclasses import dataclass, field

from .value_objects import Calificacion, PorcentajeAsistencia


@dataclass
class Pago:
    monto: float
    estado: str = "Pendiente"
    fecha: str = None

@dataclass
class Asistencia:
    fecha: str
    presente: bool

@dataclass
class Evaluacion:
    nombre: str
    calificacion: Calificacion

@dataclass
class CambioDeGrupo:
    grupo_anterior_id: str
    grupo_nuevo_id: str
    motivo: str
    autorizado_por: str
    fecha: str

@dataclass
class Certificacion:
    estado: str = "Pendiente"
    motivo_no_elegibilidad: str | None = None

@dataclass
class Inscripcion:
    id: str
    estudiante_id: str
    grupo_id: str
    estado: str = "Pendiente"
    pago: Pago | None = None
    asistencias: list[Asistencia] = field(default_factory=list)
    evaluaciones: list[Evaluacion] = field(default_factory=list)
    cambios_grupo: list[CambioDeGrupo] = field(default_factory=list)
    certificacion: Certificacion = field(default_factory=Certificacion)
    
    def confirmar_pago(self, monto: float, precio_curso: float) -> None:
        if abs(monto - precio_curso) > 0.01:
            raise ValueError(f"El monto {monto} no coincide con el precio {precio_curso}")
        self.pago = Pago(monto=monto, estado="Pagado")
        self.estado = "Confirmada"
    
    def registrar_asistencia(self, fecha: str, presente: bool) -> None:
        if self.estado != "Confirmada":
            raise ValueError("Solo se registra asistencia en inscripciones confirmadas")
        self.asistencias.append(Asistencia(fecha, presente))
    
    def registrar_evaluacion(self, nombre: str, valor: float) -> None:
        if self.estado != "Confirmada":
            raise ValueError("Solo se registra evaluación en inscripciones confirmadas")
        self.evaluaciones.append(Evaluacion(nombre, Calificacion(valor)))
    
    def calcular_calificacion_final(self) -> Calificacion | None:
        if not self.evaluaciones:
            return None
        promedio = sum(e.calificacion.valor for e in self.evaluaciones) / len(self.evaluaciones)
        return Calificacion(promedio)
    
    def calcular_porcentaje_asistencia(self) -> PorcentajeAsistencia:
        if not self.asistencias:
            return PorcentajeAsistencia(0)
        presentes = sum(1 for a in self.asistencias if a.presente)
        porcentaje = (presentes / len(self.asistencias)) * 100
        return PorcentajeAsistencia(porcentaje)
    
    def evaluar_certificacion(self, grupo_finalizado: bool) -> None:
        if not grupo_finalizado:
            raise ValueError("El grupo no está finalizado")
        
        calificacion = self.calcular_calificacion_final()
        porcentaje = self.calcular_porcentaje_asistencia()
        
        aprueba_calificacion = calificacion and calificacion.aprueba()
        cumple_asistencia = porcentaje.cumple_minimo()
        
        if aprueba_calificacion and cumple_asistencia:
            self.certificacion.estado = "Elegible"
        else:
            self.certificacion.estado = "No elegible"
            if not aprueba_calificacion and not cumple_asistencia:
                self.certificacion.motivo_no_elegibilidad = "Ambos"
            elif not aprueba_calificacion:
                self.certificacion.motivo_no_elegibilidad = "Calificación"
            else:
                self.certificacion.motivo_no_elegibilidad = "Asistencia"
    
    def emitir_certificado(self) -> None:
        if self.certificacion.estado != "Elegible":
            raise ValueError("El estudiante no es elegible para certificación")
        self.certificacion.estado = "Emitido"
    
    def cambiar_grupo(self, nuevo_grupo_id: str, autorizado_por: str, motivo: str) -> None:
        self.cambios_grupo.append(
            CambioDeGrupo(
                grupo_anterior_id=self.grupo_id,
                grupo_nuevo_id=nuevo_grupo_id,
                motivo=motivo,
                autorizado_por=autorizado_por,
                fecha="2026-10-13"
            )
        )
        self.grupo_id = nuevo_grupo_id