# BIOPRINT-VASC — Proyecto ejecutable de Semana 1

**Universidad Mayor de San Andrés — Carrera de Informática — Métodos Numéricos**  
Tema propuesto: **Modelación de la difusión y consumo de oxígeno en hidrogeles bioimpresos**, con una aplicación web y cuatro módulos matemáticos diseñados para una investigación posterior.

> **Advertencia académica decisiva:** La consigna oficial se titula **SIMTELE-RISK** y exige que sus cuatro casos se relacionen con Mi Teleférico. La adaptación a bioimpresión necesita **autorización expresa del docente**. Los cuatro casos biomédicos presentados son una propuesta, no un cambio autorizado automáticamente.

## Cómo abrir el proyecto

1. Descomprimir el ZIP. Entrar a `BIOPRINT_VASC_Proyecto_Semana1`.
2. Abrir **`index.html`** haciendo doble clic. No requiere instalación, servidor, Internet ni cuenta.
3. Elegir NORMAL, ESTRÉS o MAL CONDICIONADO. Cambiar parámetros y pulsar **Ejecutar y comparar**.
4. Revisar el gráfico, la tabla de métodos, el historial de residuos y la matriz A.
5. Pulsar **Comparar escenarios** y, si se desea, **Exportar resultados JSON**.

El JSON descargado es un archivo individual de resultados: **no constituye una base de datos persistente**. Esa función es un objetivo de la semana 2.

## Estructura

```
BIOPRINT_VASC_Proyecto_Semana1/
  index.html            Página web principal, 4 módulos visibles
  src/
    estilos.css         Presentación responsiva vino/beige
    motor.js            Modelo y cinco solucionadores numéricos
    app.js              Formularios, gráficos canvas, comparación y exportación
  tests/
    test_motor.js       Pruebas automáticas; Node.js opcional
  docs/
    DER.mmd             Modelo entidad-relación inicial
    modelo_datos.sql    Tablas futuras del historial y sus resultados
    GUIA_DEFENSA.md     Explicación y reparto de la exposición
    EVIDENCIAS.md       Lista de verificación con la consigna
    MODELOS_CUATRO_CASOS.md Definiciones y escenarios de los 4 módulos
    resultados_prueba.json Números reproducibles del primer experimento
    Informe_UMSA_Semana1.docx  Informe Word aprobado por el equipo
    Informe_UMSA_Semana1.pdf   Versión PDF para la entrega
    ANEXO_Calculos_Semana1.pdf  Operaciones y tablas verificadas
  README.md
```

## Modelo matemático de la primera semana

Por el momento, el experimento que se puede ejecutar corresponde al **caso 4 — Sensores de oxígeno**, como ejercicio de modelo espacial/calibración. El caso 4 incorporará **Lagrange, Newton y splines** en la semana 2. Los casos 1–3 muestran su planteamiento y fórmulas, pero sus algoritmos todavía no están implementados.

- Dominio 1D idealizado: `0 ≤ x ≤ L`.
- Modelo estacionario: `−D Cʺ + k C = 0`.
- Condiciones de frontera: `C(0) = C0`; `Cʹ(L) = 0`.
- Longitud L (mm), difusividad D (mm²/s), consumo k (s⁻¹), concentración relativa C (adimensional).
- Solución exacta: `C(x) = C0 cosh(√(k/D)(L−x)) / cosh(√(k/D)L)`.
- Discretización por **volúmenes finitos** con `N` celdas. Matriz tridiagonal simétrica definida positiva:
  - Primera ecuación: `(3+γ) C1 − C2 = 2 C0`.
  - Interiores: `−C(i−1) + (2+γ) Ci − C(i+1) = 0`.
  - Última ecuación: `−C(N−1) + (1+γ) CN = 0`.
  - `γ = k(L/N)² / D`.
- Cinco soluciones: Jacobi, Gauss-Seidel, descomposición LU, gradiente conjugado y referencia directa con pivoteo parcial.
- Errores en tabla: error absoluto ∞, relativo %, norma de residuo. Separado, error espacial vs. solución analítica y κ∞ de la matriz realmente resuelta.

## Escenarios predefinidos

| Escenario | Configuración | Interpretación |
|---|---|---|
| NORMAL | `L=0,15 mm; D=0,002 mm²/s; k=0,04 s⁻¹` | Modelo sintético base |
| ESTRÉS | `L=0,40 mm`; resto igual | Mayor distancia de difusión, **no** mayor condicionamiento |
| MAL CONDICIONADO | Geometría normal, cambio de variables `C=Sy`; `A'=SAS`, `b'=Sb`; `S=diag(1,0,05,0,005,1)` en N=4 | Mayor sensibilidad algebraica, **no** falla biomédica |

Con N distinto de 4 el escalamiento solo cambia las incógnitas 2 y 3; la misma definición experimental sigue siendo útil como prueba de robustez.

## Reproducibilidad

Para ejecutar pruebas automáticas (opcional):

```bash
node tests/test_motor.js
```

La prueba cubre los tres escenarios × cinco métodos, k=0, una solución conocida, sensibilidad por escalamiento, refinamiento de malla y validación de parámetros. La web calcula y muestra los resultados sin necesitar Node.

## Qué sí y qué no está implementado

**Implementado S1:** cuatro tarjetas, ecuaciones iniciales, primer modelo de oxígeno, cinco algoritmos lineales, tres escenarios del modelo, errores, condición, tablas de iteración, dos gráficos, parámetros editables y exportación JSON, DER y SQL inicial.

**No implementado S1:** algoritmos completos de detención, degradación, oscilaciones e interpolación; tres escenarios en cada módulo; base de datos conectada; guardar y recuperar un historial tras reiniciar; integración total de métodos de semana 2; despliegue público; publicación del repositorio GitHub.

El docente pide un **PDF de avance y repositorio GitHub en semana 1**. El ZIP incluye `docs/Informe_UMSA_Semana1.pdf` y un anexo de operaciones verificadas `docs/ANEXO_Calculos_Semana1.pdf`. La publicación del repositorio debe hacerse desde la cuenta del equipo.

## Referencias y límites científicos

Toda la física y los parámetros utilizados en esta demostración son **sintéticos**. La aplicación **no predice supervivencia celular**, no simula flujo sanguíneo en 3D y no sirve para diagnóstico o diseño de un implante real. Los resultados demuestran comportamientos matemáticos del modelo idealizado.
