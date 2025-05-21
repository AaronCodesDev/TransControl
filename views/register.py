import flet as ft
from database.models import Usuario
from datetime import datetime
from utils.security import hash_password  

import bcrypt

class RegisterView:
    def __init__(self, page: ft.Page, theme_button, go_to_login):
        self.page = page
        self.theme_button = theme_button
        self.go_to_login = go_to_login
        
        # Campos del formulario
        self.nif = ft.TextField(label='NIF', hint_text='Ej: 12345678A')
        self.name = ft.TextField(label='Nombre', autofocus=True)
        self.apellido = ft.TextField(label='Apellido')
        self.email = ft.TextField(label='Correo electrónico')
        self.password = ft.TextField(
            label='Contraseña', 
            password=True, 
            can_reveal_password=True
        )
        self.confirm_password = ft.TextField(
            label='Confirmar contraseña', 
            password=True, 
            can_reveal_password=True
        )
        
        # Elementos UI
        self.error_text = ft.Text('', color=ft.colors.RED, size=12, visible=False)
        self.success_text = ft.Text('', color=ft.colors.GREEN, size=12, visible=False)
        self.logo = ft.Image(
            src='assets/logo_dark.png' if page.theme_mode == ft.ThemeMode.DARK else 'assets/logo_light.png',
            width=150,
            height=150,
        )

    def build(self):
        return ft.View(
                "/register",
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row([self.theme_button], alignment=ft.MainAxisAlignment.END),
                            self.logo,
                            ft.Text("Registro de usuario", size=28, weight="bold"),
                            self.name,
                            self.apellido,
                            self.nif,
                            self.email,
                            self.password,
                            self.confirm_password,
                            self.error_text,
                            self.success_text,
                            ft.ElevatedButton("Registrarse", on_click=self.register),
                            ft.TextButton(
                                "¿Ya tienes cuenta? Inicia sesión", 
                                on_click=lambda e: self.go_to_login()
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ]
            )

    def register(self, e):
        # Resetear mensajes
        self.error_text.visible = False
        self.success_text.visible = False
        
        # Validaciones básicas
        if not all([self.nif.value, self.name.value, 
                   self.email.value, self.password.value]):
            self.show_error('Por favor completa todos los campos')
            return
            
        if '@' not in self.email.value:
            self.show_error('Correo electrónico inválido')
            return
            
        if self.password.value != self.confirm_password.value:
            self.show_error('Las contraseñas no coinciden')
            return
            
        # Verificar si el usuario ya existe
        if self.user_exists():
            self.show_error('El usuario o NIF ya están registrados')
            return
            
        # Crear nuevo usuario
        try:
            hashed_password = hash_password(self.password.value)
            new_user = Usuario(
                nombre=self.name.value,
                apellido=self.apellido.value,
                nif=self.nif.value,
                email=self.email.value,
                contrasena=hashed_password,
                fecha_creacion=datetime.now(),
                rol='usuario'  # Rol por defecto
            )
            
            self.page.db.add(new_user)
            self.page.db.commit()
            
            self.show_success('Registro exitoso! Redirigiendo...')
            self.page.update()
            
            self.go_to_login()
            
        except Exception as e:
            self.page.db.rollback()
            self.show_error(f'Error al registrar: {str(e)}')

    def user_exists(self):
        """Verifica si el usuario o NIF ya existen"""
        return self.page.db.query(Usuario).filter(
            (Usuario.nif == self.nif.value) |
            (Usuario.email == self.email.value)
        ).first() is not None

    def show_error(self, message):
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()

    def show_success(self, message):
        self.success_text.value = message
        self.success_text.visible = True
        self.page.update()

    def update_theme(self):
        """Actualiza el logo cuando cambia el tema"""
        self.logo.src = 'assets/logo_dark.png' if self.page.theme_mode == ft.ThemeMode.DARK else 'assets/logo_light.png'
        self.page.update()