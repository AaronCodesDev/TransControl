import flet as ft
from datetime import date, datetime
from database.crud import get_document_count_all, get_daily_routes, get_company_count_all, get_user_count_all


class AdminDashboardView:
    def __init__(self, page: ft.Page, theme_button, force_route):
        self.page = page
        self.theme_button = theme_button
        self.force_route = force_route
        self.user = page.user
        self.menu_visible = False

        self.is_dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        self.page.on_theme_change = self._on_theme_change

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

        actions = [self.theme_button]

        return ft.View(
            route="/admin",
            controls=[
                ft.Column(
                    controls=[
                        ft.Container(
                            content=self.welcome_card,
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=30),
                        ),
                        ft.Container(height=10),
                        self.stats_row,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            appbar=ft.AppBar(
                title=ft.Text(
                    "Panel de Administración",
                    weight=ft.FontWeight.W_600,
                ),
                center_title=True,
                bgcolor=ft.Colors.BLUE_800,
                automatically_imply_leading=False,
                actions=actions,
                toolbar_height=56,
            ),
            bottom_appbar=self._build_bottom_appbar(),
            bgcolor=ft.Colors.SURFACE,
        )

    def _build_welcome_card(self):
        initials = (self.user.nombre[0] + self.user.apellido[0]).upper() if self.user.nombre and self.user.apellido else "AD"

        avatar = ft.Container(
            width=56,
            height=56,
            border_radius=28,
            bgcolor=ft.Colors.BLUE_700,
            content=ft.Text(
                initials,
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.alignment.center,
        )

        return ft.Container(
            width=360,
            padding=ft.padding.symmetric(horizontal=28, vertical=24),
            border_radius=20,
            bgcolor=ft.Colors.SURFACE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK),
                offset=ft.Offset(0, 6),
            ),
            content=ft.Row(
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    avatar,
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(
                                f'Hola, {self.user.nombre}!',
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                self.user.email,
                                size=13,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "Administrador",
                                    size=11,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=ft.Colors.BLUE_700,
                                padding=ft.padding.symmetric(horizontal=10, vertical=3),
                                border_radius=20,
                            ),
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text(
                                datetime.now().strftime('%d/%m/%Y'),
                                size=12,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        expand=True,
                    ),
                ],
            ),
        )

    def _build_stats_row(self):
        return ft.Row(
            controls=[
                self._build_stat_card(
                    ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED,
                    "Rutas\nTotales",
                    str(self.total_routes),
                    ft.Colors.BLUE_700,
                    ft.Colors.with_opacity(0.10, ft.Colors.BLUE_700),
                    lambda e: self._navigate_clean("/documents"),
                ),
                self._build_stat_card(
                    ft.Icons.APARTMENT_ROUNDED,
                    "Empresas",
                    str(self.company_count),
                    ft.Colors.ORANGE_700,
                    ft.Colors.with_opacity(0.10, ft.Colors.ORANGE_700),
                    lambda e: self._navigate_clean("/companies"),
                ),
                self._build_stat_card(
                    ft.Icons.PERSON_ROUNDED,
                    "Usuarios",
                    str(self.user_count),
                    ft.Colors.PURPLE_700,
                    ft.Colors.with_opacity(0.10, ft.Colors.PURPLE_700),
                    lambda e: self._navigate_clean("/users"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )

    def _build_stat_card(self, icon, title, value, color, bg, on_click=None):
        return ft.Container(
            width=108,
            height=130,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=14,
                color=ft.Colors.with_opacity(0.09, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            on_click=on_click,
            ink=True,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Container(
                        width=44,
                        height=44,
                        border_radius=22,
                        bgcolor=bg,
                        content=ft.Icon(name=icon, size=24, color=color),
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(
                        value,
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        title,
                        size=11,
                        weight=ft.FontWeight.W_500,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_600,
                    ),
                ],
            ),
        )

    def _build_fab(self):
        return ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=ft.Colors.BLUE_700,
            shape=ft.CircleBorder(),
            tooltip="Opciones rápidas",
            width=60,
            height=60,
            on_click=lambda e: None,
        )

    def _navigate_clean(self, route):
        self.menu_visible = False
        self.page.overlay.clear()
        self.page.go(route)

    def _build_bottom_appbar(self):
        return ft.BottomAppBar(
            bgcolor=ft.Colors.BLUE_800,
            elevation=8,
            content=ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.HOME_ROUNDED,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Dashboard usuario",
                        on_click=lambda e: self._navigate_clean("/dashboard"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Documentos",
                        on_click=lambda e: self._navigate_clean("/documents"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.APARTMENT_ROUNDED,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Empresas",
                        on_click=lambda e: self._navigate_clean("/companies"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PERSON_ROUNDED,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Usuarios",
                        on_click=lambda e: self._navigate_clean("/users"),
                    ),
                ],
            ),
        )

    def _update_stats(self):
        self.total_routes = get_document_count_all(self.page.db)
        self.company_count = get_company_count_all(self.page.db)
        self.user_count = get_user_count_all(self.page.db)
        self.page.update()
