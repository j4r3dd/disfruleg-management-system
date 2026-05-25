# -*- coding: utf-8 -*-
"""
Receipt Generator - MVC Architecture

This module implements the Model-View-Controller pattern for the receipt generator,
separating concerns into three distinct layers:

- Model: Data access and business logic (receipt_model.py)
- View: User interface components (receipt_view.py)
- Controller: Coordination between Model and View (main_controller.py with specialized controllers)

Usage:
    from src.modules.receipts.mvc import receipt_app_mvc

    controller = receipt_app_mvc.main(parent=None, nombre_usuario="Admin")
    controller.run()
"""

from src.modules.receipts.mvc.models import ReciboModel
from src.modules.receipts.mvc.views import ReciboView
from src.modules.receipts.mvc.controllers import MainController

__all__ = ['ReciboModel', 'ReciboView', 'MainController']
