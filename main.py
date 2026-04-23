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
from views.output_pdf import OutputPDFView
from utils.doc_server import start_doc_server
from views.vehicles import VehiclesView
from utils.theme_manager import load_theme_id, save_theme_id, get_theme, THEMES


def main(page: ft.Page):
    page.title = 'TransControl'
    page.padding = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = 'auto'
    page.assets_dir = "assets"

    # ── Aplicar tema guardado ────────────────────────────
    def apply_theme(theme_id: int, _reload: bool = True):
        t = get_theme(theme_id)
        save_theme_id(theme_id)
        page.theme_mode = ft.ThemeMode.DARK if t["mode"] == "dark" else ft.ThemeMode.LIGHT
        page.theme = ft.Theme(
            color_scheme_seed=t["seed"],
            use_material3=True,
            visual_density=ft.VisualDensity.COMFORTABLE,
        )
        page.dark_theme = ft.Theme(
            color_scheme_seed=t["seed"],
            use_material3=True,
            visual_density=ft.VisualDensity.COMFORTABLE,
        )
        page.bgcolor = t["bg"]
        page.tc_theme = t           # disponible globalmente en page
        page.update()
        # Recargar vista actual para que los colores se apliquen
        if _reload:
            route_change(None)

    # Al arrancar, _reload=False porque route_change aún no está definida
    apply_theme(load_theme_id(), _reload=False)
    page.apply_theme = apply_theme  # exponer para usarlo desde las vistas

    # ── Base de datos ────────────────────────────────────
    init_db()
    page.db = SessionLocal()

    # ── Servidor PDF ─────────────────────────────────────
    start_doc_server(docs_dir="assets/docs", port=8765)

    # ── Botón tema (Día ↔ Noche) ─────────────────────────
    def _is_night():
        return getattr(page, 'tc_theme', {}).get('mode', 'dark') == 'dark'

    theme_icon_button = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if _is_night() else ft.Icons.DARK_MODE,
        icon_color=ft.Colors.WHITE,
        tooltip='Día / Noche',
        on_click=lambda e: toggle_light_dark(e),
    )

    def toggle_light_dark(e):
        current_id = getattr(page, 'tc_theme', {}).get('id', 1)
        new_id = 0 if current_id == 1 else 1          # alterna Noche(1) ↔ Día(0)
        apply_theme(new_id)
        theme_icon_button.icon = ft.Icons.LIGHT_MODE if new_id == 1 else ft.Icons.DARK_MODE
        page.update()

    theme_button = theme_icon_button

    # ── Navegación ───────────────────────────────────────
    def force_route(route):
        if page.route == route:
            route_change(None)
        else:
            page.go(route)

    def route_change(e):
        route = page.route or '/login'
        print(f'📍 {route}')
        page.views.clear()

        if route == '/dashboard':
            page.views.append(DashboardView(page, theme_button, force_route).build())
        elif route == '/profile':
            page.views.append(ProfileView(page, theme_button).build())
        elif route == '/login':
            page.views.append(LoginView(page, on_login_success, theme_button, go_to_register).build())
        elif route == '/register':
            page.views.append(RegisterView(page, theme_button, go_to_login).build())
        elif route == '/companies':
            page.views.append(CompaniesView(page, theme_button, user=page.user).build())
        elif route == '/documents':
            page.views.append(DocumentsView(page, theme_button, user=page.user).build())
        elif route == '/create_company':
            page.views.append(CreateCompanyView(page, theme_button, force_route, page.user).build())
        elif route == '/create_document':
            page.views.append(CreateDocumentView(page, theme_button, force_route, page.user).build())
        elif route == '/admin':
            page.views.append(AdminDashboardView(page, theme_button, force_route).build())
        elif route == '/users':
            page.views.append(UsersView(page, theme_button, user=page.user).build())
        elif route == '/vehicles':
            page.views.append(VehiclesView(page, theme_button, user=page.user).build())
        elif route.startswith('/output_pdf/'):
            try:
                doc_id = int(route.split('/')[-1])
                page.views.append(OutputPDFView(page, theme_button, doc_id).build())
            except ValueError:
                page.views.append(ft.View(route=route, controls=[ft.Text("Documento no encontrado.")]))

        page.update()

    page.on_route_change = route_change

    def go_to_register():
        force_route("/register")

    def on_login_success(user):
        print(f'✅ Login: {user.email}')
        page.user = user
        force_route("/dashboard")

    def go_to_login():
        force_route("/login")

    force_route("/login")


if __name__ == '__main__':
    ft.app(target=main, assets_dir='assets')
