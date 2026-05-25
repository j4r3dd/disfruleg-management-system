# -*- coding: utf-8 -*-
"""
Debt Manager - Entry Point
Sets up dependency injection and launches the debt management UI
Follows Clean Architecture principles
"""

import customtkinter as ctk
from typing import Dict, Any

from src.database.conexion import conectar, return_connection
from src.auth.auth_manager import AuthManager

# Import layers (in dependency order)
from .domain import *
from .data import MySQLDebtRepository, MySQLPaymentRepository
from .business import DebtService, PaymentService


def launch_debt_manager(user_data: Dict[str, Any]):
    """
    Launch debt management window with proper dependency injection

    Args:
        user_data: User information dictionary containing:
            - 'usuario': Username
            - 'es_admin': Admin flag
            - Other user metadata

    Architecture:
        1. Create database connection
        2. Create repositories (Data Layer)
        3. Create services (Business Layer)
        4. Create UI application (Presentation Layer)
        5. Inject dependencies from inner to outer layers
    """
    # Get database connection
    conn = conectar()

    # LAYER 1: Data Layer - Create repositories
    debt_repo = MySQLDebtRepository(conn)
    payment_repo = MySQLPaymentRepository(conn)

    # LAYER 2: Business Layer - Create services (inject repositories)
    debt_service = DebtService(debt_repo)
    payment_service = PaymentService(debt_repo, payment_repo, conn)

    # Auth Manager for admin password verification
    auth_manager = AuthManager()

    # LAYER 3: UI Layer - Create application (inject services)
    # Import here to avoid circular dependencies
    from .ui.debt_management_app import DebtManagementApp

    # Create root window (use CTk instead of CTkToplevel to avoid gray window)
    root = ctk.CTk()
    root.title("Gestión de Deudas")

    # Set window size to 1280x800 (same as original)
    root.geometry("1280x800")

    # Create application with injected services
    app = DebtManagementApp(
        root=root,
        user_data=user_data,
        debt_service=debt_service,
        payment_service=payment_service,
        auth_manager=auth_manager
    )

    # Center window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 1280) // 2
    y = (screen_height - 800) // 2
    root.geometry(f'1280x800+{x}+{y}')

    # Bring window to front
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    root.focus_force()

    # Run the application
    root.mainloop()

    # Cleanup after window closes
    return_connection(conn)


# Singleton pattern for backwards compatibility with old code
_debt_manager_instance = None


def obtener_debt_manager():
    """
    Get debt manager instance (singleton)

    DEPRECATED: This is for backwards compatibility only.
    New code should use launch_debt_manager() with dependency injection.

    Returns:
        Old DebtManager instance (if needed for migration period)
    """
    global _debt_manager_instance

    # For migration period, we can support both old and new interfaces
    # Eventually this should be removed
    from .old.debt_manager_old import DebtManager

    if _debt_manager_instance is None:
        _debt_manager_instance = DebtManager()

    return _debt_manager_instance
