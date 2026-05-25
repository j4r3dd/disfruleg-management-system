# -*- coding: utf-8 -*-
"""
Repository Interfaces - Importacion Module
Define protocols for data access (Interface Segregation)
"""

from typing import Protocol, List, Optional, Tuple
from decimal import Decimal

from ..domain.models import ProductMatch, SystemIntegrityCheck


class IProductRepository(Protocol):
    """Interface for product data access"""

    def search_similar(
        self,
        nombre: str,
        unidad: str
    ) -> Optional[ProductMatch]:
        """
        Search for similar product in database
        Uses exact match first, then fuzzy matching

        Args:
            nombre: Product name
            unidad: Product unit

        Returns:
            ProductMatch if found, None otherwise
        """
        ...

    def create_product(
        self,
        nombre: str,
        unidad: str,
        stock: Decimal = Decimal('0'),
        es_especial: bool = False
    ) -> int:
        """
        Create new product in database

        Args:
            nombre: Product name
            unidad: Product unit
            stock: Initial stock (default 0)
            es_especial: Special product flag (default False)

        Returns:
            ID of created product
        """
        ...

    def get_by_id(self, product_id: int) -> Optional[ProductMatch]:
        """
        Get product by ID

        Args:
            product_id: Product ID

        Returns:
            ProductMatch if found, None otherwise
        """
        ...


class IPriceRepository(Protocol):
    """Interface for price data access"""

    def get_all_groups_with_discounts(self) -> List[Tuple]:
        """
        Get all groups with their discount information

        Returns:
            List of tuples: (id_grupo, clave_grupo, descuento)
        """
        ...

    def set_price_for_group(
        self,
        product_id: int,
        group_id: int,
        precio_base: Decimal
    ) -> bool:
        """
        Set base price for product in specific group

        Args:
            product_id: Product ID
            group_id: Group ID
            precio_base: Base price to set

        Returns:
            True if successful
        """
        ...

    def set_price_all_groups(
        self,
        product_id: int,
        precio_base: Decimal,
        grupos: List[Tuple]
    ) -> bool:
        """
        Set base price for product across all groups
        Applies discounts automatically based on group type

        Args:
            product_id: Product ID
            precio_base: Base price (before discount)
            grupos: List of (id_grupo, clave_grupo, descuento)

        Returns:
            True if successful
        """
        ...


class ISystemRepository(Protocol):
    """Interface for system integrity checks"""

    def check_integrity(self) -> SystemIntegrityCheck:
        """
        Perform system integrity checks

        Returns:
            SystemIntegrityCheck with results
        """
        ...

    def log_import_operation(
        self,
        usuario: str,
        detalles: str
    ) -> bool:
        """
        Log import operation to system logs

        Args:
            usuario: Username performing the operation
            detalles: Operation details

        Returns:
            True if successful
        """
        ...
