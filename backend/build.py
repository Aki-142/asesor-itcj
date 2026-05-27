import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== Entrenando modelo IA con datos de Supabase ===")
subprocess.run([sys.executable, "train_model.py"], check=True)

print("\n✅ Build completado. Listo para iniciar el servidor.")
