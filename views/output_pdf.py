import os
import subprocess
import sys
import time
import flet as ft
from database import SessionLocal
from database.models import Documentos
from sqlalchemy.orm import joinedload
from utils.email_utils import enviar_pdf_por_email, config_exists, save_config


def open_with_system_viewer(path: str):
    """Abre el archivo con el visor predeterminado del sistema operativo."""
    abs_path = os.path.abspath(path)
    if sys.platform == "win32":
        os.startfile(abs_path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", abs_path])
    else:
        subprocess.Popen(["xdg-open", abs_path])


class OutputPDFView:
    def __init__(self, page: ft.Page, theme_button: ft.Control, doc_id: int):
        self.page = page
        self.theme_button = theme_button
        self.doc_id = doc_id

    def build(self) -> ft.View:
        session = SessionLocal()
        doc = (
            session.query(Documentos)
            .options(
                joinedload(Documentos.contratante),
                joinedload(Documentos.transportista),
                joinedload(Documentos.usuario),
            )
            .filter_by(id=self.doc_id)
            .first()
        )

        # Extraer todo antes de cerrar la sesión para evitar lazy-load tras cierre
        if doc:
            d = {
                'archivo':             doc.archivo,
                'lugar_origen':        doc.lugar_origen,
                'lugar_destino':       doc.lugar_destino,
                'naturaleza_carga':    doc.naturaleza_carga,
                'matricula_vehiculo':  doc.matricula_vehiculo,
                'fecha_transporte':    doc.fecha_transporte.strftime("%d/%m/%Y") if doc.fecha_transporte else "—",
                'fecha_creacion':      doc.fecha_creacion.strftime("%d/%m/%Y") if doc.fecha_creacion else "—",
                'contratante_nombre':  doc.contratante.nombre if doc.contratante else "—",
                'contratante_email':   (doc.contratante.email or '') if doc.contratante else '',
                'usuario_nombre':      f"{doc.usuario.nombre} {doc.usuario.apellido}" if doc.usuario else "—",
            }
        else:
            d = None
        session.close()

        ab_color = getattr(self.page, 'tc_theme', {}).get('appbar_color', '#1A1A1A')
        accent = getattr(self.page, 'tc_theme', {}).get('accent', '#22C55E')

        appbar = ft.AppBar(
            title=ft.Text("Documento guardado", weight=ft.FontWeight.W_600),
            center_title=True,
            bgcolor=ab_color,
            automatically_imply_leading=False,
            actions=[self.theme_button],
            toolbar_height=56,
        )

        if not d or not d['archivo']:
            return ft.View(
                route=f"/output_pdf/{self.doc_id}",
                appbar=appbar,
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=16,
                            controls=[
                                ft.Icon(ft.Icons.ERROR_OUTLINE, size=72, color=ft.Colors.GREY_400),
                                ft.Text("Documento no encontrado", size=18, color=ft.Colors.GREY_600),
                                ft.FilledButton(
                                    "Ir a documentos",
                                    icon=ft.Icons.ARROW_BACK,
                                    on_click=lambda e: self.page.go("/documents"),
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                                ),
                            ],
                        ),
                    )
                ],
            )

        pdf_path = os.path.abspath(f"assets/docs/{d['archivo']}")
        file_exists = os.path.exists(pdf_path)
        doc_info_email = {
            'origen':    d['lugar_origen'],
            'destino':   d['lugar_destino'],
            'fecha':     d['fecha_creacion'],
            'matricula': d['matricula_vehiculo'],
        }

        # ── helpers ───────────────────────────────────────
        def _info_row(icon, label, value):
            return ft.Row([
                ft.Icon(icon, size=15, color=ft.Colors.GREY_500),
                ft.Column(spacing=0, controls=[
                    ft.Text(label, size=10, color=ft.Colors.GREY_400),
                    ft.Text(value or "—", size=13, weight=ft.FontWeight.W_500),
                ]),
            ], spacing=10)

        def abrir_pdf(e):
            if file_exists:
                try:
                    open_with_system_viewer(pdf_path)
                except Exception as ex:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"No se pudo abrir el PDF: {ex}"),
                        bgcolor=ft.Colors.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()

        def enviar_email(e):
            if not d['contratante_email']:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("La empresa no tiene email registrado"),
                    bgcolor=ft.Colors.ORANGE_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            if not config_exists():
                self._show_smtp_dialog(d, pdf_path, doc_info_email)
            else:
                self._show_email_dialog(d, pdf_path, doc_info_email)

        # ── success banner ────────────────────────────────
        success_banner = ft.Container(
            border_radius=14,
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREEN_500),
            border=ft.border.all(1, ft.Colors.with_opacity(0.25, ft.Colors.GREEN_500)),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=ft.Colors.GREEN_500, size=22),
                ft.Column(spacing=1, controls=[
                    ft.Text("Documento creado", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_600),
                    ft.Text("El PDF está listo para abrir o enviar", size=11, color=ft.Colors.GREEN_700),
                ]),
            ], spacing=12),
        )

        # ── document info card ────────────────────────────
        info_card = ft.Container(
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            shadow=ft.BoxShadow(
                blur_radius=16,
                color=ft.Colors.with_opacity(0.07, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row([
                        ft.Container(
                            width=40, height=40, border_radius=20,
                            bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.RED_400),
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.Icons.PICTURE_AS_PDF_ROUNDED, size=22, color=ft.Colors.RED_400),
                        ),
                        ft.Column(spacing=1, expand=True, controls=[
                            ft.Text(d['contratante_nombre'], size=15, weight=ft.FontWeight.W_700),
                            ft.Text(d['archivo'] or "—", size=10, color=ft.Colors.GREY_500),
                        ]),
                    ], spacing=12),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Column(expand=1, spacing=4, controls=[
                            ft.Text("Origen", size=10, color=ft.Colors.GREY_400),
                            ft.Text(d['lugar_origen'] or "—", size=12, weight=ft.FontWeight.W_500),
                        ]),
                        ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color=ft.Colors.GREY_400, size=16),
                        ft.Column(expand=1, spacing=4, controls=[
                            ft.Text("Destino", size=10, color=ft.Colors.GREY_400),
                            ft.Text(d['lugar_destino'] or "—", size=12, weight=ft.FontWeight.W_500),
                        ]),
                    ]),
                    ft.Divider(height=1),
                    _info_row(ft.Icons.CALENDAR_TODAY_OUTLINED, "Fecha de transporte", d['fecha_transporte']),
                    _info_row(ft.Icons.DIRECTIONS_CAR_OUTLINED, "Matrícula", d['matricula_vehiculo']),
                    _info_row(ft.Icons.INVENTORY_2_OUTLINED, "Carga", d['naturaleza_carga']),
                    # Estado del archivo
                    ft.Container(
                        border_radius=8,
                        bgcolor=ft.Colors.with_opacity(
                            0.08,
                            ft.Colors.GREEN_500 if file_exists else ft.Colors.ORANGE_500,
                        ),
                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                        content=ft.Row([
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE_OUTLINE if file_exists else ft.Icons.WARNING_AMBER_OUTLINED,
                                color=ft.Colors.GREEN_600 if file_exists else ft.Colors.ORANGE_600,
                                size=14,
                            ),
                            ft.Text(
                                "PDF generado correctamente" if file_exists else "Archivo no localizado",
                                size=12,
                                color=ft.Colors.GREEN_700 if file_exists else ft.Colors.ORANGE_700,
                            ),
                        ], spacing=6),
                    ),
                ],
            ),
        )

        # ── action buttons ────────────────────────────────
        btn_abrir = ft.FilledButton(
            "Abrir PDF",
            icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
            on_click=abrir_pdf,
            disabled=not file_exists,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                bgcolor=accent,
            ),
            expand=True,
            height=48,
        )
        btn_email = ft.OutlinedButton(
            "Enviar email",
            icon=ft.Icons.EMAIL_OUTLINED,
            on_click=enviar_email,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            expand=True,
            height=48,
        )
        btn_volver = ft.TextButton(
            "Ir a documentos",
            icon=ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED,
            on_click=lambda e: self.page.go("/documents"),
            style=ft.ButtonStyle(color=ft.Colors.GREY_500),
        )

        card_width = min(420, (self.page.width or 440) - 40)

        return ft.View(
            route=f"/output_pdf/{self.doc_id}",
            appbar=appbar,
            bgcolor=getattr(self.page, 'tc_theme', {}).get('bg', None),
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=20, vertical=24),
                    alignment=ft.alignment.top_center,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                        spacing=16,
                        controls=[
                            ft.Container(success_banner, width=card_width),
                            ft.Container(info_card, width=card_width),
                            ft.Container(
                                width=card_width,
                                content=ft.Row([btn_abrir, btn_email], spacing=10),
                            ),
                            ft.Container(
                                width=card_width,
                                alignment=ft.alignment.center,
                                content=btn_volver,
                            ),
                        ],
                    ),
                )
            ],
        )

    # ── email dialogs ──────────────────────────────────────────
    def _show_email_dialog(self, d: dict, pdf_path: str, doc_info: dict):
        """d es el dict de datos ya extraídos de la sesión."""
        email_dest = ft.TextField(
            label="Enviar a",
            value=d['contratante_email'],
            border_radius=10, filled=True, dense=True,
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
        )
        sending_text = ft.Text("", size=12, color=ft.Colors.GREY_600, visible=False)
        dialog = ft.AlertDialog(modal=True)

        def enviar(e):
            sending_text.value = "Enviando…"
            sending_text.visible = True
            self.page.update()
            dialog.open = False
            self.page.update()
            try:
                msg = enviar_pdf_por_email(
                    pdf_path=os.path.abspath(pdf_path),
                    destinatario_email=email_dest.value,
                    destinatario_nombre=d['contratante_nombre'],
                    remitente_nombre=d['usuario_nombre'],
                    doc_info=doc_info,
                )
                self.page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=ft.Colors.GREEN_700)
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Error al enviar: {ex}"), bgcolor=ft.Colors.ERROR,
                )
            self.page.snack_bar.open = True
            self.page.update()

        dialog.title = ft.Row([
            ft.Icon(ft.Icons.EMAIL_OUTLINED, color=ft.Colors.GREEN_700),
            ft.Text("Enviar por email", weight=ft.FontWeight.W_600),
        ], spacing=8)
        dialog.content = ft.Container(width=300, content=ft.Column(
            spacing=10, tight=True,
            controls=[email_dest, sending_text],
        ))
        dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._close(dialog),
                          style=ft.ButtonStyle(color=ft.Colors.GREY_600)),
            ft.FilledButton("Enviar", icon=ft.Icons.SEND_OUTLINED, on_click=enviar,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
        ]
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _show_smtp_dialog(self, d: dict, pdf_path: str, doc_info: dict):
        fs = dict(border_radius=10, filled=True, dense=True)
        smtp_host = ft.TextField(label="Servidor SMTP", value="smtp.gmail.com", **fs)
        smtp_port = ft.TextField(label="Puerto", value="587", keyboard_type=ft.KeyboardType.NUMBER, **fs)
        email_f = ft.TextField(label="Tu email remitente", **fs)
        password_f = ft.TextField(label="Contraseña de aplicación", password=True, can_reveal_password=True, **fs)
        error = ft.Text("", color=ft.Colors.ERROR, size=11, visible=False)
        dialog = ft.AlertDialog(modal=True)

        def guardar_y_enviar(e):
            if not all([email_f.value, password_f.value]):
                error.value = "Email y contraseña son obligatorios"
                error.visible = True
                self.page.update()
                return
            try:
                save_config(smtp_host.value, int(smtp_port.value), email_f.value, password_f.value)
                dialog.open = False
                self.page.update()
                self._show_email_dialog(d, pdf_path, doc_info)
            except Exception as ex:
                error.value = str(ex)
                error.visible = True
                self.page.update()

        dialog.title = ft.Row([
            ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=ft.Colors.GREEN_700),
            ft.Text("Configurar email", weight=ft.FontWeight.W_600),
        ], spacing=8)
        dialog.content = ft.Container(width=320, content=ft.Column(
            spacing=10, tight=True,
            controls=[
                ft.Text("Primera configuración SMTP:", size=12, color=ft.Colors.GREY_600),
                ft.Text("(Gmail → usa contraseña de aplicación)", size=11, color=ft.Colors.GREY_500, italic=True),
                smtp_host, smtp_port, email_f, password_f, error,
            ],
        ))
        dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._close(dialog),
                          style=ft.ButtonStyle(color=ft.Colors.GREY_600)),
            ft.FilledButton("Guardar y enviar", icon=ft.Icons.SEND_OUTLINED, on_click=guardar_y_enviar,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
        ]
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close(self, dialog):
        dialog.open = False
        self.page.update()
