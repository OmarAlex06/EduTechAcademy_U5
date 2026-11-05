from src.domain.inscripcion import Inscripcion


class CertificacionService:
    def __init__(self, grupo_repo, inscripcion_repo):
        self.grupo_repo = grupo_repo
        self.inscripcion_repo = inscripcion_repo
    
    def validar_certificacion(self, grupo_id: str) -> dict:
        grupo = self.grupo_repo.buscar(grupo_id)
        if not grupo:
            raise ValueError("Grupo no encontrado")
        
        if grupo.estado != "Finalizado":
            raise ValueError(f"El grupo no está finalizado. Estado actual: {grupo.estado}")
        
        inscripciones = self.inscripcion_repo.listar_por_grupo(grupo_id)
        resultados = {"elegibles": [], "no_elegibles": []}
        
        for inscripcion in inscripciones:
            if inscripcion.estado != "Confirmada":
                continue
            
            inscripcion.evaluar_certificacion(grupo_finalizado=True)
            
            if inscripcion.certificacion.estado == "Elegible":
                resultados["elegibles"].append(inscripcion.id)
            else:
                resultados["no_elegibles"].append({
                    "id": inscripcion.id,
                    "motivo": inscripcion.certificacion.motivo_no_elegibilidad
                })
            
            self.inscripcion_repo.guardar(inscripcion)
        
        return resultados
    
    def emitir_certificado(self, inscripcion_id: str) -> Inscripcion:
        inscripcion = self.inscripcion_repo.buscar(inscripcion_id)
        if not inscripcion:
            raise ValueError("Inscripción no encontrada")
        
        grupo = self.grupo_repo.buscar(inscripcion.grupo_id)
        if grupo.estado != "Finalizado":
            raise ValueError("El grupo no está finalizado")
        
        inscripcion.emitir_certificado()
        self.inscripcion_repo.guardar(inscripcion)
        return inscripcion