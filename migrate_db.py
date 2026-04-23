"""
Script de migración — ejecutar UNA VEZ con la app cerrada.
Añade las columnas nuevas a la base de datos existente.

Uso:
    python migrate_db.py
"""

import sqlite3
import os

DB_PATH = "database/transcontrol.db"

if not os.path.exists(DB_PATH):
    print(f"❌ No se encontró la base de datos en: {DB_PATH}")
    print("   Asegúrate de ejecutar este script desde la carpeta raíz del proyecto.")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

migrations = [
    (
        "vehiculos",
        """CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            marca VARCHAR(50) NOT NULL,
            modelo VARCHAR(50) NOT NULL,
            matricula VARCHAR(20) NOT NULL,
            matricula_remolque VARCHAR(20),
            fecha_creacion DATETIME
        )""",
    ),
    (
        "documentos_control.vehiculo_id",
        "ALTER TABLE documentos_control ADD COLUMN vehiculo_id INTEGER REFERENCES vehiculos(id)",
    ),
    (
        "documentos_control.firma_cargador_img",
        "ALTER TABLE documentos_control ADD COLUMN firma_cargador_img VARCHAR(300)",
    ),
    (
        "documentos_control.firma_transportista_img",
        "ALTER TABLE documentos_control ADD COLUMN firma_transportista_img VARCHAR(300)",
    ),
    (
        "documentos_control.albaran_path",
        "ALTER TABLE documentos_control ADD COLUMN albaran_path VARCHAR(300)",
    ),
    (
        "usuarios.foto_perfil",
        "ALTER TABLE usuarios ADD COLUMN foto_perfil VARCHAR(300)",
    ),
]

print("🔄 Ejecutando migraciones...\n")
ok = 0
skip = 0
for name, sql in migrations:
    try:
        cur.execute(sql)
        print(f"  ✅ {name}")
        ok += 1
    except sqlite3.OperationalError as e:
        print(f"  ⏭  {name} — ya existe ({e})")
        skip += 1

conn.commit()
conn.close()

print(f"\n✅ Migración completada: {ok} aplicadas, {skip} omitidas.")
print("   Ya puedes arrancar la app.")
