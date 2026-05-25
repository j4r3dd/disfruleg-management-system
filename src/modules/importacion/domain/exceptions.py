# -*- coding: utf-8 -*-
"""
Domain Exceptions - Importacion Module
Custom exceptions for business rule violations
"""


class ImportacionDomainError(Exception):
    """Base exception for importacion domain errors"""
    pass


class PDFExtractionError(ImportacionDomainError):
    """Raised when PDF extraction fails"""
    pass


class InvalidProductDataError(ImportacionDomainError):
    """Raised when product data is invalid"""
    pass


class ProductMatchError(ImportacionDomainError):
    """Raised when product matching fails"""
    pass


class PriceApplicationError(ImportacionDomainError):
    """Raised when price application fails"""
    pass


class ReportGenerationError(ImportacionDomainError):
    """Raised when report generation fails"""
    pass


class SystemIntegrityError(ImportacionDomainError):
    """Raised when system integrity check fails"""
    pass
