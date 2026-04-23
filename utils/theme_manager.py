"""
Gestor de temas visuales para TransControl.
Define 4 paletas y guarda/carga la selección en config/theme.json.
"""

import json
import os

CONFIG_PATH = "config/theme.json"

THEMES = [
    {
        "id": 0,
        "name": "Día",
        "desc": "Fondo blanco · Verde · Modo claro",
        "seed": "#22C55E",
        "mode": "light",
        "appbar_color": "#16A34A",
        "nav_color": "#16A34A",
        "accent": "#16A34A",
        "bg": "#FFFFFF",
        "card": "#F4F4F5",
        "preview_colors": ["#16A34A", "#22C55E", "#FFFFFF", "#F4F4F5"],
    },
    {
        "id": 1,
        "name": "Noche",
        "desc": "Fondo negro · Lima neón · Modo oscuro",
        "seed": "#A3E635",
        "mode": "dark",
        "appbar_color": "#0D0D0D",
        "nav_color": "#0D0D0D",
        "accent": "#A3E635",
        "bg": "#0D0D0D",
        "card": "#1C1E24",
        "preview_colors": ["#0D0D0D", "#A3E635", "#1C1E24", "#252830"],
    },
]


def load_theme_id() -> int:
    try:
        with open(CONFIG_PATH, "r") as f:
            return int(json.load(f).get("theme_id", 1)) % len(THEMES)
    except Exception:
        return 1  # default: Noche


def save_theme_id(theme_id: int):
    os.makedirs("config", exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"theme_id": theme_id}, f)


def get_theme(theme_id: int) -> dict:
    return THEMES[theme_id % len(THEMES)]


def get_current_theme() -> dict:
    return get_theme(load_theme_id())
