# EvalúaBeca — Motor híbrido de evaluación de solicitudes de beca

Proyecto del curso **SC-250 Paradigmas de Programación** · Universidad Fidélitas · Grupo #5

Integrantes: Santiago Artavia Villanueva · Sebastián Ortega Di Capua · Santiago Rosales Arceyut · Kevin Yang Li

EvalúaBeca recibe solicitudes de beca, las valida y las evalúa contra los criterios del reglamento
escritos como hechos y reglas en Prolog. Cada dictamen explica qué criterios se cumplieron y cuáles no.

## Paradigmas

| Paradigma | Dónde |
|---|---|
| Orientado a objetos | `app/dominio`, `app/servicios`, `app/integracion`, `app/repositorio` |
| Lógico | `prolog/criterios.pl`, `prolog/reglas.pl` |
| Funcional | `app/funcional` |
| Orientado a eventos | `web/app.js` |

## Requisitos

- Python 3.10 o superior
- SWI-Prolog 9.x ([descarga](https://www.swi-prolog.org/download/stable)); en Windows, marque la opción de agregarlo al PATH

## Instalación y ejecución

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    ·    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Aplicación web: http://127.0.0.1:8000
- Documentación de la API (Swagger): http://127.0.0.1:8000/docs

## Pruebas

```bash
python -m pytest -v
```

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
│   ├── repositorio/    # Almacenamiento de solicitudes
│   ├── servicios/      # GestorSolicitudes (capa de negocio)
│   └── main.py         # API FastAPI
├── prolog/             # Base de conocimiento (lógico)
├── web/                # Interfaz HTML/CSS/JS (eventos)
└── tests/              # Pruebas con pytest
```
