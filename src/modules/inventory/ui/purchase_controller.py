# -*- coding: utf-8 -*-
"""
UI Layer - Purchase Controller
Handles user interactions and coordinates business services.
Follows Single Responsibility: Orchestration only, no business logic.
"""

from typing import Optional
from decimal import Decimal
from datetime import date, datetime
import logging
from ..business.purchase_service import PurchaseService
from ..business.product_service import ProductService
from ..domain.models import (
    Purchase,
    PurchaseSearchCriteria,
    BusinessLogicError,
    ProductNotFoundError,
    PurchaseNotFoundError,
    InvalidFiscalDataError,
    InvalidDateError,
)

logger = logging.getLogger(__name__)


class PurchaseController:
    """
    Controller for purchase management UI.
    Orchestrates purchase and product services.
    """

    def __init__(
        self,
        purchase_service: PurchaseService,
        product_service: ProductService
    ):
        """
        Initialize controller with services (Dependency Injection).

        Args:
            purchase_service: Purchase business service
            product_service: Product business service
        """
        if purchase_service is None:
            raise ValueError("Purchase service cannot be None")
        if product_service is None:
            raise ValueError("Product service cannot be None")

        self.purchase_service = purchase_service
        self.product_service = product_service

    # ==================== QUERY OPERATIONS ====================

    def get_all_purchases(self) -> list:
        """
        Get all purchases for display.

        Returns:
            List of purchases
        """
        try:
            purchases = self.purchase_service.get_all_purchases()
            logger.info(f"Retrieved {len(purchases)} purchases")
            return purchases
        except Exception as e:
            logger.error(f"Error retrieving purchases: {e}")
            raise

    def get_purchase(self, purchase_id: int) -> Optional[Purchase]:
        """
        Get a specific purchase.

        Args:
            purchase_id: Purchase ID

        Returns:
            Purchase entity or None
        """
        try:
            return self.purchase_service.get_purchase_by_id(purchase_id)
        except PurchaseNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error retrieving purchase {purchase_id}: {e}")
            raise

    def search_purchases(
        self,
        search_text: Optional[str] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        solo_fiscales: bool = False,
        solo_informales: bool = False,
        proveedor: Optional[str] = None
    ) -> list:
        """
        Search purchases with filters.

        Args:
            search_text: Text to search in product, supplier, folio
            fecha_inicio: Start date filter
            fecha_fin: End date filter
            solo_fiscales: Only show fiscal purchases
            solo_informales: Only show informal purchases
            proveedor: Filter by supplier

        Returns:
            List of filtered purchases
        """
        try:
            criteria = PurchaseSearchCriteria(
                search_text=search_text,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                solo_fiscales=solo_fiscales,
                solo_informales=solo_informales,
                proveedor=proveedor
            )
            return self.purchase_service.search_purchases(criteria)
        except Exception as e:
            logger.error(f"Error searching purchases: {e}")
            raise

    def get_all_products(self) -> list:
        """
        Get all products for product selection.

        Returns:
            List of products
        """
        try:
            return self.product_service.get_all_products()
        except Exception as e:
            logger.error(f"Error retrieving products: {e}")
            raise

    # ==================== COMMAND OPERATIONS ====================

    def create_purchase(
        self,
        product_id: int,
        cantidad: str,
        precio: str,
        fecha_compra: str,
        fecha_registro: str,
        incluir_iva: bool = True,
        folio: str = "",
        proveedor: str = "",
        rfc: str = "",
        ieps: str = "0.00",
        tasa_interes: str = "0.00",
        metodo_pago: str = "PUE",
        forma_pago: str = "03",
        usuario: Optional[str] = None,
        notas: str = ""
    ) -> tuple[bool, str, Optional[int]]:
        """
        Create a new purchase.

        Args:
            product_id: Product ID
            cantidad: Quantity as string
            precio: Unit price as string
            fecha_compra: Purchase date (YYYY-MM-DD)
            fecha_registro: Registration date (YYYY-MM-DD)
            incluir_iva: Include IVA
            folio: Invoice folio
            proveedor: Supplier name
            rfc: Supplier RFC
            ieps: IEPS amount
            tasa_interes: Interest rate
            metodo_pago: Payment method
            forma_pago: Payment form
            usuario: User registering
            notas: Notes

        Returns:
            Tuple of (success, message, purchase_id)
        """
        try:
            # Convert and validate inputs
            cantidad_dec = Decimal(cantidad)
            precio_dec = Decimal(precio)
            ieps_dec = Decimal(ieps or "0")
            tasa_dec = Decimal(tasa_interes or "0")

            # Parse dates
            fecha_compra_date = datetime.strptime(fecha_compra, "%Y-%m-%d").date()
            fecha_registro_date = datetime.strptime(fecha_registro, "%Y-%m-%d").date()

            # Clean strings
            folio = folio.strip() if folio else None
            proveedor = proveedor.strip() if proveedor else None
            rfc = rfc.strip() if rfc else None
            notas = notas.strip() if notas else None

            # Call service
            purchase_id = self.purchase_service.create_purchase(
                id_producto=product_id,
                cantidad_compra=cantidad_dec,
                precio_unitario_compra=precio_dec,
                fecha_compra=fecha_compra_date,
                fecha_registro=fecha_registro_date,
                incluir_iva=incluir_iva,
                folio_factura=folio,
                proveedor=proveedor,
                rfc_proveedor=rfc,
                importe_ieps=ieps_dec,
                tasa_interes=tasa_dec,
                metodo_pago=metodo_pago,
                forma_pago=forma_pago,
                usuario_registro=usuario,
                notas=notas
            )

            # Calculate total for message
            subtotal = cantidad_dec * precio_dec
            iva = subtotal * Decimal("0.16") if incluir_iva else Decimal("0")
            total = subtotal + iva + ieps_dec

            return True, f"Purchase registered successfully. Total: ${total:,.2f}", purchase_id

        except ProductNotFoundError as e:
            logger.warning(f"Product not found: {e}")
            return False, "Product not found", None

        except InvalidDateError as e:
            logger.warning(f"Invalid date: {e}")
            return False, str(e), None

        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return False, f"Validation error: {str(e)}", None

        except BusinessLogicError as e:
            logger.warning(f"Business logic error: {e}")
            return False, str(e), None

        except Exception as e:
            logger.error(f"Unexpected error creating purchase: {e}")
            return False, f"Error: {str(e)}", None

    def update_purchase(
        self,
        purchase_id: int,
        cantidad: str,
        precio: str,
        fecha_compra: str,
        fecha_registro: str,
        incluir_iva: bool = True,
        folio: str = "",
        proveedor: str = "",
        rfc: str = "",
        ieps: str = "0.00",
        tasa_interes: str = "0.00",
        metodo_pago: str = "PUE",
        forma_pago: str = "03",
        notas: str = ""
    ) -> tuple[bool, str]:
        """
        Update an existing purchase.

        Args:
            purchase_id: Purchase ID
            cantidad: Quantity as string
            precio: Unit price as string
            fecha_compra: Purchase date (YYYY-MM-DD)
            fecha_registro: Registration date (YYYY-MM-DD)
            incluir_iva: Include IVA
            folio: Invoice folio
            proveedor: Supplier name
            rfc: Supplier RFC
            ieps: IEPS amount
            tasa_interes: Interest rate
            metodo_pago: Payment method
            forma_pago: Payment form
            notas: Notes

        Returns:
            Tuple of (success, message)
        """
        try:
            # Convert and validate inputs
            cantidad_dec = Decimal(cantidad)
            precio_dec = Decimal(precio)
            ieps_dec = Decimal(ieps or "0")
            tasa_dec = Decimal(tasa_interes or "0")

            # Parse dates
            fecha_compra_date = datetime.strptime(fecha_compra, "%Y-%m-%d").date()
            fecha_registro_date = datetime.strptime(fecha_registro, "%Y-%m-%d").date()

            # Clean strings
            folio = folio.strip() if folio else None
            proveedor = proveedor.strip() if proveedor else None
            rfc = rfc.strip() if rfc else None
            notas = notas.strip() if notas else None

            # Call service
            self.purchase_service.update_purchase(
                id_compra=purchase_id,
                cantidad_compra=cantidad_dec,
                precio_unitario_compra=precio_dec,
                fecha_compra=fecha_compra_date,
                fecha_registro=fecha_registro_date,
                incluir_iva=incluir_iva,
                folio_factura=folio,
                proveedor=proveedor,
                rfc_proveedor=rfc,
                importe_ieps=ieps_dec,
                tasa_interes=tasa_dec,
                metodo_pago=metodo_pago,
                forma_pago=forma_pago,
                notas=notas
            )

            return True, "Purchase updated successfully"

        except PurchaseNotFoundError as e:
            logger.warning(f"Purchase not found: {e}")
            return False, "Purchase not found"

        except InvalidDateError as e:
            logger.warning(f"Invalid date: {e}")
            return False, str(e)

        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return False, f"Validation error: {str(e)}"

        except BusinessLogicError as e:
            logger.warning(f"Business logic error: {e}")
            return False, str(e)

        except Exception as e:
            logger.error(f"Unexpected error updating purchase: {e}")
            return False, f"Error: {str(e)}"

    def delete_purchase(self, purchase_id: int) -> tuple[bool, str]:
        """
        Delete a purchase.

        Args:
            purchase_id: Purchase ID

        Returns:
            Tuple of (success, message)
        """
        try:
            self.purchase_service.delete_purchase(purchase_id)
            return True, "Purchase deleted successfully"

        except PurchaseNotFoundError as e:
            logger.warning(f"Purchase not found: {e}")
            return False, "Purchase not found"

        except Exception as e:
            logger.error(f"Error deleting purchase: {e}")
            return False, f"Error: {str(e)}"

    def create_product(
        self,
        nombre: str,
        unidad: str
    ) -> tuple[bool, str, Optional[int]]:
        """
        Create a new product.

        Args:
            nombre: Product name
            unidad: Product unit

        Returns:
            Tuple of (success, message, product_id)
        """
        try:
            product_id = self.product_service.create_product(
                nombre_producto=nombre,
                unidad_producto=unidad
            )
            return True, f"Product '{nombre}' created successfully", product_id

        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return False, str(e), None

    # ==================== VALIDATION HELPERS ====================

    def validate_fiscal_info(self, purchase_id: int) -> tuple[bool, str]:
        """
        Validate fiscal information for a purchase.

        Args:
            purchase_id: Purchase ID

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            purchase = self.purchase_service.get_purchase_by_id(purchase_id)
            return self.purchase_service.validate_fiscal_info(purchase)
        except Exception as e:
            return False, str(e)

    def check_deductibility(self, purchase_id: int) -> tuple[bool, str]:
        """
        Check if a purchase is tax deductible.

        Args:
            purchase_id: Purchase ID

        Returns:
            Tuple of (is_deductible, reason)
        """
        try:
            purchase = self.purchase_service.get_purchase_by_id(purchase_id)
            return self.purchase_service.is_purchase_deductible(purchase)
        except Exception as e:
            return False, str(e)
