# -*- coding: utf-8 -*-
"""
Domain Models - Analytics Module
Pure business entities with no database dependencies
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List, Dict
from datetime import datetime, date

from .exceptions import InvalidDateRangeError, InvalidMetricError


@dataclass
class ProductAnalytics:
    """Product analytics entity"""
    id_producto: int
    nombre_producto: str
    unidad_producto: str
    cantidad_vendida: Decimal
    ingresos_totales: Decimal
    costos_totales: Decimal
    ganancia_total: Decimal
    margen_ganancia_porcentaje: Decimal
    stock: Decimal
    meses_inventario: Optional[Decimal] = None
    # New fields from updated database views
    precio_venta_promedio: Optional[Decimal] = None
    costo_unitario_promedio: Optional[Decimal] = None
    ganancia_por_unidad: Optional[Decimal] = None

    def __post_init__(self):
        """Validate product analytics data - Fail Fast"""
        if self.id_producto <= 0:
            raise ValueError("Product ID must be positive")

        if not self.nombre_producto or not self.nombre_producto.strip():
            raise ValueError("Product name cannot be empty")

        if self.cantidad_vendida < 0:
            raise ValueError("Quantity sold cannot be negative")

        if self.ingresos_totales < 0:
            raise ValueError("Total revenue cannot be negative")

        if self.costos_totales < 0:
            raise ValueError("Total costs cannot be negative")


@dataclass
class ClientAnalytics:
    """Client analytics entity"""
    id_cliente: int
    nombre_cliente: str
    clave_grupo: str
    tipo_cliente: str
    porcentaje_descuento: Decimal
    total_ventas: Decimal
    cantidad_facturas: int
    ultima_compra: Optional[date]
    saldo_pendiente: Decimal

    def __post_init__(self):
        """Validate client analytics data - Fail Fast"""
        if self.id_cliente <= 0:
            raise ValueError("Client ID must be positive")

        if not self.nombre_cliente or not self.nombre_cliente.strip():
            raise ValueError("Client name cannot be empty")

        if self.porcentaje_descuento < 0 or self.porcentaje_descuento > 100:
            raise ValueError("Discount percentage must be between 0 and 100")

        if self.total_ventas < 0:
            raise ValueError("Total sales cannot be negative")

        if self.cantidad_facturas < 0:
            raise ValueError("Invoice count cannot be negative")

        if self.saldo_pendiente < 0:
            raise ValueError("Outstanding balance cannot be negative")


@dataclass
class GroupAnalytics:
    """Group analytics entity"""
    id_grupo: int
    clave_grupo: str
    tipo_cliente: Optional[str]
    cantidad_clientes: int
    total_ventas: Decimal
    cantidad_facturas: int
    descuento_aplicado: Decimal
    ticket_promedio: Decimal

    def __post_init__(self):
        """Validate group analytics data - Fail Fast"""
        if self.id_grupo <= 0:
            raise ValueError("Group ID must be positive")

        if not self.clave_grupo or not self.clave_grupo.strip():
            raise ValueError("Group code cannot be empty")

        if self.cantidad_clientes < 0:
            raise ValueError("Client count cannot be negative")

        if self.total_ventas < 0:
            raise ValueError("Total sales cannot be negative")

        if self.cantidad_facturas < 0:
            raise ValueError("Invoice count cannot be negative")


@dataclass
class SalesTrend:
    """Sales trend data point"""
    fecha: str  # Format: DD/MM or DD/MM/YYYY
    total_ventas: Decimal
    cantidad_facturas: Optional[int] = None
    clientes_activos: Optional[int] = None

    def __post_init__(self):
        """Validate sales trend data"""
        if not self.fecha:
            raise ValueError("Date cannot be empty")

        if self.total_ventas < 0:
            raise ValueError("Total sales cannot be negative")


@dataclass
class OverallMetrics:
    """Overall business metrics KPIs"""
    total_facturas: int
    clientes_unicos: int
    total_vendido: Decimal
    costo_total: Decimal
    precio_promedio: Decimal
    deudas_activas: int
    total_pendiente: Decimal
    total_comprado: Decimal  # Total purchases from compra table

    def __post_init__(self):
        """Validate overall metrics"""
        if self.total_facturas < 0:
            raise ValueError("Total invoices cannot be negative")

        if self.clientes_unicos < 0:
            raise ValueError("Unique clients cannot be negative")

        if self.total_vendido < 0:
            raise ValueError("Total sold cannot be negative")

        if self.costo_total < 0:
            raise ValueError("Total cost cannot be negative")

        if self.total_pendiente < 0:
            raise ValueError("Outstanding amount cannot be negative")

        if self.total_comprado < 0:
            raise ValueError("Total purchases cannot be negative")

    @property
    def liquidez(self) -> Decimal:
        """
        Calculate liquidity (cash flow)
        Liquidez = Total Vendido - Pendiente de Pago
        This represents the actual money received
        """
        return self.total_vendido - self.total_pendiente

    @property
    def ganancia_total(self) -> Decimal:
        """
        Calculate total profit
        Ganancia = Total Vendido - Costo Total
        Kept for backwards compatibility with vista_ganancias_por_producto
        """
        return self.total_vendido - self.costo_total

    def calculate_margin_percentage(self) -> Decimal:
        """Calculate profit margin percentage"""
        if self.total_vendido > 0:
            return (self.ganancia_total / self.total_vendido) * 100
        return Decimal('0')


@dataclass
class ProductDetail:
    """Detailed product information with history"""
    producto_info: ProductAnalytics
    historial_ventas: List[Dict]  # [{fecha, cantidad, ventas, ganancia}]
    top_clientes: List[Dict]  # [{nombre_cliente, cantidad_total, num_compras}]

    def __post_init__(self):
        """Validate product detail"""
        if not isinstance(self.producto_info, ProductAnalytics):
            raise ValueError("producto_info must be ProductAnalytics instance")

        if not isinstance(self.historial_ventas, list):
            raise ValueError("historial_ventas must be a list")

        if not isinstance(self.top_clientes, list):
            raise ValueError("top_clientes must be a list")


@dataclass
class ClientDetail:
    """Detailed client information with history"""
    cliente_info: ClientAnalytics
    historial_compras: List[Dict]  # [{fecha, total_ventas, cantidad_total, num_facturas}]
    top_productos: List[Dict]  # [{nombre_producto, cantidad_total, total_comprado}]
    deudas: List[Dict]  # [{id_deuda, monto, monto_pagado, fecha_generada}]

    def __post_init__(self):
        """Validate client detail"""
        if not isinstance(self.cliente_info, ClientAnalytics):
            raise ValueError("cliente_info must be ClientAnalytics instance")

        if not isinstance(self.historial_compras, list):
            raise ValueError("historial_compras must be a list")

        if not isinstance(self.top_productos, list):
            raise ValueError("top_productos must be a list")

        if not isinstance(self.deudas, list):
            raise ValueError("deudas must be a list")


@dataclass
class DateRange:
    """Date range for analytics queries"""
    start_date: datetime
    end_date: datetime
    days: int

    def __post_init__(self):
        """Validate date range - Fail Fast"""
        if self.start_date > self.end_date:
            raise InvalidDateRangeError("Start date cannot be after end date")

        if self.days < 0:
            raise InvalidDateRangeError("Days cannot be negative")

    @classmethod
    def from_days(cls, days: int) -> 'DateRange':
        """Create date range from number of days back"""
        if days < 0:
            raise InvalidDateRangeError("Days cannot be negative")

        end_date = datetime.now()

        if days >= 9999:  # Special case: all history
            start_date = datetime(2000, 1, 1)
        else:
            from datetime import timedelta
            start_date = end_date - timedelta(days=days)

        return cls(start_date=start_date, end_date=end_date, days=days)

    @classmethod
    def from_period(cls, period: str) -> 'DateRange':
        """Create date range from period string (1D, 7D, 30D, 90D, 1Y, ALL)"""
        period_map = {
            '1D': 1,
            '7D': 7,
            '30D': 30,
            '90D': 90,
            '1Y': 365,
            'ALL': 9999
        }

        if period not in period_map:
            raise InvalidMetricError(f"Invalid period: {period}. Must be one of {list(period_map.keys())}")

        return cls.from_days(period_map[period])
