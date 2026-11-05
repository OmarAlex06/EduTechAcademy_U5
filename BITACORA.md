# Bitácora – EduTechAcademy U5

**Actividad 05 · Componentes de Lógica del Negocio**

Este archivo organiza la información de la sección **8. Uso responsable de IA (bitácora)** y los problemas y aprendizajes documentados en la sección 7 del reporte de la Unidad 5.

## Uso responsable de IA

Se usó IA para planear la actividad, revisar el borrador del reporte y generar el código base de las pruebas. Ningún resultado se aceptó sin ejecutarse: las pruebas se corrieron en nuestras computadoras y en GitHub Actions. Agregamos una fila por cada caso en que la IA propuso algo que corregimos o rechazamos.

### Registro de uso de IA

| # | Objetivo y prompt | Respuesta útil y error o supuesto detectado | Decisión del equipo |
|---|---|---|---|
| 1 | Entender el laboratorio y planear la actividad a partir de la Unidad 3. Prompt: revisar los archivos de la unidad y explicar qué se debe hacer. | Resumen de los 9 pasos del laboratorio y propuesta de 3 reglas del PIA (certificación, cupo y pago). Supuesto: la IA no pudo abrir el repositorio de la Unidad 3 (GitHub bloqueó el acceso automático), así que propuso el diseño sin ver el código original. | **Pendiente de completar por el equipo:** el reporte propone como ejemplo: “se creó el proyecto de la Unidad 5 con los mismos nombres y reglas de la Unidad 3”. |
| 2 | Revisar el borrador de este reporte y generar el código de las pruebas. Prompt: “checa si está bien, corrige los errores y ayúdame con el código paso a paso”. | Detectó fragmentos sin importaciones ni fixtures, un assert que comparaba una clase con una instancia (PagoRecibido), el riesgo de `pip freeze >` en PowerShell (UTF-16), una fixture con llaves foráneas inexistentes y la falta de evidencia E2E. Supuesto: la IA no pudo ejecutar pytest ni SQLAlchemy; solo verificó la lógica con un corredor propio. | **Pendiente de completar por el equipo:** indicar qué se aceptó, qué falló al ejecutarlo en sus computadoras y cómo se corrigió. |
| 3 | **Pendiente de documentar:** caso sugerido por la IA que el equipo corrigió o rechazó. | **Pendiente de documentar:** qué propuso la IA y por qué era incorrecto o incompleto. | **Pendiente de completar por el equipo:** decisión tomada y evidencia correspondiente. |

> Nota: los campos marcados como pendientes aparecen incompletos en el reporte original. Se conservan como pendientes para que el equipo los complete con lo que realmente ocurrió; no se inventaron decisiones ni evidencias.

## Problemas encontrados y aprendizajes

### 1. La regla nueva de TDD rompió una prueba de la Unidad 3

Al llegar a la fase verde de SUP-12 (un estudiante no puede tener dos inscripciones activas en el mismo grupo), pytest terminó con 1 fallida y 30 aprobadas. La prueba `test_inscripcion_sin_cupo` de la Unidad 3 inscribía dos veces a EST-01 para “simular otro estudiante”, y ahora el dominio lanzaba `InscripcionDuplicada`.

La causa era un error de datos en la prueba vieja, que la regla nueva dejó al descubierto. Se corrigió usando un segundo estudiante distinto en esa prueba y la suite volvió a verde.

**Aprendizaje:** una prueba de regresión puede detectar errores en las pruebas anteriores, no solo en el código, y conviene correr toda la suite en cada paso del ciclo TDD.

### 2. Hallazgos iniciales de ruff

El primer `ruff check .` reportó 31 hallazgos: importaciones desordenadas, importaciones sin usar y anotaciones anticuadas (`List`, `Optional`). 28 eran corregibles con `ruff check . --fix` y los demás se arreglaron a mano. Después se volvió a ejecutar pytest para confirmar que ninguna regla cambió, y ruff terminó con `All checks passed!`.

**Aprendizaje:** el análisis estático conviene correrlo desde el inicio y no al final.

## Secuencia general de trabajo documentada

El reporte describe este orden de trabajo:

1. Preparación del entorno.
2. Pruebas unitarias de las reglas.
3. Desarrollo guiado por pruebas (TDD) de una regla nueva.
4. Pruebas de persistencia con SQLAlchemy.
5. Simulación de la pasarela de pagos con mocks.
6. Pruebas de autorización por rol.
7. Análisis estático con ruff y cobertura con pytest-cov.
8. Integración continua (CI) con GitHub Actions.

## Verificación de resultados

El reporte documenta 87 pruebas aprobadas, 90.20 % de cobertura total y 31 hallazgos iniciales de ruff corregidos. Estos datos son los resultados consignados en el reporte; cualquier actualización debe basarse en una nueva ejecución de las pruebas.

---

**Fuente:** Reporte de la Unidad 5 de EduTechAcademy, secciones 7 y 8.
