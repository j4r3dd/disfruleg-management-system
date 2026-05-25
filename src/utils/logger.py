"""
Módulo de logging centralizado para la aplicación
Proporciona funciones de logging con diferentes niveles y rotación de archivos
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

class AppLogger:
    """Clase para manejo centralizado de logs"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Configura el logger de la aplicación"""
        # Crear directorio de logs si no existe
        try:
            from src.utils.resource_path import get_writable_path
            log_dir = get_writable_path("logs").parent / "logs"
        except ImportError:
            # Fallback for development
            log_dir = Path("logs")

        log_dir.mkdir(exist_ok=True)
        
        # Crear logger
        self._logger = logging.getLogger("BodegaDisfruleg")
        self._logger.setLevel(logging.DEBUG)
        
        # Evitar duplicación de handlers
        if self._logger.handlers:
            return
        
        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo con rotación (máximo 10MB, mantener 5 backups)
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler para errores (archivo separado)
        error_handler = RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Agregar handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(error_handler)
        self._logger.addHandler(console_handler)
    
    def get_logger(self):
        """Retorna el logger configurado"""
        return self._logger
    
    # Métodos de conveniencia
    def debug(self, mensaje: str, **kwargs):
        """Log nivel DEBUG"""
        self._logger.debug(mensaje, **kwargs)
    
    def info(self, mensaje: str, **kwargs):
        """Log nivel INFO"""
        self._logger.info(mensaje, **kwargs)
    
    def warning(self, mensaje: str, **kwargs):
        """Log nivel WARNING"""
        self._logger.warning(mensaje, **kwargs)
    
    def error(self, mensaje: str, exc_info=False, **kwargs):
        """Log nivel ERROR"""
        self._logger.error(mensaje, exc_info=exc_info, **kwargs)
    
    def critical(self, mensaje: str, exc_info=False, **kwargs):
        """Log nivel CRITICAL"""
        self._logger.critical(mensaje, exc_info=exc_info, **kwargs)
    
    def exception(self, mensaje: str, **kwargs):
        """Log de excepción con traceback"""
        self._logger.exception(mensaje, **kwargs)


# Instancia global del logger
_app_logger = AppLogger()

# Funciones de conveniencia para uso directo
def get_logger():
    """Obtiene el logger de la aplicación"""
    return _app_logger.get_logger()

def log_debug(mensaje: str, **kwargs):
    """Log nivel DEBUG"""
    _app_logger.debug(mensaje, **kwargs)

def log_info(mensaje: str, **kwargs):
    """Log nivel INFO"""
    _app_logger.info(mensaje, **kwargs)

def log_warning(mensaje: str, **kwargs):
    """Log nivel WARNING"""
    _app_logger.warning(mensaje, **kwargs)

def log_error(mensaje: str, exc_info=False, **kwargs):
    """Log nivel ERROR"""
    _app_logger.error(mensaje, exc_info=exc_info, **kwargs)

def log_critical(mensaje: str, exc_info=False, **kwargs):
    """Log nivel CRITICAL"""
    _app_logger.critical(mensaje, exc_info=exc_info, **kwargs)

def log_exception(mensaje: str, **kwargs):
    """Log de excepción con traceback completo"""
    _app_logger.exception(mensaje, **kwargs)


class ModuleLogger:
    """Logger específico para un módulo"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = _app_logger.get_logger()
    
    def _format_message(self, mensaje: str) -> str:
        """Formatea mensaje con nombre del módulo"""
        return f"[{self.module_name}] {mensaje}"
    
    def debug(self, mensaje: str, **kwargs):
        self.logger.debug(self._format_message(mensaje), **kwargs)
    
    def info(self, mensaje: str, **kwargs):
        self.logger.info(self._format_message(mensaje), **kwargs)
    
    def warning(self, mensaje: str, **kwargs):
        self.logger.warning(self._format_message(mensaje), **kwargs)
    
    def error(self, mensaje: str, exc_info=False, **kwargs):
        self.logger.error(self._format_message(mensaje), exc_info=exc_info, **kwargs)
    
    def critical(self, mensaje: str, exc_info=False, **kwargs):
        self.logger.critical(self._format_message(mensaje), exc_info=exc_info, **kwargs)
    
    def exception(self, mensaje: str, **kwargs):
        self.logger.exception(self._format_message(mensaje), **kwargs)


# Decorador para logging automático de funciones
def log_function_call(logger: Optional[ModuleLogger] = None):
    """
    Decorador que registra la entrada y salida de funciones
    
    Args:
        logger: Logger a usar (opcional)
    """
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or _app_logger
            
            _logger.debug(f"Llamando a {func.__name__} con args={args}, kwargs={kwargs}")
            
            try:
                resultado = func(*args, **kwargs)
                _logger.debug(f"{func.__name__} completado exitosamente")
                return resultado
            except Exception as e:
                _logger.error(f"Error en {func.__name__}: {str(e)}", exc_info=True)
                raise
        
        return wrapper
    return decorator


# Ejemplo de uso:
if __name__ == "__main__":
    # Uso básico
    log_info("Aplicación iniciada")
    log_debug("Detalles de debug")
    log_warning("Advertencia")
    log_error("Error encontrado")
    
    # Uso con logger de módulo
    mi_logger = ModuleLogger("TestModule")
    mi_logger.info("Módulo de prueba iniciado")
    mi_logger.error("Error en módulo de prueba")
    
    # Uso con decorador
    @log_function_call()
    def funcion_ejemplo(x, y):
        return x + y
    
    funcion_ejemplo(5, 3)