import unittest

from src.domain.value_objects import Calificacion, Cupo, PorcentajeAsistencia


class TestValueObjects(unittest.TestCase):
    def test_cupo_hay_lugar(self):
        cupo = Cupo(5, 3)
        self.assertTrue(cupo.hay_lugar())
    
    def test_cupo_lleno(self):
        cupo = Cupo(5, 5)
        self.assertFalse(cupo.hay_lugar())
    
    def test_cupo_ocupar(self):
        cupo = Cupo(5, 3)
        nuevo = cupo.ocupar()
        self.assertEqual(nuevo.ocupados, 4)
        self.assertEqual(cupo.ocupados, 3)  # Inmutable
    
    def test_cupo_excede_capacidad(self):
        with self.assertRaises(ValueError):
            Cupo(5, 6)
    
    def test_calificacion_aprueba(self):
        self.assertTrue(Calificacion(70).aprueba())
        self.assertTrue(Calificacion(100).aprueba())
        self.assertFalse(Calificacion(69).aprueba())
    
    def test_calificacion_invalida(self):
        with self.assertRaises(ValueError):
            Calificacion(101)
        with self.assertRaises(ValueError):
            Calificacion(-1)
    
    def test_porcentaje_asistencia_cumple(self):
        self.assertTrue(PorcentajeAsistencia(80).cumple_minimo())
        self.assertTrue(PorcentajeAsistencia(100).cumple_minimo())
        self.assertFalse(PorcentajeAsistencia(79).cumple_minimo())

if __name__ == "__main__":
    unittest.main()