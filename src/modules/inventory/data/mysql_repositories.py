# -*- coding: utf-8 -*-
"""
MySQL Repositories para módulo de inventario
Con sistema de reciclaje de IDs de productos
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime, date
import pymysql.cursors
from ..domain.models import Product, Purchase, PurchaseSearchCriteria


class MySQLProductRepository:
    """MySQL implementation of product repository con reciclaje de IDs"""

    def __init__(self, connection):
        """
        Initialize with database connection

        Args:
            connection: MySQL database connection
        """
        if connection is None:
            raise ValueError("Database connection cannot be None")
        self.conn = connection
        self.cursor = connection.cursor()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        if product_id is None or product_id <= 0:
            return None

        self.cursor.execute("""
            SELECT id_producto, nombre_producto, unidad_producto, stock, es_especial
            FROM producto
            WHERE id_producto = %s
        """, (product_id,))

        row = self.cursor.fetchone()
        return self._map_to_product(row) if row else None

    def get_all(self) -> List[Product]:
        """Get all products ordered by name"""
        self.cursor.execute("""
            SELECT id_producto, nombre_producto, unidad_producto, stock, es_especial
            FROM producto
            ORDER BY nombre_producto
        """)

        rows = self.cursor.fetchall()
        return [self._map_to_product(row) for row in rows]

    def get_by_name(self, nombre: str) -> Optional[Product]:
        """Get product by exact name"""
        if not nombre:
            return None

        self.cursor.execute("""
            SELECT id_producto, nombre_producto, unidad_producto, stock, es_especial
            FROM producto
            WHERE nombre_producto = %s
        """, (nombre,))

        row = self.cursor.fetchone()
        return self._map_to_product(row) if row else None

    def create(self, product: Product) -> int:
        """Create a new product, returns the new product ID
        
        Reutiliza IDs reciclados si están disponibles, de lo contrario usa AUTO_INCREMENT
        """
        # Paso 1: Intentar obtener un ID reciclado
        recycled_id = self._get_recycled_id()
        
        if recycled_id:
            # Insertar con ID específico - deshabilitar AUTO_INCREMENT temporalmente
            try:
                self.cursor.execute("SET SESSION sql_mode='NO_AUTO_VALUE_ON_ZERO'")
                self.cursor.execute("""
                    INSERT INTO producto
                    (id_producto, nombre_producto, unidad_producto, stock, es_especial)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    recycled_id,
                    product.nombre_producto,
                    product.unidad_producto,
                    float(product.stock),
                    product.es_especial
                ))
                self.conn.commit()
                self.cursor.execute("SET SESSION sql_mode=''")
                return recycled_id
            except Exception as e:
                print(f"Error al insertar ID reciclado: {e}")
                # Si falla, usar AUTO_INCREMENT normal
                self.cursor.execute("""
                    INSERT INTO producto
                    (nombre_producto, unidad_producto, stock, es_especial)
                    VALUES (%s, %s, %s, %s)
                """, (
                    product.nombre_producto,
                    product.unidad_producto,
                    float(product.stock),
                    product.es_especial
                ))
                self.conn.commit()
                return self.cursor.lastrowid
        else:
            # Usar AUTO_INCREMENT normal
            self.cursor.execute("""
                INSERT INTO producto
                (nombre_producto, unidad_producto, stock, es_especial)
                VALUES (%s, %s, %s, %s)
            """, (
                product.nombre_producto,
                product.unidad_producto,
                float(product.stock),
                product.es_especial
            ))
            self.conn.commit()
            return self.cursor.lastrowid
    
    def _get_recycled_id(self) -> Optional[int]:
        """Obtiene el ID reciclado más antiguo disponible y lo elimina de la cola"""
        try:
            # Obtener el ID más antiguo
            self.cursor.execute("""
                SELECT id_disponible FROM producto_ids_reciclados
                ORDER BY fecha_reciclado ASC
                LIMIT 1
            """)
            row = self.cursor.fetchone()
            
            if row:
                recycled_id = row['id_disponible'] if isinstance(row, dict) else row[0]
                # Eliminar de la tabla de reciclados
                self.cursor.execute("""
                    DELETE FROM producto_ids_reciclados
                    WHERE id_disponible = %s
                """, (recycled_id,))
                self.conn.commit()
                return recycled_id
            return None
        except Exception as e:
            # Si algo falla, retornar None y usar AUTO_INCREMENT
            print(f"Error obteniendo ID reciclado: {e}")
            return None

    def update(self, product: Product) -> None:
        """Update existing product"""
        if product.id_producto is None:
            raise ValueError("Cannot update product without ID")

        self.cursor.execute("""
            UPDATE producto
            SET nombre_producto = %s,
                unidad_producto = %s,
                stock = %s,
                es_especial = %s
            WHERE id_producto = %s
        """, (
            product.nombre_producto,
            product.unidad_producto,
            float(product.stock),
            product.es_especial,
            product.id_producto
        ))

        self.conn.commit()

    def delete(self, product_id: int) -> None:
        """Delete product"""
        if product_id is None or product_id <= 0:
            raise ValueError("Invalid product ID")

        self.cursor.execute("DELETE FROM producto WHERE id_producto = %s", (product_id,))
        self.conn.commit()

    def update_stock(self, product_id: int, quantity: Decimal, add: bool = True) -> None:
        """Update product stock"""
        if product_id is None or product_id <= 0:
            raise ValueError("Invalid product ID")

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        operation = "+" if add else "-"
        self.cursor.execute(f"""
            UPDATE producto
            SET stock = stock {operation} %s
            WHERE id_producto = %s
        """, (float(quantity), product_id))

        self.conn.commit()

    def get_stock(self, product_id: int) -> Decimal:
        """Get current stock for a product"""
        if product_id is None or product_id <= 0:
            return Decimal("0")

        self.cursor.execute("SELECT stock FROM producto WHERE id_producto = %s", (product_id,))
        row = self.cursor.fetchone()

        return Decimal(str(row['stock'])) if row else Decimal("0")

    def _map_to_product(self, row) -> Product:
        """Map database row to Product entity"""
        return Product(
            id_producto=row['id_producto'],
            nombre_producto=row['nombre_producto'],
            unidad_producto=row['unidad_producto'],
            stock=Decimal(str(row['stock'])),
            es_especial=bool(row['es_especial'])
        )


class MySQLPurchaseRepository:
    """MySQL implementation of purchase repository"""

    def __init__(self, connection):
        """
        Initialize with database connection

        Args:
            connection: MySQL database connection
        """
        if connection is None:
            raise ValueError("Database connection cannot be None")
        self.conn = connection
        self.cursor = connection.cursor()

    def get_by_id(self, purchase_id: int) -> Optional[Purchase]:
        """Get purchase by ID"""
        if purchase_id is None or purchase_id <= 0:
            return None

        self.cursor.execute("""
            SELECT
                c.id_compra,
                c.id_producto,
                c.cantidad_compra,
                c.precio_unitario_compra,
                c.fecha_compra,
                c.fecha_registro,
                c.folio_factura,
                c.proveedor,
                c.rfc_proveedor,
                c.importe_ieps,
                c.tasa_interes,
                c.metodo_pago,
                c.forma_pago,
                c.subtotal,
                c.iva,
                c.total_con_impuestos,
                c.usuario_registro,
                c.notas,
                p.nombre_producto,
                p.unidad_producto
            FROM compra c
            INNER JOIN producto p ON c.id_producto = p.id_producto
            WHERE c.id_compra = %s
        """, (purchase_id,))

        row = self.cursor.fetchone()
        return self._map_to_purchase(row) if row else None

    def get_all(self) -> List[Purchase]:
        """Get all purchases ordered by date (newest first)"""
        self.cursor.execute("""
            SELECT
                c.id_compra,
                c.id_producto,
                c.cantidad_compra,
                c.precio_unitario_compra,
                c.fecha_compra,
                c.fecha_registro,
                c.folio_factura,
                c.proveedor,
                c.rfc_proveedor,
                c.importe_ieps,
                c.tasa_interes,
                c.metodo_pago,
                c.forma_pago,
                c.subtotal,
                c.iva,
                c.total_con_impuestos,
                c.usuario_registro,
                c.notas,
                p.nombre_producto,
                p.unidad_producto
            FROM compra c
            INNER JOIN producto p ON c.id_producto = p.id_producto
            ORDER BY c.fecha_compra DESC, c.id_compra DESC
        """)

        rows = self.cursor.fetchall()
        return [self._map_to_purchase(row) for row in rows]

    def search(self, criteria: PurchaseSearchCriteria) -> List[Purchase]:
        """Search purchases with filters"""
        # Get all purchases first
        all_purchases = self.get_all()
        
        if not criteria.has_filters():
            return all_purchases
        
        # Apply filters in memory
        results = []
        for purchase in all_purchases:
            # Search text filter
            if criteria.search_text:
                search_lower = criteria.search_text.lower()
                if not (search_lower in purchase.nombre_producto.lower() or
                       (purchase.proveedor and search_lower in purchase.proveedor.lower()) or
                       (purchase.folio_factura and search_lower in purchase.folio_factura.lower())):
                    continue
            
            # Date range filters
            if criteria.fecha_inicio and purchase.fecha_compra < criteria.fecha_inicio:
                continue
            if criteria.fecha_fin and purchase.fecha_compra > criteria.fecha_fin:
                continue
            
            # Fiscal info filters
            if criteria.solo_fiscales and not purchase.has_fiscal_info():
                continue
            if criteria.solo_informales and purchase.has_fiscal_info():
                continue
            
            # Supplier filter
            if criteria.proveedor and purchase.proveedor != criteria.proveedor:
                continue
            
            results.append(purchase)
        
        return results

    def create(self, purchase: Purchase) -> int:
        """Create a new purchase, returns the new purchase ID"""
        self.cursor.execute("""
            INSERT INTO compra
            (id_producto, cantidad_compra, precio_unitario_compra, fecha_compra,
             fecha_registro, folio_factura, proveedor, rfc_proveedor, importe_ieps,
             tasa_interes, metodo_pago, forma_pago, subtotal, iva,
             total_con_impuestos, usuario_registro, notas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            purchase.id_producto,
            float(purchase.cantidad_compra),
            float(purchase.precio_unitario_compra),
            purchase.fecha_compra,
            purchase.fecha_registro,
            purchase.folio_factura,
            purchase.proveedor,
            purchase.rfc_proveedor,
            float(purchase.importe_ieps),
            float(purchase.tasa_interes),
            purchase.metodo_pago,
            purchase.forma_pago,
            float(purchase.subtotal),
            float(purchase.iva),
            float(purchase.total_con_impuestos),
            purchase.usuario_registro,
            purchase.notas
        ))

        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, purchase: Purchase) -> None:
        """Update existing purchase"""
        if purchase.id_compra is None:
            raise ValueError("Cannot update purchase without ID")

        self.cursor.execute("""
            UPDATE compra SET
                cantidad_compra = %s,
                precio_unitario_compra = %s,
                fecha_compra = %s,
                fecha_registro = %s,
                folio_factura = %s,
                proveedor = %s,
                rfc_proveedor = %s,
                importe_ieps = %s,
                tasa_interes = %s,
                metodo_pago = %s,
                forma_pago = %s,
                subtotal = %s,
                iva = %s,
                total_con_impuestos = %s,
                notas = %s
            WHERE id_compra = %s
        """, (
            float(purchase.cantidad_compra),
            float(purchase.precio_unitario_compra),
            purchase.fecha_compra,
            purchase.fecha_registro,
            purchase.folio_factura,
            purchase.proveedor,
            purchase.rfc_proveedor,
            float(purchase.importe_ieps),
            float(purchase.tasa_interes),
            purchase.metodo_pago,
            purchase.forma_pago,
            float(purchase.subtotal),
            float(purchase.iva),
            float(purchase.total_con_impuestos),
            purchase.notas,
            purchase.id_compra
        ))

        self.conn.commit()

    def delete(self, purchase_id: int) -> None:
        """Delete purchase"""
        if purchase_id is None or purchase_id <= 0:
            raise ValueError("Invalid purchase ID")

        self.cursor.execute("DELETE FROM compra WHERE id_compra = %s", (purchase_id,))
        self.conn.commit()

    def get_by_product(self, product_id: int) -> List[Purchase]:
        """Get all purchases for a specific product"""
        if product_id is None or product_id <= 0:
            return []

        self.cursor.execute("""
            SELECT
                c.id_compra,
                c.id_producto,
                c.cantidad_compra,
                c.precio_unitario_compra,
                c.fecha_compra,
                c.fecha_registro,
                c.folio_factura,
                c.proveedor,
                c.rfc_proveedor,
                c.importe_ieps,
                c.tasa_interes,
                c.metodo_pago,
                c.forma_pago,
                c.subtotal,
                c.iva,
                c.total_con_impuestos,
                c.usuario_registro,
                c.notas,
                p.nombre_producto,
                p.unidad_producto
            FROM compra c
            INNER JOIN producto p ON c.id_producto = p.id_producto
            WHERE c.id_producto = %s
            ORDER BY c.fecha_compra DESC
        """, (product_id,))

        rows = self.cursor.fetchall()
        return [self._map_to_purchase(row) for row in rows]

    def get_by_supplier(self, supplier: str) -> List[Purchase]:
        """Get all purchases from a specific supplier"""
        if not supplier:
            return []

        self.cursor.execute("""
            SELECT
                c.id_compra,
                c.id_producto,
                c.cantidad_compra,
                c.precio_unitario_compra,
                c.fecha_compra,
                c.fecha_registro,
                c.folio_factura,
                c.proveedor,
                c.rfc_proveedor,
                c.importe_ieps,
                c.tasa_interes,
                c.metodo_pago,
                c.forma_pago,
                c.subtotal,
                c.iva,
                c.total_con_impuestos,
                c.usuario_registro,
                c.notas,
                p.nombre_producto,
                p.unidad_producto
            FROM compra c
            INNER JOIN producto p ON c.id_producto = p.id_producto
            WHERE c.proveedor = %s
            ORDER BY c.fecha_compra DESC
        """, (supplier,))

        rows = self.cursor.fetchall()
        return [self._map_to_purchase(row) for row in rows]

    def get_fiscal_purchases(self) -> List[Purchase]:
        """Get only purchases with complete fiscal information"""
        self.cursor.execute("""
            SELECT
                c.id_compra,
                c.id_producto,
                c.cantidad_compra,
                c.precio_unitario_compra,
                c.fecha_compra,
                c.fecha_registro,
                c.folio_factura,
                c.proveedor,
                c.rfc_proveedor,
                c.importe_ieps,
                c.tasa_interes,
                c.metodo_pago,
                c.forma_pago,
                c.subtotal,
                c.iva,
                c.total_con_impuestos,
                c.usuario_registro,
                c.notas,
                p.nombre_producto,
                p.unidad_producto
            FROM compra c
            INNER JOIN producto p ON c.id_producto = p.id_producto
            WHERE c.folio_factura IS NOT NULL
              AND c.proveedor IS NOT NULL
              AND c.rfc_proveedor IS NOT NULL
            ORDER BY c.fecha_compra DESC
        """)

        rows = self.cursor.fetchall()
        return [self._map_to_purchase(row) for row in rows]

    def get_informal_purchases(self) -> List[Purchase]:
        """Get only purchases without fiscal information"""
        self.cursor.execute("""
            SELECT
                c.id_compra,
                c.id_producto,
                c.cantidad_compra,
                c.precio_unitario_compra,
                c.fecha_compra,
                c.fecha_registro,
                c.folio_factura,
                c.proveedor,
                c.rfc_proveedor,
                c.importe_ieps,
                c.tasa_interes,
                c.metodo_pago,
                c.forma_pago,
                c.subtotal,
                c.iva,
                c.total_con_impuestos,
                c.usuario_registro,
                c.notas,
                p.nombre_producto,
                p.unidad_producto
            FROM compra c
            INNER JOIN producto p ON c.id_producto = p.id_producto
            WHERE c.folio_factura IS NULL
              OR c.proveedor IS NULL
              OR c.rfc_proveedor IS NULL
            ORDER BY c.fecha_compra DESC
        """)

        rows = self.cursor.fetchall()
        return [self._map_to_purchase(row) for row in rows]

    def _map_to_purchase(self, row) -> Purchase:
        """Map database row to Purchase entity"""
        # Convert date fields
        fecha_compra = row['fecha_compra']
        if isinstance(fecha_compra, datetime):
            fecha_compra = fecha_compra.date()

        fecha_registro = row.get('fecha_registro', fecha_compra)
        if isinstance(fecha_registro, datetime):
            fecha_registro = fecha_registro.date()

        return Purchase(
            id_compra=row['id_compra'],
            id_producto=row['id_producto'],
            cantidad_compra=Decimal(str(row['cantidad_compra'])),
            precio_unitario_compra=Decimal(str(row['precio_unitario_compra'])),
            fecha_compra=fecha_compra,
            fecha_registro=fecha_registro,
            folio_factura=row.get('folio_factura'),
            proveedor=row.get('proveedor'),
            rfc_proveedor=row.get('rfc_proveedor'),
            importe_ieps=Decimal(str(row.get('importe_ieps', 0))),
            tasa_interes=Decimal(str(row.get('tasa_interes', 0))),
            metodo_pago=row.get('metodo_pago', 'PUE'),
            forma_pago=row.get('forma_pago', '03'),
            subtotal=Decimal(str(row.get('subtotal', 0))),
            iva=Decimal(str(row.get('iva', 0))),
            total_con_impuestos=Decimal(str(row.get('total_con_impuestos', 0))),
            usuario_registro=row.get('usuario_registro'),
            notas=row.get('notas'),
            nombre_producto=row.get('nombre_producto'),
            unidad_producto=row.get('unidad_producto')
        )