# -*- coding: utf-8 -*-
"""
Receipt Application - MVC Integration
Entry point for the refactored receipt generator using MVC pattern with specialized controllers
"""

import sys
from pathlib import Path

# Add project root to path if needed
# Path: receipt_app_mvc.py -> mvc -> receipts -> modules -> src -> di_senos (project root)
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.modules.receipts.mvc.models.receipt_model import ReciboModel
from src.modules.receipts.mvc.views.receipt_view import ReciboView
from src.modules.receipts.mvc.controllers.main_controller import MainController
from src.config import debug_print


def main(parent=None, nombre_usuario: str = "Usuario", username: str = None):
    """
    Main entry point for Receipt Generator MVC application

    Args:
        parent: Parent window (optional, for launcher integration)
        nombre_usuario: User name to display in header
        username: Username for database operations (if different from nombre_usuario)

    Returns:
        MainController instance
    """
    try:
        debug_print("🚀 Iniciando Receipt Generator (MVC with Specialized Controllers)")

        # Create Model (data and business logic)
        model = ReciboModel()
        debug_print("✅ Model created")

        # Create View (UI)
        view = ReciboView(parent=parent)
        debug_print("✅ View created")

        # Create Main Controller (orchestrates specialized controllers)
        controller = MainController(
            view=view,
            model=model,
            nombre_usuario=nombre_usuario,
            username=username
        )
        debug_print("✅ MainController with specialized controllers created")

        debug_print("✅ MVC components initialized successfully")

        return controller

    except Exception as e:
        debug_print(f"❌ Error al iniciar aplicación MVC: {e}")
        import traceback
        traceback.print_exc()
        raise


def standalone_mode():
    """
    Run application in standalone mode (without launcher)

    Usage:
        python receipt_app_mvc.py
    """
    controller = main(parent=None, nombre_usuario="Administrador")
    controller.run()


if __name__ == "__main__":
    standalone_mode()
