from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os

def rellenar_pdf_con_fondo(datos, fondo_path="assets/documento_control.png",
                           salida_path="output_pdf/documento_final.pdf"):
    os.makedirs(os.path.dirname(salida_path), exist_ok=True)
    
    c = canvas.Canvas(salida_path, pagesize=A4)
    width, height = A4

    # Fondo como imagen
    fondo = ImageReader(fondo_path)
    c.drawImage(fondo, 0, 0, width=width, height=height)

    # Texto sobre el fondo
    c.setFont("Helvetica", 20)

    # Fecha
    c.drawString(100, 290, f"{datos['fecha']}")

    # Datos Contratante
    c.drawString(50, 520, f"{datos['contratante']}")
    c.drawString(50, 490, f"{datos['direccion_contratante']}")
    c.drawString(50, 470, f"{datos['poblacion_contratante']} ({datos['codigo_postal_contratante']})")
    c.drawString(50, 450, f"{datos['provincia_contratante']}")
    c.drawString(50, 430, f"Tel: {datos['telefono_contratante']}")


    # Datos Transportista
    c.drawString(50, 680, f"{datos['transportista']}")
    c.drawString(50, 650, f"{datos['direccion_transportista']}")
    c.drawString(50, 630, f"{datos['poblacion_transportista']} ({datos['codigo_postal_transportista']})")
    c.drawString(50, 610, f"{datos['provincia_transportista']}")
    c.drawString(50, 590, f"Tel: {datos['telefono_transportista']}")

    # Datos del transporte
    c.drawString(50, 360, f"{datos['origen']}")
    c.drawString(310, 360, f"{datos['destino']}")
    c.drawString(50, 220, f"{datos['naturaleza']}")
    c.drawString(370, 220, f"{datos['peso']} kg")

    # Matrículas
    c.setFont("Helvetica", 16)
    c.drawString(310, 300, f"Matrícula: {datos['matricula']}")
    c.drawString(310, 280, f"Remolque: {datos['matricula_remolque']}")
    
    # Firmas
    c.setFont("Helvetica", 20)
    c.drawString(50, 150, f"{datos['firma_cargador']}")
    c.drawString(310, 150, f"{datos['firma_transportista']}")

    c.save()
