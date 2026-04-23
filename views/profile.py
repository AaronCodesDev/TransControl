import flet as ft
from utils.nav_bar import build_bottom_nav
import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Usuario
from utils.theme_manager import THEMES, load_theme_id


def _engine():
    return create_engine('sqlite:///database/transcontrol.db')


class ProfileView:
    def __init__(self, page: ft.Page, theme_button, user=None):
        self.page = page
        self.theme_button = theme_button
        self.user = user or page.user
        self.edit_mode = False

        self.direccion_input = ft.TextField(label='Dirección', value=self.user.direccion or '', border_radius=12, filled=True, prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, dense=True)
        self.ciudad_input = ft.TextField(label='Ciudad', value=self.user.ciudad or '', border_radius=12, filled=True, prefix_icon=ft.Icons.LOCATION_CITY_OUTLINED, dense=True)
        self.provincia_input = ft.TextField(label='Provincia', value=self.user.provincia or '', border_radius=12, filled=True, prefix_icon=ft.Icons.MAP_OUTLINED, dense=True)
        self.codigo_postal_input = ft.TextField(label='Código Postal', value=self.user.codigo_postal or '', border_radius=12, filled=True, prefix_icon=ft.Icons.PIN_OUTLINED, dense=True)
        self.telefono_input = ft.TextField(label='Teléfono', value=self.user.telefono or '', border_radius=12, filled=True, prefix_icon=ft.Icons.PHONE_OUTLINED, dense=True)

    # ─────────────────────────────────────────
    #  BUILD
    # ─────────────────────────────────────────
    def build(self):
        ab_color = getattr(self.page, 'tc_theme', {}).get('appbar_color', '#1B5E20')
        accent   = getattr(self.page, 'tc_theme', {}).get('accent', '#A3E635')

        admin_button = None
        if self.user and getattr(self.user, 'rol', '') == 'admin':
            admin_button = ft.IconButton(
                icon=ft.Icons.SECURITY,
                icon_color=ft.Colors.WHITE,
                tooltip='Panel de administración',
                on_click=lambda e: self.page.go('/admin'),
            )

        nombre_completo = f"{self.user.nombre or ''} {self.user.apellido or ''}".strip()

        header = ft.Container(
            padding=ft.padding.only(top=44, bottom=16, left=20, right=20),
            bgcolor=ab_color,
            content=ft.Column(
                spacing=12,
                controls=[
                    # ── Fila top: título + botones ──
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(width=40),
                            ft.Text('Mi Perfil', size=15, weight=ft.FontWeight.W_700,
                                    color=ft.Colors.WHITE),
                            ft.Row(spacing=0, controls=[
                                *(([admin_button]) if admin_button else []),
                                self.theme_button,
                            ]),
                        ],
                    ),
                    # ── Fila avatar + info ──
                    ft.Row(
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self._build_gradient_avatar(ab_color),
                            ft.Column(spacing=3, controls=[
                                ft.Text(nombre_completo, size=16,
                                        weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                                ft.Text(self.user.email or '', size=11,
                                        color=ft.Colors.with_opacity(0.70, ft.Colors.WHITE)),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                    border_radius=6,
                                    bgcolor=ft.Colors.with_opacity(0.20, ft.Colors.WHITE),
                                    content=ft.Text(
                                        (self.user.rol or 'usuario').upper(),
                                        size=9, weight=ft.FontWeight.W_700,
                                        color=ft.Colors.WHITE,
                                    ),
                                ),
                            ]),
                        ],
                    ),
                ],
            ),
        )

        bg = getattr(self.page, 'tc_theme', {}).get('bg', '#0D0D0D')

        body = ft.Container(
            expand=True,
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            bgcolor=bg,
            padding=ft.padding.only(left=20, right=20, top=20, bottom=90),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                controls=[
                    self._build_info_card(),
                    self._build_contact_section(),
                    self._build_actions_row(),
                ],
            ),
        )

        return ft.View(
            route='/profile',
            padding=0,
            bgcolor=bg,
            bottom_appbar=self._build_bottom_appbar(),
            controls=[
                ft.Column(
                    spacing=0,
                    expand=True,
                    controls=[header, body],
                ),
            ],
        )

    def _build_gradient_avatar(self, ab_color='#0D0D0D'):
        """Avatar circular con borde blanco para el header en gradiente."""
        foto = getattr(self.user, 'foto_perfil', None)
        has_photo = foto and os.path.exists(foto)

        if has_photo:
            inner = ft.Image(src=foto, width=54, height=54, fit=ft.ImageFit.COVER)
        else:
            nombre   = self.user.nombre or ''
            apellido = self.user.apellido or ''
            initials = (nombre[:1] + apellido[:1]).upper() or 'TC'
            inner = ft.Text(initials, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

        return ft.Stack(
            width=58, height=58,
            controls=[
                ft.Container(
                    width=58, height=58, border_radius=29,
                    bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
                    border=ft.border.all(2, ft.Colors.with_opacity(0.55, ft.Colors.WHITE)),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    alignment=ft.alignment.center,
                    content=inner,
                ),
                ft.Container(
                    width=20, height=20, border_radius=10,
                    bgcolor=ab_color,
                    alignment=ft.alignment.center,
                    right=0, bottom=0,
                    border=ft.border.all(1.5, ft.Colors.WHITE),
                    content=ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=10, color=ft.Colors.WHITE),
                    on_click=lambda e: self._pick_photo(),
                ),
            ],
        )

    # ─────────────────────────────────────────
    #  AVATAR
    # ─────────────────────────────────────────
    def _build_avatar_section(self):
        foto = getattr(self.user, 'foto_perfil', None)
        has_photo = foto and os.path.exists(foto)

        if has_photo:
            avatar_content = ft.Image(src=foto, width=90, height=90, fit=ft.ImageFit.COVER)
        else:
            nombre = self.user.nombre or ''
            apellido = self.user.apellido or ''
            initials = (nombre[:1] + apellido[:1]).upper() or "TC"
            avatar_content = ft.Text(
                initials, size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800,
            )

        avatar_stack = ft.Stack(
            width=90, height=90,
            controls=[
                ft.Container(
                    width=90, height=90,
                    border_radius=45,
                    bgcolor=ft.Colors.GREEN_100,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    alignment=ft.alignment.center,
                    content=avatar_content,
                    border=ft.border.all(2, ft.Colors.with_opacity(0.15, ft.Colors.GREEN_700)),
                ),
                ft.Container(
                    width=28, height=28,
                    border_radius=14,
                    bgcolor=ft.Colors.GREEN_700,
                    alignment=ft.alignment.center,
                    right=0, bottom=0,
                    border=ft.border.all(2, ft.Colors.WHITE),
                    content=ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=14, color=ft.Colors.WHITE),
                    on_click=lambda e: self._pick_photo(),
                ),
            ],
        )

        nombre_completo = f"{self.user.nombre or ''} {self.user.apellido or ''}".strip()
        rol_label = ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=3),
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.GREEN_700),
            content=ft.Text(
                (self.user.rol or 'usuario').capitalize(),
                size=11, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700,
            ),
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                avatar_stack,
                ft.Text(nombre_completo, size=18, weight=ft.FontWeight.W_700),
                ft.Text(self.user.email or '', size=12, color=ft.Colors.GREY_500),
                rol_label,
            ],
        )

    def _pick_photo(self):
        """Abre el selector de archivo y luego muestra el diálogo de recorte."""
        def on_result(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            src_path = e.files[0].path
            self._show_crop_dialog(src_path)

        for item in list(self.page.overlay):
            if isinstance(item, ft.FilePicker):
                self.page.overlay.remove(item)
        picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(picker)
        self.page.update()
        picker.pick_files(
            dialog_title="Seleccionar foto de perfil",
            allowed_extensions=["jpg", "jpeg", "png", "webp"],
            allow_multiple=False,
        )

    def _show_crop_dialog(self, src_path: str):
        """Muestra un diálogo con zoom slider para ajustar el recorte circular."""
        import base64
        from PIL import Image as PILImage

        # Estado del zoom (1.0 = sin zoom, 2.0 = doble zoom)
        zoom_state = {"value": 1.0}
        PREVIEW_SIZE = 200  # px del círculo de previsualización

        def _render_preview(zoom: float) -> str:
            """Aplica zoom y recorte cuadrado centrado; devuelve base64 PNG."""
            img = PILImage.open(src_path).convert("RGB")
            w, h = img.size
            # El lado mínimo define el cuadrado base
            side = min(w, h)
            # Zoom: reducimos el recuadro de recorte
            crop_size = int(side / zoom)
            left  = (w - crop_size) // 2
            top   = (h - crop_size) // 2
            img = img.crop((left, top, left + crop_size, top + crop_size))
            img = img.resize((PREVIEW_SIZE, PREVIEW_SIZE), PILImage.LANCZOS)
            import io
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode()

        # Imagen de previsualización reactiva
        preview_img = ft.Image(
            src_base64=_render_preview(1.0),
            width=PREVIEW_SIZE, height=PREVIEW_SIZE,
            fit=ft.ImageFit.COVER,
        )

        # Contenedor circular con clip
        preview_circle = ft.Container(
            width=PREVIEW_SIZE, height=PREVIEW_SIZE,
            border_radius=PREVIEW_SIZE // 2,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.border.all(3, ft.Colors.GREEN_600),
            content=preview_img,
        )

        zoom_label = ft.Text("Zoom: 1.0×", size=12, color=ft.Colors.GREY_500)

        def on_zoom_change(e):
            z = round(float(e.control.value), 1)
            zoom_state["value"] = z
            zoom_label.value = f"Zoom: {z}×"
            preview_img.src_base64 = _render_preview(z)
            self.page.update()

        zoom_slider = ft.Slider(
            min=1.0, max=3.0, divisions=20,
            value=1.0,
            active_color=ft.Colors.GREEN_600,
            on_change=on_zoom_change,
        )

        crop_dialog = ft.AlertDialog(modal=True)

        def _save(e):
            """Aplica el recorte final y guarda."""
            from PIL import Image as PILImage
            zoom = zoom_state["value"]
            img = PILImage.open(src_path).convert("RGB")
            w, h = img.size
            side = min(w, h)
            crop_size = int(side / zoom)
            left  = (w - crop_size) // 2
            top   = (h - crop_size) // 2
            img = img.crop((left, top, left + crop_size, top + crop_size))
            img = img.resize((400, 400), PILImage.LANCZOS)

            os.makedirs("assets/avatars", exist_ok=True)
            dst = f"assets/avatars/avatar_{self.user.id}.png"
            img.save(dst, format="PNG")

            # Guardar en DB
            Session = sessionmaker(bind=_engine())
            session = Session()
            try:
                u = session.query(Usuario).filter_by(id=self.user.id).first()
                u.foto_perfil = dst
                session.commit()
                self.user.foto_perfil = dst
            finally:
                session.close()

            crop_dialog.open = False
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Foto de perfil actualizada"),
                bgcolor=ft.Colors.GREEN_700,
            )
            self.page.snack_bar.open = True
            self.page.views[-1] = self.build()
            self.page.update()

        def _cancel(e):
            crop_dialog.open = False
            self.page.update()

        crop_dialog.title = ft.Row([
            ft.Icon(ft.Icons.CROP_ROUNDED, color=ft.Colors.GREEN_600),
            ft.Text("Ajustar foto", weight=ft.FontWeight.W_600),
        ], spacing=8)

        crop_dialog.content = ft.Container(
            width=280,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                tight=True,
                controls=[
                    ft.Text("Mueve el zoom para encuadrar tu cara",
                            size=12, color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER),
                    preview_circle,
                    ft.Column(spacing=4, controls=[
                        zoom_label,
                        zoom_slider,
                    ]),
                ],
            ),
        )

        crop_dialog.actions = [
            ft.TextButton("Cancelar", on_click=_cancel,
                          style=ft.ButtonStyle(color=ft.Colors.GREY_600)),
            ft.FilledButton("Guardar", icon=ft.Icons.CHECK_ROUNDED,
                            on_click=_save,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            )),
        ]

        self.page.dialog = crop_dialog
        crop_dialog.open = True
        self.page.update()

    # ─────────────────────────────────────────
    #  INFO CARD (NIF / email)
    # ─────────────────────────────────────────
    def _build_info_card(self):
        tc      = getattr(self.page, 'tc_theme', {})
        accent  = tc.get('accent', '#A3E635')
        card    = tc.get('card', '#1C1E24')
        is_dark = tc.get('mode', 'light') == 'dark'
        hdr_bg  = ft.Colors.with_opacity(0.10, ft.Colors.WHITE) if is_dark else '#F1F8E9'
        hdr_txt = accent if is_dark else '#2E7D32'
        div_col = ft.Colors.with_opacity(0.08, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)
        txt_dim = ft.Colors.with_opacity(0.45, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_400
        txt_val = ft.Colors.WHITE if is_dark else '#1A1A1A'

        def prow(emoji, label, value):
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                content=ft.Row([
                    ft.Text(emoji, size=16),
                    ft.Column(spacing=1, controls=[
                        ft.Text(label, size=10, color=txt_dim),
                        ft.Text(value or '—', size=13, weight=ft.FontWeight.W_500, color=txt_val),
                    ]),
                ], spacing=12),
            )

        return ft.Container(
            border_radius=16,
            bgcolor=card,
            border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(spacing=0, controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    bgcolor=hdr_bg,
                    content=ft.Text('DATOS PERSONALES', size=10, weight=ft.FontWeight.W_700, color=hdr_txt),
                ),
                prow('🪪', 'NIF / DNI', self.user.nif),
                ft.Divider(height=1, color=div_col),
                prow('📧', 'Correo electrónico', self.user.email),
            ]),
        )

    # ─────────────────────────────────────────
    #  CONTACT SECTION
    # ─────────────────────────────────────────
    def _build_contact_section(self):
        tc      = getattr(self.page, 'tc_theme', {})
        accent  = tc.get('accent', '#A3E635')
        card    = tc.get('card', '#1C1E24')
        is_dark = tc.get('mode', 'light') == 'dark'
        hdr_bg  = ft.Colors.with_opacity(0.10, ft.Colors.WHITE) if is_dark else '#F1F8E9'
        div_col = ft.Colors.with_opacity(0.08, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)
        txt_dim = ft.Colors.with_opacity(0.45, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_400
        txt_val = ft.Colors.WHITE if is_dark else '#1A1A1A'

        def view_row(emoji, label, value):
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                content=ft.Row([
                    ft.Text(emoji, size=16),
                    ft.Column(spacing=1, controls=[
                        ft.Text(label, size=10, color=txt_dim),
                        ft.Text(value or '—', size=13, weight=ft.FontWeight.W_500, color=txt_val),
                    ]),
                ], spacing=12),
            )

        edit_btn = ft.TextButton(
            'Editar' if not self.edit_mode else 'Cancelar',
            icon=ft.Icons.EDIT_OUTLINED if not self.edit_mode else ft.Icons.CLOSE,
            on_click=self._toggle_edit_mode,
            style=ft.ButtonStyle(color=accent, padding=ft.padding.all(0)),
        )

        if self.edit_mode:
            body_controls = [
                ft.Container(height=4),
                self.direccion_input,
                self.ciudad_input,
                self.codigo_postal_input,
                self.provincia_input,
                self.telefono_input,
            ]
        else:
            div = lambda: ft.Divider(height=1, color=div_col)
            body_controls = [
                view_row('📍', 'Dirección',     self.user.direccion),
                div(),
                view_row('🏙', 'Ciudad',        self.user.ciudad),
                div(),
                view_row('📮', 'Código Postal', self.user.codigo_postal),
                div(),
                view_row('🗺', 'Provincia',     self.user.provincia),
                div(),
                view_row('📞', 'Teléfono',      self.user.telefono),
            ]

        return ft.Container(
            border_radius=16,
            bgcolor=card,
            border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(spacing=0, controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    bgcolor=hdr_bg,
                    content=ft.Row([
                        ft.Text('DIRECCIÓN', size=10, weight=ft.FontWeight.W_700, color=accent, expand=True),
                        edit_btn,
                    ]),
                ),
                *body_controls,
            ]),
        )

    # ─────────────────────────────────────────
    #  ACTIONS
    # ─────────────────────────────────────────
    def _build_actions_row(self):
        if self.edit_mode:
            return ft.Row(
                alignment=ft.MainAxisAlignment.END,
                spacing=10,
                controls=[
                    ft.OutlinedButton(
                        "Cancelar",
                        icon=ft.Icons.CLOSE,
                        on_click=self._toggle_edit_mode,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    ),
                    ft.FilledButton(
                        "Guardar",
                        icon=ft.Icons.SAVE_OUTLINED,
                        on_click=self._guardar_datos,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    ),
                ],
            )
        else:
            return ft.OutlinedButton(
                "Cerrar sesión",
                icon=ft.Icons.LOGOUT,
                on_click=lambda e: self.page.go('/login'),
                style=ft.ButtonStyle(
                    color=ft.Colors.ERROR,
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
                width=float('inf'),
            )

    # ─────────────────────────────────────────
    #  LOGIC
    # ─────────────────────────────────────────
    def _toggle_edit_mode(self, e):
        self.edit_mode = not self.edit_mode
        self.page.views[-1] = self.build()
        self.page.update()

    def _guardar_datos(self, e):
        Session = sessionmaker(bind=_engine())
        session = Session()
        try:
            u = session.query(Usuario).filter_by(id=self.user.id).first()
            u.direccion = self.direccion_input.value or ''
            u.ciudad = self.ciudad_input.value or ''
            u.provincia = self.provincia_input.value or ''
            u.codigo_postal = self.codigo_postal_input.value or ''
            u.telefono = self.telefono_input.value or ''
            session.commit()
        finally:
            session.close()

        self.user.direccion = self.direccion_input.value
        self.user.ciudad = self.ciudad_input.value
        self.user.provincia = self.provincia_input.value
        self.user.codigo_postal = self.codigo_postal_input.value
        self.user.telefono = self.telefono_input.value
        self.edit_mode = False

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Datos actualizados correctamente"),
            bgcolor=ft.Colors.GREEN_700,
        )
        self.page.snack_bar.open = True
        self.page.views[-1] = self.build()
        self.page.update()

    # ─────────────────────────────────────────
    #  THEME PICKER
    # ─────────────────────────────────────────
    def _build_theme_section(self):
        current_id = load_theme_id()

        def make_swatch(theme):
            is_selected = theme["id"] == current_id
            t_is_dark   = theme.get("mode", "light") == "dark"
            colors      = theme["preview_colors"]  # [appbar, accent, bg, card]
            label_bg    = theme["card"]
            label_txt   = ft.Colors.WHITE if t_is_dark else '#1A1A1A'
            label_sub   = ft.Colors.with_opacity(0.55, ft.Colors.WHITE) if t_is_dark else ft.Colors.GREY_500
            border_sel  = theme["accent"]

            strips = ft.Row(
                spacing=0,
                controls=[
                    ft.Container(bgcolor=c, expand=True, height=40)
                    for c in colors
                ],
            )

            card = ft.Container(
                expand=True,
                border_radius=14,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                border=ft.border.all(
                    2.5 if is_selected else 1,
                    border_sel if is_selected else ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                ),
                shadow=ft.BoxShadow(
                    blur_radius=10 if is_selected else 2,
                    color=ft.Colors.with_opacity(0.20 if is_selected else 0.06, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
                content=ft.Column(
                    spacing=0,
                    controls=[
                        strips,
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=10, vertical=10),
                            bgcolor=label_bg,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(theme["name"], size=12, weight=ft.FontWeight.W_700, color=label_txt),
                                            ft.Text(theme["desc"], size=9, color=label_sub),
                                        ],
                                    ),
                                    ft.Icon(
                                        ft.Icons.CHECK_CIRCLE_ROUNDED,
                                        size=18,
                                        color=border_sel,
                                        visible=is_selected,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
                on_click=lambda e, tid=theme["id"]: self._apply_theme(tid),
                animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            )
            return card

        swatches_row = ft.Row(
            spacing=12,
            controls=[make_swatch(t) for t in THEMES],
        )

        tc      = getattr(self.page, 'tc_theme', {})
        accent  = tc.get('accent', '#A3E635')
        card    = tc.get('card', '#1C1E24')
        is_dark = tc.get('mode', 'light') == 'dark'
        txt_val = ft.Colors.WHITE if is_dark else '#1A1A1A'

        return ft.Container(
            border_radius=16,
            bgcolor=card,
            border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)),
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.PALETTE_OUTLINED, size=16, color=accent),
                        ft.Text("Tema visual", size=13, weight=ft.FontWeight.W_600, color=txt_val),
                    ], spacing=8),
                    swatches_row,
                ],
            ),
        )

    def _apply_theme(self, theme_id: int):
        if hasattr(self.page, 'apply_theme'):
            self.page.apply_theme(theme_id)

    # ─────────────────────────────────────────
    #  NAV
    # ─────────────────────────────────────────
    def _build_bottom_appbar(self):
        ab_color = getattr(self.page, 'tc_theme', {}).get('appbar_color', '#0D0D0D')
        return build_bottom_nav(self.page, '/profile', ab_color)
