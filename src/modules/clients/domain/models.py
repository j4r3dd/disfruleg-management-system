# -*- coding: utf-8 -*-
"""
Domain Layer - Models/Entities
These are pure data structures with no dependencies on other layers.
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class ClientType:
    """Client type entity with discount information"""
    id_tipo_cliente: Optional[int]
    nombre_tipo: str
    descuento: Decimal

    def __post_init__(self):
        """Validate entity invariants"""
        if not self.nombre_tipo or not self.nombre_tipo.strip():
            raise ValueError("Client type name cannot be empty")

        if self.descuento < 0 or self.descuento > 100:
            raise ValueError("Discount must be between 0 and 100")


@dataclass
class Group:
    """Group entity associating clients with client types"""
    id_grupo: Optional[int]
    clave_grupo: str
    descripcion: Optional[str]
    id_tipo_cliente: int

    # Denormalized fields for display (optional)
    nombre_tipo: Optional[str] = None
    descuento: Optional[Decimal] = None

    def __post_init__(self):
        """Validate entity invariants"""
        if not self.clave_grupo or not self.clave_grupo.strip():
            raise ValueError("Group key cannot be empty")

        if self.id_tipo_cliente is None or self.id_tipo_cliente <= 0:
            raise ValueError("Client type ID must be a positive integer")


@dataclass
class Client:
    """Client entity with all business information"""
    # Required fields
    id_cliente: Optional[int]
    nombre_cliente: str
    id_grupo: int
    activo: bool = True

    # Optional contact information
    telefono: Optional[str] = None
    correo: Optional[str] = None

    # Optional fiscal information
    rfc: Optional[str] = None
    razon_social: Optional[str] = None
    regimen_fiscal: Optional[str] = None
    codigo_postal: Optional[str] = None
    direccion_fiscal: Optional[str] = None

    # Additional notes
    notas: Optional[str] = None

    # Denormalized fields for display (optional)
    clave_grupo: Optional[str] = None
    nombre_tipo: Optional[str] = None
    descuento: Optional[Decimal] = None

    def __post_init__(self):
        """Validate entity invariants"""
        if not self.nombre_cliente or not self.nombre_cliente.strip():
            raise ValueError("Client name cannot be empty")

        if self.id_grupo is None or self.id_grupo <= 0:
            raise ValueError("Group ID must be a positive integer")

        # Validate RFC format if provided
        if self.rfc:
            rfc = self.rfc.strip()
            if len(rfc) not in [12, 13] or not rfc.isalnum():
                raise ValueError("RFC must be 12 or 13 alphanumeric characters")

        # Validate email format if provided
        if self.correo:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, self.correo):
                raise ValueError("Invalid email format")

    def is_active(self) -> bool:
        """Check if client is active"""
        return self.activo

    def has_fiscal_info(self) -> bool:
        """Check if client has fiscal information"""
        return bool(self.rfc or self.razon_social)


@dataclass
class ClientSearchCriteria:
    """Value object for client search criteria"""
    search_text: Optional[str] = None
    group_filter: Optional[str] = None
    status_filter: Optional[str] = None  # "Todos", "Activos", "Inactivos"
    discount_filter: Optional[str] = None  # "Todos", "Sin descuento", "1-10%", etc.

    def has_filters(self) -> bool:
        """Check if any filters are applied"""
        return bool(
            self.search_text or
            (self.group_filter and self.group_filter != "Todos") or
            (self.status_filter and self.status_filter != "Todos") or
            (self.discount_filter and self.discount_filter != "Todos")
        )


# Business Exceptions
class BusinessLogicError(Exception):
    """Base exception for business logic errors"""
    pass


class ClientNotFoundError(BusinessLogicError):
    """Raised when a client is not found"""
    pass


class GroupNotFoundError(BusinessLogicError):
    """Raised when a group is not found"""
    pass


class ClientTypeNotFoundError(BusinessLogicError):
    """Raised when a client type is not found"""
    pass


class ClientHasInvoicesError(BusinessLogicError):
    """Raised when trying to delete a client with invoices"""
    pass


class GroupInUseError(BusinessLogicError):
    """Raised when trying to delete a group that's in use"""
    pass


class ClientTypeInUseError(BusinessLogicError):
    """Raised when trying to delete a client type that's in use"""
    pass
