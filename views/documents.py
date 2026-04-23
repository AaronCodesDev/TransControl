import flet as ft
import shutil
import os
from database.models import Documentos
from database.db import SessionLocal
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from utils.qr_utils import generate_qr_base64, build_document_qr_text
from utils.email_utils import enviar_pdf_por_email, config_exists, save_config


class DocumentsView:
    def __init__(self, page: ft.Page, theme_button, user=None):
        self.user = user
        self.page = page
        self.theme_button = theme_button
        self.documents = []
        self.filtered_documents = []
        self.search_term = ''
        self.table = ft.Column()
        self.dialog = ft.AlertDialog(modal=True, title=ft.Text(''), content=ft.Text(''), actions=[])

    def build(self):
        self._load_documents()

        admin_button = None
        if self.user and getattr(self.user, 'rol', '') == 'admin':
            admin_button = ft.IconButton(
                icon=ft.Icons.SECURITY,
                icon_color=ft.Colors.WHITE,
                tooltip='Panel de administración',
                on_click=lambda e: self.page.go('/admin'),
            )
        actions = [self.theme_button]
        if admin_button:
            actions.insert(0, admin_button)

        self.table.controls.clear()
        self.table.controls.append(self._build_documents_list())

        tc       = getattr(self.page, 'tc_theme', {})
        ab_color = tc.get('appbar_color', '#1B5E20')
        accent   = tc.get('accent', '#43A047')
        bg       = tc.get('bg', '#F8FBF8')
        is_dark  = tc.get('mode', 'light') == 'dark'

        header = ft.Container(
            padding=ft.padding.only(top=48, bottom=20, left=20, right=20),
            bgcolor=ab_color,
            content=ft.Column(spacing=10, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text('Documentos', size=20, weight=ft.FontWeight.W_700,
                                color=ft.Colors.WHITE),
                        ft.Row(spacing=0, controls=[
                            *(([admin_button]) if admin_button else []),
                            self.theme_button,
                        ]),
                    ],
                ),
                self._build_search_box(is_dark),
            ]),
        )

        body = ft.Container(
            expand=True,
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            bgcolor=bg,
            padding=ft.padding.only(left=16, right=16, top=20, bottom=90),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                controls=[self.table, self.dialog],
            ),
        )

        return ft.View(
            route='/documents',
            padding=0,
            bgcolor=bg,
            bottom_appbar=self._build_bottom_appbar(),
            floating_action_button=ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                bgcolor=accent,
                shape=ft.CircleBorder(),
                width=54, height=54,
                tooltip='Nuevo documento',
                on_click=lambda e: self.page.go('/create_document'),
            ),
            floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_FLOAT,
            controls=[
                ft.Column(
                    spacing=0,
                    expand=True,
                    controls=[header, body],
                )
            ],
        )

    def _load_documents(self):
        db = SessionLocal()
        try:
            if self.user:
                query = db.query(Documentos).options(
                    joinedload(Documentos.contratante),
                    joinedload(Documentos.transportista),
                    joinedload(Documentos.usuario),
                ).order_by(desc(Documentos.fecha_transporte))

                if getattr(self.user, 'rol', '') != 'admin':
                    query = query.filter(Documentos.usuarios_id == self.user.id)

                self.documents = query.all()
            else:
                self.documents = []

            self.filtered_documents = self.documents
        finally:
            db.close()

    def _build_documents_list(self):
        tc      = getattr(self.page, 'tc_theme', {})
        accent  = tc.get('accent', '#43A047')
        card_bg = tc.get('card', '#FFFFFF')
        is_dark = tc.get('mode', 'light') == 'dark'

        text_primary   = ft.Colors.WHITE if is_dark else '#1A1A1A'
        text_secondary = ft.Colors.with_opacity(0.55, ft.Colors.WHITE) if is_dark else '#555555'
        text_dim       = ft.Colors.with_opacity(0.40, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_400

        if not self.filtered_documents:
            return ft.Container(
                padding=40,
                alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=64, color=text_dim),
                        ft.Text("No hay documentos", size=16, color=text_secondary,
                                weight=ft.FontWeight.W_600),
                        ft.Text("Pulsa + para crear un documento", size=13, color=text_dim),
                    ],
                ),
            )

        cards = []
        for doc in self.filtered_documents:
            fecha_str = doc.fecha_transporte.strftime('%d/%m/%Y') if doc.fecha_transporte else '—'
            empresa   = doc.contratante.nombre if doc.contratante else '—'
            has_pdf   = bool(doc.archivo)

            badge = ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                border_radius=6,
                bgcolor=ft.Colors.with_opacity(0.15, accent) if has_pdf else ft.Colors.with_opacity(0.12, ft.Colors.ORANGE_400),
                content=ft.Text(
                    'PDF ✓' if has_pdf else 'Pendiente',
                    size=9, weight=ft.FontWeight.W_700,
                    color=accent if has_pdf else ft.Colors.ORANGE_400,
                ),
            )

            btn_qr = ft.IconButton(
                icon=ft.Icons.QR_CODE_2,
                icon_size=18,
                tooltip='Ver QR',
                icon_color=accent,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.with_opacity(0.10, accent),
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.padding.all(4),
                ),
                on_click=lambda e, d=doc: self._mostrar_dialogo_qr(d),
            )
            btn_view = ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                icon_size=18,
                tooltip='Ver documento',
                icon_color=accent,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.with_opacity(0.10, accent),
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.padding.all(4),
                ),
                on_click=(lambda e, d=doc: self.page.go(f'/output_pdf/{d.id}')) if has_pdf else None,
                disabled=not has_pdf,
            )
            btn_more = ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        text='Descargar PDF' if has_pdf else 'PDF no disponible',
                        icon=ft.Icons.DOWNLOAD_OUTLINED,
                        on_click=(lambda e, d=doc: self._descargar_documento(d)) if has_pdf else lambda e: None,
                    ),
                    ft.PopupMenuItem(
                        text='Enviar por email',
                        icon=ft.Icons.EMAIL_OUTLINED,
                        on_click=lambda e, d=doc: self._enviar_por_email(d),
                    ),
                    ft.PopupMenuItem(
                        text='Eliminar',
                        icon=ft.Icons.DELETE_OUTLINED,
                        on_click=lambda e, d=doc: self._delete_document(d),
                    ),
                ],
                content=ft.Container(
                    width=32, height=32,
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
                    alignment=ft.alignment.center,
                    content=ft.Icon(ft.Icons.MORE_VERT, size=16, color=text_secondary),
                ),
            )

            admin_user_row = []
            if self.user and getattr(self.user, 'rol', '') == 'admin' and doc.usuario:
                admin_user_row = [
                    ft.Container(height=4),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON_OUTLINE, size=11, color=text_dim),
                        ft.Text(doc.usuario.email, size=10, color=text_dim,
                                overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=4),
                ]

            card = ft.Container(
                border_radius=16,
                bgcolor=card_bg,
                border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
                padding=ft.padding.all(14),
                content=ft.Column(spacing=0, controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Text(empresa, size=14, weight=ft.FontWeight.W_700,
                                    color=accent, expand=True,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            badge,
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=12, color=text_dim),
                        ft.Text(doc.lugar_origen or '—', size=12, color=text_secondary,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text('→', size=11, color=accent, weight=ft.FontWeight.W_700),
                        ft.Text(doc.lugar_destino or '—', size=12, color=text_secondary,
                                overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                    ]),
                    *admin_user_row,
                    ft.Container(height=10),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(spacing=4, controls=[
                                ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=11, color=text_dim),
                                ft.Text(fecha_str, size=11, color=text_secondary),
                            ]),
                            ft.Row(spacing=4, controls=[btn_qr, btn_view, btn_more]),
                        ],
                    ),
                ]),
            )
            cards.append(card)

        return ft.Column(spacing=10, controls=cards)

    def _build_search_box(self, is_dark=False):
        box_bg = ft.Colors.with_opacity(0.12, ft.Colors.WHITE) if is_dark else ft.Colors.WHITE
        return ft.Container(
            border_radius=14,
            bgcolor=box_bg,
            border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)),
            padding=ft.padding.symmetric(horizontal=14, vertical=2),
            content=ft.TextField(
                hint_text='Buscar empresa, origen o destino...',
                value=self.search_term,
                prefix_icon=ft.Icons.SEARCH,
                border=ft.InputBorder.NONE,
                on_change=self._filter_documents,
                dense=True,
                hint_style=ft.TextStyle(
                    color=ft.Colors.with_opacity(0.40, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_400,
                    size=13,
                ),
                color=ft.Colors.WHITE if is_dark else None,
            ),
        )

    def _filter_documents(self, e):
        self.search_term = e.control.value
        search_term = self.search_term.lower()
        self.filtered_documents = (
            [
                d for d in self.documents
                if search_term in (d.contratante.nombre.lower() if d.contratante else '')
                or search_term in d.lugar_origen.lower()
                or search_term in d.lugar_destino.lower()
            ]
            if search_term else self.documents
        )
        self.table.controls.clear()
        self.table.controls.append(self._build_documents_list())
        self.page.update()

    def _mostrar_dialogo_qr(self, doc):
        try:
            qr_text = build_document_qr_text(doc)
            qr_b64 = generate_qr_base64(qr_text)

            self.dialog.title = ft.Row([
                ft.Icon(ft.Icons.QR_CODE_2, color=ft.Colors.GREEN_700),
                ft.Text("Código QR del documento", weight=ft.FontWeight.W_600),
            ], spacing=8)

            contratante_nombre = doc.contratante.nombre if doc.contratante else "—"
            fecha_str = doc.fecha_transporte.strftime('%d/%m/%Y') if doc.fecha_transporte else "—"

            # Subtítulo según si es URL o texto
            es_url = qr_text.startswith("http")
            subtitulo = (
                ft.Text(
                    "Escanea para abrir el PDF en tu móvil\n(misma red WiFi)",
                    size=12,
                    color=ft.Colors.GREEN_700,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.W_500,
                )
                if es_url else
                ft.Text(
                    "Escanea para ver los datos del documento",
                    size=12,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER,
                )
            )

            url_row = (
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.07, ft.Colors.GREEN_700),
                    content=ft.Text(
                        qr_text,
                        size=10,
                        color=ft.Colors.GREEN_800,
                        text_align=ft.TextAlign.CENTER,
                        selectable=True,
                    ),
                )
                if es_url else ft.Container()
            )

            self.dialog.content = ft.Container(
                width=300,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        subtitulo,
                        ft.Image(src_base64=qr_b64, width=220, height=220, fit=ft.ImageFit.CONTAIN),
                        url_row,
                        ft.Divider(),
                        ft.Text(f"Empresa: {contratante_nombre}", size=13, weight=ft.FontWeight.W_500),
                        ft.Text(f"{doc.lugar_origen} → {doc.lugar_destino}", size=13, color=ft.Colors.GREY_700),
                        ft.Text(f"Fecha: {fecha_str}", size=12, color=ft.Colors.GREY_500),
                    ],
                ),
            )

        except Exception as ex:
            self.dialog.title = ft.Text("Error al generar QR")
            self.dialog.content = ft.Text(f"No se pudo generar el código QR: {ex}")

        self.dialog.actions = [
            ft.TextButton(
                "Cerrar",
                on_click=lambda e: self._cerrar_dialogo(),
                style=ft.ButtonStyle(color=ft.Colors.GREEN_700),
            )
        ]
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _descargar_documento(self, doc):
        """Abre un diálogo para guardar el PDF en la ubicación que elija el usuario."""
        src_path = os.path.join("assets", "docs", doc.archivo)

        if not os.path.exists(src_path):
            self.dialog.title = ft.Text("Archivo no encontrado")
            self.dialog.content = ft.Text(f"El archivo {doc.archivo} no existe en el servidor.")
            self.dialog.actions = [
                ft.TextButton("Cerrar", on_click=lambda e: self._cerrar_dialogo())
            ]
            self.page.dialog = self.dialog
            self.dialog.open = True
            self.page.update()
            return

        def on_save_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    shutil.copy(src_path, e.path)
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"✅ Documento guardado en {e.path}"),
                        bgcolor=ft.Colors.GREEN_700,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                except Exception as ex:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"❌ Error al guardar: {ex}"),
                        bgcolor=ft.Colors.ERROR,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()

        # Limpiar FilePickers previos y añadir uno nuevo
        for item in list(self.page.overlay):
            if isinstance(item, ft.FilePicker):
                self.page.overlay.remove(item)
        file_picker = ft.FilePicker(on_result=on_save_result)
        self.page.overlay.append(file_picker)
        self.page.update()

        file_picker.save_file(
            dialog_title="Guardar documento PDF",
            file_name=doc.archivo,
            allowed_extensions=["pdf"],
        )

    def _delete_document(self, doc):
        session = SessionLocal()
        try:
            document = session.query(Documentos).filter(Documentos.id == doc.id).first()
            if document:
                session.delete(document)
                session.commit()
                self._load_documents()
                self.table.controls.clear()
                self.table.controls.append(self._build_documents_list())
        except Exception as ex:
            session.rollback()
        finally:
            session.close()
        self.page.update()

    def _cerrar_dialogo(self):
        self.dialog.open = False
        self.page.update()

    # ──────────────────────────────────────────
    #  ENVIAR POR EMAIL
    # ──────────────────────────────────────────
    def _enviar_por_email(self, doc):
        """Muestra el diálogo de envío de email para un documento ya existente."""
        contratante = doc.contratante
        email_destino = contratante.email if contratante else None

        # Campo editable para el email destino
        email_field = ft.TextField(
            label="Email destinatario",
            value=email_destino or "",
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            border_radius=12,
            filled=True,
            dense=True,
            keyboard_type=ft.KeyboardType.EMAIL,
        )
        error_text = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)

        def _do_send(e):
            dest_email = email_field.value.strip()
            if not dest_email or "@" not in dest_email:
                error_text.value = "Introduce un email válido"
                error_text.visible = True
                self.page.update()
                return

            if not doc.archivo:
                error_text.value = "Este documento no tiene PDF generado"
                error_text.visible = True
                self.page.update()
                return

            pdf_path = os.path.abspath(os.path.join("assets", "docs", doc.archivo))
            if not os.path.exists(pdf_path):
                error_text.value = "No se encuentra el archivo PDF en el servidor"
                error_text.visible = True
                self.page.update()
                return

            if not config_exists():
                self.dialog.open = False
                self.page.update()
                self._show_email_config_dialog(doc, dest_email, pdf_path)
                return

            self.dialog.open = False
            self.page.update()

            try:
                fecha_str = doc.fecha_transporte.strftime('%d/%m/%Y') if doc.fecha_transporte else "—"
                usuario = doc.usuario
                remitente = f"{usuario.nombre} {usuario.apellido}" if usuario else "TransControl"

                msg = enviar_pdf_por_email(
                    pdf_path=pdf_path,
                    destinatario_email=dest_email,
                    destinatario_nombre=contratante.nombre if contratante else dest_email,
                    remitente_nombre=remitente,
                    doc_info={
                        'origen': doc.lugar_origen,
                        'destino': doc.lugar_destino,
                        'fecha': fecha_str,
                        'matricula': doc.matricula_vehiculo or "—",
                    },
                )
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(msg),
                    bgcolor=ft.Colors.GREEN_700,
                )
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Error al enviar: {ex}"),
                    bgcolor=ft.Colors.ERROR,
                )
            self.page.snack_bar.open = True
            self.page.update()

        fecha_str = doc.fecha_transporte.strftime('%d/%m/%Y') if doc.fecha_transporte else "—"

        self.dialog.title = ft.Row([
            ft.Icon(ft.Icons.EMAIL_OUTLINED, color=ft.Colors.GREEN_700),
            ft.Text("Enviar por email", weight=ft.FontWeight.W_600),
        ], spacing=8)

        self.dialog.content = ft.Container(
            width=320,
            content=ft.Column(
                spacing=10,
                tight=True,
                controls=[
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN_700),
                        content=ft.Column(spacing=2, controls=[
                            ft.Text(
                                f"{doc.lugar_origen}  →  {doc.lugar_destino}",
                                size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_800,
                            ),
                            ft.Text(fecha_str, size=11, color=ft.Colors.GREY_600),
                        ]),
                    ),
                    email_field,
                    error_text,
                ],
            ),
        )

        self.dialog.actions = [
            ft.TextButton(
                "Cancelar",
                on_click=lambda e: self._cerrar_dialogo(),
                style=ft.ButtonStyle(color=ft.Colors.GREY_600),
            ),
            ft.FilledButton(
                "Enviar",
                icon=ft.Icons.SEND_OUTLINED,
                on_click=_do_send,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            ),
        ]
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _show_email_config_dialog(self, doc, dest_email, pdf_path):
        """Solicita configuración SMTP la primera vez."""
        fs = dict(border_radius=10, filled=True, dense=True)
        smtp_host = ft.TextField(label="Servidor SMTP", value="smtp.gmail.com", **fs)
        smtp_port = ft.TextField(label="Puerto", value="587", keyboard_type=ft.KeyboardType.NUMBER, **fs)
        email_f = ft.TextField(label="Tu email remitente", **fs)
        password_f = ft.TextField(label="Contraseña de aplicación", password=True, can_reveal_password=True, **fs)
        error = ft.Text("", color=ft.Colors.ERROR, size=11, visible=False)

        cfg_dialog = ft.AlertDialog(modal=True)

        def guardar_y_enviar(e):
            if not all([email_f.value, password_f.value]):
                error.value = "Email y contraseña son obligatorios"
                error.visible = True
                self.page.update()
                return
            try:
                save_config(smtp_host.value, int(smtp_port.value), email_f.value, password_f.value)
                cfg_dialog.open = False
                self.page.update()

                fecha_str = doc.fecha_transporte.strftime('%d/%m/%Y') if doc.fecha_transporte else "—"
                usuario = doc.usuario
                remitente = f"{usuario.nombre} {usuario.apellido}" if usuario else "TransControl"
                contratante = doc.contratante

                msg = enviar_pdf_por_email(
                    pdf_path=pdf_path,
                    destinatario_email=dest_email,
                    destinatario_nombre=contratante.nombre if contratante else dest_email,
                    remitente_nombre=remitente,
                    doc_info={
                        'origen': doc.lugar_origen,
                        'destino': doc.lugar_destino,
                        'fecha': fecha_str,
                        'matricula': doc.matricula_vehiculo or "—",
                    },
                )
                self.page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=ft.Colors.GREEN_700)
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Error: {ex}"),
                    bgcolor=ft.Colors.ERROR,
                )
            self.page.snack_bar.open = True
            self.page.update()

        cfg_dialog.title = ft.Row([
            ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=ft.Colors.GREEN_700),
            ft.Text("Configurar email", weight=ft.FontWeight.W_600),
        ], spacing=8)
        cfg_dialog.content = ft.Container(
            width=320,
            content=ft.Column(spacing=10, tight=True, controls=[
                ft.Text("Configura tu cuenta de correo saliente:", size=12, color=ft.Colors.GREY_600),
                ft.Text("(Gmail → usa contraseña de aplicación)", size=11, color=ft.Colors.GREY_500, italic=True),
                smtp_host, smtp_port, email_f, password_f, error,
            ]),
        )
        cfg_dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._close_cfg(cfg_dialog),
                          style=ft.ButtonStyle(color=ft.Colors.GREY_600)),
            ft.FilledButton("Guardar y enviar", icon=ft.Icons.SEND_OUTLINED,
                            on_click=guardar_y_enviar,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
        ]
        self.page.dialog = cfg_dialog
        cfg_dialog.open = True
        self.page.update()

    def _close_cfg(self, dialog):
        dialog.open = False
        self.page.update()

    def _build_bottom_appbar(self):
        ab_color = getattr(self.page, 'tc_theme', {}).get('appbar_color', '#1A1A1A')
        accent = getattr(self.page, 'tc_theme', {}).get('accent', '#A3E635')
        return ft.BottomAppBar(
            bgcolor=ab_color,
            elevation=8,
            content=ft.Row(
                expand=True,
                controls=[
                    ft.IconButton(icon=ft.Icons.HOME_ROUNDED, icon_color=ft.Colors.WHITE, tooltip="Inicio", on_click=lambda e: self.page.go('/dashboard')),
                    ft.IconButton(icon=ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED, icon_color=accent, tooltip="Documentos"),
                    ft.IconButton(icon=ft.Icons.DIRECTIONS_CAR_ROUNDED, icon_color=ft.Colors.WHITE, tooltip="Vehículos", on_click=lambda e: self.page.go('/vehicles')),
                    ft.IconButton(icon=ft.Icons.APARTMENT_ROUNDED, icon_color=ft.Colors.WHITE, tooltip="Empresas", on_click=lambda e: self.page.go('/companies')),
                    ft.IconButton(icon=ft.Icons.PERSON_ROUNDED, icon_color=ft.Colors.WHITE, tooltip="Perfil", on_click=lambda e: self.page.go('/profile')),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
        )
