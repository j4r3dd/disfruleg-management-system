# -*- coding: utf-8 -*-
"""
Enhanced UbicuoAI Service - Business Logic Layer
Procesa TODOS los productos del pedido, incluso si no hay match en la base de datos
"""

from typing import List, Optional, Tuple, Dict

from .parser_service import EnhancedParserService
from .matcher_service import MatcherService
from .learning_service import LearningService

from ..data.repositories import IClientRepository
from ..domain.models import OrderItem, ProductMatch, OrderParseResult
from ..domain.value_objects import Unit, MatchMethod


class EnhancedUbicuoAIService:
    """
    Servicio mejorado que procesa TODOS los productos del pedido
    - Captura todas las líneas (incluyendo secciones)
    - Mantiene productos sin match para revisión manual
    - Proporciona estadísticas detalladas
    """

    def __init__(
        self,
        parser_service: EnhancedParserService,
        matcher_service: MatcherService,
        learning_service: LearningService,
        client_repo: IClientRepository
    ):
        """
        Initialize with injected services

        Args:
            parser_service: Enhanced parser service instance
            matcher_service: Matcher service instance
            learning_service: Learning service instance
            client_repo: Client repository interface
        """
        self.parser = parser_service
        self.matcher = matcher_service
        self.learning = learning_service
        self.client_repo = client_repo

        # Current selected client/group for pricing
        self.current_client_id: Optional[int] = None
        self.current_group_id: Optional[int] = None

    def initialize(self) -> dict:
        """
        Initialize the system
        Loads products and learning corrections

        Returns:
            Dictionary with initialization stats
        """
        # Load products into matcher cache
        products_loaded = self.matcher.load_products()

        # Load learning corrections
        corrections = self.learning.get_all_corrections()
        self.matcher.set_learning_dictionary(corrections)

        return {
            'products_loaded': products_loaded,
            'corrections_loaded': len(corrections)
        }

    def process_order(
        self,
        order_text: str
    ) -> Tuple[OrderParseResult, List[Optional[ProductMatch]], Dict]:
        """
        Procesa TODO el pedido - incluyendo productos sin match

        Args:
            order_text: Raw order text from WhatsApp

        Returns:
            Tuple of (OrderParseResult, List of ProductMatch or None, Statistics dict)
        """
        # Step 1: Parse the order text - CAPTURA TODO
        parse_result = self.parser.parse_order_text(order_text)

        # Step 2: Match each parsed item to products
        matches: List[Optional[ProductMatch]] = []
        unmatched_items = []
        sections = []
        
        for item in parse_result.items:
            # Skip section headers from matching
            if item.is_section:
                sections.append(item)
                matches.append(None)
                continue
                
            # Try to match the product
            match = None
            try:
                match = self.matcher.match_product(
                    item.product_name,
                    item.unit
                )
            except Exception as e:
                # Si hay error en el matching, continuamos
                print(f"Error matching {item.product_name}: {e}")
            
            matches.append(match)
            
            # Track unmatched items for reporting
            if match is None:
                unmatched_items.append(item)

        # Step 3: Generate comprehensive statistics
        statistics = self._generate_statistics(
            parse_result,
            matches,
            unmatched_items,
            sections
        )

        return parse_result, matches, statistics

    def _generate_statistics(
        self,
        parse_result: OrderParseResult,
        matches: List[Optional[ProductMatch]],
        unmatched_items: List[OrderItem],
        sections: List[OrderItem]
    ) -> Dict:
        """
        Genera estadísticas detalladas del procesamiento
        """
        total_items = len([item for item in parse_result.items if not item.is_section])
        matched_count = sum(1 for m in matches if m is not None)
        unmatched_count = len(unmatched_items)
        
        # Calculate match rate (excluding sections)
        match_rate = (matched_count / total_items * 100) if total_items > 0 else 0
        
        # Get items that need review
        needs_review = [
            item for item in parse_result.items 
            if item.needs_review and not item.is_section
        ]
        
        # Confidence breakdown
        high_confidence = sum(1 for m in matches if m and m.confidence >= 0.8)
        medium_confidence = sum(1 for m in matches if m and 0.6 <= m.confidence < 0.8)
        low_confidence = sum(1 for m in matches if m and m.confidence < 0.6)
        
        return {
            'total_lines_processed': len(parse_result.items),
            'total_products': total_items,
            'matched_products': matched_count,
            'unmatched_products': unmatched_count,
            'match_rate': round(match_rate, 1),
            'sections_detected': len(sections),
            'needs_review': len(needs_review),
            'confidence_breakdown': {
                'high': high_confidence,
                'medium': medium_confidence,
                'low': low_confidence
            },
            'unmatched_items': [
                {
                    'line': item.line_number,
                    'text': item.raw_text,
                    'parsed_as': item.product_name,
                    'quantity': float(item.quantity),
                    'unit': item.unit.value,
                    'section': item.section
                }
                for item in unmatched_items
            ],
            'sections': [
                {
                    'line': section.line_number,
                    'name': section.product_name
                }
                for section in sections
            ]
        }

    def get_product_suggestions(
        self,
        product_name: str,
        limit: int = 5
    ) -> List[ProductMatch]:
        """
        Get product suggestions for a name

        Args:
            product_name: Product name to search
            limit: Maximum number of suggestions

        Returns:
            List of ProductMatch suggestions
        """
        return self.matcher.get_suggestions(product_name, limit)

    def find_products_with_different_units(
        self,
        product_name: str
    ) -> List[ProductMatch]:
        """
        Find all products with similar name but different units
        Example: "Cebolla KG" and "Cebolla PZ"

        Args:
            product_name: Product name to search for

        Returns:
            List of ProductMatch for all variants
        """
        return self.matcher.find_products_by_name_with_different_units(product_name)

    def match_single_product(
        self,
        product_name: str,
        unit_hint = None
    ) -> Optional[ProductMatch]:
        """
        Match a single product name against the database.
        Uses current group prices if a client is selected.
        
        Args:
            product_name: Product name to match
            unit_hint: Optional unit hint for better matching
            
        Returns:
            ProductMatch if found, None otherwise
        """
        try:
            return self.matcher.match_product(product_name, unit_hint)
        except Exception as e:
            print(f"Error matching single product '{product_name}': {e}")
            return None

    def learn_correction(
        self,
        incorrect: str,
        correct: str
    ) -> bool:
        """
        Learn a correction and update matcher

        Args:
            incorrect: Incorrect product name
            correct: Correct product name

        Returns:
            True if successful
        """
        success = self.learning.add_correction(incorrect, correct)

        if success:
            # Reload learning dictionary in matcher
            corrections = self.learning.get_all_corrections()
            self.matcher.set_learning_dictionary(corrections)

        return success

    def get_system_statistics(self) -> dict:
        """
        Get overall system statistics

        Returns:
            Dictionary with comprehensive stats
        """
        matcher_stats = self.matcher.get_statistics()
        learning_stats = self.learning.get_statistics()

        return {
            'matcher': matcher_stats,
            'learning': learning_stats
        }

    def get_all_clients(self) -> List[Dict]:
        """
        Get all active clients

        Returns:
            List of client dictionaries
        """
        return self.client_repo.get_all_clients()

    def set_selected_client(self, client_id: Optional[int]) -> Optional[Dict]:
        """
        Set the selected client for pricing

        Args:
            client_id: Client ID to select, or None to clear selection

        Returns:
            Selected client data or None
        """
        if client_id is None:
            self.current_client_id = None
            self.current_group_id = None
            # Clear group in matcher
            self.matcher.set_group_for_pricing(None)
            # Reload all products (no group filter)
            self.matcher.load_products(None)
            return None

        client = self.client_repo.get_client_by_id(client_id)
        if client:
            self.current_client_id = client_id
            self.current_group_id = client['id_grupo']
            # Set group in matcher for pricing
            self.matcher.set_group_for_pricing(self.current_group_id)
            # Reload products filtered by this group (only products with prices for this group)
            self.matcher.load_products(self.current_group_id)
            return client

        return None

    def get_selected_client(self) -> Optional[Dict]:
        """
        Get the currently selected client

        Returns:
            Client data or None if no client selected
        """
        if self.current_client_id:
            return self.client_repo.get_client_by_id(self.current_client_id)
        return None

    def reload_products(self) -> int:
        """
        Reload products in matcher cache
        Uses current group filter if a client is selected

        Returns:
            Number of products loaded
        """
        return self.matcher.load_products(self.current_group_id)