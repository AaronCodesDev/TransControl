import flet as ft
from database.models import Usuario
from database.db import SessionLocal

class UsersView:
    def __init__(self, page: ft.Page, theme_button, user=None):
        self.page = page
        self.theme_button = theme_button
        self.user = user
        self.users = []
        self.filtered_users = []
        self.search_term = ''
        self.table = ft.Column()
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(''),
            content=ft.Text(''),
            actions=[]
        )

    def build(self):
        self.page.overlay.clear()
        self._load_users()

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
        self.table.controls.append(self._build_users_list())

        return ft.View(
            route='/users',
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self._build_search_box(),
                            self.table,
                            self.dialog
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.alignment.top_center,
                    padding=ft.padding.only(top=40),
                    expand=True
                )
            ],
            appbar=ft.AppBar(
                title=ft.Text('Usuarios Registrados'),
                center_title=True,
                bgcolor=ft.Colors.GREEN_700,
                automatically_imply_leading=False,
                actions=actions,
            ),
            bottom_appbar=self._build_bottom_appbar()
        )

    def _load_users(self):
        db = SessionLocal()
        try:
            self.users = db.query(Usuario).all()
            self.filtered_users = self.users
        finally:
            db.close()

    def _build_users_list(self):
        columns = [
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Apellido")),
            ft.DataColumn(ft.Text("Dirección")),
            ft.DataColumn(ft.Text("Ciudad")),
            ft.DataColumn(ft.Text("Provincia")),
            ft.DataColumn(ft.Text("C P")),
            ft.DataColumn(ft.Text("Teléfono")),
            ft.DataColumn(ft.Text("Email")),
        ]

        rows = []
        for u in self.filtered_users:
            cells = [
                ft.DataCell(ft.Text(str(u.id)), ),
                ft.DataCell(ft.Text(u.nombre), on_tap=lambda e, u=u: self._on_user_click(e, u)),
                ft.DataCell(ft.Text(u.apellido)),
                ft.DataCell(ft.Text(u.direccion if hasattr(u, 'direccion') else '')),
                ft.DataCell(ft.Text(u.ciudad if hasattr(u, 'ciudad') else '')),
                ft.DataCell(ft.Text(u.provincia if hasattr(u, 'provincia') else '')),
                ft.DataCell(ft.Text(u.codigo_postal if hasattr(u, 'codigo_postal') else '')),
                ft.DataCell(ft.Text(u.telefono if hasattr(u, 'telefono') else '')),
                ft.DataCell(ft.Text(u.email)),
            ]
            rows.append(ft.DataRow(cells=cells))

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.DataTable(
                        columns=columns,
                        rows=rows,
                        column_spacing=10,
                        data_row_max_height=56,
                        horizontal_margin=10,
                    )
                ],
                scroll="auto"
            ),
            padding=10
        )

    def _build_search_box(self):
        return ft.TextField(
            label="Buscar usuario",
            hint_text="Nombre, apellido o email",
            value=self.search_term,
            width=350,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._filter_users
        )

    def _filter_users(self, e):
        self.search_term = e.control.value.lower()
        if self.search_term:
            self.filtered_users = [
                u for u in self.users
                if (u.nombre and self.search_term in u.nombre.lower())
                or (u.apellido and self.search_term in u.apellido.lower())
                or (u.email and self.search_term in u.email.lower())
            ]
        else:
            self.filtered_users = self.users

        self.table.controls.clear()
        self.table.controls.append(self._build_users_list())
        self.page.update()

    def _on_user_click(self, e, u):
        fields = {
            'nombre': ft.TextField(label="Nombre", value=u.nombre, disabled=True),
            'apellido': ft.TextField(label="Apellido", value=u.apellido, disabled=True),
            'direccion': ft.TextField(label="Dirección", value=u.direccion if hasattr(u, 'direccion') else '', disabled=True),
            'ciudad': ft.TextField(label="Ciudad", value=u.ciudad if hasattr(u, 'ciudad') else '', disabled=True),
            'provincia': ft.TextField(label="Provincia", value=u.provincia if hasattr(u, 'provincia') else '', disabled=True),
            'codigo_postal': ft.TextField(label="C P", value=u.codigo_postal if hasattr(u, 'codigo_postal') else '', disabled=True),
            'telefono': ft.TextField(label="Teléfono", value=u.telefono if hasattr(u, 'telefono') else '', disabled=True),
            'email': ft.TextField(label="Email", value=u.email if hasattr(u, 'email') else '', disabled=True),
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
                db_user = session.query(Usuario).filter(Usuario.id == u.id).first()
                if db_user:
                    db_user.nombre = fields['nombre'].value
                    db_user.apellido = fields['apellido'].value
                    db_user.direccion = fields['direccion'].value
                    db_user.ciudad = fields['ciudad'].value
                    db_user.provincia = fields['provincia'].value
                    db_user.codigo_postal = fields['codigo_postal'].value
                    db_user.telefono = fields['telefono'].value
                    db_user.email = fields['email'].value
                    session.commit()
                    print('Usuario actualizado correctamente')
                self.dialog.open = False
                self._load_users()
                self.table.controls.clear()
                self.table.controls.append(self._build_users_list())
            except Exception as ex:
                print(f'Error al actualizar usuario: {ex}')
                session.rollback()
            finally:
                session.close()
            self.page.update()

        def delete_user(e, user_id):
            session = SessionLocal()
            try:
                user_to_delete = session.query(Usuario).filter(Usuario.id == user_id).first()
                if user_to_delete:
                    session.delete(user_to_delete)
                    session.commit()
                    print(f'Usuario {user_to_delete.nombre} eliminado correctamente')
                    self._load_users()
                    self.table.controls.clear()
                    self.table.controls.append(self._build_users_list())
                    self.dialog.open = False
                else:
                    print(f'Usuario con ID {user_id} no encontrado.')
            except Exception as ex:
                print(f'Error al eliminar usuario: {ex}')
                session.rollback()
            finally:
                session.close()
            self.page.update()

        def close_dialog(e):
            self.dialog.open = False
            self.page.update()

        # Solo mostrar botones editar/guardar/borrar si el usuario actual es admin
        is_admin = self.user and getattr(self.user, 'rol', '') == 'admin'

        edit_button = ft.IconButton(icon=ft.Icons.EDIT, tooltip='Editar', on_click=edit_mode, visible=is_admin)
        save_button = ft.IconButton(icon=ft.Icons.SAVE, tooltip='Guardar', on_click=save_changes, visible=False)
        delete_button = ft.IconButton(icon=ft.Icons.DELETE, tooltip='Eliminar', on_click=lambda e: delete_user(e, u.id), visible=is_admin)
        close_button = ft.IconButton(icon=ft.Icons.CLOSE, tooltip='Cerrar', on_click=close_dialog)

        self.dialog.title = ft.Text(f'Información de {u.nombre}')
        self.dialog.content = ft.Column(list(fields.values()), tight=True)
        self.dialog.actions = [
            ft.Row(
                controls=[edit_button, save_button, delete_button, close_button],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ]
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
