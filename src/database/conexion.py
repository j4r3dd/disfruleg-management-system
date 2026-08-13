from .cloud_config import create_connection, DB_USER, DB_PASSWORD, DB_NAME
import pymysql.cursors
import logging
from pathlib import Path
from src.utils.resource_path import get_writable_path
from queue import Queue, Empty, Full
import threading
from contextlib import contextmanager

# Configure logging
log_file = get_writable_path('logs/database_connection.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

db_available = False
_silent_mode = True  # [OK] Modo silencioso activado
last_connection_error = None  # Store last error for user display

# Connection Pool Configuration
POOL_SIZE = 6  # Maximum number of connections per process
POOL_TIMEOUT = 15.00  # Timeout in seconds when waiting for available connection
_connection_pool = None
_pool_lock = threading.Lock()

# Module initialization guard - only run once per process
_module_initialized = False


class ConnectionPool:
    """Thread-safe connection pool for Cloud SQL"""

    _instance_count = 0  # Track how many instances are created (should be 1)

    def __init__(self, pool_size: int = POOL_SIZE):
        """
        Initialize connection pool

        Args:
            pool_size: Maximum number of connections to maintain
        """
        # Track instance creation for debugging
        ConnectionPool._instance_count += 1
        instance_num = ConnectionPool._instance_count

        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self._all_connections = []
        self._created_count = 0
        self._lock = threading.Lock()
        self._instance_number = instance_num

        # Log with instance number to detect duplicates
        logger.info(f"🔄 Initializing connection pool #{instance_num} (size={pool_size})")

        if instance_num > 1:
            logger.warning(f"⚠️ WARNING: Multiple pool instances detected! (This is instance #{instance_num})")
            logger.warning(f"⚠️ This should NOT happen - pool should be singleton!")
            import traceback
            logger.warning("⚠️ Pool creation traceback:")
            for line in traceback.format_stack():
                logger.warning(line.strip())

        # Pre-create initial connections
        for i in range(pool_size):
            conn = self._create_new_connection()
            if conn:
                self.pool.put(conn)
                self._all_connections.append(conn)
                self._created_count += 1
                # Only log first 3 connections to reduce noise
                if i < 3:
                    logger.info(f"  ✓ Pre-created connection {i+1}/{pool_size}")

        # Single summary message
        logger.info(f"✅ Connection pool #{instance_num} ready ({self._created_count} connections)")

    def _create_new_connection(self):
        """Create a new database connection"""
        try:
            return create_connection()
        except Exception as e:
            logger.error(f"❌ Failed to create connection: {e}")
            return None

    def get_connection(self, timeout: float = POOL_TIMEOUT):
        """
        Get a connection from the pool

        Args:
            timeout: Maximum time to wait for available connection

        Returns:
            Database connection

        Raises:
            Empty: If no connection available within timeout
        """
        try:
            conn = self.pool.get(timeout=timeout)

            # Verify connection is still alive
            if not self._is_connection_alive(conn):
                logger.warning("⚠️ Retrieved dead connection, creating new one")
                conn = self._create_new_connection()
                if not conn:
                    raise Exception("Failed to create replacement connection")

            return conn

        except Empty:
            logger.error(f"❌ Connection pool exhausted (timeout={timeout}s)")
            logger.error(f"   Pool size: {self.pool_size}, Active: {self._created_count - self.pool.qsize()}")
            raise Exception(
                f"Connection pool exhausted. All {self.pool_size} connections are in use. "
                "Consider increasing POOL_SIZE or closing unused connections."
            )

    def return_connection(self, conn):
        """
        Return a connection to the pool

        Args:
            conn: Database connection to return
        """
        if conn is None:
            return

        try:
            # Verify connection is still alive before returning to pool
            if self._is_connection_alive(conn):
                # Cerrar la transacción abierta antes de reciclar la conexión.
                # InnoDB usa REPEATABLE READ: sin esto la conexión conserva el
                # snapshot de su primera lectura y el siguiente uso vería datos
                # obsoletos (p. ej. un bloqueo de usuario ya levantado).
                try:
                    conn.rollback()
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo hacer rollback al devolver la conexión: {e}")

                self.pool.put_nowait(conn)
                logger.debug(f"✓ Connection returned to pool (available: {self.pool.qsize()})")
            else:
                logger.warning("⚠️ Discarding dead connection from pool")
                # Remove from tracking and create replacement
                if conn in self._all_connections:
                    self._all_connections.remove(conn)
                    self._created_count -= 1
                try:
                    conn.close()
                except:
                    pass
                # Create replacement connection
                new_conn = self._create_new_connection()
                if new_conn:
                    self.pool.put_nowait(new_conn)
                    self._all_connections.append(new_conn)
                    self._created_count += 1
        except Full:
            # Pool is full - this means connection was already returned or is duplicate
            logger.error(f"❌ CRITICAL: Attempted to return connection but pool is full!")
            logger.error(f"   Pool size: {self.pool_size}, Queue size: {self.pool.qsize()}")
            logger.error(f"   This indicates a connection was returned twice or pool is corrupted")
            # This is a serious error - don't silently discard the connection
            raise Exception("Connection pool is full - cannot return connection. This indicates a double-return bug.")

    def _is_connection_alive(self, conn) -> bool:
        """Check if connection is alive"""
        try:
            if conn is None:
                return False
            conn.ping(reconnect=False)
            return True
        except:
            return False

    def close_all(self):
        """Close all connections in the pool"""
        logger.info("🔄 Closing all pooled connections...")

        # Close all connections in queue
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except:
                pass

        # Close any remaining tracked connections
        for conn in self._all_connections:
            try:
                conn.close()
            except:
                pass

        self._all_connections.clear()
        self._created_count = 0
        logger.info("✅ All connections closed")


def _get_pool() -> ConnectionPool:
    """Get or create the connection pool singleton"""
    global _connection_pool

    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                logger.info("📊 Creating new connection pool (first time)")
                _connection_pool = ConnectionPool(POOL_SIZE)
    else:
        # Pool already exists, just return it
        logger.debug(f"♻️ Reusing existing connection pool #{_connection_pool._instance_number}")

    return _connection_pool


def verify_db_availability():
    global db_available, last_connection_error
    try:
        logger.info("Verificando disponibilidad de base de datos...")
        conn = conectar()
        if conn:
            db_available = True
            return_connection(conn)  # Return to pool instead of closing
            logger.info("✅ Base de datos disponible")
            last_connection_error = None
        else:
            logger.error("❌ No se pudo conectar a la base de datos")
        return db_available
    except Exception as e:
        logger.error(f"❌ Error verificando base de datos: {e}", exc_info=True)
        last_connection_error = str(e)
        return False

def conectar():
    """
    Get a connection from the pool.

    IMPORTANT: Connections obtained via this function are NOT automatically returned
    to the pool. Use the get_pooled_connection() context manager for automatic
    connection management, or manually call return_connection() when done.

    Returns:
        Database connection from pool

    Raises:
        Exception: If pool is exhausted or connection fails
    """
    global last_connection_error
    try:
        pool = _get_pool()
        conn = pool.get_connection()

        if conn:
            last_connection_error = None
            return conn
        else:
            raise Exception("Failed to get connection from pool")

    except Exception as e:
        # [ERROR] Log detailed error information
        error_msg = f"Error de conexion: {type(e).__name__}: {str(e)}"
        logger.error(f"[ERROR] {error_msg}", exc_info=True)
        last_connection_error = error_msg

        # Additional debugging info
        import sys
        logger.error(f"Python version: {sys.version}")
        logger.error(f"Frozen: {getattr(sys, 'frozen', False)}")
        if hasattr(sys, '_MEIPASS'):
            logger.error(f"MEIPASS: {sys._MEIPASS}")

        import os
        creds_env = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'NOT SET')
        logger.error(f"GOOGLE_APPLICATION_CREDENTIALS: {creds_env}")

        if creds_env != 'NOT SET':
            from pathlib import Path
            creds_path = Path(creds_env)
            logger.error(f"Credentials file exists: {creds_path.exists()}")
            if creds_path.exists():
                logger.error(f"Credentials file size: {creds_path.stat().st_size} bytes")

        # Re-raise the exception instead of returning None
        # This allows calling code to handle pool exhaustion and other errors
        raise


def return_connection(conn):
    """
    Return a connection to the pool.

    Args:
        conn: Database connection to return
    """
    if conn is None:
        return

    pool = _get_pool()
    pool.return_connection(conn)


@contextmanager
def get_pooled_connection():
    """
    Context manager for automatic connection management.

    Usage:
        with get_pooled_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
            # Connection automatically returned to pool when done

    Yields:
        Database connection from pool
    """
    conn = None
    try:
        conn = conectar()
        yield conn
    finally:
        if conn:
            return_connection(conn)


def _initialize_module():
    """Initialize module only once per process"""
    global _module_initialized, db_available
    
    if _module_initialized:
        logger.debug("⏭️ Module already initialized, skipping verification")
        return
    
    logger.info("🔧 Initializing conexion module for the first time")
    _module_initialized = True
    
    # Only verify database availability on first import
    if _connection_pool is None:
        verify_db_availability()
    else:
        logger.debug(f"♻️ Database connection pool already initialized (instance #{_connection_pool._instance_number})")
        db_available = True


def is_connection_alive(conn):
    try:
        if conn is None:
            return False
        conn.ping(reconnect=False)
        return True
    except Exception as e:
        logger.debug(f"Connection ping failed: {e}")
        return False

def get_last_error():
    """Get the last connection error message for display to user"""
    return last_connection_error


def get_pool_stats():
    """
    Get connection pool statistics for monitoring.

    Returns:
        dict: Pool statistics including size, available, and active connections
    """
    try:
        pool = _get_pool()
        available = pool.pool.qsize()
        active = pool._created_count - available

        return {
            'pool_size': pool.pool_size,
            'total_created': pool._created_count,
            'available': available,
            'active': active,
            'utilization_percent': round((active / pool.pool_size) * 100, 1) if pool.pool_size > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error getting pool stats: {e}")
        return {
            'pool_size': 0,
            'total_created': 0,
            'available': 0,
            'active': 0,
            'utilization_percent': 0
        }


def close_all_connections():
    """
    Close all connections in the pool.
    Call this when shutting down the application.
    """
    global _connection_pool

    if _connection_pool is not None:
        _connection_pool.close_all()
        _connection_pool = None


def print_pool_stats():
    """Print connection pool statistics to logger"""
    stats = get_pool_stats()
    logger.info("=" * 50)
    logger.info("CONNECTION POOL STATISTICS")
    logger.info("=" * 50)
    logger.info(f"Pool Size:       {stats['pool_size']}")
    logger.info(f"Total Created:   {stats['total_created']}")
    logger.info(f"Available:       {stats['available']}")
    logger.info(f"Active:          {stats['active']}")
    logger.info(f"Utilization:     {stats['utilization_percent']}%")
    logger.info("=" * 50)


# Initialize module - this will only run once per process
_initialize_module()