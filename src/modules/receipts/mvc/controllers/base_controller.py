# -*- coding: utf-8 -*-
"""
Base Controller
Base class for all controllers with common functionality
"""

from typing import Optional
from src.modules.receipts.mvc.models.receipt_model import ReciboModel
from src.modules.receipts.mvc.views.receipt_view import ReciboView
from src.modules.receipts.models.cart_model import CartModel
from src.modules.receipts.exceptions import (
    ReceiptException,
    ValidationError,
    ClientNotSelectedError,
    EmptyCartError,
    DatabaseError,
    OrderError,
    ExportError,
    CartError,
    SalesError,
    get_user_friendly_message,
    is_user_facing_error
)
from src.modules.receipts.logging_config import get_logger
from src.config import debug_print

logger = get_logger(__name__)


class BaseController:
    """
    Base class for all controllers
    Provides common functionality and shared access to core components
    """

    def __init__(
        self,
        view: ReciboView,
        model: ReciboModel,
        cart_model: CartModel
    ):
        """
        Initialize base controller

        Args:
            view: The main view component
            model: The data model
            cart_model: The cart data model
        """
        self.view = view
        self.model = model
        self.cart_model = cart_model

    def log_info(self, message: str):
        """Log informational message"""
        debug_print(f"ℹ️ {message}")

    def log_success(self, message: str):
        """Log success message"""
        debug_print(f"✅ {message}")

    def log_error(self, message: str):
        """Log error message"""
        debug_print(f"❌ {message}")

    def log_warning(self, message: str):
        """Log warning message"""
        debug_print(f"⚠️ {message}")

    def show_error(self, title: str, message: str):
        """Show error dialog to user"""
        self.view.mostrar_error(title, message)

    def show_warning(self, title: str, message: str):
        """Show warning dialog to user"""
        self.view.mostrar_advertencia(title, message)

    def show_success(self, title: str, message: str):
        """Show success dialog to user"""
        self.view.mostrar_exito(title, message)

    def show_info(self, title: str, message: str):
        """Show info dialog to user"""
        self.view.mostrar_info(title, message)

    def confirm(self, title: str, message: str) -> bool:
        """
        Show confirmation dialog

        Returns:
            True if user confirmed, False otherwise
        """
        return self.view.mostrar_confirmacion(title, message)

    def handle_exception(self, operation: str, exception: Exception):
        """
        Global exception handler for controllers

        Logs the exception and shows appropriate user message

        Args:
            operation: Description of the operation that failed
            exception: The exception that occurred
        """
        # Log the error
        logger.error(f"Error in {operation}: {exception}", exc_info=True)

        # Get user-friendly message
        if is_user_facing_error(exception):
            message = str(exception)
        else:
            message = get_user_friendly_message(exception)

        # Show error dialog
        self.show_error(f"Error al {operation}", message)
