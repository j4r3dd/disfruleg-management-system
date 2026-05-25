# -*- coding: utf-8 -*-
"""
Repository Interfaces - Pricing Module
Define protocols for data access (Interface Segregation)
"""

from typing import Protocol, List, Optional
from decimal import Decimal

from ..domain.models import (
    Product,
    Group,
    ClientType,
    PriceByGroup,
    ProductPrice,
    ProductLock
)


class IProductRepository(Protocol):
    """Interface for product data access"""

    def get_all(self, filter_ids: Optional[List[int]] = None) -> List[Product]:
        """Get all products, optionally filtered by IDs"""
        ...

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        ...

    def get_by_name(self, name: str) -> Optional[Product]:
        """Get product by name"""
        ...

    def create(self, product: Product) -> int:
        """Create new product, returns ID"""
        ...

    def update(self, product: Product) -> bool:
        """Update existing product"""
        ...

    def delete(self, product_id: int) -> bool:
        """Delete product by ID"""
        ...

    def search(self, query: str, filter_ids: Optional[List[int]] = None) -> List[Product]:
        """Search products by name"""
        ...


class IGroupRepository(Protocol):
    """Interface for group data access"""

    def get_all() -> List[Group]:
        """Get all groups"""
        ...

    def get_by_id(self, group_id: int) -> Optional[Group]:
        """Get group by ID"""
        ...

    def get_client_count(self, group_id: int) -> int:
        """Get count of clients in a group"""
        ...


class IClientTypeRepository(Protocol):
    """Interface for client type data access"""

    def get_all() -> List[ClientType]:
        """Get all client types"""
        ...

    def get_by_id(self, type_id: int) -> Optional[ClientType]:
        """Get client type by ID"""
        ...

    def get_by_group_id(self, group_id: int) -> Optional[ClientType]:
        """Get client type for a specific group"""
        ...


class IPriceRepository(Protocol):
    """Interface for price data access"""

    def get_by_product_and_group(
        self,
        product_id: int,
        group_id: int
    ) -> Optional[PriceByGroup]:
        """Get price for product in group"""
        ...

    def get_all_by_group(
        self,
        group_id: int,
        filter_product_ids: Optional[List[int]] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> tuple[List[ProductPrice], int]:
        """
        Get all product prices for a group with pagination and search support

        Args:
            group_id: Group ID
            filter_product_ids: Optional list of product IDs to filter
            search_query: Optional search string for product names
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            Tuple of (product_prices, total_count)
        """
        ...

    def set_base_price(
        self,
        product_id: int,
        group_id: int,
        base_price: Decimal
    ) -> bool:
        """Set or update base price for product in group"""
        ...

    def delete_by_product(self, product_id: int) -> bool:
        """Delete all prices for a product"""
        ...


class ILockRepository(Protocol):
    """Interface for product lock management"""

    def acquire_lock(
        self,
        product_id: int,
        usuario: str,
        modulo: str
    ) -> bool:
        """Try to acquire lock on product"""
        ...

    def release_lock(self, product_id: int) -> bool:
        """Release lock on product"""
        ...

    def get_lock(self, product_id: int) -> Optional[ProductLock]:
        """Get current lock information"""
        ...

    def release_all_by_user(self, usuario: str) -> int:
        """Release all locks held by user, returns count"""
        ...

    def ensure_lock_table_exists(self) -> bool:
        """Ensure lock table exists in database"""
        ...
