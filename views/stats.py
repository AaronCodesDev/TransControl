"""
Vista de estadísticas — TransControl
Muestra KPIs, gráficas y rankings basados en los documentos del usuario.
"""
import flet as ft
import threading
from collections import defaultdict, Counter
from datetime import date, timedelta
from database import SessionLocal
from database.models import Documentos, Empresas
from sqlalchemy.orm import joinedload
from utils.nav_bar import build_bottom_nav
from utils.map_utils import generate_map_html, open_map

MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


class StatsView:
    def __init__(self, page: ft.Page, theme_button: ft.Control, user=None):
        self.page = page
        self.theme_button = theme_button
        self.user = user

    # ── carga de datos ─────────────────────────────────────────
    def _load_docs(self):
        session = SessionLocal()
        try:
            q = (session.query(Documentos)
                 .options(joinedload(Documentos.contratante),
                          joinedload(Documentos.vehiculo))
                 .filter(Documentos.usuarios_id == self.user.id)
                 .all())
            # Materializar antes de cerrar sesión
            docs = []
            for d in q:
                docs.append({
                    'id':        d.id,
                    'origen':    d.lugar_origen or '',
                    'destino':   d.lugar_destino or '',
                    'fecha':     d.fecha_transporte or d.fecha_creacion,
                    'peso':      d.peso or 0,
                    'carga':     d.naturaleza_carga or '—',
                    'matricula': d.matricula_vehiculo or '—',
                    'empresa':   d.contratante.nombre if d.contratante else '—',
                    'albaran':   bool(d.albaran_path),
                    'archivo':   bool(d.archivo),
                })
            return docs
        finally:
            session.close()

    # ── build ──────────────────────────────────────────────────
    def build(self) -> ft.View:
        tc       = getattr(self.page, 'tc_theme', {})
        ab_color = tc.get('appbar_color', '#1B5E20')
        accent   = tc.get('accent', '#43A047')
        bg       = tc.get('bg', '#F8FBF8')
        card_bg  = tc.get('card', '#FFFFFF')
        is_dark  = tc.get('mode', 'light') == 'dark'
        text_dim = ft.Colors.with_opacity(0.55, ft.Colors.WHITE if is_dark else ft.Colors.BLACK)

        docs = self._load_docs()
        today = date.today()

        # ── calcular estadísticas ──────────────────────────────
        # KPIs mes actual vs anterior
        mes_actual  = [(d) for d in docs if d['fecha'] and
                       d['fecha'].year == today.year and d['fecha'].month == today.month]
        mes_ant_m   = (today.month - 2) % 12 + 1
        mes_ant_y   = today.year if today.month > 1 else today.year - 1
        mes_anterior = [d for d in docs if d['fecha'] and
                        d['fecha'].year == mes_ant_y and d['fecha'].month == mes_ant_m]

        viajes_mes    = len(mes_actual)
        viajes_ant    = len(mes_anterior)
        kg_mes        = sum(d['peso'] for d in mes_actual)
        kg_ant        = sum(d['peso'] for d in mes_anterior)
        sin_albaran   = sum(1 for d in docs if not d['albaran'])
        total_docs    = len(docs)

        empresa_cnt   = Counter(d['empresa'] for d in docs)
        empresa_top   = empresa_cnt.most_common(1)[0][0] if empresa_cnt else '—'

        def _delta_str(actual, anterior):
            if anterior == 0:
                return "+100%" if actual > 0 else "—"
            pct = (actual - anterior) / anterior * 100
            return f"+{pct:.0f}%" if pct >= 0 else f"{pct:.0f}%"

        def _delta_color(actual, anterior):
            if anterior == 0:
                return ft.Colors.GREEN_400
            return ft.Colors.GREEN_400 if actual >= anterior else ft.Colors.RED_400

        # Últimos 6 meses para gráficas
        meses_labels, viajes_por_mes, kg_por_mes = [], [], []
        for i in range(5, -1, -1):
            ref = date(today.year, today.month, 1) - timedelta(days=i * 30)
            m, y = ref.month, ref.year
            cnt = sum(1 for d in docs if d['fecha'] and
                      d['fecha'].year == y and d['fecha'].month == m)
            kg  = sum(d['peso'] for d in docs if d['fecha'] and
                      d['fecha'].year == y and d['fecha'].month == m)
            meses_labels.append(MESES_ES[m - 1])
            viajes_por_mes.append(cnt)
            kg_por_mes.append(kg)

        # Rutas frecuentes
        rutas = Counter(f"{d['origen']} → {d['destino']}" for d in docs
                        if d['origen'] and d['destino'])
        top_rutas = rutas.most_common(6)

        # Empresas
        top_empresas = empresa_cnt.most_common(6)

        # Vehículos
        vehiculo_cnt = Counter(d['matricula'] for d in docs if d['matricula'] != '—')
        top_vehiculos = vehiculo_cnt.most_common(5)

        # Cargas
        carga_cnt  = Counter(d['carga'] for d in docs if d['carga'] != '—')
        carga_peso = defaultdict(float)
        for d in docs:
            carga_peso[d['carga']] += d['peso']
        top_cargas = carga_cnt.most_common(6)

        # Albaranes
        con_albaran = sum(1 for d in docs if d['albaran'])
        sin_alb     = total_docs - con_albaran

        # Mapa — contadores de orígenes y destinos por lugar
        origen_cnt  = Counter(d['origen']  for d in docs if d['origen']  and d['origen']  != '—')
        destino_cnt = Counter(d['destino'] for d in docs if d['destino'] and d['destino'] != '—')

        # ── helpers UI ────────────────────────────────────────
        def _card(content, padding=16):
            return ft.Container(
                border_radius=16,
                bgcolor=card_bg,
                border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.BLACK)),
                shadow=ft.BoxShadow(blur_radius=12,
                                    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                                    offset=ft.Offset(0, 3)),
                padding=padding,
                content=content,
            )

        def _section_title(text, icon):
            return ft.Row([
                ft.Icon(icon, color=accent, size=18),
                ft.Text(text, size=15, weight=ft.FontWeight.W_700, color=accent),
            ], spacing=8)

        def _kpi(label, value, sub, sub_color):
            return ft.Container(
                expand=1,
                border_radius=14,
                bgcolor=card_bg,
                border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.BLACK)),
                shadow=ft.BoxShadow(blur_radius=10,
                                    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                                    offset=ft.Offset(0, 3)),
                padding=ft.padding.symmetric(horizontal=14, vertical=12),
                content=ft.Column(spacing=2, controls=[
                    ft.Text(label, size=10, color=text_dim),
                    ft.Text(str(value), size=22, weight=ft.FontWeight.W_800),
                    ft.Text(sub, size=11, color=sub_color, weight=ft.FontWeight.W_500),
                ]),
            )

        def _bar_chart(values, labels, color, max_val=None, unit=""):
            if not any(values):
                return ft.Text("Sin datos aún", size=12, color=ft.Colors.GREY_500, italic=True)
            top = max(values) or 1
            groups = []
            for i, v in enumerate(values):
                groups.append(ft.BarChartGroup(
                    x=i,
                    bar_rods=[ft.BarChartRod(
                        from_y=0, to_y=v,
                        width=28,
                        color=ft.Colors.with_opacity(0.85 if v == max(values) else 0.55, accent),
                        border_radius=ft.border_radius.only(top_left=6, top_right=6),
                        tooltip=f"{v}{unit}",
                    )],
                ))
            axis_labels = [
                ft.ChartAxisLabel(value=i, label=ft.Text(l, size=9, color=text_dim))
                for i, l in enumerate(labels)
            ]
            return ft.BarChart(
                bar_groups=groups,
                expand=True,
                height=160,
                max_y=top * 1.25,
                bottom_axis=ft.ChartAxis(labels=axis_labels, labels_size=24),
                left_axis=ft.ChartAxis(labels_size=32),
                horizontal_grid_lines=ft.ChartGridLines(
                    interval=max(1, top // 4),
                    color=ft.Colors.with_opacity(0.08, ft.Colors.GREY_500),
                    dash_pattern=[4, 4],
                ),
                border=ft.Border(
                    bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.1, ft.Colors.GREY_500))
                ),
            )

        def _ranking_row(idx, label, value, total, unit="", color=None):
            pct = value / total if total > 0 else 0
            bar_color = color or accent
            return ft.Column(spacing=4, controls=[
                ft.Row([
                    ft.Container(
                        width=22, height=22, border_radius=11,
                        bgcolor=ft.Colors.with_opacity(0.15, accent),
                        alignment=ft.alignment.center,
                        content=ft.Text(str(idx), size=10, weight=ft.FontWeight.W_700, color=accent),
                    ),
                    ft.Text(label, size=12, expand=True,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{value}{unit}", size=12,
                            weight=ft.FontWeight.W_700, color=accent),
                ], spacing=8),
                ft.Container(
                    height=5, border_radius=4,
                    bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.GREY_500),
                    content=ft.Container(
                        width=float('inf'),
                        height=5,
                        border_radius=4,
                        bgcolor=ft.Colors.with_opacity(0.7, bar_color),
                        alignment=ft.alignment.center_left,
                        padding=ft.padding.only(right=(1 - pct) * 100),  # no es ideal pero funciona
                    ),
                ),
            ])

        def _pct_bar(label, value, total, color):
            pct = value / total * 100 if total > 0 else 0
            return ft.Column(spacing=6, controls=[
                ft.Row([
                    ft.Text(label, size=12, expand=True),
                    ft.Text(f"{value}  ({pct:.0f}%)", size=12,
                            weight=ft.FontWeight.W_600, color=color),
                ]),
                ft.Stack([
                    ft.Container(height=8, border_radius=4,
                                 bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.GREY_500)),
                    ft.Container(height=8, border_radius=4, bgcolor=color,
                                 width=pct * 2.8),  # aproximado
                ]),
            ])

        # ── sección sin datos ──────────────────────────────────
        if total_docs == 0:
            return ft.View(
                route='/stats',
                padding=0,
                bgcolor=bg,
                appbar=ft.AppBar(
                    title=ft.Text("Estadísticas", weight=ft.FontWeight.W_600),
                    center_title=True,
                    bgcolor=ab_color,
                    automatically_imply_leading=False,
                    actions=[self.theme_button],
                    toolbar_height=56,
                ),
                bottom_appbar=build_bottom_nav(self.page, '/stats', ab_color),
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=12,
                            controls=[
                                ft.Icon(ft.Icons.BAR_CHART_ROUNDED, size=72, color=ft.Colors.GREY_300),
                                ft.Text("Sin datos aún", size=18, color=ft.Colors.GREY_500),
                                ft.Text("Crea tu primer documento de control\npara ver las estadísticas.",
                                        size=13, color=ft.Colors.GREY_400,
                                        text_align=ft.TextAlign.CENTER),
                            ],
                        ),
                    )
                ],
            )

        # ── construir UI ───────────────────────────────────────
        header = ft.Container(
            padding=ft.padding.only(top=48, bottom=20, left=20, right=20),
            bgcolor=ab_color,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Estadísticas", size=20,
                            weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                    self.theme_button,
                ],
            ),
        )

        # KPIs
        kpi_row1 = ft.Row(spacing=10, controls=[
            _kpi("Viajes este mes", viajes_mes,
                 _delta_str(viajes_mes, viajes_ant),
                 _delta_color(viajes_mes, viajes_ant)),
            _kpi("Kg este mes", f"{kg_mes:,.0f}",
                 _delta_str(kg_mes, kg_ant),
                 _delta_color(kg_mes, kg_ant)),
        ])
        kpi_row2 = ft.Row(spacing=10, controls=[
            _kpi("Total documentos", total_docs,
                 f"{viajes_mes} este mes", ft.Colors.GREY_500),
            _kpi("Sin albarán", sin_albaran,
                 "pendientes" if sin_albaran > 0 else "✓ todos adjuntos",
                 ft.Colors.ORANGE_600 if sin_albaran > 0 else ft.Colors.GREEN_600),
        ])

        # Gráfica viajes por mes
        chart_viajes = _card(
            ft.Column(spacing=12, controls=[
                _section_title("Viajes por mes", ft.Icons.CALENDAR_MONTH_ROUNDED),
                _bar_chart(viajes_por_mes, meses_labels, accent, unit=" viajes"),
            ]),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )

        # Gráfica kg por mes
        chart_kg = _card(
            ft.Column(spacing=12, controls=[
                _section_title("Toneladas por mes", ft.Icons.SCALE_ROUNDED),
                _bar_chart(
                    [round(k / 1000, 1) for k in kg_por_mes],
                    meses_labels, accent, unit=" t",
                ),
            ]),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )

        # Rutas frecuentes
        ruta_max = top_rutas[0][1] if top_rutas else 1
        rutas_controls = [_section_title("Rutas más frecuentes", ft.Icons.ROUTE)]
        for i, (ruta, cnt) in enumerate(top_rutas, 1):
            rutas_controls.append(_ranking_row(i, ruta, cnt, ruta_max, " viajes"))
            if i < len(top_rutas):
                rutas_controls.append(ft.Divider(height=1, color=ft.Colors.with_opacity(0.06, ft.Colors.GREY_500)))
        card_rutas = _card(ft.Column(spacing=10, controls=rutas_controls),
                           padding=ft.padding.symmetric(horizontal=16, vertical=14))

        # Empresas
        emp_max = top_empresas[0][1] if top_empresas else 1
        emp_controls = [_section_title("Empresas contratantes", ft.Icons.APARTMENT_ROUNDED)]
        for i, (emp, cnt) in enumerate(top_empresas, 1):
            emp_controls.append(_ranking_row(i, emp, cnt, emp_max, " viajes"))
            if i < len(top_empresas):
                emp_controls.append(ft.Divider(height=1, color=ft.Colors.with_opacity(0.06, ft.Colors.GREY_500)))
        card_empresas = _card(ft.Column(spacing=10, controls=emp_controls),
                              padding=ft.padding.symmetric(horizontal=16, vertical=14))

        # Vehículos
        veh_max = top_vehiculos[0][1] if top_vehiculos else 1
        veh_controls = [_section_title("Uso por vehículo", ft.Icons.DIRECTIONS_CAR_ROUNDED)]
        for i, (mat, cnt) in enumerate(top_vehiculos, 1):
            veh_controls.append(_ranking_row(i, mat, cnt, veh_max, " viajes"))
            if i < len(top_vehiculos):
                veh_controls.append(ft.Divider(height=1, color=ft.Colors.with_opacity(0.06, ft.Colors.GREY_500)))
        card_vehiculos = _card(ft.Column(spacing=10, controls=veh_controls),
                               padding=ft.padding.symmetric(horizontal=16, vertical=14))

        # Mercancías
        carga_max = top_cargas[0][1] if top_cargas else 1
        carga_controls = [_section_title("Tipos de mercancía", ft.Icons.INVENTORY_2_ROUNDED)]
        for i, (tipo, cnt) in enumerate(top_cargas, 1):
            peso_total = carga_peso.get(tipo, 0)
            label = f"{tipo}  ·  {peso_total:,.0f} kg"
            carga_controls.append(_ranking_row(i, label, cnt, carga_max, " viajes"))
            if i < len(top_cargas):
                carga_controls.append(ft.Divider(height=1, color=ft.Colors.with_opacity(0.06, ft.Colors.GREY_500)))
        card_cargas = _card(ft.Column(spacing=10, controls=carga_controls),
                            padding=ft.padding.symmetric(horizontal=16, vertical=14))

        # Albaranes
        card_albaranes = _card(
            ft.Column(spacing=12, controls=[
                _section_title("Estado de albaranes", ft.Icons.RECEIPT_LONG_ROUNDED),
                ft.Text(f"Total documentos: {total_docs}", size=12, color=text_dim),
                _pct_bar("Con albarán adjunto", con_albaran, total_docs, ft.Colors.GREEN_600),
                _pct_bar("Sin albarán (pendiente)", sin_alb, total_docs, ft.Colors.ORANGE_500),
                ft.Container(height=4),
                ft.Container(
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.08,
                        ft.Colors.ORANGE_500 if sin_alb > 0 else ft.Colors.GREEN_500),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    content=ft.Row([
                        ft.Icon(
                            ft.Icons.WARNING_AMBER_ROUNDED if sin_alb > 0 else ft.Icons.CHECK_CIRCLE_ROUNDED,
                            size=16,
                            color=ft.Colors.ORANGE_600 if sin_alb > 0 else ft.Colors.GREEN_600,
                        ),
                        ft.Text(
                            f"Tienes {sin_alb} documento{'s' if sin_alb != 1 else ''} sin albarán sellado."
                            if sin_alb > 0 else "Todos los albaranes están adjuntos.",
                            size=12,
                            color=ft.Colors.ORANGE_700 if sin_alb > 0 else ft.Colors.GREEN_700,
                        ),
                    ], spacing=8),
                ),
            ]),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )

        # Empresa top destacada
        card_top_empresa = _card(
            ft.Row([
                ft.Container(
                    width=44, height=44, border_radius=14,
                    bgcolor=ft.Colors.with_opacity(0.12, accent),
                    alignment=ft.alignment.center,
                    content=ft.Icon(ft.Icons.STAR_ROUNDED, color=accent, size=24),
                ),
                ft.Column(spacing=2, expand=True, controls=[
                    ft.Text("Empresa más activa", size=10, color=text_dim),
                    ft.Text(empresa_top, size=14, weight=ft.FontWeight.W_700,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{empresa_cnt.get(empresa_top, 0)} viajes en total",
                            size=11, color=ft.Colors.GREY_500),
                ]),
            ], spacing=14),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

        # ── tarjeta mapa ───────────────────────────────────────
        map_btn_text = ft.Text("Abrir mapa interactivo", size=13,
                               weight=ft.FontWeight.W_600, color=ft.Colors.BLACK)
        map_btn_icon = ft.Icon(ft.Icons.MAP_ROUNDED, color=ft.Colors.BLACK, size=18)
        map_btn_prog = ft.ProgressRing(width=16, height=16, stroke_width=2,
                                       color=ft.Colors.BLACK, visible=False)
        map_status   = ft.Text("", size=11, color=ft.Colors.GREY_500, italic=True, visible=False)

        def _abrir_mapa(e):
            map_btn_text.value = "Generando mapa…"
            map_btn_icon.visible = False
            map_btn_prog.visible = True
            map_status.value = "Geocodificando ubicaciones (puede tardar unos segundos)…"
            map_status.visible = True
            self.page.update()

            def _worker():
                try:
                    html_path = generate_map_html(
                        origins=dict(origen_cnt),
                        destinations=dict(destino_cnt),
                        output_path="assets/map_actividad.html",
                        accent=accent,
                    )

                    is_web = getattr(self.page, 'web', False)
                    if is_web:
                        # 1. Render pone RENDER_EXTERNAL_URL automáticamente
                        import os as _os
                        base = _os.environ.get('RENDER_EXTERNAL_URL', '').rstrip('/')
                        # 2. Si no, intentar extraerlo de page.url
                        if not base:
                            try:
                                from urllib.parse import urlparse
                                page_url = getattr(self.page, 'url', '') or ''
                                if page_url:
                                    p = urlparse(page_url)
                                    if p.netloc:
                                        base = f"{p.scheme}://{p.netloc}"
                            except Exception:
                                pass
                        map_url = f"{base}/assets/map_actividad.html" if base else "/assets/map_actividad.html"
                        self.page.launch_url(map_url)
                    else:
                        open_map(html_path)

                    map_status.value = "✅ Mapa abierto en el navegador"
                    map_status.color = ft.Colors.GREEN_600
                except Exception as ex:
                    map_status.value = f"❌ Error: {ex}"
                    map_status.color = ft.Colors.ERROR
                finally:
                    map_btn_text.value = "Abrir mapa interactivo"
                    map_btn_icon.visible = True
                    map_btn_prog.visible = False
                    self.page.update()

            threading.Thread(target=_worker, daemon=True).start()

        total_lugares = len(set(origen_cnt) | set(destino_cnt))
        card_mapa = _card(
            ft.Column(spacing=12, controls=[
                _section_title("Mapa de actividad", ft.Icons.MAP_ROUNDED),
                ft.Text(
                    f"Se han detectado {total_lugares} ubicación(es) distintas "
                    f"entre orígenes y destinos de tus {total_docs} documento(s).",
                    size=12, color=text_dim,
                ),
                ft.Container(
                    border_radius=12,
                    bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.GREY_500),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    content=ft.Column(spacing=4, controls=[
                        ft.Text("Lugares más frecuentes:", size=11,
                                color=text_dim, weight=ft.FontWeight.W_600),
                        *[
                            ft.Row([
                                ft.Icon(ft.Icons.LOCATION_ON_ROUNDED,
                                        color=accent, size=13),
                                ft.Text(lugar, size=12, expand=True,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(f"{cnt} v.", size=11,
                                        color=ft.Colors.GREY_500),
                            ], spacing=6)
                            for lugar, cnt in (origen_cnt + destino_cnt).most_common(5)
                        ],
                    ]),
                ),
                ft.Container(
                    border_radius=12,
                    bgcolor=accent,
                    on_click=_abrir_mapa,
                    ink=True,
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                        controls=[map_btn_prog, map_btn_icon, map_btn_text],
                    ),
                ),
                map_status,
            ]),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )

        body = ft.Container(
            expand=True,
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            bgcolor=bg,
            padding=ft.padding.only(left=16, right=16, top=20, bottom=90),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=14,
                controls=[
                    kpi_row1,
                    kpi_row2,
                    card_top_empresa,
                    card_mapa,
                    chart_viajes,
                    chart_kg,
                    card_rutas,
                    card_empresas,
                    card_vehiculos,
                    card_cargas,
                    card_albaranes,
                ],
            ),
        )

        return ft.View(
            route='/stats',
            padding=0,
            bgcolor=bg,
            bottom_appbar=build_bottom_nav(self.page, '/stats', ab_color),
            controls=[
                ft.Column(spacing=0, expand=True, controls=[header, body]),
            ],
        )
