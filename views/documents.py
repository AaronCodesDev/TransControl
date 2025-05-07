import flet as ft
from database.models import SessionLocal, Empresas, Documentos #Usuario

class DocumentsView:
    def __init__(self, page: ft.Page, theme_button):
        self.page = page
        self.theme_button = theme_button
        
    def build(self):

        self.page.views.clear()
        self.page.views.append(
            ft.View(
                '/documents',
                controls=[
                    ft.Column(
                        controls=[
                
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                        scroll=True,
                        expand=True
                    ),
                ],
                appbar=ft.AppBar(
                    title=ft.Text('Documentos Registrados'),
                    center_title=True,
                    bgcolor=ft.colors.GREEN_300,
                    automatically_imply_leading=False,
                    actions=[self.theme_button],
                ),
                bottom_appbar=self._build_bottom_appbar()
            )
        )
        self.page.update()

        
    def _build_bottom_appbar(self):
        return ft.BottomAppBar(
            bgcolor=ft.colors.GREEN_300,
            shape=ft.NotchShape.CIRCULAR,
            elevation=8,
            content=ft.Row(
                controls=[
                    ft.IconButton(icon=ft.icons.HOME, icon_color=ft.colors.WHITE, tooltip="Inicio", on_click=lambda e: self.page.go('/dashboard')),
                    ft.IconButton(icon=ft.icons.FORMAT_LIST_NUMBERED, icon_color=ft.colors.WHITE, tooltip="Documentos", on_click=lambda e: self.page.go('/documents')),
                    ft.IconButton(icon=ft.icons.APARTMENT, icon_color=ft.colors.WHITE, tooltip="Empresas", on_click=lambda e: self.page.go('/companies')),
                    ft.IconButton(icon=ft.icons.PERSON, icon_color=ft.colors.WHITE, tooltip="Perfil", on_click=lambda e: self.page.go('/profile')),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            )
        )