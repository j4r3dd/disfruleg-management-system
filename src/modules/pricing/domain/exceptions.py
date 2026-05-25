# -*- coding: utf-8 -*-
"""
Domain Exceptions - Pricing Module
Custom exceptions for business rule violations
"""


class PricingDomainError(Exception):
    """Base exception for pricing domain errors"""
    pass


class ProductNotFoundError(PricingDomainError):
    """Raised when a product is not found"""
    pass


class GroupNotFoundError(PricingDomainError):
    """Raised when a group is not found"""
    pass


class ClientTypeNotFoundError(PricingDomainError):
    """Raised when a client type is not found"""
    pass


class InvalidPriceError(PricingDomainError):
    """Raised when a price value is invalid"""
    pass


class DuplicateProductError(PricingDomainError):
    """Raised when attempting to create a duplicate product"""
    pass


class ProductLockError(PricingDomainError):
    """Raised when a product is locked by another user"""
    pass
