# -*- coding: utf-8 -*-
"""
Custom Exceptions - Domain Layer
Domain-specific exceptions for the deudas module
"""


class DebtDomainError(Exception):
    """Base exception for all debt domain errors"""
    pass


class DebtNotFoundError(DebtDomainError):
    """Raised when a debt is not found"""
    pass


class PaymentExceedsSaldoError(DebtDomainError):
    """Raised when payment amount exceeds pending balance"""
    pass


class InvalidPaymentAmountError(DebtDomainError):
    """Raised when payment amount is invalid (zero or negative)"""
    pass


class DebtAlreadyPaidError(DebtDomainError):
    """Raised when attempting to pay an already-paid debt"""
    pass


class InvalidPaymentMethodError(DebtDomainError):
    """Raised when payment method is invalid"""
    pass


class PaymentNotFoundError(DebtDomainError):
    """Raised when a payment record is not found"""
    pass


class ClientNotFoundError(DebtDomainError):
    """Raised when a client is not found"""
    pass


class InvalidDebtStateError(DebtDomainError):
    """Raised when debt is in an invalid state"""
    pass
