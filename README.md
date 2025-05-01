# 📦 TransControl

**TransControl** es una aplicación desarrollada en Python para gestionar hojas de control de transporte de mercancías.  
Permite almacenar, consultar y organizar información de rutas, transportistas y empresas de manera eficiente.

---

## 🚀 Características principales

- Registro de transportistas, rutas y empresas.
- Almacenamiento de datos en base de datos local (`SQLite`).
- Interfaz gráfica desarrollada con [Flet](https://flet.dev/).
- Organización de documentos y control de operaciones diarias.
- Entorno preparado para ser ampliado a versiones Web y Mobile.

---

## 📂 Estructura del proyecto



```
TransControl/
├── assets/              # Archivos estáticos (imágenes, iconos, etc.)
├── database/            # Scripts de base de datos y modelos
├── storage/             # Documentos o archivos de usuarios
├── utils/               # Utilidades como hashing de contraseñas
├── views/               # Vistas principales de la aplicación
├── main.py              # Punto de entrada de la aplicación
├── requirements.txt     # Dependencias del proyecto
└── .gitignore           # Archivos y carpetas ignorados por Git
```

---

## ⚙️ Requisitos

- Python 3.10 o superior
- Librerías listadas en `requirements.txt`

Crear Venv

```bash
python3 -m venv venv
```
Entrar en Entorno virtual

```bash
source venv/bin/activate      
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Cómo ejecutar

Para crear la base datos para pruebas
```bash
python3 database/reset_db.py
```

Dentro de la carpeta del proyecto:

```bash
python main.py o flet main.py
```

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**.  
Puedes usarlo, modificarlo y distribuirlo libremente.

---

## ✨ Estado actual

🚧 Proyecto en desarrollo — Se están implementando nuevas funcionalidades y mejoras de interfaz.

---

# ✅ ¿Cómo usarlo?
- Clona el repositorio.
- Instala las dependencias.
- Ejecuta `main.py` para iniciar la aplicación.

