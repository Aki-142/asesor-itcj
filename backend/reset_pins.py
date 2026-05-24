import sqlite3
import hashlib

conn = sqlite3.connect('asesor.db')

rows = conn.execute('SELECT matricula, nombre, apellido FROM estudiantes').fetchall()

print(f"{'Matricula':<12} {'Nombre':<20} {'PIN'}")
print("-" * 40)

for r in rows:
    matricula = r[0]
    nombre    = f"{r[1]} {r[2]}"
    pin       = matricula[:4]
    h         = hashlib.sha256(pin.encode()).hexdigest()
    conn.execute('UPDATE estudiantes SET pin_hash=? WHERE matricula=?', (h, matricula))
    print(f"{matricula:<12} {nombre:<20} {pin}")

# Dejar el tuyo con tu PIN original
mi_pin = "5545"
mi_hash = hashlib.sha256(mi_pin.encode()).hexdigest()
conn.execute('UPDATE estudiantes SET pin_hash=? WHERE matricula=?', (mi_hash, '22111326'))

conn.commit()
conn.close()
print("\n✅ PINs actualizados. Tu PIN (22111326) sigue siendo 5545")