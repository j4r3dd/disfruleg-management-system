# -*- coding: utf-8 -*-
"""
Analytics Module Launcher - Clean Architecture
Entry point for the analytics module with dependency injection
"""

import customtkinter as ctk
import platform
import logging

from src.database.conexion import conectar, return_connection

# Import layers
from .business import AnalyticsService
from .data import (
    MySQLAnalyticsRepository,
    MySQLProductAnalyticsRepository,
    MySQLClientAnalyticsRepository,
    MySQLGroupAnalyticsRepository,
    MySQLSalesTrendRepository,
    InMemoryCacheRepository
)
from .ui import AnalisisGananciasApp

logger = logging.getLogger(__name__)


def launch_analytics(user_data=None):
    """
    Launcher para la aplicación de analytics con Clean Architecture

    Args:
        user_data: Dictionary with user information

    Returns:
        Analytics window instance
    """
    import platform

    # Create main CTk window (not Toplevel) to avoid blank parent window
    analytics_window = ctk.CTk()
    analytics_window.title("Análisis de Ventas - Disfruleg")

    if not user_data:
        user_data = {
            'nombre_completo': 'Usuario Prueba',
            'rol': 'admin'
        }

    try:
        # Establish database connection
        conn = conectar()

        # Initialize repositories
        analytics_repo = MySQLAnalyticsRepository(conn)
        product_repo = MySQLProductAnalyticsRepository(conn)
        client_repo = MySQLClientAnalyticsRepository(conn)
        group_repo = MySQLGroupAnalyticsRepository(conn)
        sales_trend_repo = MySQLSalesTrendRepository(conn)
        cache_repo = InMemoryCacheRepository(default_ttl=300)

        # Initialize service with dependency injection
        analytics_service = AnalyticsService(
            analytics_repo=analytics_repo,
            product_repo=product_repo,
            client_repo=client_repo,
            group_repo=group_repo,
            sales_trend_repo=sales_trend_repo,
            cache_repo=cache_repo
        )

        # Initialize UI with service
        app = AnalisisGananciasApp(analytics_window, user_data, analytics_service)

        # Store connection for cleanup
        app.conn = conn

        # Setup close handler
        def on_close():
            try:
                app.on_closing()
                return_connection(conn)
            except Exception as e:
                logger.error(f"Error closing analytics: {e}")

        analytics_window.protocol("WM_DELETE_WINDOW", on_close)

        is_mac = platform.system() == 'Darwin'
        delay = 200 if is_mac else 100

        analytics_window.after(delay, lambda: _bring_to_front(analytics_window, is_mac))

        return analytics_window

    except Exception as e:
        logger.error(f"Error launching analytics: {e}")
        from tkinter import messagebox
        messagebox.showerror("Error", f"No se pudo abrir analytics:\n{e}")
        analytics_window.destroy()
        return None


def _bring_to_front(window, is_mac=False):
    """Helper para traer ventana al frente (optimizado Mac/Windows)"""
    try:
        if is_mac:
            window.withdraw()
            window.deiconify()
            window.lift()
            window.attributes('-topmost', True)
            window.update_idletasks()
            window.after(100, lambda: window.attributes('-topmost', False))
            window.focus_force()
            window.after(200, lambda: _mac_focus_retry(window))
        else:
            window.lift()
            window.attributes('-topmost', True)
            window.update()
            window.after(50, lambda: window.attributes('-topmost', False))
            window.focus_force()

    except Exception as e:
        logger.error(f"Error bringing window to front: {e}")


def _mac_focus_retry(window):
    """Reintento adicional para macOS"""
    try:
        window.lift()
        window.focus_force()

        current_geo = window.geometry()
        if 'x' in current_geo and 'y' in current_geo:
            parts = current_geo.split('+')
            if len(parts) == 3:
                x, y = int(parts[1]), int(parts[2])
                window.geometry(f"+{x}+{y-1}")
                window.after(10, lambda: window.geometry(f"+{x}+{y}"))
    except:
        pass