# EduTechAcademy U5 – Pruebas automáticas y CI

**Actividad 05 · Componentes de Lógica del Negocio**

Proyecto de pruebas automáticas para el núcleo de negocio de EduTechAcademy. La entrega valida reglas del dominio mediante pruebas unitarias, pruebas de integración con SQLAlchemy y SQLite en memoria, pruebas de extremo a extremo (E2E) a través del Service Layer e integración continua con GitHub Actions.

## Objetivo

Comprobar que las reglas de certificación, cupo, inscripción y pago se mantengan al realizar cambios en el código, con pruebas reproducibles y sin utilizar datos de producción ni cobros reales.

## Instalación

Crear el entorno virtual:

```bash
python -m venv .venv
```

Activarlo en Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

En macOS/Linux:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Ejecutar toda la suite:

```bash
python -m pytest -v
```

Ejecutar por tipo de prueba:

```bash
python -m pytest tests/unit -v
python -m pytest tests/integration -v
python -m pytest tests/e2e -v
```

Revisar estilo y errores estáticos:

```bash
ruff check .
```

Medir cobertura de líneas y ramas, generar el reporte HTML y exigir al menos 80 %:

```bash
python -m pytest --cov=src --cov-branch --cov-report=term-missing --cov-report=html --cov-fail-under=80
```

El reporte HTML se genera en `htmlcov/index.html`.

## Estructura del proyecto

```text
.github/
  workflows/
    ci.yml
src/
  domain/
  application/
  infrastructure/
tests/
  unit/
  integration/
  e2e/
  conftest.py
.gitignore
pyproject.toml
requirements.txt
README.md
```

- `src/domain/`: entidades, objetos de valor, eventos y reglas del negocio.
- `src/application/`: servicios de aplicación y puertos.
- `src/infrastructure/`: persistencia y repositorios.
- `tests/unit/`: validación aislada de reglas del dominio.
- `tests/integration/`: persistencia, transacciones y restricciones con SQLite.
- `tests/e2e/`: recorrido de flujos completos a través de los servicios de aplicación.
- `.github/workflows/ci.yml`: pipeline de integración continua.

## Reglas de negocio verificadas

| Regla | Comportamiento |
|---|---|
| RB-06 / RB-07 · Certificación | Se requiere calificación mínima de 70/100 y asistencia mínima de 80 %, con el grupo finalizado. |
| RB-02 · Cupo | No se permite superar la capacidad máxima del grupo; al ocupar el último lugar se publica el evento de cupo agotado. |
| RB-03 · Pago | La inscripción se confirma cuando el pago es aprobado; un rechazo o timeout no debe confirmarla. |
| SUP-12 · Inscripción duplicada | Se rechaza una segunda inscripción activa del mismo estudiante en el mismo grupo. |
| RB-14 · Autorización | Los permisos se controlan según el rol: Estudiante, Instructor o Control Escolar. |

## Tipos de pruebas

- **Unitarias:** comprueban objetos de valor y reglas del dominio, incluidos los valores límite.
- **Integración:** comprueban el repositorio y las transacciones con SQLAlchemy y SQLite en memoria; incluyen commit, rollback y restricciones.
- **E2E:** recorren casos de uso completos mediante el Service Layer. No se utiliza navegador porque el proyecto no cuenta con interfaz gráfica.

## Herramientas

- Python y pytest para ejecutar las pruebas.
- `unittest.mock` para simular la pasarela de pagos y evitar cobros reales.
- SQLAlchemy y SQLite en memoria para las pruebas de persistencia.
- ruff para análisis estático.
- pytest-cov para medir cobertura.
- GitHub Actions para ejecutar las verificaciones en cada push y pull request a `main`.

Las dependencias del proyecto se encuentran en `requirements.txt`. La configuración de pytest está en `pyproject.toml`.

## Resultados documentados en el reporte

- 87 pruebas aprobadas.
- 90.20 % de cobertura total.
- Mínimo de cobertura configurado: 80 %.
- 31 hallazgos iniciales de ruff corregidos.
- Pipeline de CI con análisis estático y ejecución de pruebas.

Estos son los resultados consignados en el reporte de la actividad; deben volver a comprobarse al ejecutar la versión actual del repositorio.

## Integración continua

El workflow `.github/workflows/ci.yml` se activa con `push` y `pull_request` hacia la rama `main`. Ejecuta los siguientes pasos:

1. Descarga el repositorio.
2. Configura Python 3.12.
3. Instala las dependencias.
4. Ejecuta `ruff check .`.
5. Ejecuta pytest con cobertura mínima del 80 %.

## Limitaciones y pendientes

- SQLite en memoria no sustituye las pruebas contra el motor de base de datos de producción.
- La pasarela de pagos se simula con mocks; falta probar contra el sandbox del proveedor.
- No hay pruebas E2E con navegador o interfaz gráfica.
- Falta ampliar las pruebas de concurrencia.
- Los supuestos de negocio indicados en el reporte requieren confirmación con el docente o stakeholder.

## Equipo

- Valeria Ordaz García
- Luis José Mendoza Serrano
- Omar Alejandro Salazar Castro

**Curso:** Componentes de Lógica del Negocio  
**Actividad:** 05 – EduTechAcademy  
**Fecha del reporte:** 04/11/2026
