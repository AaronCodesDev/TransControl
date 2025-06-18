import flet as ft
from datetime import date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Documentos, Empresas, Usuario
import asyncio
from utils.create_pdf import rellenar_pdf_con_fondo
import re 

class CreateDocumentView:
    def __init__(self, page, theme_button, force_route, user):
        self.page = page
        self.theme_button = theme_button
        self.force_route = force_route
        self.user = user

    def build(self):
        self._load_empresas()
        self.empresas_dropdown = ft.Dropdown(
            label='Selecciona Empresa Contratante',
            options=[ft.dropdown.Option(str(e.id), e.nombre) for e in self.empresas],
            width=310,
            menu_height=425
        )
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
                ft.AppBar(
                    title=ft.Text('Nuevo Documento'),
                    center_title=True,
                    bgcolor=ft.Colors.GREEN_700,
                    automatically_imply_leading=False,
                    actions=[self.theme_button]
                ),
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
        
        try:
            if getattr(self.user, 'rol', '') == 'admin':
                self.empresas = session.query(Empresas).all()
            else:
                self.empresas = session.query(Empresas).filter(Empresas.usuario_id == self.user.id).all()
        finally:
            session.close()
        
        self.empresas = session.query(Empresas).filter(Empresas.usuario_id == self.page.user.id).all()
        session.close()

    async def save_document(self, e):
        try:
            engine = create_engine('sqlite:///database/transcontrol.db')
            Session = sessionmaker(bind=engine)
            session = Session()

            usuario = session.query(Usuario).filter_by(id=self.page.user.id).first()

            if not self.empresas_dropdown.value:
                self.message.value = "❌ Debes seleccionar una empresa antes de guardar."
                self.message.visible = True
                self.page.update()
                session.close()
                return

            empresa_id = int(self.empresas_dropdown.value)
            empresa = session.query(Empresas).filter_by(id=empresa_id).first()

            if not all([usuario.direccion, usuario.ciudad, usuario.provincia, usuario.codigo_postal, usuario.telefono]):
                self.message.value = "❌ Debes completar tu perfil antes de generar un documento."
                self.message.visible = True
                self.page.update()
                session.close()
                return

            doc = Documentos(
                usuarios_id=usuario.id,
                empresas_id_transportista=empresa.id,
                empresas_id_contratante=empresa.id,
                lugar_origen=self.origen_input.value,
                lugar_destino=self.destino_input.value,
                fecha_transporte=date.today(),
                fecha_creacion=date.today(),
                matricula_vehiculo=self.matricula_input.value,
                matricula_semiremolque=self.matricula_remolque_input.value,
                naturaleza_carga=self.naturaleza_input.value,
                peso=float(self.peso_input.value),
                firma_cargador='Cargador',
                firma_transportista='Transportista'
            )

            session.add(doc)
            session.commit()

            print(f"Empresa seleccionada: {empresa.nombre} (ID: {empresa.id})")

            datos = {
                'fecha': doc.fecha_creacion.strftime('%d/%m/%Y'),
                'contratante': empresa.nombre,
                'direccion_contratante': empresa.direccion,
                'poblacion_contratante': empresa.ciudad,
                'provincia_contratante': empresa.provincia,
                'codigo_postal_contratante': empresa.codigo_postal,
                'telefono_contratante': empresa.telefono,
                'transportista': usuario.nombre,
                'direccion_transportista': usuario.direccion,
                'poblacion_transportista': usuario.ciudad,
                'provincia_transportista': usuario.provincia,
                'codigo_postal_transportista': usuario.codigo_postal,
                'telefono_transportista': usuario.telefono,
                'origen': doc.lugar_origen,
                'destino': doc.lugar_destino,
                'naturaleza': doc.naturaleza_carga,
                'peso': doc.peso,
                'matricula': doc.matricula_vehiculo,
                'matricula_remolque': doc.matricula_semiremolque
            }
            correo_limpio = re.sub(r'[^\w\-_.]', '_', usuario.email)
            archivo_nombre = f"documento_{correo_limpio}_{doc.id}.pdf"
            salida_pdf = f"assets/docs/{archivo_nombre}"  # asegurarte de que esta ruta exista
            rellenar_pdf_con_fondo(datos, salida_path=salida_pdf)

            doc.archivo = archivo_nombre  # Guarda el nombre del archivo en la base de datos
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