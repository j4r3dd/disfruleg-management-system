# -*- coding: utf-8 -*-
"""
Purchase Manager - Main Entry Point (Refactored with Clean Architecture)
This module initializes and manages the purchase registration application.

Architecture Layers:
    UI Layer (Controller) → Business Layer (Services) → Data Layer (Repositories) → Domain Layer (Models)
"""

import customtkinter as ctk
from src.database.conexion import conectar, return_connection

# Import from architecture layers
from src.modules.inventory.data.mysql_repositories import (
    MySQLProductRepository,
    MySQLPurchaseRepository
)
from src.modules.inventory.business.purchase_service import PurchaseService
from src.modules.inventory.business.product_service import ProductService
from src.modules.inventory.ui.purchase_app import PurchaseApplication


def launch_purchase_manager(user_data: dict) -> None:
    """
    Launch the purchase manager application with clean architecture.

    Args:
        user_data: Dictionary containing user information (nombre_completo, rol, etc.)
    """
    # Create root window
    root = ctk.CTk()
    root.title("Purchase Manager - DISFRULEG")
    root.geometry("1600x900")

    # Establish database connection
    conn = conectar()

    if conn is None:
        from tkinter import messagebox
        messagebox.showerror(
            "Connection Error",
            "Could not connect to the database.\nPlease check your connection settings."
        )
        root.destroy()
        return

    try:
        # ==================== DEPENDENCY INJECTION ====================
        # Layer 1: Data Layer - Repository implementations
        product_repo = MySQLProductRepository(conn)
        purchase_repo = MySQLPurchaseRepository(conn)

        # Layer 2: Business Layer - Services (depend on repositories)
        product_service = ProductService(product_repo)
        purchase_service = PurchaseService(purchase_repo, product_repo)

        # Layer 3: UI Layer - Application Controller (coordinates View with Services)
        app = PurchaseApplication(
            root=root,
            user_data=user_data,
            purchase_service=purchase_service,
            product_service=product_service
        )

        # Set up clean exit
        def on_closing():
            """Clean shutdown"""
            try:
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
            f"Failed to initialize the application:\n{str(e)}"
        )
        if conn:
            return_connection(conn)
        root.destroy()


# Entry point for standalone execution
if __name__ == "__main__":
    # Test user data
    test_user = {
        'nombre_completo': 'Test User',
        'rol': 'admin'
    }
    launch_purchase_manager(test_user)
