import flet as ft
from datetime import date, datetime
from database.crud import get_document_count_all, get_daily_routes,  get_company_count_all, get_user_count_all

class AdminDashboardView:
    def __init__(self, page: ft.Page, theme_button, force_route):
        self.page = page
        self.theme_button = theme_button
        self.force_route = force_route
        self.user = page.user
        self.menu_visible = False

        # Detectar modo inicial
        self.is_dark_mode = self.page.theme_mode == ft.ThemeMode.DARK

        # mirar cambios de tema
        self.page.on_theme_change = self._on_theme_change

        # Stats iniciales
        self.total_routes = get_document_count_all(self.page.db)
        self.daily_routes = len(get_daily_routes(self.page.db, date.today()))
        self.company_count = get_company_count_all(self.page.db)
        self.user_count = get_user_count_all(self.page.db)

        self.welcome_card = self._build_welcome_card()
        self.stats_row = self._build_stats_row()

    def _on_theme_change(self, e):
        self.is_dark_mode = e.data == "dark"
        self.page.views[-1] = self.build()  
        self.page.update()

    def build(self):
        self._update_stats()

        admin_button = None
        if self.user and self.user.rol == "admin":
            admin_button = ft.IconButton(
                icon=ft.Icons.SECURITY,
                icon_color=ft.Colors.ON_PRIMARY,
                tooltip="Panel de administración",
                on_click=lambda e: self._navigate_clean("/admin"),
            )

        actions = [self.theme_button]
        if admin_button:
            actions.insert(0, admin_button)

        return self._build_admin_view(actions)

    def _build_admin_view(self, actions):
        print("is_dark_mode:", self.is_dark_mode)
        title_color = ft.Colors.WHITE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK,


        return ft.View(
            route="/admin",
            controls=[
                ft.Column(
                    controls=[
                        ft.Container(
                            content=self.welcome_card,
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=50),
                        ),
                        self.stats_row,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
                        
            appbar=ft.AppBar(
                title=ft.Text(
                    f"Panel de Administración - {self.user.rol.capitalize()}",
                    color=title_color,
                ),
                center_title=True,
                bgcolor=ft.Colors.BLUE_700,
                automatically_imply_leading=False,
                actions=actions,
            ),
            floating_action_button=self._build_fab(),
            floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_DOCKED,
            bottom_appbar=self._build_bottom_appbar(),
            bgcolor=ft.Colors.SURFACE,
        )

    def _build_welcome_card(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Bienvenido al Panel Admin",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            f"{self.user.nombre} {self.user.apellido}",
                            size=16,
                            italic=True,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            f"Rol: {self.user.rol}",
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            f"Fecha: {datetime.now().strftime('%d/%m/%Y')}",
                            size=14,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=30,
                width=350,
                height=180,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.SURFACE,
                border_radius=10,
            ),
            elevation=8,
        )

    def _build_stats_row(self):
        return ft.Row(
            controls=[
                self._build_stat_card(
                    ft.Icons.FORMAT_LIST_NUMBERED,
                    "Rutas Totales",
                    str(self.total_routes),
                    ft.Colors.BLUE_700,
                    lambda e: self._navigate_clean("/documents"),
                ),
                self._build_stat_card(
                    ft.Icons.APARTMENT,
                    "Empresas",
                    str(self.company_count),
                    ft.Colors.ORANGE,
                    lambda e: self._navigate_clean("/companies"),
                ),
                self._build_stat_card(
                    ft.Icons.PERSON,
                    "Usuarios",
                    str(self.user_count),
                    ft.Colors.PURPLE,
                    lambda e: self._navigate_clean("/users"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
    
    def _build_stat_card(self, icon, title, value, color, on_click=None):
        
        bgcolor = ft.Colors.SURFACE if self.is_dark_mode else ft.Colors.SURFACE

        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=icon, size=40, color=color),
                        ft.Text(
                            title,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            value,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=10,
                width=110,
                alignment=ft.alignment.center,
                on_click=on_click,
                bgcolor=bgcolor,
                border_radius=10,
                on_hover=lambda e: (
                    setattr(
                        e.control,
                        "bgcolor",
                        ft.Colors.GREY_100 if e.data == "true" else ft.Colors.SURFACE,
                    ),
                    e.control.update(),
                ),
            ),
            elevation=4,
        )

    def _build_fab(self):
        def toggle_menu(e):
            self.menu_visible = not self.menu_visible
            self.page.overlay.clear()
            self.page.overlay.append(self._build_fab_menu())
            self.page.update()

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
            bgcolor=ft.Colors.BLUE_700,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.HOME,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Inicio",
                        on_click=lambda e: self._navigate_clean("/dashboard"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PERSON,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Usuarios",
                        on_click=lambda e: self._navigate_clean("/users"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
        )

    def _update_stats(self):
        self.total_routes = get_document_count_all(self.page.db)
        self.company_count = get_company_count_all(self.page.db)
        self.user_count = get_user_count_all(self.page.db)
        self.page.update()
