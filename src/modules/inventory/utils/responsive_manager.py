# -*- coding: utf-8 -*-
"""
Responsive Window Manager
Sistema de ventanas responsive con presets predefinidos
"""

import customtkinter as ctk
from typing import Literal, Optional, Dict, Tuple


# ============================================================================
# PRESETS DE VENTANAS
# ============================================================================

WINDOW_PRESETS: Dict[str, Dict[str, any]] = {
    'fullscreen': {
        'width_ratio': 1.0,
        'height_ratio': 1.0,
        'min_width': 1024,
        'min_height': 768,
        'resizable': True,
        'center': True
    },
    'large': {
        'width': 1400,
        'height': 900,
        'width_ratio': 0.85,
        'height_ratio': 0.85,
        'min_width': 1200,
        'min_height': 800,
        'resizable': True,
        'center': True
    },
    'medium': {
        'width': 1200,
        'height': 800,
        'width_ratio': 0.75,
        'height_ratio': 0.75,
        'min_width': 900,
        'min_height': 600,
        'resizable': True,
        'center': True
    },
    'small': {
        'width': 800,
        'height': 600,
        'width_ratio': 0.55,
        'height_ratio': 0.60,
        'min_width': 600,
        'min_height': 400,
        'resizable': True,
        'center': True
    },
    'dialog': {
        'width': 500,
        'height': 400,
        'width_ratio': None,  # Fixed size
        'height_ratio': None,
        'min_width': 400,
        'min_height': 300,
        'resizable': False,
        'center': True
    }
}


# ============================================================================
# RESPONSIVE MIXIN
# ============================================================================

class ResponsiveMixin:
    """
    Mixin para agregar funcionalidad responsive a cualquier ventana
    
    Uso con herencia múltiple:
        class MyWindow(ResponsiveMixin, ctk.CTkToplevel):
            def __init__(self, parent):
                super().__init__(parent)
                self.make_responsive('medium')
    """
    
    def make_responsive(
        self,
        preset: Literal['fullscreen', 'large', 'medium', 'small', 'dialog'] = 'medium',
        custom_width: Optional[int] = None,
        custom_height: Optional[int] = None,
        force_visible: bool = True
    ):
        """
        Aplicar configuración responsive a la ventana
        
        Args:
            preset: Preset predefinido
            custom_width: Ancho personalizado (sobreescribe preset)
            custom_height: Alto personalizado (sobreescribe preset)
            force_visible: Si True, fuerza la ventana al frente
        """
        # Obtener configuración del preset
        config = WINDOW_PRESETS.get(preset, WINDOW_PRESETS['medium']).copy()
        
        # Obtener dimensiones de la pantalla
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calcular dimensiones de la ventana
        if custom_width and custom_height:
            # Usar dimensiones personalizadas
            width = custom_width
            height = custom_height
        elif config.get('width_ratio') and config.get('height_ratio'):
            # Usar ratios de pantalla
            width = int(screen_width * config['width_ratio'])
            height = int(screen_height * config['height_ratio'])
        else:
            # Usar dimensiones fijas del preset
            width = config.get('width', 800)
            height = config.get('height', 600)
        
        # Aplicar dimensiones mínimas
        min_width = config.get('min_width', 600)
        min_height = config.get('min_height', 400)
        
        width = max(width, min_width)
        height = max(height, min_height)
        
        # Centrar ventana si está configurado
        if config.get('center', True):
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.geometry(f"{width}x{height}")
        
        # Configurar si es redimensionable
        if hasattr(self, 'resizable'):
            resizable = config.get('resizable', True)
            self.resizable(resizable, resizable)
        
        # Configurar tamaño mínimo
        if hasattr(self, 'minsize'):
            self.minsize(min_width, min_height)
        
        # Force visible - traer ventana al frente
        if force_visible:
            self.attributes('-topmost', True)
            self.lift()
            self.focus_force()
            # Quitar topmost después de 100ms para permitir otras ventanas
            self.after(100, lambda: self.attributes('-topmost', False))


# ============================================================================
# RESPONSIVE WINDOW (Clase completa)
# ============================================================================

class ResponsiveWindow(ctk.CTkToplevel):
    """
    Ventana CTkToplevel con capacidades responsive integradas
    
    Uso directo:
        window = ResponsiveWindow(parent, preset='large', title="Mi Ventana")
    """
    
    def __init__(
        self,
        parent,
        preset: Literal['fullscreen', 'large', 'medium', 'small', 'dialog'] = 'medium',
        title: str = "Ventana",
        custom_width: Optional[int] = None,
        custom_height: Optional[int] = None,
        modal: bool = False,
        **kwargs
    ):
        """
        Crear ventana responsive
        
        Args:
            parent: Ventana padre
            preset: Preset predefinido
            title: Título de la ventana
            custom_width: Ancho personalizado
            custom_height: Alto personalizado
            modal: Si la ventana debe ser modal
            **kwargs: Argumentos adicionales para CTkToplevel
        """
        super().__init__(parent, **kwargs)
        
        # Configurar título
        self.title(title)
        
        # Aplicar responsive
        self._apply_responsive(preset, custom_width, custom_height)
        
        # Configurar modal si es necesario
        if modal:
            self.transient(parent)
            self.grab_set()
    
    def _apply_responsive(
        self,
        preset: str,
        custom_width: Optional[int],
        custom_height: Optional[int]
    ):
        """Aplicar configuración responsive"""
        # Obtener configuración del preset
        config = WINDOW_PRESETS.get(preset, WINDOW_PRESETS['medium']).copy()
        
        # Obtener dimensiones de la pantalla
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calcular dimensiones de la ventana
        if custom_width and custom_height:
            width = custom_width
            height = custom_height
        elif config.get('width_ratio') and config.get('height_ratio'):
            width = int(screen_width * config['width_ratio'])
            height = int(screen_height * config['height_ratio'])
        else:
            width = config.get('width', 800)
            height = config.get('height', 600)
        
        # Aplicar dimensiones mínimas
        min_width = config.get('min_width', 600)
        min_height = config.get('min_height', 400)
        
        width = max(width, min_width)
        height = max(height, min_height)
        
        # Centrar ventana
        if config.get('center', True):
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.geometry(f"{width}x{height}")
        
        # Configurar redimensionable
        resizable = config.get('resizable', True)
        self.resizable(resizable, resizable)
        
        # Configurar tamaño mínimo
        self.minsize(min_width, min_height)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_responsive_dimensions(
    preset: str = 'medium',
    screen_width: Optional[int] = None,
    screen_height: Optional[int] = None
) -> Tuple[int, int, int, int]:
    """
    Calcular dimensiones responsive sin crear ventana
    
    Args:
        preset: Nombre del preset
        screen_width: Ancho de pantalla (auto si None)
        screen_height: Alto de pantalla (auto si None)
    
    Returns:
        Tuple de (width, height, x, y)
    """
    # Obtener dimensiones de pantalla si no se proporcionan
    if screen_width is None or screen_height is None:
        root = ctk.CTk()
        root.withdraw()
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
    
    # Obtener configuración
    config = WINDOW_PRESETS.get(preset, WINDOW_PRESETS['medium'])
    
    # Calcular dimensiones
    if config.get('width_ratio') and config.get('height_ratio'):
        width = int(screen_width * config['width_ratio'])
        height = int(screen_height * config['height_ratio'])
    else:
        width = config.get('width', 800)
        height = config.get('height', 600)
    
    # Aplicar mínimos
    width = max(width, config.get('min_width', 600))
    height = max(height, config.get('min_height', 400))
    
    # Calcular posición central
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    return width, height, x, y


def apply_responsive_to_window(
    window,
    preset: str = 'medium',
    custom_width: Optional[int] = None,
    custom_height: Optional[int] = None
):
    """
    Aplicar responsive a una ventana existente
    
    Args:
        window: Ventana CTk o CTkToplevel
        preset: Preset a aplicar
        custom_width: Ancho personalizado
        custom_height: Alto personalizado
    """
    config = WINDOW_PRESETS.get(preset, WINDOW_PRESETS['medium'])
    
    # Obtener dimensiones
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calcular dimensiones
    if custom_width and custom_height:
        width = custom_width
        height = custom_height
    elif config.get('width_ratio') and config.get('height_ratio'):
        width = int(screen_width * config['width_ratio'])
        height = int(screen_height * config['height_ratio'])
    else:
        width = config.get('width', 800)
        height = config.get('height', 600)
    
    # Aplicar mínimos
    min_width = config.get('min_width', 600)
    min_height = config.get('min_height', 400)
    width = max(width, min_width)
    height = max(height, min_height)
    
    # Centrar
    if config.get('center', True):
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    else:
        window.geometry(f"{width}x{height}")
    
    # Configurar
    if hasattr(window, 'resizable'):
        resizable = config.get('resizable', True)
        window.resizable(resizable, resizable)
    
    if hasattr(window, 'minsize'):
        window.minsize(min_width, min_height)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'ResponsiveWindow',
    'ResponsiveMixin',
    'WINDOW_PRESETS',
    'get_responsive_dimensions',
    'apply_responsive_to_window'
]