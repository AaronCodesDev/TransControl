import flet as ft
from database.models import SessionLocal, Usuario

class UsersView:
    def __init__(self, page: ft.Page, theme_button, force_route):
        self.page = page
        self.theme_button = theme_button
        self.users = []
        self.filtered_users = []
        self.search_term = ''
        self.table = ft.Column()
        self.force_route = force_route

    def build(self):
        self.page.overlay.clear()
        self._load_users()
        self._update_users_list()

        return ft.View(
            route='/users',
            appbar=ft.AppBar(
                title=ft.Text('Usuarios Registrados'),
                center_title=True,
                bgcolor=ft.Colors.GREEN_700,
                automatically_imply_leading=False,
                actions=[
                    ft.IconButton(
                        icon=ft.Icons.SECURITY,
                        tooltip='Panel de administración',
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.page.go('/admin')
                    ),
                    self.theme_button
                ]
            ),
            controls=[
                ft.Column(
                    controls=[
                        self._build_search_box(),
                        ft.Container(
                            content=ft.Row(
                                controls=[self.table],
                                scroll="auto"  # Permite scroll horizontal
                            ),
                            expand=True,
                            padding=10,
                            margin=ft.margin.symmetric(horizontal=10),
                            height=600,
                            width=float("inf"),  # Ocupa todo el ancho disponible
                            alignment=ft.alignment.center,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=10,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.GREY_300),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    scroll=True,  # Scroll vertical si la columna es muy larga
                    expand=True
                )
            ],
            bottom_appbar=self._build_bottom_appbar()
        )

    def _load_users(self):
        db = SessionLocal()
        self.users = db.query(Usuario).all()
        self.filtered_users = self.users
        db.close()

    def _build_users_list(self):
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("Nombre", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("Apellido", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("Dirección", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("Ciudad", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("Provincia", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("C P", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("Teléfono", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("Email", color=ft.Colors.BLACK)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(u.id), max_lines=1, overflow='ellipsis', color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(u.nombre, max_lines=1, overflow='ellipsis', color=ft.Colors.BLACK), on_tap=self._on_user_click, data=u),
                        ft.DataCell(ft.Text(u.apellido, max_lines=1, overflow='ellipsis', color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(u.direccion, max_lines=1, overflow='ellipsis', color=ft.Colors.BLACK) if hasattr(u, 'direccion') else ft.Text('')),
                        ft.DataCell(ft.Text(u.ciudad, max_lines=1, overflow='ellipsis', color=ft.Colors.BLACK) if hasattr(u, 'ciudad') else ft.Text('')),
                        ft.DataCell(ft.Text(u.provincia, max_lines=1, overflow='ellipsis', color=ft.Colors.BLACK) if hasattr(u, 'provincia') else ft.Text('')),
                        ft.DataCell(ft.Text(u.codigo_postal, max_lines=1, overflow='ellipsis', color=ft.Colors.BLACK) if hasattr(u, 'codigo_postal') else ft.Text('')),
                        ft.DataCell(ft.Text(u.telefono, max_lines=1, overflow='ellipsis', color=ft.Colors.BLACK) if hasattr(u, 'telefono') else ft.Text('')),
                        ft.DataCell(ft.Text(u.email, max_lines=1, overflow='ellipsis', color=ft.Colors.BLACK)),
                    ]
                )
                for u in self.filtered_users
            ],
            column_spacing=10,
            data_row_max_height=56
        )

    def _build_search_box(self):
        return ft.TextField(
            label="Buscar usuario",
            hint_text="Nombre, apellido o email",
            value=self.search_term,
            width=350,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._filter_users,
            text_style=ft.TextStyle(color=ft.Colors.BLACK)
        )

    def _filter_users(self, e):
        self.search_term = e.control.value
        search_term = self.search_term.lower()
        self.filtered_users = [
            u for u in self.users
            if search_term in u.nombre.lower() or
               search_term in u.apellido.lower() or
               (u.email and search_term in u.email.lower())
        ] if search_term else self.users

        self._update_users_list()

    def _update_users_list(self):
        self.table.controls.clear()
        self.table.controls.append(self._build_users_list())
        self.page.update()

    def _on_user_click(self, e):
        user = e.control.data
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f'Detalle de usuario: {user.nombre}'),
            content=ft.Text(f"ID: {user.id}\nNombre: {user.nombre}\nEmail: {user.email}"),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.page.dialog.dismiss())
            ]
        )
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _build_bottom_appbar(self):
        return ft.BottomAppBar(
            bgcolor=ft.Colors.GREEN_700,
            shape=ft.NotchShape.CIRCULAR,
            elevation=8,
            content=ft.Row(
                controls=[
                    ft.IconButton(icon=ft.Icons.HOME, icon_color=ft.Colors.WHITE, tooltip="Inicio", on_click=lambda e: self.page.go('/dashboard')),
                    ft.IconButton(icon=ft.Icons.FORMAT_LIST_NUMBERED, icon_color=ft.Colors.WHITE, tooltip="Documentos", on_click=lambda e: self.page.go('/documents')),
                    ft.IconButton(icon=ft.Icons.APARTMENT, icon_color=ft.Colors.WHITE, tooltip="Empresas", on_click=lambda e: self.page.go('/companies')),
                    ft.IconButton(icon=ft.Icons.PERSON, icon_color=ft.Colors.WHITE, tooltip="Perfil", on_click=lambda e: self.page.go('/profile')),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            )
        )
