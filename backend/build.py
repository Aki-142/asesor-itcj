#!/usr/bin/env python3
"""
Ejecutar este script UNA VEZ antes de subir a Render,
o añadirlo como 'Build Command' en Render:
    python build.py
"""
import subprocess
import sys
import os
import sqlite3
import hashlib

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== PASO 1: Creando base de datos ===")
subprocess.run([sys.executable, "setup_db.py"], check=True)

print("\n=== PASO 2: Entrenando modelo IA ===")
subprocess.run([sys.executable, "train_model.py"], check=True)

print("\n=== PASO 3: Configurando PINs ===")
conn = sqlite3.connect("asesor.db")
rows = conn.execute("SELECT matricula FROM estudiantes").fetchall()
for r in rows:
    pin = r[0][:4]
    h = hashlib.sha256(pin.encode()).hexdigest()
    conn.execute("UPDATE estudiantes SET pin_hash=? WHERE matricula=?", (h, r[0]))
# PIN especial para Noe
mi_hash = hashlib.sha256("5545".encode()).hexdigest()
conn.execute("UPDATE estudiantes SET pin_hash=? WHERE matricula=?", (mi_hash, "22111326"))
conn.commit()
conn.close()
print("✅ PINs configurados")

print("\n✅ Build completado. Listo para iniciar el servidor.")