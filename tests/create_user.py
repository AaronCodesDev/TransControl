from database.models import Usuario, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from database.models import Base, Usuario  # 👈 Corrige la importación si falla con '.models'
from utils.security import hash_password 
from faker import Faker

fake = Faker('es_ES')


def create_db():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Base.metadata.create_all(engine)
    
def create_users():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    hashed_password = hash_password('test')  # 👈 Ahora sí, ciframos la contraseña
    user = Usuario(
            nombre=fake.name(),
            apellido=fake.last_name(),
            nif=fake.ssn(),
            email=fake.email(),
            contrasena=hashed_password,
            fecha_creacion=datetime.today().date(),
            rol="user"
        )


    session.add(user)
    session.commit()
    users = session.query(Usuario).all()
    for e in users:
        print(f"{e.id} - {e.nombre} {e.apellido} ({e.email})")
    session.close()

if __name__ == "__main__":
    create_db()
    create_users()
    