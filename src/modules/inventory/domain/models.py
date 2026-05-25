# -*- coding: utf-8 -*-
"""
Domain Layer - Models/Entities for Inventory
Pure data structures with no dependencies on other layers.
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from datetime import datetime, date


@dataclass
class Product:
    """Product entity"""
    id_producto: Optional[int]
    nombre_producto: str
    unidad_producto: str
    stock: Decimal = Decimal("0")
    es_especial: bool = False

    def __post_init__(self):
        """Validate entity invariants (Fail Fast)"""
        if not self.nombre_producto or not self.nombre_producto.strip():
            raise ValueError("Product name cannot be empty")

        if not self.unidad_producto or not self.unidad_producto.strip():
            raise ValueError("Product unit cannot be empty")


@dataclass
class Purchase:
    """Purchase entity with fiscal and financial information"""
    # Identity
    id_compra: Optional[int]
    id_producto: int

    # Basic purchase data
    cantidad_compra: Decimal
    precio_unitario_compra: Decimal
    fecha_compra: date  # Invoice/purchase date
    fecha_registro: date  # System registration date

    # Fiscal information (optional for informal purchases)
    folio_factura: Optional[str] = None
    proveedor: Optional[str] = None
    rfc_proveedor: Optional[str] = None

    # Taxes and financial
    importe_ieps: Decimal = Decimal("0.00")
    tasa_interes: Decimal = Decimal("0.00")
    metodo_pago: str = "PUE"  # PUE or PPD
    forma_pago: str = "03"  # SAT catalog

    # Calculated totals
    subtotal: Decimal = Decimal("0.00")
    iva: Decimal = Decimal("0.00")
    total_con_impuestos: Decimal = Decimal("0.00")

    # Metadata
    usuario_registro: Optional[str] = None
    notas: Optional[str] = None

    # Denormalized fields for display (optional)
    nombre_producto: Optional[str] = None
    unidad_producto: Optional[str] = None

    def __post_init__(self):
        """Validate entity invariants (Fail Fast)"""
        # Validate required fields
        if self.id_producto is None or self.id_producto <= 0:
            raise ValueError("Product ID must be a positive integer")

        if self.cantidad_compra <= 0:
            raise ValueError("Purchase quantity must be positive")

        if self.precio_unitario_compra <= 0:
            raise ValueError("Unit price must be positive")

        # Validate dates
        if isinstance(self.fecha_compra, str):
            self.fecha_compra = datetime.strptime(self.fecha_compra, "%Y-%m-%d").date()

        if isinstance(self.fecha_registro, str):
            self.fecha_registro = datetime.strptime(self.fecha_registro, "%Y-%m-%d").date()

        # Validate future dates
        today = date.today()
        if self.fecha_compra > today:
            raise ValueError("Purchase date cannot be in the future")

        if self.fecha_registro > today:
            raise ValueError("Registration date cannot be in the future")

        # Validate RFC format if provided
        if self.rfc_proveedor:
            import re
            rfc = self.rfc_proveedor.strip().upper()
            patron_rfc = r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$'
            if not re.match(patron_rfc, rfc):
                raise ValueError(
                    "Invalid RFC format. Expected: "
                    "3-4 letters + 6 digits + 3 alphanumeric characters"
                )

        # Validate payment method
        if self.metodo_pago not in ["PUE", "PPD"]:
            raise ValueError("Payment method must be PUE or PPD")

        # Validate negative values
        if self.importe_ieps < 0:
            raise ValueError("IEPS cannot be negative")

        if self.tasa_interes < 0:
            raise ValueError("Interest rate cannot be negative")

        if self.subtotal < 0:
            raise ValueError("Subtotal cannot be negative")

        if self.iva < 0:
            raise ValueError("IVA cannot be negative")

        if self.total_con_impuestos < 0:
            raise ValueError("Total cannot be negative")

    def has_fiscal_info(self) -> bool:
        """Check if purchase has complete fiscal information"""
        return bool(
            self.folio_factura and
            self.proveedor and
            self.rfc_proveedor
        )

    def is_deductible(self) -> bool:
        """Check if purchase is tax deductible"""
        # Cash payments over 2000 are not deductible
        if self.forma_pago == "01" and self.subtotal > 2000:
            return False

        # Must have fiscal info to be deductible
        return self.has_fiscal_info()

    def calculate_totals(self, incluir_iva: bool = True) -> None:
        """Calculate subtotal, IVA, and total"""
        self.subtotal = self.cantidad_compra * self.precio_unitario_compra
        self.iva = self.subtotal * Decimal("0.16") if incluir_iva else Decimal("0.00")
        self.total_con_impuestos = self.subtotal + self.iva + self.importe_ieps


@dataclass
class PurchaseSearchCriteria:
    """Value object for purchase search criteria"""
    search_text: Optional[str] = None  # Search in product, supplier, folio
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    solo_fiscales: bool = False  # Only purchases with fiscal info
    solo_informales: bool = False  # Only purchases without fiscal info
    proveedor: Optional[str] = None

    def has_filters(self) -> bool:
        """Check if any filters are applied"""
        return bool(
            self.search_text or
            self.fecha_inicio or
            self.fecha_fin or
            self.solo_fiscales or
            self.solo_informales or
            self.proveedor
        )


# Business Exceptions
class BusinessLogicError(Exception):
    """Base exception for business logic errors"""
    pass


class ProductNotFoundError(BusinessLogicError):
    """Raised when a product is not found"""
    pass


class PurchaseNotFoundError(BusinessLogicError):
    """Raised when a purchase is not found"""
    pass


class InsufficientStockError(BusinessLogicError):
    """Raised when trying to remove more stock than available"""
    pass


class DuplicateProductError(BusinessLogicError):
    """Raised when trying to create a product that already exists"""
    pass


class InvalidFiscalDataError(BusinessLogicError):
    """Raised when fiscal data is invalid or incomplete"""
    pass


class InvalidDateError(BusinessLogicError):
    """Raised when a date is invalid"""
    pass