# -*- coding: utf-8 -*-
"""
Product Repository
Handles all product-related database operations
"""

from typing import List, Dict, Any
from src.modules.receipts.database.base_repository import BaseRepository
from src.modules.receipts.constants import DatabaseTables, ValidationRules


class ProductRepository(BaseRepository):
    """Repository for producto table"""

    def __init__(self):
        super().__init__()
        self.table_name = DatabaseTables.PRODUCTO

    def search_products(
        self,
        id_grupo: int,
        search_text: str
    ) -> List[Dict[str, Any]]:
        """
        Search products by name for a specific group

        Args:
            id_grupo: Group ID for pricing
            search_text: Search query (matches start of product name)

        Returns:
            List of product dictionaries with pricing
        """
        if len(search_text) < ValidationRules.MIN_SEARCH_LENGTH:
            return []

        query = """
            SELECT
                p.id_producto,
                p.nombre_producto,
                p.unidad_producto as unidad,
                p.stock,
                COALESCE(ppg.precio_base, 0) as precio_base,
                COALESCE(tc.descuento, 0) as descuento,
                ROUND(COALESCE(ppg.precio_base * (1 - tc.descuento/100), 0), 2) as precio
            FROM producto p
            LEFT JOIN precio_por_grupo ppg
                ON p.id_producto = ppg.id_producto
                AND ppg.id_grupo = %s
            LEFT JOIN grupo g
                ON ppg.id_grupo = g.id_grupo
            LEFT JOIN tipo_cliente tc
                ON g.id_tipo_cliente = tc.id_tipo_cliente
            WHERE LOWER(p.nombre_producto) LIKE %s
            ORDER BY p.nombre_producto
        """

        search_pattern = f"{search_text.lower()}%"
        results = self._execute_query(
            query,
            (id_grupo, search_pattern),
            fetch_all=True
        )

        # Filter to only exact prefix matches
        filtered = [
            p for p in (results or [])
            if p['nombre_producto'].lower().startswith(search_text.lower())
        ]

        return filtered

    def get_products_with_prices(
        self,
        id_grupo: int,
        only_active: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all products with prices for a group"""
        query = """
            SELECT
                p.id_producto,
                p.nombre_producto,
                p.unidad_producto as unidad,
                COALESCE(ppg.precio_base, 0) as precio_base,
                COALESCE(tc.descuento, 0) as descuento,
                ROUND(COALESCE(ppg.precio_base * (1 - tc.descuento/100), 0), 2) as precio,
                p.stock
            FROM producto p
            LEFT JOIN precio_por_grupo ppg
                ON p.id_producto = ppg.id_producto
                AND ppg.id_grupo = %s
            LEFT JOIN grupo g
                ON ppg.id_grupo = g.id_grupo
            LEFT JOIN tipo_cliente tc
                ON g.id_tipo_cliente = tc.id_tipo_cliente
            WHERE 1=1
        """

        params = [id_grupo]

        if only_active:
            query += " AND p.stock > 0"

        query += " ORDER BY p.nombre_producto"

        return self._execute_query(query, tuple(params), fetch_all=True) or []

    def get_products_prices_by_ids(
        self,
        product_ids: List[int],
        id_grupo: int
    ) -> Dict[int, float]:
        """
        Get prices for specific products and group

        Args:
            product_ids: List of product IDs
            id_grupo: Group ID

        Returns:
            Dictionary mapping id_producto -> calculated price
        """
        if not product_ids:
            return {}

        # Create placeholders for IN clause
        placeholders = ', '.join(['%s'] * len(product_ids))
        
        query = f"""
            SELECT
                p.id_producto,
                ROUND(COALESCE(ppg.precio_base * (1 - tc.descuento/100), 0), 2) as precio
            FROM producto p
            LEFT JOIN precio_por_grupo ppg
                ON p.id_producto = ppg.id_producto
                AND ppg.id_grupo = %s
            LEFT JOIN grupo g
                ON ppg.id_grupo = g.id_grupo
            LEFT JOIN tipo_cliente tc
                ON g.id_tipo_cliente = tc.id_tipo_cliente
            WHERE p.id_producto IN ({placeholders})
        """

        # Params: id_grupo first, then all product_ids
        params = [id_grupo] + product_ids
        
        results = self._execute_query(query, tuple(params), fetch_all=True)
        
        # Convert to dict
        prices = {}
        for row in (results or []):
            prices[row['id_producto']] = float(row['precio']) if row['precio'] is not None else 0.0
            
        return prices
