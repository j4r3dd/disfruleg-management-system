# -*- coding: utf-8 -*-
"""
Domain Layer - Importacion Module
"""

from .models import (
    ExtractedProduct,
    ProductChange,
    ProductMatch,
    ImportReport,
    SystemIntegrityCheck
)

from .exceptions import (
    ImportacionDomainError,
    PDFExtractionError,
    InvalidProductDataError,
    ProductMatchError,
    PriceApplicationError,
    ReportGenerationError,
    SystemIntegrityError
)

__all__ = [
    # Models
    'ExtractedProduct',
    'ProductChange',
    'ProductMatch',
    'ImportReport',
    'SystemIntegrityCheck',
    # Exceptions
    'ImportacionDomainError',
    'PDFExtractionError',
    'InvalidProductDataError',
    'ProductMatchError',
    'PriceApplicationError',
    'ReportGenerationError',
    'SystemIntegrityError',
]
