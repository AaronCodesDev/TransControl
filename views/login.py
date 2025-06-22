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
        self.error_text = ft.Text('', color=ft.Colors.RED, size=12, visible=False)
        self.message_text = ft.Text('', color=ft.Colors.GREEN, size=12, visible=False)

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

        logo_patch = 'assets/logo.png' if self.page.theme_mode == ft.ThemeMode.DARK else 'logo.png'
        logo = ft.Image(src=logo_patch, width=250, height=250)

        return ft.View(
            route='/login',
            controls=[
                # Botón de modo oscuro arriba a la derecha sin expandir
                ft.Container(
                    content=ft.Row(
                        controls=[self.theme_button],
                        alignment=ft.MainAxisAlignment.END
                    ),
                    padding=ft.padding.only(top=20, right=20)
                ),

                # Formulario centrado
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        controls=[
                            logo,
                            ft.Text('Iniciar Sesión', size=30, weight='bold'),
                            ft.Container(self.email, alignment=ft.alignment.center, width=300),
                            ft.Container(self.password, alignment=ft.alignment.center, width=300),
                            ft.Container(
                                content=ft.Row([self.remember_me], alignment=ft.MainAxisAlignment.START),
                                alignment=ft.alignment.center,
                                width=300
                            ),
                            ft.Container(login_btn, alignment=ft.alignment.center, width=300),
                            ft.Container(self.error_text, alignment=ft.alignment.center, width=300),
                            ft.Container(self.message_text, alignment=ft.alignment.center, width=300),
                            ft.Container(
                                ft.TextButton(
                                    "❌ Olvidar datos recordados",
                                    on_click=lambda e: (clear_credentials(), self.reset_fields())
                                ),
                                alignment=ft.alignment.center,
                                width=300
                            ),
                            ft.Container(
                                ft.TextButton(
                                    "¿No tienes cuenta? Regístrate",
                                    on_click=lambda e: self.go_to_register()
                                ),
                                alignment=ft.alignment.center,
                                width=300
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    )
                )
            ]
        )
