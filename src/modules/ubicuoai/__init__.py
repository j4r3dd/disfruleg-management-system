# -*- coding: utf-8 -*-
"""
UbicuoAI Module
Sistema Inteligente de Procesamiento de Pedidos

Clean Architecture implementation with proper dependency injection
"""

from .ubicuoai_manager import (
    ubicuoai_manager,
    get_ubicuoai_service,
    get_product_service,
    initialize_ubicuoai,
    is_ubicuoai_initialized
)

__all__ = [
    'ubicuoai_manager',
    'get_ubicuoai_service',
    'initialize_ubicuoai',
    'is_ubicuoai_initialized',
    'open_ubicuoai_window'
]

__version__ = '2.0.0'


def open_ubicuoai_window(parent, user_data=None):
    """
    Open UbicuoAI window
    Handles initialization and window creation

    Args:
        parent: Parent window (Tkinter/CTk window)
        user_data: User data dictionary with username, rol, etc.

    Returns:
        UbicuoAI window instance
    """
    from tkinter import messagebox
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Initialize if not already done
        if not is_ubicuoai_initialized():
            init_result = initialize_ubicuoai()

            if not init_result.get('success'):
                error_msg = f"No se pudo inicializar UbicuoAI:\n{init_result.get('message')}"
                logger.error(f"❌ {error_msg}")
                messagebox.showerror("Error de Inicialización", error_msg)
                return None

            # Log initialization info to console instead of showing messagebox
            print(f"✅ UbicuoAI Inicializado:")
            print(f"   ✓ {init_result['products_loaded']} productos cargados")
            print(f"   ✓ {init_result['corrections_loaded']} correcciones aprendidas")

        # Get services
        service = get_ubicuoai_service()
        if not service:
            raise RuntimeError("No se pudo obtener el servicio UbicuoAI")

        # Get product service with logging
        product_service = None
        try:
            product_service = get_product_service()
            print(f"✓ Product service loaded: {product_service}")
        except Exception as e:
            print(f"⚠️ Advertencia: No se pudo cargar product service: {e}")
            logger.warning(f"Product service no disponible: {e}")

        # Default user_data if not provided
        if user_data is None:
            user_data = {
                'username': 'test',
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin'
            }

        # Import controller
        from .ui.controllers.ubicuoai_controller import UbicuoAIController

        # Create controller
        controller = UbicuoAIController(
            service=service,
            on_status_update=lambda msg, status="info": None,
            on_stats_update=lambda total, matched: None,
            product_service=product_service,
            user_data=user_data
        )

        logger.info(f"✓ Controller created successfully")

        # Import and create window
        from .ui.ubicuoai_window import UbicuoAIWindow

        try:
            window = UbicuoAIWindow(parent, controller)

            if window is None:
                raise RuntimeError("UbicuoAIWindow retornó None")

            # Update controller callbacks to use window methods
            if hasattr(window, 'update_status'):
                controller.on_status_update = window.update_status
            if hasattr(window, 'update_stats'):
                controller.on_stats_update = window.update_stats

            logger.info("✅ UbicuoAI Window created and returned successfully")
            return window

        except Exception as e:
            logger.error(f"❌ Error creating UbicuoAIWindow: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Error de Ventana",
                f"Error al crear la ventana de UbicuoAI:\n{str(e)}"
            )
            return None

    except RuntimeError as e:
        error_msg = f"Error al abrir UbicuoAI:\n{str(e)}\n\nAsegúrate de haber iniciado sesión primero."
        logger.error(f"❌ {error_msg}")
        messagebox.showerror("Error", error_msg)
        return None

    except Exception as e:
        error_msg = f"Error inesperado al abrir UbicuoAI:\n{str(e)}"
        logger.error(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Error Inesperado", error_msg)
        return None
