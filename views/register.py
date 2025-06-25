import flet as ft
from database.models import Usuario
from datetime import datetime
from utils.security import hash_password

class RegisterView:
    def __init__(self, page: ft.Page, theme_button, go_to_login):
        self.page = page
        self.theme_button = theme_button
        self.go_to_login = go_to_login

        # Definir carpeta de assets para las imágenes
        self.page.assets_dir = "assets"

        # Logo ajustado
        self.logo = ft.Image(
            src="logo.png",  # Flet buscará en assets_dir
            width=250,
            height=250,
        )

        # Campos del formulario
        self.nif = ft.TextField(label='NIF', hint_text='Ej: 12345678A')
        self.name = ft.TextField(label='Nombre', autofocus=True)
        self.apellido = ft.TextField(label='Apellido')
        self.email = ft.TextField(label='Correo electrónico')
        self.password = ft.TextField(label='Contraseña', password=True, can_reveal_password=True)
        self.confirm_password = ft.TextField(label='Confirmar contraseña', password=True, can_reveal_password=True)

        # Mensajes
        self.error_text = ft.Text('', color=ft.Colors.RED, size=12, visible=False)
        self.success_text = ft.Text('', color=ft.Colors.GREEN, size=12, visible=False)

    def build(self):
        return ft.View(
            "/register",
            controls=[
                ft.Row([self.theme_button], alignment=ft.MainAxisAlignment.END),
                ft.Container(
                    alignment=ft.alignment.center,
                    expand=True,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,  # más pegado
                        controls=[
                            self.logo,
                            ft.Text("Registro de usuario", size=24, weight="bold"),
                            *(ft.Container(
                                field,
                                alignment=ft.alignment.center,
                                width=300
                            ) for field in [
                                self.name,
                                self.apellido,
                                self.nif,
                                self.email,
                                self.password,
                                self.confirm_password,
                            ]),
                            ft.Container(self.error_text, alignment=ft.alignment.center, width=300),
                            ft.Container(self.success_text, alignment=ft.alignment.center, width=300),
                            ft.Container(
                                ft.ElevatedButton("Registrarse", on_click=self.register),
                                alignment=ft.alignment.center,
                                width=300
                            ),
                            ft.Container(
                                ft.TextButton(
                                    "¿Ya tienes cuenta? Inicia sesión",
                                    on_click=lambda e: self.go_to_login()
                                ),
                                alignment=ft.alignment.center,
                                width=300
                            ),
                        ],
                    ),
                ),
            ],
            padding=0,  # sin margen alrededor
            spacing=10  # menos espacio entre los bloques principales
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

            self.show_success("Registro exitoso! Redirigiendo...")
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
