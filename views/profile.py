import flet as ft

class ProfileView:
    def __init__(self, page: ft.Page, theme_button):
        self.page = page
        self.theme_button = theme_button
        self.user = page.user

    def build(self):
        return ft.View(
            route='/profile',
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.END),
                        self._build_profile_card(),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=30
                )
            ],
            appbar=ft.AppBar(
                title=ft.Text(f'Perfil - {self.user.nombre}'),
                center_title=True,
                bgcolor=ft.colors.GREEN_300,
                automatically_imply_leading=False,
                actions=[self.theme_button],
            ),
            bottom_appbar=self._build_bottom_appbar()
        )

    def _build_profile_card(self):
        return ft.Card(
            elevation=8,
            content=ft.Container(
                width=350,
                padding=30,
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Text("Perfil de Usuario", size=22, weight='bold'),
                        ft.Divider(),
                        ft.Text(f'Nombre: {self.user.nombre}', size=16, italic=True, color=ft.colors.GREY),
                        ft.Text(f'Apellido: {self.user.apellido}', size=16, italic=True, color=ft.colors.GREY),
                        ft.Text(f'Email: {self.user.email}', size=16, italic=True, color=ft.colors.GREY),
                        ft.Text(f'Rol: {self.user.rol}', size=14, color=ft.colors.BLUE_GREY),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                )
            ),
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
