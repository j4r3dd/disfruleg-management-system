"""
Módulo de gestión de locks para operaciones concurrentes
Previene condiciones de carrera y conflictos en bases de datos
"""
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from contextlib import contextmanager

class LockManager:
    """
    Gestor de locks para operaciones concurrentes
    Thread-safe y con soporte para timeouts
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LockManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._locks: Dict[str, threading.Lock] = {}
            self._lock_info: Dict[str, Dict[str, Any]] = {}
            self._main_lock = threading.Lock()
            self._initialized = True
    
    def acquire(self, resource_name: str, timeout: Optional[float] = None, 
                blocking: bool = True) -> bool:
        """
        Adquiere un lock para un recurso
        
        Args:
            resource_name: Nombre del recurso a bloquear
            timeout: Tiempo máximo de espera en segundos
            blocking: Si debe bloquear hasta obtener el lock
            
        Returns:
            True si se adquirió el lock, False si no
        """
        with self._main_lock:
            if resource_name not in self._locks:
                self._locks[resource_name] = threading.Lock()
                self._lock_info[resource_name] = {
                    'acquired_at': None,
                    'acquired_by': None,
                    'acquisition_count': 0
                }
        
        # Intentar adquirir el lock
        acquired = self._locks[resource_name].acquire(blocking=blocking, timeout=timeout or -1)
        
        if acquired:
            with self._main_lock:
                thread_id = threading.current_thread().ident
                self._lock_info[resource_name]['acquired_at'] = datetime.now()
                self._lock_info[resource_name]['acquired_by'] = thread_id
                self._lock_info[resource_name]['acquisition_count'] += 1
        
        return acquired
    
    def release(self, resource_name: str):
        """
        Libera un lock
        
        Args:
            resource_name: Nombre del recurso a liberar
        """
        if resource_name in self._locks:
            try:
                self._locks[resource_name].release()
                with self._main_lock:
                    self._lock_info[resource_name]['acquired_at'] = None
                    self._lock_info[resource_name]['acquired_by'] = None
            except RuntimeError:
                # El lock no estaba adquirido
                pass
    
    def is_locked(self, resource_name: str) -> bool:
        """
        Verifica si un recurso está bloqueado
        
        Args:
            resource_name: Nombre del recurso
            
        Returns:
            True si está bloqueado
        """
        if resource_name not in self._locks:
            return False
        
        return self._locks[resource_name].locked()
    
    def get_lock_info(self, resource_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información sobre un lock
        
        Args:
            resource_name: Nombre del recurso
            
        Returns:
            Diccionario con información del lock o None
        """
        with self._main_lock:
            return self._lock_info.get(resource_name, None)
    
    def get_all_locks_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene información de todos los locks
        
        Returns:
            Diccionario con información de todos los locks
        """
        with self._main_lock:
            return {
                name: {
                    'locked': self._locks[name].locked(),
                    **info
                }
                for name, info in self._lock_info.items()
            }
    
    def clear_stale_locks(self, max_age_seconds: int = 300):
        """
        Limpia locks que han estado adquiridos por demasiado tiempo
        
        Args:
            max_age_seconds: Edad máxima en segundos
        """
        now = datetime.now()
        max_age = timedelta(seconds=max_age_seconds)
        
        with self._main_lock:
            for resource_name, info in self._lock_info.items():
                if info['acquired_at']:
                    age = now - info['acquired_at']
                    if age > max_age:
                        print(f"[LockManager] Limpiando lock antiguo: {resource_name} "
                              f"(edad: {age.total_seconds():.1f}s)")
                        try:
                            self._locks[resource_name].release()
                            info['acquired_at'] = None
                            info['acquired_by'] = None
                        except RuntimeError:
                            pass
    
    @contextmanager
    def lock(self, resource_name: str, timeout: Optional[float] = None):
        """
        Context manager para uso con 'with'
        
        Args:
            resource_name: Nombre del recurso
            timeout: Timeout en segundos
            
        Example:
            with lock_manager.lock('mi_recurso'):
                # código protegido
        """
        acquired = self.acquire(resource_name, timeout=timeout)
        
        try:
            if not acquired:
                raise TimeoutError(f"No se pudo adquirir lock para '{resource_name}'")
            yield
        finally:
            if acquired:
                self.release(resource_name)


# Instancia global
_lock_manager = LockManager()

# Funciones de conveniencia
def acquire_lock(resource_name: str, timeout: Optional[float] = None, 
                 blocking: bool = True) -> bool:
    """Adquiere un lock"""
    return _lock_manager.acquire(resource_name, timeout, blocking)

def release_lock(resource_name: str):
    """Libera un lock"""
    _lock_manager.release(resource_name)

def is_locked(resource_name: str) -> bool:
    """Verifica si un recurso está bloqueado"""
    return _lock_manager.is_locked(resource_name)

@contextmanager
def resource_lock(resource_name: str, timeout: Optional[float] = None):
    """Context manager para locks"""
    with _lock_manager.lock(resource_name, timeout):
        yield

def get_lock_manager() -> LockManager:
    """Obtiene la instancia del LockManager"""
    return _lock_manager


# Decorador para proteger funciones con locks
def synchronized(lock_name: str = None, timeout: Optional[float] = None):
    """
    Decorador que sincroniza el acceso a una función
    
    Args:
        lock_name: Nombre del lock (usa nombre de función si es None)
        timeout: Timeout en segundos
    """
    import functools
    
    def decorator(func):
        resource_name = lock_name or f"func_{func.__name__}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with resource_lock(resource_name, timeout):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


class DatabaseLockManager:
    """
    Gestor de locks específico para operaciones de base de datos
    """
    
    def __init__(self):
        self.lock_manager = _lock_manager
    
    def lock_table(self, table_name: str, timeout: float = 30.0) -> bool:
        """
        Bloquea una tabla para operaciones exclusivas
        
        Args:
            table_name: Nombre de la tabla
            timeout: Timeout en segundos
            
        Returns:
            True si se adquirió el lock
        """
        resource_name = f"db_table_{table_name}"
        return self.lock_manager.acquire(resource_name, timeout=timeout)
    
    def unlock_table(self, table_name: str):
        """
        Desbloquea una tabla
        
        Args:
            table_name: Nombre de la tabla
        """
        resource_name = f"db_table_{table_name}"
        self.lock_manager.release(resource_name)
    
    @contextmanager
    def table_lock(self, table_name: str, timeout: float = 30.0):
        """
        Context manager para bloquear tablas
        
        Example:
            with db_lock_manager.table_lock('productos'):
                # operaciones en tabla productos
        """
        acquired = self.lock_table(table_name, timeout)
        
        try:
            if not acquired:
                raise TimeoutError(f"No se pudo bloquear tabla '{table_name}'")
            yield
        finally:
            if acquired:
                self.unlock_table(table_name)
    
    def lock_record(self, table_name: str, record_id: Any, timeout: float = 10.0) -> bool:
        """
        Bloquea un registro específico
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
            timeout: Timeout en segundos
            
        Returns:
            True si se adquirió el lock
        """
        resource_name = f"db_record_{table_name}_{record_id}"
        return self.lock_manager.acquire(resource_name, timeout=timeout)
    
    def unlock_record(self, table_name: str, record_id: Any):
        """
        Desbloquea un registro
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
        """
        resource_name = f"db_record_{table_name}_{record_id}"
        self.lock_manager.release(resource_name)
    
    @contextmanager
    def record_lock(self, table_name: str, record_id: Any, timeout: float = 10.0):
        """
        Context manager para bloquear registros
        
        Example:
            with db_lock_manager.record_lock('ordenes', orden_id):
                # operaciones en orden específica
        """
        acquired = self.lock_record(table_name, record_id, timeout)
        
        try:
            if not acquired:
                raise TimeoutError(f"No se pudo bloquear registro {record_id} en '{table_name}'")
            yield
        finally:
            if acquired:
                self.unlock_record(table_name, record_id)


# Instancia global para operaciones de DB
db_lock_manager = DatabaseLockManager()


# Ejemplo de uso
if __name__ == "__main__":
    # Uso básico
    print("Ejemplo 1: Uso básico")
    acquire_lock("recurso_test")
    print(f"Recurso bloqueado: {is_locked('recurso_test')}")
    release_lock("recurso_test")
    print(f"Recurso bloqueado: {is_locked('recurso_test')}")
    
    # Uso con context manager
    print("\nEjemplo 2: Context manager")
    with resource_lock("recurso_test2"):
        print(f"Dentro del bloque: {is_locked('recurso_test2')}")
    print(f"Fuera del bloque: {is_locked('recurso_test2')}")
    
    # Uso con decorador
    print("\nEjemplo 3: Decorador")
    @synchronized()
    def funcion_sincronizada():
        print("Ejecutando función sincronizada")
        time.sleep(0.5)
    
    import threading
    threads = [threading.Thread(target=funcion_sincronizada) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Uso con DB locks
    print("\nEjemplo 4: DB locks")
    with db_lock_manager.table_lock("productos"):
        print("Tabla 'productos' bloqueada")
    
    print("\nInfo de todos los locks:")
    for name, info in get_lock_manager().get_all_locks_info().items():
        print(f"  {name}: {info}")