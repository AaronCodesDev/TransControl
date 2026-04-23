from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os


def _draw_signature_image(c, img_path: str, x: float, y_bottom: float,
                           box_w: float = 150, box_h: float = 45):
    """
    Dibuja una imagen de firma escalada y centrada dentro del recuadro.
    x        : borde izquierdo del recuadro
    y_bottom : borde inferior del recuadro
    box_w/h  : dimensiones máximas del recuadro
    """
    try:
        reader = ImageReader(img_path)
        iw, ih = reader.getSize()
        ratio = min(box_w / iw, box_h / ih)
        w, h = iw * ratio, ih * ratio
        # Centrar dentro del recuadro
        x_centered = x + (box_w - w) / 2
        y_centered = y_bottom + (box_h - h) / 2
        c.drawImage(reader, x_centered, y_centered, width=w, height=h, mask='auto')
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
        _draw_signature_image(c, firma_cargador_img, x=52, y_bottom=122, box_w=150, box_h=45)
    else:
        c.setFont("Helvetica", 13)
        c.drawString(50, 150, f"{datos.get('firma_cargador', '')}")

    # Firma transportista: primero imagen, si no texto
    firma_transp_img = datos.get('firma_transportista_img')
    if firma_transp_img and os.path.exists(firma_transp_img):
        _draw_signature_image(c, firma_transp_img, x=322, y_bottom=122, box_w=150, box_h=45)
    else:
        c.setFont("Helvetica", 13)
        c.drawString(320, 150, f"{datos.get('firma_transportista', '')}")

    # ── Segunda página: Albarán adjunto (imagen) ─────────
    albaran_path = datos.get('albaran_path')
    if albaran_path and os.path.exists(albaran_path):
        ext = os.path.splitext(albaran_path)[1].lower()
        if ext != '.pdf':
            # Dibujar directamente en el mismo canvas (sin pypdf)
            c.showPage()
            c.setFont("Helvetica-Bold", 13)
            c.setFillColorRGB(0.18, 0.49, 0.20)
            c.drawString(50, height - 50, "Albarán adjunto")
            c.setFillColorRGB(0, 0, 0)
            try:
                img = ImageReader(albaran_path)
                iw, ih = img.getSize()
                max_w, max_h = width - 100, height - 120
                ratio = min(max_w / iw, max_h / ih)
                w, h = iw * ratio, ih * ratio
                c.drawImage(img, 50, (height - 80) - h, width=w, height=h, mask='auto')
            except Exception:
                c.setFont("Helvetica", 11)
                c.setFillColorRGB(0.5, 0.5, 0.5)
                c.drawString(50, height - 90, f"No se pudo cargar la imagen: {os.path.basename(albaran_path)}")

    c.save()

    # ── Si el albarán es un PDF, concatenarlo ────────────
    if albaran_path and os.path.exists(albaran_path):
        ext = os.path.splitext(albaran_path)[1].lower()
        if ext == '.pdf':
            try:
                from pypdf import PdfWriter, PdfReader
                import tempfile, shutil
                writer = PdfWriter()
                for path in [salida_path, albaran_path]:
                    reader = PdfReader(path)
                    for page in reader.pages:
                        writer.add_page(page)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp_path = tmp.name
                with open(tmp_path, 'wb') as f:
                    writer.write(f)
                shutil.move(tmp_path, salida_path)
            except Exception:
                pass  # pypdf no instalado o error — el PDF principal sigue válido
