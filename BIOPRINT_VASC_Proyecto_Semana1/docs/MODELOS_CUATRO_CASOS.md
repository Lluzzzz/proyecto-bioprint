# Formulación de los cuatro casos y tres escenarios (propuesta para S1)

La consigna original **SIMTELE-RISK** obliga a desarrollar detención de cabinas, deterioro mecánico, oscilaciones por viento y sensores. Estos modelos de **bioimpresión** solo pueden sustituirlos con autorización docente. Todos los parámetros siguientes son ilustrativos, nunca tomados de un equipo clínico.

## Caso 1 · Parada de extrusión de biotinta

Pregunta: ¿qué volumen adicional se deposita si la extrusión se detiene con desaceleración de caudal constante?

`Q(t)=max(Q0−at,0)`, `dV/dt=Q(t)`. Unidades: `Q [mL/s]`, `a [mL/s²]`, `V [mL]`, `t [s]`.

Referencia analítica: `t_parada=Q0/a`, `V_parada=Q0²/(2a)`.

Métodos de semana 2: RK2, RK4, trapecio, Simpson, Romberg; raíces con bisección, Newton y secante sobre `Q0−at=0`.

- NORMAL: `Q0=0,04`, `a=0,01`, `t_parada=4 s`, `V=0,08 mL`.
- ESTRÉS: `Q0=0,06`, `a=0,01`; aumenta el volumen residual previsto.
- MAL CONDICIONADO: subproblema de raíces con pendiente `a` deliberadamente muy pequeña cerca de cero; se cuantificaría sensibilidad `|dt/da|=Q0/a²` con parámetros explícitos. No equivale a una situación clínica.

## Caso 2 · Degradación del hidrogel

`H(t)=H0+αt+βt²`, H indicador de deterioro adimensional, `t [h]`; `α [h⁻¹]`, `β [h⁻²]`. Se compara contra umbral ficticio `H_lim=0,40`.

NORMAL: `H0=0,05`, `α=0,003`, `β=0,00002`.

ESTRÉS: `H0=0,05`, `α=0,005`, `β=0,00004`.

MAL CONDICIONADO: subproblema de calibración por mínimos cuadrados, sistema SPD con matrices y columnas escaladas de forma desfavorable; se medirá κ y sensibilidad antes de usar CG, no se inventará una matriz no SPD.

Métodos de semana 2: bisección, Newton y secante para `H(t)-H_lim=0`; en un ajuste de coeficientes Jacobi, GS, LU y CG (semana 1).

## Caso 3 · Oscilación del cabezal

`x'=v`, `m v'=F(t)−c v−K x` con posición `x [m]`, masa `[kg]`, `c [N s/m]`, rigidez `K [N/m]`, fuerza `[N]`.

NORMAL: `m=0,5`, `c=0,8`, `K=60`, `F(t)=0`, `x0=0,001`, `v0=0`.

ESTRÉS: misma estructura, `F(t)=0,05 sin(12t)` N.

MAL CONDICIONADO: calibración de parámetros con mediciones casi redundantes, matriz SPD con número de condición alto para el ajuste. No se equipara oscilación grande a mal condicionamiento.

Métodos de semana 2: RK2, RK4 y trapecio, Simpson, Romberg sobre `∫x(t)² dt`. Solución libre subamortiguada como referencia analítica.

## Caso 4 · Sensores de oxígeno

Subexperimento activo semana 1: modelo de campo espacial `−D C''+k C=0` para generar un perfil de referencia sintético; métodos lineales por volúmenes finitos. NO se está reconociendo todavía una señal perdida.

NORMAL: `L=0,15 mm`, `D=0,002 mm²/s`, `k=0,04 s⁻¹`; semicanal de referencia.

ESTRÉS: `L=0,40 mm`, resto igual. El centro queda físicamente más lejos del suministro.

MAL CONDICIONADO: misma geometría normal; transformación algebraica `C=S y`, `A'=S A S`, `b'=S b`; el sistema sigue SPD y la solución física se conserva.

Se completará en semana 2 con una señal sintética de oxígeno `s(t)=0,65+0,25 exp(−t/4)` de referencia conocida. Se ocultarán puntos para comparar Lagrange, Newton y splines cúbicos, y se añadirá ruido simulado para el escenario de estrés.

## Fuente de los parámetros

Todos los números son **supuestos educativos del equipo**, no extraídos de literatura clínica ni de un protocolo real. Para un trabajo posterior habrá que justificarlos con estudios, mediciones o datos experimentales y revisar las unidades de cada parámetro.
