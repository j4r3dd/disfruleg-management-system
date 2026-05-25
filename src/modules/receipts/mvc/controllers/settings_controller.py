# -*- coding: utf-8 -*-
"""
Settings Controller
Handles application settings and configuration
"""

from src.modules.receipts.mvc.controllers.base_controller import BaseController
from src.modules.receipts.mvc.models.receipt_model import ReciboModel
from src.modules.receipts.mvc.views.receipt_view import ReciboView
from src.modules.receipts.models.cart_model import CartModel
from src.modules.receipts.components.user_preferences import get_preferences
from src.modules.receipts.exceptions import (
    ConfigurationError,
    MissingConfigurationError,
    InvalidConfigurationError,
)


class SettingsController(BaseController):
    """
    Controller for settings and configuration

    Responsibilities:
    - Handle export path configuration
    - Manage user preferences
    - Update application settings
    """

    def __init__(self, view: ReciboView, model: ReciboModel, cart_model: CartModel):
        super().__init__(view, model, cart_model)

    # ==================== EVENT HANDLERS ====================

    def on_configurar_rutas(self):
        """
        Handle '⚙️' settings button click - Configure export paths

        Workflow:
        1. Show dialog with options to configure PDF and Excel paths
        2. Allow user to select new directories
        3. Save preferences
        """
        try:
            self.log_info("Configurando rutas de exportación")

            # Ask user if they want to configure paths
            respuesta = self.confirm(
                "Configurar Rutas de Exportación",
                "¿Desea cambiar la ruta donde se guardan los archivos PDF y Excel?\n\n" +
                "Se abrirán dos diálogos para seleccionar las carpetas."
            )

            if not respuesta:
                return

            prefs = get_preferences()

            # Configure PDF path
            pdf_path = prefs.prompt_for_export_path('pdf', parent=self.view.root)
            if pdf_path:
                self.log_success(f"Ruta PDF configurada: {pdf_path}")
            else:
                self.log_warning("Configuración de PDF cancelada")

            # Configure Excel path
            excel_path = prefs.prompt_for_export_path('excel', parent=self.view.root)
            if excel_path:
                self.log_success(f"Ruta Excel configurada: {excel_path}")
            else:
                self.log_warning("Configuración de Excel cancelada")

            # Show confirmation
            if pdf_path or excel_path:
                mensaje = "Rutas configuradas:\n\n"
                if pdf_path:
                    mensaje += f"📄 PDF: {pdf_path}\n"
                if excel_path:
                    mensaje += f"📊 Excel: {excel_path}\n"

                self.show_success(
                    "Rutas Configuradas",
                    mensaje
                )
            else:
                self.show_info(
                    "Sin Cambios",
                    "No se realizaron cambios en las rutas de exportación."
                )

        except ConfigurationError as e:
            # Configuration error
            self.show_error(
                "Error de Configuración",
                f"No se pudieron configurar las rutas de exportación"
            )
            self.log_error(f"Configuration error: {e}")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("configurar rutas", e)
