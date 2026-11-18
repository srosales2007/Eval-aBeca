:- encoding(utf8).

/*  ==========================================================
    EvalúaBeca - Base de conocimiento: CRITERIOS DEL REGLAMENTO
    Paradigma lógico (SWI-Prolog)
    ----------------------------------------------------------
    Este archivo contiene SOLO hechos. Para ajustar los criterios
    entre un periodo y otro se modifican estos valores; no hace
    falta tocar el código Python ni las reglas de evaluacion.
    ========================================================== */

% Periodo al que aplican los criterios
periodo_vigente('III-2026').

% umbral(Nombre, Valor)
umbral(promedio_minimo,                 80).     % escala 0-100
umbral(promedio_minimo_condicion,       75).     % si tiene condicion especial
umbral(ingreso_per_capita_maximo,   250000).     % colones por persona
umbral(ingreso_per_capita_prioridad, 120000).    % por debajo: beca total
umbral(materias_minimas,                 3).     % carga academica minima

% Criterios que el motor debe revisar en toda solicitud
criterio(promedio).
criterio(ingreso).
criterio(carga_academica).

% Condiciones especiales reconocidas por el reglamento
condicion_especial(discapacidad).
condicion_especial(jefe_de_hogar).
condicion_especial(zona_vulnerable).
condicion_especial(primera_generacion).
