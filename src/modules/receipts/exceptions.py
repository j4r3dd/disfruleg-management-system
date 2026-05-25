# -*- coding: utf-8 -*-
"""
Custom Exceptions for Receipts Module
Provides specific exception types for better error handling and debugging
"""


# ==================== BASE EXCEPTIONS ====================

class ReceiptException(Exception):
    """Base exception for all receipt module errors"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# ==================== VALIDATION EXCEPTIONS ====================

class ValidationError(ReceiptException):
    """Raised when data validation fails"""
    pass


class ClientNotSelectedError(ValidationError):
    """Raised when no client is selected"""

    def __init__(self):
        super().__init__("No se ha seleccionado un cliente")


class EmptyCartError(ValidationError):
    """Raised when cart is empty"""

    def __init__(self):
        super().__init__("El carrito está vacío")


class InvalidQuantityError(ValidationError):
    """Raised when quantity is invalid"""

    def __init__(self, quantity):
        super().__init__(
            f"Cantidad inválida: {quantity}",
            details={"quantity": quantity}
        )


class InvalidPriceError(ValidationError):
    """Raised when price is invalid"""

    def __init__(self, price):
        super().__init__(
            f"Precio inválido: {price}",
            details={"price": price}
        )


# ==================== DATABASE EXCEPTIONS ====================

class DatabaseError(ReceiptException):
    """Base exception for database-related errors"""
    pass


class ClientNotFoundError(DatabaseError):
    """Raised when client is not found in database"""

    def __init__(self, client_id: int = None, client_name: str = None):
        if client_id:
            super().__init__(
                f"Cliente no encontrado",
                details={"client_id": client_id}
            )
        elif client_name:
            super().__init__(
                f"Cliente no encontrado",
                details={"client_name": client_name}
            )
        else:
            super().__init__("Cliente no encontrado")


class ProductNotFoundError(DatabaseError):
    """Raised when product is not found in database"""

    def __init__(self, product_id: int = None, product_name: str = None):
        if product_id:
            super().__init__(
                f"Producto no encontrado",
                details={"product_id": product_id}
            )
        elif product_name:
            super().__init__(
                f"Producto no encontrado",
                details={"product_name": product_name}
            )
        else:
            super().__init__("Producto no encontrado")


class OrderNotFoundError(DatabaseError):
    """Raised when order is not found in database"""

    def __init__(self, folio: int):
        super().__init__(
            f"Orden no encontrada",
            details={"folio": folio}
        )


class DuplicateOrderError(DatabaseError):
    """Raised when trying to create an order with existing folio"""

    def __init__(self, folio: int):
        super().__init__(
            f"Ya existe una orden con este folio",
            details={"folio": folio}
        )


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""

    def __init__(self, original_error: Exception = None):
        super().__init__(
            "No se pudo conectar a la base de datos",
            details={"original_error": str(original_error)} if original_error else {}
        )
        self.original_error = original_error


# ==================== ORDER EXCEPTIONS ====================

class OrderError(ReceiptException):
    """Base exception for order-related errors"""
    pass


class OrderCreationError(OrderError):
    """Raised when order creation fails"""

    def __init__(self, folio: int, reason: str = None):
        details = {"folio": folio}
        if reason:
            details["reason"] = reason
        super().__init__(
            f"No se pudo crear la orden",
            details=details
        )


class OrderUpdateError(OrderError):
    """Raised when order update fails"""

    def __init__(self, folio: int, reason: str = None):
        details = {"folio": folio}
        if reason:
            details["reason"] = reason
        super().__init__(
            f"No se pudo actualizar la orden",
            details=details
        )


class OrderLoadError(OrderError):
    """Raised when order cannot be loaded"""

    def __init__(self, folio: int, reason: str = None):
        details = {"folio": folio}
        if reason:
            details["reason"] = reason
        super().__init__(
            f"No se pudo cargar la orden",
            details=details
        )


class OrderAlreadyRegisteredError(OrderError):
    """Raised when trying to modify a registered order"""

    def __init__(self, folio: int):
        super().__init__(
            f"La orden ya está registrada y no puede ser modificada",
            details={"folio": folio}
        )


# ==================== EXPORT EXCEPTIONS ====================

class ExportError(ReceiptException):
    """Base exception for export-related errors"""
    pass


class PDFGenerationError(ExportError):
    """Raised when PDF generation fails"""

    def __init__(self, client_name: str, reason: str = None):
        details = {"client_name": client_name}
        if reason:
            details["reason"] = reason
        super().__init__(
            f"No se pudo generar el PDF",
            details=details
        )


class ExcelGenerationError(ExportError):
    """Raised when Excel generation fails"""

    def __init__(self, client_name: str, reason: str = None):
        details = {"client_name": client_name}
        if reason:
            details["reason"] = reason
        super().__init__(
            f"No se pudo generar el Excel",
            details=details
        )


class FileWriteError(ExportError):
    """Raised when file cannot be written"""

    def __init__(self, file_path: str, reason: str = None):
        details = {"file_path": file_path}
        if reason:
            details["reason"] = reason
        super().__init__(
            f"No se pudo escribir el archivo",
            details=details
        )


class DirectoryNotFoundError(ExportError):
    """Raised when export directory doesn't exist and can't be created"""

    def __init__(self, directory_path: str):
        super().__init__(
            f"No se pudo acceder o crear el directorio de exportación",
            details={"directory_path": directory_path}
        )


# ==================== CART EXCEPTIONS ====================

class CartError(ReceiptException):
    """Base exception for cart-related errors"""
    pass


class ItemNotFoundError(CartError):
    """Raised when item is not found in cart"""

    def __init__(self, item_id: str):
        super().__init__(
            f"Item no encontrado en el carrito",
            details={"item_id": item_id}
        )


class SectionNotFoundError(CartError):
    """Raised when section is not found"""

    def __init__(self, section_name: str):
        super().__init__(
            f"Sección no encontrada",
            details={"section_name": section_name}
        )


class DuplicateItemError(CartError):
    """Raised when trying to add duplicate item (in contexts where not allowed)"""

    def __init__(self, product_id: int, product_name: str):
        super().__init__(
            f"El producto ya existe en el carrito",
            details={"product_id": product_id, "product_name": product_name}
        )


# ==================== SALES EXCEPTIONS ====================

class SalesError(ReceiptException):
    """Base exception for sales-related errors"""
    pass


class SaleProcessingError(SalesError):
    """Raised when sale processing fails"""

    def __init__(self, folio: int = None, reason: str = None):
        details = {}
        if folio:
            details["folio"] = folio
        if reason:
            details["reason"] = reason
        super().__init__(
            "No se pudo procesar la venta",
            details=details
        )


class InsufficientStockError(SalesError):
    """Raised when product stock is insufficient"""

    def __init__(self, product_name: str, requested: float, available: float):
        super().__init__(
            f"Stock insuficiente para el producto",
            details={
                "product_name": product_name,
                "requested": requested,
                "available": available
            }
        )


# ==================== CONFIGURATION EXCEPTIONS ====================

class ConfigurationError(ReceiptException):
    """Base exception for configuration-related errors"""
    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing"""

    def __init__(self, config_key: str):
        super().__init__(
            f"Falta configuración requerida",
            details={"config_key": config_key}
        )


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration value is invalid"""

    def __init__(self, config_key: str, value, reason: str = None):
        details = {"config_key": config_key, "value": value}
        if reason:
            details["reason"] = reason
        super().__init__(
            f"Configuración inválida",
            details=details
        )


# ==================== PERMISSION EXCEPTIONS ====================

class PermissionError(ReceiptException):
    """Base exception for permission-related errors"""
    pass


class UnauthorizedError(PermissionError):
    """Raised when user doesn't have permission for operation"""

    def __init__(self, operation: str, user: str = None):
        details = {"operation": operation}
        if user:
            details["user"] = user
        super().__init__(
            f"No tiene permisos para realizar esta operación",
            details=details
        )


# ==================== UTILITY FUNCTIONS ====================

def is_user_facing_error(exception: Exception) -> bool:
    """
    Check if exception should be shown to user

    Args:
        exception: The exception to check

    Returns:
        True if exception should be shown to user
    """
    # All our custom exceptions are user-facing
    if isinstance(exception, ReceiptException):
        return True

    # Standard exceptions that are user-facing
    user_facing_types = (ValueError, KeyError, FileNotFoundError)
    return isinstance(exception, user_facing_types)


def get_user_friendly_message(exception: Exception) -> str:
    """
    Get user-friendly error message

    Args:
        exception: The exception

    Returns:
        User-friendly error message
    """
    if isinstance(exception, ReceiptException):
        return str(exception)

    # Map common exceptions to friendly messages
    error_messages = {
        ValueError: "Valor inválido proporcionado",
        KeyError: "Dato requerido no encontrado",
        FileNotFoundError: "Archivo no encontrado",
        PermissionError: "Permisos insuficientes",
        ConnectionError: "Error de conexión",
    }

    for error_type, message in error_messages.items():
        if isinstance(exception, error_type):
            return f"{message}: {str(exception)}"

    # Generic message for unknown exceptions
    return f"Error inesperado: {str(exception)}"


# ==================== EXCEPTION CONTEXT ====================

class ExceptionContext:
    """
    Context manager for handling exceptions with additional context

    Usage:
        with ExceptionContext("Saving order", folio=123):
            # ... code that might raise exceptions ...
    """

    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Add context to exception if it's one of ours
            if isinstance(exc_val, ReceiptException):
                exc_val.details.update(self.context)
                exc_val.details['operation'] = self.operation

        # Don't suppress the exception
        return False
