# Defensa de la semana 1 (4 integrantes, alrededor de 5–7 minutos)

Estos son roles **sugeridos**: deben asignarse según los aportes reales de cada integrante, no afirmarse como actividades realizadas sin comprobarlo.

### 1. Carlos Illed Burgoa Orellana — Contexto y problema (60–90 s)
“Queremos investigar de forma computacional un problema importante de la bioimpresión: cómo se distribuye el oxígeno cuando aumenta la distancia entre canales. El objetivo de esta semana no es imprimir un tejido, sino desarrollar el primer modelo matemático y comprobar que nuestro código lo resuelve bien.” Explicar cuatro módulos y por qué los datos son sintéticos.

### 2. Deivid Enrique Mamani Trujillo — Formulación (60–90 s)
Explicar `−D Cʺ+kC=0`, las fronteras `C(0)=1, Cʹ(L)=0`, las unidades D mm²/s, k s⁻¹, L mm y la discretización 4×4 por volúmenes finitos. Aclarar que se obtiene una matriz SPD.

### 3. Carlos Andrés Mamani Mamani — Métodos y errores (60–90 s)
Demostrar Jacobi, Gauss-Seidel, LU y gradiente conjugado, comparados con la solución directa. Señalar diferencia entre residuo algebraico (Ax−b), error algebraico (respecto a la directa) y error espacial (respecto a la analítica).

### 4. Luz Gabriela Castañeta Tarquino — Demostración (60–90 s)
Abrir `index.html`, ejecutar NORMAL, cambiar a ESTRÉS, luego MAL CONDICIONADO. Mostrar que C mínima cambia de aproximadamente 0,810658 a 0,325217 por la distancia, mientras la concentración física de NORMAL y MAL CONDICIONADO es equivalente y solo empeora la condición matemática. Mostrar tabla, dos gráficos, DER y que los datos pueden exportarse a JSON.

### Preguntas posibles del docente

**¿Por qué usar gradiente conjugado?** Porque la matriz ensamblada es simétrica definida positiva; con matrices no SPD el método estándar no está justificado.

**¿Qué valida los resultados?** Comparación con solución continua analítica, referencia directa del mismo sistema, errores residuales y prueba de refinamiento de malla.

**¿Un valor de 0,325 significa que las células mueren?** No. Es una concentración normalizada dentro de un modelo simplificado, sin validación celular ni umbrales fisiológicos.

**¿Por qué el escenario mal condicionado no modifica el perfil?** Porque cambia las variables algebraicas `C=Sy`, no las ecuaciones físicas ni las fronteras originales.

**¿Ya guarda experimentos en una base de datos?** No: está diseñado el DER/SQL; en semana 1 la web permite exportar JSON. La persistencia se desarrollará en semana 2.

**¿Se puede usar bioimpresión en vez de Mi Teleférico?** Solo si el docente autoriza cambiar el contexto obligatorio.
