from database.models import Base, Documentos, Usuario, Empresas
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from faker import Faker
from datetime import datetime, date

fake = Faker('es_ES')
matricula = fake.bothify(text='####-???')
matricula_semi = fake.bothify(text='R-####-???')
peso_int = int(fake.bothify(text='####'))
fecha_transporte = datetime.strptime(fake.date(), '%Y-%m-%d').date()
fecha_creacion = date.today()

    
def create_db():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Base.metadata.create_all(engine)
    
def create_documents():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    usuario = session.query(Usuario).first()
    empresa = session.query(Empresas).first()

    # Creacion de documentos fake
    document = Documentos(
            usuarios_id = usuario.id,
            empresas_nombres = empresa.nombre,
            empresas_id_transportista = empresa.id,
            empresas_id_contratante = empresa.id,
            lugar_origen = fake.city(),
            lugar_destino = fake.city(),
            fecha_transporte = fecha_transporte,
            fecha_creacion = fecha_creacion,
            matricula_vehiculo = matricula,  
            matricula_semiremolque = matricula_semi,
            naturaleza_carga = 'Palets',
            peso = peso_int,
            firma_cargador = 'Cargador',
            firma_transportista = 'Transportista'
    )

    session.add(document)
    session.commit()
    
    #Mostrar Docs generado
    documents = session.query(Documentos).all()
    for e in documents:
        print(f"{e.id} - Carga de {e.empresas_nombres} {e.empresas_id_contratante} - {e.lugar_origen} para {e.lugar_destino} con el peso ({e.peso} Kg.)")
    session.close()

if __name__ == "__main__":
    create_db()
    create_documents()