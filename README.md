# 📦 TransControl

**TransControl** es una aplicación desarrollada en Python para gestionar hojas de control de transporte de mercancías.  
Permite almacenar, consultar y organizar información de rutas y empresas de manera eficiente.

---

## 🚀 Características principales

- Registro de rutas y empresas.
- Almacenamiento de datos en base de datos local (`SQLite`).
- Interfaz gráfica desarrollada con [Flet](https://flet.dev/).
- Organización de documentos y control de diario y total de operaciones.
- Preparado para ser ampliado a versiones Web y Mobile.
- Generación automática de un documento PDF con código QR para su presentación ante las autoridades, si así se requiere.

---

## 📂 Estructura del proyecto



```
TransControl/
├── assets/              # Archivos estáticos (imágenes, iconos, etc.)
├── database/            # Modelos y conexión a la base de datos
├── output_pdf/          # Lugar donde se guardaran los Documentos de control en formato PDF
├── storage/             # Documentos o archivos generados por usuarios
├── tests/               # Scripts de pruebas(reset, creación de datos, etc.)
├── utils/               # Funciones Auxiliares(hashing, validaciones, etc.)
├── views/               # Vistas principales de la interfaz
├── credentials.json     # Archivo de credenciales
├── main.py              # Punto de entrada de la aplicación
├── requirements.txt     # Lista de dependencias del proyecto
└── .gitignore           # Exclusiones para Git
```

---

## ⚙️ Requisitos

- Python 3.10 o superior
- Librerías listadas en `requirements.txt`

Crear y activar entorno virtual

```bash
python3 -m venv venv       # En Windows: python -m venv venv
source venv/bin/activate   # En Windows: venv\Scipts\activate   
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Cómo ejecutar

Para crear/resetear la base datos para pruebas
```bash
python -m tests.reset_db
```

Crear empresas en la base datos para pruebas
```bash
python -m tests.create_company # Empresas
python -m tests.create_document # Documentos
python -m tests.create_user # usuarios
```

Ejecutar la app

```bash
python main.py
# o usando flet 
flet main.py
```
Para vista movil:

```bash
python main.py --ios # Para iOS 
flet main.py --android # Para Android 
```
---

# ✅ ¿Cómo usarlo?
- Clona el repositorio.
```bash
git clone https://github.com/AaronCodesDev/TransControl.git
```
- Instala las dependencias.
- Ejecuta `main.py` o `flet main.py` para iniciar la aplicación.

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**.  
Puedes usarlo, modificarlo y distribuirlo libremente.

---

## ✨ Estado actual

🚧 Proyecto en desarrollo — Se están implementando nuevas funcionalidades y mejoras de interfaz.

---
