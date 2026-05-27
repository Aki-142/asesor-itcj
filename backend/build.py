import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== PASO 1: Configurando base de datos en Supabase ===")
subprocess.run([sys.executable, "setup_db.py"], check=True)

print("\n=== PASO 2: Entrenando modelo IA con datos de Supabase ===")
subprocess.run([sys.executable, "train_model.py"], check=True)

print("\n✅ Build completado. Listo para iniciar el servidor.")
