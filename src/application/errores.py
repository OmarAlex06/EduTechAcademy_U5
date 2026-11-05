class PasarelaNoDisponible(Exception):
    """La pasarela de pagos no respondió (timeout o caída)."""


class PagoYaConfirmado(ValueError):
    """La inscripción ya está confirmada; no se cobra de nuevo."""

class PermisoDenegado(Exception):
    """El actor no tiene permiso para esta operación (RB-14)."""