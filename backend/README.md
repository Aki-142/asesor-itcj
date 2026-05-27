# Asesor IA ITCJ

Sistema de asesoría académica con modelo de regresión logística para recomendación de especialidad.

## Estructura

```
itcj_asesor/
├── backend/
│   ├── app.py              ← Servidor Flask (API REST)
│   ├── train_model.py      ← Entrena el modelo de ML
│   ├── build.py            ← Script de build para Render
│   ├── requirements.txt
│   └── Procfile
├── frontend/
│   ├── index.html
│   ├── Principal.html
│   ├── Rendimiento.html
│   ├── MateriaReco.html
│   ├── Encuesta.html
│   ├── Especialidad.html
│   └── Liebre.png
├── supabase_schema.sql     ← Ejecutar PRIMERO en Supabase
├── supabase_seed.sql       ← Ejecutar SEGUNDO en Supabase
└── .gitignore
```

## Deploy paso a paso

### 1. Supabase — crear tablas y datos

1. Entra a tu proyecto en [supabase.com](https://supabase.com) → **SQL Editor**
2. Pega y ejecuta el contenido de `supabase_schema.sql`
3. Pega y ejecuta el contenido de `supabase_seed.sql`
4. Copia tu connection string: **Settings → Database → URI** (modo *Session pooler*)
   - Formato: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres`

### 2. Render — configurar el backend

1. Crea un nuevo **Web Service** conectado a tu repositorio
2. Configura:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt && python build.py`
   - **Start Command:** `gunicorn app:app`
3. En **Environment Variables** agrega:
   - `DATABASE_URL` = tu connection string de Supabase
4. Despliega. El build entrena el modelo automáticamente.

### 3. Frontend

Sube la carpeta `frontend/` a GitHub Pages, Netlify, o cualquier hosting estático.
La URL del API ya apunta a `https://asesor-itcj.onrender.com/api`.

## Credenciales de prueba

| Matrícula | NIP  | Perfil |
|-----------|------|--------|
| 22111326  | 5545 | IA (alumno real) |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/login` | Autenticación |
| GET | `/api/rendimiento/:matricula` | Historial y materias en riesgo |
| GET | `/api/materias-recomendadas/:matricula` | Carga sugerida próximo semestre |
| POST | `/api/especialidad/:matricula` | Predicción de especialidad (requiere `{"encuesta": [0,100,...]}`) |
| GET | `/api/health` | Healthcheck |
