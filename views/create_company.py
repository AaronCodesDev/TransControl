import flet as ft
from datetime import date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Empresas
import asyncio


class CreateCompanyView:
    def __init__(self, page: ft.Page, theme_button, force_route, user):
        self.page = page
        self.theme_button = theme_button
        self.force_route = force_route
        self.user = user

    def build(self):
        field_style = dict(border_radius=12, filled=True)

        self.nombre = ft.TextField(label='Nombre de la empresa', prefix_icon=ft.Icons.APARTMENT_OUTLINED, **field_style)
        self.direccion = ft.TextField(label='Dirección', prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, **field_style)
        self.codigo_postal = ft.TextField(label='Código Postal', prefix_icon=ft.Icons.PIN_OUTLINED, **field_style)
        self.ciudad = ft.TextField(label='Ciudad', prefix_icon=ft.Icons.LOCATION_CITY_OUTLINED, **field_style)
        self.provincia = ft.TextField(label='Provincia', prefix_icon=ft.Icons.MAP_OUTLINED, **field_style)
        self.cif = ft.TextField(label='CIF', prefix_icon=ft.Icons.BADGE_OUTLINED, **field_style)
        self.telefono = ft.TextField(label='Teléfono', prefix_icon=ft.Icons.PHONE_OUTLINED, **field_style)
        self.email = ft.TextField(label='Email', keyboard_type=ft.KeyboardType.EMAIL, prefix_icon=ft.Icons.EMAIL_OUTLINED, **field_style)
        self.message = ft.Text(value="", visible=False, text_align=ft.TextAlign.CENTER)

        tc       = getattr(self.page, 'tc_theme', {})
        ab_color = tc.get('appbar_color', '#0D0D0D')
        accent   = tc.get('accent', '#A3E635')
        bg       = tc.get('bg', '#0D0D0D')

        header = ft.Container(
            padding=ft.padding.only(top=48, bottom=24, left=20, right=20),
            bgcolor=ab_color,
            content=ft.Column(spacing=0, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.GestureDetector(
                            on_tap=lambda e: self.force_route('/companies'),
                            content=ft.Row(spacing=6, controls=[
                                ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE), size=16),
                                ft.Text('Volver', size=13,
                                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
                            ]),
                        ),
                        self.theme_button,
                    ],
                ),
                ft.Container(height=14),
                ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Container(
                        width=40, height=40, border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.15, accent),
                        alignment=ft.alignment.center,
                        content=ft.Icon(ft.Icons.APARTMENT_ROUNDED, color=accent, size=22),
                    ),
                    ft.Text('Registrar Empresa', size=22, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                ]),
            ]),
        )

        body = ft.Container(
            expand=True,
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            bgcolor=bg,
            padding=ft.padding.only(left=24, right=24, top=20, bottom=32),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=14,
                controls=[
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border_radius=16,
                        bgcolor=ft.Colors.with_opacity(0.12, accent),
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINED, color=accent, size=18),
                            ft.Text("Todos los campos son obligatorios", size=13, color=accent),
                        ], spacing=8),
                    ),
                    self.nombre,
                    self.direccion,
                    ft.ResponsiveRow(controls=[
                        ft.Container(self.ciudad, col={"xs": 12, "sm": 8, "md": 8}),
                        ft.Container(self.codigo_postal, col={"xs": 12, "sm": 4, "md": 4}),
                    ], spacing=12),
                    ft.ResponsiveRow(controls=[
                        ft.Container(self.provincia, col={"xs": 12, "sm": 6, "md": 6}),
                        ft.Container(self.cif, col={"xs": 12, "sm": 6, "md": 6}),
                    ], spacing=12),
                    ft.ResponsiveRow(controls=[
                        ft.Container(self.telefono, col={"xs": 12, "sm": 4, "md": 4}),
                        ft.Container(self.email, col={"xs": 12, "sm": 8, "md": 8}),
                    ], spacing=12),
                    ft.Container(height=4),
                    self.message,
                    ft.Container(
                        border_radius=14,
                        bgcolor=accent,
                        shadow=ft.BoxShadow(blur_radius=14,
                                            color=ft.Colors.with_opacity(0.35, accent),
                                            offset=ft.Offset(0, 4)),
                        on_click=self.save_company,
                        padding=ft.padding.symmetric(vertical=15),
                        alignment=ft.alignment.center,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.SAVE_OUTLINED, color=ft.Colors.BLACK, size=18),
                                ft.Text('Guardar empresa', size=15, weight=ft.FontWeight.W_700,
                                        color=ft.Colors.BLACK),
                            ],
                        ),
                    ),
                    ft.TextButton(
                        "Cancelar",
                        icon=ft.Icons.CLOSE,
                        on_click=lambda e: self.force_route("/companies"),
                        style=ft.ButtonStyle(color=ft.Colors.GREY_500),
                    ),
                ],
            ),
        )

        return ft.View(
            "/create_company",
            padding=0,
            bgcolor=bg,
            controls=[
                ft.Column(spacing=0, expand=True, controls=[header, body]),
            ],
        )

    async def save_company(self, e):
        if not all([
            self.nombre.value.strip(),
            self.direccion.value.strip(),
            self.ciudad.value.strip(),
            self.provincia.value.strip(),
            self.codigo_postal.value.strip(),
            self.cif.value.strip(),
            self.telefono.value.strip(),
            self.email.value.strip()
        ]):
            self.message.value = "⚠️ Todos los campos son obligatorios."
            self.message.color = ft.Colors.ERROR
            self.message.visible = True
            self.page.update()
            return

        if '@' not in self.email.value or '.' not in self.email.value:
            self.message.value = "⚠️ Email inválido."
            self.message.color = ft.Colors.ERROR
            self.message.visible = True
            self.page.update()
            return

        try:
            engine = create_engine('sqlite:///database/transcontrol.db')
            Session = sessionmaker(bind=engine)
            session = Session()

            new_company = Empresas(
                nombre=self.nombre.value.strip(),
                direccion=self.direccion.value.strip(),
                ciudad=self.ciudad.value.strip(),
                provincia=self.provincia.value.strip(),
                codigo_postal=self.codigo_postal.value.strip(),
                cif=self.cif.value.strip(),
                telefono=self.telefono.value.strip(),
                email=self.email.value.strip(),
                fecha_creacion=date.today(),
                usuario_id=self.user.id,
            )

            session.add(new_company)
            session.commit()
            company_name = new_company.nombre
            session.close()

            self.message.value = f"✅ Empresa '{company_name}' guardada correctamente"
            self.message.color = ft.Colors.GREEN_700
            self.message.visible = True
            self.page.update()

            await asyncio.sleep(1)
            await self.page.go('/companies')

        except Exception as err:
            self.message.value = f"❌ Error: {err}"
            self.message.color = ft.Colors.ERROR
            self.message.visible = True
            self.page.update()
