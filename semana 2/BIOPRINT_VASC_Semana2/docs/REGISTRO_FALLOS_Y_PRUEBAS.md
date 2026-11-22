# Registro de experimentos, fallos y correcciones — Semana 2

## Alcance de pruebas
- 12 combinaciones ejecutadas: 4 casos × 3 escenarios.
- Los cinco grupos metodológicos obligatorios: sistemas lineales, interpolación, raíces, integración y RK2/RK4; teoría de errores aplicada transversalmente.
- Validación mediante referencias analíticas, pruebas de algoritmos independientes y pruebas reales del servidor SQLite.

## Hallazgos científicos y fallos detectados

| Caso | Fenómeno de prueba | Evidencia/interpretación | Respuesta o corrección |
|---|---|---|---|
| Parada de extrusión | Criterio de terminación en raíz cúbica `(q₀−at)³` | Newton y secante pueden detenerse sin declarar convergencia al acercarse a una derivada nula, aunque el residual se reduzca. | Se muestra estado `No convergió`, error frente a raíz analítica y bisección como contraste; se advierte que el residual cúbico no mide directamente error en tiempo. |
| Degradación | Reescalamiento `S A S` para calibración SPD | La condición matricial aumenta aunque la solución física recuperada no cambie. | CG solamente se ejecuta sobre matrices SPD; se presenta condición y residuo. |
| Oscilaciones | Integración RK2 con paso moderado | En el caso normal, el error máximo de RK2 supera el de RK4 para la solución analítica. | Ambos resultados se grafican, con errores distintos; no se afirma que RK4 sea siempre mejor en cualquier problema. |
| Sensores | Benchmark de Runge, nodos equiespaciados | Lagrange y Newton globales muestran oscilaciones severas; el spline natural presenta menor error máximo. | Se etiqueta como benchmark numérico, no concentración fisiológica; se muestra el índice de Lebesgue aproximado. |
| Interfaz web | Algunos `input type=number` rechazaban valores nominales por incompatibilidad entre `min` y `step`. | El formulario impedía ejecutar escenarios con parámetros válidos. | Se ajustaron los pasos y mínimos; los cuatro módulos pasaron QA visual con respuestas numéricas simuladas. |
| Historial | Validación requerida tras reiniciar | No basta con variables del navegador. | API y SQLite probados: guardar, cerrar servidor, abrir nuevamente, recuperar parámetros/resultados/gráficos y repetir con SHA-256 idéntico. |
| Seguridad básica | Exposición accidental de datos SQLite mediante rutas estáticas | Un servidor de archivos sin reglas podría permitir descargar el `.sqlite3`. | Acceso `/data/` restringido (HTTP 403); servidor escucha en loopback por defecto. |

## Pruebas reproducibles

```bash
python -m unittest discover -s tests -v
python tests/test_api.py
```

Se verificaron 9 pruebas automatizadas de lógica numérica, 12 combinaciones de escenarios en el servidor y una secuencia HTTP real de guardado/reinicio/recuperación/repetición. La interfaz se ensayó con Playwright alimentado por respuestas precomputadas porque el navegador del entorno bloqueaba la navegación al servidor local; esa prueba de interfaz **no** se debe confundir con el ensayo HTTP real.

**Límites pendientes:** no existe enlace público desplegado automáticamente; no hay calibración experimental de materiales ni verificación biológica; la seguridad de un despliegue productivo requeriría autenticación, HTTPS, controles contra abuso y almacenamiento persistente administrado.


## Corrección adicional 2.1.0 tras detectar fallos de publicación

| Problema | Diagnóstico | Solución verificada |
|---|---|---|
| El servicio Python no responde en un alojamiento Render cuando se usa `python app.py` | La versión inicial escuchaba solo `127.0.0.1:8000`, pero Render usa `PORT` y requiere `0.0.0.0`. | Arranque controlado por variables `PORT`, `HOST`, `BIOPRINT_DB_PATH`, archivo `render.yaml` y `/api/health`. |
| UI desplegada sin API | GitHub Pages sirve HTML/CSS/JS pero no ejecuta el servidor Python. | Mensaje de conexión y guía de alojamiento compatible. |
| Datos de una corrida vieja guardados después de editar campos | Los parámetros cambian pero el último resultado aún estaba habilitado para guardar. | Deshabilitar guardar hasta volver a calcular. |
| Respuestas AJAX tardías entre módulos | Peticiones simultáneas pueden llegar fuera de orden. | Token de generación para descartar respuestas antiguas. |
| Archivos internos accesibles por rutas estáticas | `SimpleHTTPRequestHandler` servía cualquier archivo del directorio de proyecto salvo algunos bloqueos. | Lista de extensiones y rutas frontend permitidas, con bloqueo de fuente, SQL y SQLite. |

La ejecución completa desde navegador real local a través de Playwright puede estar bloqueada por las restricciones de red del entorno de pruebas. En ese caso se separa la comprobación HTTP/SQLite real de la prueba de interfaz con respuestas conocidas. No equivale a una prueba de despliegue externo en la cuenta del usuario.
