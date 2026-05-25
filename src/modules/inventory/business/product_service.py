# -*- coding: utf-8 -*-
"""
Business Layer - Product Service
Contains all business logic for product management.
No direct database access - depends on repository interfaces.
"""

from typing import List, Optional
from decimal import Decimal
import logging
from ..domain.models import (
    Product,
    ProductNotFoundError,
    DuplicateProductError,
    InsufficientStockError,
    BusinessLogicError,
)
from ..data.repositories import IProductRepository

logger = logging.getLogger(__name__)


class ProductService:
    """
    Service for product business logic.
    Depends on repository interface (Dependency Injection).
    """

    def __init__(self, product_repo: IProductRepository):
        """
        Initialize service with dependencies.

        Args:
            product_repo: Product repository implementation
        """
        if product_repo is None:
            raise ValueError("Product repository cannot be None")

        self.product_repo = product_repo

    # ==================== QUERY METHODS ====================

    def get_product_by_id(self, product_id: int) -> Product:
        """
        Get product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product entity

        Raises:
            ProductNotFoundError: If product doesn't exist
        """
        # Fail fast validation
        if product_id is None or product_id <= 0:
            raise ValueError("Product ID must be a positive integer")

        product = self.product_repo.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")

        return product

    def get_all_products(self) -> List[Product]:
        """
        Get all products.

        Returns:
            List of all products ordered by name
        """
        return self.product_repo.get_all()

    def get_product_by_name(self, nombre: str) -> Optional[Product]:
        """
        Get product by exact name.

        Args:
            nombre: Product name

        Returns:
            Product entity or None if not found
        """
        if not nombre or not nombre.strip():
            raise ValueError("Product name cannot be empty")

        return self.product_repo.get_by_name(nombre.strip())

    def get_product_stock(self, product_id: int) -> Decimal:
        """
        Get current stock for a product.

        Args:
            product_id: Product ID

        Returns:
            Current stock quantity
        """
        if product_id is None or product_id <= 0:
            raise ValueError("Product ID must be a positive integer")

        return self.product_repo.get_stock(product_id)

    # ==================== COMMAND METHODS ====================

    def create_product(
        self,
        nombre_producto: str,
        unidad_producto: str,
        stock: Decimal = Decimal("0"),
        es_especial: bool = False
    ) -> int:
        """
        Create a new product with business logic validation.

        Args:
            nombre_producto: Product name
            unidad_producto: Product unit (PIEZA, KG, LITRO, etc.)
            stock: Initial stock (default 0)
            es_especial: Whether product is special

        Returns:
            New product ID

        Raises:
            DuplicateProductError: If product with same name exists
            BusinessLogicError: For other business rule violations
        """
        # Fail fast: Validate required fields
        if not nombre_producto or not nombre_producto.strip():
            raise BusinessLogicError("Product name cannot be empty")

        if not unidad_producto or not unidad_producto.strip():
            raise BusinessLogicError("Product unit cannot be empty")

        if len(nombre_producto.strip()) < 3:
            raise BusinessLogicError("Product name must have at least 3 characters")

        # Fail fast: Check for duplicates
        existing = self.product_repo.get_by_name(nombre_producto.strip())
        if existing is not None:
            raise DuplicateProductError(
                f"Product '{nombre_producto.strip()}' already exists"
            )

        # Create product entity (will validate invariants)
        product = Product(
            id_producto=None,
            nombre_producto=nombre_producto.strip(),
            unidad_producto=unidad_producto.strip().upper(),
            stock=stock,
            es_especial=es_especial
        )

        # Save to repository
        product_id = self.product_repo.create(product)

        logger.info(
            f"Product created: ID={product_id}, "
            f"Name={product.nombre_producto}, "
            f"Unit={product.unidad_producto}"
        )

        return product_id

    def update_product(
        self,
        product_id: int,
        nombre_producto: str,
        unidad_producto: str,
        es_especial: bool = False
    ) -> None:
        """
        Update an existing product.

        Args:
            product_id: Product ID
            nombre_producto: New product name
            unidad_producto: New product unit
            es_especial: Whether product is special

        Raises:
            ProductNotFoundError: If product doesn't exist
            DuplicateProductError: If new name conflicts with existing product
            BusinessLogicError: For other business rule violations
        """
        # Fail fast: Get existing product
        existing = self.get_product_by_id(product_id)

        # Fail fast: Validate required fields
        if not nombre_producto or not nombre_producto.strip():
            raise BusinessLogicError("Product name cannot be empty")

        if not unidad_producto or not unidad_producto.strip():
            raise BusinessLogicError("Product unit cannot be empty")

        if len(nombre_producto.strip()) < 3:
            raise BusinessLogicError("Product name must have at least 3 characters")

        # Fail fast: Check for duplicates (if name changed)
        if nombre_producto.strip() != existing.nombre_producto:
            duplicate = self.product_repo.get_by_name(nombre_producto.strip())
            if duplicate is not None:
                raise DuplicateProductError(
                    f"Product '{nombre_producto.strip()}' already exists"
                )

        # Create updated product entity
        product = Product(
            id_producto=product_id,
            nombre_producto=nombre_producto.strip(),
            unidad_producto=unidad_producto.strip().upper(),
            stock=existing.stock,  # Keep existing stock
            es_especial=es_especial
        )

        # Update in repository
        self.product_repo.update(product)

        logger.info(f"Product updated: ID={product_id}, Name={product.nombre_producto}")

    def delete_product(self, product_id: int) -> None:
        """
        Delete a product.

        Args:
            product_id: Product ID

        Raises:
            ProductNotFoundError: If product doesn't exist
        """
        # Fail fast: Verify product exists
        self.get_product_by_id(product_id)

        # Delete from repository
        self.product_repo.delete(product_id)

        logger.info(f"Product deleted: ID={product_id}")

    def adjust_stock(
        self,
        product_id: int,
        quantity: Decimal,
        add: bool = True
    ) -> None:
        """
        Adjust product stock.

        Args:
            product_id: Product ID
            quantity: Quantity to add or subtract
            add: True to add, False to subtract

        Raises:
            ProductNotFoundError: If product doesn't exist
            InsufficientStockError: If trying to subtract more than available
            BusinessLogicError: For other business rule violations
        """
        # Fail fast: Verify product exists
        product = self.get_product_by_id(product_id)

        # Fail fast: Validate quantity
        if quantity <= 0:
            raise BusinessLogicError("Adjustment quantity must be positive")

        # Update stock (permite stock negativo)
        self.product_repo.update_stock(product_id, quantity, add=add)

        action = "Added" if add else "Removed"
        logger.info(
            f"Stock adjusted: Product ID={product_id}, "
            f"{action} {quantity} {product.unidad_producto}"
        )

    # ==================== VALIDATION METHODS ====================

    def validate_product_name(self, nombre: str) -> tuple[bool, str]:
        """
        Validate product name.

        Args:
            nombre: Product name to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not nombre or not nombre.strip():
            return False, "Product name cannot be empty"

        if len(nombre.strip()) < 3:
            return False, "Product name must have at least 3 characters"

        # Check for duplicates
        existing = self.product_repo.get_by_name(nombre.strip())
        if existing is not None:
            return False, f"Product '{nombre.strip()}' already exists"

        return True, "Product name is valid"