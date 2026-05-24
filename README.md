# Asesor IA ITCJ

Sistema de asesoría académica inteligente para el Instituto Tecnológico de Ciudad Juárez.

## Estructura del Proyecto

```
itcj_asesor/
├── backend/
│   ├── app.py              ← Servidor Flask (API REST)
│   ├── setup_db.py         ← Crea la base de datos SQLite
│   ├── train_model.py      ← Entrena el modelo de regresión logística
│   ├── build.py            ← Script de inicialización completo
│   ├── requirements.txt    ← Dependencias Python
│   └── Procfile            ← Para deploy en Render
└── frontend/
    ├── index.html          ← Login
    ├── Principal.html      ← Panel principal
    ├── Rendimiento.html    ← Análisis de rendimiento académico
    ├── MateriaReco.html    ← Recomendación de materias
    ├── Especialidad.html   ← Predicción de especialidad con IA
    └── Liebre.png          ← Logo ITCJ
```

## Correr en Local

### 1. Iniciar el Backend
```bash
cd backend
pip install -r requirements.txt
python build.py        # Crea DB y entrena modelo (solo la primera vez)
python app.py          # Inicia servidor en http://localhost:5000
```

### 2. Abrir el Frontend
Abre `frontend/index.html` en tu navegador.

**Credenciales de prueba:**
- Matrícula: `22111326`
- NIP: `5545`

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/login` | Autenticación |
| GET  | `/api/rendimiento/<matricula>` | Calificaciones y riesgo |
| GET  | `/api/materias-recomendadas/<matricula>` | Carga académica sugerida |
| GET  | `/api/especialidad/<matricula>` | Predicción de especialidad con ML |
| GET  | `/api/health` | Estado del servidor |

## Modelo de IA

Se usa **Regresión Logística** (con función sigmoide) entrenada con calificaciones
de 16 materias clave para predecir la especialidad más adecuada:
- Ciencia de Datos e IA
- Ciberseguridad Aplicada

## Deploy (GitHub Pages + Render)

Ver la guía en la sección de instrucciones del proyecto.
