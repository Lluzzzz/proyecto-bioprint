PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS caso_estudio (
 id TEXT PRIMARY KEY, nombre TEXT NOT NULL, modelo_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS escenario (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 caso_id TEXT NOT NULL REFERENCES caso_estudio(id),
 tipo TEXT NOT NULL CHECK (tipo IN ('NORMAL','ESTRES','MAL_CONDICIONADO')),
 parametros_json TEXT NOT NULL,
 fuente_datos TEXT NOT NULL DEFAULT 'sintético'
);
CREATE TABLE IF NOT EXISTS simulacion (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 escenario_id INTEGER NOT NULL REFERENCES escenario(id),
 fecha TEXT NOT NULL,
 equipo TEXT,
 estado TEXT NOT NULL DEFAULT 'COMPLETADA',
 entrada_json TEXT NOT NULL,
 resultado_json TEXT NOT NULL,
 sha256_resultado TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ejecucion_metodo (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 simulacion_id INTEGER NOT NULL REFERENCES simulacion(id) ON DELETE CASCADE,
 metodo TEXT NOT NULL, tolerancia REAL, paso REAL,
 max_iter INTEGER, iteraciones INTEGER, convergio INTEGER NOT NULL,
 valor REAL, residual REAL, error_abs REAL, error_rel REAL
);
CREATE TABLE IF NOT EXISTS iteracion_resultado (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 ejecucion_id INTEGER NOT NULL REFERENCES ejecucion_metodo(id) ON DELETE CASCADE,
 numero INTEGER NOT NULL, aproximacion_json TEXT NOT NULL,
 residual REAL, error_abs REAL, error_rel REAL
);
CREATE TABLE IF NOT EXISTS resultado_resumen (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 simulacion_id INTEGER NOT NULL REFERENCES simulacion(id) ON DELETE CASCADE,
 referencia_json TEXT NOT NULL,
 metricas_json TEXT NOT NULL,
 interpretacion_numerica TEXT NOT NULL,
 interpretacion_problema TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_simulacion_fecha ON simulacion(fecha);
CREATE INDEX IF NOT EXISTS idx_escenario_caso ON escenario(caso_id,tipo);
