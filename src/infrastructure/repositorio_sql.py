from src.domain.inscripcion import Inscripcion, Pago
from src.infrastructure.orm import InscripcionORM


class InscripcionRepositorySQL:
    def __init__(self, session):
        self.session = session

    def guardar(self, insc: Inscripcion) -> None:
        monto = insc.pago.monto if insc.pago else None
        self.session.add(InscripcionORM(
            id=insc.id,
            estudiante_id=insc.estudiante_id,
            grupo_id=insc.grupo_id,
            estado=insc.estado,
            monto_centavos=None if monto is None else round(monto * 100),
        ))

    def buscar(self, insc_id: str):
        fila = self.session.get(InscripcionORM, insc_id)
        return self._a_dominio(fila) if fila else None

    def por_estudiante(self, estudiante_id: str):
        filas = self.session.query(InscripcionORM).filter_by(
            estudiante_id=estudiante_id).all()
        return [self._a_dominio(f) for f in filas]

    @staticmethod
    def _a_dominio(fila: InscripcionORM) -> Inscripcion:
        pago = None
        if fila.monto_centavos is not None:
            pago = Pago(monto=fila.monto_centavos / 100, estado="Pagado")
        return Inscripcion(
            id=fila.id,
            estudiante_id=fila.estudiante_id,
            grupo_id=fila.grupo_id,
            estado=fila.estado,
            pago=pago,
        )