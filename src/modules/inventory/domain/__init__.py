# -*- coding: utf-8 -*-
"""
Domain Layer - Inventory Module
Exports domain entities and exceptions
"""

from .models import (
    Product,
    Purchase,
    PurchaseSearchCriteria,
    BusinessLogicError,
    ProductNotFoundError,
    PurchaseNotFoundError,
    InsufficientStockError,
    DuplicateProductError,
    InvalidFiscalDataError,
    InvalidDateError,
)

__all__ = [
    "Product",
    "Purchase",
    "PurchaseSearchCriteria",
    "BusinessLogicError",
    "ProductNotFoundError",
    "PurchaseNotFoundError",
    "InsufficientStockError",
    "DuplicateProductError",
    "InvalidFiscalDataError",
    "InvalidDateError",
]
