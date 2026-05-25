# -*- coding: utf-8 -*-
"""
Deudas Module - Debt Management System
Clean Architecture implementation with full separation of concerns

Architecture Layers:
    1. Domain Layer (innermost) - Business entities, value objects, exceptions
    2. Data Layer - Repository interfaces and MySQL implementations
    3. Business Layer - Business logic services
    4. UI Layer (outermost) - User interface and controllers

Entry Points:
    - launch_debt_manager(user_data) - New Clean Architecture entry point
    - obtener_debt_manager() - Legacy entry point (deprecated)

Usage:
    from src.modules.deudas import launch_debt_manager

    launch_debt_manager(user_data={
        'usuario': 'admin',
        'es_admin': True
    })
"""

# Entry points
from .debt_manager import launch_debt_manager, obtener_debt_manager

# Domain exports (for external use)
from .domain import (
    # Models
    Debt,
    Payment,
    ClientDebtSummary,
    DebtStatistics,

    # Value Objects
    PaymentMethod,
    DebtStatus,

    # Exceptions
    DebtDomainError,
    DebtNotFoundError,
    PaymentExceedsSaldoError,
    InvalidPaymentAmountError,
    DebtAlreadyPaidError,
    InvalidPaymentMethodError,
    ClientNotFoundError,
    InvalidDebtStateError,
)

# Business layer exports (for receipts module integration)
from .business import DebtService, PaymentService

# Data layer exports (for advanced use cases)
from .data import (
    IDebtRepository,
    IPaymentRepository,
    MySQLDebtRepository,
    MySQLPaymentRepository
)

__all__ = [
    # Entry points
    'launch_debt_manager',
    'obtener_debt_manager',

    # Domain models
    'Debt',
    'Payment',
    'ClientDebtSummary',
    'DebtStatistics',

    # Value objects
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

    # Services (for integration)
    'DebtService',
    'PaymentService',

    # Repositories (for advanced use)
    'IDebtRepository',
    'IPaymentRepository',
    'MySQLDebtRepository',
    'MySQLPaymentRepository',
]
