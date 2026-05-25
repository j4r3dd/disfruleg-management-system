# -*- coding: utf-8 -*-
"""
Data Layer - Repository Interfaces (Protocols)
Define contracts for data access without implementation details.
"""

from typing import Protocol, List, Optional
from decimal import Decimal
from ..domain.models import Product, Purchase, PurchaseSearchCriteria


class IProductRepository(Protocol):
    """Interface for product data access"""

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        ...

    def get_all(self) -> List[Product]:
        """Get all products ordered by name"""
        ...

    def get_by_name(self, nombre: str) -> Optional[Product]:
        """Get product by exact name"""
        ...

    def create(self, product: Product) -> int:
        """Create a new product, returns the new product ID"""
        ...

    def update(self, product: Product) -> None:
        """Update existing product"""
        ...

    def delete(self, product_id: int) -> None:
        """Delete product"""
        ...

    def update_stock(self, product_id: int, quantity: Decimal, add: bool = True) -> None:
        """
        Update product stock

        Args:
            product_id: Product ID
            quantity: Amount to add or subtract
            add: True to add, False to subtract
        """
        ...

    def get_stock(self, product_id: int) -> Decimal:
        """Get current stock for a product"""
        ...


class IPurchaseRepository(Protocol):
    """Interface for purchase data access"""

    def get_by_id(self, purchase_id: int) -> Optional[Purchase]:
        """Get purchase by ID"""
        ...

    def get_all(self) -> List[Purchase]:
        """Get all purchases ordered by date (newest first)"""
        ...

    def search(self, criteria: PurchaseSearchCriteria) -> List[Purchase]:
        """Search purchases with filters"""
        ...

    def create(self, purchase: Purchase) -> int:
        """Create a new purchase, returns the new purchase ID"""
        ...

    def update(self, purchase: Purchase) -> None:
        """Update existing purchase"""
        ...

    def delete(self, purchase_id: int) -> None:
        """Delete purchase"""
        ...

    def get_by_product(self, product_id: int) -> List[Purchase]:
        """Get all purchases for a specific product"""
        ...

    def get_by_supplier(self, supplier: str) -> List[Purchase]:
        """Get all purchases from a specific supplier"""
        ...

    def get_fiscal_purchases(self) -> List[Purchase]:
        """Get only purchases with complete fiscal information"""
        ...

    def get_informal_purchases(self) -> List[Purchase]:
        """Get only purchases without fiscal information"""
        ...
