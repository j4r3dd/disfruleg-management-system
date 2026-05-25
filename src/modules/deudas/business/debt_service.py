# -*- coding: utf-8 -*-
"""
Debt Service - Business Logic Layer
Handles debt management operations
NO direct database access - uses repositories only!
"""

from typing import List, Optional, Dict
from decimal import Decimal
from datetime import date

from ..data.repositories import IDebtRepository
from ..domain.models import Debt, ClientDebtSummary, DebtStatistics
from ..domain.exceptions import (
    DebtNotFoundError,
    ClientNotFoundError
)


class DebtService:
    """
    Debt management business service
    Handles debt CRUD operations and queries
    """

    def __init__(self, debt_repo: IDebtRepository, invoice_access_service=None):
        """
        Initialize service with injected dependencies

        Args:
            debt_repo: Debt repository interface
            invoice_access_service: Optional invoice access service for PDF management
        """
        self.debt_repo = debt_repo
        self.invoice_access_service = invoice_access_service

    # ==================== QUERY OPERATIONS ====================

    def get_clients_with_debts(self) -> List[ClientDebtSummary]:
        """
        Get all clients with pending debts

        Returns:
            List of client debt summaries ordered by pending balance (DESC)

        Raises:
            Exception: If database error occurs
        """
        return self.debt_repo.get_clients_with_debts()

    def get_client_debts(self, id_cliente: int) -> List[Debt]:
        """
        Get all debts for a specific client

        Args:
            id_cliente: Client ID

        Returns:
            List of debts for the client, ordered by date (newest first)

        Raises:
            ValueError: If client ID is invalid
        """
        # Fail fast: Validate ID
        if id_cliente <= 0:
            raise ValueError("Client ID must be positive")

        debts = self.debt_repo.get_debts_by_client(id_cliente)

        # Business rule: If no debts found, could be invalid client
        # However, client might just have no debts (valid state)
        # So we return empty list

        return debts

    def get_debt_by_id(self, id_deuda: int) -> Debt:
        """
        Get debt by ID

        Args:
            id_deuda: Debt ID

        Returns:
            Debt entity

        Raises:
            ValueError: If debt ID is invalid
            DebtNotFoundError: If debt not found
        """
        # Fail fast: Validate ID
        if id_deuda <= 0:
            raise ValueError("Debt ID must be positive")

        debt = self.debt_repo.get_debt_by_id(id_deuda)

        if not debt:
            raise DebtNotFoundError(f"Debt with ID {id_deuda} not found")

        return debt

    def get_debt_statistics(self) -> DebtStatistics:
        """
        Get system-wide debt statistics

        Returns:
            Debt statistics including totals and counts
        """
        return self.debt_repo.get_statistics()

    def search_invoice_history(
        self,
        query: str,
        id_cliente: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        incluir_pagadas: bool = True
    ) -> List[Dict]:
        """
        Search invoice history with PDF availability

        Args:
            query: Search term (invoice #, client name, reference)
            id_cliente: Optional client ID filter
            fecha_inicio: Optional start date filter
            fecha_fin: Optional end date filter
            incluir_pagadas: Include paid invoices

        Returns:
            List of invoice search results with PDF info
        """
        if self.invoice_access_service:
            return self.invoice_access_service.get_invoices_by_search(
                query=query,
                id_cliente=id_cliente,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                incluir_pagadas=incluir_pagadas
            )
        return []

    # ==================== COMMAND OPERATIONS ====================

    def create_debt(
        self,
        id_cliente: int,
        id_factura: int,
        monto: Decimal,
        fecha_generada: Optional[date] = None,
        descripcion: Optional[str] = None
    ) -> int:
        """
        Create new debt
        Used when receipts/invoices are generated

        Args:
            id_cliente: Client ID
            id_factura: Invoice/receipt ID
            monto: Debt amount (must be positive)
            fecha_generada: Debt generation date (defaults to today)
            descripcion: Optional description

        Returns:
            ID of created debt

        Raises:
            ValueError: If validation fails
        """
        # Fail fast: Validate inputs
        if id_cliente <= 0:
            raise ValueError("Client ID must be positive")

        if id_factura <= 0:
            raise ValueError("Invoice ID must be positive")

        if monto <= 0:
            raise ValueError("Debt amount must be positive")

        # Default to today if no date provided
        if fecha_generada is None:
            fecha_generada = date.today()

        # Validate description length
        if descripcion and len(descripcion) > 255:
            raise ValueError("Description too long (max 255 characters)")

        # Create debt via repository
        debt_id = self.debt_repo.create_debt(
            id_cliente=id_cliente,
            id_factura=id_factura,
            monto=monto,
            fecha_generada=fecha_generada,
            descripcion=descripcion
        )

        return debt_id

    # ==================== VALIDATION HELPERS ====================

    def validate_debt_exists(self, id_deuda: int) -> Debt:
        """
        Validate that a debt exists and return it

        Args:
            id_deuda: Debt ID

        Returns:
            Debt entity

        Raises:
            DebtNotFoundError: If debt not found
        """
        return self.get_debt_by_id(id_deuda)