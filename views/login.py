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

        self.email = ft.TextField(
            label='Correo electrónico',
            value=guardado['email'] if guardado else '',
            autofocus=True,
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            border_radius=14,
            filled=True,
            focused_border_color='#2E7D32',
        )
        self.password = ft.TextField(
            label='Contraseña',
            password=True,
            can_reveal_password=True,
            value=guardado['password'] if guardado else '',
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            border_radius=14,
            filled=True,
            focused_border_color='#2E7D32',
        )
        self.remember_me = ft.Checkbox(
            label='Recordarme',
            value=True if guardado else False,
            active_color='#2E7D32',
        )
        self.error_text = ft.Text('', color=ft.Colors.RED_400, size=13, visible=False,
                                  text_align=ft.TextAlign.CENTER)
        self.message_text = ft.Text('', color='#2E7D32', size=13, visible=False,
                                    text_align=ft.TextAlign.CENTER)

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
                    self.error_text.visible = False
                    self.message_text.value = f'Bienvenido, {user.nombre} {user.apellido}'
                    self.message_text.visible = True
                    if self.remember_me.value:
                        save_credentials(self.email.value, self.password.value)
                    else:
                        clear_credentials()
                    self.page.update()
                    self.on_login_success(user)
                else:
                    clear_credentials()
                    self.reset_fields()
                    self.error_text.value = 'Usuario o contraseña incorrectos'
                    self.error_text.visible = True
                    self.page.update()
            except Exception as ex:
                clear_credentials()
                self.reset_fields()
                self.error_text.value = f'Error inesperado: {str(ex)}'
                self.error_text.visible = True
                self.page.update()
            finally:
                login_btn.disabled = False
                self.page.update()

        login_btn = ft.Container(
            content=ft.Text('Iniciar sesión', size=15, weight=ft.FontWeight.W_700,
                            color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            on_click=login,
            border_radius=14,
            padding=ft.padding.symmetric(vertical=14),
            gradient=ft.LinearGradient(
                begin=ft.alignment.center_left,
                end=ft.alignment.center_right,
                colors=['#2E7D32', '#43A047'],
            ),
            shadow=ft.BoxShadow(
                blur_radius=16,
                color=ft.Colors.with_opacity(0.35, '#2E7D32'),
                offset=ft.Offset(0, 4),
            ),
            alignment=ft.alignment.center,
        )

        # ── Sección superior con gradiente ─────────────────
        top_section = ft.Container(
            padding=ft.padding.only(top=56, bottom=36, left=20, right=20),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=['#1B5E20', '#2E7D32'],
            ),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Row([self.theme_button], alignment=ft.MainAxisAlignment.END),
                    ft.Image(src='logo.svg', width=90, height=90, fit=ft.ImageFit.CONTAIN),
                    ft.Text('TransControl', size=24, weight=ft.FontWeight.W_800,
                            color=ft.Colors.WHITE),
                    ft.Text('GESTIÓN DE TRANSPORTES', size=10,
                            color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                            weight=ft.FontWeight.W_600),
                ],
            ),
        )

        # ── Tarjeta blanca inferior ────────────────────────
        bottom_card = ft.Container(
            expand=True,
            border_radius=ft.border_radius.only(top_left=28, top_right=28),
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.only(left=24, right=24, top=28, bottom=24),
            shadow=ft.BoxShadow(
                blur_radius=32,
                color=ft.Colors.with_opacity(0.14, ft.Colors.BLACK),
                offset=ft.Offset(0, -8),
            ),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=0,
                controls=[
                    ft.Text('Bienvenido', size=22, weight=ft.FontWeight.W_700, color='#1B5E20'),
                    ft.Container(height=4),
                    ft.Text('Accede a tu cuenta para continuar', size=13, color='#9E9E9E'),
                    ft.Container(height=22),
                    self.email,
                    ft.Container(height=12),
                    self.password,
                    ft.Container(height=8),
                    ft.Row([self.remember_me], alignment=ft.MainAxisAlignment.START),
                    ft.Container(height=4),
                    self.error_text,
                    self.message_text,
                    ft.Container(height=8),
                    login_btn,
                    ft.Container(height=16),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.TextButton(
                                'Olvidar datos',
                                icon=ft.Icons.DELETE_OUTLINE,
                                on_click=lambda e: (clear_credentials(), self.reset_fields()),
                                style=ft.ButtonStyle(color='#BDBDBD'),
                            ),
                            ft.TextButton(
                                '¿No tienes cuenta? Regístrate',
                                on_click=lambda e: self.go_to_register(),
                                style=ft.ButtonStyle(color='#2E7D32'),
                            ),
                        ],
                    ),
                ],
            ),
        )

        return ft.View(
            route='/login',
            bgcolor='#1B5E20',
            padding=0,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Column(
                    spacing=0,
                    expand=True,
                    controls=[top_section, bottom_card],
                )
            ],
        )
