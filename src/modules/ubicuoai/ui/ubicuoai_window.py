# -*- coding: utf-8 -*-
"""
ubicuoai_window.py - Ventana Principal UbicuoAI (REFACTORIZADA Y FUNCIONAL)
Coordinador de: Eventos, Presentación, Diálogos, Ciclo de Vida
Totalmente compatible con launch_module.py
"""

import customtkinter as ctk
from typing import Optional
import logging

from src.utils.responsive_manager import ResponsiveMixin
from .window_ui_constants import COLORS, FONTS, WINDOW_WIDTH, WINDOW_HEIGHT
from .window_lifecycle_manager import WindowLifecycleManager
from .window_event_handlers import WindowEventHandlers
from .window_display_results import WindowDisplayResults
from .window_dialog_handlers import WindowDialogHandlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UbicuoAIWindow(ResponsiveMixin, ctk.CTkToplevel,
                     WindowLifecycleManager,
                     WindowEventHandlers,
                     WindowDisplayResults,
                     WindowDialogHandlers):
    """
    Ventana Principal UbicuoAI - Refactorizada
    
    Hereda de:
    - WindowLifecycleManager: Inicialización y ciclo de vida
    - WindowEventHandlers: Manejo de eventos de usuario
    - WindowDisplayResults: Presentación de resultados
    - WindowDialogHandlers: Diálogos y popups
    """

    def __init__(self, parent, controller=None):
        """Inicializa la ventana principal"""
        super().__init__(parent)
        
        try:
            logger.info("🚀 Iniciando UbicuoAI Window...")

            # Estado base
            self.controller = controller
            self._is_destroyed = False
            self.manual_overrides = {}
            self.groups_dict = {}
            self.clients_by_group = {}

            # Configurar ventana
            self.setup_window()
            
            # Crear interfaz
            self.create_ui()
            
            # Inicializar contenido
            self.after(500, self._initialize_content)
            
            # Protocolo de cierre
            self.protocol("WM_DELETE_WINDOW", self.on_closing)

            logger.info("✅ UbicuoAI Window creada exitosamente")

        except Exception as e:
            logger.error(f"❌ Error inicializando UbicuoAI Window: {e}")
            import traceback
            traceback.print_exc()
            raise
