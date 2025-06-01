from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Date, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from database.db import Base , SessionLocal
from datetime import datetime
class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), index=True)
    apellido = Column(String(50), index=True)
    nif = Column(String(30), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    contrasena = Column(String(128))
    direccion = Column(String(200), nullable=True)
    ciudad = Column(String(50), nullable=True)
    provincia = Column(String(50), nullable=True)
    codigo_postal = Column(String(20), nullable=True)
    telefono = Column(String(30), nullable=True)
    fecha_creacion = Column(DateTime)
    rol = Column(String(20))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)  # Para relaciones jerárquicas
    is_admin = Column(Boolean, default=False)
        
    empresas = relationship('Empresas', back_populates='usuario')

    documentos = relationship('Documentos', back_populates='usuario')
    
class Empresas(Base):
    __tablename__ = 'empresas'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    direccion = Column(String(200))
    codigo_postal = Column(String(20))
    ciudad = Column(String(50))
    provincia = Column(String(50))
    cif = Column(String(20), unique=True, index=True)
    telefono = Column(String(30))
    email = Column(String(100), unique=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'),nullable=False)
    fecha_creacion = Column(DateTime)
        
    usuario = relationship('Usuario', back_populates='empresas')
    
    
    # Crear relaciones entre documentos y empresas
    documentos_como_transportista = relationship(
        'Documentos',
        foreign_keys='Documentos.empresas_id_transportista',
        back_populates='transportista'
        )
    
    documentos_como_contratante = relationship(
        'Documentos',
        foreign_keys='Documentos.empresas_id_contratante',
        back_populates='contratante'
    )
    
class Documentos(Base):
    __tablename__ = 'documentos_control'

    id = Column(Integer, primary_key=True, index=True)
    usuarios_id = Column(Integer, ForeignKey('usuarios.id'))
    empresas_id_transportista = Column(Integer, ForeignKey('empresas.id'))
    empresas_id_contratante = Column(Integer, ForeignKey('empresas.id'))
    lugar_origen = Column(String(200), nullable=False)
    lugar_destino = Column(String(200), nullable=False)
    fecha_transporte = Column(Date) #Fecha realizacion del transporte
    fecha_creacion = Column(Date) # Fecha de creacion del documento
    matricula_vehiculo = Column(String(20), nullable=False)
    matricula_semiremolque = Column(String(20))
    naturaleza_carga = Column(String(200), nullable=False)
    peso = Column(Float, nullable=False)
    firma_cargador = Column(String(100)) 
    firma_transportista = Column(String(100))
    
    usuario = relationship('Usuario', back_populates='documentos')
    transportista = relationship('Empresas',
                                    foreign_keys=[empresas_id_transportista],
                                    back_populates='documentos_como_transportista'
    )
    
    contratante = relationship('Empresas',
                                    foreign_keys=[empresas_id_contratante],
                                    back_populates='documentos_como_contratante'
        )
