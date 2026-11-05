from dataclasses import dataclass

from src.application.errores import PermisoDenegado


@dataclass(frozen=True)
class Actor:
    id: str
    rol: str  # "estudiante" | "instructor" | "control_escolar"


class ServicioAutorizado:
    """Verifica el rol (RB-14) y delega en los Application Services."""

    def __init__(self, inscripcion_service, asistencia_service,
                 certificacion_service, grupo_repo):
        self.inscripcion = inscripcion_service
        self.asistencia = asistencia_service
        self.certificacion = certificacion_service
        self.grupo_repo = grupo_repo

    def inscribir(self, actor: Actor, estudiante_id: str, grupo_id: str):
        es_control = actor.rol == "control_escolar"
        es_el_mismo = actor.rol == "estudiante" and actor.id == estudiante_id
        if not (es_control or es_el_mismo):
            raise PermisoDenegado(f"{actor.rol} no puede inscribir a {estudiante_id}")
        return self.inscripcion.inscribir(estudiante_id, grupo_id)

    def registrar_asistencia(self, actor: Actor, grupo_id: str, fecha: str, asistentes: list):
        if actor.rol != "instructor":
            raise PermisoDenegado(f"{actor.rol} no puede registrar asistencia")
        grupo = self.grupo_repo.buscar(grupo_id)
        if not grupo:
            raise ValueError("Grupo no encontrado")
        if not grupo.es_instructor(actor.id):
            raise PermisoDenegado("El instructor no está asignado a este grupo")
        return self.asistencia.registrar_asistencia(grupo_id, fecha, asistentes, actor.id)

    def validar_certificacion(self, actor: Actor, grupo_id: str):
        if actor.rol != "control_escolar":
            raise PermisoDenegado(f"{actor.rol} no puede validar certificaciones")
        return self.certificacion.validar_certificacion(grupo_id)

    def emitir_certificado(self, actor: Actor, inscripcion_id: str):
        if actor.rol != "control_escolar":
            raise PermisoDenegado(f"{actor.rol} no puede emitir certificados")
        return self.certificacion.emitir_certificado(inscripcion_id)