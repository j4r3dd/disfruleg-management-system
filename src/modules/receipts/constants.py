# -*- coding: utf-8 -*-
"""
Constants and Enums for Receipt Module
Centralizes all magic strings and configuration values
"""

from enum import Enum
from decimal import Decimal


# ==================== ORDER STATES ====================

class OrderState(Enum):
    """Order states in the system"""
    GUARDADA = "guardada"      # Saved order (draft)
    REGISTRADA = "registrada"  # Registered (completed)
    CANCELADA = "cancelada"    # Cancelled

    def __str__(self):
        return self.value


# ==================== SECTION NAMES ====================

class SectionNames:
    """Standard section names"""
    GENERAL = "GENERAL"
    DEFAULT = GENERAL  # Alias for clarity


# ==================== DATABASE CONSTANTS ====================

class DatabaseTables:
    """Database table names"""
    ORDENES_GUARDADAS = "ordenes_guardadas"
    FACTURA = "factura"
    DETALLE_FACTURA = "detalle_factura"
    FOLIO_SEQUENCE = "folio_sequence"
    FACTURA_SEQUENCE = "factura_sequence"
    PRODUCTO = "producto"
    CLIENTE = "cliente"
    GRUPO = "grupo"
    PRECIO_POR_GRUPO = "precio_por_grupo"


# ==================== VALIDATION CONSTANTS ====================

class ValidationRules:
    """Validation rules and limits"""
    MIN_QUANTITY = Decimal("0.01")
    MAX_QUANTITY = Decimal("9999.99")
    MIN_PRICE = Decimal("0.00")
    MAX_PRICE = Decimal("999999.99")
    MIN_SEARCH_LENGTH = 2  # Minimum characters for product search


# ==================== UI CONSTANTS ====================

class UIConstants:
    """UI-related constants"""
    WINDOW_WIDTH_EDIT_PRODUCT = 550
    WINDOW_HEIGHT_BASIC = 500
    WINDOW_HEIGHT_WITH_SECTIONS = 700
    DEFAULT_QUANTITY = "1.0"


# ==================== ERROR MESSAGES ====================

class ErrorMessages:
    """Standard error messages"""
    INVALID_QUANTITY = "La cantidad debe ser mayor a {min_val}"
    INVALID_PRICE = "El precio no puede ser negativo"
    NO_CLIENT_SELECTED = "Por favor seleccione un cliente"
    EMPTY_CART = "El carrito está vacío"
    FOLIO_IN_USE = "El folio {folio} ya está en uso"
    DATABASE_ERROR = "Error de conexión a la base de datos"
    PRODUCT_NOT_FOUND = "Producto no encontrado"


# ==================== SUCCESS MESSAGES ====================

class SuccessMessages:
    """Standard success messages"""
    ORDER_SAVED = "Orden guardada exitosamente. Folio: {folio}"
    ORDER_LOADED = "Orden {folio} cargada exitosamente"
    SALE_PROCESSED = "Venta procesada. Folio: {folio}"
    PDF_GENERATED = "PDF generado: {path}"
    EXCEL_GENERATED = "Excel generado: {path}"


# ==================== EXPORT FORMATS ====================

class ExportFormat(Enum):
    """Export file formats"""
    PDF = "pdf"
    EXCEL = "excel"
