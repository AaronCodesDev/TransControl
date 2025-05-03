import flet as ft
from flet import Icons
from views.login import LoginView
from views.register import RegisterView
from views.dashboard import DashboardView
from views.companies import CompaniesView
from database import SessionLocal, init_db
from database.models import Usuario
from views.profile import ProfileView

def main(page: ft.Page):
    # Configuración inicial de la página
    page.title = 'TransControl'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Inicialización de la base de datos
    init_db()
    page.db = SessionLocal()  # Sesión accesible desde cualquier vista

    theme_icon_button = ft.IconButton(
        icon=Icons.DARK_MODE,
        tooltip='Cambiar tema',
        on_click=lambda e: toggle_theme(e)  # usamos lambda para pasar el evento
    )

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        theme_icon_button.icon = (
            Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else Icons.LIGHT_MODE
        )
        page.update()

    # Este es el botón que se pasa a las vistas
    theme_button = theme_icon_button

    # SISTEMA DE RUTAS
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
            
    page.on_route_change = route_change

    # Navegación
    def go_to_register():
        print("Redirigiendo a la vista de registro...")
        page.views.clear()
        RegisterView(page, theme_button, go_to_login).build()
        page.update()

    def on_login_success(user):
        print(f'Login exitoso con usuario: {user}')
        page.user = user
        go_to_dashboard()

    def go_to_login():
        print("Redirigiendo a la vista de login...")
        page.views.clear()
        page.go(page.route)
        LoginView(page, on_login_success, theme_button, go_to_register).build()

    def go_to_dashboard():
        print(f'Redirigiendo al Dashboard de: {page.user.nombre}')
        page.views.clear()
        DashboardView(page, theme_button).build()
        
    def go_to_companies():
        print("Redirigiendo a la vista de empresas...")
        page.views.clear()
        page.go(page.route)
        CompaniesView(page, theme_button).build()

    # Comenzar mostrando la pantalla de login
    go_to_login()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
