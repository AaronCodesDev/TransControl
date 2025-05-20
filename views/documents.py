import flet as ft
from database.models import SessionLocal, Documentos
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

class DocumentsView:
    def __init__(self, page: ft.Page, theme_button):
        self.page = page
        self.theme_button = theme_button
        self.documents = []
        self.filtered_documents = []
        self.search_term = ''
        self.table = None
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(''),
            content=ft.Text(''),
            actions=[]
        )

    def build(self):
        self._load_documents()
        self.table = self._build_documents_list()

        return ft.View(
            route='/documents',
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
                title=ft.Text('Documentos Registrados'),
                center_title=True,
                bgcolor=ft.colors.GREEN_300,
                automatically_imply_leading=False,
                actions=[self.theme_button],
            ),
            bottom_appbar=self._build_bottom_appbar()
        )

    def _load_documents(self):
        db = SessionLocal()
        self.documents = db.query(Documentos).options(
            joinedload(Documentos.contratante),
            joinedload(Documentos.transportista),
            joinedload(Documentos.usuario)
        ).order_by(desc(Documentos.fecha_transporte)).all()
        self.filtered_documents = self.documents
        db.close()

    def _build_documents_list(self):
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(doc.contratante.nombre if doc.contratante else 'sin asignar', size=14, overflow="ellipsis", max_lines=1, no_wrap=True, text_align=ft.TextAlign.CENTER),
                            width=60,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(doc.lugar_origen, size=14, overflow="ellipsis", text_align=ft.TextAlign.CENTER),
                            width=70,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(doc.lugar_destino, size=14, overflow="ellipsis", text_align=ft.TextAlign.CENTER),
                            width=70,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.icons.QR_CODE,
                                        tooltip='Ver QR del documento',
                                        on_click=lambda e, d=doc: self.mostrar_qr(e, d),
                                        icon_size=20,
                                        alignment=ft.alignment.center_left
                                    )
                                ],
                                spacing=5
                            ),
                            width=70
                        )
                    ),
                ]
            )
            for doc in self.filtered_documents
        ]

        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Contratante")),
                            ft.DataColumn(ft.Text("Origen")),
                            ft.DataColumn(ft.Text("Destino")),
                            ft.DataColumn(ft.Text("  QR")),
                        ],
                        rows=rows,
                        column_spacing=20,
                        data_row_max_height=56
                    ),
                    padding=10            
                )       
            ],
            scroll=True,
            expand=True
        )    
    def _build_search_box(self):
        return ft.TextField(
            label='Buscar Contratante',
            hint_text='Nombre del contratante',
            value=self.search_term,
            width=300,
            prefix_icon=ft.icons.SEARCH,
            on_change=self._filter_documents
        )

    def _filter_documents(self, e):
        self.search_term = e.control.value
        term = self.search_term.lower()

        self.filtered_documents = [
            d for d in self.documents
            if term in str(d.empresas_id_contratante).lower()
            or term in d.lugar_origen.lower()
            or term in d.lugar_destino.lower()
            or term in d.nombre.lower()
        ] if term else self.documents

        self.table.rows.clear()
        self.table.rows.extend(self._build_documents_list().rows)
        self.page.update()

    def mostrar_qr(self, e, document):
        print(f"📦 Mostrar QR para documento ID: {document.id}")

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
