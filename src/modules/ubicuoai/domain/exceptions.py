# -*- coding: utf-8 -*-
"""
Custom Exceptions - Domain Layer
Domain-specific exceptions for the ubicuoai module
"""


class UbicuoAIError(Exception):
    """Base exception for all UbicuoAI domain errors"""
    pass


class ProductNotFoundError(UbicuoAIError):
    """Raised when a product cannot be matched"""
    pass


class InvalidOrderFormatError(UbicuoAIError):
    """Raised when order text format is invalid"""
    pass


class InvalidQuantityError(UbicuoAIError):
    """Raised when quantity is invalid (zero, negative, or unreasonable)"""
    pass


class LearningError(UbicuoAIError):
    """Raised when learning system encounters an error"""
    pass


class InvalidProductNameError(UbicuoAIError):
    """Raised when product name is invalid"""
    pass


class ConfigurationError(UbicuoAIError):
    """Raised when configuration is invalid or missing"""
    pass


class DatabaseError(UbicuoAIError):
    """Raised when database operation fails"""
    pass


class MatchingError(UbicuoAIError):
    """Raised when matching process fails"""
    pass


class ParsingError(UbicuoAIError):
    """Raised when parsing process fails"""
    pass


class SectionError(UbicuoAIError):
    """Raised when section management fails"""
    pass


class ClientError(UbicuoAIError):
    """Raised when client operation fails"""
    pass


class PriceNotFoundError(UbicuoAIError):
    """Raised when price cannot be found for a product"""
    pass


class ValidationError(UbicuoAIError):
    """Raised when validation fails"""
    pass
