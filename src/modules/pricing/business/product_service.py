# -*- coding: utf-8 -*-
"""
Product Service - Business Logic
Handles product management business rules
NO direct database access - uses repositories only!
"""

from typing import List, Optional
from decimal import Decimal

from ..data.repositories import IProductRepository, ILockRepository
from ..domain.models import Product
from ..domain.exceptions import (
    ProductNotFoundError,
    DuplicateProductError,
    ProductLockError
)


class ProductService:
    """
    Product business service
    Handles product CRUD and validation
    """

    def __init__(
        self,
        product_repo: IProductRepository,
        lock_repo: ILockRepository
    ):
        """
        Initialize service with injected dependencies

        Args:
            product_repo: Product repository
            lock_repo: Lock repository
        """
        self.product_repo = product_repo
        self.lock_repo = lock_repo

    def get_all_products(
        self,
        filter_ids: Optional[List[int]] = None
    ) -> List[Product]:
        """
        Get all products

        Args:
            filter_ids: Optional list of product IDs to filter by

        Returns:
            List of products
        """
        return self.product_repo.get_all(filter_ids)

    def get_product_by_id(self, product_id: int) -> Product:
        """
        Get product by ID

        Args:
            product_id: Product ID

        Returns:
            Product

        Raises:
            ProductNotFoundError: If product not found
        """
        # Fail fast: Validate ID
        if product_id <= 0:
            raise ValueError("Product ID must be positive")

        product = self.product_repo.get_by_id(product_id)

        if not product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")

        return product

    def search_products(
        self,
        query: str,
        filter_ids: Optional[List[int]] = None
    ) -> List[Product]:
        """
        Search products by name

        Args:
            query: Search query
            filter_ids: Optional list of product IDs to filter by

        Returns:
            List of matching products
        """
        if not query or not query.strip():
            return self.get_all_products(filter_ids)

        return self.product_repo.search(query.strip(), filter_ids)

    def create_product(
        self,
        nombre_producto: str,
        unidad_producto: str,
        stock: Decimal = Decimal("0"),
        es_especial: bool = False
    ) -> int:
        """
        Create a new product

        Args:
            nombre_producto: Product name
            unidad_producto: Product unit
            stock: Initial stock (default 0)
            es_especial: Is special product (default False)

        Returns:
            New product ID

        Raises:
            ValueError: If validation fails
            DuplicateProductError: If product already exists
        """
        # Fail fast: Validate inputs
        if not nombre_producto or not nombre_producto.strip():
            raise ValueError("Product name cannot be empty")

        if not unidad_producto or not unidad_producto.strip():
            raise ValueError("Product unit cannot be empty")

        if stock < 0:
            raise ValueError("Stock cannot be negative")

        # Create product entity (will validate in __post_init__)
        product = Product(
            id_producto=None,
            nombre_producto=nombre_producto.strip(),
            unidad_producto=unidad_producto.strip(),
            stock=stock,
            es_especial=es_especial
        )

        # Save to database
        return self.product_repo.create(product)

    def update_product(
        self,
        product_id: int,
        nombre_producto: str,
        unidad_producto: str,
        stock: Decimal,
        es_especial: bool
    ) -> bool:
        """
        Update an existing product

        Args:
            product_id: Product ID
            nombre_producto: Product name
            unidad_producto: Product unit
            stock: Stock quantity
            es_especial: Is special product

        Returns:
            True if updated successfully

        Raises:
            ValueError: If validation fails
            ProductNotFoundError: If product not found
        """
        # Fail fast: Validate product exists
        existing_product = self.get_product_by_id(product_id)

        # Create updated product entity (validates in __post_init__)
        updated_product = Product(
            id_producto=product_id,
            nombre_producto=nombre_producto.strip(),
            unidad_producto=unidad_producto.strip(),
            stock=stock,
            es_especial=es_especial
        )

        return self.product_repo.update(updated_product)

    def delete_product(
        self,
        product_id: int,
        usuario: str
    ) -> bool:
        """
        Delete a product

        Args:
            product_id: Product ID to delete
            usuario: User performing the deletion

        Returns:
            True if deleted successfully

        Raises:
            ProductNotFoundError: If product not found
            ProductLockError: If product is locked by another user
        """
        # Fail fast: Validate product exists
        self.get_product_by_id(product_id)

        # Check if product is locked by someone else
        lock = self.lock_repo.get_lock(product_id)
        if lock and lock.usuario != usuario:
            raise ProductLockError(
                f"Product is locked by {lock.usuario} in module {lock.modulo}"
            )

        # Delete product
        return self.product_repo.delete(product_id)

    def acquire_product_lock(
        self,
        product_id: int,
        usuario: str,
        modulo: str = "PriceEditor"
    ) -> bool:
        """
        Try to acquire lock on product

        Args:
            product_id: Product ID
            usuario: User name
            modulo: Module name

        Returns:
            True if lock acquired

        Raises:
            ProductNotFoundError: If product not found
            ProductLockError: If product is locked by another user
        """
        # Fail fast: Validate product exists
        self.get_product_by_id(product_id)

        # Try to acquire lock
        success = self.lock_repo.acquire_lock(product_id, usuario, modulo)

        if not success:
            # Get lock info for error message
            lock = self.lock_repo.get_lock(product_id)
            if lock:
                raise ProductLockError(
                    f"Product is locked by {lock.usuario} in module {lock.modulo}"
                )
            raise ProductLockError("Failed to acquire product lock")

        return True

    def release_product_lock(self, product_id: int) -> bool:
        """
        Release lock on product

        Args:
            product_id: Product ID

        Returns:
            True if lock released
        """
        return self.lock_repo.release_lock(product_id)

    def release_all_locks_for_user(self, usuario: str) -> int:
        """
        Release all locks held by user

        Args:
            usuario: User name

        Returns:
            Number of locks released
        """
        return self.lock_repo.release_all_by_user(usuario)
