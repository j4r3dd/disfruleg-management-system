# -*- coding: utf-8 -*-
"""
UI Layer - Analytics Module
User interface components
"""

from .analizador_ganancias_app import AnalisisGananciasApp
from .ui_components import (
    StatCard,
    MetricRow,
    LoadingIndicator,
    SearchBar,
    NoDataMessage,
    FilterBar
)
from .product_detail_dialog import ProductDetailDialog
from .client_detail_dialog import ClientDetailDialog
from .export_dialog import ExportDialog, ExportProgressDialog
from .export_manager import ExportManager, ChartExporter

__all__ = [
    "AnalisisGananciasApp",
    "StatCard",
    "MetricRow",
    "LoadingIndicator",
    "SearchBar",
    "NoDataMessage",
    "FilterBar",
    "ProductDetailDialog",
    "ClientDetailDialog",
    "ExportDialog",
    "ExportProgressDialog",
    "ExportManager",
    "ChartExporter",
]
