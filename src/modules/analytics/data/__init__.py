# -*- coding: utf-8 -*-
"""
Data Layer - Analytics Module
Repository interfaces and implementations
"""

from .repositories import (
    IAnalyticsRepository,
    IProductAnalyticsRepository,
    IClientAnalyticsRepository,
    IGroupAnalyticsRepository,
    ISalesTrendRepository,
    ICacheRepository
)

from .mysql_repositories import (
    MySQLAnalyticsRepository,
    MySQLProductAnalyticsRepository,
    MySQLClientAnalyticsRepository,
    MySQLGroupAnalyticsRepository,
    MySQLSalesTrendRepository,
    InMemoryCacheRepository
)

__all__ = [
    # Interfaces
    "IAnalyticsRepository",
    "IProductAnalyticsRepository",
    "IClientAnalyticsRepository",
    "IGroupAnalyticsRepository",
    "ISalesTrendRepository",
    "ICacheRepository",

    # MySQL Implementations
    "MySQLAnalyticsRepository",
    "MySQLProductAnalyticsRepository",
    "MySQLClientAnalyticsRepository",
    "MySQLGroupAnalyticsRepository",
    "MySQLSalesTrendRepository",
    "InMemoryCacheRepository",
]
