# -*- coding: utf-8 -*-
"""
Order Repository
Handles all database operations for orders
"""

from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from src.modules.receipts.database.base_repository import BaseRepository
from src.modules.receipts.constants import OrderState, DatabaseTables
from src.config import debug_print


class OrdenRepository(BaseRepository):
    """Repository for ordenes_guardadas table"""

    def __init__(self):
        super().__init__()
        self.table_name = DatabaseTables.ORDENES_GUARDADAS

    def find_active_orders(
        self,
        username: Optional[str] = None,
        is_admin: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all active (saved) orders

        Args:
            username: Filter by username (if not admin)
            is_admin: If True, return all orders

        Returns:
            List of order dictionaries
        """
        query = """
            SELECT
                og.folio_numero,
                og.id_cliente,
                c.nombre_cliente,
                og.usuario_creador,
                og.fecha_creacion,
                og.fecha_modificacion,
                og.total_estimado,
                JSON_LENGTH(og.datos_carrito, '$.items') as num_items
            FROM ordenes_guardadas og
            JOIN cliente c ON og.id_cliente = c.id_cliente
            WHERE og.estado = %s AND og.activo = TRUE
        """

        params = [OrderState.GUARDADA.value]

        if not is_admin and username:
            query += " AND og.usuario_creador = %s"
            params.append(username)

        query += " ORDER BY og.fecha_modificacion DESC"

        return self._execute_query(query, tuple(params), fetch_all=True) or []

    def find_by_folio(self, folio: int) -> Optional[Dict[str, Any]]:
        """Get full order data by folio"""
        query = """
            SELECT
                og.*,
                c.nombre_cliente,
                c.id_grupo,
                g.clave_grupo
            FROM ordenes_guardadas og
            JOIN cliente c ON og.id_cliente = c.id_cliente
            JOIN grupo g ON c.id_grupo = g.id_grupo
            WHERE og.folio_numero = %s AND og.activo = TRUE
        """

        result = self._execute_query(query, (folio,), fetch_one=True)

        if result and result.get('datos_carrito'):
            # Parse JSON cart data
            try:
                result['datos_carrito_obj'] = json.loads(result['datos_carrito'])
            except json.JSONDecodeError as e:
                debug_print(f"❌ Error parsing cart JSON for folio {folio}: {e}")
                result['datos_carrito_obj'] = None

        return result

    def create_order(
        self,
        folio: int,
        id_cliente: int,
        usuario: str,
        datos_carrito: Dict[str, Any],
        total: float
    ) -> bool:
        """
        Create a new order

        Returns:
            True if successful, False otherwise
        """
        try:
            carrito_json = json.dumps(datos_carrito, ensure_ascii=False, indent=2)

            data = {
                'folio_numero': folio,
                'id_cliente': id_cliente,
                'usuario_creador': usuario,
                'datos_carrito': carrito_json,
                'total_estimado': total,
                'estado': OrderState.GUARDADA.value
            }

            rows_affected = self.insert(data)
            return rows_affected > 0

        except Exception as e:
            debug_print(f"❌ Error creating order: {e}")
            return False

    def update_order(
        self,
        folio: int,
        datos_carrito: Dict[str, Any],
        total: float
    ) -> bool:
        """Update an existing order"""
        try:
            carrito_json = json.dumps(datos_carrito, ensure_ascii=False, indent=2)

            query = """
                UPDATE ordenes_guardadas
                SET datos_carrito = %s,
                    total_estimado = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE folio_numero = %s
                    AND estado = %s
                    AND activo = TRUE
            """

            params = (carrito_json, total, folio, OrderState.GUARDADA.value)
            rows_affected = self._execute_query(query, params, commit=True)

            return rows_affected > 0

        except Exception as e:
            debug_print(f"❌ Error updating order: {e}")
            return False

    def mark_as_registered(self, folio: int) -> bool:
        """Mark order as registered (sale completed)"""
        query = """
            UPDATE ordenes_guardadas
            SET estado = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE folio_numero = %s
                AND estado = %s
                AND activo = TRUE
        """

        params = (OrderState.REGISTRADA.value, folio, OrderState.GUARDADA.value)
        rows_affected = self._execute_query(query, params, commit=True)

        return rows_affected > 0

    def release_folio(self, folio: int) -> bool:
        """
        Release folio (physical delete order)

        Only deletes orders with estado='guardada'.
        Protection enforced by database trigger 'before_orden_delete'.

        Args:
            folio: Folio number to delete

        Returns:
            True if deleted successfully, False otherwise

        Raises:
            Exception: If trying to delete a registered order (estado='registrada')
        """
        return self.delete(folio, id_column='folio_numero', soft_delete=False) > 0
