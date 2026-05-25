# -*- coding: utf-8 -*-
"""
MySQL Repository Implementations - Importacion Module
Concrete implementations of repository interfaces
"""

from typing import List, Optional, Tuple
from decimal import Decimal
import difflib

from ..domain.models import ProductMatch, SystemIntegrityCheck
from ..domain.exceptions import ProductMatchError, PriceApplicationError, SystemIntegrityError


class MySQLProductRepository:
    """MySQL implementation of IProductRepository"""

    def __init__(self, connection):
        """
        Initialize repository with database connection

        Args:
            connection: MySQL connection object
        """
        # Fail fast: Validate connection
        if connection is None:
            raise ValueError("Database connection cannot be None")

        if not hasattr(connection, 'cursor'):
            raise ValueError(f"Invalid database connection: {type(connection)}")

        self.conn = connection

    def search_similar(
        self,
        nombre: str,
        unidad: str
    ) -> Optional[ProductMatch]:
        """
        Search for similar product in database
        Uses exact match first, then fuzzy matching
        """
        # Fail fast: Validate inputs
        if not nombre or not nombre.strip():
            raise ValueError("Product name cannot be empty")

        if not unidad or not unidad.strip():
            raise ValueError("Product unit cannot be empty")

        cursor = self.conn.cursor()

        try:
            # Normalize unit for comparison
            unidad_normalizada = self._normalizar_unidad(unidad)

            # Try exact match first
            cursor.execute("""
                SELECT id_producto, nombre_producto, unidad_producto, stock
                FROM producto
                WHERE LOWER(TRIM(nombre_producto)) = LOWER(TRIM(%s))
                AND LOWER(TRIM(unidad_producto)) = %s
            """, (nombre, unidad_normalizada))

            result = cursor.fetchone()
            if result:
                return self._row_to_product_match(result)

            # Try fuzzy matching
            cursor.execute("""
                SELECT id_producto, nombre_producto, unidad_producto, stock
                FROM producto
                WHERE LOWER(TRIM(unidad_producto)) = %s
            """, (unidad_normalizada,))

            productos_bd = cursor.fetchall()
            mejor_match = None
            mejor_ratio = 0.85  # 85% similarity threshold

            for prod in productos_bd:
                nombre_bd = prod['nombre_producto'] if isinstance(prod, dict) else prod[1]

                ratio = difflib.SequenceMatcher(
                    None,
                    nombre.lower().strip(),
                    nombre_bd.lower().strip()
                ).ratio()

                if ratio > mejor_ratio:
                    mejor_ratio = ratio
                    mejor_match = self._row_to_product_match(prod)

            return mejor_match

        except Exception as e:
            raise ProductMatchError(f"Error searching for product '{nombre}': {e}")
        finally:
            cursor.close()

    def create_product(
        self,
        nombre: str,
        unidad: str,
        stock: Decimal = Decimal('0'),
        es_especial: bool = False
    ) -> int:
        """
        Create new product in database

        ✅ UPDATED: Allows negative stock (backorders, pending deliveries, etc.)
        """
        # Fail fast: Validate inputs
        if not nombre or not nombre.strip():
            raise ValueError("Product name cannot be empty")

        if not unidad or not unidad.strip():
            raise ValueError("Product unit cannot be empty")

        # ✅ REMOVED: Stock validation - negative stock is allowed

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO producto (nombre_producto, unidad_producto, stock, es_especial)
                VALUES (%s, %s, %s, %s)
            """, (nombre, unidad, float(stock), int(es_especial)))

            return cursor.lastrowid

        except Exception as e:
            raise ProductMatchError(f"Error creating product '{nombre}': {e}")
        finally:
            cursor.close()

    def get_by_id(self, product_id: int) -> Optional[ProductMatch]:
        """Get product by ID"""
        # Fail fast: Validate input
        if product_id <= 0:
            raise ValueError("Product ID must be positive")

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT id_producto, nombre_producto, unidad_producto, stock
                FROM producto
                WHERE id_producto = %s
            """, (product_id,))

            result = cursor.fetchone()
            return self._row_to_product_match(result) if result else None

        except Exception as e:
            raise ProductMatchError(f"Error fetching product {product_id}: {e}")
        finally:
            cursor.close()

    def _row_to_product_match(self, row) -> ProductMatch:
        """
        Convert database row to ProductMatch

        ✅ UPDATED: Preserves stock values as-is, including negative values
        Negative stock can represent backorders, pending deliveries, etc.
        """
        if isinstance(row, dict):
            return ProductMatch(
                id=row['id_producto'],
                nombre=row['nombre_producto'],
                unidad=row['unidad_producto'],
                stock=Decimal(str(row['stock'])) if row['stock'] is not None else Decimal('0')
            )
        else:
            return ProductMatch(
                id=row[0],
                nombre=row[1],
                unidad=row[2],
                stock=Decimal(str(row[3])) if row[3] is not None else Decimal('0')
            )

    def _normalizar_unidad(self, unidad: str) -> str:
        """Normalize product unit to standard form"""
        unidad = unidad.upper().strip()

        normalizaciones = {
            'KILO': 'kg', 'KG': 'kg', 'KILOS': 'kg', 'K': 'kg',
            'PIEZA': 'pz', 'PZ': 'pz', 'PZA': 'pz', 'PIEZAS': 'pz', 'UNIDAD': 'pz',
            'LIBRA': 'lb', 'LB': 'lb', 'LIBRAS': 'lb',
            'MANOJO': 'mjo', 'MJO': 'mjo', 'MJ': 'mjo', 'MANOJOS': 'mjo',
            'PAQUETE': 'paq', 'PAQ': 'paq', 'PQ': 'paq', 'PAQUETES': 'paq',
            'LITRO': 'lt', 'LT': 'lt', 'LITROS': 'lt', 'L': 'lt',
            'HECTOGRAMO': 'hg', 'HG': 'hg', 'HECTOGRAMOS': 'hg',
            'GRAMO': 'g', 'G': 'g', 'GRAMOS': 'g', 'GR': 'g',
            'BURBUJA': 'burbuja', 'GRANEL': 'granel', 'CUBETA': 'cubeta',
            'CAJA': 'caja', 'COSTAL': 'costal', 'CHAROLA': 'charola',
            'BOLSA': 'bolsa',
        }

        return normalizaciones.get(unidad, unidad.lower())


class MySQLPriceRepository:
    """MySQL implementation of IPriceRepository"""

    def __init__(self, connection):
        """
        Initialize repository with database connection

        Args:
            connection: MySQL connection object
        """
        # Fail fast: Validate connection
        if connection is None:
            raise ValueError("Database connection cannot be None")

        if not hasattr(connection, 'cursor'):
            raise ValueError(f"Invalid database connection: {type(connection)}")

        self.conn = connection

    def get_all_groups_with_discounts(self) -> List[Tuple]:
        """Get all groups with their discount information"""
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT g.id_grupo, g.clave_grupo, tc.descuento
                FROM grupo g
                LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                ORDER BY g.clave_grupo
            """)

            return cursor.fetchall()

        except Exception as e:
            raise PriceApplicationError(f"Error fetching groups: {e}")
        finally:
            cursor.close()

    def set_price_for_group(
        self,
        product_id: int,
        group_id: int,
        precio_base: Decimal
    ) -> bool:
        """Set base price for product in specific group"""
        # Fail fast: Validate inputs
        if product_id <= 0:
            raise ValueError("Product ID must be positive")

        if group_id <= 0:
            raise ValueError("Group ID must be positive")

        if precio_base < 0:
            raise ValueError("Price cannot be negative")

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO precio_por_grupo (id_producto, id_grupo, precio_base)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE precio_base = %s
            """, (product_id, group_id, precio_base, precio_base))

            return True

        except Exception as e:
            raise PriceApplicationError(
                f"Error setting price for product {product_id} in group {group_id}: {e}"
            )
        finally:
            cursor.close()

    def set_price_all_groups(
        self,
        product_id: int,
        precio_base: Decimal,
        grupos: List[Tuple]
    ) -> bool:
        """
        Set base price for product across all groups
        The same precio_base is set for all groups.
        The discount is applied at query time to calculate precio_final.
        """
        # Fail fast: Validate inputs
        if product_id <= 0:
            raise ValueError("Product ID must be positive")

        if precio_base < 0:
            raise ValueError("Price cannot be negative")

        if not grupos:
            raise ValueError("Groups list cannot be empty")

        cursor = self.conn.cursor()

        try:
            for grupo in grupos:
                if isinstance(grupo, dict):
                    id_grupo = grupo['id_grupo']
                else:
                    id_grupo = grupo[0]

                # Set the SAME precio_base for ALL groups
                # The discount will be applied when calculating precio_final in queries
                cursor.execute("""
                    INSERT INTO precio_por_grupo (id_producto, id_grupo, precio_base)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE precio_base = %s
                """, (product_id, id_grupo, precio_base, precio_base))

            return True

        except Exception as e:
            raise PriceApplicationError(
                f"Error setting prices for product {product_id} across all groups: {e}"
            )
        finally:
            cursor.close()


class MySQLSystemRepository:
    """MySQL implementation of ISystemRepository"""

    def __init__(self, connection):
        """
        Initialize repository with database connection

        Args:
            connection: MySQL connection object
        """
        # Fail fast: Validate connection
        if connection is None:
            raise ValueError("Database connection cannot be None")

        if not hasattr(connection, 'cursor'):
            raise ValueError(f"Invalid database connection: {type(connection)}")

        self.conn = connection

    def check_integrity(self) -> SystemIntegrityCheck:
        """Perform system integrity checks"""
        cursor = self.conn.cursor()

        try:
            # Check groups without client type
            cursor.execute("""
                SELECT g.id_grupo, g.clave_grupo
                FROM grupo g
                WHERE g.id_tipo_cliente IS NULL
            """)
            grupos_sin_tipo = cursor.fetchall()

            # Check invalid discounts
            cursor.execute("""
                SELECT nombre_tipo, descuento
                FROM tipo_cliente
                WHERE descuento < 0 OR descuento > 100
            """)
            descuentos_invalidos = cursor.fetchall()

            return SystemIntegrityCheck(
                grupos_sin_tipo=list(grupos_sin_tipo),
                descuentos_invalidos=list(descuentos_invalidos),
                tiene_advertencias=bool(grupos_sin_tipo or descuentos_invalidos)
            )

        except Exception as e:
            raise SystemIntegrityError(f"Error checking system integrity: {e}")
        finally:
            cursor.close()

    def log_import_operation(
        self,
        usuario: str,
        detalles: str
    ) -> bool:
        """Log import operation to system logs"""
        # Fail fast: Validate inputs
        if not usuario or not usuario.strip():
            raise ValueError("Usuario cannot be empty")

        if not detalles or not detalles.strip():
            raise ValueError("Detalles cannot be empty")

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO logs_sistema (usuario, modulo, accion, detalles)
                VALUES (%s, 'Importación', 'Importar cotización masiva', %s)
            """, (usuario, detalles))

            return True

        except Exception as e:
            # Log errors are non-critical, so we just return False
            print(f"Warning: Failed to log operation: {e}")
            return False
        finally:
            cursor.close()
