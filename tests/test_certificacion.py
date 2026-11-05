import unittest

from src.application.certificacion_service import CertificacionService
from src.domain.grupo import Grupo
from src.domain.inscripcion import Inscripcion
from src.infrastructure.repositorios_memoria import (
    GrupoRepositoryMemoria,
    InscripcionRepositoryMemoria,
)


class TestCertificacion(unittest.TestCase):
    def setUp(self):
        self.grupo_repo = GrupoRepositoryMemoria()
        self.insc_repo = InscripcionRepositoryMemoria()
        
        self.grupo = Grupo("GRP-01", "CUR-01", "INST-01", 5)
        self.grupo_repo.guardar(self.grupo)
        
        self.service = CertificacionService(self.grupo_repo, self.insc_repo)
    
    def test_estudiante_elegible(self):
        inscripcion = Inscripcion("INS-01", "EST-01", "GRP-01")
        inscripcion.estado = "Confirmada"
        inscripcion.registrar_evaluacion("Examen 1", 80)
        inscripcion.registrar_evaluacion("Examen 2", 90)
        inscripcion.registrar_asistencia("2026-01-01", True)
        inscripcion.registrar_asistencia("2026-01-02", True)
        inscripcion.registrar_asistencia("2026-01-03", True)
        inscripcion.registrar_asistencia("2026-01-04", True)
        inscripcion.registrar_asistencia("2026-01-05", False)  # 80% asistencia
        
        self.insc_repo.guardar(inscripcion)
        
        self.grupo.finalizar()
        resultados = self.service.validar_certificacion("GRP-01")
        
        self.assertIn("INS-01", resultados["elegibles"])
    
    def test_estudiante_no_elegible_por_calificacion(self):
        inscripcion = Inscripcion("INS-02", "EST-02", "GRP-01")
        inscripcion.estado = "Confirmada"
        inscripcion.registrar_evaluacion("Examen 1", 50)  # Reprobado
        inscripcion.registrar_asistencia("2026-01-01", True)
        inscripcion.registrar_asistencia("2026-01-02", True)
        
        self.insc_repo.guardar(inscripcion)
        
        self.grupo.finalizar()
        resultados = self.service.validar_certificacion("GRP-01")
        
        self.assertEqual(len(resultados["no_elegibles"]), 1)
        self.assertEqual(resultados["no_elegibles"][0]["motivo"], "Calificación")
    
    def test_estudiante_no_elegible_por_asistencia(self):
        inscripcion = Inscripcion("INS-03", "EST-03", "GRP-01")
        inscripcion.estado = "Confirmada"
        inscripcion.registrar_evaluacion("Examen 1", 90)
        inscripcion.registrar_asistencia("2026-01-01", True)
        inscripcion.registrar_asistencia("2026-01-02", False)
        inscripcion.registrar_asistencia("2026-01-03", False)  # 33% asistencia
        
        self.insc_repo.guardar(inscripcion)
        
        self.grupo.finalizar()
        resultados = self.service.validar_certificacion("GRP-01")
        
        self.assertEqual(resultados["no_elegibles"][0]["motivo"], "Asistencia")
    
    def test_grupo_no_finalizado(self):
        with self.assertRaises(ValueError) as ctx:
            self.service.validar_certificacion("GRP-01")
        self.assertIn("no está finalizado", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()