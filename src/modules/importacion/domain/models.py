# -*- coding: utf-8 -*-
"""
Domain Models - Importacion Module
Pure business entities with no database dependencies
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

from .exceptions import InvalidProductDataError


@dataclass
class ExtractedProduct:
    """
    Product extracted from PDF
    Represents raw data from PDF before processing
    """
    nombre: str
    unidad: str
    precio: Decimal
    tiene_precio: bool

    def __post_init__(self):
        """Validate product data - Fail Fast"""
        if not self.nombre or not self.nombre.strip():
            raise InvalidProductDataError("Product name cannot be empty")

        if not self.unidad or not self.unidad.strip():
            raise InvalidProductDataError("Product unit cannot be empty")

        if self.precio < 0:
            raise InvalidProductDataError("Price cannot be negative")


@dataclass
class ProductChange:
    """
    Represents a proposed change to apply to the database
    Can be either a new product or an update to existing one
    """
    tipo: str  # 'nuevo' or 'actualizar'
    nombre: str
    unidad: str
    precio_nuevo: Decimal
    tiene_precio: bool
    stock: Decimal
    id_producto: Optional[int] = None  # Only for updates

    def __post_init__(self):
        """Validate change data - Fail Fast"""
        if self.tipo not in ['nuevo', 'actualizar']:
            raise ValueError("Change type must be 'nuevo' or 'actualizar'")

        if not self.nombre or not self.nombre.strip():
            raise InvalidProductDataError("Product name cannot be empty")

        if not self.unidad or not self.unidad.strip():
            raise InvalidProductDataError("Product unit cannot be empty")

        if self.precio_nuevo < 0:
            raise InvalidProductDataError("Price cannot be negative")

        # ✅ REMOVED: Stock validation - negative stock is allowed
        # Stock can represent backorders, pending deliveries, or other business cases

        if self.tipo == 'actualizar' and self.id_producto is None:
            raise ValueError("Update changes must have product ID")


@dataclass
class ProductMatch:
    """
    Represents a matched product from database
    Used during product search and comparison

    ✅ UPDATED: Stock can be negative (represents backorders, debts, etc.)
    """
    id: int
    nombre: str
    unidad: str
    stock: Decimal

    def __post_init__(self):
        """Validate match data"""
        if self.id <= 0:
            raise ValueError("Product ID must be positive")

        # ✅ REMOVED: Stock validation - negative stock is allowed
        # This can represent backorders, pending deliveries, or other business cases


@dataclass
class ImportReport:
    """
    Report of import operation results
    Contains statistics and details of the operation
    """
    fecha: datetime
    usuario: str
    archivo_pdf: str
    productos_procesados: int
    productos_nuevos: int
    productos_actualizados: int
    productos_sin_precio: int
    grupos_afectados: int
    archivo_reporte: Optional[str] = None

    def __post_init__(self):
        """Validate report data"""
        if self.productos_procesados < 0:
            raise ValueError("Processed products count cannot be negative")

        if self.productos_nuevos < 0:
            raise ValueError("New products count cannot be negative")

        if self.productos_actualizados < 0:
            raise ValueError("Updated products count cannot be negative")

        if self.productos_sin_precio < 0:
            raise ValueError("Products without price count cannot be negative")

        if self.grupos_afectados < 0:
            raise ValueError("Affected groups count cannot be negative")


@dataclass
class SystemIntegrityCheck:
    """
    Results of system integrity validation
    Checks for groups without client type, invalid discounts, etc.
    """
    grupos_sin_tipo: list
    descuentos_invalidos: list
    tiene_advertencias: bool

    def __post_init__(self):
        """Calculate if has warnings"""
        self.tiene_advertencias = bool(self.grupos_sin_tipo or self.descuentos_invalidos)

    def get_mensaje_advertencias(self) -> str:
        """Generate warning message for display"""
        if not self.tiene_advertencias:
            return ""

        mensaje = "Se encontraron las siguientes advertencias:\n\n"

        if self.grupos_sin_tipo:
            nombres = ', '.join([g['clave_grupo'] if isinstance(g, dict) else g[1] for g in self.grupos_sin_tipo])
            mensaje += f"⚠️ Grupos sin tipo de cliente: {nombres}\n"

        if self.descuentos_invalidos:
            nombres = ', '.join([
                f"{d['nombre_tipo'] if isinstance(d, dict) else d[0]} ({d['descuento'] if isinstance(d, dict) else d[1]}%)"
                for d in self.descuentos_invalidos
            ])
            mensaje += f"⚠️ Descuentos inválidos: {nombres}\n"

        mensaje += "\n⚠️ Se recomienda corregir estos problemas antes de importar."
        mensaje += "\n\n¿Desea continuar de todos modos?"

        return mensaje
