from sqlalchemy import Index, Integer, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class InscripcionORM(Base):
    __tablename__ = "inscripciones"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    estudiante_id: Mapped[str] = mapped_column(String, nullable=False)
    grupo_id: Mapped[str] = mapped_column(String, nullable=False)
    estado: Mapped[str] = mapped_column(String, nullable=False)
    # monto del pago en centavos enteros (None mientras no haya pago)
    monto_centavos: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # SUP-12: un alumno no puede tener dos inscripciones activas en el mismo grupo
    __table_args__ = (
        Index(
            "ux_inscripcion_activa",
            "estudiante_id",
            "grupo_id",
            unique=True,
            sqlite_where=text("estado != 'Cancelada'"),
        ),
    )