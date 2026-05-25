# -*- coding: utf-8 -*-
"""
MySQL Repository Implementations - Data Layer
Concrete implementations of repository interfaces for MySQL
"""

from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import json

from ..domain.models import LearningCorrection
from ..domain.value_objects import Unit


class MySQLClientRepository:
    """
    MySQL implementation of IClientRepository
    Handles all client-related database operations
    """

    def __init__(self, connection):
        """
        Initialize repository with database connection

        Args:
            connection: Active database connection (dependency injection)
        """
        self.conn = connection

    def get_all_clients(self) -> List[Dict]:
        """Get all active clients from database"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT
                    c.id_cliente,
                    c.nombre_cliente,
                    c.id_grupo,
                    g.clave_grupo,
                    tc.nombre_tipo,
                    tc.descuento
                FROM cliente c
                JOIN grupo g ON c.id_grupo = g.id_grupo
                JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                WHERE c.activo = TRUE
                ORDER BY c.nombre_cliente
            """

            cursor.execute(query)
            clients = cursor.fetchall()

            return [{
                'id_cliente': c['id_cliente'],
                'nombre_cliente': c['nombre_cliente'],
                'id_grupo': c['id_grupo'],
                'clave_grupo': c['clave_grupo'],
                'nombre_tipo': c['nombre_tipo'],
                'descuento': Decimal(str(c['descuento'])) if c['descuento'] else Decimal('0')
            } for c in (clients or [])]

        finally:
            cursor.close()

    def get_client_by_id(self, client_id: int) -> Optional[Dict]:
        """Get client by ID"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT
                    c.id_cliente,
                    c.nombre_cliente,
                    c.id_grupo,
                    g.clave_grupo,
                    tc.nombre_tipo,
                    tc.descuento
                FROM cliente c
                JOIN grupo g ON c.id_grupo = g.id_grupo
                JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                WHERE c.id_cliente = %s AND c.activo = TRUE
            """

            cursor.execute(query, (client_id,))
            client = cursor.fetchone()

            if client:
                return {
                    'id_cliente': client['id_cliente'],
                    'nombre_cliente': client['nombre_cliente'],
                    'id_grupo': client['id_grupo'],
                    'clave_grupo': client['clave_grupo'],
                    'nombre_tipo': client['nombre_tipo'],
                    'descuento': Decimal(str(client['descuento'])) if client['descuento'] else Decimal('0')
                }

            return None

        finally:
            cursor.close()


class MySQLProductRepository:
    """
    MySQL implementation of IProductRepository
    Handles all product-related database operations
    """

    def __init__(self, connection):
        """
        Initialize repository with database connection

        Args:
            connection: Active database connection (dependency injection)
        """
        self.conn = connection

    def get_all_products(self, group_id: Optional[int] = None) -> List[Dict]:
        """
        Get all active products from database
        
        Args:
            group_id: Optional - if provided, includes price for that specific group
        """
        cursor = self.conn.cursor()

        try:
            # Always load ALL products, but get price for specific group if provided
            if group_id:
                # Get all products with their group-specific price (NULL if no price for group)
                query = """
                    SELECT
                        p.id_producto as id,
                        p.nombre_producto as nombre,
                        p.unidad_producto as unidad,
                        p.stock,
                        p.es_especial,
                        ppg.precio_base as precio
                    FROM producto p
                    LEFT JOIN precio_por_grupo ppg ON p.id_producto = ppg.id_producto
                        AND ppg.id_grupo = %s
                    ORDER BY p.nombre_producto
                """
                cursor.execute(query, (group_id,))
            else:
                # Fallback: Get all products with minimum price
                query = """
                    SELECT
                        p.id_producto as id,
                        p.nombre_producto as nombre,
                        p.unidad_producto as unidad,
                        p.stock,
                        p.es_especial,
                        COALESCE(ppg.precio_base, 0) as precio
                    FROM producto p
                    LEFT JOIN (
                        SELECT id_producto, MIN(precio_base) as precio_base
                        FROM precio_por_grupo
                        GROUP BY id_producto
                    ) ppg ON p.id_producto = ppg.id_producto
                    ORDER BY p.nombre_producto
                """
                cursor.execute(query)

            productos = cursor.fetchall()

            # Format for UbicuoAI
            formatted = []
            for p in (productos or []):
                # precio will be None if no price exists for the group
                precio_valor = p['precio']
                has_price = precio_valor is not None and float(precio_valor) > 0
                
                formatted.append({
                    'id': p['id'],
                    'nombre': p['nombre'],
                    'unidad': p['unidad'] or 'pz',
                    'precio': Decimal(str(precio_valor)) if precio_valor else None,
                    'has_price': has_price,  # Flag to indicate if product has valid price
                    'categoria': 'Especial' if p.get('es_especial') else 'General',
                    'stock': Decimal(str(p['stock'])) if p.get('stock') else Decimal('0')
                })

            return formatted

        finally:
            cursor.close()

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT
                    id_producto as id,
                    nombre_producto as nombre,
                    unidad_producto as unidad,
                    stock,
                    es_especial
                FROM producto
                WHERE id_producto = %s
            """

            cursor.execute(query, (product_id,))
            producto = cursor.fetchone()

            if producto:
                return {
                    'id': producto['id'],
                    'nombre': producto['nombre'],
                    'unidad': producto['unidad'] or 'pz',
                    'stock': Decimal(str(producto['stock'])) if producto.get('stock') else Decimal('0'),
                    'es_especial': producto.get('es_especial', False)
                }

            return None

        finally:
            cursor.close()

    def search_products(self, search_term: str, limit: int = 50) -> List[Dict]:
        """Search products by name"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT
                    id_producto as id,
                    nombre_producto as nombre,
                    unidad_producto as unidad,
                    stock
                FROM producto
                WHERE nombre_producto LIKE %s
                ORDER BY nombre_producto
                LIMIT %s
            """

            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, limit))
            productos = cursor.fetchall()

            return [{
                'id': p['id'],
                'nombre': p['nombre'],
                'unidad': p['unidad'] or 'pz',
                'stock': Decimal(str(p['stock'])) if p.get('stock') else Decimal('0')
            } for p in (productos or [])]

        finally:
            cursor.close()

    def get_product_price(
        self,
        product_id: int,
        group_id: Optional[int] = None
    ) -> Decimal:
        """Get product price (optionally for specific group)"""
        cursor = self.conn.cursor()

        try:
            if group_id:
                # Group-specific price
                query = """
                    SELECT precio_base
                    FROM precio_por_grupo
                    WHERE id_producto = %s AND id_grupo = %s
                """
                cursor.execute(query, (product_id, group_id))
            else:
                # General price (first available)
                query = """
                    SELECT precio_base
                    FROM precio_por_grupo
                    WHERE id_producto = %s
                    LIMIT 1
                """
                cursor.execute(query, (product_id,))

            result = cursor.fetchone()
            return Decimal(str(result['precio_base'])) if result else Decimal('0')

        finally:
            cursor.close()


class MySQLLearningRepository:
    """
    MySQL implementation of ILearningRepository
    Stores learning corrections in ubicuoai_learning table
    """

    def __init__(self, connection):
        """
        Initialize repository with database connection

        Args:
            connection: Active database connection (dependency injection)
        """
        self.conn = connection
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Create learning table if it doesn't exist"""
        cursor = self.conn.cursor()

        try:
            query = """
                CREATE TABLE IF NOT EXISTS ubicuoai_learning (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    incorrect VARCHAR(200) NOT NULL UNIQUE,
                    correct VARCHAR(200) NOT NULL,
                    times_used INT NOT NULL DEFAULT 1,
                    first_added DATETIME NOT NULL,
                    last_used DATETIME NOT NULL,
                    confidence_boost DECIMAL(3, 2) NOT NULL DEFAULT 0.05,
                    INDEX idx_incorrect (incorrect),
                    INDEX idx_last_used (last_used)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """

            cursor.execute(query)
            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            # Table might already exist, that's okay
            pass
        finally:
            cursor.close()

    def get_all_corrections(self) -> Dict[str, LearningCorrection]:
        """Get all learning corrections"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT
                    incorrect,
                    correct,
                    times_used,
                    first_added,
                    last_used,
                    confidence_boost
                FROM ubicuoai_learning
                ORDER BY times_used DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            corrections = {}
            for row in (results or []):
                correction = LearningCorrection(
                    incorrect=row['incorrect'],
                    correct=row['correct'],
                    times_used=row['times_used'],
                    first_added=row['first_added'],
                    last_used=row['last_used'],
                    confidence_boost=float(row['confidence_boost'])
                )
                corrections[row['incorrect'].lower()] = correction

            return corrections

        finally:
            cursor.close()

    def get_correction(self, incorrect: str) -> Optional[LearningCorrection]:
        """Get correction for specific incorrect text"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT
                    incorrect,
                    correct,
                    times_used,
                    first_added,
                    last_used,
                    confidence_boost
                FROM ubicuoai_learning
                WHERE incorrect = %s
            """

            cursor.execute(query, (incorrect,))
            row = cursor.fetchone()

            if row:
                return LearningCorrection(
                    incorrect=row['incorrect'],
                    correct=row['correct'],
                    times_used=row['times_used'],
                    first_added=row['first_added'],
                    last_used=row['last_used'],
                    confidence_boost=float(row['confidence_boost'])
                )

            return None

        finally:
            cursor.close()

    def save_correction(self, correction: LearningCorrection) -> bool:
        """Save or update a correction"""
        cursor = self.conn.cursor()

        try:
            query = """
                INSERT INTO ubicuoai_learning (
                    incorrect,
                    correct,
                    times_used,
                    first_added,
                    last_used,
                    confidence_boost
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    correct = VALUES(correct),
                    times_used = VALUES(times_used),
                    last_used = VALUES(last_used),
                    confidence_boost = VALUES(confidence_boost)
            """

            cursor.execute(
                query,
                (
                    correction.incorrect,
                    correction.correct,
                    correction.times_used,
                    correction.first_added,
                    correction.last_used,
                    correction.confidence_boost
                )
            )
            self.conn.commit()

            return True

        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def delete_correction(self, incorrect: str) -> bool:
        """Delete a correction"""
        cursor = self.conn.cursor()

        try:
            query = """
                DELETE FROM ubicuoai_learning
                WHERE incorrect = %s
            """

            cursor.execute(query, (incorrect,))
            self.conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def increment_usage(self, incorrect: str) -> bool:
        """Increment usage counter for a correction"""
        cursor = self.conn.cursor()

        try:
            query = """
                UPDATE ubicuoai_learning
                SET
                    times_used = times_used + 1,
                    last_used = %s
                WHERE incorrect = %s
            """

            cursor.execute(query, (datetime.now(), incorrect))
            self.conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def get_statistics(self) -> Dict:
        """Get learning system statistics"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT
                    COUNT(*) as total_entries,
                    SUM(times_used) as total_uses,
                    AVG(times_used) as avg_uses
                FROM ubicuoai_learning
            """

            cursor.execute(query)
            row = cursor.fetchone()

            if row and row['total_entries'] > 0:
                return {
                    'total_entries': row['total_entries'],
                    'total_uses': row['total_uses'] or 0,
                    'avg_uses_per_entry': round(float(row['avg_uses'] or 0), 2)
                }

            return {
                'total_entries': 0,
                'total_uses': 0,
                'avg_uses_per_entry': 0.0
            }

        finally:
            cursor.close()

    def cleanup_old_entries(
        self,
        max_age_days: int = 180,
        min_usage: int = 1
    ) -> int:
        """Clean up old, rarely-used corrections"""
        cursor = self.conn.cursor()

        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)

            query = """
                DELETE FROM ubicuoai_learning
                WHERE last_used < %s
                  AND times_used < %s
            """

            cursor.execute(query, (cutoff_date, min_usage))
            self.conn.commit()

            return cursor.rowcount

        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()