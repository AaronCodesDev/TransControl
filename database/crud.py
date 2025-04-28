from sqlalchemy.orm import Session
from database.models import Usuario, Documentos, Empresas
import bcrypt  # Para el manejo seguro de contraseñas

### CRUD PARA USUARIOS ###

# Crear un nuevo usuario
def create_user(db: Session, nombre: str, apellido: str, nif: str, email: str, password: str):
    # Encriptar la contraseña antes de guardarla
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db_user = Usuario(nombre=nombre, apellido=apellido, nif=nif, email=email, contrasena=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Actualiza datos del usuario después de insertarlo
    return db_user

# Obtener un usuario por su email
def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

# Login de usuario (validar email y contraseña)
def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None  # Usuario no encontrado

    # Validar la contraseña usando bcrypt
    if bcrypt.checkpw(password.encode(), user.contrasena):
        return user  # Login exitoso

    return None  # Contraseña incorrecta

# Registro de usuario (verificando que no exista antes)
def register_user(db: Session, nombre: str, apellido: str, nif: str, email: str, password: str):
    # Primero revisamos si ya existe un usuario con ese email o nif
    existing_user = db.query(Usuario).filter(
        (Usuario.email == email) | (Usuario.nif == nif)
    ).first()
    
    if existing_user:
        return None  # Ya existe, no se puede registrar

    # Si no existe, creamos el nuevo usuario
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
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
            db_user.contrasena = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
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
def get_document_count(db: Session):
    return db.query(Documentos).count()

# Obtener todas las rutas de transporte en una fecha específica
def get_daily_routes(db: Session, fecha: str):
    return db.query(Documentos).filter(Documentos.fecha_transporte == fecha).all()

### CRUD PARA EMPRESAS ###

# Obtener el conteo de empresas registradas
def get_company_count(db: Session):
    return db.query(Empresas).count()