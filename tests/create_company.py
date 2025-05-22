from database.models import Empresas, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from faker import Faker
import random

faker = Faker('es_ES')

def create_db():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Base.metadata.create_all(engine)
    
def create_company():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Session = sessionmaker(bind=engine)
    session = Session()


    empresa = Empresas(nombre=faker.company(),
                        direccion=faker.address(),
                        codigo_postal=faker.postcode(),
                        ciudad=faker.city(),
                        provincia=faker.state(),
                        cif=faker.ssn(),
                        telefono=faker.phone_number(),
                        email=faker.email(),
                        fecha_creacion= datetime.today().date(),
                        )

    session.add(empresa)
    session.commit()
    empresas = session.query(Empresas).all()
    print("Empresas en la base de datos:")
    print("=====================================")
    for e in empresas:
        print(f"{e.id} - {e.nombre} ( {e.ciudad} )")
    session.close()

if __name__ == "__main__":
    create_db()
    create_company()