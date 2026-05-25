# -*- coding: utf-8 -*-
"""
Price Manager - Main Entry Point (Clean Architecture)
This module initializes and manages the price editor application.

Architecture Layers:
    UI Layer → Business Layer → Data Layer → Domain Layer
"""

import customtkinter as ctk
from src.database.conexion import conectar, return_connection

# Import from architecture layers
from src.modules.pricing.data.mysql_repositories import (
    MySQLProductRepository,
    MySQLGroupRepository,
    MySQLClientTypeRepository,
    MySQLPriceRepository,
    MySQLLockRepository
)
from src.modules.pricing.business.pricing_service import PricingService
from src.modules.pricing.business.product_service import ProductService


def launch_price_editor(user_data: dict, filtro_productos=None) -> None:
    """
    Launch the price editor application with clean architecture.

    Args:
        user_data: Dictionary containing user information (nombre_completo, rol, etc.)
        filtro_productos: Optional list of product IDs to filter
    """
    # Create root window
    root = ctk.CTk()
    root.title("Editor de Precios - DISFRULEG")
    root.geometry("1400x900")

    # Establish database connection
    conn = conectar()

    if conn is None:
        from tkinter import messagebox
        messagebox.showerror(
            "Connection Error",
            "Could not connect to the database.\\nPlease check your connection settings."
        )
        root.destroy()
        return

    try:
        # ==================== DEPENDENCY INJECTION ====================
        # Layer 1: Data Layer - Repository implementations
        product_repo = MySQLProductRepository(conn)
        group_repo = MySQLGroupRepository(conn)
        client_type_repo = MySQLClientTypeRepository(conn)
        price_repo = MySQLPriceRepository(conn)
        lock_repo = MySQLLockRepository(conn)

        # Layer 2: Business Layer - Services (depend on repositories)
        product_service = ProductService(product_repo, lock_repo)
        pricing_service = PricingService(
            price_repo,
            group_repo,
            client_type_repo,
            product_repo
        )

        # Layer 3: UI Layer - Application (coordinates View with Services)
        # NOTE: Import here to avoid circular dependencies
        from src.modules.pricing.ui.price_editor_app import PriceEditorApplication

        app = PriceEditorApplication(
            root=root,
            user_data=user_data,
            product_service=product_service,
            pricing_service=pricing_service,
            filtro_productos=filtro_productos
        )

        # Set up clean exit
        def on_closing():
            """Clean shutdown"""
            try:
                # Release all locks for this user
                username = user_data.get('nombre_completo', 'Unknown')
                product_service.release_all_locks_for_user(username)

                if conn:
                    return_connection(conn)
            except:
                pass
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Start the application
        root.mainloop()

    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror(
            "Initialization Error",
            f"Failed to initialize the application:\\n{str(e)}"
        )
        if conn:
            return_connection(conn)
        root.destroy()


# Entry point for standalone execution
if __name__ == "__main__":
    # Test user data
    test_user = {
        'nombre_completo': 'Test User',
        'username': 'testuser',
        'rol': 'admin'
    }
    launch_price_editor(test_user)
