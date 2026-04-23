import os
import flet as ft
from datetime import date, datetime
from database.crud import get_document_count, get_daily_routes, get_company_count, get_top_destinations


class DashboardView:
    def __init__(self, page: ft.Page, theme_button, force_route):
        self.page = page
        self.theme_button = theme_button
        self.user = page.user
        self.force_route = force_route

    def build(self):
        total_docs    = get_document_count(self.page.db, self.user)
        daily_docs    = len(get_daily_routes(self.page.db, datetime.now().date(), self.user))
        company_count = get_company_count(self.page.db, self.user)
        top_dests     = get_top_destinations(self.page.db, self.user, limit=5)

        hora   = datetime.now().hour
        saludo = "Buenos días" if hora < 13 else ("Buenas tardes" if hora < 20 else "Buenas noches")

        tc     = getattr(self.page, 'tc_theme', {})
        ab_color = tc.get('appbar_color', '#1B5E20')
        accent   = tc.get('accent', '#43A047')
        bg       = tc.get('bg', '#F1F8E9')
        card     = tc.get('card', '#FFFFFF')
        is_dark  = tc.get('mode', 'light') == 'dark'

        text_primary   = ft.Colors.WHITE if is_dark else '#1A1A1A'
        text_secondary = ft.Colors.with_opacity(0.55, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_600
        text_label     = ft.Colors.with_opacity(0.45, ft.Colors.WHITE) if is_dark else ft.Colors.GREY_500

        # ── Avatar ───────────────────────────────────────────
        foto = getattr(self.user, 'foto_perfil', None)
        if foto and os.path.exists(foto):
            avatar_content = ft.Image(src=foto, width=40, height=40, fit=ft.ImageFit.COVER)
        else:
            initials = ((self.user.nombre or '')[:1] + (self.user.apellido or '')[:1]).upper() or 'TC'
            avatar_content = ft.Text(initials, size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

        avatar = ft.GestureDetector(
            on_tap=lambda e: self._nav('/profile'),
            content=ft.Container(
                width=40, height=40, border_radius=20,
                bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                border=ft.border.all(2, ft.Colors.with_opacity(0.35, ft.Colors.WHITE)),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                alignment=ft.alignment.center,
                content=avatar_content,
            ),
        )

        admin_btn = None
        if self.user and self.user.rol == 'admin':
            admin_btn = ft.IconButton(
                icon=ft.Icons.SECURITY,
                icon_color=ft.Colors.WHITE,
                tooltip='Panel de administración',
                on_click=lambda e: self._nav('/admin'),
            )

        # ── Header ───────────────────────────────────────────
        header = ft.Container(
            padding=ft.padding.only(top=48, bottom=28, left=20, right=20),
            bgcolor=ab_color,
            content=ft.Column(spacing=0, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text('TransControl', size=14, weight=ft.FontWeight.W_600,
                                color=ft.Colors.with_opacity(0.55, ft.Colors.WHITE)),
                        ft.Row(spacing=0, controls=[
                            *(([admin_btn]) if admin_btn else []),
                            self.theme_button,
                        ]),
                    ],
                ),
                ft.Container(height=20),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(spacing=2, controls=[
                            ft.Text(saludo + ',', size=13, color=text_secondary),
                            ft.Row(spacing=6, controls=[
                                ft.Text(self.user.nombre or 'Usuario', size=24,
                                        weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                            ]),
                        ]),
                        avatar,
                    ],
                ),
            ]),
        )

        # ── Stats row ─────────────────────────────────────────
        def stat_card(value, label, icon):
            return ft.Container(
                expand=1,
                border_radius=16,
                bgcolor=card,
                border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)),
                padding=ft.padding.symmetric(horizontal=8, vertical=14),
                shadow=ft.BoxShadow(
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                    controls=[
                        ft.Icon(icon, size=18, color=accent),
                        ft.Text(value, size=24, weight=ft.FontWeight.W_800, color=accent),
                        ft.Text(label, size=9, color=text_label, weight=ft.FontWeight.W_600,
                                text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )

        stats_row = ft.Row(spacing=10, controls=[
            stat_card(str(total_docs),    'DOCS',     ft.Icons.DESCRIPTION_OUTLINED),
            stat_card(str(company_count), 'EMPRESAS', ft.Icons.APARTMENT_OUTLINED),
            stat_card(str(daily_docs),    'HOY',      ft.Icons.TODAY_OUTLINED),
        ])

        # ── Quick actions ─────────────────────────────────────
        def action_card(label, sublabel, icon, route):
            return ft.GestureDetector(
                on_tap=lambda e, r=route: self._nav(r),
                content=ft.Container(
                    expand=1,
                    border_radius=16,
                    padding=ft.padding.all(14),
                    bgcolor=card,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)),
                    shadow=ft.BoxShadow(
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                        offset=ft.Offset(0, 3),
                    ),
                    content=ft.Column(spacing=6, controls=[
                        ft.Container(
                            width=36, height=36, border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.15, accent),
                            alignment=ft.alignment.center,
                            content=ft.Icon(icon, size=20, color=accent),
                        ),
                        ft.Text(label, size=12, weight=ft.FontWeight.W_700, color=text_primary),
                        ft.Text(sublabel, size=10, color=text_secondary),
                    ]),
                ),
            )

        quick_actions = ft.Row(spacing=10, controls=[
            action_card('Nuevo doc', 'Carta de porte',
                        ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, '/create_document'),
            action_card('Empresa', 'Contratante',
                        ft.Icons.APARTMENT_ROUNDED, '/create_company'),
            action_card('Vehículos', 'Mis matrículas',
                        ft.Icons.DIRECTIONS_CAR_ROUNDED, '/vehicles'),
        ])

        # ── Recent docs ───────────────────────────────────────
        recent_docs = get_daily_routes(self.page.db, None, self.user) if hasattr(self.page.db, 'query') else []
        # Use top_dests as recent indicator or fetch from crud
        def recent_docs_widget():
            if not top_dests:
                return ft.Container(
                    padding=ft.padding.symmetric(vertical=16),
                    alignment=ft.alignment.center,
                    content=ft.Text("Sin documentos todavía", size=13,
                                    color=text_label, italic=True),
                )
            rows = []
            medals = ['🥇', '🥈', '🥉', '④', '⑤']
            max_val = top_dests[0][1] if top_dests else 1
            for i, (destino, total) in enumerate(top_dests):
                pct = total / max_val if max_val > 0 else 0
                rows.append(ft.Container(
                    border_radius=12,
                    bgcolor=card,
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    margin=ft.margin.only(bottom=8),
                    shadow=ft.BoxShadow(
                        blur_radius=6,
                        color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK),
                        offset=ft.Offset(0, 2),
                    ),
                    content=ft.Column(spacing=6, controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(spacing=6, expand=True, controls=[
                                    ft.Text(medals[i] if i < 3 else f"{i+1}.", size=13),
                                    ft.Text(destino, size=13, weight=ft.FontWeight.W_600,
                                            color=accent,
                                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                ]),
                                ft.Text(f"{total}×", size=11, color=text_secondary),
                            ],
                        ),
                        ft.Container(
                            height=3, border_radius=2,
                            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
                            content=ft.Container(
                                height=3, border_radius=2,
                                bgcolor=accent,
                                expand=pct,
                            ),
                        ),
                    ]),
                ))
            return ft.Column(spacing=0, controls=rows)

        def section_label(text):
            return ft.Text(text, size=10, weight=ft.FontWeight.W_700, color=text_label)

        # ── Body ─────────────────────────────────────────────
        body = ft.Container(
            expand=True,
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            bgcolor=bg,
            padding=ft.padding.only(left=20, right=20, top=24, bottom=90),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=16,
                controls=[
                    stats_row,
                    section_label('ACCIONES RÁPIDAS'),
                    quick_actions,
                    section_label('DESTINOS MÁS FRECUENTES'),
                    recent_docs_widget(),
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            datetime.now().strftime('%A, %d de %B de %Y').capitalize(),
                            size=11, color=text_label,
                        ),
                    ),
                ],
            ),
        )

        return ft.View(
            '/dashboard',
            padding=0,
            bgcolor=bg,
            bottom_appbar=self._build_bottom_appbar(ab_color, accent),
            floating_action_button=ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                bgcolor=accent,
                shape=ft.CircleBorder(),
                width=54, height=54,
                tooltip='Nuevo documento',
                on_click=lambda e: self._nav('/create_document'),
            ),
            floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_FLOAT,
            controls=[
                ft.Column(
                    spacing=0,
                    expand=True,
                    controls=[header, body],
                ),
            ],
        )

    def _nav(self, route: str):
        self.page.go(route)

    def _build_bottom_appbar(self, ab_color, accent):
        return ft.BottomAppBar(
            bgcolor=ab_color,
            elevation=8,
            content=ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    ft.IconButton(icon=ft.Icons.HOME_ROUNDED,                 icon_color=accent,          tooltip='Inicio'),
                    ft.IconButton(icon=ft.Icons.FORMAT_LIST_NUMBERED_ROUNDED,  icon_color=ft.Colors.WHITE, tooltip='Documentos', on_click=lambda e: self._nav('/documents')),
                    ft.IconButton(icon=ft.Icons.DIRECTIONS_CAR_ROUNDED,        icon_color=ft.Colors.WHITE, tooltip='Vehículos',  on_click=lambda e: self._nav('/vehicles')),
                    ft.IconButton(icon=ft.Icons.APARTMENT_ROUNDED,             icon_color=ft.Colors.WHITE, tooltip='Empresas',   on_click=lambda e: self._nav('/companies')),
                    ft.IconButton(icon=ft.Icons.PERSON_ROUNDED,                icon_color=ft.Colors.WHITE, tooltip='Perfil',     on_click=lambda e: self._nav('/profile')),
                ],
            ),
        )
