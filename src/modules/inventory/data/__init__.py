# -*- coding: utf-8 -*-
"""
Data Layer - Inventory Module
Exports repository interfaces and implementations
"""

from .repositories import IProductRepository, IPurchaseRepository
from .mysql_repositories import MySQLProductRepository, MySQLPurchaseRepository

__all__ = [
    "IProductRepository",
    "IPurchaseRepository",
    "MySQLProductRepository",
    "MySQLPurchaseRepository",
]
