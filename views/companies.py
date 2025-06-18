import flet as ft
from database.models import Empresas
from database.db import SessionLocal
from sqlalchemy.orm import joinedload

class CompaniesView:
    def __init__(self, page: ft.Page, theme_button, user=None):
        self.page = page
        self.theme_button = theme_button
        self.user = user
        self.companies = []
        self.filtered_companies = []
        self.search_term = ''
        self.table = ft.Column()
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(''),
            content=ft.Text(''),
            actions=[]
        )

    def build(self):
        self.page.overlay.clear()
        self._load_companies()

        admin_button = None
        if self.user and getattr(self.user, 'rol', '') == 'admin':
            admin_button = ft.IconButton(
                icon=ft.Icons.SECURITY,
                icon_color=ft.Colors.WHITE,
                tooltip='Panel de administración',
                on_click=lambda e: self.page.go('/admin'),
            )

        actions = [self.theme_button]
        if admin_button:
            actions.insert(0, admin_button)

        self.table.controls.clear()
        self.table.controls.append(self._build_companies_list())

        return ft.View(
            route='/companies',
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self._build_search_box(),
                            self.table,
                            self.dialog
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.alignment.top_center,
                    padding=ft.padding.only(top=40),
                    expand=True
                )
            ],
            appbar=ft.AppBar(
                title=ft.Text('Empresas Registradas'),
                center_title=True,
                bgcolor=ft.Colors.GREEN_700,
                automatically_imply_leading=False,
                actions=actions,
            ),
            bottom_appbar=self._build_bottom_appbar()
        )

    def _load_companies(self):
        db = SessionLocal()
        try:
            query = db.query(Empresas).options(joinedload(Empresas.usuario))
            if self.user and getattr(self.user, 'rol', '') == 'admin':
                self.companies = query.all()
            elif self.user and hasattr(self.user, 'id'):
                self.companies = query.filter(Empresas.usuario_id == self.user.id).all()
            else:
                self.companies = []
            self.filtered_companies = self.companies
        finally:
            db.close()

    def _build_companies_list(self):
        columns = [
            ft.DataColumn(ft.Text('Nombre')),
            ft.DataColumn(ft.Text('CIF')),
            ft.DataColumn(ft.Text('Dirección')),
            ft.DataColumn(ft.Text('Teléfono')),
            ft.DataColumn(ft.Text('Email')),
        ]
        if self.user and getattr(self.user, 'rol', '') == 'admin':
            columns.insert(0, ft.DataColumn(ft.Text('Creado por')))

        rows = []
        for c in self.filtered_companies:
            cells = []
            if self.user and getattr(self.user, 'rol', '') == 'admin':
                cells.append(ft.DataCell(ft.Text(c.usuario.email if c.usuario else 'Desconocido')))

            cells.extend([
                ft.DataCell(ft.Text(c.nombre), on_tap=lambda e, c=c: self._on_company_click(e, c)),
                ft.DataCell(ft.Text(c.cif)),
                ft.DataCell(ft.Text(c.direccion)),
                ft.DataCell(ft.Text(c.telefono)),
                ft.DataCell(ft.Text(c.email)),
            ])
            rows.append(ft.DataRow(cells=cells))

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.DataTable(
                        columns=columns,
                        rows=rows,
                        column_spacing=20,
                        data_row_max_height=56,
                        horizontal_margin=10,
                    )
                ],
                scroll="auto"
            ),
            padding=10
        )

    def _build_search_box(self):
        return ft.TextField(
            label="Buscar empresa",
            hint_text="Nombre de la empresa",
            value=self.search_term,
            width=300,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._filter_companies
        )

    def _filter_companies(self, e):
        self.search_term = e.control.value
        search_term = self.search_term.lower()
        self.filtered_companies = [
            c for c in self.companies if search_term in c.nombre.lower()
        ] if search_term else self.companies

        self.table.controls.clear()
        self.table.controls.append(self._build_companies_list())
        self.page.update()

    def _on_company_click(self, e, c):
        print(f'Visualizando Empresa: {c.nombre}')

        fields = {
            'nombre': ft.TextField(label="Nombre", value=c.nombre, disabled=True),
            'cif': ft.TextField(label="CIF", value=c.cif, disabled=True),
            'direccion': ft.TextField(label="Dirección", value=c.direccion, disabled=True),
            'telefono': ft.TextField(label="Teléfono", value=c.telefono, disabled=True),
            'email': ft.TextField(label="Email", value=c.email if hasattr(c, 'email') else '', disabled=True)
        }

        def edit_mode(e):
            for f in fields.values():
                f.disabled = False
            edit_button.visible = False
            save_button.visible = True
            delete_button.visible = True
            self.page.update()

        def save_changes(e):
            print(f'Guardando cambios para: {c.nombre}')
            session = SessionLocal()
            try:
                db_company = session.query(Empresas).filter(Empresas.id == c.id).first()
                if db_company:
                    db_company.nombre = fields['nombre'].value
                    db_company.cif = fields['cif'].value
                    db_company.direccion = fields['direccion'].value
                    db_company.telefono = fields['telefono'].value
                    db_company.email = fields['email'].value
                    session.commit()
                    print('Datos actualizados correctamente')
                self.dialog.open = False
                self._load_companies()
                self.table.controls.clear()
                self.table.controls.append(self._build_companies_list())
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
                    self.table.controls.clear()
                    self.table.controls.append(self._build_companies_list())
                    self.dialog.open = False
                else:
                    print(f'Empresa con ID {company_id} no encontrada.')
            except Exception as ex:
                print(f'Error al eliminar: {ex}')
                session.rollback()
            finally:
                session.close()
            self.page.update()

        edit_button = ft.IconButton(icon=ft.Icons.EDIT, tooltip='Editar', on_click=edit_mode)
        save_button = ft.IconButton(icon=ft.Icons.SAVE, tooltip='Guardar', on_click=save_changes, visible=False)
        delete_button = ft.IconButton(icon=ft.Icons.DELETE, tooltip='Eliminar', on_click=lambda e: delete_company(e, c.id))
        close_button = ft.IconButton(icon=ft.Icons.CLOSE, tooltip='Cerrar', on_click=close_dialog)

        self.dialog.title = ft.Text(f'Información de {c.nombre}')
        self.dialog.content = ft.Column(list(fields.values()), tight=True)
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
            bgcolor=ft.Colors.GREEN_700,
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
