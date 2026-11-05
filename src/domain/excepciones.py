class CupoAgotadoException(ValueError):
    """No hay lugares disponibles en el grupo (RB-02)."""


class InscripcionDuplicada(ValueError):
    """El estudiante ya tiene una inscripción activa en el grupo (SUP-12)."""

    def __init__(self, estudiante_id, grupo_id):
        super().__init__(
            f"El estudiante {estudiante_id} ya tiene una inscripción activa en el grupo {grupo_id}"
        )
        self.estudiante_id = estudiante_id
        self.grupo_id = grupo_id


class GrupoNoAdmiteInscripciones(ValueError):
    """El grupo no está Programado ni En curso."""