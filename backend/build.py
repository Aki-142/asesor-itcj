#!/usr/bin/env python3
"""
Ejecutar este script UNA VEZ antes de subir a Render,
o añadirlo como 'Build Command' en Render:
    python build.py
"""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== PASO 1: Creando base de datos ===")
subprocess.run([sys.executable, "setup_db.py"], check=True)

print("\n=== PASO 2: Entrenando modelo IA ===")
subprocess.run([sys.executable, "train_model.py"], check=True)

print("\n✅ Build completado. Listo para iniciar el servidor.")
