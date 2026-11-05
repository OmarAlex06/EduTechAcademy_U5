from src.domain.inscripcion import Inscripcion


class InscripcionService:
    def __init__(self, estudiante_repo, curso_repo, grupo_repo, inscripcion_repo):
        self.estudiante_repo = estudiante_repo
        self.curso_repo = curso_repo
        self.grupo_repo = grupo_repo
        self.inscripcion_repo = inscripcion_repo
    
    def inscribir(self, estudiante_id: str, grupo_id: str) -> Inscripcion:
        estudiante = self.estudiante_repo.buscar(estudiante_id)
        if not estudiante:
            raise ValueError("Estudiante no encontrado")
        
        grupo = self.grupo_repo.buscar(grupo_id)
        if not grupo:
            raise ValueError("Grupo no encontrado")
        
        curso = self.curso_repo.buscar(grupo.curso_id)
        
        # Verificar requisitos (simplificado)
        if curso.requisitos and estudiante_id not in curso.requisitos:
            # En un caso real, aquí se verificaría con PoliticalInscripcion
            pass
        
        # El dominio decide si hay cupo
        grupo.ocupar_lugar(estudiante_id)
        
        # Crear inscripción en estado Pendiente
        inscripcion = Inscripcion(
            id=f"INS-{estudiante_id}-{grupo_id}",
            estudiante_id=estudiante_id,
            grupo_id=grupo_id
        )
        
        self.grupo_repo.guardar(grupo)
        self.inscripcion_repo.guardar(inscripcion)
        
        return inscripcion
    
    def registrar_pago(self, inscripcion_id: str, monto: float) -> Inscripcion:
        inscripcion = self.inscripcion_repo.buscar(inscripcion_id)
        if not inscripcion:
            raise ValueError("Inscripción no encontrada")
        
        grupo = self.grupo_repo.buscar(inscripcion.grupo_id)
        curso = self.curso_repo.buscar(grupo.curso_id)
        
        # El dominio valida el monto
        inscripcion.confirmar_pago(monto, curso.precio)
        
        self.inscripcion_repo.guardar(inscripcion)
        return inscripcion
    
    def cambiar_grupo(self, inscripcion_id: str, nuevo_grupo_id: str, motivo: str, autorizado_por: str) -> Inscripcion:
        inscripcion = self.inscripcion_repo.buscar(inscripcion_id)
        grupo_anterior = self.grupo_repo.buscar(inscripcion.grupo_id)
        grupo_nuevo = self.grupo_repo.buscar(nuevo_grupo_id)
        
        if not grupo_nuevo:
            raise ValueError("Grupo destino no encontrado")
        
        # Ocupar lugar en el nuevo grupo
        grupo_nuevo.ocupar_lugar(inscripcion.estudiante_id)
        # Liberar lugar en el anterior
        grupo_anterior.liberar_lugar()
        # Registrar el cambio
        inscripcion.cambiar_grupo(nuevo_grupo_id, autorizado_por, motivo)
        
        self.grupo_repo.guardar(grupo_nuevo)
        self.grupo_repo.guardar(grupo_anterior)
        self.inscripcion_repo.guardar(inscripcion)
        
        return inscripcion