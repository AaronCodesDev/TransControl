import flet as ft
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Documentos, Empresas, Usuario, Vehiculos
from utils.create_pdf import rellenar_pdf_con_fondo
from utils.email_utils import enviar_pdf_por_email, config_exists, save_config


def _open_pdf(path: str):
    """Abre el PDF con el visor predeterminado del sistema."""
    try:
        abs_path = os.path.abspath(path)
        if sys.platform == "win32":
            os.startfile(abs_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", abs_path])
        else:
            subprocess.Popen(["xdg-open", abs_path])
    except Exception:
        pass


def _engine():
    return create_engine('sqlite:///database/transcontrol.db')


class CreateDocumentView:
    def __init__(self, page, theme_button, force_route, user):
        self.page = page
        self.theme_button = theme_button
        self.force_route = force_route
        self.user = user

        self._firma_cargador_img_path: str | None = None
        self._firma_transportista_img_path: str | None = None
        self._albaran_img_path: str | None = None

        self._firma_cargador_preview = None
        self._firma_cargador_status = None
        self._firma_transp_preview = None
        self._firma_transp_status = None
        self._albaran_preview = None
        self._albaran_status = None

    # ─────────────────────────────────────────────
    #  BUILD
    # ─────────────────────────────────────────────
    def build(self):
        self._load_data()
        field_style = dict(border_radius=12, filled=True)

        self.empresas_dropdown = ft.Dropdown(
            label='Empresa Contratante',
            options=[ft.dropdown.Option(str(e.id), e.nombre) for e in self.empresas],
            menu_height=300,
            border_radius=12,
            filled=True,
            width=float('inf'),
        )

        vehicle_options = [ft.dropdown.Option("manual", "✏️ Introducir manualmente")]
        for v in self.vehiculos:
            vehicle_options.append(ft.dropdown.Option(str(v.id), f"{v.marca} {v.modelo} — {v.matricula}"))

        self.vehiculo_dropdown = ft.Dropdown(
            label='Seleccionar vehículo registrado',
            options=vehicle_options,
            menu_height=300,
            border_radius=12,
            filled=True,
            width=float('inf'),
            value="manual",
            on_change=self._on_vehicle_change,
        )

        self.origen_input = ft.TextField(label='Lugar de origen', prefix_icon=ft.Icons.PLACE_OUTLINED, **field_style)
        self.destino_input = ft.TextField(label='Lugar de destino', prefix_icon=ft.Icons.FLAG_OUTLINED, **field_style)
        self.matricula_input = ft.TextField(label='Matrícula vehículo', prefix_icon=ft.Icons.DIRECTIONS_CAR_OUTLINED, **field_style)
        self.matricula_remolque_input = ft.TextField(label='Matrícula semiremolque', prefix_icon=ft.Icons.LOCAL_SHIPPING_OUTLINED, **field_style)
        self.naturaleza_input = ft.TextField(label='Naturaleza de la carga', prefix_icon=ft.Icons.INVENTORY_2_OUTLINED, **field_style)
        self.peso_input = ft.TextField(label='Peso (kg)', prefix_icon=ft.Icons.SCALE_OUTLINED, keyboard_type=ft.KeyboardType.NUMBER, **field_style)
        self.firma_cargador_input = ft.TextField(label='Nombre firma empresa cargadora', prefix_icon=ft.Icons.DRAW_OUTLINED, **field_style)
        self.firma_transportista_input = ft.TextField(label='Nombre firma transportista', prefix_icon=ft.Icons.DRAW_OUTLINED, **field_style)
        self.message = ft.Text(value='', visible=False, text_align=ft.TextAlign.CENTER)

        self._manual_fields = ft.Column(
            visible=True,
            spacing=12,
            controls=[
                ft.Row([
                    ft.Container(self.matricula_input, expand=1),
                    ft.Container(self.matricula_remolque_input, expand=1),
                ], spacing=12),
            ],
        )

        _tc      = getattr(self.page, 'tc_theme', {})
        _accent  = _tc.get('accent', '#A3E635')
        _card    = _tc.get('card', '#1C1E24')

        def _section(title, icon, controls):
            return ft.Container(
                border_radius=16,
                bgcolor=_card,
                border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE)),
                shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK), offset=ft.Offset(0, 3)),
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Row([
                            ft.Icon(icon, color=_accent, size=18),
                            ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=_accent),
                        ], spacing=8),
                        ft.Divider(height=1, color=ft.Colors.with_opacity(0.10, ft.Colors.WHITE)),
                        *controls,
                    ],
                ),
            )

        firma_cargador_picker = self._build_image_picker_row(
            label="Foto del sello/firma cargador",
            on_pick=self._pick_firma_cargador,
            preview_key="cargador",
        )
        firma_transp_picker = self._build_image_picker_row(
            label="Foto de la firma conductora",
            on_pick=self._pick_firma_transportista,
            preview_key="transportista",
        )
        albaran_picker = self._build_image_picker_row(
            label="Foto o PDF del albarán",
            on_pick=self._pick_albaran,
            preview_key="albaran",
            allow_pdf=True,
        )

        tc       = getattr(self.page, 'tc_theme', {})
        ab_color = tc.get('appbar_color', '#0D0D0D')
        accent   = tc.get('accent', '#A3E635')
        bg       = tc.get('bg', '#0D0D0D')
        card     = tc.get('card', '#1C1E24')
        is_dark  = tc.get('mode', 'light') == 'dark'
        text_dim = ft.Colors.with_opacity(0.50, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_600

        header = ft.Container(
            padding=ft.padding.only(top=48, bottom=24, left=20, right=20),
            bgcolor=ab_color,
            content=ft.Column(spacing=0, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.GestureDetector(
                            on_tap=lambda e: self.force_route('/documents'),
                            content=ft.Row(spacing=6, controls=[
                                ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE), size=16),
                                ft.Text('Volver', size=13,
                                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
                            ]),
                        ),
                        self.theme_button,
                    ],
                ),
                ft.Container(height=14),
                ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Container(
                        width=40, height=40, border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.15, accent),
                        alignment=ft.alignment.center,
                        content=ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, color=accent, size=22),
                    ),
                    ft.Text('Nuevo Documento', size=22, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                ]),
            ]),
        )

        body = ft.Container(
            expand=True,
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            bgcolor=bg,
            padding=ft.padding.only(left=20, right=20, top=20, bottom=32),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=16,
                controls=[
                    _section("Empresa contratante", ft.Icons.APARTMENT_OUTLINED, [
                        self.empresas_dropdown,
                    ]),
                    _section("Ruta", ft.Icons.ROUTE, [
                        self.origen_input,
                        self.destino_input,
                    ]),
                    _section("Vehículo y carga", ft.Icons.LOCAL_SHIPPING_OUTLINED, [
                        self.vehiculo_dropdown,
                        self._manual_fields,
                        self.naturaleza_input,
                        self.peso_input,
                    ]),
                    _section("Firmas / Sellos", ft.Icons.DRAW_OUTLINED, [
                        ft.Text("Sello empresa cargadora", size=12, color=text_dim, weight=ft.FontWeight.W_500),
                        firma_cargador_picker,
                        self.firma_cargador_input,
                        ft.Divider(height=1),
                        ft.Text("Firma transportista", size=12, color=text_dim, weight=ft.FontWeight.W_500),
                        firma_transp_picker,
                        self.firma_transportista_input,
                    ]),
                    _section("Albarán de la empresa", ft.Icons.RECEIPT_LONG_OUTLINED, [
                        ft.Text(
                            "Adjunta la foto o PDF del albarán que te entrega la empresa",
                            size=12,
                            color=text_dim,
                        ),
                        albaran_picker,
                    ]),
                    self.message,
                    ft.Container(
                        border_radius=14,
                        bgcolor=accent,
                        shadow=ft.BoxShadow(blur_radius=14,
                                            color=ft.Colors.with_opacity(0.35, accent),
                                            offset=ft.Offset(0, 4)),
                        on_click=self.save_document,
                        padding=ft.padding.symmetric(vertical=15),
                        alignment=ft.alignment.center,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.SAVE_OUTLINED, color=ft.Colors.BLACK, size=18),
                                ft.Text('Guardar documento', size=15, weight=ft.FontWeight.W_700,
                                        color=ft.Colors.BLACK),
                            ],
                        ),
                    ),
                    ft.TextButton(
                        "Cancelar",
                        icon=ft.Icons.CLOSE,
                        on_click=lambda e: self.force_route("/documents"),
                        style=ft.ButtonStyle(color=ft.Colors.GREY_500),
                    ),
                ],
            ),
        )

        return ft.View(
            route="/create_document",
            padding=0,
            bgcolor=bg,
            controls=[
                ft.Column(spacing=0, expand=True, controls=[header, body]),
            ],
        )

    # ─────────────────────────────────────────────
    #  IMAGE PICKER ROW
    # ─────────────────────────────────────────────
    def _build_image_picker_row(self, label, on_pick, preview_key, allow_pdf=False):
        preview = ft.Image(
            width=120, height=80,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(8),
            visible=False,
        )
        status_text = ft.Text("Sin seleccionar", size=11, color=ft.Colors.GREY_500, italic=True)

        if preview_key == "cargador":
            self._firma_cargador_preview = preview
            self._firma_cargador_status = status_text
        elif preview_key == "transportista":
            self._firma_transp_preview = preview
            self._firma_transp_status = status_text
        elif preview_key == "albaran":
            self._albaran_preview = preview
            self._albaran_status = status_text

        allowed = ["jpg", "jpeg", "png", "webp"]
        if allow_pdf:
            allowed.append("pdf")

        pick_btn = ft.OutlinedButton(
            label,
            icon=ft.Icons.ATTACH_FILE if allow_pdf else ft.Icons.PHOTO_CAMERA_OUTLINED,
            on_click=lambda e: on_pick(allowed),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        return ft.Column(spacing=6, controls=[
            ft.Row([pick_btn, status_text], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            preview,
        ])

    # ─────────────────────────────────────────────
    #  FILE PICKERS
    # ─────────────────────────────────────────────
    def _open_picker(self, allowed_extensions, on_result):
        for item in list(self.page.overlay):
            if isinstance(item, ft.FilePicker):
                self.page.overlay.remove(item)
        picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(picker)
        self.page.update()
        picker.pick_files(
            dialog_title="Seleccionar archivo",
            allowed_extensions=allowed_extensions,
            allow_multiple=False,
        )

    def _pick_firma_cargador(self, allowed):
        def on_result(e: ft.FilePickerResultEvent):
            if e.files:
                path = e.files[0].path
                self._firma_cargador_img_path = path
                self._firma_cargador_preview.src = path
                self._firma_cargador_preview.visible = True
                self._firma_cargador_status.value = os.path.basename(path)
                self._firma_cargador_status.color = ft.Colors.GREEN_700
                self.page.update()
        self._open_picker(allowed, on_result)

    def _pick_firma_transportista(self, allowed):
        def on_result(e: ft.FilePickerResultEvent):
            if e.files:
                path = e.files[0].path
                self._firma_transportista_img_path = path
                self._firma_transp_preview.src = path
                self._firma_transp_preview.visible = True
                self._firma_transp_status.value = os.path.basename(path)
                self._firma_transp_status.color = ft.Colors.GREEN_700
                self.page.update()
        self._open_picker(allowed, on_result)

    def _pick_albaran(self, allowed):
        def on_result(e: ft.FilePickerResultEvent):
            if e.files:
                path = e.files[0].path
                self._albaran_img_path = path
                ext = os.path.splitext(path)[1].lower()
                if ext != '.pdf':
                    self._albaran_preview.src = path
                    self._albaran_preview.visible = True
                self._albaran_status.value = f"✓ {os.path.basename(path)}"
                self._albaran_status.color = ft.Colors.GREEN_700
                self.page.update()
        self._open_picker(allowed, on_result)

    # ─────────────────────────────────────────────
    #  VEHICLE CHANGE
    # ─────────────────────────────────────────────
    def _on_vehicle_change(self, e):
        val = self.vehiculo_dropdown.value
        if val and val != "manual":
            v = next((v for v in self.vehiculos if str(v.id) == val), None)
            if v:
                self.matricula_input.value = v.matricula
                self.matricula_remolque_input.value = v.matricula_remolque or ""
        else:
            self.matricula_input.value = ""
            self.matricula_remolque_input.value = ""
        self.page.update()

    # ─────────────────────────────────────────────
    #  LOAD DATA
    # ─────────────────────────────────────────────
    def _load_data(self):
        Session = sessionmaker(bind=_engine())
        session = Session()
        try:
            if getattr(self.user, 'rol', '') == 'admin':
                self.empresas = session.query(Empresas).all()
            else:
                self.empresas = session.query(Empresas).filter(Empresas.usuario_id == self.user.id).all()
            self.vehiculos = session.query(Vehiculos).filter(Vehiculos.usuario_id == self.user.id).all()
        finally:
            session.close()

    # ─────────────────────────────────────────────
    #  SAVE DOCUMENT
    # ─────────────────────────────────────────────
    def save_document(self, e):
        Session = sessionmaker(bind=_engine())
        session = Session()

        try:
            usuario = session.query(Usuario).filter_by(id=self.page.user.id).first()

            if not self.empresas_dropdown.value:
                self._show_msg("❌ Debes seleccionar una empresa antes de guardar.")
                return

            empresa_id = int(self.empresas_dropdown.value)
            empresa = session.query(Empresas).filter_by(id=empresa_id).first()

            if not all([usuario.direccion, usuario.ciudad, usuario.provincia, usuario.codigo_postal, usuario.telefono]):
                self._show_msg("❌ Debes completar tu perfil antes de generar un documento.")
                return

            peso_val = 0
            try:
                peso_val = float(self.peso_input.value) if self.peso_input.value else 0
            except ValueError:
                self._show_msg("❌ El peso debe ser un número válido.")
                return

            vehiculo_id = None
            val = self.vehiculo_dropdown.value
            if val and val != "manual":
                vehiculo_id = int(val)

            doc = Documentos(
                usuarios_id=usuario.id,
                empresas_id_transportista=empresa.id,
                empresas_id_contratante=empresa.id,
                vehiculo_id=vehiculo_id,
                lugar_origen=self.origen_input.value,
                lugar_destino=self.destino_input.value,
                fecha_transporte=date.today(),
                fecha_creacion=date.today(),
                matricula_vehiculo=self.matricula_input.value,
                matricula_semiremolque=self.matricula_remolque_input.value,
                naturaleza_carga=self.naturaleza_input.value,
                peso=peso_val,
                firma_cargador=self.firma_cargador_input.value,
                firma_transportista=self.firma_transportista_input.value,
            )

            session.add(doc)
            session.flush()

            correo_limpio = re.sub(r'[^\w\-_.]', '_', usuario.email)

            # Copiar imágenes
            firma_cargador_dst = self._copy_asset(
                self._firma_cargador_img_path,
                f"assets/signatures/firma_cargador_{correo_limpio}_{doc.id}",
            )
            if firma_cargador_dst:
                doc.firma_cargador_img = firma_cargador_dst

            firma_transp_dst = self._copy_asset(
                self._firma_transportista_img_path,
                f"assets/signatures/firma_transp_{correo_limpio}_{doc.id}",
            )
            if firma_transp_dst:
                doc.firma_transportista_img = firma_transp_dst

            albaran_dst = self._copy_asset(
                self._albaran_img_path,
                f"assets/albaranes/albaran_{correo_limpio}_{doc.id}",
            )
            if albaran_dst:
                doc.albaran_path = albaran_dst

            datos = {
                'fecha': doc.fecha_creacion.strftime('%d/%m/%Y'),
                'contratante': empresa.nombre,
                'cif_contratante': empresa.cif or '',
                'direccion_contratante': empresa.direccion,
                'poblacion_contratante': empresa.ciudad,
                'provincia_contratante': empresa.provincia,
                'codigo_postal_contratante': empresa.codigo_postal,
                'telefono_contratante': empresa.telefono,
                'transportista': f'{usuario.nombre} {usuario.apellido}',
                'nif_transportista': usuario.nif or '',
                'direccion_transportista': usuario.direccion,
                'poblacion_transportista': usuario.ciudad,
                'provincia_transportista': usuario.provincia,
                'codigo_postal_transportista': usuario.codigo_postal,
                'telefono_transportista': usuario.telefono,
                'origen': doc.lugar_origen,
                'destino': doc.lugar_destino,
                'naturaleza': doc.naturaleza_carga,
                'peso': doc.peso,
                'matricula': doc.matricula_vehiculo,
                'matricula_remolque': doc.matricula_semiremolque or '',
                'firma_cargador': doc.firma_cargador or '',
                'firma_transportista': doc.firma_transportista or '',
                'firma_cargador_img': firma_cargador_dst,
                'firma_transportista_img': firma_transp_dst,
                'albaran_path': albaran_dst,
            }

            archivo_nombre = f"documento_{correo_limpio}_{doc.id}.pdf"
            salida_pdf = f"assets/docs/{archivo_nombre}"
            rellenar_pdf_con_fondo(datos, salida_path=salida_pdf)

            doc.archivo = archivo_nombre
            self._saved_doc_id = doc.id
            session.commit()

            self._show_msg('✅ Documento creado correctamente', color=ft.Colors.GREEN_700)
            self.page.update()

            # Abrir el PDF automáticamente para previsualizar
            _open_pdf(salida_pdf)

            self._offer_email(doc, empresa, usuario, salida_pdf)

        except Exception as err:
            import traceback
            self._show_msg(f'❌ Error: {err}\n{traceback.format_exc()}')
            self.page.update()
        finally:
            session.close()

    def _copy_asset(self, src_path, dst_base) -> str | None:
        if not src_path or not os.path.exists(src_path):
            return None
        ext = os.path.splitext(src_path)[1]
        dst = f"{dst_base}{ext}"
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src_path, dst)
        return dst

    # ─────────────────────────────────────────────
    #  EMAIL OFFER
    # ─────────────────────────────────────────────
    def _offer_email(self, doc, empresa, usuario, pdf_path):
        if not empresa.email:
            time.sleep(1)
            self.page.go('/documents')
            return

        dialog = ft.AlertDialog(modal=True)

        def enviar(e):
            dialog.open = False
            self.page.update()
            if not config_exists():
                self._show_email_config_dialog(doc, empresa, usuario, pdf_path)
                return
            try:
                msg = enviar_pdf_por_email(
                    pdf_path=os.path.abspath(pdf_path),
                    destinatario_email=empresa.email,
                    destinatario_nombre=empresa.nombre,
                    remitente_nombre=f"{usuario.nombre} {usuario.apellido}",
                    doc_info={
                        'origen': doc.lugar_origen,
                        'destino': doc.lugar_destino,
                        'fecha': doc.fecha_creacion.strftime('%d/%m/%Y'),
                        'matricula': doc.matricula_vehiculo,
                    },
                )
                self.page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=ft.Colors.GREEN_700)
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Error al enviar: {ex}"),
                    bgcolor=ft.Colors.ERROR,
                )
            self.page.snack_bar.open = True
            self.page.update()
            time.sleep(0.8)
            doc_id = getattr(self, '_saved_doc_id', None)
            self.page.go(f'/output_pdf/{doc_id}' if doc_id else '/documents')

        def saltar(e):
            dialog.open = False
            self.page.update()
            time.sleep(0.3)
            doc_id = getattr(self, '_saved_doc_id', None)
            self.page.go(f'/output_pdf/{doc_id}' if doc_id else '/documents')

        dialog.title = ft.Row([
            ft.Icon(ft.Icons.EMAIL_OUTLINED, color=ft.Colors.GREEN_700),
            ft.Text("¿Enviar por email?", weight=ft.FontWeight.W_600),
        ], spacing=8)
        dialog.content = ft.Container(
            width=300,
            content=ft.Column(spacing=8, tight=True, controls=[
                ft.Text("¿Quieres enviar el documento a la empresa contratante?", size=13),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.07, ft.Colors.GREEN_700),
                    content=ft.Text(empresa.email, size=13, color=ft.Colors.GREEN_700, weight=ft.FontWeight.W_500),
                ),
            ]),
        )
        dialog.actions = [
            ft.TextButton("Ahora no", on_click=saltar, style=ft.ButtonStyle(color=ft.Colors.GREY_600)),
            ft.FilledButton("Enviar email", icon=ft.Icons.SEND_OUTLINED, on_click=enviar,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
        ]
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _show_email_config_dialog(self, doc, empresa, usuario, pdf_path):
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
                msg = enviar_pdf_por_email(
                    pdf_path=os.path.abspath(pdf_path),
                    destinatario_email=empresa.email,
                    destinatario_nombre=empresa.nombre,
                    remitente_nombre=f"{usuario.nombre} {usuario.apellido}",
                    doc_info={
                        'origen': doc.lugar_origen,
                        'destino': doc.lugar_destino,
                        'fecha': doc.fecha_creacion.strftime('%d/%m/%Y'),
                        'matricula': doc.matricula_vehiculo,
                    },
                )
                self.page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=ft.Colors.GREEN_700)
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as ex:
                error.value = str(ex)
                error.visible = True
                self.page.update()
                return
            time.sleep(0.8)
            doc_id = getattr(self, '_saved_doc_id', None)
            self.page.go(f'/output_pdf/{doc_id}' if doc_id else '/documents')

        dialog.title = ft.Row([
            ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=ft.Colors.GREEN_700),
            ft.Text("Configurar email", weight=ft.FontWeight.W_600),
        ], spacing=8)
        dialog.content = ft.Container(
            width=320,
            content=ft.Column(spacing=10, tight=True, controls=[
                ft.Text("Primera configuración SMTP:", size=12, color=ft.Colors.GREY_600),
                ft.Text("(Gmail → usa contraseña de aplicación)", size=11, color=ft.Colors.GREY_500, italic=True),
                smtp_host, smtp_port, email_f, password_f, error,
            ]),
        )
        dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._close_dialog_and_go(dialog),
                          style=ft.ButtonStyle(color=ft.Colors.GREY_600)),
            ft.FilledButton("Guardar y enviar", icon=ft.Icons.SEND_OUTLINED, on_click=guardar_y_enviar,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
        ]
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog_and_go(self, dialog):
        dialog.open = False
        self.page.update()
        time.sleep(0.3)
        doc_id = getattr(self, '_saved_doc_id', None)
        self.page.go(f'/output_pdf/{doc_id}' if doc_id else '/documents')

    def _show_msg(self, text, color=ft.Colors.ERROR):
        self.message.value = text
        self.message.color = color
        self.message.visible = True
        self.page.update()
