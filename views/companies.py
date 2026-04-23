import flet as ft
from database.models import Empresas
from database.db import SessionLocal
from sqlalchemy.orm import joinedload


class CompaniesView:
    def __init__(self, page: ft.Page, theme_button, user=None):
        self.page = page
        self.theme_button = theme_button
        self.user = user
        self.companies = []
        self.filtered_companies = []
        self.search_term = ''
        self.table = ft.Column()
        self.dialog = ft.AlertDialog(modal=True, title=ft.Text(''), content=ft.Text(''), actions=[])

    def build(self):
        self.page.overlay.clear()
        self._load_companies()

        tc       = getattr(self.page, 'tc_theme', {})
        ab_color = tc.get('appbar_color', '#0D0D0D')
        accent   = tc.get('accent', '#A3E635')
        bg       = tc.get('bg', '#0D0D0D')

        admin_btn = None
        if self.user and getattr(self.user, 'rol', '') == 'admin':
            admin_btn = ft.IconButton(
                icon=ft.Icons.SECURITY,
                icon_color=ft.Colors.WHITE,
                tooltip='Panel de administración',
                on_click=lambda e: self.page.go('/admin'),
            )

        header = ft.Container(
            padding=ft.padding.only(top=48, bottom=24, left=20, right=20),
            bgcolor=ab_color,
            content=ft.Column(spacing=0, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text('TransControl', size=14, weight=ft.FontWeight.W_600,
                                color=ft.Colors.with_opacity(0.50, ft.Colors.WHITE)),
                        ft.Row(spacing=0, controls=[
                            *(([admin_btn]) if admin_btn else []),
                            self.theme_button,
                        ]),
                    ],
                ),
                ft.Container(height=14),
                ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Container(
                        width=40, height=40, border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.15, accent),
                        alignment=ft.alignment.center,
                        content=ft.Icon(ft.Icons.APARTMENT_ROUNDED, color=accent, size=22),
                    ),
                    ft.Text('Empresas', size=22, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                ]),
            ]),
        )

        self.table.controls.clear()
        self.table.controls.append(self._build_companies_list())

        body = ft.Container(
            expand=True,
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            bgcolor=bg,
            padding=ft.padding.only(left=16, right=16, top=20, bottom=90),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
                controls=[
                    self._build_search_box(),
                    self.table,
                    self.dialog,
                ],
            ),
        )

        return ft.View(
            route='/companies',
            padding=0,
            bgcolor=bg,
            controls=[
                ft.Column(spacing=0, expand=True, controls=[header, body]),
            ],
            bottom_appbar=self._build_bottom_appbar(),
            floating_action_button=ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                bgcolor=accent,
                shape=ft.CircleBorder(),
                width=54, height=54,
                tooltip="Nueva empresa",
                on_click=lambda e: self.page.go('/create_company'),
            ),
            floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_FLOAT,
        )

    def _load_companies(self):
        db = SessionLocal()
        try:
            query = db.query(Empresas).options(joinedload(Empresas.usuario))
            if self.user and getattr(self.user, 'rol', '') == 'admin':
                self.companies = query.all()
            elif self.user and hasattr(self.user, 'id'):
                self.companies = query.filter(Empresas.usuario_id == self.user.id).all()
            else:
                self.companies = []
            self.filtered_companies = self.companies
        finally:
            db.close()

    def _build_companies_list(self):
        tc      = getattr(self.page, 'tc_theme', {})
        accent  = tc.get('accent', '#A3E635')
        card    = tc.get('card', '#1C1E24')
        is_dark = tc.get('mode', 'light') == 'dark'
        text_secondary = ft.Colors.with_opacity(0.55, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_600
        border_col = ft.Colors.with_opacity(0.07, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)

        if not self.filtered_companies:
            return ft.Container(
                padding=40,
                alignment=ft.alignment.center,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.APARTMENT_OUTLINED, size=64, color=ft.Colors.GREY_400),
                        ft.Text("No hay empresas registradas", size=16, color=ft.Colors.GREY_500),
                        ft.Text("Pulsa + para añadir una empresa", size=13, color=ft.Colors.GREY_400),
                    ],
                ),
            )

        cards = []
        for c in self.filtered_companies:
            is_admin = self.user and getattr(self.user, 'rol', '') == 'admin'
            owner_row = ft.Row([
                ft.Icon(ft.Icons.PERSON_OUTLINE, size=11, color=text_secondary),
                ft.Text(c.usuario.email if c.usuario else '—', size=11, color=text_secondary),
            ], spacing=4) if is_admin else ft.Container()

            card_widget = ft.GestureDetector(
                on_tap=lambda e, company=c: self._on_company_click(e, company),
                content=ft.Container(
                    border_radius=16,
                    bgcolor=card,
                    border=ft.border.all(1, border_col),
                    shadow=ft.BoxShadow(
                        blur_radius=12,
                        color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                        offset=ft.Offset(0, 3),
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=14),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(spacing=12, expand=True, controls=[
                                ft.Container(
                                    width=42, height=42, border_radius=12,
                                    bgcolor=ft.Colors.with_opacity(0.15, accent),
                                    alignment=ft.alignment.center,
                                    content=ft.Icon(ft.Icons.APARTMENT_ROUNDED, color=accent, size=22),
                                ),
                                ft.Column(spacing=2, expand=True, controls=[
                                    ft.Text(c.nombre, size=14, weight=ft.FontWeight.W_700,
                                            color=accent, max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Row(spacing=6, controls=[
                                        ft.Text(c.cif or '—', size=11, color=text_secondary),
                                        ft.Text('·', size=11, color=text_secondary),
                                        ft.Text(c.ciudad or '—', size=11, color=text_secondary),
                                    ]),
                                    owner_row,
                                ]),
                            ]),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color=text_secondary, size=20),
                        ],
                    ),
                ),
            )
            cards.append(card_widget)

        return ft.Column(spacing=10, controls=cards)

    def _build_search_box(self):
        tc      = getattr(self.page, 'tc_theme', {})
        card    = tc.get('card', '#1C1E24')
        accent  = tc.get('accent', '#A3E635')
        is_dark = tc.get('mode', 'light') == 'dark'
        hint_col  = ft.Colors.with_opacity(0.40, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_400
        icon_col  = ft.Colors.with_opacity(0.50, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_500
        box_bg    = card if is_dark else ft.Colors.WHITE
        return ft.Container(
            border_radius=16,
            bgcolor=box_bg,
            border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)),
            shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK), offset=ft.Offset(0, 3)),
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
            content=ft.TextField(
                hint_text="Buscar empresa…",
                hint_style=ft.TextStyle(color=hint_col),
                value=self.search_term,
                prefix_icon=ft.Icons.SEARCH,
                color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                border=ft.InputBorder.NONE,
                on_change=self._filter_companies,
            ),
        )

    def _filter_companies(self, e):
        self.search_term = e.control.value
        search_term = self.search_term.lower()
        self.filtered_companies = (
            [c for c in self.companies if search_term in c.nombre.lower()]
            if search_term else self.companies
        )
        self.table.controls.clear()
        self.table.controls.append(self._build_companies_list())
        self.page.update()

    def _on_company_click(self, e, c):
        fields = {
            'nombre': ft.TextField(label="Nombre", value=c.nombre, disabled=True, border_radius=10, filled=True),
            'cif': ft.TextField(label="CIF", value=c.cif, disabled=True, border_radius=10, filled=True),
            'direccion': ft.TextField(label="Dirección", value=c.direccion, disabled=True, border_radius=10, filled=True),
            'ciudad': ft.TextField(label="Ciudad", value=c.ciudad, disabled=True, border_radius=10, filled=True),
            'provincia': ft.TextField(label="Provincia", value=c.provincia, disabled=True, border_radius=10, filled=True),
            'codigo_postal': ft.TextField(label="Código Postal", value=c.codigo_postal, disabled=True, border_radius=10, filled=True),
            'telefono': ft.TextField(label="Teléfono", value=c.telefono, disabled=True, border_radius=10, filled=True),
            'email': ft.TextField(label="Email", value=c.email if hasattr(c, 'email') else '', disabled=True, border_radius=10, filled=True),
        }

        def edit_mode(e):
            for f in fields.values():
                f.disabled = False
            edit_button.visible = False
            save_button.visible = True
            delete_button.visible = True
            self.page.update()

        def save_changes(e):
            session = SessionLocal()
            try:
                db_company = session.query(Empresas).filter(Empresas.id == c.id).first()
                if db_company:
                    db_company.nombre = fields['nombre'].value
                    db_company.cif = fields['cif'].value
                    db_company.direccion = fields['direccion'].value
                    db_company.telefono = fields['telefono'].value
                    db_company.email = fields['email'].value
                    session.commit()
                self.dialog.open = False
                self._load_companies()
                self.table.controls.clear()
                self.table.controls.append(self._build_companies_list())
            except Exception as ex:
                session.rollback()
            finally:
                session.close()
            self.page.update()

        def close_dialog(e):
            self.dialog.open = False
            self.page.update()

        def delete_company(e, company_id):
            session = SessionLocal()
            try:
                company = session.query(Empresas).filter(Empresas.id == company_id).first()
                if company:
                    session.delete(company)
                    session.commit()
                    self._load_companies()
                    self.table.controls.clear()
                    self.table.controls.append(self._build_companies_list())
                    self.dialog.open = False
            except Exception as ex:
                session.rollback()
            finally:
                session.close()
            self.page.update()

        edit_button = ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, tooltip='Editar', on_click=edit_mode, icon_color=ft.Colors.BLUE_700)
        save_button = ft.IconButton(icon=ft.Icons.SAVE_OUTLINED, tooltip='Guardar', on_click=save_changes, visible=False, icon_color=ft.Colors.GREEN_700)
        delete_button = ft.IconButton(icon=ft.Icons.DELETE_OUTLINED, tooltip='Eliminar', on_click=lambda e: delete_company(e, c.id), icon_color=ft.Colors.ERROR, visible=False)
        close_button = ft.IconButton(icon=ft.Icons.CLOSE, tooltip='Cerrar', on_click=close_dialog)

        self.dialog.title = ft.Row([
            ft.Icon(ft.Icons.APARTMENT, color=ft.Colors.GREEN_700),
            ft.Text(c.nombre, weight=ft.FontWeight.W_600),
        ], spacing=8)
        self.dialog.content = ft.Container(
            content=ft.Column(list(fields.values()), tight=True, spacing=10, scroll=ft.ScrollMode.AUTO),
            width=320,
        )
        self.dialog.actions = [
            ft.Row(
                controls=[edit_button, save_button, delete_button, close_button],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        ]
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _build_bottom_appbar(self):
        ab_color = getattr(self.page, 'tc_theme', {}).get('appbar_color', '#1B5E20')
        accent   = getattr(self.page, 'tc_theme', {}).get('accent', '#43A047')
        return ft.BottomAppBar(
            bgcolor=ab_color,
            elevation=8,
            content=ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    ft.IconButton(icon=ft.Icons.HOME_ROUNDED,                 icon_color=ft.Colors.WHITE, tooltip="Inicio",      on_click=lambda e: self.page.go('/dashboard')),
                    ft.IconButton(icon=ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED,  icon_color=ft.Colors.WHITE, tooltip="Documentos",  on_click=lambda e: self.page.go('/documents')),
                    ft.IconButton(icon=ft.Icons.DIRECTIONS_CAR_ROUNDED,        icon_color=ft.Colors.WHITE, tooltip="Vehículos",   on_click=lambda e: self.page.go('/vehicles')),
                    ft.IconButton(icon=ft.Icons.APARTMENT_ROUNDED,             icon_color=accent,          tooltip="Empresas"),
                    ft.IconButton(icon=ft.Icons.PERSON_ROUNDED,                icon_color=ft.Colors.WHITE, tooltip="Perfil",      on_click=lambda e: self.page.go('/profile')),
                ],
            ),
        )
