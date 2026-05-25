"""
Módulo de Event Bus para comunicación desacoplada entre componentes
Implementa patrón Observer/Publish-Subscribe
"""
from typing import Callable, Dict, List, Any
import threading
from datetime import datetime

class EventBus:
    """
    Bus de eventos centralizado para comunicación entre componentes
    Thread-safe y con soporte para prioridades
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EventBus, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._subscribers: Dict[str, List[tuple]] = {}
            self._event_history: List[Dict] = []
            self._max_history = 100
            self._lock = threading.Lock()
            self._initialized = True
    
    def subscribe(self, event_name: str, callback: Callable, priority: int = 0):
        """
        Suscribe un callback a un evento
        
        Args:
            event_name: Nombre del evento
            callback: Función a llamar cuando ocurra el evento
            priority: Prioridad (mayor = ejecuta primero)
        """
        with self._lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            
            # Agregar con prioridad
            self._subscribers[event_name].append((priority, callback))
            
            # Ordenar por prioridad (mayor primero)
            self._subscribers[event_name].sort(key=lambda x: x[0], reverse=True)
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """
        Desuscribe un callback de un evento
        
        Args:
            event_name: Nombre del evento
            callback: Función a desuscribir
        """
        with self._lock:
            if event_name in self._subscribers:
                self._subscribers[event_name] = [
                    (priority, cb) for priority, cb in self._subscribers[event_name]
                    if cb != callback
                ]
    
    def publish(self, event_name: str, data: Any = None, **kwargs):
        """
        Publica un evento a todos los suscriptores
        
        Args:
            event_name: Nombre del evento
            data: Datos del evento
            **kwargs: Argumentos adicionales para los callbacks
        """
        # Registrar en historial
        self._add_to_history(event_name, data)
        
        with self._lock:
            subscribers = self._subscribers.get(event_name, []).copy()
        
        # Ejecutar callbacks
        for priority, callback in subscribers:
            try:
                callback(data, **kwargs)
            except Exception as e:
                print(f"Error ejecutando callback para evento '{event_name}': {e}")
    
    def publish_async(self, event_name: str, data: Any = None, **kwargs):
        """
        Publica un evento de forma asíncrona
        
        Args:
            event_name: Nombre del evento
            data: Datos del evento
            **kwargs: Argumentos adicionales
        """
        thread = threading.Thread(
            target=self.publish,
            args=(event_name, data),
            kwargs=kwargs,
            daemon=True
        )
        thread.start()
    
    def clear_subscribers(self, event_name: str = None):
        """
        Limpia suscriptores
        
        Args:
            event_name: Nombre del evento (None para limpiar todos)
        """
        with self._lock:
            if event_name:
                self._subscribers[event_name] = []
            else:
                self._subscribers.clear()
    
    def get_subscribers_count(self, event_name: str) -> int:
        """
        Obtiene el número de suscriptores de un evento
        
        Args:
            event_name: Nombre del evento
            
        Returns:
            Número de suscriptores
        """
        with self._lock:
            return len(self._subscribers.get(event_name, []))
    
    def _add_to_history(self, event_name: str, data: Any):
        """Agrega evento al historial"""
        event_record = {
            'event': event_name,
            'data': data,
            'timestamp': datetime.now()
        }
        
        self._event_history.append(event_record)
        
        # Mantener solo los últimos N eventos
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
    
    def get_history(self, event_name: str = None, limit: int = None) -> List[Dict]:
        """
        Obtiene el historial de eventos
        
        Args:
            event_name: Filtrar por nombre de evento (None para todos)
            limit: Límite de eventos a retornar
            
        Returns:
            Lista de eventos
        """
        history = self._event_history
        
        if event_name:
            history = [e for e in history if e['event'] == event_name]
        
        if limit:
            history = history[-limit:]
        
        return history


# Instancia global del EventBus
_event_bus = EventBus()

# Funciones de conveniencia
def subscribe(event_name: str, callback: Callable, priority: int = 0):
    """Suscribe un callback a un evento"""
    _event_bus.subscribe(event_name, callback, priority)

def unsubscribe(event_name: str, callback: Callable):
    """Desuscribe un callback de un evento"""
    _event_bus.unsubscribe(event_name, callback)

def publish(event_name: str, data: Any = None, **kwargs):
    """Publica un evento"""
    _event_bus.publish(event_name, data, **kwargs)

def publish_async(event_name: str, data: Any = None, **kwargs):
    """Publica un evento de forma asíncrona"""
    _event_bus.publish_async(event_name, data, **kwargs)

def get_event_bus() -> EventBus:
    """Obtiene la instancia del EventBus"""
    return _event_bus


# Eventos predefinidos comunes en la aplicación
class Events:
    """Nombres de eventos comunes"""
    
    # Eventos de aplicación
    APP_STARTED = "app_started"
    APP_CLOSED = "app_closed"
    
    # Eventos de autenticación
    USER_LOGGED_IN = "user_logged_in"
    USER_LOGGED_OUT = "user_logged_out"
    SESSION_EXPIRED = "session_expired"
    
    # Eventos de base de datos
    DB_CONNECTED = "db_connected"
    DB_DISCONNECTED = "db_disconnected"
    DB_ERROR = "db_error"
    
    # Eventos de órdenes
    ORDER_CREATED = "order_created"
    ORDER_UPDATED = "order_updated"
    ORDER_DELETED = "order_deleted"
    ORDER_COMPLETED = "order_completed"
    
    # Eventos de productos
    PRODUCT_ADDED = "product_added"
    PRODUCT_UPDATED = "product_updated"
    PRODUCT_DELETED = "product_deleted"
    INVENTORY_UPDATED = "inventory_updated"
    
    # Eventos de clientes
    CLIENT_CREATED = "client_created"
    CLIENT_UPDATED = "client_updated"
    CLIENT_DELETED = "client_deleted"
    
    # Eventos de recibos
    RECEIPT_GENERATED = "receipt_generated"
    RECEIPT_PRINTED = "receipt_printed"
    
    # Eventos de UI
    THEME_CHANGED = "theme_changed"
    WINDOW_OPENED = "window_opened"
    WINDOW_CLOSED = "window_closed"
    
    # Eventos de carrito
    CART_ITEM_ADDED = "cart_item_added"
    CART_ITEM_REMOVED = "cart_item_removed"
    CART_CLEARED = "cart_cleared"
    CART_UPDATED = "cart_updated"


# Decorador para publicar eventos automáticamente
def emit_event(event_name: str, data_extractor: Callable = None):
    """
    Decorador que publica un evento después de ejecutar una función
    
    Args:
        event_name: Nombre del evento a publicar
        data_extractor: Función que extrae datos del resultado (opcional)
    """
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            resultado = func(*args, **kwargs)
            
            # Extraer datos si se provee extractor
            data = data_extractor(resultado) if data_extractor else resultado
            
            # Publicar evento
            publish(event_name, data)
            
            return resultado
        
        return wrapper
    return decorator


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo básico
    def mi_callback(data):
        print(f"Evento recibido: {data}")
    
    subscribe(Events.ORDER_CREATED, mi_callback)
    publish(Events.ORDER_CREATED, {"orden_id": 123, "cliente": "Juan"})
    
    # Ejemplo con prioridad
    def callback_alta_prioridad(data):
        print(f"[ALTA PRIORIDAD] {data}")
    
    def callback_baja_prioridad(data):
        print(f"[BAJA PRIORIDAD] {data}")
    
    subscribe("test_event", callback_alta_prioridad, priority=10)
    subscribe("test_event", callback_baja_prioridad, priority=1)
    publish("test_event", "Hola mundo")
    
    # Ver historial
    print("\nHistorial de eventos:")
    for event in get_event_bus().get_history(limit=5):
        print(f"  {event['timestamp']} - {event['event']}: {event['data']}")