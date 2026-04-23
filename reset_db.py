"""
reset_db.py — Limpia la base de datos y archivos generados.

Mantiene únicamente:
  · admin@transcontrol.com  (rol: admin,  pass: admin123)
  · test@transcontrol.com   (rol: test,   pass: test123)

Uso:  python reset_db.py
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime

# ── Rutas absolutas (funciona desde cualquier directorio) ──────────────────
ROOT    = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT, "database", "transcontrol.db")

ASSET_DIRS = [
    os.path.join(ROOT, "assets", "docs"),
    os.path.join(ROOT, "assets", "signatures"),
    os.path.join(ROOT, "assets", "albaranes"),
]

# ── Añadir root al path para importar utils ────────────────────────────────
sys.path.insert(0, ROOT)
from utils.security import hash_password


def _sep(msg=""):
    print(f"\n{'─'*52}")
    if msg:
        print(f"  {msg}")
        print(f"{'─'*52}")


# ──────────────────────────────────────────────────────────────────────────
#  1. Limpiar archivos generados
# ──────────────────────────────────────────────────────────────────────────
def clean_assets():
    _sep("🗂  Limpiando archivos generados")
    for folder in ASSET_DIRS:
        os.makedirs(folder, exist_ok=True)   # crear si no existe
        count = 0
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)
                    count += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    count += 1
            except Exception as e:
                print(f"  ⚠  {path}: {e}")
        label = os.path.relpath(folder, ROOT)
        print(f"  🗑  {label}: {count} elemento(s) eliminado(s)")


# ──────────────────────────────────────────────────────────────────────────
#  2. Limpiar base de datos con SQL directo
# ──────────────────────────────────────────────────────────────────────────
def clean_database():
    _sep("🧹 Limpiando base de datos")

    if not os.path.exists(DB_PATH):
        print(f"  ℹ  No existe la BD en {DB_PATH}")
        print("  ℹ  Se creará al arrancar la app.")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    try:
        # Desactivar FK temporalmente para poder borrar en cualquier orden
        cur.execute("PRAGMA foreign_keys = OFF")
        con.commit()

        tables = {
            "documentos_control": "documento(s)",
            "empresas":           "empresa(s)",
            "vehiculos":          "vehículo(s)",
            "usuarios":           "usuario(s)",
        }

        for table, label in tables.items():
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            before = cur.fetchone()[0]
            cur.execute(f"DELETE FROM {table}")
            con.commit()
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            after = cur.fetchone()[0]
            print(f"  🗑  {table}: {before - after} {label} eliminado(s)")

        # Reiniciar auto-increment
        for table in tables:
            cur.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        con.commit()

        cur.execute("PRAGMA foreign_keys = ON")
        con.commit()
        print("  ✅ Tablas limpiadas")

    except Exception as e:
        con.rollback()
        print(f"  ❌ Error: {e}")
        raise
    finally:
        con.close()


# ──────────────────────────────────────────────────────────────────────────
#  3. Insertar usuarios semilla
# ──────────────────────────────────────────────────────────────────────────
SEED_USERS = [
    {
        "nombre": "Admin", "apellido": "TransControl",
        "nif": "123456789W", "email": "admin@transcontrol.com",
        "password": "admin123",
        "direccion": "Calle Admin, 123", "ciudad": "Ciudad Admin",
        "provincia": "Provincia Admin", "codigo_postal": "28001",
        "telefono": "123456789", "rol": "admin", "is_admin": 1,
    },
    {
        "nombre": "Test", "apellido": "TransControl",
        "nif": "987654321W", "email": "test@transcontrol.com",
        "password": "test123",
        "direccion": None, "ciudad": None,
        "provincia": None, "codigo_postal": None,
        "telefono": None, "rol": "test", "is_admin": 1,
    },
]


def insert_users():
    _sep("👤 Insertando usuarios base")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    try:
        for u in SEED_USERS:
            cur.execute(
                """INSERT INTO usuarios
                   (nombre, apellido, nif, email, contrasena,
                    direccion, ciudad, provincia, codigo_postal,
                    telefono, rol, is_admin, fecha_creacion)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    u["nombre"], u["apellido"], u["nif"], u["email"],
                    hash_password(u["password"]),
                    u["direccion"], u["ciudad"], u["provincia"],
                    u["codigo_postal"], u["telefono"],
                    u["rol"], u["is_admin"], now,
                ),
            )
            print(f"  ✅ {u['email']}  (pass: {u['password']})")
        con.commit()
    except Exception as e:
        con.rollback()
        print(f"  ❌ Error: {e}")
        raise
    finally:
        con.close()


# ──────────────────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────────────────
def main():
    print("\n🔄  RESET — TransControl")
    print(f"    BD: {DB_PATH}")

    clean_assets()
    clean_database()

    if os.path.exists(DB_PATH):
        insert_users()
        _sep("🎉 Listo — arranca con:  flet run main.py")
    else:
        _sep("⚠  No se encontró la BD. Arranca la app una vez para crearla y vuelve a ejecutar este script.")


if __name__ == "__main__":
    main()
