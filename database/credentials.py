import json
import os

CREDENCIALES_FILE = "credentials.json"  # ⚡ Guarda en el directorio actual del proyecto

def save_credentials(email, password):
    """Guarda el email y password en un archivo JSON."""
    with open(CREDENCIALES_FILE, "w") as f:
        json.dump({"email": email, "password": password}, f)
    print(f"✅ Credenciales guardadas en {CREDENCIALES_FILE}")

def load_credentials():
    """Carga las credenciales si existen, sino None."""
    if os.path.exists(CREDENCIALES_FILE):
        with open(CREDENCIALES_FILE, "r") as f:
            return json.load(f)
    return None

def clear_credentials():
    """Borra las credenciales guardadas."""
    if os.path.exists(CREDENCIALES_FILE):
        os.remove(CREDENCIALES_FILE)
