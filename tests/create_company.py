from database.models import Empresas, Usuario, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from faker import Faker

faker = Faker('es_ES')

def create_db():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Base.metadata.create_all(engine)

def create_company():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Obtener o crear un usuario
    usuario = session.query(Usuario).first()
    if not usuario:
        usuario = Usuario(
            nombre=faker.first_name(),
            apellido=faker.last_name(),
            email=faker.email(),
            password="hashed_password",  # Pon aquí algo de prueba o usa hash real
            rol="admin"
        )
        session.add(usuario)
        session.commit()

    # Crear empresa asociada al usuario
    empresa = Empresas(
        nombre=faker.company(),
        direccion=faker.address(),
        codigo_postal=faker.postcode(),
        ciudad=faker.city(),
        provincia=faker.state(),
        cif=faker.ssn(),
        telefono=faker.phone_number(),
        email=faker.email(),
        fecha_creacion=datetime.today().date(),
        usuario_id=usuario.id  # ✅ Esta es la clave para evitar el error
    )

    session.add(empresa)
    session.commit()

    empresas = session.query(Empresas).all()
    print("Empresas en la base de datos:")
    print("=====================================")
    for e in empresas:
        print(f"{e.id} - {e.nombre} ({e.ciudad})")

    session.close()

if __name__ == "__main__":
    create_db()
    create_company()
