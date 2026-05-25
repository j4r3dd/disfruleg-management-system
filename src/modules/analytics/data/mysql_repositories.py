# -*- coding: utf-8 -*-
"""
MySQL Repository Implementations - Analytics Module
Concrete implementations of repository interfaces
"""

from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from ..domain.models import (
    ProductAnalytics,
    ClientAnalytics,
    GroupAnalytics,
    SalesTrend,
    OverallMetrics,
    DateRange
)
from ..domain.exceptions import DataNotFoundError

logger = logging.getLogger(__name__)


class MySQLProductAnalyticsRepository:
    """MySQL implementation for product analytics"""

    def __init__(self, connection):
        self.conn = connection

    def get_top_products(self, limit: int = 10, date_range: Optional[DateRange] = None) -> List[ProductAnalytics]:
        """Get top products by profit (ganancia_total)

        Args:
            limit: Maximum number of products to return
            date_range: Optional date range for filtering. If provided, uses stored procedure.
        """
        cursor = self.conn.cursor()

        try:
            if date_range:
                # Use stored procedure for date-filtered queries
                # Format dates as strings for MySQL
                fecha_inicio = date_range.start_date.strftime('%Y-%m-%d')
                fecha_fin = date_range.end_date.strftime('%Y-%m-%d')

                # Use direct CALL statement instead of callproc for better compatibility
                query = """
                CALL sp_ganancias_por_producto_periodo(%s, %s)
                """

                cursor.execute(query, (fecha_inicio, fecha_fin))
                results = cursor.fetchall()

                # Limit results
                results = results[:limit] if results else []
            else:
                # Use view for all-time data
                query = """
                SELECT
                    id_producto,
                    nombre_producto,
                    unidad_producto,
                    cantidad_vendida,
                    ingresos_totales,
                    precio_venta_promedio,
                    costos_totales,
                    costo_unitario_promedio,
                    ganancia_total,
                    ganancia_por_unidad,
                    margen_ganancia_porcentaje,
                    stock,
                    meses_inventario
                FROM vista_ganancias_por_producto
                WHERE cantidad_vendida > 0
                ORDER BY ganancia_total DESC
                LIMIT %s
                """

                cursor.execute(query, (limit,))
                results = cursor.fetchall()

            return [
                ProductAnalytics(
                    id_producto=row['id_producto'],
                    nombre_producto=row['nombre_producto'],
                    unidad_producto=row['unidad_producto'],
                    cantidad_vendida=Decimal(str(row['cantidad_vendida'] or 0)),
                    ingresos_totales=Decimal(str(row['ingresos_totales'] or 0)),
                    costos_totales=Decimal(str(row['costos_totales'] or 0)),
                    ganancia_total=Decimal(str(row['ganancia_total'] or 0)),
                    margen_ganancia_porcentaje=Decimal(str(row['margen_ganancia_porcentaje'] or 0)),
                    stock=Decimal(str(row['stock'] or 0)),
                    meses_inventario=Decimal(str(row['meses_inventario'])) if row.get('meses_inventario') else None,
                    # New fields from the updated view
                    precio_venta_promedio=Decimal(str(row.get('precio_venta_promedio') or 0)) if row.get('precio_venta_promedio') else None,
                    costo_unitario_promedio=Decimal(str(row.get('costo_unitario_promedio') or 0)) if row.get('costo_unitario_promedio') else None,
                    ganancia_por_unidad=Decimal(str(row.get('ganancia_por_unidad') or 0)) if row.get('ganancia_por_unidad') else None
                )
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return []
        finally:
            cursor.close()

    def get_product_detail(
        self,
        product_id: int,
        date_range: DateRange,
        metric: str = 'cantidad'
    ) -> Dict:
        """Get detailed product information with history"""
        cursor = self.conn.cursor()

        try:
            # Get basic product info
            query_base = """
            SELECT
                id_producto,
                nombre_producto,
                unidad_producto,
                cantidad_vendida,
                ingresos_totales,
                costos_totales,
                ganancia_total,
                margen_ganancia_porcentaje,
                stock,
                meses_inventario
            FROM vista_ganancias_por_producto
            WHERE id_producto = %s
            """

            cursor.execute(query_base, (product_id,))
            result = cursor.fetchone()

            if not result:
                raise DataNotFoundError(f"Product {product_id} not found")

            producto_info = ProductAnalytics(
                id_producto=result['id_producto'],
                nombre_producto=result['nombre_producto'],
                unidad_producto=result['unidad_producto'],
                cantidad_vendida=Decimal(str(result['cantidad_vendida'] or 0)),
                ingresos_totales=Decimal(str(result['ingresos_totales'] or 0)),
                costos_totales=Decimal(str(result['costos_totales'] or 0)),
                ganancia_total=Decimal(str(result['ganancia_total'] or 0)),
                margen_ganancia_porcentaje=Decimal(str(result['margen_ganancia_porcentaje'] or 0)),
                stock=Decimal(str(result['stock'] or 0)),
                meses_inventario=Decimal(str(result['meses_inventario'])) if result.get('meses_inventario') else None
            )

            # Get sales history
            query_ventas = """
            SELECT
                DATE(f.fecha_factura) as fecha,
                SUM(df.cantidad_factura) as cantidad,
                SUM(df.cantidad_factura * df.precio_unitario_venta) as ventas,
                SUM(df.cantidad_factura * df.precio_unitario_venta) -
                SUM(df.cantidad_factura * COALESCE(
                    (SELECT AVG(c.precio_unitario_compra)
                     FROM compra c
                     WHERE c.id_producto = df.id_producto
                     AND c.fecha_compra <= f.fecha_factura),
                    0
                )) as ganancia
            FROM detalle_factura df
            INNER JOIN factura f ON df.id_factura = f.id_factura
            WHERE df.id_producto = %s
                AND f.fecha_factura BETWEEN %s AND %s
            GROUP BY DATE(f.fecha_factura)
            ORDER BY fecha ASC
            """

            cursor.execute(query_ventas, (product_id, date_range.start_date, date_range.end_date))
            ventas_raw = cursor.fetchall()

            historial_ventas = []
            for row in ventas_raw:
                fecha_formateada = 'N/A'
                if row.get('fecha'):
                    try:
                        if hasattr(row['fecha'], 'strftime'):
                            fecha_formateada = row['fecha'].strftime('%d/%m')
                        else:
                            fecha_formateada = str(row['fecha'])
                    except:
                        fecha_formateada = 'N/A'

                historial_ventas.append({
                    'fecha': fecha_formateada,
                    'cantidad': float(row.get('cantidad') or 0),
                    'ventas': float(row.get('ventas') or 0),
                    'ganancia': float(row.get('ganancia') or 0)
                })

            # Get top clients
            query_clientes = """
            SELECT
                c.nombre_cliente,
                SUM(df.cantidad_factura) as cantidad_total,
                COUNT(DISTINCT f.id_factura) as num_compras
            FROM detalle_factura df
            INNER JOIN factura f ON df.id_factura = f.id_factura
            INNER JOIN cliente c ON f.id_cliente = c.id_cliente
            WHERE df.id_producto = %s
                AND f.fecha_factura BETWEEN %s AND %s
            GROUP BY c.id_cliente, c.nombre_cliente
            ORDER BY cantidad_total DESC
            LIMIT 5
            """

            cursor.execute(query_clientes, (product_id, date_range.start_date, date_range.end_date))
            top_clientes = [dict(row) for row in cursor.fetchall()]

            return {
                'historial_ventas': historial_ventas,
                'top_clientes': top_clientes,
                'producto_info': producto_info
            }

        except Exception as e:
            logger.error(f"Error getting product detail: {e}")
            return {}
        finally:
            cursor.close()

    def search_products(self, search_term: str, limit: int = 20) -> List[ProductAnalytics]:
        """Search products by name"""
        cursor = self.conn.cursor()

        try:
            query = """
            SELECT
                id_producto,
                nombre_producto,
                unidad_producto,
                cantidad_vendida,
                ingresos_totales,
                precio_venta_promedio,
                costos_totales,
                costo_unitario_promedio,
                ganancia_total,
                ganancia_por_unidad,
                margen_ganancia_porcentaje,
                stock,
                meses_inventario
            FROM vista_ganancias_por_producto
            WHERE nombre_producto LIKE %s
            ORDER BY ganancia_total DESC
            LIMIT %s
            """

            pattern = f"%{search_term}%"
            cursor.execute(query, (pattern, limit))
            results = cursor.fetchall()

            return [
                ProductAnalytics(
                    id_producto=row['id_producto'],
                    nombre_producto=row['nombre_producto'],
                    unidad_producto=row['unidad_producto'],
                    cantidad_vendida=Decimal(str(row['cantidad_vendida'] or 0)),
                    ingresos_totales=Decimal(str(row['ingresos_totales'] or 0)),
                    costos_totales=Decimal(str(row['costos_totales'] or 0)),
                    ganancia_total=Decimal(str(row['ganancia_total'] or 0)),
                    margen_ganancia_porcentaje=Decimal(str(row['margen_ganancia_porcentaje'] or 0)),
                    stock=Decimal(str(row['stock'] or 0)),
                    meses_inventario=Decimal(str(row['meses_inventario'])) if row.get('meses_inventario') else None,
                    # New fields from the updated view
                    precio_venta_promedio=Decimal(str(row.get('precio_venta_promedio') or 0)) if row.get('precio_venta_promedio') else None,
                    costo_unitario_promedio=Decimal(str(row.get('costo_unitario_promedio') or 0)) if row.get('costo_unitario_promedio') else None,
                    ganancia_por_unidad=Decimal(str(row.get('ganancia_por_unidad') or 0)) if row.get('ganancia_por_unidad') else None
                )
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
        finally:
            cursor.close()


class MySQLClientAnalyticsRepository:
    """MySQL implementation for client analytics"""

    def __init__(self, connection):
        self.conn = connection

    def get_top_clients(self, limit: int = 10, date_range: Optional[DateRange] = None) -> List[ClientAnalytics]:
        """Get top clients by sales volume

        Args:
            limit: Maximum number of clients to return
            date_range: Optional date range for filtering sales
        """
        cursor = self.conn.cursor()

        try:
            if date_range:
                # Calculate metrics for the specified date range
                fecha_inicio = date_range.start_date.strftime('%Y-%m-%d')
                fecha_fin = date_range.end_date.strftime('%Y-%m-%d')

                # FIXED: Use actual precio_unitario_venta from detalle_factura
                query = """
                SELECT
                    c.id_cliente,
                    c.nombre_cliente,
                    g.clave_grupo,
                    tc.nombre_tipo AS tipo_cliente,
                    tc.descuento AS porcentaje_descuento,
                    COALESCE(SUM(df.cantidad_factura * df.precio_unitario_venta), 0) AS total_ventas,
                    COUNT(DISTINCT f.id_factura) AS cantidad_facturas,
                    MAX(f.fecha_factura) AS ultima_compra,
                    0 AS saldo_pendiente
                FROM cliente c
                LEFT JOIN grupo g ON c.id_grupo = g.id_grupo
                LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                LEFT JOIN factura f ON c.id_cliente = f.id_cliente
                    AND f.fecha_factura BETWEEN %s AND %s
                LEFT JOIN detalle_factura df ON f.id_factura = df.id_factura
                GROUP BY c.id_cliente, c.nombre_cliente, g.clave_grupo, tc.nombre_tipo, tc.descuento
                HAVING total_ventas > 0
                ORDER BY total_ventas DESC
                LIMIT %s
                """

                cursor.execute(query, (fecha_inicio, fecha_fin, limit))
            else:
                # Use view for all-time data
                query = """
                SELECT
                    id_cliente,
                    nombre_cliente,
                    clave_grupo,
                    tipo_cliente,
                    porcentaje_descuento,
                    total_ventas,
                    cantidad_facturas,
                    ultima_compra,
                    saldo_pendiente
                FROM vista_ganancias_por_cliente
                ORDER BY total_ventas DESC
                LIMIT %s
                """

                cursor.execute(query, (limit,))

            results = cursor.fetchall()

            return [
                ClientAnalytics(
                    id_cliente=row['id_cliente'],
                    nombre_cliente=row['nombre_cliente'],
                    clave_grupo=row['clave_grupo'],
                    tipo_cliente=row['tipo_cliente'],
                    porcentaje_descuento=Decimal(str(row['porcentaje_descuento'] or 0)),
                    total_ventas=Decimal(str(row['total_ventas'] or 0)),
                    cantidad_facturas=int(row['cantidad_facturas'] or 0),
                    ultima_compra=row.get('ultima_compra'),
                    saldo_pendiente=Decimal(str(row['saldo_pendiente'] or 0))
                )
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting top clients: {e}")
            return []
        finally:
            cursor.close()

    def get_client_detail(
        self,
        client_id: int,
        date_range: DateRange,
        metric: str = 'ventas'
    ) -> Dict:
        """Get detailed client information with history"""
        cursor = self.conn.cursor()

        try:
            # Get basic client info
            query_base = """
            SELECT
                id_cliente,
                nombre_cliente,
                clave_grupo,
                tipo_cliente,
                porcentaje_descuento,
                total_ventas,
                cantidad_facturas,
                ultima_compra,
                saldo_pendiente
            FROM vista_ganancias_por_cliente
            WHERE id_cliente = %s
            """

            cursor.execute(query_base, (client_id,))
            result = cursor.fetchone()

            if not result:
                raise DataNotFoundError(f"Client {client_id} not found")

            cliente_info = ClientAnalytics(
                id_cliente=result['id_cliente'],
                nombre_cliente=result['nombre_cliente'],
                clave_grupo=result['clave_grupo'],
                tipo_cliente=result['tipo_cliente'],
                porcentaje_descuento=Decimal(str(result['porcentaje_descuento'] or 0)),
                total_ventas=Decimal(str(result['total_ventas'] or 0)),
                cantidad_facturas=int(result['cantidad_facturas'] or 0),
                ultima_compra=result.get('ultima_compra'),
                saldo_pendiente=Decimal(str(result['saldo_pendiente'] or 0))
            )

            # Get purchase history
            # FIXED: Use actual precio_unitario_venta from detalle_factura
            query_compras = """
            SELECT
                DATE(f.fecha_factura) as fecha,
                SUM(df.cantidad_factura * df.precio_unitario_venta) as total_ventas,
                SUM(df.cantidad_factura) as cantidad_total,
                COUNT(DISTINCT f.id_factura) as num_facturas
            FROM factura f
            INNER JOIN detalle_factura df ON f.id_factura = df.id_factura
            WHERE f.id_cliente = %s
                AND f.fecha_factura BETWEEN %s AND %s
            GROUP BY DATE(f.fecha_factura)
            ORDER BY fecha ASC
            """

            cursor.execute(query_compras, (client_id, date_range.start_date, date_range.end_date))
            compras_raw = cursor.fetchall()

            historial_compras = []
            for row in compras_raw:
                fecha_formateada = 'N/A'
                if row.get('fecha'):
                    try:
                        if hasattr(row['fecha'], 'strftime'):
                            fecha_formateada = row['fecha'].strftime('%d/%m')
                        else:
                            fecha_formateada = str(row['fecha'])
                    except:
                        fecha_formateada = 'N/A'

                historial_compras.append({
                    'fecha': fecha_formateada,
                    'total_ventas': float(row.get('total_ventas') or 0),
                    'cantidad_total': float(row.get('cantidad_total') or 0),
                    'num_facturas': int(row.get('num_facturas') or 0)
                })

            # Get top products
            query_productos = """
            SELECT
                p.nombre_producto,
                p.unidad_producto,
                SUM(df.cantidad_factura) as cantidad_total,
                SUM(df.cantidad_factura * df.precio_unitario_venta) as total_comprado,
                COUNT(DISTINCT f.id_factura) as num_facturas
            FROM detalle_factura df
            INNER JOIN factura f ON df.id_factura = df.id_factura
            INNER JOIN producto p ON df.id_producto = p.id_producto
            WHERE f.id_cliente = %s
                AND f.fecha_factura BETWEEN %s AND %s
            GROUP BY p.id_producto, p.nombre_producto, p.unidad_producto
            ORDER BY cantidad_total DESC
            LIMIT 5
            """

            cursor.execute(query_productos, (client_id, date_range.start_date, date_range.end_date))
            top_productos = [dict(row) for row in cursor.fetchall()]

            # Get debts - UPDATED to use 'deudas' table instead of 'deuda'
            query_deudas = """
            SELECT
                d.id_deuda,
                d.id_factura,
                d.monto_total as monto,
                d.monto_pagado,
                d.fecha_generada,
                d.pagado,
                d.fecha_pago,
                d.descripcion,
                d.metodo_pago,
                d.referencia_pago
            FROM deudas d
            WHERE d.id_cliente = %s
                AND d.pagado = 0
            ORDER BY d.fecha_generada DESC
            LIMIT 10
            """

            cursor.execute(query_deudas, (client_id,))
            deudas = [dict(row) for row in cursor.fetchall()]

            return {
                'historial_compras': historial_compras,
                'top_productos': top_productos,
                'deudas': deudas,
                'cliente_info': cliente_info
            }

        except Exception as e:
            logger.error(f"Error getting client detail: {e}")
            return {}
        finally:
            cursor.close()

    def search_clients(self, search_term: str, limit: int = 20) -> List[ClientAnalytics]:
        """Search clients by name or group"""
        cursor = self.conn.cursor()

        try:
            query = """
            SELECT
                id_cliente,
                nombre_cliente,
                clave_grupo,
                tipo_cliente,
                porcentaje_descuento,
                total_ventas,
                cantidad_facturas,
                ultima_compra,
                saldo_pendiente
            FROM vista_ganancias_por_cliente
            WHERE nombre_cliente LIKE %s OR clave_grupo LIKE %s
            ORDER BY total_ventas DESC
            LIMIT %s
            """

            pattern = f"%{search_term}%"
            cursor.execute(query, (pattern, pattern, limit))
            results = cursor.fetchall()

            return [
                ClientAnalytics(
                    id_cliente=row['id_cliente'],
                    nombre_cliente=row['nombre_cliente'],
                    clave_grupo=row['clave_grupo'],
                    tipo_cliente=row['tipo_cliente'],
                    porcentaje_descuento=Decimal(str(row['porcentaje_descuento'] or 0)),
                    total_ventas=Decimal(str(row['total_ventas'] or 0)),
                    cantidad_facturas=int(row['cantidad_facturas'] or 0),
                    ultima_compra=row.get('ultima_compra'),
                    saldo_pendiente=Decimal(str(row['saldo_pendiente'] or 0))
                )
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error searching clients: {e}")
            return []
        finally:
            cursor.close()

    def get_clients_with_debts(self):
        """
        Get all clients with pending debts
        Returns ClientDebtSummary objects from deudas module
        """
        cursor = self.conn.cursor()

        try:
            from ...deudas.domain.models import ClientDebtSummary

            query = """
                SELECT
                    d.id_cliente,
                    d.nombre_cliente,
                    COALESCE(d.nombre_grupo, '') as clave_grupo,
                    COALESCE(SUM(CASE WHEN d.pagado = 0 THEN (d.monto_total - d.monto_pagado) ELSE 0 END), 0) as saldo_pendiente,
                    COUNT(CASE WHEN d.pagado = 0 THEN 1 END) as deudas_pendientes,
                    COALESCE(SUM(CASE WHEN d.pagado = 0 THEN (d.monto_total - d.monto_pagado) ELSE 0 END), 0) as total_deuda_pendiente,
                    COALESCE(SUM(d.monto_pagado), 0) as total_deuda_pagada
                FROM deudas d
                WHERE d.pagado = 0
                GROUP BY d.id_cliente, d.nombre_cliente, d.nombre_grupo
                HAVING saldo_pendiente > 0
                ORDER BY saldo_pendiente DESC
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                try:
                    result.append(ClientDebtSummary(
                        id_cliente=int(row['id_cliente']),
                        nombre_cliente=str(row['nombre_cliente']),
                        clave_grupo=str(row['clave_grupo']),
                        saldo_pendiente=Decimal(str(row['saldo_pendiente'] or 0)),
                        deudas_pendientes=int(row['deudas_pendientes'] or 0),
                        total_deuda_pendiente=Decimal(str(row['total_deuda_pendiente'] or 0)),
                        total_deuda_pagada=Decimal(str(row['total_deuda_pagada'] or 0))
                    ))
                except Exception as e:
                    logger.error(f"Error mapping client debt summary: {e}")
                    continue

            return result

        except Exception as e:
            logger.error(f"Error getting clients with debts: {e}")
            return []
        finally:
            cursor.close()


class MySQLGroupAnalyticsRepository:
    """MySQL implementation for group analytics"""

    def __init__(self, connection):
        self.conn = connection

    def get_groups_summary(self, date_range: Optional[DateRange] = None) -> List[GroupAnalytics]:
        """Get summary for all groups

        Args:
            date_range: Optional date range for filtering sales
        """
        cursor = self.conn.cursor()

        try:
            if date_range:
                # Calculate metrics for the specified date range
                fecha_inicio = date_range.start_date.strftime('%Y-%m-%d')
                fecha_fin = date_range.end_date.strftime('%Y-%m-%d')

                # FIXED: Use actual precio_unitario_venta from detalle_factura
                query = """
                SELECT
                    g.id_grupo,
                    g.clave_grupo,
                    tc.nombre_tipo AS tipo_cliente,
                    COUNT(DISTINCT c.id_cliente) AS cantidad_clientes,
                    COALESCE(SUM(df.cantidad_factura * df.precio_unitario_venta), 0) AS total_ventas,
                    COUNT(DISTINCT f.id_factura) AS cantidad_facturas,
                    tc.descuento AS descuento_aplicado,
                    COALESCE(AVG(df.cantidad_factura * df.precio_unitario_venta), 0) AS ticket_promedio
                FROM grupo g
                LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                LEFT JOIN cliente c ON g.id_grupo = c.id_grupo
                LEFT JOIN factura f ON c.id_cliente = f.id_cliente
                    AND f.fecha_factura BETWEEN %s AND %s
                LEFT JOIN detalle_factura df ON f.id_factura = df.id_factura
                GROUP BY g.id_grupo, g.clave_grupo, tc.nombre_tipo, tc.descuento
                HAVING total_ventas > 0
                ORDER BY total_ventas DESC
                """

                cursor.execute(query, (fecha_inicio, fecha_fin))
            else:
                # Use view for all-time data
                query = """
                SELECT
                    id_grupo,
                    clave_grupo,
                    tipo_cliente,
                    cantidad_clientes,
                    total_ventas,
                    cantidad_facturas,
                    descuento_aplicado,
                    ticket_promedio
                FROM vista_ganancias_por_grupo
                ORDER BY total_ventas DESC
                """

                cursor.execute(query)

            results = cursor.fetchall()

            return [
                GroupAnalytics(
                    id_grupo=row['id_grupo'],
                    clave_grupo=row['clave_grupo'],
                    tipo_cliente=row.get('tipo_cliente'),
                    cantidad_clientes=int(row['cantidad_clientes'] or 0),
                    total_ventas=Decimal(str(row['total_ventas'] or 0)),
                    cantidad_facturas=int(row['cantidad_facturas'] or 0),
                    descuento_aplicado=Decimal(str(row['descuento_aplicado'] or 0)),
                    ticket_promedio=Decimal(str(row['ticket_promedio'] or 0))
                )
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting groups summary: {e}")
            return []
        finally:
            cursor.close()

    def get_group_by_id(self, group_id: int) -> Optional[GroupAnalytics]:
        """Get group analytics by ID"""
        cursor = self.conn.cursor()

        try:
            query = """
            SELECT
                id_grupo,
                clave_grupo,
                tipo_cliente,
                cantidad_clientes,
                total_ventas,
                cantidad_facturas,
                descuento_aplicado,
                ticket_promedio
            FROM vista_ganancias_por_grupo
            WHERE id_grupo = %s
            """

            cursor.execute(query, (group_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return GroupAnalytics(
                id_grupo=row['id_grupo'],
                clave_grupo=row['clave_grupo'],
                tipo_cliente=row.get('tipo_cliente'),
                cantidad_clientes=int(row['cantidad_clientes'] or 0),
                total_ventas=Decimal(str(row['total_ventas'] or 0)),
                cantidad_facturas=int(row['cantidad_facturas'] or 0),
                descuento_aplicado=Decimal(str(row['descuento_aplicado'] or 0)),
                ticket_promedio=Decimal(str(row['ticket_promedio'] or 0))
            )

        except Exception as e:
            logger.error(f"Error getting group by ID: {e}")
            return None
        finally:
            cursor.close()


class MySQLSalesTrendRepository:
    """MySQL implementation for sales trend"""

    def __init__(self, connection):
        self.conn = connection

    def get_sales_trend(self, days: int = 30) -> List[SalesTrend]:
        """Get sales trend for specified days"""
        cursor = self.conn.cursor()

        try:
            # FIXED: Use actual precio_unitario_venta from detalle_factura
            query = """
            SELECT
                DATE(f.fecha_factura) as fecha,
                SUM(df.cantidad_factura * df.precio_unitario_venta) as total_ventas,
                COUNT(DISTINCT f.id_factura) as cantidad_facturas,
                COUNT(DISTINCT f.id_cliente) as clientes_activos
            FROM factura f
            INNER JOIN detalle_factura df ON f.id_factura = df.id_factura
            WHERE f.fecha_factura >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(f.fecha_factura)
            ORDER BY fecha ASC
            """

            cursor.execute(query, (days,))
            results = cursor.fetchall()

            data = []
            for row in results:
                fecha = row.get('fecha') or row[0]
                fecha_str = fecha.strftime('%d/%m') if hasattr(fecha, 'strftime') else str(fecha)

                data.append(SalesTrend(
                    fecha=fecha_str,
                    total_ventas=Decimal(str(row.get('total_ventas') or row[1] or 0)),
                    cantidad_facturas=int(row.get('cantidad_facturas') or row[2] or 0) if len(row) > 2 else None,
                    clientes_activos=int(row.get('clientes_activos') or row[3] or 0) if len(row) > 3 else None
                ))

            return data

        except Exception as e:
            logger.error(f"Error getting sales trend: {e}")
            return []
        finally:
            cursor.close()

    def get_sales_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[SalesTrend]:
        """Get sales data for specific date range"""
        cursor = self.conn.cursor()

        try:
            # FIXED: Use actual precio_unitario_venta from detalle_factura
            query = """
            SELECT
                DATE(f.fecha_factura) as fecha,
                SUM(df.cantidad_factura * df.precio_unitario_venta) as total_ventas,
                COUNT(DISTINCT f.id_factura) as cantidad_facturas,
                COUNT(DISTINCT f.id_cliente) as clientes_activos
            FROM factura f
            JOIN detalle_factura df ON f.id_factura = df.id_factura
            WHERE f.fecha_factura BETWEEN %s AND %s
            GROUP BY DATE(f.fecha_factura)
            ORDER BY fecha DESC
            """

            cursor.execute(query, (start_date, end_date))
            results = cursor.fetchall()

            data = []
            for row in results:
                fecha = row.get('fecha') or row[0]
                fecha_str = fecha.strftime('%d/%m') if hasattr(fecha, 'strftime') else str(fecha)

                data.append(SalesTrend(
                    fecha=fecha_str,
                    total_ventas=Decimal(str(row.get('total_ventas') or row[1] or 0)),
                    cantidad_facturas=int(row.get('cantidad_facturas') or row[2] or 0) if len(row) > 2 else None,
                    clientes_activos=int(row.get('clientes_activos') or row[3] or 0) if len(row) > 3 else None
                ))

            return data

        except Exception as e:
            logger.error(f"Error getting sales by date range: {e}")
            return []
        finally:
            cursor.close()

    def get_sales_comparison(self, days: int = 30) -> Dict:
        """Compare sales between current and previous period"""
        cursor = self.conn.cursor()

        try:
            current_start = datetime.now() - timedelta(days=days)
            current_end = datetime.now()

            previous_start = current_start - timedelta(days=days)
            previous_end = current_start

            # FIXED: Use actual precio_unitario_venta from detalle_factura
            query = """
            SELECT
                SUM(df.cantidad_factura * df.precio_unitario_venta) as total
            FROM factura f
            INNER JOIN detalle_factura df ON f.id_factura = df.id_factura
            WHERE f.fecha_factura BETWEEN %s AND %s
            """

            cursor.execute(query, (current_start, current_end))
            current_result = cursor.fetchone()
            current_sales = float(current_result[0] or 0) if current_result else 0

            cursor.execute(query, (previous_start, previous_end))
            previous_result = cursor.fetchone()
            previous_sales = float(previous_result[0] or 0) if previous_result else 0

            if previous_sales > 0:
                growth = ((current_sales - previous_sales) / previous_sales) * 100
            else:
                growth = 0

            return {
                'current': current_sales,
                'previous': previous_sales,
                'growth_percentage': round(growth, 2)
            }

        except Exception as e:
            logger.error(f"Error getting sales comparison: {e}")
            return {'current': 0, 'previous': 0, 'growth_percentage': 0}
        finally:
            cursor.close()


class MySQLAnalyticsRepository:
    """MySQL implementation for overall analytics"""

    def __init__(self, connection):
        self.conn = connection

    def get_overall_metrics(self) -> OverallMetrics:
        """Get overall business metrics KPIs"""
        cursor = self.conn.cursor()

        try:
            # Main metrics (sales and clients)
            # FIXED: Use actual precio_unitario_venta from detalle_factura instead of recalculating
            query_main = """
            SELECT
                COUNT(DISTINCT f.id_factura) as total_facturas,
                COUNT(DISTINCT f.id_cliente) as clientes_unicos,
                SUM(df.cantidad_factura * df.precio_unitario_venta) as total_vendido,
                ROUND(AVG(df.precio_unitario_venta), 2) as precio_promedio
            FROM factura f
            LEFT JOIN detalle_factura df ON f.id_factura = df.id_factura
            """

            cursor.execute(query_main)
            result_main = cursor.fetchone()

            # Cost metrics
            query_cost = """
            SELECT
                SUM(costos_totales) as costo_total
            FROM vista_ganancias_por_producto
            """

            cursor.execute(query_cost)
            result_cost = cursor.fetchone()

            # Debt metrics - Query deudas table directly to avoid row multiplication
            # This ensures the same calculation as the deudas module
            query_debts = """
            SELECT
                COUNT(CASE WHEN pagado = 0 THEN 1 END) as deudas_activas,
                COALESCE(SUM(CASE WHEN pagado = 0 THEN (monto_total - monto_pagado) END), 0) as total_pendiente
            FROM deudas
            """

            cursor.execute(query_debts)
            result_debts = cursor.fetchone()

            # Purchase metrics - Query compra table for total purchases
            query_purchases = """
            SELECT
                COALESCE(SUM(total_con_impuestos), 0) as total_comprado
            FROM compra
            """

            cursor.execute(query_purchases)
            result_purchases = cursor.fetchone()

            return OverallMetrics(
                total_facturas=int(result_main.get('total_facturas') or 0),
                clientes_unicos=int(result_main.get('clientes_unicos') or 0),
                total_vendido=Decimal(str(result_main.get('total_vendido') or 0)),
                costo_total=Decimal(str(result_cost.get('costo_total') or 0)),
                precio_promedio=Decimal(str(result_main.get('precio_promedio') or 0)),
                deudas_activas=int(result_debts.get('deudas_activas') or 0),
                total_pendiente=Decimal(str(result_debts.get('total_pendiente') or 0)),
                total_comprado=Decimal(str(result_purchases.get('total_comprado') or 0))
            )

        except Exception as e:
            logger.error(f"Error getting overall metrics: {e}")
            return OverallMetrics(
                total_facturas=0,
                clientes_unicos=0,
                total_vendido=Decimal('0'),
                costo_total=Decimal('0'),
                precio_promedio=Decimal('0'),
                deudas_activas=0,
                total_pendiente=Decimal('0'),
                total_comprado=Decimal('0')
            )
        finally:
            cursor.close()


class InMemoryCacheRepository:
    """In-memory cache implementation"""

    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.last_update = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[any]:
        """Get cached data by key"""
        if self.is_valid(key):
            return self.cache.get(key)
        return None

    def set(self, key: str, data: any, ttl: Optional[int] = None) -> None:
        """Set data in cache with optional TTL"""
        self.cache[key] = data
        self.last_update[key] = datetime.now()

    def is_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.last_update:
            return False
        elapsed = (datetime.now() - self.last_update[key]).total_seconds()
        return elapsed < self.default_ttl

    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        self.last_update.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cached_keys': len(self.cache),
            'cache_size': sum(len(str(v)) for v in self.cache.values()),
            'last_updates': {k: v.isoformat() for k, v in self.last_update.items()}
        }
