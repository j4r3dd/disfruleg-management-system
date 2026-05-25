#!/usr/bin/env python3
"""
DISFRULEG - Sistema de Gestión Comercial
Refactored modular version - Entry Point
"""

import sys
import os
import warnings

# Suppress Tkinter/CustomTkinter warnings on macOS
if sys.platform == "darwin":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*invalid command name.*")

    class TkinterStderrFilter:
        """Filter Tkinter errors in stderr"""
        def __init__(self):
            self.original_stderr = sys.stderr

        def write(self, text):
            # Filter only known Tkinter errors
            if not any(x in str(text) for x in [
                'invalid command name',
                'bgerror failed',
                'application has been destroyed',
                'check_dpi_scaling'
            ]):
                self.original_stderr.write(text)

        def flush(self):
            self.original_stderr.flush()

    sys.stderr = TkinterStderrFilter()

import customtkinter as ctk
from tkinter import messagebox
from customtkinter import *
from src.config import debug_print, get_app_config
from src.main_application import MainApplication

def main():
    """Main function - Entry point"""
    try:
        config = get_app_config()
        
        # ✅ Solo muestra info esencial
        if config['debug_mode']:
            debug_print("=== PROGRAM START ===")
            debug_print(f"Debug mode: {config['debug_mode']}")
            debug_print(f"Use login: {config['use_login']}")
            debug_print(f"Use session manager: {config['use_session_manager']}")
            debug_print(f"Use canvas scroll: {config['use_canvas_scroll']}")
            debug_print(f"Use hover effects: {config['use_hover_effects']}")
        
        # Create and start application
        app = MainApplication()
        app.start()
        
    except Exception as e:
        # ✅ Solo errores fatales
        print(f"❌ Error Fatal: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Error Fatal", f"Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()