# -*- coding: utf-8 -*-
"""
Client Repository
Handles client and group database operations
"""

from typing import List, Dict, Any, Optional
from src.modules.receipts.database.base_repository import BaseRepository
from src.modules.receipts.constants import DatabaseTables


class ClientRepository(BaseRepository):
    """Repository for cliente table"""

    def __init__(self):
        super().__init__()
        self.table_name = DatabaseTables.CLIENTE

    def get_all_groups(self) -> List[Dict[str, Any]]:
        """Get all client groups"""
        query = "SELECT id_grupo, clave_grupo FROM grupo ORDER BY clave_grupo"
        return self._execute_query(query, fetch_all=True) or []

    def get_clients_by_group(self, id_grupo: int) -> List[Dict[str, Any]]:
        """Get all clients in a group"""
        query = """
            SELECT id_cliente, nombre_cliente, id_grupo
            FROM cliente
            WHERE id_grupo = %s AND activo = TRUE
            ORDER BY nombre_cliente
        """
        return self._execute_query(query, (id_grupo,), fetch_all=True) or []

    def get_client_by_id(self, id_cliente: int) -> Optional[Dict[str, Any]]:
        """Get full client information by ID"""
        query = """
            SELECT
                c.id_cliente,
                c.nombre_cliente,
                c.id_grupo,
                g.clave_grupo
            FROM cliente c
            LEFT JOIN grupo g ON c.id_grupo = g.id_grupo
            WHERE c.id_cliente = %s
        """
        return self._execute_query(query, (id_cliente,), fetch_one=True)
