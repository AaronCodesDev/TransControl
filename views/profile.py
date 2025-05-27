import flet as ft
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Usuario

class ProfileView:
    def __init__(self, page: ft.Page, theme_button, user=None):
        self.page = page
        self.theme_button = theme_button
        self.user = user or page.user
        self.edit_mode = False
        self.direccion_input = ft.TextField(label='Dirección', value=self.user.direccion, width=350)
        self.ciudad_input = ft.TextField(label='Ciudad', value=self.user.ciudad, width=350)
        self.provincia_input = ft.TextField(label='Provincia', value=self.user.provincia, width=350)
        self.codigo_postal_input = ft.TextField(label='Código Postal', value=self.user.codigo_postal, width=350)
        self.telefono_input = ft.TextField(label='Teléfono', value=self.user.telefono, width=350)

    def _guardar_datos(self, e):
        engine = create_engine('sqlite:///database/transcontrol.db')
        Session = sessionmaker(bind=engine)
        session = Session()

        usuario = session.query(Usuario).filter_by(id=self.user.id).first()

        usuario.direccion = self.direccion_input.value or ''
        usuario.ciudad = self.ciudad_input.value or ''
        usuario.provincia = self.provincia_input.value or ''
        usuario.codigo_postal = self.codigo_postal_input.value or ''
        usuario.telefono = self.telefono_input.value or ''

        session.commit()
        session.close()

        self.user.direccion = self.direccion_input.value
        self.user.ciudad = self.ciudad_input.value
        self.user.provincia = self.provincia_input.value
        self.user.codigo_postal = self.codigo_postal_input.value
        self.user.telefono = self.telefono_input.value

        self.edit_mode = False

        self.page.snack_bar = ft.SnackBar(ft.Text("✅ Datos actualizados correctamente"), bgcolor=ft.colors.GREEN)
        self.page.snack_bar.open = True
        
        self.page.views[-1] = self.build()
        self.page.update()

    def _toggle_edit_mode(self, e):
        self.edit_mode = not self.edit_mode
        self.page.views[-1] = self.build()
        self.page.update()

    def build(self):
        # Construir la lista de acciones con botón admin si corresponde
        admin_button = None
        if self.user and getattr(self.user, 'rol', '') == 'admin':
            admin_button = ft.IconButton(
                icon=ft.icons.SECURITY,
                icon_color=ft.Colors.WHITE,
                tooltip='Panel de administración',
                on_click=lambda e: self.page.go('/admin'),
            )
        if admin_button:
            actions = [admin_button, self.theme_button]
        else:
            actions = [self.theme_button]

        return ft.View(
            route='/profile',
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        controls=[
                            ft.Row(alignment=ft.MainAxisAlignment.END),
                            self._build_profile_card(),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10
                    )
                )
            ],
            appbar=ft.AppBar(
                title=ft.Text(f'Perfil - {self.user.nombre}'),
                center_title=True,
                bgcolor=ft.colors.GREEN_300,
                automatically_imply_leading=False,
                actions=actions,
            ),
            bottom_appbar=self._build_bottom_appbar()
        )



    def _build_profile_card(self):
        editable = not all([
            self.user.direccion,
            self.user.ciudad,
            self.user.provincia,
            self.user.codigo_postal,
            self.user.telefono
        ]) or self.edit_mode

        controls = [
            ft.Text("Perfil de Usuario", size=22, weight='bold'),
            ft.Divider(),
            ft.Text(f'Nombre: {self.user.nombre}', size=16, italic=True, color=ft.Colors.GREY),
            ft.Text(f'Apellido: {self.user.apellido}', size=16, italic=True, color=ft.Colors.GREY),
            ft.Text(f'Email: {self.user.email}', size=16, italic=True, color=ft.Colors.GREY),
            ft.Divider(),
        ]

        if editable:
            controls += [
                self.direccion_input,
                self.ciudad_input,
                self.provincia_input,
                self.codigo_postal_input,
                self.telefono_input,
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Guardar cambios", on_click=self._guardar_datos),
                        ft.ElevatedButton("Cerrar Sesión", bgcolor=ft.colors.RED_300, color=ft.colors.WHITE,
                                          on_click=lambda e: self.page.go('/login'))
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                )
            ]
        else:
            controls += [
                ft.Text(f'Dirección: {self.user.direccion}'),
                ft.Text(f'Ciudad: {self.user.ciudad}'),
                ft.Text(f'Provincia: {self.user.provincia}'),   
                ft.Text(f'Código Postal: {self.user.codigo_postal}'),
                ft.Text(f'Teléfono: {self.user.telefono}'),
                ft.Row(
                    controls=[
                        ft.OutlinedButton("Editar datos", on_click=self._toggle_edit_mode),
                        ft.ElevatedButton("Cerrar Sesión", bgcolor=ft.colors.RED_300, color=ft.colors.WHITE,
                                          on_click=lambda e: self.page.go('/login'))
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                )
            ]

        return ft.Card(
            elevation=8,
            content=ft.Container(
                width=350,
                padding=ft.Padding(top=10, left=30, right=30, bottom=20),  # ⬅️ padding superior reducido
                alignment=ft.alignment.center,
                content=ft.Column(
                    controls,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                )
            )
        )


    def _build_bottom_appbar(self):
        return ft.BottomAppBar(
            bgcolor=ft.colors.GREEN_300,
            shape=ft.NotchShape.CIRCULAR,
            elevation=8,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.HOME,
                        icon_color=ft.colors.WHITE,
                        tooltip="Inicio",
                        on_click=lambda e: self.page.go('/dashboard')
                    ),
                    ft.IconButton(
                        icon=ft.icons.FORMAT_LIST_NUMBERED,
                        icon_color=ft.colors.WHITE,
                        tooltip="Documentos",
                        on_click=lambda e: self.page.go('/documents')
                    ),
                    ft.IconButton(
                        icon=ft.icons.APARTMENT,
                        icon_color=ft.colors.WHITE,
                        tooltip="Empresas",
                        on_click=lambda e: self.page.go('/companies')
                    ),
                    ft.IconButton(
                        icon=ft.icons.PERSON,
                        icon_color=ft.colors.WHITE,
                        tooltip="Perfil",
                        on_click=lambda e: self.page.go('/profile')
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            )
        )
