# -*- coding: utf-8 -*-
"""
Base Service Class
Provides common functionality for all services
"""

from typing import Optional
from src.config import debug_print


class BaseService:
    """Base class for all business logic services"""

    def __init__(self):
        pass

    def _log_info(self, message: str):
        """Log informational message"""
        debug_print(f"ℹ️ {message}")

    def _log_success(self, message: str):
        """Log success message"""
        debug_print(f"✅ {message}")

    def _log_error(self, message: str, exception: Optional[Exception] = None):
        """Log error message"""
        debug_print(f"❌ {message}")
        if exception:
            import traceback
            traceback.print_exc()

    def _log_warning(self, message: str):
        """Log warning message"""
        debug_print(f"⚠️ {message}")
