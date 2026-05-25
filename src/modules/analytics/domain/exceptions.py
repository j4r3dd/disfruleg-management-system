# -*- coding: utf-8 -*-
"""
Domain Exceptions - Analytics Module
Custom exceptions for business rule violations
"""


class AnalyticsDomainError(Exception):
    """Base exception for analytics domain errors"""
    pass


class DataNotFoundError(AnalyticsDomainError):
    """Raised when requested data is not found"""
    pass


class InvalidDateRangeError(AnalyticsDomainError):
    """Raised when date range is invalid"""
    pass


class InvalidMetricError(AnalyticsDomainError):
    """Raised when metric type is invalid"""
    pass


class CacheError(AnalyticsDomainError):
    """Raised when cache operations fail"""
    pass
