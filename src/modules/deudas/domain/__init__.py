# -*- coding: utf-8 -*-
"""
Domain Layer
Core business entities, value objects, and exceptions
This layer has NO dependencies on other layers
"""

from .models import (
    Debt,
    Payment,
    ClientDebtSummary,
    DebtStatistics
)

from .value_objects import (
    PaymentMethod,
    DebtStatus
)

from .exceptions import (
    DebtDomainError,
    DebtNotFoundError,
    PaymentExceedsSaldoError,
    InvalidPaymentAmountError,
    DebtAlreadyPaidError,
    InvalidPaymentMethodError,
    ClientNotFoundError,
    InvalidDebtStateError
)

__all__ = [
    # Models
    'Debt',
    'Payment',
    'ClientDebtSummary',
    'DebtStatistics',

    # Value Objects
    'PaymentMethod',
    'DebtStatus',

    # Exceptions
    'DebtDomainError',
    'DebtNotFoundError',
    'PaymentExceedsSaldoError',
    'InvalidPaymentAmountError',
    'DebtAlreadyPaidError',
    'InvalidPaymentMethodError',
    'ClientNotFoundError',
    'InvalidDebtStateError',
]
