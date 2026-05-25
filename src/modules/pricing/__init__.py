# -*- coding: utf-8 -*-
"""
Pricing Module - Clean Architecture
Main entry point for the pricing module

Usage:
    from src.modules.pricing import launch_price_editor

    user_data = {'nombre_completo': 'John Doe', 'rol': 'admin'}
    launch_price_editor(user_data)
"""

# Main entry point
from .price_manager import launch_price_editor

# Services (for direct use if needed)
from .business import (
    ProductService,
    PricingService
)

# Domain models (for type hints)
from .domain import (
    Product,
    Group,
    ClientType,
    PriceByGroup,
    ProductPrice,
    ProductLock,
    # Exceptions
    PricingDomainError,
    ProductNotFoundError,
    GroupNotFoundError,
    ClientTypeNotFoundError,
    InvalidPriceError,
    DuplicateProductError,
    ProductLockError
)

# Data layer (for custom implementations)
from .data import (
    # Interfaces
    IProductRepository,
    IGroupRepository,
    IClientTypeRepository,
    IPriceRepository,
    ILockRepository,
    # MySQL implementations
    MySQLProductRepository,
    MySQLGroupRepository,
    MySQLClientTypeRepository,
    MySQLPriceRepository,
    MySQLLockRepository
)

__all__ = [
    # Main entry point
    "launch_price_editor",

    # Services
    "ProductService",
    "PricingService",

    # Domain Models
    "Product",
    "Group",
    "ClientType",
    "PriceByGroup",
    "ProductPrice",
    "ProductLock",

    # Domain Exceptions
    "PricingDomainError",
    "ProductNotFoundError",
    "GroupNotFoundError",
    "ClientTypeNotFoundError",
    "InvalidPriceError",
    "DuplicateProductError",
    "ProductLockError",

    # Repository Interfaces
    "IProductRepository",
    "IGroupRepository",
    "IClientTypeRepository",
    "IPriceRepository",
    "ILockRepository",

    # MySQL Implementations
    "MySQLProductRepository",
    "MySQLGroupRepository",
    "MySQLClientTypeRepository",
    "MySQLPriceRepository",
    "MySQLLockRepository",
]

__version__ = "2.0.0"
__author__ = "Claude (Anthropic)"
__description__ = "Pricing module with clean architecture - refactored from 1,733-line monolith"
