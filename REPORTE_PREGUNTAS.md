# Reporte de preguntas – EduTechAcademy U5

**Actividad 05 · Componentes de Lógica del Negocio**

Este archivo reúne las preguntas y respuestas de la sección **5. Preguntas del reporte** del documento de la Unidad 5.

## 1. ¿En qué se distinguen las pruebas unitarias, de integración y E2E?

La unitaria prueba una regla aislada (por ejemplo `Calificacion.aprueba()`); la de integración prueba que varias piezas funcionen juntas (dominio, repositorio y base de datos); la E2E recorre un caso de uso completo. Se prefieren muchas unitarias porque son rápidas y señalan con precisión dónde está el error; las E2E se reservan para pocos flujos críticos.

## 2. ¿Por qué usar Arrange–Act–Assert?

Separa preparar, ejecutar y comprobar. Cada prueba verifica una sola acción, es fácil de leer y, cuando falla, el bloque que falló indica si el problema estaba en los datos, en la operación o en el resultado.

## 3. ¿Por qué en TDD hay que ver fallar la prueba primero?

Porque una prueba que nunca ha fallado no demuestra que pueda detectar el error. Ver el rojo confirma que la prueba comprueba lo que dice y que el código nuevo es la causa de que pase.

## 4. ¿Cómo se prueba la persistencia sin tocar datos de producción?

Con una base SQLite en memoria creada y destruida en cada prueba mediante una fixture, sin leer nunca la conexión de producción. La limitación es que SQLite no es idéntico al motor de producción (tipos, bloqueos, comportamiento de restricciones), por lo que se declara que falta probar contra el motor real.

## 5. ¿Para qué sirve un mock y qué no demuestra?

Permite controlar la respuesta de un servicio externo (aprobado, rechazado, timeout) sin cobrar de verdad. No demuestra que la integración real funcione: si la pasarela cambia su contrato, el mock seguirá pasando. Eso requiere pruebas contra un ambiente de pruebas (sandbox) del proveedor.

## 6. ¿Una cobertura del 100 % garantiza que el sistema es correcto?

No. Mide qué código se ejecutó, no si las aserciones son suficientes ni si se probaron los casos límite. Sirve para descubrir código que nunca se prueba.

## 7. ¿Qué aporta el pipeline de CI?

Ejecuta las mismas verificaciones en una máquina limpia en cada cambio. Evita que alguien suba código sin correr las pruebas y deja evidencia pública de quién rompió qué y cuándo se arregló.

---

**Fuente:** Reporte de la Unidad 5 de EduTechAcademy, sección 5, “Preguntas del reporte”.
