import os
import shutil
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Usuario
from utils.security import hash_password

# Configuración de la base de datos
DATABASE_URL = "sqlite:///database/transcontrol.db"
DB_FILE = "database/transcontrol.db"  # <- Para poder eliminar el archivo
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_documents():
    """Elimina los documentos PDF generados en las carpetas configuradas."""
    document_dirs = [
        'assets/output_pdf',
        'assets/docs/output_pdf',
        'assets/docs',
    ]

    for folder in document_dirs:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f'🗑 Documento eliminado: {file_path}')
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  
                        print(f'🗑 Carpeta eliminada: {file_path}')          
                except Exception as e:
                    print(f'⚠️ Error al eliminar {file_path}: {e}')
            else:
                print(f'ℹ️ La carpeta no existe: {folder}')

def delete_db():
    """Elimina el archivo de la base de datos si existe."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print('🗑 Base de datos antigua eliminada')
    else:
        print('ℹ️ No existía base de datos anterior')

def create_db():
    """Crea las tablas en una nueva base de datos."""
    Base.metadata.create_all(bind=engine)
    print('✅ Tablas creadas exitosamente')
    time.sleep(0.5)

def insert_initial_admin():
    """Inserta el usuario admin inicial con contraseña segura."""
    db = SessionLocal()
    try:
        password = 'admin123'
        hashed_password = hash_password(password)
        
        password_test = 'test123'
        hashed_password_test = hash_password(password_test)
        

        admin = Usuario(
            nombre='Admin',
            apellido='TransControl',
            nif='123456789W',
            email='admin@transcontrol.com',
            direccion='Calle Admin, 123',
            ciudad='Ciudad Admin',
            provincia='Provincia Admin',
            codigo_postal='28001',
            telefono='123456789',
            contrasena=hashed_password,
            rol='admin'
        )
        
        test = Usuario(
            nombre='Test',
            apellido='TransControl',
            nif='987654321W',
            email='test@transcontrol.com',
            contrasena=hashed_password_test,
            rol='test',
            is_admin = 1
        )
        
        db.add(admin)
        db.add(test)
        db.commit()
        print('👤 Usuario admin creado exitosamente')
        print('👤 Usuario test creado exitosamente')
    except Exception as e:
        db.rollback()
        print(f'⚠️ Error al insertar usuario admin: {e}')
    finally:
        db.close()

def reset_database():
    delete_db()            # 1. Elimina la base de datos
    delete_documents()     # 2. Elimina los documentos PDF
    create_db()            # 3. Crea las tablas
    insert_initial_admin() # 4. Inserta el admin

if __name__ == "__main__":
    print('\n🔄 Reseteando base de datos...\n')
    reset_database()

    if os.path.exists(DB_FILE):
        print("\n🎉 Nueva base de datos lista en 'database/transcontrol.db'\n")
    else:
        print('\n❌ No se pudo crear la base de datos')
