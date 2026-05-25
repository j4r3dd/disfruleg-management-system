"""
Paquete de utilidades para BodegaDisfruleg
Contiene módulos de normalización, logging, event bus y locks
"""

# Importar módulos principales
try:
    from .normalizacion import (
        Normalizador,
        normalizar_texto,
        normalizar_nombre,
        normalizar_telefono,
        normalizar_precio,
        normalizar_unidad
    )
    NORMALIZACION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ No se pudo importar módulo de normalización: {e}")
    NORMALIZACION_AVAILABLE = False

try:
    from .logger import (
        AppLogger,
        ModuleLogger,
        get_logger,
        log_debug,
        log_info,
        log_warning,
        log_error,
        log_critical,
        log_exception,
        log_function_call
    )
    LOGGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ No se pudo importar módulo de logger: {e}")
    LOGGER_AVAILABLE = False

try:
    from .event_bus import (
        EventBus,
        Events,
        get_event_bus,
        subscribe,
        unsubscribe,
        publish,
        publish_async,
        emit_event
    )
    EVENTBUS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ No se pudo importar módulo de event bus: {e}")
    EVENTBUS_AVAILABLE = False

try:
    from .locks import (
        LockManager,
        DatabaseLockManager,
        get_lock_manager,
        acquire_lock,
        release_lock,
        is_locked,
        resource_lock,
        synchronized,
        db_lock_manager
    )
    LOCKS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ No se pudo importar módulo de locks: {e}")
    LOCKS_AVAILABLE = False

# Versión del paquete
__version__ = "1.0.0"

# Exportar todo
__all__ = [
    # Normalización
    'Normalizador',
    'normalizar_texto',
    'normalizar_nombre',
    'normalizar_telefono',
    'normalizar_precio',
    'normalizar_unidad',
    
    # Logger
    'AppLogger',
    'ModuleLogger',
    'get_logger',
    'log_debug',
    'log_info',
    'log_warning',
    'log_error',
    'log_critical',
    'log_exception',
    'log_function_call',
    
    # Event Bus
    'EventBus',
    'Events',
    'get_event_bus',
    'subscribe',
    'unsubscribe',
    'publish',
    'publish_async',
    'emit_event',
    
    # Locks
    'LockManager',
    'DatabaseLockManager',
    'get_lock_manager',
    'acquire_lock',
    'release_lock',
    'is_locked',
    'resource_lock',
    'synchronized',
    'db_lock_manager',
    
    # Flags de disponibilidad
    'NORMALIZACION_AVAILABLE',
    'LOGGER_AVAILABLE',
    'EVENTBUS_AVAILABLE',
    'LOCKS_AVAILABLE',
]


def print_module_status():
    """Imprime el estado de disponibilidad de los módulos"""
    print("\n" + "="*50)
    print("Estado de módulos de utilidades:")
    print("="*50)
    print(f"✓ Normalización: {'Disponible' if NORMALIZACION_AVAILABLE else 'No disponible'}")
    print(f"✓ Logger: {'Disponible' if LOGGER_AVAILABLE else 'No disponible'}")
    print(f"✓ Event Bus: {'Disponible' if EVENTBUS_AVAILABLE else 'No disponible'}")
    print(f"✓ Locks: {'Disponible' if LOCKS_AVAILABLE else 'No disponible'}")
    print("="*50 + "\n")


# Funciones de fallback si los módulos no están disponibles
if not NORMALIZACION_AVAILABLE:
    def normalizar_texto(texto: str) -> str:
        """Fallback básico para normalización de texto"""
        return texto.lower().strip() if texto else ""
    
    def normalizar_nombre(nombre: str) -> str:
        """Fallback básico para normalización de nombre"""
        return nombre.strip() if nombre else ""
    
    def normalizar_telefono(telefono: str) -> str:
        """Fallback básico para normalización de teléfono"""
        import re
        return re.sub(r'\D', '', str(telefono)) if telefono else ""
    
    def normalizar_precio(precio) -> float:
        """Fallback básico para normalización de precio"""
        try:
            if isinstance(precio, str):
                precio = precio.replace('$', '').replace(',', '').strip()
            return float(precio)
        except:
            return 0.0
    
    def normalizar_unidad(unidad: str) -> str:
        """Fallback básico para normalización de unidad"""
        return unidad.upper().strip() if unidad else "UNIDAD"

if not LOGGER_AVAILABLE:
    class ModuleLogger:
        """Fallback logger que solo imprime a consola"""
        def __init__(self, module_name: str):
            self.module_name = module_name
        
        def debug(self, msg, **kwargs):
            print(f"[DEBUG][{self.module_name}] {msg}")
        
        def info(self, msg, **kwargs):
            print(f"[INFO][{self.module_name}] {msg}")
        
        def warning(self, msg, **kwargs):
            print(f"[WARNING][{self.module_name}] {msg}")
        
        def error(self, msg, **kwargs):
            print(f"[ERROR][{self.module_name}] {msg}")
        
        def critical(self, msg, **kwargs):
            print(f"[CRITICAL][{self.module_name}] {msg}")
        
        def exception(self, msg, **kwargs):
            print(f"[EXCEPTION][{self.module_name}] {msg}")
    
    def log_info(msg, **kwargs):
        print(f"[INFO] {msg}")
    
    def log_error(msg, **kwargs):
        print(f"[ERROR] {msg}")
    
    def log_warning(msg, **kwargs):
        print(f"[WARNING] {msg}")

if not EVENTBUS_AVAILABLE:
    def subscribe(event_name: str, callback, priority: int = 0):
        """Fallback: no hace nada"""
        pass
    
    def publish(event_name: str, data=None, **kwargs):
        """Fallback: no hace nada"""
        pass
    
    def publish_async(event_name: str, data=None, **kwargs):
        """Fallback: no hace nada"""
        pass

if not LOCKS_AVAILABLE:
    import threading
    from contextlib import contextmanager
    
    _fallback_locks = {}
    
    def acquire_lock(resource_name: str, timeout=None, blocking=True) -> bool:
        """Fallback básico con threading.Lock"""
        if resource_name not in _fallback_locks:
            _fallback_locks[resource_name] = threading.Lock()
        return _fallback_locks[resource_name].acquire(blocking=blocking, timeout=timeout or -1)
    
    def release_lock(resource_name: str):
        """Fallback básico con threading.Lock"""
        if resource_name in _fallback_locks:
            try:
                _fallback_locks[resource_name].release()
            except:
                pass
    
    def is_locked(resource_name: str) -> bool:
        """Fallback básico con threading.Lock"""
        if resource_name in _fallback_locks:
            return _fallback_locks[resource_name].locked()
        return False
    
    @contextmanager
    def resource_lock(resource_name: str, timeout=None):
        """Fallback básico con threading.Lock"""
        acquired = acquire_lock(resource_name, timeout)
        try:
            yield
        finally:
            if acquired:
                release_lock(resource_name)