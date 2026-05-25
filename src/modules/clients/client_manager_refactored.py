# -*- coding: utf-8 -*-
"""
DISFRULEG - Client Manager (Clean Architecture Refactor)
Main entry point using clean architecture with dependency injection.
"""

import customtkinter as ctk
from src.database.conexion import conectar, return_connection
from src.theme import COLORS, FONTS

# Import layers
from .data import (
    MySQLClientRepository,
    MySQLGroupRepository,
    MySQLClientTypeRepository
)
from .business import (
    ClientService,
    GroupService,
    ClientTypeService
)
from .ui.client_controller import ClientController
from .ui.client_view import ClientManagerView  # Will create this


def launch_client_manager(parent_window=None, user_data=None):
    """
    Launch client manager with clean architecture.
    This is the composition root where we wire up dependencies.
    
    Args:
        parent_window: Parent window for the client manager
        user_data: User information dictionary
    """
    try:
        # Get database connection
        conn = conectar()
        if conn is None:
            from tkinter import messagebox
            messagebox.showerror("Database Error", "Cannot connect to database")
            return False

        # ========== COMPOSITION ROOT ==========
        # Layer 1: Data Layer - Create repositories
        client_repo = MySQLClientRepository(conn)
        group_repo = MySQLGroupRepository(conn)
        client_type_repo = MySQLClientTypeRepository(conn)

        # Layer 2: Business Layer - Create services (inject repositories)
        client_service = ClientService(client_repo, group_repo)
        group_service = GroupService(group_repo, client_type_repo)
        client_type_service = ClientTypeService(client_type_repo)

        # Layer 3: UI Layer - Create controller (inject services)
        controller = ClientController(
            client_service,
            group_service,
            client_type_service
        )

        # Layer 4: Create view (inject controller)
        # Use parent_window if provided, otherwise create new CTkToplevel
        if parent_window:
            # Create as toplevel window within the app
            view = ClientManagerView(parent_window, controller)
        else:
            # Fallback: create standalone window
            import customtkinter as ctk
            root = ctk.CTk()
            view = ClientManagerView(root, controller)
            root.protocol("WM_DELETE_WINDOW", lambda: on_closing(conn, root))
            root.mainloop()
            return True

        # If parent_window was provided, return success (view handles its own lifecycle)
        return True

    except Exception as e:
        print(f"Error launching client manager: {e}")
        import traceback
        traceback.print_exc()
        return False


def on_closing(conn, root):
    """Clean up resources on closing"""
    try:
        if conn:
            return_connection(conn)
    except:
        pass

    try:
        root.destroy()
    except:
        pass


if __name__ == "__main__":
    launch_client_manager()