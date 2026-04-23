from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os


def _draw_signature_image(c, img_path: str, x: float, y: float,
                           max_w: float = 160, max_h: float = 60):
    """Dibuja una imagen de firma/sello escalada y centrada en la posición dada."""
    try:
        reader = ImageReader(img_path)
        iw, ih = reader.getSize()
        ratio = min(max_w / iw, max_h / ih)
        w, h = iw * ratio, ih * ratio
        c.drawImage(reader, x, y - h, width=w, height=h, mask='auto')
    except Exception:
        pass  # Si falla la imagen, simplemente no dibuja nada


def rellenar_pdf_con_fondo(datos, fondo_path="assets/documento_control.png",
                           salida_path="output_pdf/documento_final.pdf"):
    os.makedirs(os.path.dirname(salida_path), exist_ok=True)

    c = canvas.Canvas(salida_path, pagesize=A4)
    width, height = A4

    # ── Fondo ──────────────────────────────────────────
    fondo = ImageReader(fondo_path)
    c.drawImage(fondo, 0, 0, width=width, height=height)

    # ── Datos Contratante ───────────────────────────────
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 520, f"{datos['contratante']}")

    c.setFont("Helvetica", 13)
    c.drawString(50, 500, f"CIF: {datos.get('cif_contratante', '')}")
    c.drawString(50, 480, f"{datos['direccion_contratante']}")
    c.drawString(50, 462, f"{datos['poblacion_contratante']} ({datos['codigo_postal_contratante']})")
    c.drawString(50, 444, f"{datos['provincia_contratante']}")
    c.drawString(50, 426, f"Tel: {datos['telefono_contratante']}")

    # ── Datos Transportista ─────────────────────────────
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 680, f"{datos['transportista']}")

    c.setFont("Helvetica", 13)
    c.drawString(50, 660, f"NIF: {datos.get('nif_transportista', '')}")
    c.drawString(50, 640, f"{datos['direccion_transportista']}")
    c.drawString(50, 622, f"{datos['poblacion_transportista']} ({datos['codigo_postal_transportista']})")
    c.drawString(50, 604, f"{datos['provincia_transportista']}")
    c.drawString(50, 586, f"Tel: {datos['telefono_transportista']}")

    # ── Ruta ────────────────────────────────────────────
    c.setFont("Helvetica", 14)
    c.drawString(50, 360, f"{datos['origen']}")
    c.drawString(310, 360, f"{datos['destino']}")

    # ── Fecha ───────────────────────────────────────────
    c.setFont("Helvetica", 14)
    c.drawString(100, 290, f"{datos['fecha']}")

    # ── Carga ───────────────────────────────────────────
    c.drawString(50, 220, f"{datos['naturaleza']}")
    c.drawString(370, 220, f"{datos['peso']} kg")

    # ── Matrículas ──────────────────────────────────────
    c.setFont("Helvetica", 13)
    c.drawString(310, 300, f"Matrícula: {datos['matricula']}")
    c.drawString(310, 282, f"Remolque: {datos.get('matricula_remolque', '')}")

    # ── Firmas ──────────────────────────────────────────
    # Firma cargador: primero imagen, si no texto
    firma_cargador_img = datos.get('firma_cargador_img')
    if firma_cargador_img and os.path.exists(firma_cargador_img):
        _draw_signature_image(c, firma_cargador_img, x=50, y=165, max_w=160, max_h=60)
    else:
        c.setFont("Helvetica", 13)
        c.drawString(50, 150, f"{datos.get('firma_cargador', '')}")

    # Firma transportista: primero imagen, si no texto
    firma_transp_img = datos.get('firma_transportista_img')
    if firma_transp_img and os.path.exists(firma_transp_img):
        _draw_signature_image(c, firma_transp_img, x=320, y=165, max_w=160, max_h=60)
    else:
        c.setFont("Helvetica", 13)
        c.drawString(320, 150, f"{datos.get('firma_transportista', '')}")

    c.save()

    # ── Segunda página: Albarán adjunto ─────────────────
    albaran_path = datos.get('albaran_path')
    if albaran_path and os.path.exists(albaran_path):
        _append_albaran(salida_path, albaran_path)


def _append_albaran(pdf_path: str, albaran_path: str):
    """
    Añade una segunda página al PDF con la imagen del albarán.
    Si el albarán ya es un PDF, lo concatena usando pypdf si está disponible,
    si no, lo incrusta como imagen.
    """
    ext = os.path.splitext(albaran_path)[1].lower()

    if ext == '.pdf':
        # Intentar concatenar PDFs
        try:
            from pypdf import PdfWriter, PdfReader
            writer = PdfWriter()
            for path in [pdf_path, albaran_path]:
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
            # Sobreescribir el original
            import tempfile, shutil
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp_path = tmp.name
            with open(tmp_path, 'wb') as f:
                writer.write(f)
            shutil.move(tmp_path, pdf_path)
        except ImportError:
            pass  # pypdf no instalado, omitir concatenación
    else:
        # Es imagen: añadir segunda página con la imagen
        try:
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.utils import ImageReader
            from pypdf import PdfWriter, PdfReader
            import tempfile

            width, height = A4
            tmp_page_path = tempfile.mktemp(suffix='.pdf')

            c2 = pdf_canvas.Canvas(tmp_page_path, pagesize=A4)
            c2.setFont("Helvetica-Bold", 12)
            c2.setFillColorRGB(0.18, 0.49, 0.20)
            c2.drawString(50, height - 50, "Albarán adjunto")
            c2.setFillColorRGB(0, 0, 0)

            img = ImageReader(albaran_path)
            iw, ih = img.getSize()
            max_w, max_h = width - 100, height - 120
            ratio = min(max_w / iw, max_h / ih)
            w, h = iw * ratio, ih * ratio
            c2.drawImage(img, 50, (height - 80) - h, width=w, height=h)
            c2.save()

            # Concatenar
            writer = PdfWriter()
            for path in [pdf_path, tmp_page_path]:
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
            import tempfile as tf, shutil
            with tf.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp_path = tmp.name
            with open(tmp_path, 'wb') as f:
                writer.write(f)
            shutil.move(tmp_path, pdf_path)
            os.remove(tmp_page_path)
        except Exception:
            pass  # Si falla, el PDF sigue siendo válido sin la segunda página
