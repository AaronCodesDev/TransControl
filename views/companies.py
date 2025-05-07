import flet as ft
from database.models import SessionLocal, Empresas

class CompaniesView:
    def __init__(self, page: ft.Page, theme_button):
        self.page = page
        self.theme_button = theme_button
        self.companies = []
        self.filtered_companies = []
        self.search_term = ''
        self.table = None
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(''),
            content=ft.Text(''),
            actions=[]
        )

    def build(self):
        if not self.table:
            self.table = self._build_companies_list()
            
        self._update_companies_list()

        self.page.views.clear()
        self.page.views.append(
            ft.View(
                '/companies',
                controls=[
                    ft.Column(
                        controls=[
                            self._build_search_box(),
                            self.table,
                            self.dialog
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
                    value=self.search_term,
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
        self.search_term = e.control.value
        search_term = self.search_term.lower()
        print(f'Filtrando empresas por: {search_term}')

        if search_term:
            self.filtered_companies = [
                company for company in self.companies
                if search_term in company.nombre.lower()
            ]
        else:
            self.filtered_companies = self.companies

        self._update_companies_list()

    def _build_companies_list(self):
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(company.nombre, max_lines=1, overflow='ellipsis'), on_tap=self._on_company_click, data=company),
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
        print('Actualizando lista de empresas...')
        if self.table is None:
            self.table = self._build_companies_list()
        
        
        self.table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(company.nombre, max_lines=1, overflow='ellipsis'), on_tap=self._on_company_click, data=company),
                    ft.DataCell(ft.Text(company.cif, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.direccion, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.telefono, max_lines=1, overflow='ellipsis')),
                ]
            )
            for company in self.filtered_companies
        ]
        
        if self.table not in self.page.controls:
            self.page.controls.append(self.table)
            
        self.page.update()

    def _on_company_click(self, e):
        
        company = e.control.data
        print(f'Editando Empresa: {company.nombre}')
        session = SessionLocal()
        company = session.query(Empresas).filter(Empresas.id == company.id).first()
        
        if not company:
            print('Empresa no encontrada')
            session.close()
            return
        
        # Form Editar datos
        nombre = ft.TextField(label='Nombre', value=company.nombre)
        cif = ft.TextField(label='Cif', value=company.cif)
        direccion = ft.TextField(label='Dirección', value=company.direccion)
        ciudad = ft.TextField(label='Ciudad', value=company.ciudad)
        provincia = ft.TextField(label='Provincia', value=company.provincia)
        codigo = ft.TextField(label='Código postal', value=company.codigo_postal)
        email = ft.TextField(label='Email', value=company.email)
        telefono = ft.TextField(label='Teléfono', value=company.telefono)
        
        def edit_company(e):
            print(f'Actualizando datos empresa: {company.nombre}')
            try:
                company.nombre = nombre.value
                company.cif = cif.value
                company.direccion = direccion.value
                company.ciudad = ciudad.value
                company.provincia = provincia.value
                company.codigo_postal = codigo.value
                company.email = email.value
                company.telefono = telefono.value
            
                session.commit()
                print('Datos actualizados')
                
                self.dialog.open = False
                self.page.update()
                self.fetch_companies()
            except Exception as ex:
                print(f'Error al actualizar: {ex}')
                session.rollback()
            finally:
                session.close()    
            
        def delete_company(e):
            print(f'Eliminando empresa: {company.nombre}')
            try:
                session.delete(company)
                session.commit()
                print('Empresa eliminada')
                
                self.dialog.open = False
                self.page.update()
                self.fetch_companies()
            except Exception as ex:
                print(f'Error al eliminar: {ex}')
                session.rollback()
            finally:
                session.close()
                            
        def close(e):
            self.dialog.open = False
            self.page.update()
            
        self.dialog.title = ft.Text(f'Editar {company.nombre}')
        self.dialog.content = ft.Column([
            nombre,
            cif,
            direccion,
            ciudad,
            provincia,
            codigo,
            email,
            telefono
        ],
        tight=True)
        
        self.dialog.actions = [
            ft.TextButton('Guardar Cambios', on_click=edit_company),
            ft.TextButton('Eliminar', on_click=delete_company),
            ft.TextButton('Cerrar', on_click=close)
        ]
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

        print(f"Empresa seleccionada: {company.nombre}")

    def _close_dialog(self):
        self.dialog.open = False
        self.page.update()

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
