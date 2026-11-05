import unittest

from src.application.inscripcion_service import InscripcionService
from src.domain.curso import Curso
from src.domain.estudiante import Estudiante
from src.domain.grupo import Grupo
from src.infrastructure.repositorios_memoria import (
    CursoRepositoryMemoria,
    EstudianteRepositoryMemoria,
    GrupoRepositoryMemoria,
    InscripcionRepositoryMemoria,
)


class TestInscripcion(unittest.TestCase):
    def setUp(self):
        self.est_repo = EstudianteRepositoryMemoria()
        self.curso_repo = CursoRepositoryMemoria()
        self.grupo_repo = GrupoRepositoryMemoria()
        self.insc_repo = InscripcionRepositoryMemoria()
        
        self.estudiante = Estudiante("EST-01", "Juan Pérez", "juan@mail.com")
        self.curso = Curso("CUR-01", "Python Básico", "En línea", 1000.0, [])
        self.grupo = Grupo("GRP-01", "CUR-01", "INST-01", 2)
        
        self.est_repo.guardar(self.estudiante)
        self.curso_repo.guardar(self.curso)
        self.grupo_repo.guardar(self.grupo)
        
        self.service = InscripcionService(
            self.est_repo, self.curso_repo, self.grupo_repo, self.insc_repo
        )
    
    def test_inscripcion_exitosa(self):
        inscripcion = self.service.inscribir("EST-01", "GRP-01")
        self.assertEqual(inscripcion.estado, "Pendiente")
        self.assertEqual(self.grupo.cupo.ocupados, 1)
    
    def test_inscripcion_sin_cupo(self):
        self.est_repo.guardar(Estudiante("EST-02", "Ana López", "ana@mail.com"))
        self.est_repo.guardar(Estudiante("EST-03", "Luis Ruiz", "luis@mail.com"))
        self.service.inscribir("EST-01", "GRP-01")
        self.service.inscribir("EST-02", "GRP-01")

        with self.assertRaises(ValueError) as ctx:
            self.service.inscribir("EST-03", "GRP-01")
        self.assertIn("No hay cupo", str(ctx.exception))
    
    def test_pago_confirma_inscripcion(self):
        inscripcion = self.service.inscribir("EST-01", "GRP-01")
        inscripcion = self.service.registrar_pago(inscripcion.id, 1000.0)
        self.assertEqual(inscripcion.estado, "Confirmada")
    
    def test_pago_monto_incorrecto(self):
        inscripcion = self.service.inscribir("EST-01", "GRP-01")
        with self.assertRaises(ValueError):
            self.service.registrar_pago(inscripcion.id, 500.0)

if __name__ == "__main__":
    unittest.main()