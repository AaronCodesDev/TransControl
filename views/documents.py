import flet as ft
from database.models import SessionLocal, Documentos
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

class DocumentsView:
    def __init__(self, page: ft.Page, theme_button, user=None):
        self.user = user
        self.page = page
        self.theme_button = theme_button
        self.documents = []
        self.filtered_documents = []
        self.search_term = ''
        self.table = ft.Column()
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(''),
            content=ft.Text(''),
            actions=[]
        )

    def build(self):
        self._load_documents()

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
        self.table.controls.append(self._build_documents_list())

        return ft.View(
            route='/documents',
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
                        scroll=True,
                        expand=True
                    ),
                    alignment=ft.alignment.top_center,
                    padding=ft.padding.only(top=40),
                    expand=True
                )
            ],
            appbar=ft.AppBar(
                title=ft.Text('Documentos Registrados'),
                center_title=True,
                bgcolor=ft.Colors.GREEN_300,
                automatically_imply_leading=False,
                actions=actions,
            ),
            bottom_appbar=self._build_bottom_appbar()
        )

    def _load_documents(self):
        db = SessionLocal()
        try:
            self.documents = db.query(Documentos).options(
                joinedload(Documentos.contratante),
                joinedload(Documentos.transportista),
                joinedload(Documentos.usuario)
            ).order_by(desc(Documentos.fecha_transporte)).all()
            self.filtered_documents = self.documents
        finally:
            db.close()

    def _build_documents_list(self):
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                doc.usuario.email if doc.usuario else 'Desconocido',
                                size=14,
                                overflow="ellipsis",
                                max_lines=1,
                                no_wrap=True,
                                text_align=ft.TextAlign.CENTER
                            ),
                            width=180,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                doc.contratante.nombre if doc.contratante else 'Sin asignar',
                                size=14,
                                overflow="ellipsis",
                                max_lines=1,
                                no_wrap=True,
                                text_align=ft.TextAlign.CENTER
                            ),
                            width=150,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                doc.lugar_origen,
                                size=14,
                                overflow="ellipsis",
                                text_align=ft.TextAlign.CENTER
                            ),
                            width=150,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                doc.lugar_destino,
                                size=14,
                                overflow="ellipsis",
                                text_align=ft.TextAlign.CENTER
                            ),
                            width=150,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(
                                        text="Ver QR",
                                        icon=ft.Icons.QR_CODE,
                                        on_click=lambda e, doc=doc: self.page.go(f'/qr/{doc.id}')
                                    ),
                                    ft.PopupMenuItem(
                                        text='Ver Documento' if doc.archivo else 'Documento no disponible',
                                        icon=ft.Icons.CONTENT_PASTE_SEARCH,
                                        on_click=(lambda e, d=doc: self.page.go(f'/output_pdf/{d.id}')) if doc.archivo else None
                                    ),
                                    ft.PopupMenuItem(
                                        text="Eliminar Documento",
                                        icon=ft.Icons.DELETE,
                                        on_click=lambda e, doc=doc: self._delete_document(doc)
                                    )
                                ],
                                icon=ft.Icons.MORE_VERT
                            ),
                            alignment=ft.alignment.center
                        )
                    ),
                ]
            )
            for doc in self.filtered_documents
        ]

        columns = [
            ft.DataColumn(ft.Text("Creador")),
            ft.DataColumn(ft.Text("Contratante")),
            ft.DataColumn(ft.Text("Origen")),
            ft.DataColumn(ft.Text("Destino")),
            ft.DataColumn(ft.Text("Acciones")),
        ]

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
            label="Buscar documento",
            hint_text="Buscar por contratante o lugar",
            value=self.search_term,
            width=300,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._filter_documents
        )

    def _filter_documents(self, e):
        self.search_term = e.control.value
        search_term = self.search_term.lower()
        self.filtered_documents = [
            d for d in self.documents if
            search_term in (d.contratante.nombre.lower() if d.contratante else '') or
            search_term in d.lugar_origen.lower() or
            search_term in d.lugar_destino.lower()
        ] if search_term else self.documents

        self.table.controls.clear()
        self.table.controls.append(self._build_documents_list())
        self.page.update()

    def _delete_document(self, doc):
        session = SessionLocal()
        try:
            document = session.query(Documentos).filter(Documentos.id == doc.id).first()
            if document:
                session.delete(document)
                session.commit()
                print(f'Documento {doc.id} eliminado correctamente')
                self._load_documents()
                self.table.controls.clear()
                self.table.controls.append(self._build_documents_list())
            else:
                print(f'Documento con ID {doc.id} no encontrado.')
        except Exception as ex:
            print(f'Error al eliminar documento: {ex}')
            session.rollback()
        finally:
            session.close()
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
