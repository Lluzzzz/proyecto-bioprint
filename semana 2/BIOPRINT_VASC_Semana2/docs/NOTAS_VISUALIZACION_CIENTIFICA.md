# BIOPRINT-VASC — Fundamento matemático del visualizador de tejido (v2.2)

## Qué representa realmente el dibujo

La pantalla muestra un **corte esquemático bidimensional** de un hidrogel con microcanales paralelos ideales. Se visualizan células dibujadas artificialmente y partículas decorativas dentro de los canales; no se calculan fuerzas sobre células ni su viabilidad.

**Los colores sí están conectados a un cálculo matemático reproducible.** Cada punto de la imagen recibe un valor de la solución analítica de un problema **unidimensional** de difusión-reacción, repetida periódicamente a través de un corte 2D. No se resuelve una PDE bidimensional ni una simulación CFD.

## Modelo continuo

\[
-D\frac{d^2 C}{dx^2}+kC=0,
\qquad C(0)=C_0=1,\qquad C'(L)=0.
\]

Con `D=0.002 mm²/s`, `k=0.04 s⁻¹`, semidistancia `L=s/2`, `s` separación entre dos canales:

\[
C(x)=C_0\,\frac{\cosh(\sqrt{k/D}(L-x))}{\cosh(\sqrt{k/D}L)},
\quad C_{\min}=\frac{C_0}{\cosh(\sqrt{k/D}L)}.
\]

La pantalla representa una ventana física fija de `2,40 mm` de altura; los canales se ubican en `s/2, 3s/2, 5s/2, ...` mm dentro de esa ventana. El valor de concentración de cada píxel depende exclusivamente de su distancia al canal más cercano, calculada a partir del mismo perfil 1D. Así, **al aumentar la separación se ven menos canales en el mismo espacio y disminuye la concentración mínima**.

## Umbral exploratorio, SIN significado clínico

El usuario ajusta un umbral ilustrativo `T` (inicialmente 0.60). Para `0 < T < C0`, si `C_min < T < C0`, la fracción de una celda periódica ideal con concentración inferior a ese valor es:

\[
 f_{C<T}=\frac{\operatorname{arcosh}\left[(T/C_0)\cosh(\sqrt{k/D}L)\right]}{\sqrt{k/D}L}.
\]

Si `T <= C_min`, esa fracción es 0; si `T >= C0`, es 1. La cifra **es una fracción espacial matemática**, no un porcentaje de células muertas, vivas, dañadas ni protegidas. Tampoco corresponde necesariamente al porcentaje exacto de píxeles de la ventana si contiene una celda periódica incompleta en los bordes.

## Pruebas numéricas y ejemplos

| Separación s | Semidistancia L | C mínimo calculado | Fracción C<0.60 |
|---|---|---|---|
| 0.30 mm | 0.15 mm | 0.8106584828525429 | 0% |
| 0.80 mm | 0.40 mm | 0.32521666668732585 | 68.3342118347406% |

El archivo `tests/test_oxygen_visual.js` verifica condiciones de frontera, valor analítico, periodicidad y fracción de área mediante un muestreo numérico independiente. La prueba visual `tests/browser_qa_visual.py` verifica cambios en la web y produce capturas de referencia, usando respuestas simuladas para las API. **Las pruebas HTTP, de SQLite y del motor de semana 2 son independientes** y están en `tests/test_*.py`.

## Qué se puede afirmar en la exposición

- «Al aumentar la separación entre los canales, el modelo predice menores concentraciones en la región media».
- «La visualización cambia a partir de ecuaciones; el color de cada franja procede de un valor calculado».
- «Las células están dibujadas para interpretar la sección, pero no estamos simulando su supervivencia».
- «La geometría, difusividad y consumo efectivos necesitan mediciones de laboratorio y modelos 2D/3D reales para conclusiones de diseño clínico».
