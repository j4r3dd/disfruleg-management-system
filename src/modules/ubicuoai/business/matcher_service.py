# -*- coding: utf-8 -*-
"""
Matcher Service - Business Logic Layer
Handles product matching with fuzzy logic
NO direct database access - uses repositories only!
"""

from typing import List, Optional, Dict
from decimal import Decimal

try:
    from rapidfuzz import fuzz, process
    FUZZY_LIBRARY = 'rapidfuzz'
except ImportError:
    try:
        from fuzzywuzzy import fuzz, process
        FUZZY_LIBRARY = 'fuzzywuzzy'
    except ImportError:
        raise ImportError("Se requiere 'rapidfuzz' o 'fuzzywuzzy'. Instala con: pip install rapidfuzz")

from ..data.repositories import IProductRepository
from ..domain.models import ProductMatch
from ..domain.value_objects import MatchMethod, Unit
from ..domain.exceptions import ProductNotFoundError


class MatcherService:
    """
    Product matching service with fuzzy logic
    Coordinates between product repository and matching algorithms
    """

    def __init__(
        self,
        product_repo: IProductRepository,
        threshold: float = 0.75
    ):
        """
        Initialize matcher with injected dependencies

        Args:
            product_repo: Product repository interface
            threshold: Minimum confidence threshold for matches (0.0-1.0)
        """
        self.product_repo = product_repo
        self.threshold = threshold
        self.products_cache: Dict[str, dict] = {}
        self.learning_dict: Dict[str, str] = {}
        self.current_group_id: Optional[int] = None

    def load_products(self, group_id: Optional[int] = None) -> int:
        """
        Load products from database into cache
        
        Args:
            group_id: If provided, only loads products with prices for this group

        Returns:
            Number of products loaded
        """
        # Store the group_id for pricing
        if group_id:
            self.current_group_id = group_id
        
        products = self.product_repo.get_all_products(group_id)

        self.products_cache = {}
        for product in products:
            name_lower = product['nombre'].strip().lower()
            self.products_cache[name_lower] = product

        return len(self.products_cache)

    def set_learning_dictionary(self, learning_dict: Dict[str, str]) -> None:
        """
        Set learning corrections dictionary

        Args:
            learning_dict: Dict mapping incorrect -> correct names
        """
        self.learning_dict = {
            k.lower(): v.lower()
            for k, v in learning_dict.items()
        }

    def set_group_for_pricing(self, group_id: Optional[int]) -> None:
        """
        Set the group ID for price calculation

        Args:
            group_id: Group ID to use for pricing, or None for default
        """
        self.current_group_id = group_id

    def match_product(
        self,
        query: str,
        unit_hint: Optional[Unit] = None
    ) -> Optional[ProductMatch]:
        """
        Find best match for a product query

        Args:
            query: Product name to search for
            unit_hint: Optional unit hint for confidence boost

        Returns:
            ProductMatch or None if no suitable match found
        """
        # Fail fast: Validate query
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not self.products_cache:
            raise RuntimeError("Products not loaded. Call load_products() first.")

        query_lower = query.strip().lower()

        # Level 1: Exact match
        exact_match = self._exact_match(query_lower)
        if exact_match:
            return self._create_match_result(
                query, exact_match, 1.0, MatchMethod.EXACT, unit_hint
            )

        # Level 2: Learning dictionary
        learned_match = self._learned_match(query_lower)
        if learned_match:
            return self._create_match_result(
                query, learned_match, 0.95, MatchMethod.LEARNED, unit_hint
            )

        # Level 3: Fuzzy matching
        fuzzy_match = self._fuzzy_match(query_lower, unit_hint)
        if fuzzy_match:
            return fuzzy_match

        return None

    def get_suggestions(
        self,
        query: str,
        limit: int = 5
    ) -> List[ProductMatch]:
        """
        Get multiple suggestions for a query

        Args:
            query: Product name to search for
            limit: Maximum number of suggestions

        Returns:
            List of ProductMatch ordered by confidence
        """
        if not query or not self.products_cache:
            return []

        query_lower = query.strip().lower()
        product_names = list(self.products_cache.keys())

        # Use token_sort_ratio for better results
        results = process.extract(
            query_lower,
            product_names,
            scorer=fuzz.token_sort_ratio,
            limit=limit
        )

        suggestions = []
        for item in results:
            if FUZZY_LIBRARY == 'rapidfuzz':
                name, score, _ = item
            else:
                name, score = item[0], item[1]

            confidence = score / 100.0

            if confidence >= 0.5:  # Minimum threshold for suggestions
                product_data = self.products_cache[name]
                suggestions.append(
                    self._create_match_result(
                        query,
                        product_data,
                        confidence,
                        MatchMethod.FUZZY,
                        None
                    )
                )

        return suggestions

    def find_products_by_name_with_different_units(
        self,
        product_name: str
    ) -> List[ProductMatch]:
        """
        Find all products that match the given name but have different units
        Used to handle cases like "Cebolla KG" vs "Cebolla PZ"

        Args:
            product_name: Product name to search for

        Returns:
            List of ProductMatch for all products with similar names
        """
        if not product_name or not self.products_cache:
            return []

        query_lower = product_name.strip().lower()
        product_names = list(self.products_cache.keys())

        # Find all products with very high similarity (>90%)
        results = process.extract(
            query_lower,
            product_names,
            scorer=fuzz.token_sort_ratio,
            limit=10  # Get more to find all variants
        )

        matches = []
        for item in results:
            if FUZZY_LIBRARY == 'rapidfuzz':
                name, score, _ = item
            else:
                name, score = item[0], item[1]

            confidence = score / 100.0

            # Only include very close matches (>90%)
            if confidence >= 0.90:
                product_data = self.products_cache[name]
                matches.append(
                    self._create_match_result(
                        product_name,
                        product_data,
                        confidence,
                        MatchMethod.FUZZY,
                        None
                    )
                )

        return matches

    def _exact_match(self, query: str) -> Optional[dict]:
        """Find exact match in cache"""
        return self.products_cache.get(query)

    def _learned_match(self, query: str) -> Optional[dict]:
        """Find match using learning dictionary"""
        if query in self.learning_dict:
            corrected_name = self.learning_dict[query]
            return self.products_cache.get(corrected_name)
        return None

    def _fuzzy_match(
        self,
        query: str,
        unit_hint: Optional[Unit]
    ) -> Optional[ProductMatch]:
        """Perform fuzzy matching"""
        product_names = list(self.products_cache.keys())

        # Use token_sort_ratio for best results
        results = process.extract(
            query,
            product_names,
            scorer=fuzz.token_sort_ratio,
            limit=5
        )

        if not results:
            return None

        # Get best result
        if FUZZY_LIBRARY == 'rapidfuzz':
            best_match, score, _ = results[0]
        else:
            best_match, score = results[0][0], results[0][1]

        confidence = score / 100.0

        # Apply confidence boosts
        product_data = self.products_cache[best_match]
        confidence = self._apply_confidence_boosts(
            confidence,
            product_data,
            unit_hint
        )

        # Check threshold
        if confidence < self.threshold:
            return None

        return self._create_match_result(
            query,
            product_data,
            confidence,
            MatchMethod.FUZZY,
            unit_hint
        )

    def _apply_confidence_boosts(
        self,
        base_confidence: float,
        product_data: dict,
        unit_hint: Optional[Unit]
    ) -> float:
        """Apply confidence boosts based on additional criteria"""
        confidence = base_confidence

        # Boost for unit match
        if unit_hint and product_data.get('unidad'):
            product_unit_str = product_data['unidad']
            try:
                if Unit.are_equivalent(unit_hint.value, product_unit_str):
                    confidence += 0.15
            except ValueError:
                pass

        return min(confidence, 1.0)

    def _create_match_result(
        self,
        query: str,
        product_data: dict,
        confidence: float,
        method: MatchMethod,
        unit_hint: Optional[Unit]
    ) -> ProductMatch:
        """Create ProductMatch from data"""
        # Parse unit
        unit = None
        if product_data.get('unidad'):
            try:
                unit = Unit.normalize(product_data['unidad'])
            except ValueError:
                pass

        # Get price - check if product has valid price for current group
        price = product_data.get('precio')
        has_price = product_data.get('has_price', True)  # Default to True for backwards compatibility
        
        # If group is selected and price needs to be fetched
        if self.current_group_id and price is None:
            try:
                price = self.product_repo.get_product_price(
                    product_data['id'],
                    self.current_group_id
                )
                has_price = price is not None and price > 0
            except Exception:
                price = None
                has_price = False
        
        # Determine has_price based on actual price value
        if price is None or (isinstance(price, (int, float, Decimal)) and price <= 0):
            has_price = False

        return ProductMatch(
            query=query,
            matched_id=product_data['id'],
            matched_name=product_data['nombre'],
            confidence=confidence,
            method=method,
            category=product_data.get('categoria'),
            unit=unit,
            price=price,
            stock=product_data.get('stock'),
            has_price=has_price
        )

    def get_statistics(self) -> dict:
        """Get matcher statistics"""
        return {
            'products_in_cache': len(self.products_cache),
            'learning_entries': len(self.learning_dict),
            'threshold': self.threshold,
            'fuzzy_library': FUZZY_LIBRARY
        }