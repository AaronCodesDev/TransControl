import flet as ft
from datetime import date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Documentos, Empresas, Usuario
import asyncio

class CreateDocumentView:
    def __init__(self, page, theme_button, force_route):
        self.page = page
        self.theme_button = theme_button
        self.force_route = force_route

    def build(self):
        self._load_empresas()
        self.empresas_dropdown = ft.Dropdown(label='Selecciona Empresa Contratante', options=[ft.dropdown.Option(str(e.id), e.nombre) for e in self.empresas], width=300)
        self.origen_input = ft.TextField(label='Lugar de origen')
        self.destino_input = ft.TextField(label="Lugar de destino")
        self.matricula_input = ft.TextField(label='Matrícula')
        self.matricula_remolque_input = ft.TextField(label='Matrícula Semiremolque')
        self.naturaleza_input = ft.TextField(label='Naturaleza Carga')
        self.peso_input = ft.TextField(label='Peso en Kg')
        self.message = ft.Text(value='', visible=False)

        return ft.View(
            route="/create_document",
            controls=[
                ft.AppBar(title=ft.Text('Nuevo Documento'), actions=[self.theme_button]),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self.empresas_dropdown,
                            self.origen_input,
                            self.destino_input,
                            self.matricula_input,
                            self.matricula_remolque_input,
                            self.naturaleza_input,
                            self.peso_input,
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton('Guardar', on_click=self.save_document),
                                    ft.OutlinedButton("Cancelar", on_click=lambda e: self.force_route("/dashboard")),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            self.message
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15
                    ),
                    padding=30,
                    alignment=ft.alignment.top_center
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )
        
    def _load_empresas(self):
        engine = create_engine('sqlite:///database/transcontrol.db')
        Session = sessionmaker(bind=engine)
        session = Session()
        self.empresas = session.query(Empresas).all()
        session.close()

    async def save_document(self, e):
        try:
            engine = create_engine('sqlite:///database/transcontrol.db')
            Session = sessionmaker(bind=engine)
            session = Session()

            usuario = session.query(Usuario).first()
            empresa = session.query(Empresas).first()

            doc = Documentos(
                usuarios_id=usuario.id,
                empresas_id_transportista=empresa.id,
                empresas_id_contratante=empresa.id,
                lugar_origen=self.origen_input.value,
                lugar_destino=self.destino_input.value,
                fecha_transporte=date.today(),
                fecha_creacion=date.today(),
                matricula_vehiculo=self.matricula_input.value,
                matricula_semiremolque='R-0000-XXX',
                naturaleza_carga='Palets',
                peso=float(self.peso_input.value),
                firma_cargador='Cargador',
                firma_transportista='Transportista'
            )

            session.add(doc)
            session.commit()
            self.message.value = '✅ Documento creado correctamente'
            self.message.visible = True

            await asyncio.sleep(1)
            await self.page.go('/documents')

        except Exception as err:
            self.message.value = f'❌ Error: {err}'
            self.message.visible = True

        finally:
            session.close()
            self.page.update()
