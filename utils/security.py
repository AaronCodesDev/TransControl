import bcrypt

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt y devuelve un string."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # <- DECODIFICAR para guardar un STR

def verify_password(password_input: str, hashed_password: str) -> bool:
    """Verifica que la contraseña introducida coincida con el hash almacenado."""
    return bcrypt.checkpw(password_input.encode('utf-8'), hashed_password.encode('utf-8'))
