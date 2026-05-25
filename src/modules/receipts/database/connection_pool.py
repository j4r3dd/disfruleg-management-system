# -*- coding: utf-8 -*-
"""
Database Connection Pool Manager
UPDATED: Now uses the main application's connection pool instead of creating its own

This module now acts as a wrapper around the main connection pool to maintain
compatibility with existing receipts module code.
"""

from contextlib import contextmanager
from src.database.conexion import get_pooled_connection
from src.config import debug_print


@contextmanager
def get_connection():
    """
    Get a connection from the MAIN application pool (not a separate pool)

    Usage:
        from src.modules.receipts.database.connection_pool import get_connection

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")

    This now uses the main application's connection pool (src.database.conexion)
    instead of creating a separate pool for the receipts module.
    """
    with get_pooled_connection() as conn:
        yield conn


# Legacy compatibility - these are no longer used but kept for backwards compatibility
class ConnectionPool:
    """
    DEPRECATED: This class is no longer used.
    The receipts module now uses the main application's connection pool.
    """
    pass


def get_pool():
    """
    DEPRECATED: Returns None.
    Use get_connection() instead which uses the main pool.
    """
    return None
