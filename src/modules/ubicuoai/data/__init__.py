# -*- coding: utf-8 -*-
"""
Data Layer - UbicuoAI Module
Repository interfaces and implementations
"""

from .repositories import IClientRepository, IProductRepository, ILearningRepository
from .mysql_repositories import MySQLClientRepository, MySQLProductRepository, MySQLLearningRepository

__all__ = [
    # Interfaces
    'IClientRepository',
    'IProductRepository',
    'ILearningRepository',

    # MySQL Implementations
    'MySQLClientRepository',
    'MySQLProductRepository',
    'MySQLLearningRepository'
]
