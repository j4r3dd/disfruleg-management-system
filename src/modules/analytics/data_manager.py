# -*- coding: utf-8 -*-
"""
DISFRULEG - Data Manager para Analytics (VERSIÓN CORREGIDA)
✅ FIX: Usa vista_ganancias_por_producto para obtener costos y ganancias
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AnalyticsDataManager:
    """Gestor de datos con cache y queries optimizadas"""
    
    def __init__(self, cursor, pool_connector):
        self.cursor = cursor
        self.pool = pool_connector
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        self.last_update = {}
        
    def _is_cache_valid(self, key: str) -> bool:
        """Validar si cache aún es válido"""
        if key not in self.last_update:
            return False
        elapsed = (datetime.now() - self.last_update[key]).total_seconds()
        return elapsed < self.cache_ttl
    
    def _set_cache(self, key: str, data):
        """Guardar en cache"""
        self.cache[key] = data
        self.last_update[key] = datetime.now()
    
    def get_top_products(self, limit: int = 10) -> List[Dict]:
        """TOP productos por ventas - Ordenados por cantidad vendida"""
        cache_key = f"top_products_{limit}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        query = """
        SELECT
            id_producto,
            nombre_producto,
            unidad_producto,
            cantidad_vendida,
            ingresos_totales,
            costos_totales,
            ganancia_total,
            margen_ganancia_porcentaje,
            stock
        FROM vista_ganancias_por_producto
        WHERE cantidad_vendida > 0
        ORDER BY ganancia_total DESC
        LIMIT %s
        """
        
        try:
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            data = [dict(row) for row in results] if results else []
            self._set_cache(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return []
    
    def get_product_detail(self, id_producto: int, days: int = 30, metric: str = 'cantidad', offset_days: int = 0) -> Dict:
        """
        ✅ CORREGIDO: Obtener detalle completo de un producto con filtros avanzados
        Usa subquery para obtener el costo promedio de compra del producto
        """
        try:
            # Calcular fechas
            fecha_fin = datetime.now() - timedelta(days=offset_days)
            
            if days >= 9999:  # "Todo el historial"
                fecha_inicio = datetime(2000, 1, 1)
            else:
                fecha_inicio = fecha_fin - timedelta(days=days)
            
            # Info básica del producto (desde la vista)
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
            
            self.cursor.execute(query_base, (id_producto,))
            result = self.cursor.fetchone()
            
            if not result:
                return {}
            
            product_info = dict(result)
            
            # ✅ HISTORIAL DE VENTAS CON COSTO CALCULADO DESDE COMPRA
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
            
            self.cursor.execute(query_ventas, (id_producto, fecha_inicio, fecha_fin))
            ventas_raw = self.cursor.fetchall()
            
            # Formatear historial según métrica
            ventas_history = []
            for row in ventas_raw:
                row_dict = dict(row) if isinstance(row, dict) else {
                    'fecha': row[0],
                    'cantidad': row[1],
                    'ventas': row[2],
                    'ganancia': row[3]
                }
                
                # ✅ FIX: Manejar fechas None correctamente
                fecha_formateada = 'N/A'
                if row_dict.get('fecha'):
                    try:
                        if hasattr(row_dict['fecha'], 'strftime'):
                            fecha_formateada = row_dict['fecha'].strftime('%d/%m')
                        else:
                            fecha_formateada = str(row_dict['fecha'])
                    except:
                        fecha_formateada = 'N/A'
                
                ventas_history.append({
                    'fecha': fecha_formateada,
                    'cantidad': float(row_dict.get('cantidad') or 0),
                    'ventas': float(row_dict.get('ventas') or 0),
                    'ganancia': float(row_dict.get('ganancia') or 0)
                })
            
            # Top 5 clientes que compran este producto (EN EL PERIODO FILTRADO)
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
            
            self.cursor.execute(query_clientes, (id_producto, fecha_inicio, fecha_fin))
            top_clientes = [dict(row) for row in self.cursor.fetchall()]
            
            # ✅ FIX: Retornar estructura consistente con el diálogo
            # El diálogo espera SOLO historial_ventas y top_clientes
            return {
                'historial_ventas': ventas_history,
                'top_clientes': top_clientes,
                # Opcionalmente incluir info del producto si se necesita
                'producto_info': product_info
            }
            
        except Exception as e:
            logger.error(f"Error getting product detail: {e}")
            return {}
    
    def get_top_clients(self, limit: int = 10) -> List[Dict]:
        """TOP clientes por volumen de ventas"""
        cache_key = f"top_clients_{limit}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
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
        
        try:
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            data = [dict(row) for row in results] if results else []
            self._set_cache(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"Error getting top clients: {e}")
            return []
    
    def get_groups_summary(self) -> List[Dict]:
        """Resumen por grupo de clientes"""
        cache_key = "groups_summary"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
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
        
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            data = [dict(row) for row in results] if results else []
            self._set_cache(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"Error getting groups summary: {e}")
            return []
    
    def get_sales_by_date_range(self, start_date, end_date) -> List[Dict]:
        """Ventas por rango de fechas"""
        cache_key = f"sales_range_{start_date}_{end_date}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        query = """
        SELECT 
            DATE(f.fecha_factura) as fecha,
            COUNT(DISTINCT f.id_factura) as cantidad_facturas,
            SUM(vd.subtotal_con_descuento) as total_ventas,
            COUNT(DISTINCT f.id_cliente) as clientes_activos
        FROM factura f
        JOIN detalle_factura df ON f.id_factura = df.id_factura
        JOIN vista_detalle_factura_con_descuento vd ON df.id_detalle = vd.id_detalle
        WHERE f.fecha_factura BETWEEN %s AND %s
        GROUP BY DATE(f.fecha_factura)
        ORDER BY fecha DESC
        """
        
        try:
            self.cursor.execute(query, (start_date, end_date))
            results = self.cursor.fetchall()
            data = [dict(row) for row in results] if results else []
            self._set_cache(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"Error getting sales by date: {e}")
            return []
    
    def get_overall_metrics(self) -> Dict:
        """Métricas generales del negocio - KPIs principales
        
        ⚠️ NOTA: El cálculo de 'costo_total' y 'ganancia_total' se basa
        en la agregación de la vista 'vista_ganancias_por_producto' 
        para evitar la duplicación de filas por el JOIN a 'compra'.
        """
        cache_key = "overall_metrics"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # 1. Consulta para Métricas de Ventas, Clientes y Deudas (Sin JOIN a 'compra')
        query_main = """
        SELECT 
            COUNT(DISTINCT f.id_factura) as total_facturas,
            COUNT(DISTINCT f.id_cliente) as clientes_unicos,
            SUM(vd.subtotal_con_descuento) as total_vendido,
            ROUND(AVG(vd.subtotal_con_descuento / NULLIF(df.cantidad_factura, 0)), 2) as precio_promedio,
            COUNT(DISTINCT d.id_deuda) as deudas_activas,
            SUM(CASE WHEN d.pagado = FALSE THEN d.monto - d.monto_pagado ELSE 0 END) as total_pendiente
        FROM factura f
        LEFT JOIN detalle_factura df ON f.id_factura = df.id_factura
        LEFT JOIN vista_detalle_factura_con_descuento vd ON df.id_detalle = vd.id_detalle
        LEFT JOIN deudas d ON f.id_factura = d.id_factura
        """
        
        # 2. Consulta para Costo y Ganancia Total (Usando la vista pre-agregada)
        query_cost_gain = """
        SELECT 
            SUM(costos_totales) as costo_total,
            SUM(ganancia_total) as ganancia_total
        FROM vista_ganancias_por_producto
        """
        
        try:
            self.cursor.execute(query_main)
            result_main = self.cursor.fetchone()
            data = dict(result_main) if result_main else {}
            
            self.cursor.execute(query_cost_gain)
            result_cost_gain = self.cursor.fetchone()
            
            if result_cost_gain:
                cost_gain_dict = dict(result_cost_gain) if isinstance(result_cost_gain, dict) else {
                    'costo_total': result_cost_gain[0],
                    'ganancia_total': result_cost_gain[1]
                }
                data['costo_total'] = float(cost_gain_dict.get('costo_total') or 0)
                data['ganancia_total'] = float(cost_gain_dict.get('ganancia_total') or 0)
            else:
                data['costo_total'] = 0
                data['ganancia_total'] = 0
            
            self._set_cache(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Error getting overall metrics: {e}")
            return {}

    
    def get_sales_trend(self, days: int = 30) -> List[Dict]:
        """Obtener tendencia de ventas por día"""
        cache_key = f"sales_trend_{days}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        query = """
        SELECT 
            DATE(f.fecha_factura) as fecha,
            SUM(vd.subtotal_con_descuento) as total_ventas
        FROM factura f
        INNER JOIN detalle_factura df ON f.id_factura = df.id_factura
        INNER JOIN vista_detalle_factura_con_descuento vd ON df.id_detalle = vd.id_detalle
        WHERE f.fecha_factura >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY DATE(f.fecha_factura)
        ORDER BY fecha ASC
        """
        
        try:
            self.cursor.execute(query, (days,))
            results = self.cursor.fetchall()
            
            data = []
            for row in results:
                if isinstance(row, dict):
                    fecha = row['fecha']
                    total_ventas = row['total_ventas']
                else:
                    fecha = row[0]
                    total_ventas = row[1]
                
                data.append({
                    'fecha': fecha.strftime('%d/%m') if hasattr(fecha, 'strftime') else str(fecha),
                    'total_ventas': float(total_ventas or 0)
                })
            
            self._set_cache(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Error getting sales trend: {e}")
            return []
    
    def get_product_sales_by_metric(self, id_producto: int, days: int = 30, metric: str = 'cantidad') -> List[Dict]:
        """
        ✅ CORREGIDO: Obtener historial de ventas de un producto específico según métrica
        """
        try:
            fecha_inicio = datetime.now() - timedelta(days=days)
            
            query = """
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
                AND f.fecha_factura >= %s
            GROUP BY DATE(f.fecha_factura)
            ORDER BY fecha ASC
            """
            
            self.cursor.execute(query, (id_producto, fecha_inicio))
            results = self.cursor.fetchall()
            
            data = []
            for row in results:
                row_dict = dict(row) if isinstance(row, dict) else {
                    'fecha': row[0],
                    'cantidad': row[1],
                    'ventas': row[2],
                    'ganancia': row[3]
                }
                
                # Determinar valor según métrica
                if metric == 'ventas':
                    value = float(row_dict['ventas'] or 0)
                elif metric == 'ganancia':
                    value = float(row_dict['ganancia'] or 0)
                else:  # 'cantidad' por defecto
                    value = float(row_dict['cantidad'] or 0)
                
                data.append({
                    'fecha': row_dict['fecha'].strftime('%d/%m') if hasattr(row_dict['fecha'], 'strftime') else str(row_dict['fecha']),
                    'value': value,
                    'cantidad': float(row_dict['cantidad'] or 0),
                    'ventas': float(row_dict['ventas'] or 0),
                    'ganancia': float(row_dict['ganancia'] or 0)
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting product sales by metric: {e}")
            return []
    
    def get_sales_comparison(self, days: int = 30) -> Dict:
        """Comparar ventas del periodo actual vs. periodo anterior"""
        try:
            current_start = datetime.now() - timedelta(days=days)
            current_end = datetime.now()
            
            previous_start = current_start - timedelta(days=days)
            previous_end = current_start
            
            query = """
            SELECT 
                SUM(vd.subtotal_con_descuento) as total
            FROM factura f
            INNER JOIN detalle_factura df ON f.id_factura = df.id_factura
            INNER JOIN vista_detalle_factura_con_descuento vd ON df.id_detalle = vd.id_detalle
            WHERE f.fecha_factura BETWEEN %s AND %s
            """
            
            self.cursor.execute(query, (current_start, current_end))
            current_result = self.cursor.fetchone()
            current_sales = float(current_result[0] or 0) if current_result else 0
            
            self.cursor.execute(query, (previous_start, previous_end))
            previous_result = self.cursor.fetchone()
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
    
    def search_products(self, search_term: str, limit: int = 20) -> List[Dict]:
        """Búsqueda de productos con fuzzy matching"""
        query = """
        SELECT
            id_producto,
            nombre_producto,
            unidad_producto,
            cantidad_vendida,
            ganancia_total,
            margen_ganancia_porcentaje
        FROM vista_ganancias_por_producto
        WHERE nombre_producto LIKE %s
        ORDER BY ganancia_total DESC
        LIMIT %s
        """
        
        try:
            pattern = f"%{search_term}%"
            self.cursor.execute(query, (pattern, limit))
            results = self.cursor.fetchall()
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def search_clients(self, search_term: str, limit: int = 20) -> List[Dict]:
        """Búsqueda de clientes"""
        query = """
        SELECT 
            id_cliente,
            nombre_cliente,
            clave_grupo,
            tipo_cliente,
            total_ventas,
            cantidad_facturas,
            saldo_pendiente
        FROM vista_ganancias_por_cliente
        WHERE nombre_cliente LIKE %s OR clave_grupo LIKE %s
        ORDER BY total_ventas DESC
        LIMIT %s
        """
        
        try:
            pattern = f"%{search_term}%"
            self.cursor.execute(query, (pattern, pattern, limit))
            results = self.cursor.fetchall()
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Error searching clients: {e}")
            return []
    
    def refresh_cache(self):
        """Limpiar todo el cache para forzar actualización"""
        self.cache.clear()
        self.last_update.clear()
        logger.info("Cache cleared - next queries will fetch fresh data")
    
    def get_cache_stats(self) -> Dict:
        """Información de estado del cache"""
        return {
            'cached_keys': len(self.cache),
            'cache_size': sum(len(str(v)) for v in self.cache.values()),
            'last_updates': {k: v.isoformat() for k, v in self.last_update.items()}
        }
        
    def get_client_detail(self, id_cliente: int, days: int = 30, metric: str = 'ventas', offset_days: int = 0) -> Dict:
        """
        Obtener detalle completo de un cliente con filtros avanzados
        
        Args:
            id_cliente: ID del cliente
            days: Días hacia atrás (7, 30, 90, 180, 365, 9999 para todo)
            metric: 'ventas', 'cantidad', 'facturas'
            offset_days: Offset para periodo anterior (comparación)
        
        Returns:
            Dict con info básica, historial_compras, top_productos y deudas
        """
        try:
            # Calcular fechas
            fecha_fin = datetime.now() - timedelta(days=offset_days)
            
            if days >= 9999:  # "Todo el historial"
                fecha_inicio = datetime(2000, 1, 1)
            else:
                fecha_inicio = fecha_fin - timedelta(days=days)
            
            # Info básica del cliente (desde la vista)
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
            
            self.cursor.execute(query_base, (id_cliente,))
            result = self.cursor.fetchone()
            
            if not result:
                return {}
            
            client_info = dict(result)
            
            # ✅ HISTORIAL DE COMPRAS (ventas del cliente en el tiempo)
            query_compras = """
            SELECT 
                DATE(f.fecha_factura) as fecha,
                SUM(vd.subtotal_con_descuento) as total_ventas,
                SUM(df.cantidad_factura) as cantidad_total,
                COUNT(DISTINCT f.id_factura) as num_facturas
            FROM factura f
            INNER JOIN detalle_factura df ON f.id_factura = df.id_factura
            INNER JOIN vista_detalle_factura_con_descuento vd ON df.id_detalle = vd.id_detalle
            WHERE f.id_cliente = %s
                AND f.fecha_factura BETWEEN %s AND %s
            GROUP BY DATE(f.fecha_factura)
            ORDER BY fecha ASC
            """
            
            self.cursor.execute(query_compras, (id_cliente, fecha_inicio, fecha_fin))
            compras_raw = self.cursor.fetchall()
            
            # Formatear historial
            compras_history = []
            for row in compras_raw:
                row_dict = dict(row) if isinstance(row, dict) else {
                    'fecha': row[0],
                    'total_ventas': row[1],
                    'cantidad_total': row[2],
                    'num_facturas': row[3]
                }
                
                # ✅ FIX: Manejar fechas None correctamente
                fecha_formateada = 'N/A'
                if row_dict.get('fecha'):
                    try:
                        if hasattr(row_dict['fecha'], 'strftime'):
                            fecha_formateada = row_dict['fecha'].strftime('%d/%m')
                        else:
                            fecha_formateada = str(row_dict['fecha'])
                    except:
                        fecha_formateada = 'N/A'
                
                compras_history.append({
                    'fecha': fecha_formateada,
                    'total_ventas': float(row_dict.get('total_ventas') or 0),
                    'cantidad_total': float(row_dict.get('cantidad_total') or 0),
                    'num_facturas': int(row_dict.get('num_facturas') or 0)
                })
            
            # ✅ TOP 5 PRODUCTOS que más compra este cliente (EN EL PERIODO FILTRADO)
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
            
            self.cursor.execute(query_productos, (id_cliente, fecha_inicio, fecha_fin))
            top_productos = []
            for row in self.cursor.fetchall():
                row_dict = dict(row) if isinstance(row, dict) else {
                    'nombre_producto': row[0],
                    'unidad_producto': row[1],
                    'cantidad_total': row[2],
                    'total_comprado': row[3],
                    'num_facturas': row[4]
                }
                top_productos.append(row_dict)
            
            # ✅ ANÁLISIS DE DEUDAS (todas las deudas del cliente, no solo del periodo)
            query_deudas = """
            SELECT 
                d.id_deuda,
                d.id_factura,
                d.monto,
                d.monto_pagado,
                d.fecha_generada,
                d.pagado,
                d.fecha_pago,
                d.descripcion,
                d.metodo_pago,
                d.referencia_pago
            FROM deudas d
            WHERE d.id_cliente = %s
                AND d.pagado = FALSE
            ORDER BY d.fecha_generada DESC
            LIMIT 10
            """
            
            self.cursor.execute(query_deudas, (id_cliente,))
            deudas = []
            for row in self.cursor.fetchall():
                row_dict = dict(row) if isinstance(row, dict) else {
                    'id_deuda': row[0],
                    'id_factura': row[1],
                    'monto': row[2],
                    'monto_pagado': row[3],
                    'fecha_generada': row[4],
                    'pagado': row[5],
                    'fecha_pago': row[6],
                    'descripcion': row[7],
                    'metodo_pago': row[8],
                    'referencia_pago': row[9]
                }
                deudas.append(row_dict)
            
            # Combinar todo
            client_info['historial_compras'] = compras_history
            client_info['top_productos'] = top_productos
            client_info['deudas'] = deudas
            
            return client_info
            
        except Exception as e:
            logger.error(f"Error getting client detail: {e}")
            return {}


    def get_client_purchase_trend(self, id_cliente: int, days: int = 30) -> List[Dict]:
        """
        Obtener tendencia de compras de un cliente específico
        
        Args:
            id_cliente: ID del cliente
            days: Días hacia atrás
        
        Returns:
            Lista de dicts con fecha y total_ventas
        """
        try:
            fecha_inicio = datetime.now() - timedelta(days=days)
            
            query = """
            SELECT 
                DATE(f.fecha_factura) as fecha,
                SUM(vd.subtotal_con_descuento) as total_ventas
            FROM factura f
            INNER JOIN detalle_factura df ON f.id_factura = df.id_factura
            INNER JOIN vista_detalle_factura_con_descuento vd ON df.id_detalle = vd.id_detalle
            WHERE f.id_cliente = %s
                AND f.fecha_factura >= %s
            GROUP BY DATE(f.fecha_factura)
            ORDER BY fecha ASC
            """
            
            self.cursor.execute(query, (id_cliente, fecha_inicio))
            results = self.cursor.fetchall()
            
            data = []
            for row in results:
                row_dict = dict(row) if isinstance(row, dict) else {
                    'fecha': row[0],
                    'total_ventas': row[1]
                }
                
                data.append({
                    'fecha': row_dict['fecha'].strftime('%d/%m') if hasattr(row_dict['fecha'], 'strftime') else str(row_dict['fecha']),
                    'total_ventas': float(row_dict['total_ventas'] or 0)
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting client purchase trend: {e}")
            return []


    def get_client_debts_summary(self, id_cliente: int) -> Dict:
        """
        Obtener resumen de deudas de un cliente
        
        Returns:
            Dict con total_deuda, deudas_pendientes, monto_pagado
        """
        try:
            query = """
            SELECT 
                COUNT(*) as total_deudas,
                SUM(CASE WHEN pagado = FALSE THEN 1 ELSE 0 END) as deudas_pendientes,
                SUM(monto) as monto_total,
                SUM(monto_pagado) as monto_pagado,
                SUM(CASE WHEN pagado = FALSE THEN monto - monto_pagado ELSE 0 END) as saldo_pendiente
            FROM deudas
            WHERE id_cliente = %s
            """
            
            self.cursor.execute(query, (id_cliente,))
            result = self.cursor.fetchone()
            
            if result:
                row_dict = dict(result) if isinstance(result, dict) else {
                    'total_deudas': result[0],
                    'deudas_pendientes': result[1],
                    'monto_total': result[2],
                    'monto_pagado': result[3],
                    'saldo_pendiente': result[4]
                }
                return {
                    'total_deudas': int(row_dict['total_deudas'] or 0),
                    'deudas_pendientes': int(row_dict['deudas_pendientes'] or 0),
                    'monto_total': float(row_dict['monto_total'] or 0),
                    'monto_pagado': float(row_dict['monto_pagado'] or 0),
                    'saldo_pendiente': float(row_dict['saldo_pendiente'] or 0)
                }
            
            return {
                'total_deudas': 0,
                'deudas_pendientes': 0,
                'monto_total': 0,
                'monto_pagado': 0,
                'saldo_pendiente': 0
            }
            
        except Exception as e:
            logger.error(f"Error getting client debts summary: {e}")
            return {}