import flet as ft
from database.models import Usuario
from datetime import datetime
from utils.security import hash_password


class RegisterView:
    def __init__(self, page: ft.Page, theme_button, go_to_login):
        self.page = page
        self.theme_button = theme_button
        self.go_to_login = go_to_login
        self.page.assets_dir = "assets"

        self.logo = ft.Image(src="logo.png", width=90, height=90)

        self.nif = ft.TextField(label='NIF', hint_text='Ej: 12345678A', prefix_icon=ft.Icons.BADGE_OUTLINED, border_radius=12, filled=True)
        self.name = ft.TextField(label='Nombre', autofocus=True, prefix_icon=ft.Icons.PERSON_OUTLINE, border_radius=12, filled=True)
        self.apellido = ft.TextField(label='Apellido', prefix_icon=ft.Icons.PERSON_OUTLINE, border_radius=12, filled=True)
        self.email = ft.TextField(label='Correo electrónico', prefix_icon=ft.Icons.EMAIL_OUTLINED, border_radius=12, filled=True)
        self.password = ft.TextField(label='Contraseña', password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_OUTLINED, border_radius=12, filled=True)
        self.confirm_password = ft.TextField(label='Confirmar contraseña', password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_OUTLINED, border_radius=12, filled=True)

        self.error_text = ft.Text('', color=ft.Colors.ERROR, size=13, visible=False, text_align=ft.TextAlign.CENTER)
        self.success_text = ft.Text('', color=ft.Colors.GREEN_700, size=13, visible=False, text_align=ft.TextAlign.CENTER)

    def build(self):
        register_btn = ft.FilledButton(
            "Crear cuenta",
            on_click=self.register,
            width=300,
            height=48,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        )

        card_width = min(400, self.page.width - 32) if self.page.width else 400
        field_width = card_width - 64

        # Actualizar ancho del botón de registro
        register_btn.width = field_width

        form_card = ft.Container(
            width=card_width,
            padding=ft.padding.symmetric(horizontal=32, vertical=28),
            border_radius=24,
            bgcolor=ft.Colors.SURFACE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=24,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
                offset=ft.Offset(0, 8),
            ),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    self.logo,
                    ft.Text("Crear cuenta", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800),
                    ft.Text("Completa tus datos para registrarte", size=13, color=ft.Colors.GREY_600),
                    ft.Divider(height=4, color=ft.Colors.TRANSPARENT),
                    ft.Container(self.name, width=field_width),
                    ft.Container(self.apellido, width=field_width),
                    ft.Container(self.nif, width=field_width),
                    ft.Container(self.email, width=field_width),
                    ft.Container(self.password, width=field_width),
                    ft.Container(self.confirm_password, width=field_width),
                    self.error_text,
                    self.success_text,
                    register_btn,
                    ft.TextButton(
                        "¿Ya tienes cuenta? Inicia sesión",
                        on_click=lambda e: self.go_to_login(),
                        style=ft.ButtonStyle(color=ft.Colors.GREEN_700),
                    ),
                ],
            ),
        )

        return ft.View(
            "/register",
            bgcolor="#E8F5E9",
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(horizontal=16, vertical=16),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.Row([self.theme_button], alignment=ft.MainAxisAlignment.END),
                            ft.Container(
                                content=form_card,
                                alignment=ft.alignment.center,
                            ),
                        ],
                    ),
                )
            ],
            padding=0,
            scroll=ft.ScrollMode.AUTO,
        )

    def register(self, e):
        self.error_text.visible = False
        self.success_text.visible = False

        if not all([self.nif.value, self.name.value, self.email.value, self.password.value]):
            self.show_error("Por favor completa todos los campos")
            return
        if "@" not in self.email.value:
            self.show_error("Correo electrónico inválido")
            return
        if self.password.value != self.confirm_password.value:
            self.show_error("Las contraseñas no coinciden")
            return
        if self.user_exists():
            self.show_error("El usuario o NIF ya están registrados")
            return

        try:
            hashed_password = hash_password(self.password.value)
            new_user = Usuario(
                nombre=self.name.value,
                apellido=self.apellido.value,
                nif=self.nif.value,
                email=self.email.value,
                contrasena=hashed_password,
                fecha_creacion=datetime.now(),
                rol="usuario",
            )
            self.page.db.add(new_user)
            self.page.db.commit()
            self.show_success("¡Registro exitoso! Redirigiendo...")
            self.go_to_login()
        except Exception as ex:
            self.page.db.rollback()
            self.show_error(f"Error al registrar: {ex}")

    def user_exists(self):
        return (
            self.page.db.query(Usuario)
            .filter((Usuario.nif == self.nif.value) | (Usuario.email == self.email.value))
            .first()
            is not None
        )

    def show_error(self, msg):
        self.error_text.value = msg
        self.error_text.visible = True
        self.page.update()

    def show_success(self, msg):
        self.success_text.value = msg
        self.success_text.visible = True
        self.page.update()
