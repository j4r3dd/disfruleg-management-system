# -*- coding: utf-8 -*-
"""
UbicuoAI Manager - Module Entry Point
Handles dependency injection and module initialization
Integrates with the project's database system
"""

from typing import Optional

from src.database.conexion import conectar, return_connection

from .data.mysql_repositories import MySQLClientRepository, MySQLProductRepository, MySQLLearningRepository
from .business.parser_service import EnhancedParserService
from .business.matcher_service import MatcherService
from .business.learning_service import LearningService
from .business.ubicuoai_service import EnhancedUbicuoAIService

# Import inventory services for product creation
from ..inventory.business.product_service import ProductService
from ..inventory.data.mysql_repositories import MySQLProductRepository as InventoryProductRepository


class UbicuoAIManager:
    """
    Manager class for UbicuoAI module
    Handles dependency injection and lifecycle management
    Follows Clean Architecture with proper DI
    """

    def __init__(self):
        """Initialize manager (services created on demand)"""
        self._service: Optional[EnhancedUbicuoAIService] = None
        self._product_service: Optional[ProductService] = None
        self._initialized = False
        self._connection = None  # Store connection for proper cleanup

    def initialize(self) -> dict:
        """
        Initialize the UbicuoAI module
        Sets up all dependencies with proper injection

        Returns:
            Dictionary with initialization statistics

        Raises:
            RuntimeError: If no database connection is available
        """
        # Get database connection (same pattern as deudas module)
        connection = conectar()
        self._connection = connection  # Store for cleanup

        # === DATA LAYER ===
        # Create repositories with injected connection
        client_repo = MySQLClientRepository(connection)
        product_repo = MySQLProductRepository(connection)
        learning_repo = MySQLLearningRepository(connection)

        # Create inventory repository for product creation
        inventory_product_repo = InventoryProductRepository(connection)

        # === BUSINESS LAYER ===
        # Create services with injected repositories
        parser_service = EnhancedParserService()
        matcher_service = MatcherService(
            product_repo=product_repo,
            threshold=0.75
        )
        learning_service = LearningService(
            learning_repo=learning_repo
        )

        # Create main orchestrator service
        self._service = EnhancedUbicuoAIService(
            parser_service=parser_service,
            matcher_service=matcher_service,
            learning_service=learning_service,
            client_repo=client_repo
        )

        # Create product service for creating new products
        self._product_service = ProductService(inventory_product_repo)

        # Initialize the service (load products and corrections)
        init_stats = self._service.initialize()

        self._initialized = True

        return {
            'success': True,
            'message': 'UbicuoAI initialized successfully',
            **init_stats
        }

    def get_service(self) -> EnhancedUbicuoAIService:
        """
        Get the main UbicuoAI service

        Returns:
            EnhancedUbicuoAIService instance

        Raises:
            RuntimeError: If module not initialized
        """
        if not self._initialized or not self._service:
            raise RuntimeError(
                "UbicuoAI module not initialized. Call initialize() first."
            )

        return self._service

    def get_product_service(self) -> ProductService:
        """
        Get the product service for creating products

        Returns:
            ProductService instance

        Raises:
            RuntimeError: If module not initialized
        """
        if not self._initialized or not self._product_service:
            raise RuntimeError(
                "UbicuoAI module not initialized. Call initialize() first."
            )

        return self._product_service

    def is_initialized(self) -> bool:
        """Check if module is initialized"""
        return self._initialized

    def shutdown(self):
        """Shutdown the module (cleanup)"""
        # Return connection to pool before clearing everything
        if self._connection:
            return_connection(self._connection)
            self._connection = None
        self._service = None
        self._product_service = None
        self._initialized = False


# Global instance for use throughout the application
ubicuoai_manager = UbicuoAIManager()


# Convenience functions for easy access
def get_ubicuoai_service() -> EnhancedUbicuoAIService:
    """
    Get the UbicuoAI service instance

    Returns:
        EnhancedUbicuoAIService instance

    Raises:
        RuntimeError: If not initialized
    """
    return ubicuoai_manager.get_service()


def get_product_service() -> ProductService:
    """
    Get the product service instance

    Returns:
        ProductService instance

    Raises:
        RuntimeError: If not initialized
    """
    return ubicuoai_manager.get_product_service()


def initialize_ubicuoai() -> dict:
    """
    Initialize UbicuoAI module

    Returns:
        Initialization statistics
    """
    return ubicuoai_manager.initialize()


def is_ubicuoai_initialized() -> bool:
    """Check if UbicuoAI is initialized"""
    return ubicuoai_manager.is_initialized()
