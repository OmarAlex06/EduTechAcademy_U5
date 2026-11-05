from src.application.errores import PagoYaConfirmado, PasarelaNoDisponible
from src.domain.eventos import PagoRecibido


class PagoService:
    def __init__(self, pasarela, inscripcion_repo, grupo_repo, curso_repo, publicador):
        self.pasarela = pasarela
        self.inscripcion_repo = inscripcion_repo
        self.grupo_repo = grupo_repo
        self.curso_repo = curso_repo
        self.publicador = publicador

    def registrar_pago(self, inscripcion_id: str, monto: float):
        inscripcion = self.inscripcion_repo.buscar(inscripcion_id)
        if not inscripcion:
            raise ValueError("Inscripción no encontrada")

        # Se rechaza ANTES de llegar a la pasarela (evita doble cobro)
        if inscripcion.estado == "Confirmada":
            raise PagoYaConfirmado(f"La inscripción {inscripcion_id} ya está confirmada")

        grupo = self.grupo_repo.buscar(inscripcion.grupo_id)
        precio = self.curso_repo.buscar(grupo.curso_id).precio

        # Monto incorrecto: se rechaza antes de cobrar
        if abs(monto - precio) > 0.01:
            raise ValueError(f"El monto {monto} no coincide con el precio {precio}")

        # TC-PAGO-03: curso gratuito, se omite el cobro
        if precio == 0:
            inscripcion.confirmar_pago(monto, precio)
            self.inscripcion_repo.guardar(inscripcion)
            return inscripcion

        # 1) cobrar
        try:
            cobro = self.pasarela.cobrar(inscripcion.id, monto)
        except TimeoutError as error:
            raise PasarelaNoDisponible("La pasarela no respondió") from error

        # 2) si rechaza, sigue Pendiente y no se publica nada (SUP-13)
        if not cobro.aprobado:
            return inscripcion

        # 3) confirmar, guardar y publicar
        inscripcion.confirmar_pago(monto, precio)
        self.inscripcion_repo.guardar(inscripcion)
        self.publicador.publicar(PagoRecibido(inscripcion_id=inscripcion.id, monto=monto))
        return inscripcion