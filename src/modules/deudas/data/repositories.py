# -*- coding: utf-8 -*-
"""
Repository Interfaces - Data Layer
Protocols (interfaces) for data access
Follows Interface Segregation Principle
"""

from typing import Protocol, List, Optional, Dict, Any
from decimal import Decimal
from datetime import date

from ..domain.models import Debt, ClientDebtSummary, DebtStatistics
from ..domain.value_objects import PaymentMethod


class IDebtRepository(Protocol):
    """
    Interface for debt data access
    Handles all debt-related database operations
    """

    def get_clients_with_debts(self) -> List[ClientDebtSummary]:
        """
        Get all clients with pending debts

        Returns:
            List of client debt summaries (from vista_estado_cuenta_cliente)
        """
        ...

    def get_debts_by_client(self, id_cliente: int) -> List[Debt]:
        """
        Get all debts for a specific client

        Args:
            id_cliente: Client ID

        Returns:
            List of debts for the client
        """
        ...

    def get_debt_by_id(self, id_deuda: int) -> Optional[Debt]:
        """
        Get debt by ID

        Args:
            id_deuda: Debt ID

        Returns:
            Debt entity or None if not found
        """
        ...

    def get_debt_by_id_for_update(self, id_deuda: int) -> Optional[Debt]:
        """
        Get debt by ID with row locking (SELECT ... FOR UPDATE)
        Used in payment processing to prevent race conditions

        Args:
            id_deuda: Debt ID

        Returns:
            Debt entity or None if not found

        Note:
            Must be called within an active transaction
        """
        ...

    def create_debt(
        self,
        id_cliente: int,
        id_factura: int,
        monto: Decimal,
        fecha_generada: date,
        descripcion: Optional[str] = None
    ) -> int:
        """
        Create new debt

        Args:
            id_cliente: Client ID
            id_factura: Invoice ID
            monto: Debt amount
            fecha_generada: Debt generation date
            descripcion: Optional description

        Returns:
            ID of created debt
        """
        ...

    def update_debt_payment(
        self,
        id_deuda: int,
        monto_pagado: Decimal,
        pagado: bool,
        fecha_pago: Optional[date],
        metodo_pago: PaymentMethod,
        referencia_pago: Optional[str],
        descripcion: Optional[str],
        imagen_comprobante: Optional[bytes],
        nombre_imagen: Optional[str]
    ) -> bool:
        """
        Update debt with payment information
        Must be called within a transaction with row locking

        Args:
            id_deuda: Debt ID
            monto_pagado: New total paid amount
            pagado: Whether debt is fully paid
            fecha_pago: Payment date (if fully paid)
            metodo_pago: Payment method
            referencia_pago: Payment reference
            descripcion: Updated description
            imagen_comprobante: Payment receipt image bytes
            nombre_imagen: Image filename

        Returns:
            True if successful
        """
        ...

    def get_statistics(self) -> DebtStatistics:
        """
        Get system-wide debt statistics

        Returns:
            Debt statistics
        """
        ...


class IPaymentRepository(Protocol):
    """
    Interface for payment history access
    Read-only operations for viewing payment history
    """

    def get_payment_history(
        self,
        id_cliente: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get payment history with optional filters

        Args:
            id_cliente: Optional client ID filter
            fecha_inicio: Optional start date filter
            fecha_fin: Optional end date filter

        Returns:
            List of payment history records (from vista_historial_pagos)
        """
        ...

    def delete_payment_by_id(self, id_pago: int) -> tuple[int, Decimal]:
        """
        Delete payment record and return payment details for debt reversal

        Args:
            id_pago: Payment record ID

        Returns:
            Tuple of (id_deuda, monto_pagado) for reverting debt

        Raises:
            PaymentNotFoundError: If payment doesn't exist
        """
        ...
