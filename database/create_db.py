from sqlalchemy import create_engine
from database.models import Base, Usuario  # Asegúrate de que la importación sea correcta
from sqlalchemy.orm import sessionmaker
import os
import time

# Configuración de la base de datos
DATABASE_URL = "sqlite:///database/transcontrol.db"  # Se creará en el mismo directorio
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        time.sleep(0.5)
        insert_initial_data()
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        raise

def insert_initial_data():
    """Inserta datos iniciales para pruebas"""
    db = SessionLocal()
    try:
        if not db.query(Usuario).filter(Usuario.nif == "admin").first():
            admin = Usuario(
                usuario="admin",
                nombre="Admin",
                apellido="Sistema",
                nif="123456789W",
                email="admin@transcontrol.com",
                contrasena="admin123",  # En producción usa hashing!
                rol="admin"
            )
            db.add(admin)
            db.commit()
            print("👤 Usuario admin creado")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Error al insertar datos iniciales: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🛠 Inicializando base de datos...")
    print(f"🔗 Conexión: {DATABASE_URL}")
    init_db()
    
    # Verifica si la base de datos fue creada
    if os.path.exists("database/transcontrol.db"):
        print("\n🎉 Base de datos lista en database/transcontrol.db")
    else:
        print("\n❌ No se pudo crear la base de datos")