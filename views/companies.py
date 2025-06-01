import flet as ft
from database.models import SessionLocal, Empresas

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

        # Configuración del botón de administración si el usuario es admin
        admin_button = None
        if self.user and getattr(self.user, 'rol', '') == 'admin':
            admin_button = ft.IconButton(
                icon=ft.Icons.SECURITY,
                icon_color=ft.Colors.WHITE,
                tooltip='Panel de administración',
                on_click=lambda e: self.page.go('/admin'),
            )
        if admin_button:
            actions = [admin_button, self.theme_button]
        else:
            actions = [self.theme_button]

        self.table.controls.clear()
        self.table.controls.append(self._build_companies_list())

        return ft.View(
            route='/companies',
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
                )
            ],
            appbar=ft.AppBar(
                title=ft.Text('Empresas Registradas'),
                center_title=True,
                bgcolor=ft.colors.GREEN_300,
                automatically_imply_leading=False,
                actions=actions,
            ),
            bottom_appbar=self._build_bottom_appbar()
        )
        
    def _load_companies(self):
        db = SessionLocal()
        if self.user and hasattr(self.user, 'id'):
            self.companies = db.query(Empresas).filter(Empresas.usuario_id == self.user.id).all()
        else:
            self.companies = []
        self.filtered_companies = self.companies
        db.close()

    def _build_companies_list(self):
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                c.nombre,
                                size=14,
                                overflow="ellipsis",
                                max_lines=1,
                                no_wrap=True,
                            ),
                            width=200,
                            alignment=ft.alignment.center_left,
                            on_click=lambda e, c=c: self._on_company_click(e, c),
                            data=c
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                c.cif,
                                size=14,
                                overflow="ellipsis",
                                max_lines=1
                            ),
                            width=150,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                c.direccion,
                                size=14,
                                overflow="ellipsis",
                                max_lines=1
                            ),
                            width=250,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                c.telefono,
                                size=14,
                                overflow="ellipsis",
                                max_lines=1
                            ),
                            width=150,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                c.email,
                                size=14,
                                overflow="ellipsis",
                                max_lines=1
                            ),
                            width=150,
                            alignment=ft.alignment.center_left
                        )
                    ),
                ]
            )
            for c in self.filtered_companies
        ]

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text('Nombre')),
                            ft.DataColumn(ft.Text('CIF')),
                            ft.DataColumn(ft.Text('Dirección')),
                            ft.DataColumn(ft.Text('Teléfono')),
                            ft.DataColumn(ft.Text('Email')),
                        ],
                        rows=rows,
                        column_spacing=20,
                        data_row_max_height=56,
                        horizontal_margin=10
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
            prefix_icon=ft.icons.SEARCH,
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
                c.nombre = fields['nombre'].value
                c.cif = fields['cif'].value
                c.direccion = fields['direccion'].value
                c.telefono = fields['telefono'].value
                c.email = fields['email'].value if hasattr(c, 'email') else None
                session.commit()
                print('Datos actualizados correctamente')
                self.dialog.open = False
                self._load_companies()
                self.table.controls.clear()
                self.table.controls.append(self._build_companies_list())
                self.page.update()
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
                    self.page.update()
                    self.dialog.open = False
                else:
                    print(f'Empresa con ID {company_id} no encontrada.')
            except Exception as ex:
                print(f'Error al eliminar: {ex}')
                session.rollback()
            finally:
                session.close()
            self.page.update()

        edit_button = ft.IconButton(icon=ft.icons.EDIT, tooltip='Editar', on_click=edit_mode)
        save_button = ft.IconButton(icon=ft.icons.SAVE, tooltip='Guardar', on_click=save_changes, visible=False)
        delete_button = ft.IconButton(icon=ft.icons.DELETE, tooltip='Eliminar', on_click=lambda e: delete_company(e, c.id))
        close_button = ft.IconButton(icon=ft.icons.CLOSE, tooltip='Cerrar', on_click=close_dialog)

        self.dialog.title.value = f'Información de {c.nombre}'
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
