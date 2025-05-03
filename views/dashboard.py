import flet as ft
from datetime import datetime
from database.models import Documentos, Empresas , Usuario
from database.crud import get_document_count, get_daily_routes, get_company_count

class DashboardView:
    def __init__(self, page: ft.Page, theme_button):
        self.page = page
        self.theme_button = theme_button
        self.user = page.user
        
        self.total_routes = None
        self.daily_routes = None
        self.company_count = get_company_count(self.page.db)
        
        self.welcome_card = self._build_welcome_card()
        self.stats_row = self._build_stats_row()

    def build(self):
        self.page.views.clear()
        self.page.views.append(self._build_loading_view())
        self.page.update()
        
        self._load_dashboard()

    def _load_dashboard(self):
        self._update_stats()

        self.page.views.clear()
        self.page.views.append(
            ft.View(
                '/dashboard',
                controls=[
                    ft.Column(
                        controls=[
                            ft.Container(
                                content=self.welcome_card,
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=50),
                            ),
                            self.stats_row
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                appbar=ft.AppBar(
                    title=ft.Text(f'Dashboard - {self.user.rol.capitalize()}'),
                    center_title=True,
                    bgcolor=ft.colors.GREEN_300,
                    automatically_imply_leading=False,
                    actions=[self.theme_button],
                ),
                floating_action_button=self._build_fab(),  
                floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_DOCKED,
                bottom_appbar=self._build_bottom_appbar()
            )
        )
        self.page.update()

    def _build_welcome_card(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Bienvenido al Dashboard", size=20, weight="bold"),
                        ft.Text(f"{self.user.nombre} {self.user.apellido}", size=16, italic=True, color=ft.colors.GREY),
                        ft.Text(f"Rol: {self.user.rol}", size=14, color=ft.colors.BLUE_GREY),
                        ft.Text(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", size=14, color=ft.colors.BLUE_GREY),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=30,
                width=350,
                height=180,
                alignment=ft.alignment.center,
            ),
            elevation=8,
        )

    def _build_stats_row(self):
        return ft.Row(
            controls=[
                self._build_stat_card(
                    ft.icons.FORMAT_LIST_NUMBERED,
                    f'Historial \nRutas \nRegistradas',
                    str(self.total_routes) if self.total_routes is not None else "..."
                ),
                self._build_stat_card(
                    ft.icons.ROUTE,
                    f'Rutas \nRegistradas \nHoy', 
                    str(self.daily_routes) if self.daily_routes is not None else "..."
                    ),
                self._build_stat_card(
                    ft.icons.APARTMENT, 
                    f'Empresas \nRegistradas \n ', 
                    str(self.company_count) if self.company_count is not None else "..."
                    ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            
            spacing=5
        )

    def _build_stat_card(self, icon, title, value):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=icon, size=40, color=ft.colors.GREEN),
                        ft.Text(title, size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Text(value, size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=10,
                width=110,
                alignment=ft.alignment.center,
            )
        )

    def _build_fab(self):
        return ft.FloatingActionButton(
            icon=ft.icons.ADD,
            bgcolor=ft.colors.GREEN,
            shape=ft.CircleBorder(),
            width=56,
            height=56,
            tooltip="Nuevo documento",
            on_click=self._show_create_document_dialog  # <-- Aquí llamamos a abrir el diálogo
        )

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

    def _update_stats(self):
        self.total_routes = get_document_count(self.page.db)
        self.daily_routes = len(get_daily_routes(self.page.db, datetime.now().date()))
        self.company_count = get_company_count(self.page.db)
        self.page.update()

    def _create_new_document(self, e):
        print("Creando nuevo documento...")

    def _build_loading_view(self):
        return ft.View(
            '/loading',
            controls=[
                ft.Column(
                    [
                        ft.ProgressRing(width=50, height=50, stroke_width=6, color=ft.colors.GREEN),
                        ft.Text("Cargando Dashboard...", size=20),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
        )

    def _show_create_document_dialog(self, e):
        """Muestra un dialogo para confirmar creación de documento"""
        def confirm_create_document(ev):
            print("✅ Documento creado!")
            self.page.dialog.open = False
            self.page.update()

        def cancel(ev):
            self.page.dialog.open = False
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Crear nuevo documento"),
            content=ft.Text("¿Deseas crear un nuevo documento?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel),
                ft.ElevatedButton("Confirmar", on_click=confirm_create_document),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()
