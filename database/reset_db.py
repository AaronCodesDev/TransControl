# reset_db.py
import os
from .models import Base, Usuario
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

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
    time.sleep(0.5)  # Espera para asegurar que todo se crea antes de insertar datos

def insert_initial_admin():
    """Inserta el usuario admin inicial."""
    db = SessionLocal()
    try:
        admin = Usuario(
            usuario="admin",
            nombre="Admin",
            apellido="Sistema",
            nif="123456789W",
            email="admin@transcontrol.com",
            contrasena="admin123",  # Recuerda cifrar en producción
            rol="admin"
        )
        db.add(admin)
        db.commit()
        print("👤 Usuario admin creado exitosamente")
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
