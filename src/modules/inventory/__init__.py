# -*- coding: utf-8 -*-
"""
Inventory Module - Clean Architecture Implementation

Architecture Layers (Onion Architecture):
    +---------------------------------------------+
    |  UI Layer (Controllers/Views)               |
    |  - purchase_controller.py                   |
    |  - Orchestrates user interactions           |
    +-------------------+-------------------------+
                        | depends on
    +-------------------v-------------------------+
    |  Business Layer (Services)                  |
    |  - purchase_service.py                      |
    |  - product_service.py                       |
    |  - Contains ALL business logic              |
    +-------------------+-------------------------+
                        | depends on
    +-------------------v-------------------------+
    |  Data Layer (Repositories)                  |
    |  - repositories.py (interfaces)             |
    |  - mysql_repositories.py (implementations)  |
    |  - Data access ONLY                         |
    +-------------------+-------------------------+
                        | depends on
    +-------------------v-------------------------+
    |  Domain Layer (Models/Entities)             |
    |  - models.py                                |
    |  - Pure data structures                     |
    |  - No dependencies on other layers          |
    +---------------------------------------------+

Key Principles Applied:
    1. Dependency Injection: All layers receive dependencies via constructor
    2. Interface Segregation: Repositories implement Protocol interfaces
    3. Single Responsibility: Each layer has ONE responsibility
    4. Fail Fast: Validate early at service layer
    5. Clean Architecture: Inner layers never depend on outer layers
"""

# Lazy import for launch function to avoid importing UI dependencies
# This allows core components to be imported without customtkinter
def launch_purchase_manager(user_data: dict):
    """
    Launch the purchase manager application.

    Args:
        user_data: Dictionary with user information
    """
    from .purchase_manager import launch_purchase_manager as _launch
    return _launch(user_data)

# Export domain entities for external use
from .domain.models import (
    Product,
    Purchase,
    PurchaseSearchCriteria,
)

# Export services for external use
from .business.purchase_service import PurchaseService
from .business.product_service import ProductService

# Export controller for external use
from .ui.purchase_controller import PurchaseController

# Export repository interfaces for testing/mocking
from .data.repositories import IProductRepository, IPurchaseRepository

# Export repository implementations
from .data.mysql_repositories import (
    MySQLProductRepository,
    MySQLPurchaseRepository,
)

__all__ = [
    # Main entry point
    "launch_purchase_manager",

    # Domain
    "Product",
    "Purchase",
    "PurchaseSearchCriteria",

    # Business
    "PurchaseService",
    "ProductService",

    # UI
    "PurchaseController",

    # Data
    "IProductRepository",
    "IPurchaseRepository",
    "MySQLProductRepository",
    "MySQLPurchaseRepository",
]
