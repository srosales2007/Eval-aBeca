:- encoding(utf8).

/*  ==========================================================
    EvalúaBeca - Motor de reglas (paradigma logico)
    ----------------------------------------------------------
    Las reglas deducen, a partir de los hechos de una solicitud
    y de los criterios del reglamento (criterios.pl):
      - que criterios cumple y cuales no (con valor y umbral),
      - el dictamen (aprobada / rechazada),
      - el tipo de beca (total / parcial / ninguna) y su motivo.
    ========================================================== */

:- ensure_loaded(criterios).

% Hechos de cada solicitud: se agregan y retiran en tiempo de
% ejecucion desde Python (modulo de integracion).
:- dynamic promedio/2, ingreso_hogar/2, miembros_hogar/2,
           materias/2, tiene_condicion/2.

/* ---------- Gestion de los hechos de una solicitud ---------- */

registrar_solicitud(S, Promedio, Ingreso, Miembros, Materias, Condiciones) :-
    limpiar_solicitud(S),
    assertz(promedio(S, Promedio)),
    assertz(ingreso_hogar(S, Ingreso)),
    assertz(miembros_hogar(S, Miembros)),
    assertz(materias(S, Materias)),
    forall(member(C, Condiciones), assertz(tiene_condicion(S, C))).

limpiar_solicitud(S) :-
    retractall(promedio(S, _)),
    retractall(ingreso_hogar(S, _)),
    retractall(miembros_hogar(S, _)),
    retractall(materias(S, _)),
    retractall(tiene_condicion(S, _)).

/* ---------- Reglas auxiliares ---------- */

ingreso_per_capita(S, IPC) :-
    ingreso_hogar(S, Ingreso),
    miembros_hogar(S, Miembros),
    Miembros > 0,
    IPC is round(Ingreso / Miembros).

condicion_aplicada(S, C) :-
    tiene_condicion(S, C),
    condicion_especial(C).

condicion_no_reconocida(S, C) :-
    tiene_condicion(S, C),
    \+ condicion_especial(C).

tiene_condicion_valida(S) :-
    condicion_aplicada(S, _), !.

% Con una condicion especial reconocida el promedio exigido baja.
promedio_requerido(S, Minimo) :-
    tiene_condicion_valida(S), !,
    umbral(promedio_minimo_condicion, Minimo).
promedio_requerido(_, Minimo) :-
    umbral(promedio_minimo, Minimo).

/* ---------- Valor de cada criterio frente a su umbral ---------- */

% valor_criterio(Solicitud, Criterio, ValorObtenido, Umbral)
valor_criterio(S, promedio, P, Minimo) :-
    promedio(S, P),
    promedio_requerido(S, Minimo).
valor_criterio(S, ingreso, IPC, Maximo) :-
    ingreso_per_capita(S, IPC),
    umbral(ingreso_per_capita_maximo, Maximo).
valor_criterio(S, carga_academica, N, Minimo) :-
    materias(S, N),
    umbral(materias_minimas, Minimo).

/* ---------- Cumplimiento ---------- */

cumple(S, promedio)        :- valor_criterio(S, promedio, V, U),        V >= U.
cumple(S, ingreso)         :- valor_criterio(S, ingreso, V, U),         V =< U.
cumple(S, carga_academica) :- valor_criterio(S, carga_academica, V, U), V >= U.

incumple(S, C) :-
    criterio(C),
    \+ cumple(S, C).

% Trazabilidad: una solucion por criterio (se recorre por backtracking)
resultado_criterio(S, C, Estado, Valor, Umbral) :-
    criterio(C),
    valor_criterio(S, C, Valor, Umbral),
    (   cumple(S, C)
    ->  Estado = cumple
    ;   Estado = no_cumple
    ).

/* ---------- Dictamen ---------- */

aprobada(S) :-
    forall(criterio(C), cumple(S, C)).

tipo_beca(S, total) :-
    aprobada(S),
    (   ingreso_per_capita(S, IPC),
        umbral(ingreso_per_capita_prioridad, Prioridad),
        IPC =< Prioridad
    ;   tiene_condicion_valida(S)
    ), !.
tipo_beca(S, parcial) :-
    aprobada(S), !.
tipo_beca(_, ninguna).

% motivo_tipo(S, Motivo): por que se asigno ese tipo de beca
motivo_tipo(S, ingreso_prioritario) :-
    aprobada(S),
    ingreso_per_capita(S, IPC),
    umbral(ingreso_per_capita_prioridad, Prioridad),
    IPC =< Prioridad.
motivo_tipo(S, condicion_especial) :-
    aprobada(S),
    tiene_condicion_valida(S).

dictamen(S, aprobada, Tipo) :-
    aprobada(S), !,
    tipo_beca(S, Tipo).
dictamen(_, rechazada, ninguna).

/* ---------- Uso directo desde la consola de SWI-Prolog ---------- */

explicar(S) :-
    dictamen(S, D, T),
    format("Solicitud ~w -> ~w (beca ~w)~n", [S, D, T]),
    forall(resultado_criterio(S, C, E, V, U),
           format("  - ~w: ~w (valor ~w, umbral ~w)~n", [C, E, V, U])),
    forall(condicion_aplicada(S, Co),
           format("  * condicion especial aplicada: ~w~n", [Co])).
