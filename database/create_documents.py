from models import Documentos
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

def create_documents():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    documento = Documentos('Docuemnto 1', tipo='PDF')
    session.add(documento)
    session.commit()
    session.close()
    