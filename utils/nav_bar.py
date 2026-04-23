"""
Barra de navegación inferior compartida.
Uso: build_bottom_nav(page, active_route, ab_color)
"""
import flet as ft

NAV_ITEMS = [
    ("/dashboard", ft.Icons.HOME_ROUNDED),
    ("/documents", ft.Icons.DESCRIPTION_ROUNDED),
    ("/vehicles",  ft.Icons.DIRECTIONS_CAR_ROUNDED),
    ("/stats",     ft.Icons.BAR_CHART_ROUNDED),
    ("/companies", ft.Icons.APARTMENT_ROUNDED),
    ("/profile",   ft.Icons.PERSON_ROUNDED),
]

_NAV_ICONS = {route: icon for route, icon in NAV_ITEMS}


def build_bottom_nav(page: ft.Page, active_route: str, ab_color: str) -> ft.BottomAppBar:
    def nav_item(route, icon_name):
        is_active = route == active_route
        bg = ft.Colors.with_opacity(0.15, ft.Colors.WHITE) if is_active else ft.Colors.TRANSPARENT
        txt_alpha = 1.0 if is_active else 0.5

        return ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=4, horizontal=2),
            border_radius=10,
            bgcolor=bg,
            on_click=lambda e, r=route: page.force_route(r),
            ink=True,
            content=ft.Icon(
                _NAV_ICONS[route],
                size=22,
                color=ft.Colors.with_opacity(txt_alpha, ft.Colors.WHITE),
            ),
        )

    return ft.BottomAppBar(
        bgcolor=ab_color,
        elevation=8,
        height=56,
        content=ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[nav_item(r, i) for r, i in NAV_ITEMS],
        ),
    )
