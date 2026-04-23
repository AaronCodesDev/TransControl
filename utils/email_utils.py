"""
Utilidad para enviar el PDF de un documento por email a la empresa contratante.
Usa SMTP con autenticación (compatible con Gmail con contraseña de aplicación).

Configuración: crea un archivo config/email_config.json con:
{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "email_remitente": "tucorreo@gmail.com",
    "password": "tu_contraseña_de_aplicacion"
}
"""

import smtplib
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage


CONFIG_PATH = "config/email_config.json"


def _load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(
            f"No se encontró el archivo de configuración de email en '{CONFIG_PATH}'. "
            "Créalo con los datos SMTP de tu cuenta."
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def enviar_pdf_por_email(
    pdf_path: str,
    destinatario_email: str,
    destinatario_nombre: str,
    remitente_nombre: str,
    doc_info: dict,
) -> str:
    """
    Envía el PDF por email al destinatario.

    Args:
        pdf_path: Ruta absoluta al archivo PDF.
        destinatario_email: Email de la empresa contratante.
        destinatario_nombre: Nombre de la empresa.
        remitente_nombre: Nombre del transportista.
        doc_info: Dict con 'origen', 'destino', 'fecha', 'matricula'.

    Returns:
        Mensaje de éxito o lanza excepción.
    """
    config = _load_config()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"El archivo PDF no existe: {pdf_path}")

    msg = MIMEMultipart("mixed")
    msg["From"] = f"{remitente_nombre} <{config['email_remitente']}>"
    msg["To"] = f"{destinatario_nombre} <{destinatario_email}>"
    msg["Subject"] = (
        f"Documento de transporte — {doc_info.get('origen', '')} → {doc_info.get('destino', '')} "
        f"({doc_info.get('fecha', '')})"
    )

    # Cuerpo HTML
    cuerpo_html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333">
      <div style="max-width:560px;margin:0 auto">
        <div style="background:#2E7D32;padding:24px;border-radius:12px 12px 0 0;text-align:center">
          <h2 style="color:#fff;margin:0">🚚 TransControl</h2>
          <p style="color:rgba(255,255,255,0.8);margin:6px 0 0">Gestión de documentos de transporte</p>
        </div>
        <div style="background:#fff;padding:28px;border:1px solid #E0E0E0;border-top:none;border-radius:0 0 12px 12px">
          <p>Estimado/a <strong>{destinatario_nombre}</strong>,</p>
          <p>Le adjuntamos el documento de transporte correspondiente al siguiente servicio:</p>
          <table style="width:100%;border-collapse:collapse;margin:16px 0">
            <tr style="background:#F1F8E9">
              <td style="padding:8px 12px;font-weight:bold;color:#2E7D32;border-radius:6px">Origen</td>
              <td style="padding:8px 12px">{doc_info.get('origen', '—')}</td>
            </tr>
            <tr>
              <td style="padding:8px 12px;font-weight:bold;color:#2E7D32">Destino</td>
              <td style="padding:8px 12px">{doc_info.get('destino', '—')}</td>
            </tr>
            <tr style="background:#F1F8E9">
              <td style="padding:8px 12px;font-weight:bold;color:#2E7D32">Fecha</td>
              <td style="padding:8px 12px">{doc_info.get('fecha', '—')}</td>
            </tr>
            <tr>
              <td style="padding:8px 12px;font-weight:bold;color:#2E7D32">Matrícula</td>
              <td style="padding:8px 12px">{doc_info.get('matricula', '—')}</td>
            </tr>
          </table>
          <p style="color:#666;font-size:13px">El documento PDF se adjunta a este correo para su archivo.</p>
          <hr style="border:none;border-top:1px solid #EEE;margin:20px 0">
          <p style="font-size:12px;color:#999">Enviado por <strong>{remitente_nombre}</strong> mediante TransControl</p>
        </div>
      </div>
    </body></html>
    """
    msg.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    # Adjuntar PDF
    with open(pdf_path, "rb") as f:
        pdf_part = MIMEApplication(f.read(), _subtype="pdf")
        pdf_part.add_header(
            "Content-Disposition",
            "attachment",
            filename=os.path.basename(pdf_path),
        )
        msg.attach(pdf_part)

    # Enviar
    with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
        server.ehlo()
        server.starttls()
        server.login(config["email_remitente"], config["password"])
        server.sendmail(config["email_remitente"], destinatario_email, msg.as_string())

    return f"✅ Email enviado correctamente a {destinatario_email}"


def config_exists() -> bool:
    """Comprueba si la configuración de email está presente."""
    return os.path.exists(CONFIG_PATH)


def save_config(smtp_host: str, smtp_port: int, email: str, password: str):
    """Guarda la configuración SMTP."""
    os.makedirs("config", exist_ok=True)
    data = {
        "smtp_host": smtp_host,
        "smtp_port": smtp_port,
        "email_remitente": email,
        "password": password,
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
