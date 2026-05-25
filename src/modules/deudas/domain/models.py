# -*- coding: utf-8 -*-
"""
Domain Models - Domain Layer
Core business entities for the deudas module
All models include validation and business logic
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Optional

from .value_objects import PaymentMethod, DebtStatus
from .exceptions import InvalidPaymentAmountError, InvalidDebtStateError


@dataclass
class Debt:
    """
    Debt domain entity
    Represents a debt owed by a client
    """
    id_deuda: Optional[int]
    id_cliente: int
    id_factura: int
    nombre_cliente: str
    nombre_grupo: str
    monto_total: Decimal
    monto_pagado: Decimal
    fecha_generada: date
    pagado: bool
    fecha_pago: Optional[date]
    descripcion: Optional[str]
    metodo_pago: Optional[PaymentMethod]
    referencia_pago: Optional[str]
    imagen_comprobante: Optional[bytes]
    nombre_imagen: Optional[str]
    folio_numero: Optional[int] = None  # Folio from factura table

    @property
    def saldo_pendiente(self) -> Decimal:
        """Calculate pending balance"""
        return self.monto_total - self.monto_pagado

    @property
    def status(self) -> DebtStatus:
        """Calculate debt status based on payment state"""
        if self.pagado:
            return DebtStatus.PAID
        elif self.monto_pagado > 0:
            return DebtStatus.PARTIALLY_PAID
        return DebtStatus.PENDING

    def __post_init__(self):
        """Validate debt invariants (Fail Fast)"""
        # Validate IDs
        if self.id_cliente <= 0:
            raise ValueError("Client ID must be positive")
        if self.id_factura <= 0:
            raise ValueError("Invoice ID must be positive")

        # Validate amounts
        if self.monto_total <= 0:
            raise ValueError("Debt amount must be positive")
        if self.monto_pagado < 0:
            raise ValueError("Paid amount cannot be negative")
        if self.monto_pagado > self.monto_total:
            raise InvalidDebtStateError(
                f"Paid amount (${self.monto_pagado}) cannot exceed total (${self.monto_total})"
            )

        # Validate names
        if not self.nombre_cliente or not self.nombre_cliente.strip():
            raise ValueError("Client name cannot be empty")
        if not self.nombre_grupo or not self.nombre_grupo.strip():
            raise ValueError("Group name cannot be empty")

        # Validate payment state consistency
        if self.pagado and self.fecha_pago is None:
            raise InvalidDebtStateError("Paid debt must have payment date")
        if not self.pagado and self.fecha_pago is not None:
            raise InvalidDebtStateError("Unpaid debt cannot have payment date")

        # Validate string lengths
        if self.referencia_pago and len(self.referencia_pago) > 200:
            raise ValueError("Payment reference too long (max 200 chars)")
        if self.nombre_imagen and len(self.nombre_imagen) > 255:
            raise ValueError("Image name too long (max 255 chars)")


@dataclass
class Payment:
    """
    Payment domain entity
    Represents a payment made towards a debt
    """
    id_deuda: int
    monto: Decimal
    metodo: PaymentMethod
    referencia: Optional[str]
    imagen_bytes: Optional[bytes]
    nombre_imagen: Optional[str]
    fecha: date

    def __post_init__(self):
        """Validate payment (Fail Fast)"""
        # Validate debt ID
        if self.id_deuda <= 0:
            raise ValueError("Debt ID must be positive")

        # Validate amount
        if self.monto <= 0:
            raise InvalidPaymentAmountError(
                f"Payment amount must be greater than zero (got ${self.monto})"
            )

        # Validate payment method
        if not isinstance(self.metodo, PaymentMethod):
            raise ValueError("Payment method must be a PaymentMethod enum")

        # Validate string lengths
        if self.referencia and len(self.referencia) > 200:
            raise ValueError("Payment reference too long (max 200 chars)")
        if self.nombre_imagen and len(self.nombre_imagen) > 255:
            raise ValueError("Image name too long (max 255 chars)")

        # Validate image consistency
        if self.imagen_bytes and not self.nombre_imagen:
            raise ValueError("Image bytes provided but no image name")
        if self.nombre_imagen and not self.imagen_bytes:
            raise ValueError("Image name provided but no image bytes")


@dataclass
class ClientDebtSummary:
    """
    Client debt summary entity
    Aggregated debt information for a client (from vista_estado_cuenta_cliente)
    """
    id_cliente: int
    nombre_cliente: str
    clave_grupo: str  # Changed from nombre_grupo to clave_grupo
    saldo_pendiente: Decimal
    deudas_pendientes: int
    total_deuda_pendiente: Decimal  # Changed from total_deudas
    total_deuda_pagada: Decimal  # Changed from total_pagado

    @property
    def nombre_grupo(self) -> str:
        """Alias for backwards compatibility"""
        return self.clave_grupo

    @property
    def total_deudas(self) -> Decimal:
        """Total debts (pending + paid)"""
        return self.total_deuda_pendiente + self.total_deuda_pagada

    @property
    def total_pagado(self) -> Decimal:
        """Alias for backwards compatibility"""
        return self.total_deuda_pagada

    def __post_init__(self):
        """Validate client debt summary"""
        # Validate ID
        if self.id_cliente <= 0:
            raise ValueError("Client ID must be positive")

        # Validate names
        if not self.nombre_cliente or not self.nombre_cliente.strip():
            raise ValueError("Client name cannot be empty")
        if not self.clave_grupo or not self.clave_grupo.strip():
            raise ValueError("Group key cannot be empty")

        # Validate amounts
        if self.saldo_pendiente < 0:
            raise ValueError("Pending balance cannot be negative")
        if self.deudas_pendientes < 0:
            raise ValueError("Pending debts count cannot be negative")
        if self.total_deuda_pendiente < 0:
            raise ValueError("Total pending debt cannot be negative")
        if self.total_deuda_pagada < 0:
            raise ValueError("Total paid debt cannot be negative")


@dataclass
class DebtStatistics:
    """
    Debt statistics entity
    System-wide debt statistics
    """
    total_clientes_con_deudas: int
    total_deudas_pendientes: int
    saldo_total_pendiente: Decimal
    total_deudas: Decimal
    total_pagado: Decimal

    def __post_init__(self):
        """Validate statistics"""
        if self.total_clientes_con_deudas < 0:
            raise ValueError("Client count cannot be negative")
        if self.total_deudas_pendientes < 0:
            raise ValueError("Pending debts count cannot be negative")
        if self.saldo_total_pendiente < 0:
            raise ValueError("Total pending balance cannot be negative")
        if self.total_deudas < 0:
            raise ValueError("Total debts cannot be negative")
        if self.total_pagado < 0:
            raise ValueError("Total paid cannot be negative")