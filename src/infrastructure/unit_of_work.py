from .repositorios_memoria import (
    CursoRepositoryMemoria,
    EstudianteRepositoryMemoria,
    GrupoRepositoryMemoria,
    InscripcionRepositoryMemoria,
)


class UnitOfWorkMemoria:
    def __init__(self):
        self.estudiantes = EstudianteRepositoryMemoria()
        self.cursos = CursoRepositoryMemoria()
        self.grupos = GrupoRepositoryMemoria()
        self.inscripciones = InscripcionRepositoryMemoria()
        self._en_transaccion = False
    
    def iniciar(self):
        self._en_transaccion = True
    
    def confirmar(self):
        self._en_transaccion = False
    
    def revertir(self):
        self._en_transaccion = False
        # En memoria no hay rollback real; se documenta como limitación
    
    def __enter__(self):
        self.iniciar()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.revertir()
        else:
            self.confirmar()