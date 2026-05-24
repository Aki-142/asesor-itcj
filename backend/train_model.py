import sqlite3
import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

DB_PATH = "asesor.db"
MODEL_PATH = "modelo_especialidad.pkl"

# Materias clave para la predicción (las más discriminativas entre IA vs Ciberseguridad)
MATERIAS_CLAVE = [
    "S1-02",  # Fundamentos de Programacion
    "S2-02",  # POO
    "S2-05",  # Algebra Lineal
    "S2-06",  # Probabilidad y Estadistica
    "S3-02",  # Estructura de Datos
    "S3-05",  # Sistemas Operativos
    "S4-03",  # Topicos Avanzados de Programacion
    "S4-04",  # Fundamentos de BD
    "S4-05",  # Taller de Sistemas Operativos
    "S5-02",  # Fundamentos de Telecomunicaciones
    "S5-03",  # Taller de BD
    "S5-06",  # Arquitectura de Computadoras
    "S6-01",  # Lenguajes y Automatas I
    "S6-02",  # Redes de Computadoras
    "S6-04",  # Graficacion
    "S6-06",  # Lenguajes de Interfaz
]

LABEL_MAP = {"IA": 0, "Ciberseguridad": 1, "General": 2}
LABEL_INV = {0: "Ciencia de Datos e IA", 1: "Ciberseguridad Aplicada", 2: "General"}


def get_feature_vector(matricula: str, conn) -> list[float] | None:
    """Obtiene vector de características para un alumno."""
    c = conn.cursor()
    vector = []
    for clave in MATERIAS_CLAVE:
        row = c.execute(
            "SELECT calificacion FROM calificaciones WHERE matricula=? AND clave=?",
            (matricula, clave)
        ).fetchone()
        vector.append(row[0] if row else 70.0)  # 70 como fallback neutral
    return vector


def train_model():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    estudiantes = c.execute(
        "SELECT matricula, perfil_real FROM estudiantes"
    ).fetchall()

    X, y = [], []
    for matricula, perfil in estudiantes:
        if perfil not in LABEL_MAP:
            continue
        vec = get_feature_vector(matricula, conn)
        X.append(vec)
        y.append(LABEL_MAP[perfil])

    conn.close()

    X = np.array(X)
    y = np.array(y)

    print(f"Dataset: {len(X)} muestras, {X.shape[1]} features")
    print(f"Distribución: IA={sum(y==0)}, Ciber={sum(y==1)}, General={sum(y==2)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # Regresión logística con función sigmoide (multi-clase con softmax internamente)
    model = LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
        C=1.0,
        random_state=42
    )
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n✅ Accuracy del modelo: {acc:.2%}")
    print("\nReporte por clase:")
    print(classification_report(
        y_test, y_pred,
        target_names=["IA", "Ciberseguridad", "General"]
    ))

    # Guardar modelo + scaler + metadata
    bundle = {
        "model": model,
        "scaler": scaler,
        "materias_clave": MATERIAS_CLAVE,
        "label_map": LABEL_MAP,
        "label_inv": LABEL_INV,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)

    print(f"\n💾 Modelo guardado en: {MODEL_PATH}")
    return model, scaler


if __name__ == "__main__":
    train_model()
