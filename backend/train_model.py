import os
import pickle
import numpy as np
import psycopg2
import psycopg2.extras
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

DB_URL     = os.environ.get("DATABASE_URL")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo_especialidad.pkl")

MATERIAS_CLAVE = [
    "S1-02", "S2-02", "S2-05", "S2-06",
    "S3-02", "S3-05", "S4-03", "S4-04",
    "S4-05", "S5-02", "S5-03", "S5-06",
    "S6-01", "S6-02", "S6-04", "S6-06",
]

LABEL_MAP = {"IA": 0, "Ciberseguridad": 1, "General": 2}
LABEL_INV = {0: "Ciencia de Datos e IA", 1: "Ciberseguridad Aplicada", 2: "General"}


def get_feature_vector(matricula: str, cur) -> list:
    """Construye el vector de 23 features: 16 calificaciones + 7 encuesta."""
    vector = []

    # 1. Calificaciones de las 16 materias clave
    for clave in MATERIAS_CLAVE:
        cur.execute(
            "SELECT calificacion FROM calificaciones WHERE matricula=%s AND clave=%s",
            (matricula, clave)
        )
        row = cur.fetchone()
        vector.append(float(row["calificacion"]) if row else 70.0)

    # 2. Las 7 respuestas de la encuesta (p1-p7)
    cur.execute(
        "SELECT p1, p2, p3, p4, p5, p6, p7 FROM estudiantes WHERE matricula=%s",
        (matricula,)
    )
    enc = cur.fetchone()
    if enc and all(enc[f"p{i}"] is not None for i in range(1, 8)):
        vector.extend([float(enc[f"p{i}"]) for i in range(1, 8)])
    else:
        vector.extend([50.0] * 7)

    return vector


def train_model():
    if not DB_URL:
        raise ValueError("La variable de entorno DATABASE_URL no está definida.")

    conn = psycopg2.connect(DB_URL)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    cur  = conn.cursor()

    cur.execute("SELECT matricula, perfil_real FROM estudiantes")
    estudiantes = cur.fetchall()

    X, y = [], []
    for est in estudiantes:
        if est["perfil_real"] not in LABEL_MAP:
            continue
        vec = get_feature_vector(est["matricula"], cur)
        X.append(vec)
        y.append(LABEL_MAP[est["perfil_real"]])

    conn.close()

    X = np.array(X)
    y = np.array(y)

    print(f"Dataset: {len(X)} muestras, {X.shape[1]} features")
    print(f"Distribución: IA={sum(y==0)}, Ciber={sum(y==1)}, General={sum(y==2)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler    = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = LogisticRegression(solver="lbfgs", max_iter=1000, C=1.0, random_state=42)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    acc    = accuracy_score(y_test, y_pred)
    print(f"\n✅ Accuracy del modelo: {acc:.2%}")
    print(classification_report(y_test, y_pred, target_names=["IA", "Ciberseguridad", "General"]))

    bundle = {
        "model":          model,
        "scaler":         scaler,
        "materias_clave": MATERIAS_CLAVE,
        "label_map":      LABEL_MAP,
        "label_inv":      LABEL_INV,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)

    print(f"💾 Modelo guardado en: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
