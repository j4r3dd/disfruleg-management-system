# -*- coding: utf-8 -*-
"""
Responsive Layout Manager - Sistema centralizado para hacer ventanas responsive
Uso: Simplemente hereda de ResponsiveWindow o usa el mixin
ACTUALIZADO: Con limpieza adecuada de recursos
"""

import customtkinter as ctk
from typing import Tuple, Optional, Literal
import logging

logger = logging.getLogger(__name__)


class ResponsiveConfig:
    """Configuración responsive por tipo de ventana"""
    
    PRESETS = {
        'fullscreen': {
            'width_ratio': 0.95,
            'height_ratio': 0.90,
            'max_width': 1920,
            'max_height': 1080,
            'min_width': 1200,
            'min_height': 800
        },
        'large': {
            'width_ratio': 0.90,
            'height_ratio': 0.85,
            'max_width': 1500,
            'max_height': 950,
            'min_width': 1000,
            'min_height': 700
        },
        'medium': {
            'width_ratio': 0.75,
            'height_ratio': 0.75,
            'max_width': 1200,
            'max_height': 800,
            'min_width': 800,
            'min_height': 600
        },
        'small': {
            'width_ratio': 0.60,
            'height_ratio': 0.65,
            'max_width': 900,
            'max_height': 700,
            'min_width': 600,
            'min_height': 500
        },
        'dialog': {
            'width_ratio': 0.40,
            'height_ratio': 0.50,
            'max_width': 650,
            'max_height': 700,
            'min_width': 400,
            'min_height': 300
        }
    }
    
    @classmethod
    def get_preset(cls, preset_name: str) -> dict:
        """Obtener preset de configuración"""
        return cls.PRESETS.get(preset_name, cls.PRESETS['medium'])


class ResponsiveMixin:
    """
    Mixin para agregar funcionalidad responsive a cualquier ventana CTk
    
    Uso:
        class MiVentana(ResponsiveMixin, ctk.CTkToplevel):
            def __init__(self, parent):
                super().__init__(parent)
                self.make_responsive('large')
    """
    
    def __init__(self, *args, **kwargs):
        """Inicializar mixin con tracking de callbacks"""
        super().__init__(*args, **kwargs)
        # Inicializar lista de callbacks si no existe
        if not hasattr(self, '_responsive_after_ids'):
            self._responsive_after_ids = []
    
    def make_responsive(
        self,
        preset: Literal['fullscreen', 'large', 'medium', 'small', 'dialog'] = 'medium',
        custom_config: Optional[dict] = None,
        center: bool = True,
        force_visible: bool = True
    ):
        """
        Hacer la ventana responsive
        
        Args:
            preset: Preset de configuración
            custom_config: Configuración personalizada
            center: Centrar ventana en pantalla
            force_visible: Forzar visibilidad
        """
        try:
            # Inicializar lista de callbacks si no existe
            if not hasattr(self, '_responsive_after_ids'):
                self._responsive_after_ids = []
            
            # Obtener configuración
            config = ResponsiveConfig.get_preset(preset)
            if custom_config:
                config.update(custom_config)
            
            # Calcular dimensiones
            width, height, x, y = self._calculate_responsive_dimensions(config, center)
            
            # Aplicar geometría
            self.geometry(f"{width}x{height}+{x}+{y}")
            
            # Aplicar tamaños mínimos
            self.minsize(config['min_width'], config['min_height'])
            
            # Forzar visibilidad si se solicita
            if force_visible:
                self._force_visibility()
            
            logger.info(f"✅ Ventana responsive: {width}x{height} (preset: {preset})")
            
        except Exception as e:
            logger.error(f"❌ Error en make_responsive: {e}")
    
    def _calculate_responsive_dimensions(self, config: dict, center: bool) -> Tuple[int, int, int, int]:
        """Calcular dimensiones responsive"""
        # Obtener tamaño de pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calcular dimensiones basadas en ratios
        width = int(screen_width * config['width_ratio'])
        height = int(screen_height * config['height_ratio'])
        
        # Aplicar límites máximos
        width = min(width, config['max_width'])
        height = min(height, config['max_height'])
        
        # Aplicar límites mínimos
        width = max(width, config['min_width'])
        height = max(height, config['min_height'])
        
        # Calcular posición
        if center:
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
        else:
            x = y = 0
        
        return width, height, x, y
    
    def _force_visibility(self):
        """Forzar visibilidad de la ventana"""
        try:
            self.withdraw()
            self.deiconify()
            self.attributes('-topmost', True)
            self.update()
            self.attributes('-topmost', False)
            self.lift()
            self.focus_force()
        except Exception as e:
            logger.error(f"Error en _force_visibility: {e}")
    
    def _cleanup_responsive(self):
        """Limpiar recursos del mixin responsive"""
        try:
            # Cancelar todos los callbacks registrados
            if hasattr(self, '_responsive_after_ids'):
                for after_id in self._responsive_after_ids:
                    try:
                        self.after_cancel(after_id)
                    except:
                        pass
                self._responsive_after_ids.clear()
        except Exception as e:
            logger.error(f"Error en _cleanup_responsive: {e}")


class ResponsiveWindow(ResponsiveMixin, ctk.CTkToplevel):
    """
    Ventana base responsive - Úsala directamente o hereda de ella
    """
    
    def __init__(
        self,
        parent,
        preset: Literal['fullscreen', 'large', 'medium', 'small', 'dialog'] = 'medium',
        title: str = "Ventana",
        custom_config: Optional[dict] = None,
        fg_color: str = "#0A0E27",
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.title(title)
        self.configure(fg_color=fg_color)
        
        # Aplicar responsive
        self.make_responsive(preset=preset, custom_config=custom_config)
        
        # Configurar protocolo de cierre para limpieza
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_close(self):
        """Manejar cierre de ventana con limpieza"""
        try:
            self._cleanup_responsive()
            self.destroy()
        except:
            pass