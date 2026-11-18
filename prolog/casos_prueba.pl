:- encoding(utf8).

/*  Casos de prueba para consultar el motor sin Python.
    Uso:  swipl prolog/casos_prueba.pl
          ?- explicar(caso_ana).                                    */

:- ensure_loaded(reglas).

:- initialization(cargar_casos).

cargar_casos :-
    % Promedio alto, ingreso bajo -> aprobada, beca total
    registrar_solicitud(caso_ana,   88, 300000, 3, 5, []),
    % Ingreso medio -> aprobada, beca parcial
    registrar_solicitud(caso_luis,  85, 600000, 3, 4, []),
    % Promedio 77 con condicion especial -> aprobada, beca total
    registrar_solicitud(caso_maria, 77, 700000, 4, 4, [jefe_de_hogar]),
    % Promedio y carga insuficientes -> rechazada
    registrar_solicitud(caso_jose,  72, 900000, 3, 2, []).
