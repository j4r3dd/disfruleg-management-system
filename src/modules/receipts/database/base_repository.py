# -*- coding: utf-8 -*-
"""
Base Repository Pattern
Provides common database operations
"""

from typing import List, Dict, Any, Optional, Type
from contextlib import contextmanager
from src.modules.receipts.database.connection_pool import get_connection
from src.config import debug_print


class BaseRepository:
    """Base class for all repositories"""

    def __init__(self):
        self.table_name: Optional[str] = None

    @contextmanager
    def _get_cursor(self):
        """Get a database cursor from the connection pool"""
        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield conn, cursor
            finally:
                cursor.close()

    def _execute_query(
        self,
        query: str,
        params: tuple = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
        commit: bool = False
    ) -> Any:
        """
        Execute a query with automatic connection management

        Args:
            query: SQL query
            params: Query parameters
            fetch_one: Return single row
            fetch_all: Return all rows
            commit: Commit transaction

        Returns:
            Query results or row count
        """
        with self._get_cursor() as (conn, cursor):
            try:
                cursor.execute(query, params or ())

                if commit:
                    conn.commit()
                    return cursor.rowcount

                if fetch_one:
                    return cursor.fetchone()

                if fetch_all:
                    return cursor.fetchall()

                return cursor.rowcount

            except Exception as e:
                if commit:
                    conn.rollback()
                debug_print(f"❌ Database error: {e}")
                raise

    def find_by_id(self, id_value: int, id_column: str = 'id') -> Optional[Dict]:
        """Find a record by ID"""
        if not self.table_name:
            raise NotImplementedError("table_name must be set")

        query = f"SELECT * FROM {self.table_name} WHERE {id_column} = %s"
        return self._execute_query(query, (id_value,), fetch_one=True)

    def find_all(self, where_clause: str = None, params: tuple = None) -> List[Dict]:
        """Find all records matching criteria"""
        if not self.table_name:
            raise NotImplementedError("table_name must be set")

        query = f"SELECT * FROM {self.table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        return self._execute_query(query, params, fetch_all=True) or []

    def insert(self, data: Dict[str, Any]) -> int:
        """Insert a record"""
        if not self.table_name:
            raise NotImplementedError("table_name must be set")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"

        return self._execute_query(query, tuple(data.values()), commit=True)

    def update(self, id_value: int, data: Dict[str, Any], id_column: str = 'id') -> int:
        """Update a record"""
        if not self.table_name:
            raise NotImplementedError("table_name must be set")

        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_column} = %s"

        params = tuple(data.values()) + (id_value,)
        return self._execute_query(query, params, commit=True)

    def delete(self, id_value: int, id_column: str = 'id', soft_delete: bool = True) -> int:
        """Delete a record (soft delete by default)"""
        if not self.table_name:
            raise NotImplementedError("table_name must be set")

        if soft_delete:
            return self.update(id_value, {'activo': False}, id_column)
        else:
            query = f"DELETE FROM {self.table_name} WHERE {id_column} = %s"
            return self._execute_query(query, (id_value,), commit=True)
