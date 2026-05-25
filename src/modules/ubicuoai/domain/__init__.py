# -*- coding: utf-8 -*-
"""
Domain Layer - UbicuoAI Module
Core business entities and value objects
"""

from .models import OrderItem, ProductMatch, LearningCorrection, OrderParseResult
from .value_objects import MatchMethod, Unit
from .exceptions import (
    UbicuoAIError,
    ProductNotFoundError,
    InvalidOrderFormatError,
    InvalidQuantityError,
    LearningError
)

__all__ = [
    # Models
    'OrderItem',
    'ProductMatch',
    'LearningCorrection',
    'OrderParseResult',

    # Value Objects
    'MatchMethod',
    'Unit',

    # Exceptions
    'UbicuoAIError',
    'ProductNotFoundError',
    'InvalidOrderFormatError',
    'InvalidQuantityError',
    'LearningError'
]
