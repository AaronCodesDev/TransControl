import flet as ft
from database.crud import login_user
from database.credentials import load_credentials, clear_credentials, save_credentials

class LoginView:
    def __init__(self, page: ft.Page, on_login_success, theme_button, go_to_register):
        self.page = page
        self.on_login_success = on_login_success
        self.theme_button = theme_button
        self.go_to_register = go_to_register

        guardado = load_credentials()

        # Campos
        self.email = ft.TextField(
            label='Correo electrónico',
            value=guardado['email'] if guardado else '',
            autofocus=True
        )
        self.password = ft.TextField(
            label='Contraseña',
            password=True,
            can_reveal_password=True,
            value=guardado['password'] if guardado else ''
        )
        self.remember_me = ft.Checkbox(
            label="Recordarme",
            value=True if guardado else False
        )

        # Mensajes
        self.error_text = ft.Text('', color=ft.colors.RED, size=12, visible=False)
        self.message_text = ft.Text('', color=ft.colors.GREEN, size=12, visible=False)

    def reset_fields(self):
        self.email.value = ''
        self.password.value = ''
        self.remember_me.value = False
        self.error_text.visible = False
        self.message_text.visible = False
        self.page.update()

    def build(self):
        def login(e):
            login_btn.disabled = True
            self.page.update()

            try:
                db = self.page.db
                user = login_user(db, self.email.value, self.password.value)

                if user:
                    print(f"✅ Login exitoso para {user.email}")
                    self.error_text.visible = False
                    self.message_text.value = f'✅ Bienvenido {user.nombre} {user.apellido}'
                    self.message_text.visible = True

                    if self.remember_me.value:
                        save_credentials(self.email.value, self.password.value)
                    else:
                        clear_credentials()

                    self.page.update()
                    self.on_login_success(user)
                else:
                    print("❌ Login fallido - Email o contraseña incorrectos")
                    clear_credentials()
                    self.reset_fields()
                    self.message_text.visible = False
                    self.error_text.value = 'Usuario o contraseña incorrectos'
                    self.error_text.visible = True
                    self.page.update()

            except Exception as ex:
                print(f"⚠️ Error inesperado en login: {str(ex)}")
                clear_credentials()
                self.reset_fields()
                self.message_text.visible = False
                self.error_text.value = f'Error inesperado: {str(ex)}'
                self.error_text.visible = True
                self.page.update()
            finally:
                login_btn.disabled = False
                self.page.update()

        login_btn = ft.ElevatedButton('Iniciar Sesión', on_click=login)

        logo_patch = 'logo_dark.png' if self.page.theme_mode == ft.ThemeMode.DARK else 'logo_light.png'
        logo = ft.Image(src=logo_patch, width=150, height=150)

        return ft.View(
            route='/login',
            controls=[
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Row([self.theme_button], alignment=ft.MainAxisAlignment.END),
                            margin=ft.margin.only(top=30)
                        ),
                        logo,
                        ft.Text('Iniciar Sesión', size=30, weight='bold'),
                        self.email,
                        self.password,
                        self.remember_me,
                        login_btn,
                        self.error_text,
                        self.message_text,
                        ft.TextButton(
                            "❌ Olvidar datos recordados",
                            on_click=lambda e: (clear_credentials(), self.reset_fields())
                        ),
                        ft.TextButton(
                            "¿No tienes cuenta? Regístrate",
                            on_click=lambda e: self.go_to_register()
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ]
        )
