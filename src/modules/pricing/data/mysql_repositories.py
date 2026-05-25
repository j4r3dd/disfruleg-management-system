# -*- coding: utf-8 -*-
"""
MySQL Repository Implementations - Pricing Module
Concrete implementations of repository interfaces
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import pymysql

from ..domain.models import (
    Product,
    Group,
    ClientType,
    PriceByGroup,
    ProductPrice,
    ProductLock
)
from ..domain.exceptions import (
    ProductNotFoundError,
    GroupNotFoundError,
    ClientTypeNotFoundError,
    DuplicateProductError
)


class MySQLProductRepository:
    """MySQL implementation of IProductRepository"""

    def __init__(self, connection):
        """
        Initialize repository with database connection

        Args:
            connection: MySQL connection object
        """
        self.conn = connection

    def get_all(self, filter_ids: Optional[List[int]] = None) -> List[Product]:
        """Get all products, optionally filtered by IDs"""
        cursor = self.conn.cursor()

        try:
            if filter_ids:
                ids_str = ','.join(map(str, filter_ids))
                query = f"""
                    SELECT id_producto, nombre_producto, unidad_producto, stock, es_especial
                    FROM producto
                    WHERE id_producto IN ({ids_str})
                    ORDER BY nombre_producto
                """
                cursor.execute(query)
            else:
                query = """
                    SELECT id_producto, nombre_producto, unidad_producto, stock, es_especial
                    FROM producto
                    ORDER BY nombre_producto
                """
                cursor.execute(query)

            results = cursor.fetchall()
            return [
                Product(
                    id_producto=row['id_producto'],
                    nombre_producto=row['nombre_producto'],
                    unidad_producto=row['unidad_producto'],
                    stock=Decimal(str(row['stock'])) if row['stock'] else Decimal('0'),
                    es_especial=bool(row['es_especial'])
                )
                for row in results
            ]

        finally:
            cursor.close()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT id_producto, nombre_producto, unidad_producto, stock, es_especial
                FROM producto
                WHERE id_producto = %s
            """
            cursor.execute(query, (product_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return Product(
                id_producto=row['id_producto'],
                nombre_producto=row['nombre_producto'],
                unidad_producto=row['unidad_producto'],
                stock=Decimal(str(row['stock'])) if row['stock'] else Decimal('0'),
                es_especial=bool(row['es_especial'])
            )

        finally:
            cursor.close()

    def get_by_name(self, name: str) -> Optional[Product]:
        """Get product by name"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT id_producto, nombre_producto, unidad_producto, stock, es_especial
                FROM producto
                WHERE LOWER(nombre_producto) = LOWER(%s)
            """
            cursor.execute(query, (name,))
            row = cursor.fetchone()

            if not row:
                return None

            return Product(
                id_producto=row['id_producto'],
                nombre_producto=row['nombre_producto'],
                unidad_producto=row['unidad_producto'],
                stock=Decimal(str(row['stock'])) if row['stock'] else Decimal('0'),
                es_especial=bool(row['es_especial'])
            )

        finally:
            cursor.close()

    def create(self, product: Product) -> int:
        """Create new product, returns ID"""
        cursor = self.conn.cursor()

        try:
            # Check for duplicates - Fail Fast
            existing = self.get_by_name(product.nombre_producto)
            if existing:
                raise DuplicateProductError(
                    f"Product '{product.nombre_producto}' already exists"
                )

            query = """
                INSERT INTO producto (nombre_producto, unidad_producto, stock, es_especial)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (
                product.nombre_producto,
                product.unidad_producto,
                float(product.stock),
                product.es_especial
            ))
            self.conn.commit()

            return cursor.lastrowid

        except pymysql.IntegrityError as e:
            self.conn.rollback()
            raise DuplicateProductError(f"Product already exists: {str(e)}")
        finally:
            cursor.close()

    def update(self, product: Product) -> bool:
        """Update existing product"""
        cursor = self.conn.cursor()

        try:
            query = """
                UPDATE producto
                SET nombre_producto = %s,
                    unidad_producto = %s,
                    stock = %s,
                    es_especial = %s
                WHERE id_producto = %s
            """
            cursor.execute(query, (
                product.nombre_producto,
                product.unidad_producto,
                float(product.stock),
                product.es_especial,
                product.id_producto
            ))
            self.conn.commit()

            return cursor.rowcount > 0

        finally:
            cursor.close()

    def delete(self, product_id: int) -> bool:
        """Delete product by ID"""
        cursor = self.conn.cursor()

        try:
            query = "DELETE FROM producto WHERE id_producto = %s"
            cursor.execute(query, (product_id,))
            self.conn.commit()

            return cursor.rowcount > 0

        finally:
            cursor.close()

    def search(self, query: str, filter_ids: Optional[List[int]] = None) -> List[Product]:
        """Search products by name"""
        cursor = self.conn.cursor()

        try:
            search_pattern = f"%{query}%"

            if filter_ids:
                ids_str = ','.join(map(str, filter_ids))
                sql = f"""
                    SELECT id_producto, nombre_producto, unidad_producto, stock, es_especial
                    FROM producto
                    WHERE LOWER(nombre_producto) LIKE LOWER(%s)
                      AND id_producto IN ({ids_str})
                    ORDER BY nombre_producto
                """
                cursor.execute(sql, (search_pattern,))
            else:
                sql = """
                    SELECT id_producto, nombre_producto, unidad_producto, stock, es_especial
                    FROM producto
                    WHERE LOWER(nombre_producto) LIKE LOWER(%s)
                    ORDER BY nombre_producto
                """
                cursor.execute(sql, (search_pattern,))

            results = cursor.fetchall()
            return [
                Product(
                    id_producto=row['id_producto'],
                    nombre_producto=row['nombre_producto'],
                    unidad_producto=row['unidad_producto'],
                    stock=Decimal(str(row['stock'])) if row['stock'] else Decimal('0'),
                    es_especial=bool(row['es_especial'])
                )
                for row in results
            ]

        finally:
            cursor.close()


class MySQLGroupRepository:
    """MySQL implementation of IGroupRepository"""

    def __init__(self, connection):
        self.conn = connection

    def get_all(self) -> List[Group]:
        """Get all groups"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT id_grupo, clave_grupo, id_tipo_cliente, descripcion
                FROM grupo
                ORDER BY clave_grupo
            """
            cursor.execute(query)
            results = cursor.fetchall()

            return [
                Group(
                    id_grupo=row['id_grupo'],
                    clave_grupo=row['clave_grupo'],
                    id_tipo_cliente=row['id_tipo_cliente'],
                    descripcion=row.get('descripcion')
                )
                for row in results
            ]

        finally:
            cursor.close()

    def get_by_id(self, group_id: int) -> Optional[Group]:
        """Get group by ID"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT id_grupo, clave_grupo, id_tipo_cliente, descripcion
                FROM grupo
                WHERE id_grupo = %s
            """
            cursor.execute(query, (group_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return Group(
                id_grupo=row['id_grupo'],
                clave_grupo=row['clave_grupo'],
                id_tipo_cliente=row['id_tipo_cliente'],
                descripcion=row.get('descripcion')
            )

        finally:
            cursor.close()

    def get_client_count(self, group_id: int) -> int:
        """Get count of clients in a group"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT COUNT(*) as client_count
                FROM cliente
                WHERE id_grupo = %s
            """
            cursor.execute(query, (group_id,))
            result = cursor.fetchone()

            return result['client_count'] if result else 0

        finally:
            cursor.close()


class MySQLClientTypeRepository:
    """MySQL implementation of IClientTypeRepository"""

    def __init__(self, connection):
        self.conn = connection

    def get_all(self) -> List[ClientType]:
        """Get all client types"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT id_tipo_cliente, nombre_tipo, descuento
                FROM tipo_cliente
                ORDER BY nombre_tipo
            """
            cursor.execute(query)
            results = cursor.fetchall()

            return [
                ClientType(
                    id_tipo_cliente=row['id_tipo_cliente'],
                    nombre_tipo=row['nombre_tipo'],
                    descuento=Decimal(str(row['descuento']))
                )
                for row in results
            ]

        finally:
            cursor.close()

    def get_by_id(self, type_id: int) -> Optional[ClientType]:
        """Get client type by ID"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT id_tipo_cliente, nombre_tipo, descuento
                FROM tipo_cliente
                WHERE id_tipo_cliente = %s
            """
            cursor.execute(query, (type_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return ClientType(
                id_tipo_cliente=row['id_tipo_cliente'],
                nombre_tipo=row['nombre_tipo'],
                descuento=Decimal(str(row['descuento']))
            )

        finally:
            cursor.close()

    def get_by_group_id(self, group_id: int) -> Optional[ClientType]:
        """Get client type for a specific group"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT tc.id_tipo_cliente, tc.nombre_tipo, tc.descuento
                FROM tipo_cliente tc
                JOIN grupo g ON tc.id_tipo_cliente = g.id_tipo_cliente
                WHERE g.id_grupo = %s
            """
            cursor.execute(query, (group_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return ClientType(
                id_tipo_cliente=row['id_tipo_cliente'],
                nombre_tipo=row['nombre_tipo'],
                descuento=Decimal(str(row['descuento']))
            )

        finally:
            cursor.close()


class MySQLPriceRepository:
    """MySQL implementation of IPriceRepository"""

    def __init__(self, connection):
        self.conn = connection

    def get_by_product_and_group(
        self,
        product_id: int,
        group_id: int
    ) -> Optional[PriceByGroup]:
        """Get price for product in group"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT id_producto, id_grupo, precio_base
                FROM precio_por_grupo
                WHERE id_producto = %s AND id_grupo = %s
            """
            cursor.execute(query, (product_id, group_id))
            row = cursor.fetchone()

            if not row:
                return None

            return PriceByGroup(
                id_producto=row['id_producto'],
                id_grupo=row['id_grupo'],
                precio_base=Decimal(str(row['precio_base']))
            )

        finally:
            cursor.close()

    def get_all_by_group(
        self,
        group_id: int,
        filter_product_ids: Optional[List[int]] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> tuple[List[ProductPrice], int]:
        """
        Get all product prices for a group with pagination and search support

        Args:
            group_id: Group ID
            filter_product_ids: Optional list of product IDs to filter
            search_query: Optional search string for product names
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            Tuple of (product_prices, total_count)
        """
        cursor = self.conn.cursor()

        try:
            # First, get group and client type info (single row, cached data)
            group_query = """
                SELECT g.id_grupo, g.clave_grupo, tc.descuento, tc.nombre_tipo as nombre_tipo_cliente
                FROM grupo g
                LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                WHERE g.id_grupo = %s
            """
            cursor.execute(group_query, (group_id,))
            group_info = cursor.fetchone()

            if not group_info:
                return ([], 0)

            # Build WHERE clause conditions
            where_conditions = []
            query_params = [group_id]

            if filter_product_ids:
                ids_str = ','.join(map(str, filter_product_ids))
                where_conditions.append(f"p.id_producto IN ({ids_str})")

            if search_query:
                where_conditions.append("LOWER(p.nombre_producto) LIKE LOWER(%s)")
                query_params.append(f"%{search_query}%")

            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

            # First, get total count (for pagination)
            count_query = f"""
                SELECT COUNT(*) as total
                FROM producto p
                {where_clause}
            """
            cursor.execute(count_query, query_params[1:] if where_conditions else [])
            total_count = cursor.fetchone()['total']

            # Now query products with their prices
            query = f"""
                SELECT
                    p.id_producto,
                    p.nombre_producto,
                    p.unidad_producto,
                    p.stock,
                    p.es_especial,
                    COALESCE(ppg.precio_base, 0) as precio_base
                FROM producto p
                LEFT JOIN precio_por_grupo ppg
                    ON p.id_producto = ppg.id_producto AND ppg.id_grupo = %s
                {where_clause}
                ORDER BY p.nombre_producto
            """

            # Add pagination if limit is specified
            if limit is not None:
                query += f" LIMIT {int(limit)} OFFSET {int(offset)}"

            cursor.execute(query, query_params)
            results = cursor.fetchall()

            # Extract group info once (avoid repetition)
            descuento = Decimal(str(group_info['descuento']))

            product_prices = [
                ProductPrice(
                    id_producto=row['id_producto'],
                    nombre_producto=row['nombre_producto'],
                    unidad_producto=row['unidad_producto'],
                    stock=Decimal(str(row['stock'])) if row['stock'] else Decimal('0'),
                    es_especial=bool(row['es_especial']),
                    id_grupo=group_info['id_grupo'],
                    clave_grupo=group_info['clave_grupo'],
                    precio_base=Decimal(str(row['precio_base'])),
                    descuento=descuento,
                    precio_final=Decimal(str(row['precio_base'])) * (1 - descuento / 100),
                    nombre_tipo_cliente=group_info['nombre_tipo_cliente']
                )
                for row in results
            ]

            return (product_prices, total_count)

        finally:
            cursor.close()

    def set_base_price(
        self,
        product_id: int,
        group_id: int,
        base_price: Decimal
    ) -> bool:
        """Set or update base price for product in group"""
        cursor = self.conn.cursor()

        try:
            # Use INSERT ... ON DUPLICATE KEY UPDATE to avoid double query
            # Assumes there's a UNIQUE constraint on (id_producto, id_grupo)
            query = """
                INSERT INTO precio_por_grupo (id_producto, id_grupo, precio_base)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE precio_base = VALUES(precio_base)
            """
            cursor.execute(query, (product_id, group_id, float(base_price)))
            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def delete_by_product(self, product_id: int) -> bool:
        """Delete all prices for a product"""
        cursor = self.conn.cursor()

        try:
            query = "DELETE FROM precio_por_grupo WHERE id_producto = %s"
            cursor.execute(query, (product_id,))
            self.conn.commit()

            return cursor.rowcount > 0

        finally:
            cursor.close()


class MySQLLockRepository:
    """MySQL implementation of ILockRepository"""

    def __init__(self, connection):
        self.conn = connection
        self.ensure_lock_table_exists()

    def ensure_lock_table_exists(self) -> bool:
        """Ensure lock table exists in database"""
        cursor = self.conn.cursor()

        try:
            # Check if table exists
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name = 'producto_locks'
            """)

            result = cursor.fetchone()
            table_exists = result['count'] > 0 if result else False

            if not table_exists:
                # Create table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS producto_locks (
                        id_producto INT PRIMARY KEY,
                        usuario VARCHAR(50) NOT NULL,
                        modulo VARCHAR(50) NOT NULL,
                        fecha_bloqueo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id_producto)
                            REFERENCES producto(id_producto)
                            ON DELETE CASCADE
                    )
                """)
                self.conn.commit()

            return True

        except Exception as e:
            print(f"Error ensuring lock table exists: {e}")
            return False
        finally:
            cursor.close()

    def acquire_lock(
        self,
        product_id: int,
        usuario: str,
        modulo: str
    ) -> bool:
        """Try to acquire lock on product"""
        cursor = self.conn.cursor()

        try:
            # Check if already locked
            existing_lock = self.get_lock(product_id)

            if existing_lock and existing_lock.usuario != usuario:
                # Locked by someone else
                return False

            if existing_lock and existing_lock.usuario == usuario:
                # Already locked by this user
                return True

            # Acquire new lock
            query = """
                INSERT INTO producto_locks (id_producto, usuario, modulo, fecha_bloqueo)
                VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(query, (product_id, usuario, modulo))
            self.conn.commit()

            return True

        except pymysql.IntegrityError:
            # Lock already exists
            self.conn.rollback()
            return False
        finally:
            cursor.close()

    def release_lock(self, product_id: int) -> bool:
        """Release lock on product"""
        cursor = self.conn.cursor()

        try:
            query = "DELETE FROM producto_locks WHERE id_producto = %s"
            cursor.execute(query, (product_id,))
            self.conn.commit()

            return cursor.rowcount > 0

        finally:
            cursor.close()

    def get_lock(self, product_id: int) -> Optional[ProductLock]:
        """Get current lock information"""
        cursor = self.conn.cursor()

        try:
            query = """
                SELECT id_producto, usuario, modulo, fecha_bloqueo
                FROM producto_locks
                WHERE id_producto = %s
            """
            cursor.execute(query, (product_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return ProductLock(
                id_producto=row['id_producto'],
                usuario=row['usuario'],
                modulo=row['modulo'],
                fecha_bloqueo=row['fecha_bloqueo']
            )

        finally:
            cursor.close()

    def release_all_by_user(self, usuario: str) -> int:
        """Release all locks held by user, returns count"""
        cursor = self.conn.cursor()

        try:
            query = "DELETE FROM producto_locks WHERE usuario = %s"
            cursor.execute(query, (usuario,))
            self.conn.commit()

            return cursor.rowcount

        finally:
            cursor.close()
