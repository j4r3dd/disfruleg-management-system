# -*- coding: utf-8 -*-
"""
src/modules/ubicuoai/ui/__init__.py
Expone las clases principales del módulo UI
CORREGIDO: Cambiar ubicuoai_window_refactored por ubicuoai_window
"""

from .window_ui_constants import COLORS, FONTS, WINDOW_WIDTH, WINDOW_HEIGHT
from .window_lifecycle_manager import WindowLifecycleManager
from .window_event_handlers import WindowEventHandlers
from .window_display_results import WindowDisplayResults
from .window_dialog_handlers import WindowDialogHandlers
from .ubicuoai_window import UbicuoAIWindow  # ✅ CORREGIDO: ubicuoai_window (no refactored)
from .custom_dialogs import (
    CustomDialog,
    show_info,
    show_success, 
    show_warning,
    show_error,
    ask_confirm,
    ask_yes_no,
    show_toast,
    ToastNotification
)

__all__ = [
    'COLORS',
    'FONTS',
    'WINDOW_WIDTH',
    'WINDOW_HEIGHT',
    'WindowLifecycleManager',
    'WindowEventHandlers',
    'WindowDisplayResults',
    'WindowDialogHandlers',
    'UbicuoAIWindow',
    # Custom Dialogs
    'CustomDialog',
    'show_info',
    'show_success',
    'show_warning',
    'show_error',
    'ask_confirm',
    'ask_yes_no',
    'show_toast',
    'ToastNotification',
]