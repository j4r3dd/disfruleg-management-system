# -*- coding: utf-8 -*-
"""
Pricing Service - Business Logic
Handles price management and calculations
NO direct database access - uses repositories only!
"""

from typing import List, Optional, Tuple
from decimal import Decimal

from ..data.repositories import (
    IPriceRepository,
    IGroupRepository,
    IClientTypeRepository,
    IProductRepository
)
from ..domain.models import (
    Group,
    ClientType,
    PriceByGroup,
    ProductPrice
)
from ..domain.exceptions import (
    GroupNotFoundError,
    ClientTypeNotFoundError,
    ProductNotFoundError,
    InvalidPriceError
)


class PricingService:
    """
    Pricing business service
    Handles price calculations, group management, and price updates
    """

    def __init__(
        self,
        price_repo: IPriceRepository,
        group_repo: IGroupRepository,
        client_type_repo: IClientTypeRepository,
        product_repo: IProductRepository
    ):
        """
        Initialize service with injected dependencies

        Args:
            price_repo: Price repository
            group_repo: Group repository
            client_type_repo: Client type repository
            product_repo: Product repository
        """
        self.price_repo = price_repo
        self.group_repo = group_repo
        self.client_type_repo = client_type_repo
        self.product_repo = product_repo

    # ==================== GROUP OPERATIONS ====================

    def get_all_groups(self) -> List[Group]:
        """
        Get all groups

        Returns:
            List of groups
        """
        return self.group_repo.get_all()

    def get_group_by_id(self, group_id: int) -> Group:
        """
        Get group by ID

        Args:
            group_id: Group ID

        Returns:
            Group

        Raises:
            GroupNotFoundError: If group not found
        """
        # Fail fast: Validate ID
        if group_id <= 0:
            raise ValueError("Group ID must be positive")

        group = self.group_repo.get_by_id(group_id)

        if not group:
            raise GroupNotFoundError(f"Group with ID {group_id} not found")

        return group

    def get_group_client_count(self, group_id: int) -> int:
        """
        Get number of clients in a group

        Args:
            group_id: Group ID

        Returns:
            Number of clients

        Raises:
            GroupNotFoundError: If group not found
        """
        # Fail fast: Validate group exists
        self.get_group_by_id(group_id)

        return self.group_repo.get_client_count(group_id)

    # ==================== CLIENT TYPE OPERATIONS ====================

    def get_all_client_types(self) -> List[ClientType]:
        """
        Get all client types

        Returns:
            List of client types
        """
        return self.client_type_repo.get_all()

    def get_client_type_by_id(self, type_id: int) -> ClientType:
        """
        Get client type by ID

        Args:
            type_id: Client type ID

        Returns:
            ClientType

        Raises:
            ClientTypeNotFoundError: If client type not found
        """
        # Fail fast: Validate ID
        if type_id <= 0:
            raise ValueError("Client type ID must be positive")

        client_type = self.client_type_repo.get_by_id(type_id)

        if not client_type:
            raise ClientTypeNotFoundError(
                f"Client type with ID {type_id} not found"
            )

        return client_type

    def get_client_type_for_group(self, group_id: int) -> ClientType:
        """
        Get client type associated with a group

        Args:
            group_id: Group ID

        Returns:
            ClientType

        Raises:
            GroupNotFoundError: If group not found
            ClientTypeNotFoundError: If client type not found
        """
        # Fail fast: Validate group exists
        self.get_group_by_id(group_id)

        client_type = self.client_type_repo.get_by_group_id(group_id)

        if not client_type:
            raise ClientTypeNotFoundError(
                f"Client type for group {group_id} not found"
            )

        return client_type

    # ==================== PRICE OPERATIONS ====================

    def get_product_prices_for_group(
        self,
        group_id: int,
        filter_product_ids: Optional[List[int]] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> tuple[List[ProductPrice], int]:
        """
        Get all product prices for a specific group with pagination and search

        Args:
            group_id: Group ID
            filter_product_ids: Optional list of product IDs to filter
            search_query: Optional search string for product names
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            Tuple of (product_prices, total_count)

        Raises:
            GroupNotFoundError: If group not found
        """
        # Fail fast: Validate group exists
        self.get_group_by_id(group_id)

        return self.price_repo.get_all_by_group(
            group_id,
            filter_product_ids,
            search_query,
            limit,
            offset
        )

    def get_base_price(
        self,
        product_id: int,
        group_id: int
    ) -> Decimal:
        """
        Get base price for product in group

        Args:
            product_id: Product ID
            group_id: Group ID

        Returns:
            Base price (0 if not set)

        Raises:
            ProductNotFoundError: If product not found
            GroupNotFoundError: If group not found
        """
        # Fail fast: Validate product exists
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        # Fail fast: Validate group exists
        self.get_group_by_id(group_id)

        price = self.price_repo.get_by_product_and_group(product_id, group_id)

        return price.precio_base if price else Decimal("0")

    def set_base_price(
        self,
        product_id: int,
        group_id: int,
        base_price: Decimal
    ) -> bool:
        """
        Set base price for product in group

        Args:
            product_id: Product ID
            group_id: Group ID
            base_price: New base price

        Returns:
            True if successful

        Raises:
            ValueError: If validation fails
            ProductNotFoundError: If product not found
            GroupNotFoundError: If group not found
            InvalidPriceError: If price is invalid
        """
        # Fail fast: Validate product exists
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        # Fail fast: Validate group exists
        self.get_group_by_id(group_id)

        # Fail fast: Validate price
        if base_price < 0:
            raise InvalidPriceError("Base price cannot be negative")

        return self.price_repo.set_base_price(product_id, group_id, base_price)

    def calculate_final_price(
        self,
        base_price: Decimal,
        group_id: int
    ) -> Tuple[Decimal, ClientType]:
        """
        Calculate final price after applying group discount

        Args:
            base_price: Base price
            group_id: Group ID

        Returns:
            Tuple of (final_price, client_type)

        Raises:
            GroupNotFoundError: If group not found
            ClientTypeNotFoundError: If client type not found
        """
        # Fail fast: Validate price
        if base_price < 0:
            raise InvalidPriceError("Base price cannot be negative")

        # Get client type for group
        client_type = self.get_client_type_for_group(group_id)

        # Calculate final price
        final_price = base_price * (1 - client_type.descuento / 100)

        return final_price, client_type

    def delete_prices_for_product(self, product_id: int) -> bool:
        """
        Delete all prices for a product

        Args:
            product_id: Product ID

        Returns:
            True if successful

        Raises:
            ProductNotFoundError: If product not found
        """
        # Fail fast: Validate product exists
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        return self.price_repo.delete_by_product(product_id)

    def get_price_preview(
        self,
        product_id: int,
        group_id: int,
        new_base_price: Decimal
    ) -> Tuple[Decimal, ClientType]:
        """
        Preview final price without saving

        Args:
            product_id: Product ID
            group_id: Group ID
            new_base_price: Proposed base price

        Returns:
            Tuple of (final_price, client_type)

        Raises:
            ProductNotFoundError: If product not found
            GroupNotFoundError: If group not found
            InvalidPriceError: If price is invalid
        """
        # Fail fast: Validate product exists
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")

        # Calculate final price (validates group exists)
        return self.calculate_final_price(new_base_price, group_id)

