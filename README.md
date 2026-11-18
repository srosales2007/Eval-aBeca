# EvalúaBeca — Motor híbrido de evaluación de solicitudes de beca

Proyecto del curso **SC-250 Paradigmas de Programación** · Universidad Fidélitas · Grupo #5

Integrantes: Santiago Artavia Villanueva · Sebastián Ortega Di Capua · Santiago Rosales Arceyut · Kevin Yang Li

EvalúaBeca recibe solicitudes de beca, las valida y las evalúa contra los criterios del reglamento
escritos como hechos y reglas en Prolog. Cada dictamen explica qué criterios se cumplieron y cuáles no.

## Paradigmas

| Paradigma | Dónde | Qué resuelve |
|---|---|---|
| Orientado a objetos | `app/dominio`, `app/servicios`, `app/integracion`, `app/repositorio` | Entidades, servicios y contratos intercambiables (`MotorReglas`, `RepositorioSolicitudes`) |
| Lógico | `prolog/criterios.pl`, `prolog/reglas.pl` | Criterios del reglamento como hechos; dictamen y explicación por inferencia |
| Funcional | `app/funcional` | Transformación de respuestas de Prolog, filtros del historial y estadísticas (map, filter, reduce) |
| Orientado a eventos | `web/app.js` | Interfaz guiada por listeners y eventos propios (`solicitud-evaluada`, `pestana-cambiada`) |

## Cómo correrlo (paso a paso)

### 1. Instalar lo necesario (una sola vez)

- **Python 3.10 o superior**: https://www.python.org/downloads/ — en Windows marque *Add python.exe to PATH*.
- **SWI-Prolog 9.x**: https://www.swi-prolog.org/download/stable — en Windows marque *Add swipl to the system PATH for all users*. En macOS: `brew install swi-prolog`. En Ubuntu: `sudo apt install swi-prolog`.
- **Git**: https://git-scm.com/downloads

Para comprobar, abra una terminal **nueva** y ejecute `python --version` y `swipl --version`.

### 2. Descargar el proyecto e instalar dependencias

```bash
git clone https://github.com/srosales2007/Eval-aBeca.git
cd Eval-aBeca
python -m venv .venv
```

Active el entorno virtual:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1` (si PowerShell lo bloquea: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)
- Windows (CMD): `.venv\Scripts\activate.bat`
- macOS / Linux: `source .venv/bin/activate`

```bash
pip install -r requirements.txt
```

### 3. Ejecutar

```bash
uvicorn app.main:app --reload
```

- Aplicación web: http://127.0.0.1:8000
- Documentación de la API (Swagger): http://127.0.0.1:8000/docs
- El historial se guarda en `evaluabeca.db` (SQLite). Para usar otra ruta: variable de entorno `EVALUABECA_DB`.

### Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/solicitudes` | Registra y evalúa una solicitud |
| GET | `/api/solicitudes?resultado=&tipo=&buscar=` | Historial con filtros |
| GET | `/api/solicitudes/{id}` | Detalle de una solicitud |
| GET | `/api/estadisticas` | Indicadores del historial |
| GET | `/api/criterios` | Criterios vigentes leídos de Prolog |

### Problemas comunes

- `SwiPrologNotFoundError` o `libswipl` no encontrado: SWI-Prolog no está instalado o no está en el PATH. Reinstálelo marcando la opción del PATH y abra una terminal nueva.
- En macOS con Homebrew: `brew install swi-prolog`.
- Puerto ocupado: `uvicorn app.main:app --port 8001`.
- `uvicorn` no se reconoce: el entorno virtual no está activo; actívelo o use `python -m uvicorn app.main:app --reload`.
- Para empezar con el historial vacío: detenga el servidor y borre `evaluabeca.db`.

## Pruebas

```bash
python -m pytest -v
```

## Cambiar los criterios del reglamento

Edite los hechos `umbral/2` o `condicion_especial/1` en `prolog/criterios.pl` y reinicie el servidor. No hace falta modificar el código Python.

## Consultar el motor directamente en Prolog

```bash
swipl prolog/casos_prueba.pl
?- explicar(caso_ana).
?- resultado_criterio(caso_jose, C, Estado, Valor, Umbral).
```

## Estructura

```
EvaluaBeca/
├── app/
│   ├── dominio/        # Entidades: Estudiante, Solicitud, Dictamen (POO)
│   ├── validacion/     # Esquemas Pydantic (validación de entradas)
│   ├── funcional/      # Funciones puras de transformación (funcional)
│   ├── integracion/    # MotorReglas y MotorProlog (puente PySwip)
│   ├── repositorio/    # Memoria y SQLite (historial persistente)
│   ├── servicios/      # GestorSolicitudes (capa de negocio)
│   └── main.py         # API FastAPI
├── prolog/             # Base de conocimiento (lógico)
├── docs/
│   ├── entregas/       # Documentos de los avances, entrega final y defensa
│   ├── evidencias_avance2/  # Capturas del segundo avance
│   ├── evidencias_final/    # Capturas de la versión final
│   └── diagramas/      # Arquitectura y diagrama de clases
├── web/                # Interfaz HTML/CSS/JS (eventos)
└── tests/              # Pruebas con pytest
```

## Entregas

| Entrega | Archivos en `docs/entregas/` |
|---|---|
| Avance 1 | `Grupo5_SC250_Avance1.pdf` |
| Avance 2 | `Grupo5_SC250_Avance2.pdf` / `.docx` |
| Entrega final | `Grupo5_SC250_EntregaFinal.pdf` / `.docx` |
| Defensa | `Grupo5_SC250_Defensa.pptx`, `Grupo5_SC250_Guion_Defensa.pdf` / `.docx` |
