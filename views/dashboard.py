import os
import random
import flet as ft
from datetime import date, datetime
from database.crud import get_document_count, get_daily_routes, get_company_count, get_top_destinations
from utils.nav_bar import build_bottom_nav

FRASES_TRANSPORTE = [
    "Cada kilómetro recorrido es un paso más hacia el éxito.",
    "Las rutas más largas forjan los mejores conductores.",
    "El asfalto es tu lienzo, el camión tu pincel.",
    "Mover el mundo, un envío a la vez.",
    "La constancia en la carretera es la clave del negocio.",
    "Cada entrega a tiempo es una promesa cumplida.",
    "El transporte no para: tú tampoco.",
    "Detrás de cada producto hay un conductor que lo hizo posible.",
    "La carretera premia a los que salen temprano.",
    "Sin transportistas, el mundo se detiene.",
    "Tu volante, tu empresa, tu futuro.",
    "Cada ruta nueva es una oportunidad nueva.",
    "La puntualidad es el mejor contrato que puedes firmar.",
    "El motor que arranca todos los días es el de quien triunfa.",
    "Confía en tu ruta, confía en tu esfuerzo.",
    "El camino largo también llega a destino.",
    "Un buen transportista nunca pierde el rumbo.",
    "La carretera enseña lo que ningún aula puede.",
    "Profesionalidad al volante, confianza en el cliente.",
    "Cada km es inversión en tu reputación.",
    "El transporte es el corazón de la economía.",
    "No hay carga demasiado grande para quien está preparado.",
    "La logística perfecta empieza con un conductor comprometido.",
    "Salir antes del amanecer es el secreto de los mejores.",
    "Tu trabajo mueve el comercio de toda una región.",
    "El respeto en la carretera se gana con hechos.",
    "Cada entrega exitosa construye tu nombre.",
    "Los kilómetros no mienten: el esfuerzo siempre se nota.",
    "Un conductor organizado es un negocio que crece.",
    "La paciencia en el tráfico es sabiduría en el negocio.",
    "Hoy es un buen día para superar el récord de ayer.",
    "La carretera es larga, pero tu determinación es más.",
    "Conoces cada curva, conoces tu oficio.",
    "El transporte une ciudades y une personas.",
    "Detrás del volante hay un emprendedor.",
    "Cada factura cobrada es el fruto de tu esfuerzo.",
    "La disciplina en la ruta se refleja en los resultados.",
    "Mantén el depósito lleno y la actitud más llena aún.",
    "Los mejores negocios se construyen kilómetro a kilómetro.",
    "Tu camión es tu herramienta, cuídala como a tu empresa.",
    "El cliente que confía en ti vale más que cien nuevos.",
    "La seguridad vial es también seguridad para tu negocio.",
    "Cada parada bien gestionada ahorra tiempo y dinero.",
    "El transporte eficiente es el que nadie nota porque todo llega.",
    "Conocer la ruta es la mitad del trabajo.",
    "El motor más importante es tu motivación.",
    "Rutas claras, cuentas claras, negocio claro.",
    "El frío del amanecer despierta a los que de verdad quieren.",
    "Un camionero feliz es el mejor seguro de tu mercancía.",
    "La excelencia no se improvisa, se conduce cada día.",
    "Lo que hoy parece lejos, mañana ya está entregado.",
    "Tu GPS más fiable es tu experiencia.",
    "La carretera recompensa la dedicación.",
    "Cada nuevo cliente fue antes un desconocido en la ruta.",
    "El transportista profesional no para por el mal tiempo.",
    "Organizar bien la carga es organizar bien el negocio.",
    "Cada documento en regla es un paso libre en la carretera.",
    "La flota que se cuida es la que nunca falla.",
    "El mejor camino es el que lleva al cliente satisfecho.",
    "Conduce con cabeza, llega con orgullo.",
    "La rentabilidad empieza antes de arrancar el motor.",
    "Hay quienes mueven montañas; tú mueves lo que importa.",
    "El transporte no entiende de excusas, solo de soluciones.",
    "Conoce tus costes como conoces tus rutas.",
    "Una entrega a tiempo vale más que mil palabras.",
    "El profesional del transporte vende confianza, no solo fletes.",
    "Cada mañana que arrancas es una victoria sobre la rutina.",
    "La puntualidad es la cortesía de los camioneros.",
    "Cuida tu carta de porte como cuidas tu reputación.",
    "El transporte une lo que la distancia separa.",
    "Las mejores historias de éxito empiezan en una cabina.",
    "Quien conoce bien su ruta, conoce bien su negocio.",
    "No existe mal tiempo para un buen transportista.",
    "Tu esfuerzo hoy es el capital de mañana.",
    "La carretera es justa: da a cada uno lo que aporta.",
    "Cada kilómetro en blanco es una oportunidad perdida.",
    "El transporte bien hecho no necesita publicidad.",
    "Sé el conductor que tus clientes recomiendan.",
    "La constancia supera al talento sin esfuerzo.",
    "Haz de cada ruta una experiencia memorable.",
    "El mejor descanso es el que prepara la próxima entrega.",
    "Los grandes negocios del transporte empezaron con un solo camión.",
    "Mantén la cabeza fría y el volante firme.",
    "El transportista puntual nunca busca excusas.",
    "Tu ruta es única; nadie la conoce mejor que tú.",
    "La calidad del servicio vale más que el precio del flete.",
    "Cada nuevo contrato es una nueva confianza depositada en ti.",
    "El camino al éxito tiene muchos peajes, pero vale la pena.",
    "Los que mueven la carga mueven la economía.",
    "Hoy la carretera es tuya; aprovéchala.",
    "El transporte es vocación, no solo profesión.",
    "Cuida cada entrega como si fuera la primera.",
    "El profesional del volante sabe que el tiempo es dinero.",
    "Una ruta bien planificada es la mitad del éxito.",
    "El orgullo del transportista está en llegar siempre.",
    "Cada empresa que confía en ti es un socio de vida.",
    "La carretera no espera; tampoco tus oportunidades.",
    "Ser puntual es ser profesional.",
    "El mejor kilometraje es el que lleva satisfacción al cliente.",
    "TransControl: tu negocio organizado, tu ruta despejada.",
]


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
        frase  = random.choice(FRASES_TRANSPORTE)

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
                        ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                            ft.Image(src='logo.svg', width=28, height=28, fit=ft.ImageFit.CONTAIN),
                            ft.Text('TransControl', size=14, weight=ft.FontWeight.W_600,
                                    color=ft.Colors.with_opacity(0.80, ft.Colors.WHITE)),
                        ]),
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
                            ft.Text(saludo + ',', size=13,
                                    color=ft.Colors.with_opacity(0.80, ft.Colors.WHITE)),
                            ft.Row(spacing=6, controls=[
                                ft.Text((self.user.nombre or 'Usuario') + ' 👋', size=24,
                                        weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                            ]),
                            ft.Container(height=6),
                            ft.Text(frase, size=11,
                                    color=ft.Colors.with_opacity(0.70, ft.Colors.WHITE),
                                    italic=True, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS,
                                    width=220),
                        ]),
                        avatar,
                    ],
                ),
            ]),
        )

        # ── Stats row ─────────────────────────────────────────
        def stat_card(value, label, emoji):
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
                        ft.Text(emoji, size=22, text_align=ft.TextAlign.CENTER),
                        ft.Text(value, size=24, weight=ft.FontWeight.W_800, color=accent),
                        ft.Text(label, size=9, color=text_label, weight=ft.FontWeight.W_600,
                                text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )

        stats_row = ft.Row(spacing=10, controls=[
            stat_card(str(total_docs),    'DOCS',     '📄'),
            stat_card(str(company_count), 'EMPRESAS', '🏢'),
            stat_card(str(daily_docs),    'HOY',      '📅'),
        ])

        # ── Quick actions ─────────────────────────────────────
        def action_card(label, icon, route):
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
                on_click=lambda e, r=route: self._nav(r),
                ink=True,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                    controls=[
                        ft.Icon(icon, size=22, color=accent),
                        ft.Text(label, size=9, color=text_label, weight=ft.FontWeight.W_600,
                                text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )

        quick_actions = ft.Row(spacing=10, controls=[
            action_card('NUEVO DOC', ft.Icons.DESCRIPTION_OUTLINED,    '/create_document'),
            action_card('EMPRESA',   ft.Icons.APARTMENT_ROUNDED,       '/create_company'),
            action_card('VEHÍCULOS', ft.Icons.DIRECTIONS_CAR_ROUNDED,  '/vehicles'),
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
                                    ft.Text('📍', size=12),
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
        return build_bottom_nav(self.page, '/dashboard', ab_color)
