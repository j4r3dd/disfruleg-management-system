# -*- coding: utf-8 -*-
"""
Domain Models - Domain Layer
Core business entities for the ubicuoai module
All models include validation and business logic
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

from .value_objects import MatchMethod, Unit
from .exceptions import InvalidQuantityError, InvalidProductNameError


@dataclass
class OrderItem:
    """
    Represents a parsed item from an order
    """
    raw_text: str
    product_name: str
    quantity: Decimal
    unit: Unit
    confidence: float
    line_number: int
    is_section: bool = False  # True if this is a section header
    section: Optional[str] = None  # Name of the section this item belongs to
    needs_review: bool = False  # True if item couldn't be parsed with standard format

    def __post_init__(self):
        """Validate order item (Fail Fast)"""
        # Validate raw text
        if not self.raw_text or not self.raw_text.strip():
            raise ValueError("Raw text cannot be empty")

        # Validate product name
        if not self.product_name or not self.product_name.strip():
            raise InvalidProductNameError("Product name cannot be empty")

        if len(self.product_name) > 200:
            raise InvalidProductNameError("Product name too long (max 200 chars)")

        # Validate quantity (allow 0 for sections)
        if not self.is_section and self.quantity <= 0:
            raise InvalidQuantityError(
                f"Quantity must be positive (got {self.quantity})"
            )

        if self.quantity > Decimal('10000'):
            raise InvalidQuantityError(
                f"Quantity unreasonably high (got {self.quantity})"
            )

        # Validate unit
        if not isinstance(self.unit, Unit):
            raise ValueError("Unit must be a Unit enum value")

        # Validate confidence
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        # Validate line number
        if self.line_number < 1:
            raise ValueError("Line number must be at least 1")

    @property
    def formatted_quantity(self) -> str:
        """Get formatted quantity string"""
        return f"{self.quantity} {self.unit.value}"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'raw_text': self.raw_text,
            'product_name': self.product_name,
            'quantity': float(self.quantity),
            'unit': self.unit.value,
            'confidence': self.confidence,
            'line_number': self.line_number,
            'is_section': self.is_section,
            'section': self.section,
            'needs_review': self.needs_review
        }


@dataclass
class ProductMatch:
    """
    Represents a matched product from database
    """
    query: str
    matched_id: int
    matched_name: str
    confidence: float
    method: MatchMethod
    category: Optional[str] = None
    unit: Optional[Unit] = None
    price: Optional[Decimal] = None
    stock: Optional[Decimal] = None
    has_price: bool = True  # False if product has no price for selected group

    def __post_init__(self):
        """Validate product match (Fail Fast)"""
        # Validate query
        if not self.query or not self.query.strip():
            raise ValueError("Query cannot be empty")

        # Validate matched ID
        if self.matched_id <= 0:
            raise ValueError("Matched product ID must be positive")

        # Validate matched name
        if not self.matched_name or not self.matched_name.strip():
            raise ValueError("Matched product name cannot be empty")

        # Validate confidence
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        # Validate method
        if not isinstance(self.method, MatchMethod):
            raise ValueError("Method must be a MatchMethod enum value")

        # Validate price if provided
        if self.price is not None and self.price < 0:
            raise ValueError("Price cannot be negative")

        # Validate stock if provided
        #if self.stock is not None and self.stock < 0:
         #   raise ValueError("Stock cannot be negative")

    @property
    def is_high_confidence(self) -> bool:
        """Check if match has high confidence (>= 75%)"""
        return self.confidence >= 0.75

    @property
    def is_exact_match(self) -> bool:
        """Check if match was exact"""
        return self.method == MatchMethod.EXACT
    
    @property
    def needs_price_attention(self) -> bool:
        """Check if product needs attention due to missing price"""
        return not self.has_price or self.price is None or self.price <= 0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'query': self.query,
            'matched_id': self.matched_id,
            'matched_name': self.matched_name,
            'confidence': self.confidence,
            'method': self.method.value,
            'category': self.category,
            'unit': self.unit.value if self.unit else None,
            'price': float(self.price) if self.price else None,
            'stock': float(self.stock) if self.stock else None,
            'has_price': self.has_price
        }


@dataclass
class LearningCorrection:
    """
    Represents a learning correction entry
    """
    incorrect: str
    correct: str
    times_used: int
    first_added: datetime
    last_used: datetime
    confidence_boost: float = 0.05

    def __post_init__(self):
        """Validate learning correction (Fail Fast)"""
        # Validate incorrect text
        if not self.incorrect or not self.incorrect.strip():
            raise ValueError("Incorrect text cannot be empty")

        # Validate correct text
        if not self.correct or not self.correct.strip():
            raise ValueError("Correct text cannot be empty")

        # Validate they are different
        if self.incorrect.strip().lower() == self.correct.strip().lower():
            raise ValueError("Incorrect and correct text must be different")

        # Validate times_used
        if self.times_used < 1:
            raise ValueError("Times used must be at least 1")

        # Validate confidence boost
        if not 0.0 <= self.confidence_boost <= 1.0:
            raise ValueError("Confidence boost must be between 0.0 and 1.0")

        # Validate dates
        if self.last_used < self.first_added:
            raise ValueError("Last used date cannot be before first added date")

    def increment_usage(self):
        """Increment usage counter and update last used timestamp"""
        self.times_used += 1
        self.last_used = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'incorrect': self.incorrect,
            'correct': self.correct,
            'times_used': self.times_used,
            'first_added': self.first_added.isoformat(),
            'last_used': self.last_used.isoformat(),
            'confidence_boost': self.confidence_boost
        }


@dataclass
class OrderParseResult:
    """
    Result of parsing an order
    Contains all parsed items and statistics
    """
    items: List[OrderItem]
    total_items: int
    average_confidence: float
    low_confidence_items: List[OrderItem]

    def __post_init__(self):
        """Validate parse result"""
        # Validate total items matches list length
        if self.total_items != len(self.items):
            raise ValueError(
                f"Total items ({self.total_items}) doesn't match items list length ({len(self.items)})"
            )

        # Validate average confidence
        if self.items and not 0.0 <= self.average_confidence <= 1.0:
            raise ValueError("Average confidence must be between 0.0 and 1.0")

        # Validate low confidence items are subset of items
        for low_conf_item in self.low_confidence_items:
            if low_conf_item not in self.items:
                raise ValueError("Low confidence items must be subset of all items")

    @property
    def high_confidence_count(self) -> int:
        """Get count of high confidence items (>= 70%)"""
        return sum(1 for item in self.items if item.confidence >= 0.7)

    @property
    def success_rate(self) -> float:
        """Get success rate (percentage of items with >= 70% confidence)"""
        if not self.items:
            return 0.0
        return self.high_confidence_count / len(self.items)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'items': [item.to_dict() for item in self.items],
            'total_items': self.total_items,
            'average_confidence': self.average_confidence,
            'high_confidence_count': self.high_confidence_count,
            'success_rate': self.success_rate,
            'low_confidence_items': [item.to_dict() for item in self.low_confidence_items]
        }