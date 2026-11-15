-- Esquema inicial para BIOPRINT-VASC (implementación de persistencia en semana 2).
-- SQLite 3 con soporte JSON1. La web de semana 1 todavía no usa base de datos.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS caso_estudio (
    id INTEGER PRIMARY KEY,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    modelo_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS escenario (
    id INTEGER PRIMARY KEY,
    caso_id INTEGER NOT NULL REFERENCES caso_estudio(id),
    tipo TEXT NOT NULL CHECK(tipo IN ('NORMAL','ESTRES','MAL_CONDICIONADO')),
    parametros_json TEXT NOT NULL CHECK(json_valid(parametros_json)),
    fuente_datos TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS simulacion (
    id INTEGER PRIMARY KEY,
    escenario_id INTEGER NOT NULL REFERENCES escenario(id),
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ejecucion_metodo (
    id INTEGER PRIMARY KEY,
    simulacion_id INTEGER NOT NULL REFERENCES simulacion(id),
    metodo TEXT NOT NULL,
    tolerancia REAL,
    paso REAL,
    max_iter INTEGER,
    iteraciones INTEGER,
    convergio INTEGER,
    tiempo_ms REAL
);
CREATE TABLE IF NOT EXISTS iteracion_resultado (
    id INTEGER PRIMARY KEY,
    ejecucion_id INTEGER NOT NULL REFERENCES ejecucion_metodo(id),
    numero INTEGER NOT NULL,
    aproximacion_json TEXT,
    residual REAL,
    error_abs REAL,
    error_rel REAL,
    UNIQUE(ejecucion_id,numero)
);
CREATE TABLE IF NOT EXISTS resultado_resumen (
    id INTEGER PRIMARY KEY,
    ejecucion_id INTEGER UNIQUE NOT NULL REFERENCES ejecucion_metodo(id),
    referencia_json TEXT,
    valor_json TEXT NOT NULL,
    metrica_error_json TEXT,
    conclusion_numerica TEXT,
    conclusion_problema TEXT
);
