-- ============================================================
-- PASO 1: Ejecutar este archivo PRIMERO en Supabase SQL Editor
-- Crea las 4 tablas del sistema Asesor ITCJ
-- ============================================================

-- Materias
CREATE TABLE IF NOT EXISTS materias (
    clave       TEXT PRIMARY KEY,
    nombre      TEXT NOT NULL,
    semestre    INTEGER NOT NULL,
    creditos    INTEGER NOT NULL,
    afinidad    TEXT NOT NULL
);

-- Seriaciones (prerequisitos)
CREATE TABLE IF NOT EXISTS seriaciones (
    prereq      TEXT NOT NULL,
    desbloquea  TEXT NOT NULL,
    PRIMARY KEY (prereq, desbloquea),
    FOREIGN KEY (prereq)     REFERENCES materias(clave),
    FOREIGN KEY (desbloquea) REFERENCES materias(clave)
);

-- Estudiantes
CREATE TABLE IF NOT EXISTS estudiantes (
    matricula       TEXT PRIMARY KEY,
    nombre          TEXT NOT NULL,
    apellido        TEXT NOT NULL,
    pin_hash        TEXT NOT NULL,
    semestre_actual INTEGER NOT NULL,
    perfil_real     TEXT NOT NULL,
    p1 REAL, p2 REAL, p3 REAL,
    p4 REAL, p5 REAL, p6 REAL, p7 REAL
);

-- Calificaciones
CREATE TABLE IF NOT EXISTS calificaciones (
    id           SERIAL PRIMARY KEY,
    matricula    TEXT NOT NULL REFERENCES estudiantes(matricula),
    clave        TEXT NOT NULL REFERENCES materias(clave),
    calificacion REAL NOT NULL
);
