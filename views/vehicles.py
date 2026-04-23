import flet as ft
from utils.nav_bar import build_bottom_nav
from database.db import SessionLocal
from database.models import Vehiculos


class VehiclesView:
    def __init__(self, page: ft.Page, theme_button, user=None):
        self.page = page
        self.theme_button = theme_button
        self.user = user
        self.vehicles = []
        self.list_col = ft.Column(spacing=10)
        self.dialog = ft.AlertDialog(modal=True, title=ft.Text(''), content=ft.Text(''), actions=[])

    # ──────────────────────────────────────────
    #  BUILD
    # ──────────────────────────────────────────
    def build(self) -> ft.View:
        self._load_vehicles()

        tc       = getattr(self.page, 'tc_theme', {})
        ab_color = tc.get('appbar_color', '#0D0D0D')
        accent   = tc.get('accent', '#A3E635')
        bg       = tc.get('bg', '#0D0D0D')
        is_dark  = tc.get('mode', 'light') == 'dark'

        header = ft.Container(
            padding=ft.padding.only(top=48, bottom=24, left=20, right=20),
            bgcolor=ab_color,
            content=ft.Column(spacing=0, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                            ft.Image(src='logo.svg', width=28, height=28, fit=ft.ImageFit.CONTAIN),
                            ft.Text('TransControl', size=14, weight=ft.FontWeight.W_600,
                                    color=ft.Colors.with_opacity(0.80, ft.Colors.WHITE)),
                        ]),
                        self.theme_button,
                    ],
                ),
                ft.Container(height=14),
                ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Container(
                        width=40, height=40, border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.15, accent),
                        alignment=ft.alignment.center,
                        content=ft.Icon(ft.Icons.DIRECTIONS_CAR_ROUNDED, color=accent, size=22),
                    ),
                    ft.Text('Mis Vehículos', size=22, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                ]),
            ]),
        )

        body = ft.Container(
            expand=True,
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            bgcolor=bg,
            padding=ft.padding.only(left=16, right=16, top=20, bottom=90),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
                controls=[
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                        border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.12, accent),
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINED, color=accent, size=16),
                            ft.Text(
                                "Registra tus vehículos para seleccionarlos al crear documentos",
                                size=12,
                                color=accent,
                            ),
                        ], spacing=8),
                    ),
                    self.list_col,
                    self.dialog,
                ],
            ),
        )

        return ft.View(
            route='/vehicles',
            padding=0,
            bgcolor=bg,
            controls=[
                ft.Column(spacing=0, expand=True, controls=[header, body]),
            ],
            bottom_appbar=self._build_bottom_appbar(),
            floating_action_button=ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                bgcolor=accent,
                shape=ft.CircleBorder(),
                width=54, height=54,
                tooltip="Añadir vehículo",
                on_click=lambda e: self._show_vehicle_dialog(),
            ),
            floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_FLOAT,
        )

    # ──────────────────────────────────────────
    #  LOAD
    # ──────────────────────────────────────────
    def _load_vehicles(self):
        db = SessionLocal()
        try:
            self.vehicles = db.query(Vehiculos).filter(
                Vehiculos.usuario_id == self.user.id
            ).order_by(Vehiculos.id.desc()).all()
        finally:
            db.close()
        self._refresh_list()

    def _refresh_list(self):
        self.list_col.controls.clear()
        if not self.vehicles:
            self.list_col.controls.append(
                ft.Container(
                    padding=40,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.DIRECTIONS_CAR_OUTLINED, size=64, color=ft.Colors.GREY_400),
                            ft.Text("No tienes vehículos registrados", size=15, color=ft.Colors.GREY_500),
                            ft.Text("Pulsa + para añadir uno", size=12, color=ft.Colors.GREY_400),
                        ],
                    ),
                )
            )
        else:
            for v in self.vehicles:
                self.list_col.controls.append(self._build_vehicle_card(v))

    # ──────────────────────────────────────────
    #  VEHICLE CARD
    # ──────────────────────────────────────────
    def _build_vehicle_card(self, v: Vehiculos) -> ft.Container:
        tc      = getattr(self.page, 'tc_theme', {})
        accent  = tc.get('accent', '#A3E635')
        card    = tc.get('card', '#1C1E24')
        is_dark = tc.get('mode', 'light') == 'dark'
        text_secondary = ft.Colors.with_opacity(0.55, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_600

        remolque_row = (
            ft.Row([
                ft.Icon(ft.Icons.SWAP_HORIZ, size=14, color=text_secondary),
                ft.Text(f"Remolque: {v.matricula_remolque}", size=12, color=text_secondary),
            ], spacing=4)
            if v.matricula_remolque else ft.Container()
        )

        return ft.Container(
            border_radius=16,
            bgcolor=card,
            border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK), offset=ft.Offset(0, 3)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(spacing=14, controls=[
                        ft.Container(
                            width=48, height=48, border_radius=14,
                            bgcolor=ft.Colors.with_opacity(0.15, accent),
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.Icons.DIRECTIONS_CAR_ROUNDED, color=accent, size=24),
                        ),
                        ft.Column(spacing=2, controls=[
                            ft.Text(f"{v.marca} {v.modelo}", size=14, weight=ft.FontWeight.W_600, color=accent),
                            ft.Row([
                                ft.Icon(ft.Icons.CONFIRMATION_NUMBER_OUTLINED, size=13, color=text_secondary),
                                ft.Text(v.matricula, size=13, color=text_secondary, weight=ft.FontWeight.W_500),
                            ], spacing=4),
                            remolque_row,
                        ]),
                    ]),
                    ft.Row(spacing=4, controls=[
                        ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color=accent, icon_size=20,
                                      tooltip="Editar", on_click=lambda e, veh=v: self._show_vehicle_dialog(veh)),
                        ft.IconButton(icon=ft.Icons.DELETE_OUTLINED, icon_color=ft.Colors.RED_400, icon_size=20,
                                      tooltip="Eliminar", on_click=lambda e, veh=v: self._confirm_delete(veh)),
                    ]),
                ],
            ),
        )

    # ──────────────────────────────────────────
    #  DIALOG AÑADIR / EDITAR
    # ──────────────────────────────────────────
    def _show_vehicle_dialog(self, vehicle: Vehiculos = None):
        field_style = dict(border_radius=12, filled=True, dense=True)
        marca = ft.TextField(label="Marca", value=vehicle.marca if vehicle else "", prefix_icon=ft.Icons.DIRECTIONS_CAR_OUTLINED, **field_style)
        modelo = ft.TextField(label="Modelo", value=vehicle.modelo if vehicle else "", prefix_icon=ft.Icons.DIRECTIONS_CAR_FILLED_OUTLINED, **field_style)
        matricula = ft.TextField(label="Matrícula", value=vehicle.matricula if vehicle else "", prefix_icon=ft.Icons.CONFIRMATION_NUMBER_OUTLINED, **field_style)
        matricula_rem = ft.TextField(label="Matrícula remolque (opcional)", value=vehicle.matricula_remolque or "" if vehicle else "", prefix_icon=ft.Icons.LOCAL_SHIPPING_OUTLINED, **field_style)
        error = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)

        def guardar(e):
            if not marca.value.strip() or not modelo.value.strip() or not matricula.value.strip():
                error.value = "Marca, modelo y matrícula son obligatorios"
                error.visible = True
                self.page.update()
                return

            db = SessionLocal()
            try:
                if vehicle:
                    v = db.query(Vehiculos).filter_by(id=vehicle.id).first()
                    v.marca = marca.value.strip()
                    v.modelo = modelo.value.strip()
                    v.matricula = matricula.value.strip().upper()
                    v.matricula_remolque = matricula_rem.value.strip().upper() or None
                else:
                    v = Vehiculos(
                        usuario_id=self.user.id,
                        marca=marca.value.strip(),
                        modelo=modelo.value.strip(),
                        matricula=matricula.value.strip().upper(),
                        matricula_remolque=matricula_rem.value.strip().upper() or None,
                    )
                    db.add(v)
                db.commit()
            finally:
                db.close()

            self._cerrar_dialogo()
            self._load_vehicles()
            self.page.update()

        self.dialog.title = ft.Text("Nuevo vehículo" if not vehicle else "Editar vehículo", weight=ft.FontWeight.W_600)
        self.dialog.content = ft.Container(
            width=320,
            content=ft.Column(spacing=10, tight=True, controls=[
                marca, modelo, matricula, matricula_rem, error,
            ]),
        )
        self.dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._cerrar_dialogo(),
                          style=ft.ButtonStyle(color=ft.Colors.GREY_600)),
            ft.FilledButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=guardar,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
        ]
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    # ──────────────────────────────────────────
    #  CONFIRM DELETE
    # ──────────────────────────────────────────
    def _confirm_delete(self, vehicle: Vehiculos):
        def eliminar(e):
            db = SessionLocal()
            try:
                v = db.query(Vehiculos).filter_by(id=vehicle.id).first()
                if v:
                    db.delete(v)
                    db.commit()
            finally:
                db.close()
            self._cerrar_dialogo()
            self._load_vehicles()
            self.page.update()

        self.dialog.title = ft.Text("¿Eliminar vehículo?", weight=ft.FontWeight.W_600)
        self.dialog.content = ft.Text(
            f"Se eliminará {vehicle.marca} {vehicle.modelo} ({vehicle.matricula}).\n"
            "Los documentos existentes no se verán afectados.",
            size=13,
        )
        self.dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._cerrar_dialogo(),
                          style=ft.ButtonStyle(color=ft.Colors.GREY_600)),
            ft.FilledButton("Eliminar", icon=ft.Icons.DELETE_OUTLINED,
                            on_click=eliminar,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_600,
                                shape=ft.RoundedRectangleBorder(radius=10),
                            )),
        ]
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()

    def _cerrar_dialogo(self):
        self.dialog.open = False
        self.page.update()

    # ──────────────────────────────────────────
    #  NAV
    # ──────────────────────────────────────────
    def _build_bottom_appbar(self):
        ab_color = getattr(self.page, 'tc_theme', {}).get('appbar_color', '#0D0D0D')
        return build_bottom_nav(self.page, '/vehicles', ab_color)
