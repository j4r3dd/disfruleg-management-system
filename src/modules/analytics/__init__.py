# -*- coding: utf-8 -*-
"""
Analytics Module - Clean Architecture
Main entry point for the analytics module

Usage:
    from src.modules.analytics import launch_analytics

    user_data = {'nombre_completo': 'John Doe', 'rol': 'admin'}
    launch_analytics(user_data)
"""

# Main entry point
from .analytics_launcher import launch_analytics

# Services (for direct use if needed)
from .business import AnalyticsService

# Domain models (for type hints)
from .domain import (
    ProductAnalytics,
    ClientAnalytics,
    GroupAnalytics,
    SalesTrend,
    OverallMetrics,
    ProductDetail,
    ClientDetail,
    # Exceptions
    AnalyticsDomainError,
    DataNotFoundError,
    InvalidDateRangeError,
    InvalidMetricError,
)

# Data layer (for custom implementations)
from .data import (
    # Interfaces
    IAnalyticsRepository,
    IProductAnalyticsRepository,
    IClientAnalyticsRepository,
    IGroupAnalyticsRepository,
    ISalesTrendRepository,
    ICacheRepository,
    # MySQL implementations
    MySQLAnalyticsRepository,
    MySQLProductAnalyticsRepository,
    MySQLClientAnalyticsRepository,
    MySQLGroupAnalyticsRepository,
    MySQLSalesTrendRepository,
    InMemoryCacheRepository,
)

__all__ = [
    # Main entry point
    "launch_analytics",

    # Services
    "AnalyticsService",

    # Domain Models
    "ProductAnalytics",
    "ClientAnalytics",
    "GroupAnalytics",
    "SalesTrend",
    "OverallMetrics",
    "ProductDetail",
    "ClientDetail",

    # Domain Exceptions
    "AnalyticsDomainError",
    "DataNotFoundError",
    "InvalidDateRangeError",
    "InvalidMetricError",

    # Repository Interfaces
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

__version__ = "3.0.0"
__author__ = "Claude (Anthropic)"
__description__ = "Analytics module with clean architecture - refactored from 1,300+ line monolith"
