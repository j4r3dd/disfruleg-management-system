# -*- coding: utf-8 -*-
"""
Repository Interfaces - Data Layer
Protocols (interfaces) for data access
Follows Interface Segregation Principle
"""

from typing import Protocol, List, Dict, Optional
from decimal import Decimal
from datetime import datetime

from ..domain.models import LearningCorrection
from ..domain.value_objects import Unit


class IClientRepository(Protocol):
    """
    Interface for client data access
    Handles all client-related database operations
    """

    def get_all_clients(self) -> List[Dict]:
        """
        Get all active clients from database

        Returns:
            List of client dictionaries with fields:
            - id_cliente (int): Client ID
            - nombre_cliente (str): Client name
            - id_grupo (int): Group ID
            - clave_grupo (str): Group key
            - nombre_tipo (str): Client type name
            - descuento (Decimal): Discount percentage
        """
        ...

    def get_client_by_id(self, client_id: int) -> Optional[Dict]:
        """
        Get client by ID

        Args:
            client_id: Client ID

        Returns:
            Client dict or None if not found
        """
        ...


class IProductRepository(Protocol):
    """
    Interface for product data access
    Handles all product-related database operations
    """

    def get_all_products(self, group_id: Optional[int] = None) -> List[Dict]:
        """
        Get all active products from database

        Args:
            group_id: If provided, only returns products with prices for this group

        Returns:
            List of product dictionaries with fields:
            - id (int): Product ID
            - nombre (str): Product name
            - unidad (str): Product unit
            - precio (Decimal): Product price
            - categoria (str): Product category
            - stock (Decimal): Product stock
        """
        ...

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """
        Get product by ID

        Args:
            product_id: Product ID

        Returns:
            Product dict or None if not found
        """
        ...

    def search_products(self, search_term: str, limit: int = 50) -> List[Dict]:
        """
        Search products by name

        Args:
            search_term: Search term
            limit: Maximum number of results

        Returns:
            List of matching products
        """
        ...

    def get_product_price(
        self,
        product_id: int,
        group_id: Optional[int] = None
    ) -> Decimal:
        """
        Get product price (optionally for specific group)

        Args:
            product_id: Product ID
            group_id: Optional group ID for group-specific pricing

        Returns:
            Product price
        """
        ...


class ILearningRepository(Protocol):
    """
    Interface for learning/correction data access
    Handles storage and retrieval of learning corrections
    """

    def get_all_corrections(self) -> Dict[str, LearningCorrection]:
        """
        Get all learning corrections

        Returns:
            Dictionary mapping incorrect text to LearningCorrection objects
        """
        ...

    def get_correction(self, incorrect: str) -> Optional[LearningCorrection]:
        """
        Get correction for specific incorrect text

        Args:
            incorrect: Incorrect text to look up

        Returns:
            LearningCorrection or None if not found
        """
        ...

    def save_correction(self, correction: LearningCorrection) -> bool:
        """
        Save or update a correction

        Args:
            correction: LearningCorrection to save

        Returns:
            True if successful
        """
        ...

    def delete_correction(self, incorrect: str) -> bool:
        """
        Delete a correction

        Args:
            incorrect: Incorrect text to delete

        Returns:
            True if successful
        """
        ...

    def increment_usage(self, incorrect: str) -> bool:
        """
        Increment usage counter for a correction

        Args:
            incorrect: Incorrect text

        Returns:
            True if successful
        """
        ...

    def get_statistics(self) -> Dict:
        """
        Get learning system statistics

        Returns:
            Dictionary with statistics:
            - total_entries (int)
            - total_uses (int)
            - avg_uses_per_entry (float)
        """
        ...

    def cleanup_old_entries(
        self,
        max_age_days: int = 180,
        min_usage: int = 1
    ) -> int:
        """
        Clean up old, rarely-used corrections

        Args:
            max_age_days: Maximum age in days
            min_usage: Minimum usage count required

        Returns:
            Number of entries deleted
        """
        ...