# -*- coding: utf-8 -*-
"""
User Manager Launcher
Entry point for the user management module
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict
import json

from src.database.conexion import conectar, return_connection
from src.auth.auth_manager import AuthManager
from src.theme import COLORS, FONTS

from .data import MySQLUserRepository
from .business import UserService
from .ui import UserManagementApp


class UserManagerLauncher:
    """
    Launcher for user management module
    Handles dependency injection and lifecycle
    """
    
    def __init__(self, user_data: Optional[Dict] = None):
        """
        Initialize launcher
        
        Args:
            user_data: Current logged user data
        """
        self.user_data = self._parse_user_data(user_data)
        self.conn = None
        self.app = None
    
    def _parse_user_data(self, user_data) -> Dict:
        """Parse user data from various formats"""
        if isinstance(user_data, str):
            try:
                return json.loads(user_data)
            except:
                return {}
        return user_data if isinstance(user_data, dict) else {}
    
    def launch(self):
        """Launch the user management application"""
        # Connect to database
        try:
            self.conn = conectar()
            if not self.conn:
                raise Exception("No se pudo establecer conexión")
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
            return
        
        # Create dependencies
        repository = MySQLUserRepository(self.conn)
        auth_manager = AuthManager()
        service = UserService(repository, auth_manager)
        
        # Create and run application
        root = ctk.CTk()
        
        self.app = UserManagementApp(
            root=root,
            service=service,
            user_data=self.user_data,
            colors=COLORS,
            fonts=FONTS,
            on_close=self._on_close
        )
        
        root.mainloop()
    
    def _on_close(self):
        """Handle application close"""
        if self.conn:
            try:
                return_connection(self.conn)
            except Exception as e:
                print(f"Error returning connection: {e}")


def main(user_data=None):
    """
    Main function to run the user manager
    
    Args:
        user_data: Current logged user data (dict or JSON string)
    """
    launcher = UserManagerLauncher(user_data)
    launcher.launch()


if __name__ == "__main__":
    # Test data for standalone execution
    test_user_data = {
        'username': 'admin',
        'nombre_completo': 'Administrador',
        'rol': 'admin'
    }
    main(test_user_data)
