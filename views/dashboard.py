import flet as ft
from datetime import date, datetime
from database.models import Documentos, Empresas, Usuario
from database.crud import get_document_count, get_daily_routes, get_company_count
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class DashboardView:
    def __init__(self, page: ft.Page, theme_button):
        self.page = page
        self.theme_button = theme_button
        self.user = page.user
        self.menu_visible = False

        self.total_routes = get_document_count(self.page.db)
        self.daily_routes = len(get_daily_routes(self.page.db, date.today()))
        self.company_count = get_company_count(self.page.db)

        self.welcome_card = self._build_welcome_card()
        self.stats_row = self._build_stats_row()

    def build(self):
        self.page.views.clear()
        self.page.overlay.clear()
        self.page.views.append(self._build_loading_view())
        self.page.overlay.append(self._build_fab_menu())
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
                    bgcolor=ft.Colors.GREEN_300,
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
                                on_click=lambda e: (self.page.overlay.clear(), self.page.go('/create_document')),
                                width=64,
                                height=64
                            ),
                            ft.FloatingActionButton(
                                icon=ft.Icons.APARTMENT,
                                tooltip='Nueva empresa',
                                on_click=lambda e: (self.page.overlay.clear(), self.page.go('/create_company')),
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

    def _build_bottom_appbar(self):
        return ft.BottomAppBar(
            bgcolor=ft.Colors.GREEN_300,
            shape=ft.NotchShape.CIRCULAR,
            elevation=8,
            content=ft.Row(
                controls=[
                    ft.IconButton(icon=ft.Icons.HOME, icon_color=ft.Colors.WHITE, tooltip="Inicio", on_click=lambda e: self.page.go('/dashboard')),
                    ft.IconButton(icon=ft.Icons.FORMAT_LIST_NUMBERED, icon_color=ft.Colors.WHITE, tooltip="Documentos", on_click=lambda e: self.page.go('/documents')),
                    ft.IconButton(icon=ft.Icons.APARTMENT, icon_color=ft.Colors.WHITE, tooltip="Empresas", on_click=lambda e: self.page.go('/companies')),
                    ft.IconButton(icon=ft.Icons.PERSON, icon_color=ft.Colors.WHITE, tooltip="Perfil", on_click=lambda e: self.page.go('/profile')),
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
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Crear nuevo documento"),
            content=ft.Text("¿Deseas crear un nuevo documento?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda ev: self._close_dialog()),
                ft.ElevatedButton("Confirmar", on_click=lambda ev: self._close_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()

    def _show_create_company_dialog(self, e):
        print("🟢 Abriendo diálogo para nueva empresa...")  # Depuración
        nombre_input = ft.TextField(label='Nombre de la empresa')
        direccion_input = ft.TextField(label='Dirección')
        codigo_postal_input = ft.TextField(label='Código postal')
        ciudad_input = ft.TextField(label='Ciudad')
        provincia_input = ft.TextField(label='Provincia')
        cif_input = ft.TextField(label='CIF')
        telefono_input = ft.TextField(label='Teléfono')
        fecha_creacion = date.today()

        def save_company(ev):
            try:
                engine = create_engine('sqlite:///database/transcontrol.db')
                Session = sessionmaker(bind=engine)
                session = Session()

                new_company = Empresas(
                    nombre=nombre_input.value.strip(),
                    direccion=direccion_input.value.strip(),
                    codigo_postal=codigo_postal_input.value.strip(),
                    ciudad=ciudad_input.value.strip(),
                    provincia=provincia_input.value.strip(),
                    cif=cif_input.value.strip(),
                    telefono=telefono_input.value.strip(),
                    fecha_creacion=fecha_creacion
                )

                session.add(new_company)
                session.commit()
                print('✅ Empresa guardada:', new_company.nombre)

            except Exception as err:
                print("❌ Error al guardar empresa:", err)

            finally:
                session.close()
                self._close_dialog()
                self._hide_menu()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text('Registrar nueva empresa'),
            content=ft.Column([
                nombre_input,
                direccion_input,
                codigo_postal_input,
                ciudad_input,
                provincia_input,
                cif_input,
                telefono_input,
                ft.Text(f"Fecha de creación: {fecha_creacion.strftime('%d/%m/%Y')}")
            ], tight=True),
            actions=[
                ft.TextButton('Cancelar', on_click=lambda e: self._close_dialog()),
                ft.ElevatedButton('Guardar', on_click=save_company),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()


    def _close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _build_loading_view(self):
        return ft.View(
            '/loading',
            controls=[
                ft.Column(
                    [
                        ft.ProgressRing(width=50, height=50, stroke_width=6, color=ft.Colors.GREEN),
                        ft.Text("Cargando Dashboard...", size=20),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
        )