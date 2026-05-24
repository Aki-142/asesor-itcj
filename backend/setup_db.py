import sqlite3
import random
import hashlib

DB_PATH = "asesor.db"

# ── Materias completas con semestre, créditos y afinidad ──────────────────────
MATERIAS = [
    # (clave, nombre, semestre, creditos, afinidad)
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

    # Especialidad IA
    ("ESP-IA-01", "Machine Learning",                           10, 5, "Programacion"),
    ("ESP-IA-02", "Redes Neuronales Artificiales",              10, 5, "Programacion"),
    ("ESP-IA-03", "Mineria de Datos",                           10, 5, "Programacion"),
    ("ESP-IA-04", "Vision por Computadora",                     10, 5, "Programacion"),
    ("ESP-IA-05", "Procesamiento de Lenguaje Natural",          10, 5, "Programacion"),

    # Especialidad Ciberseguridad
    ("ESP-CS-01", "Seguridad en Redes",                         10, 5, "Redes"),
    ("ESP-CS-02", "Criptografia Aplicada",                      10, 5, "Redes"),
    ("ESP-CS-03", "Hacking Etico",                              10, 5, "Redes"),
    ("ESP-CS-04", "Forense Digital",                            10, 5, "Redes"),
    ("ESP-CS-05", "Seguridad en Aplicaciones Web",              10, 5, "Redes"),
]

# ── Seriaciones: (materia_prereq, materia_que_desbloquea) ─────────────────────
SERIACIONES = [
    ("S1-01", "S2-01"),  # Calculo Diferencial → Calculo Integral
    ("S1-02", "S2-02"),  # Fundamentos Prog → POO
    ("S1-04", "S6-01"),  # Matematicas Discretas → Lenguajes y Automatas I
    ("S1-06", "S7-03"),  # Fundamentos Investigacion → Taller Inv I
    ("S2-01", "S3-01"),  # Calculo Integral → Calculo Vectorial
    ("S2-02", "S3-02"),  # POO → Estructura de Datos
    ("S2-05", "S3-01"),  # Algebra Lineal → Calculo Vectorial
    ("S2-06", "S3-04"),  # Probabilidad → Investigacion de Operaciones
    ("S3-01", "S4-01"),  # Calculo Vectorial → Ecuaciones Diferenciales
    ("S3-02", "S4-03"),  # Estructura de Datos → Topicos Avanzados
    ("S3-03", "S5-05"),  # Cultura Empresarial → Fund. Ing. Software
    ("S3-04", "S5-04"),  # Inv. Operaciones → Simulacion
    ("S3-05", "S4-05"),  # Sistemas Operativos → Taller SO
    ("S4-04", "S5-03"),  # Fundamentos BD → Taller BD
    ("S4-06", "S5-06"),  # Principios Electricos → Arquitectura
    ("S5-02", "S6-02"),  # Fund. Telecom → Redes de Computadoras
    ("S5-03", "S6-03"),  # Taller BD → Admin BD
    ("S5-05", "S6-05"),  # Fund. Ing SW → Ingenieria SW
    ("S5-06", "S6-06"),  # Arquitectura → Lenguajes de Interfaz
    ("S6-01", "S7-01"),  # Lenguajes I → Lenguajes II
    ("S6-02", "S7-02"),  # Redes → Conmutacion
    ("S6-05", "S7-04"),  # Ing SW → Gestion Proyectos
    ("S6-06", "S7-05"),  # Lenguajes Interfaz → Sistemas Programables
    ("S7-02", "S8-02"),  # Conmutacion → Admin Redes
    ("S7-03", "S8-03"),  # Taller Inv I → Taller Inv II
    ("S7-05", "S8-01"),  # Sistemas Programables → Prog. Logica
]

NOMBRES = [
    "Carlos", "Sofia", "Miguel", "Valeria", "Diego", "Fernanda", "Andres",
    "Daniela", "Luis", "Paola", "Jorge", "Mariana", "Ricardo", "Gabriela",
    "Eduardo", "Ana", "Roberto", "Laura", "Ivan", "Alejandra", "Oscar",
    "Natalia", "Hector", "Melissa", "Abel", "Noe", "Brenda", "Emmanuel",
]
APELLIDOS = [
    "Garcia", "Martinez", "Lopez", "Gonzalez", "Rodriguez", "Perez",
    "Hernandez", "Ramirez", "Torres", "Flores", "Rivera", "Morales",
    "Cruz", "Reyes", "Ortiz", "Jimenez", "Castro", "Vargas", "Ramos",
    "Mendez", "Gutierrez", "Salazar", "Ruiz", "Aguilar", "Soto",
]


def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def gen_matricula(year: int, used: set) -> str:
    while True:
        m = f"{year}{random.randint(100000, 999999)}"
        if m not in used:
            used.add(m)
            return m


def gen_calificacion(afinidad: str, perfil: str) -> float:
    """Genera calificación acorde al perfil del alumno."""
    base = {
        "Programacion":    {"IA": (85, 10), "Ciberseguridad": (78, 8),  "General": (72, 10)},
        "Redes":           {"IA": (72, 8),  "Ciberseguridad": (88, 8),  "General": (75, 10)},
        "Base de Datos":   {"IA": (80, 8),  "Ciberseguridad": (76, 8),  "General": (73, 9)},
        "Matematica":      {"IA": (82, 9),  "Ciberseguridad": (74, 9),  "General": (70, 12)},
        "Infraestructura": {"IA": (74, 8),  "Ciberseguridad": (84, 8),  "General": (72, 10)},
        "Administracion":  {"IA": (75, 8),  "Ciberseguridad": (75, 8),  "General": (74, 10)},
        "Tronco Comun":    {"IA": (78, 8),  "Ciberseguridad": (78, 8),  "General": (76, 10)},
    }.get(afinidad, {}).get(perfil, (75, 10))
    mu, sigma = base
    cal = random.gauss(mu, sigma)
    return round(min(100, max(60, cal)), 1)


def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
        DROP TABLE IF EXISTS calificaciones;
        DROP TABLE IF EXISTS estudiantes;
        DROP TABLE IF EXISTS seriaciones;
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
            PRIMARY KEY (prereq, desbloquea),
            FOREIGN KEY (prereq)     REFERENCES materias(clave),
            FOREIGN KEY (desbloquea) REFERENCES materias(clave)
        );

        CREATE TABLE estudiantes (
            matricula   TEXT PRIMARY KEY,
            nombre      TEXT NOT NULL,
            apellido    TEXT NOT NULL,
            pin_hash    TEXT NOT NULL,
            semestre_actual INTEGER NOT NULL,
            perfil_real TEXT NOT NULL
        );

        CREATE TABLE calificaciones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula   TEXT NOT NULL,
            clave       TEXT NOT NULL,
            calificacion REAL NOT NULL,
            FOREIGN KEY (matricula) REFERENCES estudiantes(matricula),
            FOREIGN KEY (clave)     REFERENCES materias(clave)
        );
    """)

    # Insertar materias
    c.executemany(
        "INSERT INTO materias VALUES (?,?,?,?,?)", MATERIAS
    )

    # Insertar seriaciones
    c.executemany(
        "INSERT INTO seriaciones VALUES (?,?)", SERIACIONES
    )

    # Generar estudiantes ficticios
    used_matriculas = {"22111326"}  # reservar la del alumno real
    perfiles = ["IA", "Ciberseguridad", "General"]

    estudiantes_data = []
    califs_data = []

    # Alumno real (Noe) — perfil IA, semestre 4 completado
    noe_califs = []
    materias_s1_s4 = [m for m in MATERIAS if m[2] <= 4]
    for m in materias_s1_s4:
        cal = gen_calificacion(m[4], "IA")
        # boostar materias de programacion para que el modelo lo detecte
        if m[4] == "Programacion":
            cal = round(min(100, cal + 10), 1)
        noe_califs.append(("22111326", m[0], cal))

    # Materias actuales (semestre 5, en curso — sin calificacion final)
    materias_s5 = [m for m in MATERIAS if m[2] == 5]
    for m in materias_s5:
        cal = round(random.uniform(60, 85), 1)
        noe_califs.append(("22111326", m[0], cal))

    c.execute(
        "INSERT INTO estudiantes VALUES (?,?,?,?,?,?)",
        ("22111326", "Noe", "Alvarez", hash_pin("5545"), 5, "IA")
    )
    califs_data.extend(noe_califs)

    # 25 estudiantes ficticios
    random.seed(42)
    for i in range(25):
        year = random.choice([20, 21, 22])
        mat = gen_matricula(year, used_matriculas)
        nombre = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        pin = str(random.randint(1000, 9999))
        semestre = random.randint(2, 8)
        perfil = random.choice(perfiles)

        c.execute(
            "INSERT INTO estudiantes VALUES (?,?,?,?,?,?)",
            (mat, nombre, apellido, hash_pin(pin), semestre, perfil)
        )

        # Calificaciones de semestres completados
        for m in MATERIAS:
            if m[2] < semestre:
                cal = gen_calificacion(m[4], perfil)
                califs_data.append((mat, m[0], cal))
            elif m[2] == semestre:
                # Semestre actual: califs parciales (60-85)
                cal = round(random.uniform(60, 85), 1)
                califs_data.append((mat, m[0], cal))

    c.executemany(
        "INSERT INTO calificaciones (matricula, clave, calificacion) VALUES (?,?,?)",
        califs_data
    )

    conn.commit()
    conn.close()
    print(f"✅ Base de datos creada: {DB_PATH}")
    print(f"   Materias:     {len(MATERIAS)}")
    print(f"   Seriaciones:  {len(SERIACIONES)}")
    print(f"   Estudiantes:  26 (1 real + 25 ficticios)")
    print(f"   Calificaciones: {len(califs_data)}")


if __name__ == "__main__":
    create_db()
