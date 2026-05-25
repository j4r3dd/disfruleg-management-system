# -*- coding: utf-8 -*-
"""
Database package for receipts module
Provides connection pooling and repository pattern
"""

from src.modules.receipts.database.connection_pool import get_connection, get_pool
from src.modules.receipts.database.base_repository import BaseRepository
from src.modules.receipts.database.repositories import (
    OrdenRepository,
    ProductRepository,
    ClientRepository
)

__all__ = [
    'get_connection',
    'get_pool',
    'BaseRepository',
    'OrdenRepository',
    'ProductRepository',
    'ClientRepository'
]
