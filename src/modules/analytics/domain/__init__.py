# -*- coding: utf-8 -*-
"""
Domain Layer - Analytics Module
Pure business entities with no database dependencies
"""

from .models import (
    ProductAnalytics,
    ClientAnalytics,
    GroupAnalytics,
    SalesTrend,
    OverallMetrics,
    ProductDetail,
    ClientDetail
)

from .exceptions import (
    AnalyticsDomainError,
    DataNotFoundError,
    InvalidDateRangeError,
    InvalidMetricError
)

__all__ = [
    # Models
    "ProductAnalytics",
    "ClientAnalytics",
    "GroupAnalytics",
    "SalesTrend",
    "OverallMetrics",
    "ProductDetail",
    "ClientDetail",

    # Exceptions
    "AnalyticsDomainError",
    "DataNotFoundError",
    "InvalidDateRangeError",
    "InvalidMetricError",
]
