# -*- coding: utf-8 -*-
"""
Value Objects - Domain Layer
Immutable value objects for the deudas domain
"""

from enum import Enum


class PaymentMethod(Enum):
    """
    Valid payment methods
    Enforces type safety for payment method selection
    """
    CASH = "efectivo"
    TRANSFER = "transferencia"
    CARD = "tarjeta"
    CHECK = "cheque"

    @classmethod
    def from_string(cls, value: str) -> 'PaymentMethod':
        """
        Convert string to PaymentMethod enum

        Args:
            value: String representation of payment method

        Returns:
            PaymentMethod enum

        Raises:
            ValueError: If value is not a valid payment method
        """
        if not value:
            raise ValueError("Payment method cannot be empty")

        value_lower = value.lower().strip()
        for method in cls:
            if method.value == value_lower:
                return method

        raise ValueError(
            f"Invalid payment method: '{value}'. "
            f"Valid methods: {', '.join(m.value for m in cls)}"
        )

    @classmethod
    def all_values(cls) -> list:
        """Get all valid payment method values"""
        return [method.value for method in cls]


class DebtStatus(Enum):
    """
    Debt status enumeration
    Calculated based on payment state
    """
    PENDING = "pendiente"
    PARTIALLY_PAID = "parcialmente_pagada"
    PAID = "pagada"

    @property
    def display_name(self) -> str:
        """Human-readable status name"""
        display_names = {
            DebtStatus.PENDING: "Pendiente",
            DebtStatus.PARTIALLY_PAID: "Parcialmente Pagada",
            DebtStatus.PAID: "Pagada"
        }
        return display_names[self]
