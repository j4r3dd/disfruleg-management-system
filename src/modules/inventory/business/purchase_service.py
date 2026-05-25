# -*- coding: utf-8 -*-
"""
Business Layer - Purchase Service
Contains all business logic for purchase management.
No direct database access - depends on repository interfaces.
"""

from typing import List, Optional
from decimal import Decimal
from datetime import date
import logging
from ..domain.models import (
    Purchase,
    Product,
    PurchaseSearchCriteria,
    PurchaseNotFoundError,
    ProductNotFoundError,
    InvalidFiscalDataError,
    InvalidDateError,
    BusinessLogicError,
)
from ..data.repositories import IPurchaseRepository, IProductRepository

logger = logging.getLogger(__name__)


class PurchaseService:
    """
    Service for purchase business logic.
    Depends on repository interfaces (Dependency Injection).
    """

    def __init__(
        self,
        purchase_repo: IPurchaseRepository,
        product_repo: IProductRepository
    ):
        """
        Initialize service with dependencies.

        Args:
            purchase_repo: Purchase repository implementation
            product_repo: Product repository implementation
        """
        if purchase_repo is None:
            raise ValueError("Purchase repository cannot be None")
        if product_repo is None:
            raise ValueError("Product repository cannot be None")

        self.purchase_repo = purchase_repo
        self.product_repo = product_repo

    # ==================== QUERY METHODS ====================

    def get_purchase_by_id(self, purchase_id: int) -> Purchase:
        """
        Get purchase by ID.

        Args:
            purchase_id: Purchase ID

        Returns:
            Purchase entity

        Raises:
            PurchaseNotFoundError: If purchase doesn't exist
        """
        # Fail fast validation
        if purchase_id is None or purchase_id <= 0:
            raise ValueError("Purchase ID must be a positive integer")

        purchase = self.purchase_repo.get_by_id(purchase_id)
        if purchase is None:
            raise PurchaseNotFoundError(f"Purchase with ID {purchase_id} not found")

        return purchase

    def get_all_purchases(self) -> List[Purchase]:
        """
        Get all purchases.

        Returns:
            List of all purchases ordered by date (newest first)
        """
        return self.purchase_repo.get_all()

    def search_purchases(self, criteria: PurchaseSearchCriteria) -> List[Purchase]:
        """
        Search purchases with filters.

        Args:
            criteria: Search criteria

        Returns:
            List of filtered purchases
        """
        if criteria is None:
            criteria = PurchaseSearchCriteria()

        return self.purchase_repo.search(criteria)

    def get_fiscal_purchases(self) -> List[Purchase]:
        """Get only purchases with complete fiscal information"""
        return self.purchase_repo.get_fiscal_purchases()

    def get_informal_purchases(self) -> List[Purchase]:
        """Get only purchases without fiscal information"""
        return self.purchase_repo.get_informal_purchases()

    def get_purchases_by_product(self, product_id: int) -> List[Purchase]:
        """Get all purchases for a specific product"""
        if product_id is None or product_id <= 0:
            raise ValueError("Product ID must be a positive integer")

        return self.purchase_repo.get_by_product(product_id)

    def get_purchases_by_supplier(self, supplier: str) -> List[Purchase]:
        """Get all purchases from a specific supplier"""
        if not supplier or not supplier.strip():
            raise ValueError("Supplier name cannot be empty")

        return self.purchase_repo.get_by_supplier(supplier.strip())

    # ==================== COMMAND METHODS ====================

    def create_purchase(
        self,
        id_producto: int,
        cantidad_compra: Decimal,
        precio_unitario_compra: Decimal,
        fecha_compra: date,
        fecha_registro: date,
        incluir_iva: bool = True,
        folio_factura: Optional[str] = None,
        proveedor: Optional[str] = None,
        rfc_proveedor: Optional[str] = None,
        importe_ieps: Decimal = Decimal("0.00"),
        tasa_interes: Decimal = Decimal("0.00"),
        metodo_pago: str = "PUE",
        forma_pago: str = "03",
        usuario_registro: Optional[str] = None,
        notas: Optional[str] = None
    ) -> int:
        """
        Create a new purchase with business logic validation.

        Args:
            id_producto: Product ID
            cantidad_compra: Purchase quantity
            precio_unitario_compra: Unit price
            fecha_compra: Invoice/purchase date
            fecha_registro: System registration date
            incluir_iva: Whether to include IVA (16%)
            folio_factura: Invoice folio (optional)
            proveedor: Supplier name (optional)
            rfc_proveedor: Supplier RFC (optional)
            importe_ieps: IEPS amount
            tasa_interes: Interest rate for credit purchases
            metodo_pago: Payment method (PUE/PPD)
            forma_pago: Payment form (SAT catalog)
            usuario_registro: User who registered the purchase
            notas: Additional notes

        Returns:
            New purchase ID

        Raises:
            ProductNotFoundError: If product doesn't exist
            InvalidFiscalDataError: If fiscal data is incomplete
            InvalidDateError: If dates are invalid
            BusinessLogicError: For other business rule violations
        """
        # Fail fast: Validate product exists
        product = self.product_repo.get_by_id(id_producto)
        if product is None:
            raise ProductNotFoundError(f"Product with ID {id_producto} not found")

        # Fail fast: Validate quantities
        if cantidad_compra <= 0:
            raise BusinessLogicError("Purchase quantity must be positive")

        if precio_unitario_compra <= 0:
            raise BusinessLogicError("Unit price must be positive")

        # Fail fast: Validate dates
        today = date.today()
        if fecha_compra > today:
            raise InvalidDateError("Purchase date cannot be in the future")

        if fecha_registro > today:
            raise InvalidDateError("Registration date cannot be in the future")

        # Business rule: Warn about incomplete fiscal info
        has_fiscal_info = bool(folio_factura and proveedor and rfc_proveedor)

        # Business rule: Cash payments over 2000 are not deductible
        subtotal = cantidad_compra * precio_unitario_compra
        if forma_pago == "01" and subtotal > 2000:
            logger.warning(
                f"Cash payment of ${subtotal:,.2f} exceeds $2,000 limit. "
                "Not tax deductible per SAT regulations."
            )

        # Create purchase entity (will validate invariants)
        purchase = Purchase(
            id_compra=None,
            id_producto=id_producto,
            cantidad_compra=cantidad_compra,
            precio_unitario_compra=precio_unitario_compra,
            fecha_compra=fecha_compra,
            fecha_registro=fecha_registro,
            folio_factura=folio_factura.strip() if folio_factura else None,
            proveedor=proveedor.strip() if proveedor else None,
            rfc_proveedor=rfc_proveedor.strip().upper() if rfc_proveedor else None,
            importe_ieps=importe_ieps,
            tasa_interes=tasa_interes,
            metodo_pago=metodo_pago,
            forma_pago=forma_pago,
            usuario_registro=usuario_registro,
            notas=notas.strip() if notas else None
        )

        # Calculate totals
        purchase.calculate_totals(incluir_iva=incluir_iva)

        # Save to repository
        purchase_id = self.purchase_repo.create(purchase)

        # Update product stock
        self.product_repo.update_stock(id_producto, cantidad_compra, add=True)

        logger.info(
            f"Purchase created: ID={purchase_id}, Product={product.nombre_producto}, "
            f"Quantity={cantidad_compra}, Total=${purchase.total_con_impuestos:,.2f}"
        )

        return purchase_id

    def update_purchase(
        self,
        id_compra: int,
        cantidad_compra: Decimal,
        precio_unitario_compra: Decimal,
        fecha_compra: date,
        fecha_registro: date,
        incluir_iva: bool = True,
        folio_factura: Optional[str] = None,
        proveedor: Optional[str] = None,
        rfc_proveedor: Optional[str] = None,
        importe_ieps: Decimal = Decimal("0.00"),
        tasa_interes: Decimal = Decimal("0.00"),
        metodo_pago: str = "PUE",
        forma_pago: str = "03",
        notas: Optional[str] = None
    ) -> None:
        """
        Update an existing purchase with business logic validation.

        Args:
            id_compra: Purchase ID
            cantidad_compra: New purchase quantity
            precio_unitario_compra: New unit price
            fecha_compra: Invoice/purchase date
            fecha_registro: System registration date
            incluir_iva: Whether to include IVA (16%)
            folio_factura: Invoice folio
            proveedor: Supplier name
            rfc_proveedor: Supplier RFC
            importe_ieps: IEPS amount
            tasa_interes: Interest rate
            metodo_pago: Payment method
            forma_pago: Payment form
            notas: Additional notes

        Raises:
            PurchaseNotFoundError: If purchase doesn't exist
            InvalidDateError: If dates are invalid
            BusinessLogicError: For other business rule violations
        """
        # Fail fast: Get existing purchase
        existing = self.get_purchase_by_id(id_compra)

        # Fail fast: Validate quantities
        if cantidad_compra <= 0:
            raise BusinessLogicError("Purchase quantity must be positive")

        if precio_unitario_compra <= 0:
            raise BusinessLogicError("Unit price must be positive")

        # Fail fast: Validate dates
        today = date.today()
        if fecha_compra > today:
            raise InvalidDateError("Purchase date cannot be in the future")

        if fecha_registro > today:
            raise InvalidDateError("Registration date cannot be in the future")

        # Calculate stock adjustment if quantity changed
        if cantidad_compra != existing.cantidad_compra:
            difference = cantidad_compra - existing.cantidad_compra
            add = difference > 0
            amount = abs(difference)
            self.product_repo.update_stock(existing.id_producto, amount, add=add)

        # Create updated purchase entity
        purchase = Purchase(
            id_compra=id_compra,
            id_producto=existing.id_producto,
            cantidad_compra=cantidad_compra,
            precio_unitario_compra=precio_unitario_compra,
            fecha_compra=fecha_compra,
            fecha_registro=fecha_registro,
            folio_factura=folio_factura.strip() if folio_factura else None,
            proveedor=proveedor.strip() if proveedor else None,
            rfc_proveedor=rfc_proveedor.strip().upper() if rfc_proveedor else None,
            importe_ieps=importe_ieps,
            tasa_interes=tasa_interes,
            metodo_pago=metodo_pago,
            forma_pago=forma_pago,
            usuario_registro=existing.usuario_registro,
            notas=notas.strip() if notas else None
        )

        # Calculate totals
        purchase.calculate_totals(incluir_iva=incluir_iva)

        # Update in repository
        self.purchase_repo.update(purchase)

        logger.info(f"Purchase updated: ID={id_compra}")

    def delete_purchase(self, purchase_id: int) -> None:
        """
        Delete a purchase and adjust product stock.

        Args:
            purchase_id: Purchase ID

        Raises:
            PurchaseNotFoundError: If purchase doesn't exist
        """
        # Fail fast: Get existing purchase
        purchase = self.get_purchase_by_id(purchase_id)

        # Adjust stock (remove the purchased quantity)
        self.product_repo.update_stock(
            purchase.id_producto,
            purchase.cantidad_compra,
            add=False
        )

        # Delete from repository
        self.purchase_repo.delete(purchase_id)

        logger.info(
            f"Purchase deleted: ID={purchase_id}, "
            f"Product ID={purchase.id_producto}, "
            f"Quantity={purchase.cantidad_compra}"
        )

    # ==================== VALIDATION METHODS ====================

    def validate_fiscal_info(self, purchase: Purchase) -> tuple[bool, str]:
        """
        Validate fiscal information completeness.

        Args:
            purchase: Purchase entity

        Returns:
            Tuple of (is_valid, message)
        """
        if not purchase.folio_factura:
            return False, "Missing invoice folio"

        if not purchase.proveedor:
            return False, "Missing supplier name"

        if not purchase.rfc_proveedor:
            return False, "Missing supplier RFC"

        return True, "Fiscal information complete"

    def is_purchase_deductible(self, purchase: Purchase) -> tuple[bool, str]:
        """
        Check if a purchase is tax deductible.

        Args:
            purchase: Purchase entity

        Returns:
            Tuple of (is_deductible, reason)
        """
        # Must have fiscal info
        if not purchase.has_fiscal_info():
            return False, "Missing fiscal information"

        # Cash payments over 2000 are not deductible
        if purchase.forma_pago == "01" and purchase.subtotal > 2000:
            return False, f"Cash payment of ${purchase.subtotal:,.2f} exceeds $2,000 limit"

        return True, "Purchase is deductible"
