import flet as ft
from datetime import date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Empresas
import asyncio

class CreateCompanyView:
    def __init__(self, page: ft.Page, theme_button):
        self.page = page
        self.theme_button = theme_button

    def build(self):
        # Inputs
        self.nombre = ft.TextField(label='Nombre de la empresa')
        self.direccion = ft.TextField(label='Dirección')
        self.codigo_postal = ft.TextField(label='Código Postal')
        self.ciudad = ft.TextField(label='Ciudad')
        self.provincia = ft.TextField(label='Provincia')
        self.cif = ft.TextField(label='CIF')
        self.telefono = ft.TextField(label='Teléfono')
        self.mensaje = ft.Text(value="", visible=False)

        # Layout
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/create_company",
                controls=[
                    ft.AppBar(
                        title=ft.Text("Registrar Empresa"),
                        bgcolor=ft.colors.GREEN_300,
                        center_title=True,
                        actions=[self.theme_button]
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                self.nombre,
                                self.direccion,
                                self.codigo_postal,
                                self.ciudad,
                                self.provincia,
                                self.cif,
                                self.telefono,
                                self.mensaje,
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton("Guardar", on_click=self.save_company),
                                        ft.OutlinedButton("Cancelar", on_click=lambda e: self.page.go("/dashboard"))
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                )
                            ],
                            tight=True,
                            scroll=ft.ScrollMode.AUTO
                        ),
                        padding=30,
                        alignment=ft.alignment.top_center
                    )
                ]
            )
        )
        self.page.update()

    async def save_company(self, e):
        if not all([
            self.nombre.value.strip(),
            self.direccion.value.strip(),
            self.codigo_postal.value.strip(),
            self.ciudad.value.strip(),
            self.provincia.value.strip(),
            self.cif.value.strip(),
            self.telefono.value.strip()
        ]):
            self.mensaje.value = "⚠️ Todos los campos son obligatorios."
            self.mensaje.color = ft.colors.RED
            self.mensaje.visible = True
            self.page.update()
            return 
        
        try:
            engine = create_engine('sqlite:///database/transcontrol.db')
            Session = sessionmaker(bind=engine)
            session = Session()

            new_company = Empresas(
                nombre=self.nombre.value.strip(),
                direccion=self.direccion.value.strip(),
                codigo_postal=self.codigo_postal.value.strip(),
                ciudad=self.ciudad.value.strip(),
                provincia=self.provincia.value.strip(),
                cif=self.cif.value.strip(),
                telefono=self.telefono.value.strip(),
                fecha_creacion=date.today()
            )

            session.add(new_company)
            session.commit()
            new_company = new_company.nombre
            session.close()

            self.mensaje.value = f"✅ Empresa '{new_company}' guardada"
            self.mensaje.color = ft.Colors.GREEN
            self.mensaje.visible = True
            self.page.update()
            
            await asyncio.sleep(1)
            await self.page.go('/companies')

        except Exception as err:
            self.mensaje.value = f"❌ Error: {err}"
            self.mensaje.color = ft.colors.RED
            self.mensaje.visible = True
            self.page.update()
