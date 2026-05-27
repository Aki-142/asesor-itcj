import os
import random
import hashlib
import psycopg2
from psycopg2.extras import execute_values

DB_URL = os.environ.get("DATABASE_URL")

MATERIAS = [
    ("S1-01", "Calculo Diferencial",                            1, 5, "Matematica"),
    ("S1-02", "Fundamentos de Programacion",                    1, 5, "Programacion"),
    ("S1-03", "Taller de Etica",                                1, 4, "Tronco Comun"),
    ("S1-04", "Matematicas Discretas",                          1, 5, "Matematica"),
    ("S1-05", "Taller de Administracion",                       1, 4, "Administracion"),
    ("S1-06", "Fundamentos de Investigacion",                   1, 4, "Tronco Comun"),
    ("S1-07", "Tutorias",                                       1, 4, "Tronco Comun"),
    ("S2-01", "Calculo Integral",                               2, 5, "Matematica"),
    ("S2-02", "Programacion Orientada a Objetos",               2, 5, "Programacion"),
    ("S2-03", "Contabilidad Financiera",                        2, 4, "Administracion"),
    ("S2-04", "Quimica",                                        2, 4, "Tronco Comun"),
    ("S2-05", "Algebra Lineal",                                 2, 4, "Matematica"),
    ("S2-06", "Probabilidad y Estadistica",                     2, 5, "Matematica"),
    ("S3-01", "Calculo Vectorial",                              3, 5, "Matematica"),
    ("S3-02", "Estructura de Datos",                            3, 5, "Programacion"),
    ("S3-03", "Cultura Empresarial",                            3, 4, "Administracion"),
    ("S3-04", "Investigacion de Operaciones",                   3, 4, "Administracion"),
    ("S3-05", "Sistemas Operativos",                            3, 5, "Infraestructura"),
    ("S3-06", "Fisica General",                                 3, 4, "Tronco Comun"),
    ("S4-01", "Ecuaciones Diferenciales",                       4, 5, "Matematica"),
    ("S4-02", "Metodos Numericos",                              4, 4, "Matematica"),
    ("S4-03", "Topicos Avanzados de Programacion",              4, 5, "Programacion"),
    ("S4-04", "Fundamentos de Base de Datos",                   4, 5, "Base de Datos"),
    ("S4-05", "Taller de Sistemas Operativos",                  4, 4, "Infraestructura"),
    ("S4-06", "Principios Electricos y Aplicaciones Digitales", 4, 4, "Infraestructura"),
    ("S5-01", "Desarrollo Sustentable",                         5, 4, "Administracion"),
    ("S5-02", "Fundamentos de Telecomunicaciones",              5, 5, "Redes"),
    ("S5-03", "Taller de Bases de Datos",                       5, 5, "Base de Datos"),
    ("S5-04", "Simulacion",                                     5, 4, "Administracion"),
    ("S5-05", "Fundamentos de Ingenieria de Software",          5, 5, "Administracion"),
    ("S5-06", "Arquitectura de Computadoras",                   5, 5, "Infraestructura"),
    ("S6-01", "Lenguajes y Automatas I",                        6, 5, "Programacion"),
    ("S6-02", "Redes de Computadoras",                          6, 5, "Redes"),
    ("S6-03", "Administracion de Bases de Datos",               6, 5, "Base de Datos"),
    ("S6-04", "Graficacion",                                    6, 4, "Programacion"),
    ("S6-05", "Ingenieria de Software",                         6, 5, "Administracion"),
    ("S6-06", "Lenguajes de Interfaz",                          6, 4, "Programacion"),
    ("S6-07", "Actividades Complementarias",                    6, 4, "Tronco Comun"),
    ("S7-01", "Lenguajes y Automatas II",                       7, 5, "Programacion"),
    ("S7-02", "Conmutacion y Enrutamiento de Redes de Datos",   7, 5, "Redes"),
    ("S7-03", "Taller de Investigacion I",                      7, 4, "Administracion"),
    ("S7-04", "Gestion de Proyectos de Software",               7, 4, "Administracion"),
    ("S7-05", "Sistemas Programables",                          7, 5, "Programacion"),
    ("S8-01", "Programacion Logica y Funcional",                8, 5, "Programacion"),
    ("S8-02", "Administracion de Redes",                        8, 5, "Redes"),
    ("S8-03", "Taller de Investigacion II",                     8, 4, "Administracion"),
    ("S8-04", "Programacion Web",                               8, 5, "Programacion"),
    ("S8-05", "Residencia Profesional",                         8, 10, "Tronco Comun"),
    ("S8-06", "Servicio Social",                                8, 10, "Tronco Comun"),
    ("S9-01", "Inteligencia Artificial",                        9, 5, "Programacion"),
    ("ESP-IA-01", "Machine Learning",                           10, 5, "Programacion"),
    ("ESP-IA-02", "Redes Neuronales Artificiales",              10, 5, "Programacion"),
    ("ESP-IA-03", "Mineria de Datos",                           10, 5, "Programacion"),
    ("ESP-IA-04", "Vision por Computadora",                     10, 5, "Programacion"),
    ("ESP-IA-05", "Procesamiento de Lenguaje Natural",          10, 5, "Programacion"),
    ("ESP-CS-01", "Seguridad en Redes",                         10, 5, "Redes"),
    ("ESP-CS-02", "Criptografia Aplicada",                      10, 5, "Redes"),
    ("ESP-CS-03", "Hacking Etico",                              10, 5, "Redes"),
    ("ESP-CS-04", "Forense Digital",                            10, 5, "Redes"),
    ("ESP-CS-05", "Seguridad en Aplicaciones Web",              10, 5, "Redes"),
]

SERIACIONES = [
    ("S1-01","S2-01"), ("S1-02","S2-02"), ("S1-04","S6-01"),
    ("S1-06","S7-03"), ("S2-01","S3-01"), ("S2-02","S3-02"),
    ("S2-05","S3-01"), ("S2-06","S3-04"), ("S3-01","S4-01"),
    ("S3-02","S4-03"), ("S3-03","S5-05"), ("S3-04","S5-04"),
    ("S3-05","S4-05"), ("S4-04","S5-03"), ("S4-06","S5-06"),
    ("S5-02","S6-02"), ("S5-03","S6-03"), ("S5-05","S6-05"),
    ("S5-06","S6-06"), ("S6-01","S7-01"), ("S6-02","S7-02"),
    ("S6-05","S7-04"), ("S6-06","S7-05"), ("S7-02","S8-02"),
    ("S7-03","S8-03"), ("S7-05","S8-01"),
]

NOMBRES  = ["Carlos","Sofia","Miguel","Valeria","Diego","Fernanda","Andres",
            "Daniela","Luis","Paola","Jorge","Mariana","Ricardo","Gabriela",
            "Eduardo","Ana","Roberto","Laura","Ivan","Alejandra","Oscar",
            "Natalia","Hector","Melissa","Abel","Noe","Brenda","Emmanuel"]
APELLIDOS = ["Garcia","Martinez","Lopez","Gonzalez","Rodriguez","Perez",
             "Hernandez","Ramirez","Torres","Flores","Rivera","Morales",
             "Cruz","Reyes","Ortiz","Jimenez","Castro","Vargas","Ramos",
             "Mendez","Gutierrez","Salazar","Ruiz","Aguilar","Soto"]

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def gen_matricula(year, used):
    while True:
        m = f"{year}{random.randint(100000,999999)}"
        if m not in used:
            used.add(m)
            return m

def gen_calificacion(afinidad, perfil):
    base = {
        "Programacion":    {"IA":(85,10),"Ciberseguridad":(78,8), "General":(72,10)},
        "Redes":           {"IA":(72,8), "Ciberseguridad":(88,8), "General":(75,10)},
        "Base de Datos":   {"IA":(80,8), "Ciberseguridad":(76,8), "General":(73,9)},
        "Matematica":      {"IA":(82,9), "Ciberseguridad":(74,9), "General":(70,12)},
        "Infraestructura": {"IA":(74,8), "Ciberseguridad":(84,8), "General":(72,10)},
        "Administracion":  {"IA":(75,8), "Ciberseguridad":(75,8), "General":(74,10)},
        "Tronco Comun":    {"IA":(78,8), "Ciberseguridad":(78,8), "General":(76,10)},
    }.get(afinidad, {}).get(perfil, (75,10))
    mu, sigma = base
    return round(min(100, max(60, random.gauss(mu, sigma))), 1)

def gen_encuesta(perfil):
    """7 respuestas: 0.0 = opción A (IA), 100.0 = opción B (Ciberseguridad)"""
    resp = []
    for _ in range(7):
        if perfil == "IA":
            resp.append(float(random.choices([0, 100], weights=[80, 20])[0]))
        elif perfil == "Ciberseguridad":
            resp.append(float(random.choices([0, 100], weights=[20, 80])[0]))
        else:
            resp.append(float(random.choice([0, 100])))
    return resp

def setup():
    if not DB_URL:
        raise ValueError("DATABASE_URL no está definida.")

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    # ── Crear tablas ──────────────────────────────────────────────────────────
    cur.execute("""
        DROP TABLE IF EXISTS calificaciones;
        DROP TABLE IF EXISTS seriaciones;
        DROP TABLE IF EXISTS estudiantes;
        DROP TABLE IF EXISTS materias;

        CREATE TABLE materias (
            clave       TEXT PRIMARY KEY,
            nombre      TEXT NOT NULL,
            semestre    INTEGER NOT NULL,
            creditos    INTEGER NOT NULL,
            afinidad    TEXT NOT NULL
        );

        CREATE TABLE seriaciones (
            prereq      TEXT NOT NULL,
            desbloquea  TEXT NOT NULL,
            PRIMARY KEY (prereq, desbloquea)
        );

        CREATE TABLE estudiantes (
            matricula       TEXT PRIMARY KEY,
            nombre          TEXT NOT NULL,
            apellido        TEXT NOT NULL,
            pin_hash        TEXT NOT NULL,
            semestre_actual INTEGER NOT NULL,
            perfil_real     TEXT NOT NULL,
            p1 REAL, p2 REAL, p3 REAL, p4 REAL,
            p5 REAL, p6 REAL, p7 REAL
        );

        CREATE TABLE calificaciones (
            id            SERIAL PRIMARY KEY,
            matricula     TEXT NOT NULL,
            clave         TEXT NOT NULL,
            calificacion  REAL NOT NULL
        );
    """)

    # ── Insertar catálogos ────────────────────────────────────────────────────
    execute_values(cur, "INSERT INTO materias VALUES %s", MATERIAS)
    execute_values(cur, "INSERT INTO seriaciones VALUES %s", SERIACIONES)

    # ── Alumno real (Noe/Alejandro) ───────────────────────────────────────────
    noe_enc = [0.0] * 7  # perfil IA claro
    cur.execute("""
        INSERT INTO estudiantes VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, ("22111326","Alejandro","Ortiz", hash_pin("5545"), 5, "IA", *noe_enc))

    califs = []
    random.seed(42)
    for m in MATERIAS:
        if m[2] <= 5:
            cal = gen_calificacion(m[4], "IA")
            if m[4] == "Programacion":
                cal = round(min(100, cal + 10), 1)
            califs.append(("22111326", m[0], cal))

    # ── 25 estudiantes ficticios ──────────────────────────────────────────────
    used     = {"22111326"}
    perfiles = ["IA", "Ciberseguridad", "General"]

    for _ in range(25):
        year     = random.choice([20, 21, 22])
        mat      = gen_matricula(year, used)
        nombre   = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        semestre = random.randint(2, 8)
        perfil   = random.choice(perfiles)
        pin      = mat[:4]
        enc      = gen_encuesta(perfil)

        cur.execute("""
            INSERT INTO estudiantes VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (mat, nombre, apellido, hash_pin(pin), semestre, perfil, *enc))

        for m in MATERIAS:
            if m[2] <= semestre:
                califs.append((mat, m[0], gen_calificacion(m[4], perfil)))

    execute_values(
        cur,
        "INSERT INTO calificaciones (matricula, clave, calificacion) VALUES %s",
        califs
    )

    conn.commit()
    conn.close()
    print(f"✅ Supabase listo:")
    print(f"   Materias:       {len(MATERIAS)}")
    print(f"   Seriaciones:    {len(SERIACIONES)}")
    print(f"   Estudiantes:    26")
    print(f"   Calificaciones: {len(califs)}")

if __name__ == "__main__":
    setup()
