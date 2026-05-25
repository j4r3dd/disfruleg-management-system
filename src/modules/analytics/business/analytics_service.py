# -*- coding: utf-8 -*-
"""
Analytics Service - Business Logic
Handles analytics operations and calculations
NO direct database access - uses repositories only!
"""

from typing import List, Optional, Dict
from decimal import Decimal

from ..data.repositories import (
    IAnalyticsRepository,
    IProductAnalyticsRepository,
    IClientAnalyticsRepository,
    IGroupAnalyticsRepository,
    ISalesTrendRepository,
    ICacheRepository
)
from ..domain.models import (
    ProductAnalytics,
    ClientAnalytics,
    GroupAnalytics,
    SalesTrend,
    OverallMetrics,
    DateRange
)
from ..domain.exceptions import (
    DataNotFoundError,
    InvalidDateRangeError,
    InvalidMetricError
)


class AnalyticsService:
    """
    Analytics business service
    Handles analytics operations, data retrieval, and calculations
    """

    def __init__(
        self,
        analytics_repo: IAnalyticsRepository,
        product_repo: IProductAnalyticsRepository,
        client_repo: IClientAnalyticsRepository,
        group_repo: IGroupAnalyticsRepository,
        sales_trend_repo: ISalesTrendRepository,
        cache_repo: ICacheRepository
    ):
        """
        Initialize service with injected dependencies

        Args:
            analytics_repo: Overall analytics repository
            product_repo: Product analytics repository
            client_repo: Client analytics repository
            group_repo: Group analytics repository
            sales_trend_repo: Sales trend repository
            cache_repo: Cache repository
        """
        self.analytics_repo = analytics_repo
        self.product_repo = product_repo
        self.client_repo = client_repo
        self.group_repo = group_repo
        self.sales_trend_repo = sales_trend_repo
        self.cache_repo = cache_repo

    # ==================== OVERALL METRICS ====================

    def get_overall_metrics(self) -> OverallMetrics:
        """
        Get overall business metrics

        Returns:
            OverallMetrics with KPIs

        Raises:
            DataNotFoundError: If metrics cannot be retrieved
        """
        cache_key = "overall_metrics"
        cached = self.cache_repo.get(cache_key)
        if cached:
            return cached

        metrics = self.analytics_repo.get_overall_metrics()

        if not metrics:
            raise DataNotFoundError("Unable to retrieve overall metrics")

        self.cache_repo.set(cache_key, metrics)
        return metrics

    # ==================== PRODUCT ANALYTICS ====================

    def get_top_products(self, limit: int = 10, period: Optional[str] = None) -> List[ProductAnalytics]:
        """
        Get top products by profit (ganancia_total)

        Args:
            limit: Maximum number of products to return
            period: Optional period string (1D, 7D, 30D, 90D, 1Y, ALL) for date filtering

        Returns:
            List of ProductAnalytics

        Raises:
            ValueError: If limit is invalid
            InvalidMetricError: If period is invalid
        """
        # Fail fast: Validate limit
        if limit <= 0:
            raise ValueError("Limit must be positive")

        # Create cache key with period
        cache_key = f"top_products_{limit}_{period or 'all'}"
        cached = self.cache_repo.get(cache_key)
        if cached:
            return cached

        # Get date range if period is provided
        date_range = None
        if period:
            date_range = DateRange.from_period(period)

        products = self.product_repo.get_top_products(limit, date_range)
        self.cache_repo.set(cache_key, products)
        return products

    def get_product_detail(
        self,
        product_id: int,
        period: str = '30D',
        metric: str = 'cantidad'
    ) -> Dict:
        """
        Get detailed product information with history

        Args:
            product_id: Product ID
            period: Period string (1D, 7D, 30D, 90D, 1Y, ALL)
            metric: Metric type (cantidad, ventas, ganancia)

        Returns:
            Dict with historial_ventas, top_clientes, producto_info

        Raises:
            ValueError: If product_id is invalid
            DataNotFoundError: If product not found
            InvalidMetricError: If metric is invalid
        """
        # Fail fast: Validate inputs
        if product_id <= 0:
            raise ValueError("Product ID must be positive")

        valid_metrics = ['cantidad', 'ventas', 'ganancia']
        if metric not in valid_metrics:
            raise InvalidMetricError(f"Invalid metric: {metric}. Must be one of {valid_metrics}")

        # Get date range
        date_range = DateRange.from_period(period)

        # Get detail
        detail = self.product_repo.get_product_detail(product_id, date_range, metric)

        if not detail:
            raise DataNotFoundError(f"Product {product_id} not found")

        return detail

    def search_products(self, search_term: str, limit: int = 20) -> List[ProductAnalytics]:
        """
        Search products by name

        Args:
            search_term: Search term
            limit: Maximum results

        Returns:
            List of ProductAnalytics

        Raises:
            ValueError: If search_term is empty or limit is invalid
        """
        # Fail fast: Validate inputs
        if not search_term or not search_term.strip():
            raise ValueError("Search term cannot be empty")

        if limit <= 0:
            raise ValueError("Limit must be positive")

        return self.product_repo.search_products(search_term, limit)

    # ==================== CLIENT ANALYTICS ====================

    def get_top_clients(self, limit: int = 10, period: Optional[str] = None) -> List[ClientAnalytics]:
        """
        Get top clients by sales volume

        Args:
            limit: Maximum number of clients to return
            period: Optional period string (1D, 7D, 30D, 90D, 1Y, ALL) for date filtering

        Returns:
            List of ClientAnalytics

        Raises:
            ValueError: If limit is invalid
            InvalidMetricError: If period is invalid
        """
        # Fail fast: Validate limit
        if limit <= 0:
            raise ValueError("Limit must be positive")

        # Create cache key with period
        cache_key = f"top_clients_{limit}_{period or 'all'}"
        cached = self.cache_repo.get(cache_key)
        if cached:
            return cached

        # Get date range if period is provided
        date_range = None
        if period:
            date_range = DateRange.from_period(period)

        clients = self.client_repo.get_top_clients(limit, date_range)
        self.cache_repo.set(cache_key, clients)
        return clients

    def get_client_detail(
        self,
        client_id: int,
        period: str = '30D',
        metric: str = 'ventas'
    ) -> Dict:
        """
        Get detailed client information with history

        Args:
            client_id: Client ID
            period: Period string (1D, 7D, 30D, 90D, 1Y, ALL)
            metric: Metric type (ventas, cantidad, facturas)

        Returns:
            Dict with historial_compras, top_productos, deudas, cliente_info

        Raises:
            ValueError: If client_id is invalid
            DataNotFoundError: If client not found
            InvalidMetricError: If metric is invalid
        """
        # Fail fast: Validate inputs
        if client_id <= 0:
            raise ValueError("Client ID must be positive")

        valid_metrics = ['ventas', 'cantidad', 'facturas']
        if metric not in valid_metrics:
            raise InvalidMetricError(f"Invalid metric: {metric}. Must be one of {valid_metrics}")

        # Get date range
        date_range = DateRange.from_period(period)

        # Get detail
        detail = self.client_repo.get_client_detail(client_id, date_range, metric)

        if not detail:
            raise DataNotFoundError(f"Client {client_id} not found")

        return detail

    def search_clients(self, search_term: str, limit: int = 20) -> List[ClientAnalytics]:
        """
        Search clients by name or group

        Args:
            search_term: Search term
            limit: Maximum results

        Returns:
            List of ClientAnalytics

        Raises:
            ValueError: If search_term is empty or limit is invalid
        """
        # Fail fast: Validate inputs
        if not search_term or not search_term.strip():
            raise ValueError("Search term cannot be empty")

        if limit <= 0:
            raise ValueError("Limit must be positive")

        return self.client_repo.search_clients(search_term, limit)

    def get_clients_with_debts(self):
        """
        Get all clients with pending debts

        Returns:
            List of ClientDebtSummary with pending debts, ordered by debt amount
        """
        cache_key = "clients_with_debts"
        cached = self.cache_repo.get(cache_key)
        if cached:
            return cached

        clients = self.client_repo.get_clients_with_debts()
        self.cache_repo.set(cache_key, clients)
        return clients

    # ==================== GROUP ANALYTICS ====================

    def get_groups_summary(self, period: Optional[str] = None) -> List[GroupAnalytics]:
        """
        Get summary for all groups

        Args:
            period: Optional period string (1D, 7D, 30D, 90D, 1Y, ALL) for date filtering

        Returns:
            List of GroupAnalytics

        Raises:
            InvalidMetricError: If period is invalid
        """
        # Create cache key with period
        cache_key = f"groups_summary_{period or 'all'}"
        cached = self.cache_repo.get(cache_key)
        if cached:
            return cached

        # Get date range if period is provided
        date_range = None
        if period:
            date_range = DateRange.from_period(period)

        groups = self.group_repo.get_groups_summary(date_range)
        self.cache_repo.set(cache_key, groups)
        return groups

    def get_group_by_id(self, group_id: int) -> GroupAnalytics:
        """
        Get group analytics by ID

        Args:
            group_id: Group ID

        Returns:
            GroupAnalytics

        Raises:
            ValueError: If group_id is invalid
            DataNotFoundError: If group not found
        """
        # Fail fast: Validate ID
        if group_id <= 0:
            raise ValueError("Group ID must be positive")

        group = self.group_repo.get_group_by_id(group_id)

        if not group:
            raise DataNotFoundError(f"Group {group_id} not found")

        return group

    # ==================== SALES TREND ====================

    def get_sales_trend(self, period: str = '7D') -> List[SalesTrend]:
        """
        Get sales trend for specified period

        Args:
            period: Period string (1D, 7D, 30D, 90D, 1Y)

        Returns:
            List of SalesTrend

        Raises:
            InvalidDateRangeError: If period is invalid
        """
        # Get date range
        date_range = DateRange.from_period(period)

        cache_key = f"sales_trend_{period}"
        cached = self.cache_repo.get(cache_key)
        if cached:
            return cached

        trend = self.sales_trend_repo.get_sales_trend(date_range.days)
        self.cache_repo.set(cache_key, trend)
        return trend

    def get_sales_by_date_range(
        self,
        start_date,
        end_date
    ) -> List[SalesTrend]:
        """
        Get sales data for specific date range

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of SalesTrend

        Raises:
            InvalidDateRangeError: If date range is invalid
        """
        # Fail fast: Validate dates
        if start_date > end_date:
            raise InvalidDateRangeError("Start date cannot be after end date")

        return self.sales_trend_repo.get_sales_by_date_range(start_date, end_date)

    def get_sales_comparison(self, period: str = '30D') -> Dict:
        """
        Compare sales between current and previous period

        Args:
            period: Period string (1D, 7D, 30D, 90D)

        Returns:
            Dict with current, previous, growth_percentage

        Raises:
            InvalidDateRangeError: If period is invalid
        """
        # Get date range
        date_range = DateRange.from_period(period)

        return self.sales_trend_repo.get_sales_comparison(date_range.days)

    # ==================== CACHE MANAGEMENT ====================

    def refresh_cache(self) -> None:
        """Clear all cached data to force refresh"""
        self.cache_repo.clear()

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache_repo.get_stats()
