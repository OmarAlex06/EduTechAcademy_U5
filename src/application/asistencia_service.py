class AsistenciaService:
    def __init__(self, grupo_repo, inscripcion_repo):
        self.grupo_repo = grupo_repo
        self.inscripcion_repo = inscripcion_repo
    
    def registrar_asistencia(self, grupo_id: str, fecha: str, asistentes: list, instructor_id: str) -> dict:
        grupo = self.grupo_repo.buscar(grupo_id)
        if not grupo:
            raise ValueError("Grupo no encontrado")
        
        if not grupo.es_instructor(instructor_id):
            raise ValueError("El instructor no está asignado a este grupo")
        
        inscripciones = self.inscripcion_repo.listar_por_grupo(grupo_id)
        resultados = {"registradas": [], "ignoradas": []}
        
        for inscripcion in inscripciones:
            if inscripcion.estado != "Confirmada":
                resultados["ignoradas"].append(inscripcion.id)
                continue
            
            presente = inscripcion.estudiante_id in asistentes
            inscripcion.registrar_asistencia(fecha, presente)
            self.inscripcion_repo.guardar(inscripcion)
            resultados["registradas"].append(inscripcion.id)
        
        return resultados