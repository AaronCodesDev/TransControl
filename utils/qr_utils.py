import qrcode
import io
import base64


def generate_qr_base64(data: str) -> str:
    """Genera un código QR a partir de un string y lo devuelve en base64 puro (para ft.Image src_base64)."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def build_document_qr_text(doc) -> str:
    """
    Construye el contenido del QR para un documento.
    Si el documento tiene archivo PDF, el QR apunta directamente a la URL
    del servidor local para poder abrirlo desde el móvil.
    Si no hay servidor activo, incluye la información textual del documento.
    """
    # Intentar generar URL directa al PDF
    if doc.archivo:
        try:
            from utils.doc_server import get_doc_url
            return get_doc_url(doc.archivo)
        except Exception:
            pass

    # Fallback: información textual del documento
    contratante = doc.contratante.nombre if doc.contratante else "Sin asignar"
    cif = doc.contratante.cif if doc.contratante else ""
    fecha = doc.fecha_transporte.strftime("%d/%m/%Y") if doc.fecha_transporte else ""

    lines = [
        "=== TransControl ===",
        f"ID Documento: {doc.id}",
        f"Empresa: {contratante}",
        f"CIF: {cif}",
        f"Origen: {doc.lugar_origen}",
        f"Destino: {doc.lugar_destino}",
        f"Fecha: {fecha}",
        f"Matrícula: {doc.matricula_vehiculo}",
    ]
    return "\n".join(lines)
