# -*- coding: utf-8 -*-
"""
Payment Service - Business Logic Layer
Handles payment processing with transaction management
CRITICAL: Includes race condition prevention via row locking
"""

from typing import Optional, List, Dict
from decimal import Decimal
from datetime import date

from ..data.repositories import IDebtRepository, IPaymentRepository
from ..domain.models import Payment, Debt
from ..domain.value_objects import PaymentMethod
from ..domain.exceptions import (
    DebtNotFoundError,
    PaymentExceedsSaldoError,
    InvalidPaymentAmountError,
    DebtAlreadyPaidError
)


class PaymentService:
    """
    Payment processing business service
    Handles payment registration with transaction management and validation
    """

    def __init__(
        self,
        debt_repo: IDebtRepository,
        payment_repo: IPaymentRepository,
        connection
    ):
        """
        Initialize service with injected dependencies

        Args:
            debt_repo: Debt repository interface
            payment_repo: Payment repository interface
            connection: Database connection for transaction management
        """
        self.debt_repo = debt_repo
        self.payment_repo = payment_repo
        self.conn = connection

    # ==================== PAYMENT OPERATIONS ====================

    def register_payment(
        self,
        id_deuda: int,
        monto: Decimal,
        metodo: PaymentMethod,
        referencia: Optional[str] = None,
        imagen_bytes: Optional[bytes] = None,
        nombre_imagen: Optional[str] = None,
        fecha: Optional[date] = None,
        usuario: str = 'sistema'
    ) -> bool:
        """
        Register payment for a debt
        CRITICAL: Uses transaction with row locking to prevent race conditions

        Args:
            id_deuda: Debt ID
            monto: Payment amount (must be > 0 and <= pending balance)
            metodo: Payment method
            referencia: Optional payment reference
            imagen_bytes: Optional payment receipt image
            nombre_imagen: Optional image filename
            fecha: Payment date (defaults to today)
            usuario: User making the payment (defaults to 'sistema')

        Returns:
            True if payment registered successfully

        Raises:
            ValueError: If validation fails
            DebtNotFoundError: If debt not found
            DebtAlreadyPaidError: If debt already paid
            PaymentExceedsSaldoError: If payment exceeds pending balance
            InvalidPaymentAmountError: If payment amount is invalid
        """
        # Fail fast: Validate inputs
        if id_deuda <= 0:
            raise ValueError("Debt ID must be positive")

        if monto <= 0:
            raise InvalidPaymentAmountError(
                f"Payment amount must be greater than zero (got ${monto})"
            )

        if not isinstance(metodo, PaymentMethod):
            raise ValueError("Payment method must be a PaymentMethod enum")

        # Default to today if no date provided
        if fecha is None:
            fecha = date.today()

        # Create payment entity (will validate in __post_init__)
        payment = Payment(
            id_deuda=id_deuda,
            monto=monto,
            metodo=metodo,
            referencia=referencia,
            imagen_bytes=imagen_bytes,
            nombre_imagen=nombre_imagen,
            fecha=fecha
        )

        # CRITICAL: Start transaction with row locking
        try:
            # Begin transaction
            self.conn.begin()

            # Get current debt state WITH ROW LOCK
            # This prevents other transactions from modifying the same debt
            debt = self.debt_repo.get_debt_by_id_for_update(id_deuda)

            if not debt:
                raise DebtNotFoundError(f"Debt with ID {id_deuda} not found")

            # Business rule: Cannot pay already-paid debt
            if debt.pagado:
                raise DebtAlreadyPaidError(
                    f"Debt {id_deuda} is already fully paid"
                )

            # Business rule: Payment cannot exceed pending balance
            if payment.monto > debt.saldo_pendiente:
                raise PaymentExceedsSaldoError(
                    f"Payment amount ${payment.monto} exceeds pending balance ${debt.saldo_pendiente}"
                )

            # Calculate new state
            nuevo_monto_pagado = debt.monto_pagado + payment.monto
            pagado_completo = nuevo_monto_pagado >= debt.monto_total

            # Determine payment date (only if fully paid)
            fecha_pago = payment.fecha if pagado_completo else None

            # Update debt with payment information (summary)
            # NOTE: "descripcion" in debt table will reflect the latest payment note
            success_debt = self.debt_repo.update_debt_payment(
                id_deuda=id_deuda,
                monto_pagado=nuevo_monto_pagado,
                pagado=pagado_completo,
                fecha_pago=fecha_pago,
                metodo_pago=payment.metodo,
                referencia_pago=payment.referencia,
                descripcion=debt.descripcion,  # Keep original debt description, notes go to payment history
                imagen_comprobante=payment.imagen_bytes, # Still update last image on debt for quick view
                nombre_imagen=payment.nombre_imagen
            )

            if not success_debt:
                raise Exception("Failed to update debt with payment")

            # Record detailed payment in history
            # We treat the debt's "descripcion" as the payment note for now,
            # but ideally we should pass a specific note.
            # The UI passes "referencia" but not separate notes yet.
            # I will use "referencia" as notes or just empty string if not provided.
            # Actually I should update register_payment to accept 'notas' if I want to use it.
            # For now I will leave 'notas' as empty or reuse reference/desc.

            success_history = self.payment_repo.record_payment(
                id_deuda=id_deuda,
                monto=payment.monto,
                metodo_pago=payment.metodo.value if hasattr(payment.metodo, 'value') else str(payment.metodo),
                referencia=payment.referencia,
                imagen_bytes=payment.imagen_bytes,
                nombre_imagen=payment.nombre_imagen,
                notas=None, # Or pass description if added
                usuario=usuario
            )

            if not success_history:
                 raise Exception("Failed to record payment history")

            # Commit transaction
            self.conn.commit()

            return True

        except Exception as e:
            # Rollback on any error
            self.conn.rollback()
            raise e

    def undo_payment(
        self,
        id_pago: int,
        usuario: str = 'admin'
    ) -> bool:
        """
        Undo/reverse a registered payment
        CRITICAL: Uses transaction with row locking to prevent race conditions

        Args:
            id_pago: Payment record ID to undo
            usuario: User performing the undo (for audit trail)

        Returns:
            True if undo successful

        Raises:
            PaymentNotFoundError: If payment doesn't exist
            ValueError: If validation fails
            Exception: On transaction failure
        """
        from ..domain.exceptions import PaymentNotFoundError

        # Fail fast: Validate inputs
        if id_pago <= 0:
            raise ValueError("Payment ID must be positive")

        # CRITICAL: Start transaction with row locking
        try:
            # Begin transaction
            self.conn.begin()

            # Step 1: Delete payment record and get payment details
            # This will raise PaymentNotFoundError if payment doesn't exist
            id_deuda, monto_pagado = self.payment_repo.delete_payment_by_id(id_pago)

            # Step 2: Get current debt state WITH ROW LOCK
            # This prevents other transactions from modifying the same debt
            debt = self.debt_repo.get_debt_by_id_for_update(id_deuda)

            if not debt:
                raise DebtNotFoundError(f"Debt with ID {id_deuda} not found")

            # Step 3: Revert the debt payment
            # This will subtract the payment amount and update pagado status
            success_revert = self.debt_repo.revert_debt_payment(
                id_deuda=id_deuda,
                monto_to_subtract=monto_pagado
            )

            if not success_revert:
                raise Exception("Failed to revert debt payment")

            # Commit transaction
            self.conn.commit()

            return True

        except PaymentNotFoundError:
            # Rollback and re-raise PaymentNotFoundError
            self.conn.rollback()
            raise
        except DebtNotFoundError:
            # Rollback and re-raise DebtNotFoundError
            self.conn.rollback()
            raise
        except Exception as e:
            # Rollback on any other error
            self.conn.rollback()
            raise e


    # ==================== QUERY OPERATIONS ====================

    def get_payment_history(
        self,
        id_cliente: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ):
        """
        Get payment history with optional filters

        Args:
            id_cliente: Optional client ID filter
            fecha_inicio: Optional start date filter
            fecha_fin: Optional end date filter

        Returns:
            List of payment history records

        Raises:
            ValueError: If filters are invalid
        """
        # Fail fast: Validate filters
        if id_cliente is not None and id_cliente <= 0:
            raise ValueError("Client ID must be positive")

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ValueError("Start date cannot be after end date")

        return self.payment_repo.get_payment_history(
            id_cliente=id_cliente,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

    # ==================== VALIDATION HELPERS ====================

    def validate_payment_amount(self, id_deuda: int, monto: Decimal) -> tuple[bool, str]:
        """
        Validate if payment amount is acceptable for a debt
        Does NOT register the payment, just validates

        Args:
            id_deuda: Debt ID
            monto: Payment amount

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Get debt (without locking, just for validation)
            debt = self.debt_repo.get_debt_by_id(id_deuda)

            if not debt:
                return (False, f"Debt {id_deuda} not found")

            if debt.pagado:
                return (False, "Debt is already fully paid")

            if monto <= 0:
                return (False, "Payment amount must be greater than zero")

            if monto > debt.saldo_pendiente:
                return (
                    False,
                    f"Payment ${monto} exceeds pending balance ${debt.saldo_pendiente}"
                )

            return (True, "")

        except Exception as e:
            return (False, str(e))

    def calculate_payment_result(
        self,
        id_deuda: int,
        monto: Decimal
    ) -> dict:
        """
        Calculate what would happen if payment is made
        Preview payment result without actually registering it

        Args:
            id_deuda: Debt ID
            monto: Payment amount

        Returns:
            Dictionary with payment calculation details

        Raises:
            DebtNotFoundError: If debt not found
        """
        debt = self.debt_repo.get_debt_by_id(id_deuda)

        if not debt:
            raise DebtNotFoundError(f"Debt {id_deuda} not found")

        nuevo_monto_pagado = debt.monto_pagado + monto
        nuevo_saldo = debt.monto_total - nuevo_monto_pagado
        pagado_completo = nuevo_monto_pagado >= debt.monto_total

        return {
            'monto_actual_pagado': debt.monto_pagado,
            'nuevo_monto_pagado': nuevo_monto_pagado,
            'saldo_actual': debt.saldo_pendiente,
            'nuevo_saldo': nuevo_saldo,
            'pagado_completo': pagado_completo,
            'monto_total': debt.monto_total
        }