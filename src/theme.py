import customtkinter as ctk
from PIL import Image
from pathlib import Path
import platform
import os

# Paleta de colores unificada para todo el proyecto
COLORS = {
    'primary': '#2D9B6C',
    'primary_hover': '#1F618D',
    'secondary': '#2C3E50',
    'accent': '#E74C3C',
    'success': '#2ECC71',
    'success_hover': '#27AE60',
    'success_green': '#27AE60',
    'error_red': '#E74C3C',
    'danger': '#E74C3C',
    'danger_hover': '#C0392B',
    'warning': '#F39C12',
    'warning_hover': '#E67E22',
    'overlay_bg_dark': 'gray14',
    'overlay_bg_light': 'gray92',
    'text_gray': 'gray',
    'text_gray60': 'gray60',
    'transparent': 'transparent',
    'info': '#3498DB',
    'info_hover': '#2980B9',
    # Additional colors for modern UI
    'surface': 'gray20',
    'card_bg': 'gray17',
    'text_primary': 'white',
    'text_secondary': 'gray70',
}

# Fuentes estándar para la app
FONTS = {
    'header': ("Arial", 20, "bold"),
    'title': ("Arial", 24, "bold"),
    'subtitle': ("Arial", 16, "bold"),
    'subheader': ("Arial", 12, "bold"),
    'body': ("Arial", 11),
    'body_bold': ("Arial", 11, "bold"),
    'button': ("Arial", 13, "bold"),
    'small': ("Arial", 9),
    'large_number': ("Arial", 28, "bold")
}

# Función para cargar iconos desde la carpeta assets
def load_icon(relative_path, size=(22, 22)):
    """
    Intenta cargar un icono y escalarlo al tamaño dado.
    Si no lo encuentra o falla, retorna None.
    """
    try:
        from src.utils.resource_path import get_resource_path
        asset_path = get_resource_path('assets') / relative_path
        if asset_path.exists():
            img = Image.open(asset_path).resize(size, Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception as e:
        print(f"[theme.py] Error cargando icono {relative_path}: {e}")
    return None

# Helper para crear un CTkEntry con estilo común
def create_entry(parent, textvariable=None, placeholder="", show=None):
    return ctk.CTkEntry(
        parent,
        textvariable=textvariable,
        placeholder_text=placeholder,
        font=FONTS['subheader'],
        corner_radius=10,
        border_width=2,
        height=40,
        show=show
    )

# Helper para crear un botón estilizado
def create_button(parent, text, command):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=45,
        font=FONTS['button'],
        corner_radius=10,
        fg_color=COLORS['primary'],
        hover_color=COLORS['primary_hover']
    )

# Helper para crear etiquetas consistentes
def create_label(parent, text, font=FONTS['body'], color=COLORS['text_gray']):
    return ctk.CTkLabel(
        parent,
        text=text,
        font=font,
        text_color=color
    )

# Helper para crear checkbox uniformes
def create_checkbox(parent, text, variable):
    return ctk.CTkCheckBox(
        parent,
        text=text,
        variable=variable,
        font=FONTS['body'],
        checkbox_width=20,
        checkbox_height=20,
        corner_radius=6
    )

# Cambiar el modo de apariencia dark/light
def toggle_theme(theme_var, icon_label=None, sun_icon=None, moon_icon=None):
    current_mode = ctk.get_appearance_mode().lower()
    new_mode = "light" if current_mode == "dark" else "dark"
    ctk.set_appearance_mode(new_mode)
    theme_var.set(new_mode)

    if icon_label:
        if new_mode == "light" and sun_icon:
            icon_label.configure(image=sun_icon)
        elif new_mode == "dark" and moon_icon:
            icon_label.configure(image=moon_icon)

# Obtener el color para overlay de fondos
def get_overlay_color(theme_mode):
    return (COLORS['overlay_bg_light'], COLORS['overlay_bg_dark']) if theme_mode == "dark" else (COLORS['overlay_bg_dark'], COLORS['overlay_bg_light'])

# Sets appearance mode and default theme colors centrally
def initialize_theme(default_mode="dark", default_color_theme="green"):
    ctk.set_appearance_mode(default_mode)
    ctk.set_default_color_theme(default_color_theme)

# Inicializar el tema al importar
initialize_theme()
