class EstudianteRepositoryMemoria:
    def __init__(self):
        self._datos = {}
    
    def guardar(self, estudiante):
        self._datos[estudiante.id] = estudiante
    
    def buscar(self, id):
        return self._datos.get(id)

class CursoRepositoryMemoria:
    def __init__(self):
        self._datos = {}
    
    def guardar(self, curso):
        self._datos[curso.id] = curso
    
    def buscar(self, id):
        return self._datos.get(id)

class GrupoRepositoryMemoria:
    def __init__(self):
        self._datos = {}
    
    def guardar(self, grupo):
        self._datos[grupo.id] = grupo
    
    def buscar(self, id):
        return self._datos.get(id)
    
    def listar(self):
        return list(self._datos.values())

class InscripcionRepositoryMemoria:
    def __init__(self):
        self._datos = {}
    
    def guardar(self, inscripcion):
        self._datos[inscripcion.id] = inscripcion
    
    def buscar(self, id):
        return self._datos.get(id)
    
    def listar_por_grupo(self, grupo_id):
        return [i for i in self._datos.values() if i.grupo_id == grupo_id]
    
    def listar_por_estudiante(self, estudiante_id):
        return [i for i in self._datos.values() if i.estudiante_id == estudiante_id]