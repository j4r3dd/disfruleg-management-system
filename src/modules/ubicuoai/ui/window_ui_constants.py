# -*- coding: utf-8 -*-
"""
window_ui_constants.py - Constantes de UI (Colores, Fuentes, Dimensiones)
Define toda la configuración visual de la ventana UbicuoAI
"""

# Paleta de colores moderna para AI
COLORS = {
    'ai_blue': '#00D4FF',
    'ai_purple': '#8B5CF6',
    'ai_green': '#10B981',
    'ai_orange': '#F59E0B',
    'ai_red': '#EF4444',
    'bg_primary': '#0A0E27',
    'bg_secondary': '#151933',
    'bg_card': '#1E2139',
    'text_primary': '#FFFFFF',
    'text_secondary': '#94A3B8',
    'border': '#2D3250',
}

# Tipografías
FONTS = {
    'title': ('Arial', 32, 'bold'),
    'heading': ('Arial', 20, 'bold'),
    'subheading': ('Arial', 16, 'normal'),
    'body': ('Arial', 13),
    'mono': ('Courier', 12),
    'small': ('Arial', 11),
}

# Dimensiones de ventana
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Textos por defecto
DEFAULT_TEXT_AREA = "📝 Pega tu pedido (producto, cantidad y unidad)"
INITIAL_STATUS = "💡 Pega el pedido y presiona 'Procesar Pedido'"
PLACEHOLDER_TEXT = "📝 Pega un pedido para ver resultados"
