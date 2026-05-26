from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import pickle
import hashlib
import numpy as np
import os

app = Flask(__name__)
CORS(app)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "modelo_especialidad.pkl")
DB_URL     = os.environ.get("DATABASE_URL")

# ── Carga el modelo una vez al iniciar ───────────────────────────────────────
with open(MODEL_PATH, "rb") as f:
    BUNDLE = pickle.load(f)

MODEL          = BUNDLE["model"]
SCALER         = BUNDLE["scaler"]
MATERIAS_CLAVE = BUNDLE["materias_clave"]
LABEL_INV      = BUNDLE["label_inv"]


# ── Helpers ──────────────────────────────────────────────────────────────────
def get_db():
    conn = psycopg2.connect(DB_URL)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


# ── ENDPOINT: Login ──────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data      = request.get_json()
    matricula = data.get("matricula", "").strip()
    pin       = data.get("pin", "").strip()

    if not matricula or not pin:
        return jsonify({"ok": False, "msg": "Datos incompletos"}), 400

    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "SELECT matricula, nombre, apellido, semestre_actual FROM estudiantes WHERE matricula=%s AND pin_hash=%s",
        (matricula, hash_pin(pin))
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"ok": False, "msg": "Matrícula o NIP incorrectos"}), 401

    return jsonify({
        "ok": True,
        "estudiante": {
            "matricula":       row["matricula"],
            "nombre":          row["nombre"],
            "apellido":        row["apellido"],
            "semestre_actual": row["semestre_actual"],
        }
    })


# ── ENDPOINT: Rendimiento académico ─────────────────────────────────────────
@app.route("/api/rendimiento/<matricula>")
def rendimiento(matricula):
    conn = get_db()
    cur  = conn.cursor()

    cur.execute(
        "SELECT nombre, apellido, semestre_actual FROM estudiantes WHERE matricula=%s",
        (matricula,)
    )
    est = cur.fetchone()
    if not est:
        conn.close()
        return jsonify({"error": "Estudiante no encontrado"}), 404

    cur.execute("""
        SELECT m.clave, m.nombre, m.semestre, m.creditos, m.afinidad, c.calificacion
        FROM calificaciones c
        JOIN materias m ON c.clave = m.clave
        WHERE c.matricula = %s
        ORDER BY m.semestre, m.nombre
    """, (matricula,))
    califs = cur.fetchall()
    conn.close()

    semestre_actual = est["semestre_actual"]
    total_cal = [r["calificacion"] for r in califs if r["semestre"] < semestre_actual]
    promedio  = round(sum(total_cal) / len(total_cal), 2) if total_cal else 0

    actuales  = [r for r in califs if r["semestre"] == semestre_actual]
    en_riesgo = [
        {
            "clave":        r["clave"],
            "nombre":       r["nombre"],
            "calificacion": r["calificacion"],
            "riesgo":       "alto" if r["calificacion"] < 65 else "medio"
        }
        for r in actuales if r["calificacion"] < 70
    ]

    creditos_acumulados = sum(
        r["creditos"] for r in califs
        if r["semestre"] < semestre_actual and r["calificacion"] >= 70
    )

    historial_por_semestre = {}
    for r in califs:
        s = str(r["semestre"])
        if s not in historial_por_semestre:
            historial_por_semestre[s] = []
        historial_por_semestre[s].append({
            "clave":        r["clave"],
            "nombre":       r["nombre"],
            "calificacion": r["calificacion"],
        })

    return jsonify({
        "estudiante":          {"nombre": est["nombre"], "apellido": est["apellido"]},
        "promedio_general":    promedio,
        "semestre_actual":     semestre_actual,
        "creditos_acumulados": creditos_acumulados,
        "creditos_totales":    260,
        "materias_en_riesgo":  en_riesgo,
        "historial":           historial_por_semestre,
    })


# ── ENDPOINT: Materias recomendadas ─────────────────────────────────────────
@app.route("/api/materias-recomendadas/<matricula>")
def materias_recomendadas(matricula):
    conn = get_db()
    cur  = conn.cursor()

    cur.execute(
        "SELECT semestre_actual FROM estudiantes WHERE matricula=%s",
        (matricula,)
    )
    est = cur.fetchone()
    if not est:
        conn.close()
        return jsonify({"error": "Estudiante no encontrado"}), 404

    semestre_siguiente = est["semestre_actual"] + 1

    cur.execute(
        "SELECT clave FROM calificaciones WHERE matricula=%s AND calificacion >= 70",
        (matricula,)
    )
    aprobadas = set(r["clave"] for r in cur.fetchall())

    cur.execute(
        "SELECT * FROM materias WHERE semestre=%s",
        (semestre_siguiente,)
    )
    candidatas = cur.fetchall()

    recomendadas = []
    for mat in candidatas:
        cur.execute(
            "SELECT prereq FROM seriaciones WHERE desbloquea=%s",
            (mat["clave"],)
        )
        prereq_claves = [r["prereq"] for r in cur.fetchall()]
        cumple = all(p in aprobadas for p in prereq_claves)

        recomendadas.append({
            "clave":      mat["clave"],
            "nombre":     mat["nombre"],
            "creditos":   mat["creditos"],
            "afinidad":   mat["afinidad"],
            "prereqs":    prereq_claves,
            "disponible": cumple,
        })

    conn.close()
    total_creditos = sum(r["creditos"] for r in recomendadas if r["disponible"])

    return jsonify({
        "semestre_sugerido": semestre_siguiente,
        "materias":          recomendadas,
        "total_creditos":    total_creditos,
    })


# ── ENDPOINT: Recomendación de especialidad ─────────────────────────────────
@app.route("/api/especialidad/<matricula>")
def especialidad(matricula):
    conn = get_db()
    cur  = conn.cursor()

    cur.execute(
        "SELECT nombre, apellido, semestre_actual FROM estudiantes WHERE matricula=%s",
        (matricula,)
    )
    est = cur.fetchone()
    if not est:
        conn.close()
        return jsonify({"error": "Estudiante no encontrado"}), 404

    vector          = []
    materias_detalle = []
    for clave in MATERIAS_CLAVE:
        cur.execute("""
            SELECT c.calificacion, m.nombre, m.afinidad
            FROM calificaciones c
            JOIN materias m ON c.clave = m.clave
            WHERE c.matricula=%s AND c.clave=%s
        """, (matricula, clave))
        row = cur.fetchone()
        cal = row["calificacion"] if row else 70.0
        vector.append(cal)
        if row:
            materias_detalle.append({
                "nombre":       row["nombre"],
                "afinidad":     row["afinidad"],
                "calificacion": cal,
            })

    conn.close()

    X        = np.array(vector).reshape(1, -1)
    X_scaled = SCALER.transform(X)
    probs    = MODEL.predict_proba(X_scaled)[0]
    pred_idx = int(np.argmax(probs))

    especialidades_info = {
        0: {
            "nombre":      "Ciencia de Datos e IA",
            "descripcion": "Enfocada en Machine Learning, Redes Neuronales y Ciencia de Datos.",
            "icono":       "fa-brain",
            "materias":    ["Machine Learning", "Redes Neuronales Artificiales",
                            "Mineria de Datos", "Vision por Computadora",
                            "Procesamiento de Lenguaje Natural"],
        },
        1: {
            "nombre":      "Ciberseguridad Aplicada",
            "descripcion": "Especializada en seguridad de redes, criptografía y hacking ético.",
            "icono":       "fa-shield-halved",
            "materias":    ["Seguridad en Redes", "Criptografia Aplicada", "Hacking Etico",
                            "Forense Digital", "Seguridad en Aplicaciones Web"],
        },
        2: {
            "nombre":      "Perfil General",
            "descripcion": "Perfil equilibrado en todas las áreas de sistemas computacionales.",
            "icono":       "fa-laptop-code",
            "materias":    [],
        },
    }

    info       = especialidades_info[pred_idx]
    top_materias = sorted(materias_detalle, key=lambda x: x["calificacion"], reverse=True)[:5]

    return jsonify({
        "estudiante":    {"nombre": est["nombre"], "apellido": est["apellido"]},
        "especialidad":  info["nombre"],
        "descripcion":   info["descripcion"],
        "icono":         info["icono"],
        "materias_esp":  info["materias"],
        "probabilidades": {
            "Ciencia de Datos e IA":   round(float(probs[0]) * 100, 1),
            "Ciberseguridad Aplicada": round(float(probs[1]) * 100, 1),
            "Perfil General":          round(float(probs[2]) * 100, 1),
        },
        "top_materias": top_materias,
        "confianza":    round(float(probs[pred_idx]) * 100, 1),
    })


# ── Healthcheck ──────────────────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "version": "2.0", "db": "supabase"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
