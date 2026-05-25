# -*- coding: utf-8 -*-
"""
Data Layer
Repository interfaces and MySQL implementations
This layer depends only on the domain layer
"""

from .repositories import (
    IDebtRepository,
    IPaymentRepository
)

from .mysql_repositories import (
    MySQLDebtRepository,
    MySQLPaymentRepository
)

__all__ = [
    # Interfaces
    'IDebtRepository',
    'IPaymentRepository',

    # Implementations
    'MySQLDebtRepository',
    'MySQLPaymentRepository',
]
