import flet as ft
from views.login import LoginView
from views.register import RegisterView
from views.dashboard import DashboardView
from views.companies import CompaniesView
from views.documents import DocumentsView
from views.profile import ProfileView
from views.create_company import CreateCompanyView
from database import SessionLocal, init_db


def main(page: ft.Page):
    page.title = 'TransControl'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0  # Eliminamos desplazamiento visual
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = 'auto'

    # Inicialización de la base de datos
    init_db()
    page.db = SessionLocal()

    theme_icon_button = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip='Cambiar tema',
        on_click=lambda e: toggle_theme(e)
    )

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        theme_icon_button.icon = (
            ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
        )
        page.update()

    theme_button = theme_icon_button

    def route_change(e):
        print(f'Ruta cambiada a: {page.route}')
        if page.route == '/dashboard':
            DashboardView(page, theme_button).build()
        elif page.route == '/profile':
            ProfileView(page, theme_button).build()
        elif page.route == '/login':
            LoginView(page, on_login_success, theme_button, go_to_register).build()
        elif page.route == '/register':
            RegisterView(page, theme_button, go_to_login).build()
        elif page.route == '/companies':
            CompaniesView(page, theme_button).build()
        elif page.route == '/documents':
            DocumentsView(page, theme_button).build()
        elif page.route == '/create_company':
            CreateCompanyView(page, theme_button).build()

    page.on_route_change = route_change

    def go_to_register():
        print('Redirigiendo a la vista de registro...')
        page.views.clear()
        RegisterView(page, theme_button, go_to_login).build()
        page.update()

    def on_login_success(user):
        print(f'Login exitoso con usuario: {user}')
        page.user = user
        go_to_dashboard()

    def go_to_login():
        print('Redirigiendo a la vista de login...')
        page.views.clear()
        page.go(page.route)
        LoginView(page, on_login_success, theme_button, go_to_register).build()

    def go_to_dashboard():
        print(f'Redirigiendo al Dashboard de: {page.user.nombre}')
        page.views.clear()
        DashboardView(page, theme_button).build()

    def go_to_companies():
        print('Redirigiendo a la vista de empresas...')
        page.views.clear()
        page.go('/companies')

    def go_to_documents():
        print('Redirigiendo a la vista de documentos...')
        page.views.clear()
        page.go('/documents')

    go_to_login()


if __name__ == '__main__':
    ft.app(target=main, assets_dir="assets")
