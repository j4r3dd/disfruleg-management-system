# -*- coding: utf-8 -*-
"""
Domain Models - Pricing Module
Pure business entities with no database dependencies
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

from .exceptions import InvalidPriceError


@dataclass
class Product:
    """Product entity"""
    id_producto: Optional[int]
    nombre_producto: str
    unidad_producto: str
    stock: Decimal = Decimal("0")
    es_especial: bool = False

    def __post_init__(self):
        """Validate product data - Fail Fast"""
        if not self.nombre_producto or not self.nombre_producto.strip():
            raise ValueError("Product name cannot be empty")

        if not self.unidad_producto or not self.unidad_producto.strip():
            raise ValueError("Product unit cannot be empty")

        if self.stock < 0:
            raise ValueError("Stock cannot be negative")


@dataclass
class ClientType:
    """Client type entity with discount information"""
    id_tipo_cliente: Optional[int]
    nombre_tipo: str
    descuento: Decimal

    def __post_init__(self):
        """Validate client type data - Fail Fast"""
        if not self.nombre_tipo or not self.nombre_tipo.strip():
            raise ValueError("Client type name cannot be empty")

        if self.descuento < 0 or self.descuento > 100:
            raise ValueError("Discount must be between 0 and 100")


@dataclass
class Group:
    """Group entity linking clients to a client type"""
    id_grupo: Optional[int]
    clave_grupo: str
    id_tipo_cliente: int
    descripcion: Optional[str] = None

    def __post_init__(self):
        """Validate group data - Fail Fast"""
        if not self.clave_grupo or not self.clave_grupo.strip():
            raise ValueError("Group name cannot be empty")

        if self.id_tipo_cliente <= 0:
            raise ValueError("Client type ID must be positive")


@dataclass
class PriceByGroup:
    """Base price for a product in a specific group"""
    id_producto: int
    id_grupo: int
    precio_base: Decimal

    def __post_init__(self):
        """Validate price data - Fail Fast"""
        if self.id_producto <= 0:
            raise ValueError("Product ID must be positive")

        if self.id_grupo <= 0:
            raise ValueError("Group ID must be positive")

        if self.precio_base < 0:
            raise InvalidPriceError("Base price cannot be negative")


@dataclass
class ProductPrice:
    """
    Complete product price information for a group
    Includes product data, base price, and calculated final price
    """
    id_producto: int
    nombre_producto: str
    unidad_producto: str
    stock: Decimal
    es_especial: bool
    id_grupo: int
    clave_grupo: str
    precio_base: Decimal
    descuento: Decimal
    precio_final: Decimal
    nombre_tipo_cliente: str

    def __post_init__(self):
        """Validate and calculate if needed"""
        if self.precio_base < 0:
            raise InvalidPriceError("Base price cannot be negative")

        if self.descuento < 0 or self.descuento > 100:
            raise ValueError("Discount must be between 0 and 100")

        # Recalculate final price to ensure consistency
        self.precio_final = self.precio_base * (1 - self.descuento / 100)

    def calculate_final_price(self) -> Decimal:
        """Calculate final price after discount"""
        return self.precio_base * (1 - self.descuento / 100)


@dataclass
class ProductLock:
    """Product lock information"""
    id_producto: int
    usuario: str
    modulo: str
    fecha_bloqueo: datetime
