from src.database.conexion import conectar, return_connection
from typing import Optional
from src.auth.auth_manager import AuthManager
from .cloud_config import get_db_config

class DatabaseManager:
    """
    Gestor centralizado de conexiones a base de datos
    Mantiene compatibilidad con el sistema existente
    Versión v2.0 con soporte de transacciones para reciclaje de IDs
    """
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.current_user = None
        self.current_connection = None
    
    def authenticate_and_connect(self, username: str, password: str) -> dict:
        """
        Autenticar usuario y establecer conexión
        
        Returns:
            dict: {'success': bool, 'message': str, 'user_data': dict}
        """
        try:
            # Autenticar usuario
            auth_result = self.auth_manager.authenticate(username, password)
            
            if auth_result['success']:
                # Crear conexión para el usuario autenticado
                self.current_connection = self.auth_manager.create_user_connection(username, password)
                self.current_user = auth_result['user_data']
                
                return {
                    'success': True,
                    'message': 'Conexión establecida exitosamente',
                    'user_data': self.current_user
                }
            else:
                return auth_result
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error de conexión: {str(e)}'
            }
    
    def get_connection(self):
        """
        Obtener conexión actual del usuario autenticado
        """
        if not self.current_connection:
            raise Exception("No hay usuario autenticado. Debe hacer login primero.")
        
        # Verificar que la conexión sigue activa
        try:
            self.current_connection.ping(reconnect=True)
            return self.current_connection
        except Exception:
            # Reconectar si es necesario
            if self.current_user:
                raise Exception("Conexión perdida. Por favor, inicie sesión nuevamente.")
            else:
                raise Exception("No hay usuario autenticado.")
    
    def get_cursor(self, dictionary: bool = True):
        """
        Obtener cursor de la conexión actual
        """
        conn = self.get_connection()
        return conn.cursor(dictionary=dictionary)
    
    def close_connection(self):
        """
        Return connection to pool and clear session
        """
        if self.current_connection:
            try:
                # Return connection to pool instead of closing
                return_connection(self.current_connection)
            except:
                pass
            finally:
                self.current_connection = None
                self.current_user = None
    
    def get_current_user(self) -> Optional[dict]:
        """
        Obtener información del usuario actual
        """
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """
        Verificar si hay un usuario autenticado
        """
        return self.current_user is not None and self.current_connection is not None
    
    def change_password(self, old_password: str, new_password: str) -> dict:
        """
        Cambiar contraseña del usuario actual
        """
        if not self.current_user:
            return {
                'success': False,
                'message': 'No hay usuario autenticado'
            }
        
        return self.auth_manager.change_password(
            self.current_user['username'], 
            old_password, 
            new_password
        )
    
    def execute_transaction(self, operations: list) -> dict:
        """
        Ejecutar múltiples operaciones en una transacción
        NUEVO: Para operaciones críticas como reciclaje de IDs
        
        Args:
            operations: Lista de tuplas (query, params)
            
        Returns:
            dict: {'success': bool, 'message': str, 'affected_rows': int}
            
        Ejemplo:
            operations = [
                ("UPDATE dispositivos_autorizados SET estado='BLOQUEADO' WHERE id=%s", (dev_id,)),
                ("INSERT INTO dispositivos_eventos (...) VALUES (...)", (valores,)),
            ]
            result = db_manager.execute_transaction(operations)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            total_affected = 0
            
            # Iniciar transacción explícita
            cursor.execute("START TRANSACTION")
            
            try:
                # Ejecutar todas las operaciones
                for query, params in operations:
                    cursor.execute(query, params)
                    total_affected += cursor.rowcount
                
                # Commit si todas son exitosas
                conn.commit()
                
                return {
                    'success': True,
                    'message': 'Transacción completada exitosamente',
                    'affected_rows': total_affected
                }
                
            except Exception as e:
                # Rollback en caso de error
                conn.rollback()
                raise e
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error en transacción: {str(e)}',
                'affected_rows': 0
            }

# Instancia global para uso en toda la aplicación
db_manager = DatabaseManager()

# Funciones de compatibilidad con el sistema existente
def conectar():
    """
    Función de compatibilidad con conexion.py
    DEPRECADA: Usar db_manager.get_connection() en su lugar
    """
    if db_manager.is_authenticated():
        return db_manager.get_connection()
    else:
        # Para compatibilidad temporal, usar la función conectar de conexion.py
        from src.database.conexion import conectar as cloud_conectar
        return cloud_conectar()

def get_authenticated_connection():
    """
    Obtener conexión del usuario autenticado
    Lanza excepción si no hay usuario autenticado
    """
    return db_manager.get_connection()

def get_current_user():
    """
    Obtener información del usuario actual
    """
    return db_manager.get_current_user()

def is_user_authenticated():
    """
    Verificar si hay usuario autenticado
    """
    return db_manager.is_authenticated()

def logout():
    """
    Cerrar sesión del usuario actual
    """
    db_manager.close_connection()

def execute_transaction(operations: list) -> dict:
    """
    NUEVO: Ejecutar transacción directamente
    """
    return db_manager.execute_transaction(operations)
