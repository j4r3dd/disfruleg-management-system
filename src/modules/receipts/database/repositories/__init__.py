# -*- coding: utf-8 -*-
"""
Repositories package
Specific repository implementations for different entities
"""

from src.modules.receipts.database.repositories.orden_repository import OrdenRepository
from src.modules.receipts.database.repositories.product_repository import ProductRepository
from src.modules.receipts.database.repositories.client_repository import ClientRepository

__all__ = ['OrdenRepository', 'ProductRepository', 'ClientRepository']
