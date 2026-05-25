# -*- coding: utf-8 -*-
"""Data layer - Repositories and data access"""

from .repositories import (
    IClientRepository,
    IGroupRepository,
    IClientTypeRepository,
)
from .mysql_repositories import (
    MySQLClientRepository,
    MySQLGroupRepository,
    MySQLClientTypeRepository,
)

__all__ = [
    'IClientRepository',
    'IGroupRepository',
    'IClientTypeRepository',
    'MySQLClientRepository',
    'MySQLGroupRepository',
    'MySQLClientTypeRepository',
]
