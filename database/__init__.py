from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Configuración de la DB (SQLite)
DATABASE_URL = "sqlite:///database/transcontrol.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Crea todas las tablas en la base de datos"""
    from . import models
    Base.metadata.create_all(bind=engine)