import flet as ft
from database.models import SessionLocal, Empresas  # Importa la conexión a la base de datos y el modelo

class CompaniesView:
    def __init__(self, page: ft.Page, theme_button):
        self.page = page
        self.theme_button = theme_button
        self.companies = []  # Lista vacía inicial
        self.filtered_companies = []
        self.search_term = ''
        self.table = None  # 🔥 Referencia al DataTable para actualizarlo dinámicamente

    def build(self):
        self.table = self._build_companies_list()  # 🔥 Guardamos la tabla como atributo

        self.page.views.clear()
        self.page.views.append(
            ft.View(
                '/companies',
                controls=[
                    ft.Column(
                        controls=[
                            self._build_search_box(),
                            self.table,  # 🔥 Reutilizamos el DataTable
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                        scroll=True,
                        expand=True
                    ),
                ],
                appbar=ft.AppBar(
                    title=ft.Text('Empresas Registradas'),
                    center_title=True,
                    bgcolor=ft.colors.GREEN_300,
                    automatically_imply_leading=False,
                    actions=[self.theme_button],
                ),
                bottom_appbar=self._build_bottom_appbar()
            )
        )
        self.page.update()

    def _build_search_box(self):
        return ft.Column(
            controls=[
                ft.TextField(
                    label="Buscar empresa",
                    hint_text="Nombre de la empresa",
                    value=self.search_term,  # 🔥 Mantiene el texto actual
                    width=300,
                    prefix_icon=ft.icons.SEARCH,
                    on_change=self._filter_companies
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )    
    
    def _filter_companies(self, e):
        self.search_term = e.control.value  # 🔥 Guardamos el texto actual
        search_term = self.search_term.lower()
        print(f'Filtrando empresas por: {search_term}')

        if search_term:
            self.filtered_companies = [
                company for company in self.companies
                if search_term in company.nombre.lower()
            ]
        else:
            self.filtered_companies = self.companies

        self._update_companies_list()  # 🔥 Solo actualizamos el contenido de la tabla

    def _build_companies_list(self):
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(company.nombre, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.cif, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.direccion, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.telefono, max_lines=1, overflow='ellipsis')),
                ]
            )
            for company in self.filtered_companies
        ]

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("CIF")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
            ],
            rows=rows,
        )

    def _update_companies_list(self):
        self.table.rows = [  # 🔥 Solo cambiamos el contenido
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(company.nombre, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.cif, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.direccion, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.telefono, max_lines=1, overflow='ellipsis')),
                ]
            )
            for company in self.filtered_companies
        ]
        self.page.update()

    def _on_company_click(self, company):
        print(f"Empresa seleccionada: {company.nombre}")
    
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

    def fetch_companies(self):
        print("Cargando empresas desde la base de datos...")
        session = SessionLocal()
        try:
            self.companies = session.query(Empresas).all()
            print(f"Empresas cargadas: {self.companies}")
            self.filtered_companies = self.companies
            self.build()
        finally:
            session.close()
