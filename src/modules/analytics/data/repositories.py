# -*- coding: utf-8 -*-
"""
Repository Interfaces - Analytics Module
Define protocols for data access (Interface Segregation)
"""

from typing import Protocol, List, Optional, Dict, Tuple
from datetime import datetime

from ..domain.models import (
    ProductAnalytics,
    ClientAnalytics,
    GroupAnalytics,
    SalesTrend,
    OverallMetrics,
    DateRange
)


class IProductAnalyticsRepository(Protocol):
    """Interface for product analytics data access"""

    def get_top_products(self, limit: int = 10) -> List[ProductAnalytics]:
        """Get top products by sales volume"""
        ...

    def get_product_detail(
        self,
        product_id: int,
        date_range: DateRange,
        metric: str = 'cantidad'
    ) -> Dict:
        """
        Get detailed product information with history

        Returns:
            Dict with historial_ventas, top_clientes, producto_info
        """
        ...

    def search_products(self, search_term: str, limit: int = 20) -> List[ProductAnalytics]:
        """Search products by name"""
        ...


class IClientAnalyticsRepository(Protocol):
    """Interface for client analytics data access"""

    def get_top_clients(self, limit: int = 10) -> List[ClientAnalytics]:
        """Get top clients by sales volume"""
        ...

    def get_client_detail(
        self,
        client_id: int,
        date_range: DateRange,
        metric: str = 'ventas'
    ) -> Dict:
        """
        Get detailed client information with history

        Returns:
            Dict with historial_compras, top_productos, deudas
        """
        ...

    def search_clients(self, search_term: str, limit: int = 20) -> List[ClientAnalytics]:
        """Search clients by name or group"""
        ...

    def get_clients_with_debts(self):
        """
        Get all clients with pending debts
        Returns List of ClientDebtSummary from deudas module
        """
        ...


class IGroupAnalyticsRepository(Protocol):
    """Interface for group analytics data access"""

    def get_groups_summary(self) -> List[GroupAnalytics]:
        """Get summary for all groups"""
        ...

    def get_group_by_id(self, group_id: int) -> Optional[GroupAnalytics]:
        """Get group analytics by ID"""
        ...


class ISalesTrendRepository(Protocol):
    """Interface for sales trend data access"""

    def get_sales_trend(self, days: int = 30) -> List[SalesTrend]:
        """Get sales trend for specified days"""
        ...

    def get_sales_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[SalesTrend]:
        """Get sales data for specific date range"""
        ...

    def get_sales_comparison(self, days: int = 30) -> Dict:
        """
        Compare sales between current and previous period

        Returns:
            Dict with current, previous, growth_percentage
        """
        ...


class IAnalyticsRepository(Protocol):
    """Interface for overall analytics data access"""

    def get_overall_metrics(self) -> OverallMetrics:
        """Get overall business metrics KPIs"""
        ...


class ICacheRepository(Protocol):
    """Interface for cache management"""

    def get(self, key: str) -> Optional[any]:
        """Get cached data by key"""
        ...

    def set(self, key: str, data: any, ttl: Optional[int] = None) -> None:
        """Set data in cache with optional TTL (seconds)"""
        ...

    def is_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        ...

    def clear(self) -> None:
        """Clear all cached data"""
        ...

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        ...
