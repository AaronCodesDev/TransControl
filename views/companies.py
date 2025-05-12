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
        self._load_companies()
        self.table = self._build_companies_list()

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
        
    def _load_companies(self):
        db = SessionLocal()
        self.companies = db.query(Empresas).all()
        self.filtered_companies = self.companies
        db.close()
        
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

    def _build_search_box(self):
        return ft.TextField(
            label="Buscar empresa",
            hint_text="Nombre de la empresa",
            value=self.search_term,
            width=300,
            prefix_icon=ft.icons.SEARCH,
            on_change=self._filter_companies
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

        # Actualizamos solo las filas
        self._update_companies_list()

    def _update_companies_list(self):
        """ Actualiza la lista de empresas sin reconstruir el DataTable """
        self.table.rows.clear()
        for company in self.filtered_companies:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(company.nombre, max_lines=1, overflow='ellipsis'), on_tap=self._on_company_click, data=company),
                    ft.DataCell(ft.Text(company.cif, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.direccion, max_lines=1, overflow='ellipsis')),
                    ft.DataCell(ft.Text(company.telefono, max_lines=1, overflow='ellipsis')),
                ]
            )
            self.table.rows.append(row)
        self.page.update()

    def _on_company_click(self, e):
        """ Evento al hacer click en una empresa """
        company = e.control.data
        print(f'Visualizando Empresa: {company.nombre}')

        # Modo solo lectura
        form_fields = {
            'nombre': ft.TextField(label="Nombre", value=company.nombre, disabled=True),
            'cif': ft.TextField(label="CIF", value=company.cif, disabled=True),
            'direccion': ft.TextField(label="Dirección", value=company.direccion, disabled=True),
            'telefono': ft.TextField(label="Teléfono", value=company.telefono, disabled=True)
        }

        def edit_mode(e):
            for field in form_fields.values():
                field.disabled = False
            edit_button.visible = False
            save_button.visible = True
            delete_button.visible = True
            self.page.update()

        def save_changes(e):
            print(f'Guardando cambios para: {company.nombre}')
            session = SessionLocal()
            try:
                company.nombre = form_fields['nombre'].value
                company.cif = form_fields['cif'].value
                company.direccion = form_fields['direccion'].value
                company.telefono = form_fields['telefono'].value
                session.commit()
                print('Datos actualizados correctamente')
                self.dialog.open = False
                self._update_companies_list()
            except Exception as ex:
                print(f'Error al actualizar: {ex}')
                session.rollback()
            finally:
                session.close()
            self.page.update()
            
        def close_dialog(e):
            self.dialog.open = False
            self.page.update()
        
        def delete_company(e, company_id):
            session = SessionLocal()
            try:
                company = session.query(Empresas).filter(Empresas.id == company_id).first()
                if company:
                    session.delete(company)
                    session.commit()
                    print(f'Empresa {company.nombre} eliminada correctamente')
                    
                    self._load_companies()
                    self._update_companies_list()
                    self.dialog.open = False
                else:
                    print(f'Empresa con ID {company_id} no encontrada.')
            except Exception as ex:
                print(f'Error al eliminar: {ex}')
                session.rollback()
            finally:
                session.close()
            self.page.update()

        # Botones centrados
        edit_button = ft.IconButton(icon=ft.icons.EDIT, tooltip='Editar', on_click=edit_mode)
        save_button = ft.IconButton(icon=ft.icons.SAVE, tooltip='Guardar', on_click=save_changes, visible=False)
        delete_button = ft.IconButton(icon=ft.icons.DELETE, tooltip='Eliminar', on_click=lambda e: delete_company(e, company.id))
        close_button = ft.IconButton(icon=ft.icons.CLOSE, tooltip='Cerrar', on_click=close_dialog)

        self.dialog.title.value = f'Información de {company.nombre}'
        self.dialog.content = ft.Column(list(form_fields.values()), tight=True)
        self.dialog.actions = [
            ft.Row(
                controls=[edit_button, save_button, delete_button, close_button],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ]

        self.page.dialog = self.dialog
        self.dialog.open = True
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
