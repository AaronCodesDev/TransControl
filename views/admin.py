import flet as ft

class AdminDashboardView:
    def __init__(self, page, theme_button, force_route):
        self.page = page
        self.theme_button = theme_button
        self.force_route = force_route

    def build(self):
        return ft.View(
            route="/admin",
            controls=[
                ft.Text("Añadir contenido admin..."),
            ],
            appbar=ft.AppBar(
                title=ft.Text("Panel de Administración"),
                center_title=True,
                bgcolor=ft.Colors.BLUE_700,  # Azul como pediste
                automatically_imply_leading=False,
                actions=[self.theme_button],
            ),
            floating_action_button=ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                bgcolor=ft.Colors.BLUE_700,
                shape=ft.CircleBorder(),
                on_click=lambda e: print("FAB presionado"),
),
            floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_DOCKED,
            bottom_appbar=self._build_bottom_appbar()
        )

    def _build_bottom_appbar(self):
        return ft.BottomAppBar(
            bgcolor=ft.Colors.BLUE_900,
            shape=ft.NotchShape.CIRCULAR,
            elevation=8,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.HOME,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Inicio",
                        on_click=lambda e: self.page.go('/dashboard')
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SECURITY,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Admin",
                        on_click=lambda e: self.page.go('/admin')
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PERSON,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Perfil",
                        on_click=lambda e: self.page.go('/profile')
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
        )
