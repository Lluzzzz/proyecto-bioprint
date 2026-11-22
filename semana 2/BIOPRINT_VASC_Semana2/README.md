# BIOPRINT-VASC — Semana 2 · Visualizador de tejidos v2.2

**UMSA · Carrera de Informática · Métodos Numéricos**  
Proyecto aprobado por el docente, con aplicación académica a bioimpresión 3D. **Datos sintéticos, sin conexión a equipos reales ni uso clínico.**

## Novedades visuales y científicas (v2.2)

- Nueva portada con una sección de **tejido bioimpreso simulada**: microcanales, células esquemáticas y distribución de oxígeno recalculada al mover un control deslizante.
- **Una ventana física fija de 2,40 mm:** la separación de los canales modifica cuántos canales aparecen en el mismo campo de observación. El color de cada franja se obtiene de la solución analítica 1D, repetida periódicamente en un corte 2D.
- Dos modos: **Gradiente** y **Células**. Se incluyen curva `C(x)`, concentración mínima, comparación directa de referencia / diseño explorado y fracción bajo un umbral *exclusivamente ilustrativo* (no clínico).
- Archivos nuevos: `src/oxygen_model.js`, `src/visual.js`, `tests/test_oxygen_visual.js`, `tests/browser_qa_visual.py`, `docs/NOTAS_VISUALIZACION_CIENTIFICA.md`.
- **No es una PDE 2D ni predice supervivencia celular**. Los métodos y el backend de la semana 2 permanecen separados e intactos.
- Instrucciones de publicación: `docs/GUIA_SUBIR_A_GITHUB_Y_RENDER.md`.

## Correcciones anteriores conservadas (v2.1.0)

- **Arranque en Render corregido:** el servidor detecta `PORT` y cambia a `0.0.0.0` cuando está configurada esa variable. En local conserva `127.0.0.1:8000` por seguridad.
- Nuevo `render.yaml` para publicar como **Web Service Python**, no como página estática de GitHub Pages.
- Diagnóstico de conexión visible: la web te avisa cuando se ha publicado sin el servidor Python y los botones de simulación no pueden funcionar.
- El resultado se invalida al editar parámetros; ya no se guarda accidentalmente un experimento antiguo.
- Protección ante respuestas atrasadas al cambiar rápidamente de módulo.
- Acceso HTTP limitado a los archivos del frontend, bloqueando bases de datos, código fuente, pruebas y documentos internos.
- En Render gratuito, el historial SQLite se considera **temporal**. Para conservación duradera se necesita un almacenamiento persistente.

### ¿Por qué fallaba al subirla?

**GitHub Pages no puede ejecutar Python ni SQLite.** Si se publicó allí `index.html`, se verá el diseño pero fallarán `/api/simulate` y `/api/save`. Si se desplegó en Render usando solo `python app.py`, la versión anterior escuchaba en `127.0.0.1:8000` y no en `0.0.0.0:$PORT`, provocando errores de conexión o de detección del puerto. La nueva versión detecta el entorno automáticamente.

### Publicar en Render con el nuevo ZIP

1. Sube **el contenido extraído** de `BIOPRINT_VASC_Semana2_CORREGIDO` a GitHub, conservando `app.py`, `render.yaml`, `index.html`, `src/`, `numericos.py`, `docs/`, `tests/` en la **misma carpeta de la raíz** de ese repositorio.
2. En Render elige **New → Blueprint** y conecta el repositorio con el archivo `render.yaml` en su raíz. Si prefieres Web Service manual, usa `Runtime=Python`, `Build Command=python -m compileall -q app.py numericos.py`, `Start Command=python app.py`, `Health Check=/api/health`.
3. Si no puedes reorganizar la raíz del repositorio anterior y colocaste los archivos en una subcarpeta, configura **Root Directory** con el nombre exacto de esa subcarpeta.
4. Abre `https://TU-SERVICIO.onrender.com/api/health`: debe devolver `ok: true`, `db: SQLite`. Después abre la URL sin `/api/health`.
5. Prueba los cuatro casos, escenarios, guardado y recuperación desde un navegador externo. En una instancia gratuita de Render el archivo SQLite se puede borrar al reiniciar o redesplegar el servicio. **No afirmes que esa modalidad cumple persistencia duradera.** Para ello debes configurar un disco persistente en un servicio compatible y definir `BIOPRINT_DB_PATH` en una ubicación sobre dicho disco. Se incluye `render_persistente_ejemplo.yaml` como plantilla de un servicio de pago (no se usa por defecto).

### Errores habituales y solución

| Lo que ves | Motivo probable | Corrección |
|---|---|---|
| Aparece la web pero dice «No se puede conectar con el servidor Python» | Se abrió `index.html` directo o se subió solo a GitHub Pages. | Ejecutar `python app.py` o desplegar como Web Service Python. |
| Render indica **Port scan timeout / no open ports** | El proceso no escucha en `0.0.0.0:$PORT`. | Utilizar `app.py` corregido y Start Command `python app.py`. |
| Render indica `app.py: file not found` | Render está apuntando a otra carpeta. | Ajustar Root Directory o ubicar los archivos en la raíz del repositorio. |
| Simulaciones funcionan pero el historial desaparece después de un reinicio en Render gratis | Disco temporal. | Usar SQLite en almacenamiento persistente; mantener una copia local como respaldo. |
| No deja guardar después de cambiar un parámetro | Se invalida un resultado anterior de forma intencional. | Pulsar nuevamente «Calcular simulación» y después «Guardar». |

## Ejecución (Python 3, sin instalar paquetes)

1. Descomprime el ZIP y conserva la estructura de carpetas.
2. Abre una terminal dentro de `BIOPRINT_VASC_Semana2`.
3. Ejecuta:

```bash
python app.py
```

4. Abre **http://127.0.0.1:8000/** en Chrome, Edge o Firefox. La terminal debe permanecer abierta.
5. Elige un módulo, revisa o modifica parámetros y pulsa **Calcular simulación**.
6. Pulsa **Guardar en SQLite**. Abre **Historial**, cierra/reinicia el servidor y recupera un registro. Con **Repetir y verificar** se comprueba el SHA-256 del cálculo.

**Windows:** puedes usar `INICIAR_WINDOWS.bat` (si Python está instalado y disponible en PATH). Para cambiar el puerto: `python app.py --port 8080`.

**Importante:** **no** hagas doble clic en `index.html`: esta versión necesita el servidor local de Python para cálculos y base de datos.

La página principal incorpora un enlace a `semana1/index.html`: conserva el experimento espacial de oxígeno y los cinco solucionadores de la primera fase. Este laboratorio archivado funciona sin servidor, y el proyecto de semana 2 lo presenta como antecedente, **no como un quinto módulo obligatorio**.

## Lo que cumple la semana 2

| Criterio | Evidencia real |
|---|---|
| Interpolación | Lagrange baricéntrico, Newton por diferencias divididas y spline cúbico natural, mismos nodos, puntos ocultos y error sobre referencia independiente. |
| Raíces | Bisección, Newton-Raphson y secante sobre tiempo de detención o umbral de degradación. |
| Integración | Trapecio compuesto, Simpson 1/3 compuesto y Romberg con tabla de refinamiento y referencia. |
| EDO | RK2 de punto medio y RK4 clásico para extrusión y oscilaciones, con solución analítica. |
| Sistemas lineales S1 | Jacobi, Gauss-Seidel, LU, gradiente conjugado y referencia directa en calibración SPD 4×4 del módulo de hidrogel. |
| Escenarios | NORMAL, ESTRES y MAL_CONDICIONADO ejecutables en **los cuatro módulos**. |
| Gráficos | Dos gráficos por módulo (solución y error/convergencia), tabla de métodos y tablas por pasos o refinamiento. |
| Conclusiones | Separadas en numérica y biomédica/operativa en cada módulo. |
| BD funcional | SQLite con seis entidades, registros completos, SHA-256, recarga y repetición verificable tras reiniciar servidor. |
| Informe | `docs/Informe_Experimentos_Semana2_UMSA.pdf` y `.docx`; incidencias y pruebas en `docs/REGISTRO_FALLOS_Y_PRUEBAS.md`. |

## Módulos, parámetros y valores de referencia

1. **Parada de extrusión.** `Q'(t)=-a, V'(t)=Q(t)` durante `0≤t≤T`. Referencia `T=q₀/a`, `V(T)=q₀²/(2a)`. Parámetros `q₀` mL/s, `a` mL/s² y `n` subintervalos pares. El mal condicionado usa `f(t)=(q₀-at)³` para probar raíz múltiple; **no** representa un fallo físico.
2. **Degradación de hidrogel.** `D(t)=D₀+αt+βt²`. Referencia de raíz positiva `t*=2(u-D₀)/(α+√(α²+4β(u-D₀)))`. Calibración 4×4 SPD con solución fabricada conocida y reescalamiento SPD en el escenario mal condicionado. `t` en días; coeficientes sintéticos.
3. **Oscilaciones.** `m x''+c x'+k x=0` (vibración libre subamortiguada). Solución exacta: `e^{-αt}(x₀cos(ω_dt)+(v₀+αx₀)sin(ω_dt)/ω_d)`, `α=c/(2m)`, `ω_d=√(k/m-α²)`. Referencia para `∫x²dt` calculada con Simpson muy refinado. El mal condicionado aproxima raíces características coincidentes y **no** es necesariamente condición peligrosa.
4. **Sensores de oxígeno.** Curva de prueba normalizada `s(t)=0,65+0,25e^{-t/4}`; ruido determinista en estrés; benchmark de Runge para mal condicionamiento con nodos equiespaciados. Puntos ocultos 100, errores máximos y RMSE. El benchmark de Runge no se interpreta como concentración de oxígeno fisiológica.

## Archivos clave

```text
BIOPRINT_VASC_Semana2/
  app.py                      servidor HTTP y SQLite
  numericos.py                modelos y métodos numéricos
  index.html                  interfaz y cuatro módulos
  src/app.js                  gráficos, tablas, historia y acciones
  semana1/index.html          modelo espacial de oxígeno de la primera fase
  src/estilos.css             estilos responsivos
  docs/esquema.sql            SQL ejecutado al crear la base
  docs/DER_Semana2.mmd        diagrama entidad-relación
  docs/experimentos_12.json   12 resultados reproducibles
  docs/Informe_Experimentos_Semana2_UMSA.pdf
  docs/Informe_Experimentos_Semana2_UMSA.docx
  docs/REGISTRO_FALLOS_Y_PRUEBAS.md
  docs/GUIA_EXPOSICION_SEMANA2.md
  tests/test_semana2.py       9 pruebas de algoritmos y base
  tests/test_api.py           prueba HTTP real de reinicio y SHA-256
  tests/browser_qa_mock.py   QA de interfaz con API simulada (Playwright opcional)
  data/                       SQLite se crea al primer guardado
```

## Comprobar los algoritmos y SQLite

```bash
python -m unittest discover -s tests -v
python tests/test_api.py
```

Las pruebas de interfaz usan Playwright **solo si está instalado**:

```bash
python tests/browser_qa_mock.py
```

Este último ensayo utiliza respuestas previamente calculadas, para verificar comportamiento visual sin depender de bloqueos de navegación del entorno. **No** sustituye la prueba HTTP real (`test_api.py`).

## Persistencia y despliegue: advertencia importante

- **SQLite es real y funciona localmente**, en `data/bioprint.sqlite3`. Al cerrar y reabrir Python, el historial permanece en ese archivo.
- La aplicación puede exportarse a un servidor Python que tenga **almacenamiento persistente**. **GitHub Pages sirve archivos estáticos y no ejecuta `app.py`**, por lo que no basta con subir estos archivos a un sitio `github.io` para que el guardado y los métodos funcionen.
- No se incluye un enlace público activo: debe publicarse en el alojamiento elegido por el equipo y verificarse allí antes de entregar a la UMSA. Para una demo presencial basta abrir la dirección local mientras el programa esté en ejecución.
- El servidor, sin autenticación ni TLS, es un **prototipo académico**. Por defecto solo escucha en `127.0.0.1` y no se debe exponer públicamente sin controles adicionales.
- El esquema de SQLite y el DER se corresponden con las seis tablas en `docs/esquema.sql`. Las bases de prueba se excluyen del ZIP.

## Alcance y limitaciones

El trabajo usa parámetros supuestos y datos sintéticos. Los perfiles y estimaciones **no** validan viabilidad celular, degradación real de hidrogeles ni seguridad de un dispositivo de bioimpresión. Los escenarios numéricamente mal condicionados se identifican por su construcción matemática; no son predicciones de fallo clínico.

## Entrega oficial semana 2

El docente pide **enlace funcional de la aplicación, repositorio GitHub actualizado e informe de experimentos/fallos detectados**. Entrega el PDF de `docs/` y publica el repositorio desde tu cuenta. El enlace público debe probarse con el servidor correcto; no se crea por incluirlo dentro del ZIP.


## Guía visual (versión explicativa 2.3)

La portada incorpora cuatro ilustraciones conceptuales originales y una explicación breve para cada módulo. Dentro de cada laboratorio se presenta la pregunta física, qué simula el modelo y qué se debe observar en los resultados. La visualización de oxígeno es computacional y se calcula con `src/oxygen_model.js`; las imágenes `.webp` en `assets/` son representaciones artísticas de apoyo, **no mediciones ni simulaciones 3D**, y no intervienen en las ecuaciones ni en los resultados.

Las ilustraciones están optimizadas para web y funcionan sin conexión con terceros. Se mantiene el backend Python, SQLite, los escenarios y las tablas de error de semana 2.


## Opción adicional de alojamiento gratuito con SQLite persistente

Esta edición también incluye `wsgi.py` para PythonAnywhere (sin cambiar `numericos.py` ni `app.py`). Consultar **`GUIA_PUBLICACION_GRATUITA.md`**.
