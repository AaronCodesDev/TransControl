from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Usuario, Documentos, Empresas
from utils.security import hash_password, verify_password
from datetime import datetime

### CRUD PARA USUARIOS ###

# Crear un nuevo usuario
def create_user(db: Session, nombre: str, apellido: str, nif: str, email: str, password: str):
    hashed_password = hash_password(password)
    db_user = Usuario(nombre=nombre, apellido=apellido, nif=nif, email=email, contrasena=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Obtener un usuario por su email
def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

# Login de usuario (validar email y contraseña)
def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None  # Usuario no encontrado

    # Validar la contraseña usando verify_password
    if verify_password(password, user.contrasena):
        return user  # Login exitoso

    return None  # Contraseña incorrecta

# Registro de usuario (verificando que no exista antes)
def register_user(db: Session, nombre: str, apellido: str, nif: str, email: str, password: str):
    existing_user = db.query(Usuario).filter(
        (Usuario.email == email) | (Usuario.nif == nif)
    ).first()
    
    if existing_user:
        return None

    hashed_password = hash_password(password)
    new_user = Usuario(
        nombre=nombre,
        apellido=apellido,
        nif=nif,
        email=email,
        contrasena=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Actualizar usuario
def update_user(db: Session, user_id: int, nombre: str = None, apellido: str = None, password: str = None):
    db_user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if db_user:
        if nombre:
            db_user.nombre = nombre
        if apellido:
            db_user.apellido = apellido
        if password:
            db_user.contrasena = hash_password(password)  # 👈 Aquí usas hash_password también
        db.commit()
        db.refresh(db_user)
    return db_user

# Eliminar un usuario
def delete_user(db: Session, user_id: int):
    db_user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

### CRUD PARA DOCUMENTACION ###

# Obtener el conteo de documentos
def get_document_count(db: Session, user: Usuario = None):
    query = db.query(Documentos)
    if user and user.rol != 'admin':
        query = query.filter(Documentos.usuarios_id == user.id)
    return query.count()

# Obtener todas las rutas de transporte en una fecha específica
def get_daily_routes(db: Session, fecha: str, user: Usuario = None):
    query = db.query(Documentos).filter(Documentos.fecha_creacion == fecha)
    if user and user.rol != 'admin':
        query = query.filter(Documentos.usuarios_id == user.id)
    return query.all()


from datetime import datetime
    
    
### CRUD PARA EMPRESAS ###

# Obtener total de empresas registradas
def get_company_count(db: Session, user: Usuario = None):
    if user and user.rol != 'admin':
        return db.query(Empresas).filter(Empresas.usuario_id == user.id).count()
    return db.query(Empresas).count()

# Obener total de documentos 
def get_documents_count(db: Session):
    return db.query(Documentos).count()

# Obtener total de Documentos diarios
def get_dealy_documents(db: Session, fecha: str):
    return db.query(Documentos).filter(Documentos.fecha_transporte == datetime.today()).count()

# Obtener total de Documentos Registrados
def get_document_count_all(db: Session):
    return db.query(Documentos).count()


# Obtener total de Empresas Registradas
def get_company_count_all(db: Session):
    return db.query(Empresas).count()

# Obtener total de Usuarios Registrados
def get_user_count_all(db: Session):
    return db.query(Usuario).count()


def get_top_destinations(db: Session, user: Usuario = None, limit: int = 5):
    """Devuelve los destinos más frecuentes con su conteo."""
    query = db.query(
        Documentos.lugar_destino,
        func.count(Documentos.lugar_destino).label('total')
    )
    if user and user.rol != 'admin':
        query = query.filter(Documentos.usuarios_id == user.id)
    return (
        query.group_by(Documentos.lugar_destino)
        .order_by(func.count(Documentos.lugar_destino).desc())
        .limit(limit)
        .all()
    )


def get_top_origins(db: Session, user: Usuario = None, limit: int = 5):
    """Devuelve los orígenes más frecuentes con su conteo."""
    query = db.query(
        Documentos.lugar_origen,
        func.count(Documentos.lugar_origen).label('total')
    )
    if user and user.rol != 'admin':
        query = query.filter(Documentos.usuarios_id == user.id)
    return (
        query.group_by(Documentos.lugar_origen)
        .order_by(func.count(Documentos.lugar_origen).desc())
        .limit(limit)
        .all()
    )