# -*- coding: utf-8 -*-
"""
Base Controller - Funcionalidad común para controllers
"""

import logging
from typing import Optional, Dict, Callable

logger = logging.getLogger(__name__)


class BaseController:
    """Clase base con funcionalidad común para controllers"""
    
    def __init__(
        self,
        on_status_update: Callable[[str, str], None],
        on_stats_update: Callable[[int, int], None]
    ):
        self.on_status_update = on_status_update
        self.on_stats_update = on_stats_update
    
    def _notify_status(self, message: str, level: str = "info"):
        """Notifica cambio de status a la UI"""
        if self.on_status_update:
            self.on_status_update(message, level)
    
    def _notify_stats(self, total: int, matched: int):
        """Notifica estadísticas a la UI"""
        if self.on_stats_update:
            self.on_stats_update(total, matched)
    
    def _log_error(self, message: str, exception: Exception = None):
        """Log de error con stack trace opcional"""
        if exception:
            logger.exception(f"{message}: {exception}")
        else:
            logger.error(message)
    
    def _log_info(self, message: str):
        """Log informativo"""
        logger.info(message)
    
    def _log_debug(self, message: str):
        """Log de debug"""
        logger.debug(message)
