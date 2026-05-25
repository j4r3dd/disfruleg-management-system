# -*- coding: utf-8 -*-
"""
Cart Model for Purchase Registration
Manages multiple items before batch registration
Inspired by receipts cart logic but adapted for purchases
"""

from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date
from typing import List, Optional, Dict, Any
from uuid import uuid4


@dataclass
class PurchaseCartItem:
    """Single item in purchase cart"""
    # Identity
    cart_id: str = field(default_factory=lambda: str(uuid4()))

    # Product info
    id_producto: int = 0
    nombre_producto: str = ""
    unidad_producto: str = ""

    # Purchase data
    cantidad: Decimal = Decimal("0")
    precio_unitario: Decimal = Decimal("0")

    # Fiscal info (optional)
    folio_factura: Optional[str] = None
    proveedor: Optional[str] = None
    rfc_proveedor: Optional[str] = None

    # Financial
    incluir_iva: bool = True
    importe_ieps: Decimal = Decimal("0")

    # Calculated
    subtotal: Decimal = field(init=False)
    iva: Decimal = field(init=False)
    total: Decimal = field(init=False)

    def __post_init__(self):
        """Calculate totals"""
        self.calculate_totals()

    def calculate_totals(self):
        """Calculate subtotal, IVA, and total"""
        self.subtotal = self.cantidad * self.precio_unitario
        self.iva = self.subtotal * Decimal("0.16") if self.incluir_iva else Decimal("0")
        self.total = self.subtotal + self.iva + self.importe_ieps

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'cart_id': self.cart_id,
            'id_producto': self.id_producto,
            'nombre_producto': self.nombre_producto,
            'unidad_producto': self.unidad_producto,
            'cantidad': float(self.cantidad),
            'precio_unitario': float(self.precio_unitario),
            'folio_factura': self.folio_factura,
            'proveedor': self.proveedor,
            'rfc_proveedor': self.rfc_proveedor,
            'incluir_iva': self.incluir_iva,
            'importe_ieps': float(self.importe_ieps),
            'subtotal': float(self.subtotal),
            'iva': float(self.iva),
            'total': float(self.total)
        }


class PurchaseCart:
    """
    Shopping cart for multiple purchase items
    Allows adding multiple products before batch registration
    """

    def __init__(self):
        """Initialize empty cart"""
        self.items: List[PurchaseCartItem] = []
        self._listeners: List[callable] = []

    def add_item(self, item: PurchaseCartItem) -> None:
        """
        Add item to cart

        Args:
            item: PurchaseCartItem to add
        """
        self.items.append(item)
        self._notify_change()

    def remove_item(self, cart_id: str) -> bool:
        """
        Remove item from cart by ID

        Args:
            cart_id: Unique cart item ID

        Returns:
            True if removed, False if not found
        """
        initial_length = len(self.items)
        self.items = [item for item in self.items if item.cart_id != cart_id]

        if len(self.items) < initial_length:
            self._notify_change()
            return True
        return False

    def update_item(self, cart_id: str, **kwargs) -> bool:
        """
        Update item in cart

        Args:
            cart_id: Item ID to update
            **kwargs: Fields to update

        Returns:
            True if updated, False if not found
        """
        for item in self.items:
            if item.cart_id == cart_id:
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(item, key):
                        setattr(item, key, value)

                # Recalculate totals
                item.calculate_totals()
                self._notify_change()
                return True
        return False

    def get_item(self, cart_id: str) -> Optional[PurchaseCartItem]:
        """Get item by ID"""
        for item in self.items:
            if item.cart_id == cart_id:
                return item
        return None

    def clear(self) -> None:
        """Clear all items from cart"""
        self.items.clear()
        self._notify_change()

    def get_items(self) -> List[PurchaseCartItem]:
        """Get all items in cart"""
        return self.items.copy()

    def get_item_count(self) -> int:
        """Get number of items in cart"""
        return len(self.items)

    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self.items) == 0

    def get_totals(self) -> Dict[str, Decimal]:
        """
        Calculate total amounts for all items

        Returns:
            Dictionary with subtotal, iva, total
        """
        subtotal = sum(item.subtotal for item in self.items)
        iva = sum(item.iva for item in self.items)
        total = sum(item.total for item in self.items)

        return {
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'items_count': len(self.items)
        }

    def add_listener(self, callback: callable) -> None:
        """
        Add listener for cart changes

        Args:
            callback: Function to call when cart changes
        """
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: callable) -> None:
        """Remove listener"""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_change(self) -> None:
        """Notify all listeners of cart change"""
        for listener in self._listeners:
            try:
                listener()
            except Exception as e:
                print(f"Error notifying cart listener: {e}")

    def validate_cart(self) -> tuple[bool, str]:
        """
        Validate cart before registration

        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.is_empty():
            return False, "El carrito está vacío"

        for item in self.items:
            if item.cantidad <= 0:
                return False, f"Cantidad inválida para {item.nombre_producto}"

            if item.precio_unitario <= 0:
                return False, f"Precio inválido para {item.nombre_producto}"

        return True, ""
