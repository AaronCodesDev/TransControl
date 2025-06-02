import flet as ft
from views.login import LoginView
from views.register import RegisterView
from views.dashboard import DashboardView
from views.companies import CompaniesView
from views.documents import DocumentsView
from views.profile import ProfileView
from views.create_company import CreateCompanyView
from views.create_document import CreateDocumentView
from database import SessionLocal, init_db
from views.admin import AdminDashboardView
from views.users import UsersView


def main(page: ft.Page):
    page.title = 'TransControl'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = 'auto'
    

    # Inicializar base de datos
    init_db()
    page.db = SessionLocal()

    # Botón para cambiar tema
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

    # Forzar recarga de una vista si ya estás en la ruta
    def force_route(route):
        if page.route == route:
            route_change(None)
        else:
            page.go(route)

    def route_change(e):
        print(f'📍 Ruta cambiada a: {page.route}')
        page.views.clear()

        if page.route == '/dashboard':
            view = DashboardView(page, theme_button, force_route)
            page.views.append(view.build())

        elif page.route == '/profile':
            view = ProfileView(page, theme_button)
            page.views.append(view.build())

        elif page.route == '/login':
            view = LoginView(page, on_login_success, theme_button, go_to_register)
            page.views.append(view.build())

        elif page.route == '/register':
            view = RegisterView(page, theme_button, go_to_login)
            page.views.append(view.build())

        elif page.route == '/companies':
            view = CompaniesView(page, theme_button, user=page.user)
            page.views.append(view.build())

        elif page.route == '/documents':
            view = DocumentsView(page, theme_button, user=page.user)
            page.views.append(view.build())

        elif page.route == '/create_company':
            view = CreateCompanyView(page, theme_button, force_route, page.user)
            page.views.append(view.build())

        elif page.route == '/create_document':
            view = CreateDocumentView(page, theme_button, force_route)
            page.views.append(view.build())
            
        elif page.route == '/admin':
            view = AdminDashboardView(page, theme_button, force_route)
            page.views.append(view.build())
        
        elif page.route == '/users':
            view = UsersView(page, theme_button, force_route)
            page.views.append(view.build())

        page.update()

    page.on_route_change = route_change

    # Funciones de navegación reutilizables
    def go_to_register():
        print('➡️ Registro')
        force_route("/register")

    def on_login_success(user):
        print(f'✅ Login con: {user}')
        page.user = user
        force_route("/dashboard")

    def go_to_login():
        print('➡️ Login')
        force_route("/login")

    def go_to_dashboard():
        print(f'↩️ Dashboard: {page.user.nombre}')
        force_route("/dashboard")

    def go_to_companies():
        print('➡️ Empresas')
        force_route("/companies")

    def go_to_documents():
        print('➡️ Documentos')
        force_route("/documents")

    # Iniciar en login
    force_route("/login")


if __name__ == '__main__':
    ft.app(target=main, assets_dir="assets")
