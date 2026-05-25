# -*- coding: utf-8 -*-
"""
UI Layer - Inventory Module
Exports UI components
"""

from .purchase_controller import PurchaseController
from .purchase_view import PurchaseView
from .purchase_app import PurchaseApplication
from .product_dialog import create_product_dialog

__all__ = [
    "PurchaseController",
    "PurchaseView",
    "PurchaseApplication",
    "create_product_dialog",
]
