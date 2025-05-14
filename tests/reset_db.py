# reset_db.py
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Usuario  # 👈 Corrige la importación si falla con '.models'
from utils.security import hash_password  # 👈 Importamos hash_password

# Configuración de la base de datos
DATABASE_URL = "sqlite:///database/transcontrol.db"
DB_FILE = "database/transcontrol.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_db():
    """Elimina el archivo de la base de datos si existe."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("🗑 Base de datos antigua eliminada")
    else:
        print("ℹ️ No existía base de datos anterior")

def create_db():
    """Crea las tablas en una nueva base de datos."""
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")
    time.sleep(0.5)

def insert_initial_admin():
    """Inserta el usuario admin inicial con contraseña cifrada."""
    db = SessionLocal()
    try:
        hashed_password = hash_password("admin123")  # 👈 Ahora sí, ciframos la contraseña
        admin = Usuario(
            nombre="Admin",
            apellido="TransControl",
            nif="123456789W",
            email="admin@transcontrol.com",
            contrasena=hashed_password,  # 👈 Guardamos el hash
            rol="admin"
        )
        db.add(admin)
        db.commit()
        print("👤 Usuario admin creado exitosamente (con contraseña segura)")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Error al insertar usuario admin: {e}")
    finally:
        db.close()

def reset_database():
    delete_db()
    create_db()
    insert_initial_admin()

if __name__ == "__main__":
    print("\n🔄 Reseteando base de datos...\n")
    reset_database()
    print("\n🎉 Nueva base de datos lista en 'database/transcontrol.db'\n")
