from database.models import Base, Documentos, Usuario, Empresas
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from faker import Faker
from datetime import datetime, date
from utils.create_pdf import rellenar_pdf_con_fondo
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

fake = Faker('es_ES')

# Datos aleatorios
matricula = fake.bothify(text='####-???')
matricula_semi = fake.bothify(text='R-####-???')
peso_int = int(fake.bothify(text='####'))
fecha_transporte = datetime.strptime(fake.date(), '%Y-%m-%d').date()
fecha_creacion = date.today()

def generar_pdf_simple(path="output/test_solo_reportlab.pdf"):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 14)
    c.drawString(100, 800, "✅ Esto es un PDF generado solo con ReportLab.")
    c.drawString(100, 780, "Si lo ves, el sistema funciona.")
    c.save()

def create_db():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Base.metadata.create_all(engine)

def create_documents():
    engine = create_engine('sqlite:///database/transcontrol.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    usuario = session.query(Usuario).first()
    empresa = session.query(Empresas).first()

    if not usuario or not empresa:
        print("No hay usuarios o empresas en la base de datos.")
        return

    # Crear documento fake
    document = Documentos(
        usuarios_id=usuario.id,
        empresas_id_transportista=empresa.id,
        empresas_id_contratante=empresa.id,
        lugar_origen=fake.city(),
        lugar_destino=fake.city(),
        fecha_transporte=fecha_transporte,
        fecha_creacion=fecha_creacion,
        matricula_vehiculo=matricula,
        matricula_semiremolque=matricula_semi,
        naturaleza_carga='Palets',
        peso=peso_int,
        firma_cargador='Cargador',
        firma_transportista='Transportista'
    )

    session.add(document)
    session.commit()

    # Preparar datos para PDF
    datos = {
        'fecha': document.fecha_creacion.strftime('%d/%m/%Y'),
        'contratante': empresa.nombre,
        'direccion_contratante': empresa.direccion,
        'poblacion_contratante': empresa.ciudad,
        'provincia_contratante': empresa.provincia,
        'codigo_postal_contratante': empresa.codigo_postal,
        'telefono_contratante': empresa.telefono,
        'transportista': empresa.nombre,
        'direccion_transportista': empresa.direccion,
        'poblacion_transportista': empresa.ciudad,
        'provincia_transportista': empresa.provincia,
        'codigo_postal_transportista': empresa.codigo_postal,
        'telefono_transportista': empresa.telefono,
        'origen': document.lugar_origen,
        'destino': document.lugar_destino,
        'naturaleza': document.naturaleza_carga,
        'peso': document.peso,
        'matricula': document.matricula_vehiculo,
        'matricula_remolque': document.matricula_semiremolque
    }


    salida_pdf = f"output_pdf/documento_{document.id}.pdf"
    #rellenar_pdf(datos, plantilla_path="assets/documento_control.pdf", salida_path=salida_pdf)
    rellenar_pdf_con_fondo(datos, salida_path="output_pdf/test_visible.pdf")


    # Mostrar todos los documentos existentes
    documents = session.query(Documentos).all()
    for e in documents:
        print(f"{e.id} - Carga de {e.empresas_id_contratante} - {e.lugar_origen} para {e.lugar_destino} con el peso ({e.peso} Kg.)")

    session.close()

if __name__ == "__main__":
    create_db()
    create_documents()
    generar_pdf_simple()
    print("PDF generado correctamente.")