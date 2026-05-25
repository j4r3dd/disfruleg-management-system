# -*- coding: utf-8 -*-
"""
Cart Data Model - Pure data model without UI dependencies
Handles all cart business logic and data operations
"""

import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal

from src.modules.receipts.constants import SectionNames


@dataclass
class CartItem:
    """
    Represents a single item in the cart
    Pure data class with no UI dependencies
    """
    id_producto: int
    nombre: str
    cantidad: float
    precio_unitario: float
    unidad: str
    seccion: str = SectionNames.GENERAL
    es_especial: bool = False
    item_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def subtotal(self) -> float:
        """Calculate item subtotal"""
        return self.cantidad * self.precio_unitario

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id_producto': self.id_producto,
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'unidad': self.unidad,
            'seccion': self.seccion,
            'es_especial': self.es_especial,
            'item_uuid': self.item_uuid,
            'subtotal': self.subtotal
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CartItem':
        """Create CartItem from dictionary"""
        return cls(
            id_producto=data['id_producto'],
            nombre=data['nombre'],
            cantidad=float(data['cantidad']),
            precio_unitario=float(data['precio_unitario']),
            unidad=data['unidad'],
            seccion=data.get('seccion', SectionNames.GENERAL),
            es_especial=data.get('es_especial', False),
            item_uuid=data.get('item_uuid', str(uuid.uuid4()))
        )

    def update_quantity(self, nueva_cantidad: float) -> None:
        """Update item quantity"""
        if nueva_cantidad <= 0:
            raise ValueError("Quantity must be greater than 0")
        self.cantidad = nueva_cantidad


@dataclass
class CartSection:
    """
    Represents a section in the cart
    Pure data class with no UI dependencies
    """
    nombre: str
    orden: int = 0
    color: Optional[str] = None
    section_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'nombre': self.nombre,
            'orden': self.orden,
            'color': self.color,
            'section_id': self.section_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CartSection':
        """Create CartSection from dictionary"""
        return cls(
            nombre=data['nombre'],
            orden=data.get('orden', 0),
            color=data.get('color'),
            section_id=data.get('section_id', str(uuid.uuid4()))
        )


class CartModel:
    """
    Pure cart data model
    Manages cart items and sections without any UI dependencies
    """

    def __init__(self):
        """Initialize empty cart"""
        self.items: Dict[str, CartItem] = {}  # {item_uuid: CartItem}
        self.sections: Dict[str, CartSection] = {}  # {section_id: CartSection}
        self.sectioning_enabled: bool = True

        # Create default section
        self._create_default_section()

    def _create_default_section(self) -> str:
        """Create default GENERAL section and return its ID"""
        default_section = CartSection(
            nombre=SectionNames.GENERAL,
            orden=0
        )
        self.sections[default_section.section_id] = default_section
        return default_section.section_id

    def _get_default_section_id(self) -> str:
        """Get ID of default GENERAL section"""
        for section_id, section in self.sections.items():
            if section.nombre == SectionNames.GENERAL:
                return section_id

        # If not found, create it
        return self._create_default_section()

    # ==================== SECTION MANAGEMENT ====================

    def add_section(self, nombre: str, orden: Optional[int] = None, color: Optional[str] = None) -> str:
        """
        Add new section to cart

        Args:
            nombre: Section name
            orden: Display order (optional)
            color: Section color (optional)

        Returns:
            Section ID
        """
        if orden is None:
            orden = len(self.sections)

        section = CartSection(nombre=nombre, orden=orden, color=color)
        self.sections[section.section_id] = section
        return section.section_id

    def remove_section(self, section_id: str) -> bool:
        """
        Remove section from cart
        Items in this section are moved to default section

        Args:
            section_id: Section ID to remove

        Returns:
            True if successful, False otherwise
        """
        # Cannot remove default section
        if section_id == self._get_default_section_id():
            return False

        if section_id not in self.sections:
            return False

        # Move items to default section
        default_id = self._get_default_section_id()
        for item in self.items.values():
            if item.seccion == self.sections[section_id].nombre:
                item.seccion = self.sections[default_id].nombre

        # Remove section
        del self.sections[section_id]
        return True

    def get_section_by_name(self, nombre: str) -> Optional[CartSection]:
        """Get section by name"""
        for section in self.sections.values():
            if section.nombre == nombre:
                return section
        return None

    def get_section_id_by_name(self, nombre: str) -> Optional[str]:
        """Get section ID by name"""
        for section_id, section in self.sections.items():
            if section.nombre == nombre:
                return section_id
        return None

    # ==================== ITEM MANAGEMENT ====================

    def add_item(
        self,
        id_producto: int,
        nombre: str,
        cantidad: float,
        precio_unitario: float,
        unidad: str,
        seccion: Optional[str] = None,
        es_especial: bool = False
    ) -> str:
        """
        Add item to cart
        Always creates a new item (allows duplicates)

        Args:
            id_producto: Product ID
            nombre: Product name
            cantidad: Quantity
            precio_unitario: Unit price
            unidad: Unit of measurement
            seccion: Section name (optional, defaults to GENERAL)
            es_especial: Is special product flag

        Returns:
            Item UUID
        """
        # Validate section
        if seccion is None:
            seccion = SectionNames.GENERAL

        # Create new item
        item = CartItem(
            id_producto=id_producto,
            nombre=nombre,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            unidad=unidad,
            seccion=seccion,
            es_especial=es_especial
        )

        # Add to cart
        self.items[item.item_uuid] = item
        return item.item_uuid

    def remove_item(self, item_uuid: str) -> bool:
        """
        Remove item from cart

        Args:
            item_uuid: Item UUID

        Returns:
            True if successful, False if item not found
        """
        if item_uuid in self.items:
            del self.items[item_uuid]
            return True
        return False

    def update_item_price(self, item_uuid: str, nuevo_precio: float) -> bool:
        """
        Update item unit price

        Args:
            item_uuid: Item UUID
            nuevo_precio: New unit price (must be >= 0)

        Returns:
            True if successful, False if item not found or invalid price
        """
        if item_uuid not in self.items:
            return False

        if nuevo_precio < 0:
            raise ValueError("Price must be >= 0")

        self.items[item_uuid].precio_unitario = nuevo_precio
        return True

    def update_item_quantity(self, item_uuid: str, nueva_cantidad: float) -> bool:
        """
        Update item quantity

        Args:
            item_uuid: Item UUID
            nueva_cantidad: New quantity

        Returns:
            True if successful, False if item not found
        """
        if item_uuid in self.items:
            self.items[item_uuid].update_quantity(nueva_cantidad)
            return True
        return False

    def update_item_section(self, item_uuid: str, section_name: str) -> bool:
        """
        Update item section (alias for move_item_to_section for consistency)

        Args:
            item_uuid: Item UUID
            section_name: Target section name

        Returns:
            True if successful, False otherwise
        """
        return self.move_item_to_section(item_uuid, section_name)

    def get_item(self, item_uuid: str) -> Optional[CartItem]:
        """Get item by UUID"""
        return self.items.get(item_uuid)

    def move_item_to_section(self, item_uuid: str, section_name: str) -> bool:
        """
        Move item to different section

        Args:
            item_uuid: Item UUID
            section_name: Target section name

        Returns:
            True if successful, False otherwise
        """
        if item_uuid not in self.items:
            return False

        if section_name not in [s.nombre for s in self.sections.values()]:
            return False

        self.items[item_uuid].seccion = section_name
        return True

    # ==================== CALCULATIONS ====================

    def get_total(self) -> float:
        """Get total amount for all items"""
        return sum(item.subtotal for item in self.items.values())

    def get_section_subtotal(self, section_name: str) -> float:
        """
        Get subtotal for specific section

        Args:
            section_name: Section name

        Returns:
            Subtotal for section
        """
        return sum(
            item.subtotal
            for item in self.items.values()
            if item.seccion == section_name
        )

    def get_item_count(self) -> int:
        """Get total number of items in cart"""
        return len(self.items)

    def get_item_count_by_section(self, section_name: str) -> int:
        """Get number of items in specific section"""
        return sum(
            1 for item in self.items.values()
            if item.seccion == section_name
        )

    # ==================== DATA RETRIEVAL ====================

    def get_items(self) -> List[CartItem]:
        """Get all items as list"""
        return list(self.items.values())

    def get_items_by_section(self) -> Dict[str, List[CartItem]]:
        """
        Get items grouped by section

        Returns:
            Dictionary with section names as keys and lists of items as values
        """
        result: Dict[str, List[CartItem]] = {}

        # Initialize all sections
        for section in self.sections.values():
            result[section.nombre] = []

        # Group items by section
        for item in self.items.values():
            if item.seccion in result:
                result[item.seccion].append(item)
            else:
                # If item has invalid section, move to default
                default_section = self.sections[self._get_default_section_id()].nombre
                item.seccion = default_section
                result[default_section].append(item)

        return result

    def get_items_for_pdf(self) -> List[List[str]]:
        """
        Get items formatted for PDF generation

        Returns:
            List of [product, quantity, unit, price_unit, subtotal]
        """
        items_pdf = []
        for item in self.items.values():
            items_pdf.append([
                item.nombre,
                f"{item.cantidad:.2f}",
                item.unidad,
                f"${item.precio_unitario:.2f}",
                f"${item.subtotal:.2f}"
            ])
        return items_pdf

    def get_items_for_excel(self) -> List[List[str]]:
        """
        Get items formatted for Excel generation

        Returns:
            List of [product, quantity, unit, price_unit, subtotal]
        """
        items_excel = []
        for item in self.items.values():
            items_excel.append([
                item.nombre,
                f"{item.cantidad:.2f}",
                item.unidad,
                f"${item.precio_unitario:.2f}",
                f"${item.subtotal:.2f}"
            ])
        return items_excel

    def get_sectioned_items_for_pdf(self) -> Dict[str, Dict[str, Any]]:
        """
        Get items organized by section for PDF generation

        Returns:
            Dictionary with format:
            {
                "Section Name": {
                    "items": [[product, qty, unit, price, subtotal], ...],
                    "subtotal": float
                }
            }
        """
        result = {}

        items_by_section = self.get_items_by_section()

        for section_name, items in items_by_section.items():
            items_formatted = []
            for item in items:
                items_formatted.append([
                    item.nombre,
                    f"{item.cantidad:.2f}",
                    item.unidad,
                    f"${item.precio_unitario:.2f}",
                    f"${item.subtotal:.2f}"
                ])

            subtotal = sum(item.subtotal for item in items)

            result[section_name] = {
                'items': items_formatted,
                'subtotal': subtotal
            }

        return result

    def get_sectioned_items_for_excel(self) -> Dict[str, Dict[str, Any]]:
        """
        Get items organized by section for Excel generation

        Returns:
            Dictionary with format:
            {
                "Section Name": {
                    "items": [[product, qty, unit, price, subtotal], ...],
                    "subtotal": float
                }
            }
        """
        result = {}

        items_by_section = self.get_items_by_section()

        for section_name, items in items_by_section.items():
            items_formatted = []
            for item in items:
                items_formatted.append([
                    item.nombre,
                    f"{item.cantidad:.2f}",
                    item.unidad,
                    f"${item.precio_unitario:.2f}",
                    f"${item.subtotal:.2f}"
                ])

            subtotal = sum(item.subtotal for item in items)

            result[section_name] = {
                'items': items_formatted,
                'subtotal': subtotal
            }

        return result

    # ==================== VALIDATION ====================

    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self.items) == 0

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate cart state

        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.is_empty():
            return False, "Cart is empty"

        # Validate all items have positive quantities
        for item in self.items.values():
            if item.cantidad <= 0:
                return False, f"Item '{item.nombre}' has invalid quantity: {item.cantidad}"

            if item.precio_unitario < 0:
                return False, f"Item '{item.nombre}' has invalid price: {item.precio_unitario}"

        # Validate all items have valid sections
        valid_sections = {section.nombre for section in self.sections.values()}
        for item in self.items.values():
            if item.seccion not in valid_sections:
                return False, f"Item '{item.nombre}' has invalid section: {item.seccion}"

        return True, None

    # ==================== SERIALIZATION ====================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize cart to dictionary

        Returns:
            Dictionary representation of cart
        """
        return {
            'items': [item.to_dict() for item in self.items.values()],
            'sections': [section.to_dict() for section in self.sections.values()],
            'sectioning_enabled': self.sectioning_enabled,
            'total': self.get_total()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CartModel':
        """
        Deserialize cart from dictionary

        Args:
            data: Dictionary representation of cart

        Returns:
            CartModel instance
        """
        cart = cls()
        cart.items.clear()
        cart.sections.clear()

        # Load sections
        for section_data in data.get('sections', []):
            section = CartSection.from_dict(section_data)
            cart.sections[section.section_id] = section

        # Ensure default section exists
        if not any(s.nombre == SectionNames.GENERAL for s in cart.sections.values()):
            cart._create_default_section()

        # Load items
        for item_data in data.get('items', []):
            item = CartItem.from_dict(item_data)
            cart.items[item.item_uuid] = item

        cart.sectioning_enabled = data.get('sectioning_enabled', True)

        return cart

    # ==================== UTILITY METHODS ====================

    def clear(self) -> None:
        """Clear all items from cart"""
        self.items.clear()

    def __len__(self) -> int:
        """Get number of items in cart"""
        return len(self.items)

    def __bool__(self) -> bool:
        """Check if cart has items"""
        return not self.is_empty()

    def __str__(self) -> str:
        """String representation of cart"""
        return f"CartModel(items={len(self.items)}, sections={len(self.sections)}, total=${self.get_total():.2f})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"CartModel(items={len(self.items)}, sections={len(self.sections)}, "
            f"total=${self.get_total():.2f}, sectioning_enabled={self.sectioning_enabled})"
        )