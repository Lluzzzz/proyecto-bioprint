# Evidencias de la rúbrica: semana 1 (6 puntos)

| Requisito del documento original | Evidencia y estado |
|---|---|
| Cuatro casos y relación modelos–métodos | 4 tarjetas en `index.html`, fórmulas y descripción en `README.md`. **Planteados, no programados integralmente.** |
| Sistemas lineales y referencia directa | `src/motor.js`: Jacobi, Gauss-Seidel, LU, CG y referencia directa. **Funcional.** |
| Teoría de errores transversal | Error absoluto, relativo, porcentual, residuales, condición y prueba de perturbación en el motor. **Funciona sobre el primer experimento; se extenderá a los 4 casos.** |
| Tres escenarios en ≥1 caso | NORMAL, ESTRÉS, MAL CONDICIONADO sobre modelo del caso 4. **Funcional.** |
| Escenarios definidos para otros tres casos | Descritos en el proyecto; falta la tabla completa de entradas por escenario y su validación. **Parcial**. |
| Web con cuatro módulos visibles | `index.html`. **Funcional.** |
| DER inicial | `docs/DER.mmd` y `docs/modelo_datos.sql`. **Diseñados.** |
| Repositorio con README | `README.md` incluido. **Pendiente de subir a GitHub.** |
| Avance PDF con ejemplos manuales, matrices y errores | **Debe acompañar este paquete como archivo externo.** No asumir cumplido con la web. |

## Riesgos académicos a resolver antes de presentar

- La consigna obliga **SIMTELE-RISK y casos de Mi Teleférico**. Obtener autorización docente por escrito o mantener los casos originales.
- El experimento principal es un modelo 1D de oxígeno con parámetros sintéticos, no una reconstrucción real de datos de sensores: explicar su función como calibración y referencia, y completar interpolación en semana 2.
- En S1, el documento pide teoría de errores *transversal*. La primera demostración es completa para el modelo de oxígeno, pero falta extender la instrumentación de errores a todos los casos en semanas 2 y 3.
- La base de datos todavía no guarda resultados; exportar un JSON **no sustituye** la persistencia exigida para la semana 2.
