import flet as ft
from datetime import date, datetime
from database.models import Documentos, Empresas
from database.crud import get_document_count, get_daily_routes, get_company_count
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class DashboardView:
    def __init__(self, page: ft.Page, theme_button, force_route):
        self.page = page
        self.theme_button = theme_button
        self.user = page.user
        self.force_route = force_route
        self.menu_visible = False

        self.total_routes = get_document_count(self.page.db)
        self.daily_routes = len(get_daily_routes(self.page.db, date.today()))
        self.company_count = get_company_count(self.page.db)

        self.welcome_card = self._build_welcome_card()
        self.stats_row = self._build_stats_row()

    def build(self):
        self._update_stats()
        return self._build_dashboard_view()

    def _build_dashboard_view(self):
        controls = [
            ft.Container(
                content=self.welcome_card,
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=50),
            ),
            self.stats_row,
        ]

        if self.user and self.user.rol == 'admin':
            admin_button = ft.IconButton(
                icon=ft.Icons.SECURITY,
                icon_color=ft.Colors.GREEN,
                tooltip='Panel de administración',
                on_click=lambda e: self._navigate_clean('/admin'),
            )
            controls.append(
                ft.Container(
                    content=admin_button,
                    margin=ft.margin.only(top=30, right=30),
                    alignment=ft.alignment.center_right
                )
            )

        return ft.View(
            '/dashboard',
            controls=[
                ft.Column(
                    controls=controls,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            appbar=ft.AppBar(
                title=ft.Text(f'Dashboard - {self.user.rol.capitalize()}'),
                center_title=True,
                bgcolor=ft.Colors.GREEN_300,
                automatically_imply_leading=False,
                actions=[self.theme_button],
            ),
            floating_action_button=self._build_fab(),
            floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_DOCKED,
            bottom_appbar=self._build_bottom_appbar()
        )

    def _build_welcome_card(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Bienvenido al Dashboard", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{self.user.nombre} {self.user.apellido}", size=16, italic=True, color=ft.Colors.GREY),
                        ft.Text(f"Rol: {self.user.rol}", size=14, color=ft.Colors.BLUE_GREY),
                        ft.Text(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", size=14, color=ft.Colors.BLUE_GREY),
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
                self._build_stat_card(ft.Icons.FORMAT_LIST_NUMBERED, 'Historial \nRutas \nRegistradas', str(self.total_routes)),
                self._build_stat_card(ft.Icons.ROUTE, 'Rutas \nRegistradas \nHoy', str(self.daily_routes)),
                self._build_stat_card(ft.Icons.APARTMENT, 'Empresas \nRegistradas \n', str(self.company_count)),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5
        )

    def _build_stat_card(self, icon, title, value):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=icon, size=40, color=ft.Colors.GREEN),
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
        def toggle_menu(e):
            self.menu_visible = not self.menu_visible
            self.page.overlay.clear()
            self.page.overlay.append(self._build_fab_menu())
            self.page.update()

        return ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=ft.Colors.GREEN,
            shape=ft.CircleBorder(),
            tooltip="Opciones rápidas",
            width=64,
            height=64,
            on_click=toggle_menu
        )

    def _build_fab_menu(self):
        def open_create_document(e):
            self._navigate_clean('/create_document')

        def open_create_company(e):
            self._navigate_clean('/create_company')

        if not self.menu_visible:
            return ft.Container()

        return ft.Stack(
            expand=True,
            controls=[
                ft.Container(
                    width=self.page.width,
                    height=self.page.height,
                    bgcolor=ft.Colors.BLACK54,
                    on_click=self._hide_menu
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.FloatingActionButton(
                                icon=ft.Icons.DESCRIPTION,
                                tooltip='Nuevo documento',
                                on_click=open_create_document,
                                width=64,
                                height=64
                            ),
                            ft.FloatingActionButton(
                                icon=ft.Icons.APARTMENT,
                                tooltip='Nueva empresa',
                                on_click=open_create_company,
                                width=64,
                                height=64,
                            ),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    left=(self.page.width - 64) / 2,
                    bottom=110,
                )
            ]
        )

    def _hide_menu(self, e=None):
        self.menu_visible = False
        self.page.overlay.clear()
        self.page.overlay.append(self._build_fab_menu())
        self.page.update()

    def _navigate_clean(self, route):
        self.menu_visible = False
        self.page.overlay.clear()
        self.page.go(route)

    def _build_bottom_appbar(self):
        return ft.BottomAppBar(
            bgcolor=ft.Colors.GREEN_300,
            shape=ft.NotchShape.CIRCULAR,
            elevation=8,
            content=ft.Row(
                controls=[
                    ft.IconButton(icon=ft.Icons.HOME, icon_color=ft.Colors.WHITE, tooltip="Inicio", on_click=lambda e: self._navigate_clean('/dashboard')),
                    ft.IconButton(icon=ft.Icons.FORMAT_LIST_NUMBERED, icon_color=ft.Colors.WHITE, tooltip="Documentos", on_click=lambda e: self._navigate_clean('/documents')),
                    ft.IconButton(icon=ft.Icons.APARTMENT, icon_color=ft.Colors.WHITE, tooltip="Empresas", on_click=lambda e: self._navigate_clean('/companies')),
                    ft.IconButton(icon=ft.Icons.PERSON, icon_color=ft.Colors.WHITE, tooltip="Perfil", on_click=lambda e: self._navigate_clean('/profile')),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            )
        )

    def _update_stats(self):
        self.total_routes = get_document_count(self.page.db)
        self.daily_routes = len(get_daily_routes(self.page.db, datetime.now().date()))
        self.company_count = get_company_count(self.page.db)
        self.page.update()
