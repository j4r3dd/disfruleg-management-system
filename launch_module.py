#!/usr/bin/env python3
"""
Module Launcher Script
Properly launches business modules with correct Python path and imports
Updated to use consolidated receipt module architecture
CORREGIDO: Validación de window en ubicuoai_module
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def launch_receipts_module(user_data=None):
    """Launch the receipts module with VentanaOrdenes as the main hub - MVC VERSION"""
    try:
        # Change to project root directory
        os.chdir(project_root)

        # Import required modules - NOW USING MVC!
        from src.modules.receipts.components.ventana_ordenes import abrir_ventana_ordenes
        from src.modules.receipts.mvc import receipt_app_mvc
        print("✅ Using VentanaOrdenes as main hub with MVC Receipt Generator")

        # Default user data if none provided
        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }

        # Keep track of editor instances for proper window management
        editor_instances = []
        ventana_ordenes = None  # Reference to main orders window
        root = None  # Reference to root window

        def callback_nueva_orden():
            """Callback to create a new order - opens MVC Receipt Generator without folio"""
            try:
                # Create MVC receipt generator for new order
                nombre_usuario = user_data.get('nombre_completo', user_data.get('username', 'Usuario'))
                username = user_data.get('username', 'Usuario')  # Get actual username for DB operations

                # Create the MVC controller (doesn't call run() - root window handles mainloop)
                controller = receipt_app_mvc.main(
                    parent=root,
                    nombre_usuario=nombre_usuario,
                    username=username
                )
                editor_instances.append(controller)

                # Configure window title
                if controller.view.root:
                    controller.view.root.title("Disfruleg - Nueva Orden (MVC)")

                # Override close handler to refresh orders window
                original_on_close = controller.on_close
                def on_editor_close():
                    if original_on_close:
                        original_on_close()
                    else:
                        controller.view.root.destroy()

                    # Force refresh of orders window after closing
                    if ventana_ordenes and root:
                        root.after(100, ventana_ordenes.forzar_actualizacion)

                controller.on_close = on_editor_close
                controller.view.root.protocol("WM_DELETE_WINDOW", on_editor_close)

                # Bind event for order changes
                def on_orden_cambiada(event):
                    if ventana_ordenes:
                        ventana_ordenes.forzar_actualizacion()
                        print("🔨 Evento OrdenCambiada recibido - actualizando lista")

                controller.view.root.bind("<<OrdenCambiada>>", on_orden_cambiada)

                print(f"✅ Nueva orden creada (MVC) - Editor instancia #{len(editor_instances)}")

            except Exception as e:
                messagebox.showerror("Error", f"Error al crear nueva orden: {str(e)}")
                print(f"Error creating new order: {e}")
                import traceback
                traceback.print_exc()

        def callback_editar_orden(folio):
            """Callback to edit existing order - opens MVC Receipt Generator with specific folio"""
            try:
                # Create MVC receipt generator for existing order
                nombre_usuario = user_data.get('nombre_completo', user_data.get('username', 'Usuario'))
                username = user_data.get('username', 'Usuario')  # Get actual username for DB operations

                # Create the MVC controller
                controller = receipt_app_mvc.main(
                    parent=root,
                    nombre_usuario=nombre_usuario,
                    username=username
                )
                editor_instances.append(controller)

                # Configure window title
                if controller.view.root:
                    controller.view.root.title(f"Disfruleg - Editando Orden {folio:06d} (MVC)")

                # Load the existing order
                controller.cargar_orden_existente(folio)

                # Override close handler to refresh orders window
                original_on_close = controller.on_close
                def on_editor_close():
                    if original_on_close:
                        original_on_close()
                    else:
                        controller.view.root.destroy()

                    # Force refresh of orders window after closing
                    if ventana_ordenes and root:
                        root.after(100, ventana_ordenes.forzar_actualizacion)

                controller.on_close = on_editor_close
                controller.view.root.protocol("WM_DELETE_WINDOW", on_editor_close)

                # Bind event for order changes
                def on_orden_cambiada(event):
                    if ventana_ordenes:
                        ventana_ordenes.forzar_actualizacion()
                        print("🔨 Evento OrdenCambiada recibido - actualizando lista")

                controller.view.root.bind("<<OrdenCambiada>>", on_orden_cambiada)

                print(f"✅ Editando orden {folio:06d} (MVC) - Editor instancia #{len(editor_instances)}")

            except Exception as e:
                messagebox.showerror("Error", f"Error al editar orden {folio}: {str(e)}")
                print(f"Error editing order {folio}: {e}")
                import traceback
                traceback.print_exc()

        # Launch VentanaOrdenes as the main hub
        # We let VentanaOrdenes create the root window (ctk.CTk) since parent is None
        ventana_ordenes = abrir_ventana_ordenes(
            parent=None,  # Main window, not child
            user_data=user_data,
            on_nueva_orden=callback_nueva_orden,
            on_editar_orden=callback_editar_orden
        )

        # Set root reference for callbacks
        root = ventana_ordenes.root

        # Start the main event loop
        ventana_ordenes.show()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el módulo de recibos: {str(e)}")
        print(f"Error launching receipts module: {e}")
        import traceback
        traceback.print_exc()


def launch_pricing_module(user_data=None):
    """Launch the price editor module - Clean Architecture Version"""
    try:
        os.chdir(project_root)
        # Use new refactored version with clean architecture
        from src.modules.pricing import launch_price_editor

        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }

        # Launch the refactored price editor (it handles its own mainloop)
        launch_price_editor(user_data)

    except Exception as e:
        error_msg = f"No se pudo cargar el editor de precios: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Error", error_msg)
        except:
            print(f"Could not show error dialog: {error_msg}")

def launch_inventory_module(user_data=None):
    """Launch the inventory/purchases module - Clean Architecture Version"""
    try:
        os.chdir(project_root)
        # Use new refactored version with clean architecture
        from src.modules.inventory import launch_purchase_manager

        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }

        # Launch the refactored purchase manager (it handles its own mainloop)
        launch_purchase_manager(user_data)

    except Exception as e:
        error_msg = f"No se pudo cargar el registro de compras: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Error", error_msg)
        except:
            print(f"Could not show error dialog: {error_msg}")

def launch_analytics_module(user_data=None):
    """Launch the analytics module - Clean Architecture Version"""
    try:
        os.chdir(project_root)

        # ✅ Use new refactored version with clean architecture
        from src.modules.analytics import launch_analytics
        import customtkinter as ctk

        # Configurar CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }

        # Launch the refactored analytics module (it handles everything internally)
        analytics_window = launch_analytics(user_data)

        if analytics_window:
            # Start mainloop
            analytics_window.mainloop()

    except Exception as e:
        import traceback
        error_msg = f"No se pudo cargar el análisis de ganancias:\n{str(e)}"
        print(error_msg)
        print(traceback.format_exc())

        try:
            from tkinter import messagebox
            messagebox.showerror("Error Analytics", error_msg[:200])
        except:
            pass

def launch_clients_module(user_data=None):
    """Launch the client management module - Clean Architecture Version"""
    try:
        os.chdir(project_root)
        # Use new refactored version with clean architecture
        from src.modules.clients import launch_client_manager

        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }

        # Launch the refactored client manager (it handles its own mainloop)
        launch_client_manager()

    except Exception as e:
        error_msg = f"No se pudo cargar el administrador de clientes: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Error", error_msg)
        except:
            print(f"Could not show error dialog: {error_msg}")

def launch_users_module(user_data=None):
    """Launch the user management module - Clean Architecture Version"""
    try:
        os.chdir(project_root)
        
        # ✅ NEW: Use refactored version with clean architecture
        from src.modules.users import main as launch_user_manager

        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }

        # Launch the refactored user manager (it handles its own mainloop)
        launch_user_manager(user_data)

    except Exception as e:
        error_msg = f"No se pudo cargar el administrador de usuarios: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Error", error_msg)
        except:
            print(f"Could not show error dialog: {error_msg}")

# ==================== FUNCIÓN CORREGIDA ====================

def launch_debts_module(user_data=None):
    """Launch the debt management module"""
    try:
        os.chdir(project_root)
        from src.modules.deudas import launch_debt_manager
        import customtkinter as ctk

        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test',
                'es_admin': True
            }

        # Configurar tema oscuro
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')

        # Lanzar el debt manager (crea su propia ventana internamente)
        # launch_debt_manager() solo acepta user_data como argumento
        launch_debt_manager(user_data)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el módulo de deudas: {str(e)}")
        print(f"Error launching debts module: {e}")
        import traceback
        traceback.print_exc()

def launch_ubicuoai_module(user_data=None):
    """Launch the UbicuoAI intelligent order processing module - Clean Architecture Version"""
    try:
        os.chdir(project_root)

        # Import CustomTkinter for the main window
        import customtkinter as ctk

        # Configure CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create root window
        root = ctk.CTk()
        root.withdraw()  # Hide the root window
        root.title("Ubicuo AI - Sistema Inteligente de Pedidos")

        if user_data is None:
            user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }

        # Import and initialize ubicuoai - Use open_ubicuoai_window function
        from src.modules.ubicuoai import open_ubicuoai_window

        # Open window using the module's initialization function
        # This ensures all services are properly injected
        window = open_ubicuoai_window(root, user_data)
        
        # ✅ VALIDACIÓN AGREGADA: Verificar que la ventana se creó correctamente
        if not window:
            raise RuntimeError("No se pudo crear la ventana de UbicuoAI")
        
        # ✅ VALIDACIÓN AGREGADA: Verificar antes de llamar a métodos
        if window:
            window.update()  # Force window update
            window.lift()
            window.focus_force()

        # Start mainloop
        root.mainloop()

        # Clean exit after window closes
        print("✅ UbicuoAI cerrado correctamente")

    except Exception as e:
        error_msg = f"No se pudo cargar UbicuoAI: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Error", error_msg)
        except:
            print(f"Could not show error dialog: {error_msg}")

def main():
    """Main entry point when script is run directly"""
    if len(sys.argv) < 2:
        print("Usage: python launch_module.py <module_name>")
        print("Available modules: receipts, pricing, inventory, analytics, clients, users, debts, ubicuoai")
        sys.exit(1)

    module_name = sys.argv[1].lower()

    # Get user data from command line if provided (as JSON string)
    user_data = None
    if len(sys.argv) > 2:
        import json
        try:
            user_data = json.loads(sys.argv[2])
        except:
            print("Warning: Invalid user data JSON, using default")

    # Launch the appropriate module
    if module_name == "receipts":
        launch_receipts_module(user_data)
    elif module_name == "pricing":
        launch_pricing_module(user_data)
    elif module_name == "purchases":
        launch_inventory_module(user_data)
    elif module_name in ["analytics", "reports"]:
        launch_analytics_module(user_data)
    elif module_name == "clients":
        launch_clients_module(user_data)
    elif module_name == "users":
        launch_users_module(user_data)
    elif module_name == "debts":
        launch_debts_module(user_data)
    elif module_name == "ubicuoai":
        launch_ubicuoai_module(user_data)
    else:
        print(f"Unknown module: {module_name}")
        print("Available modules: receipts, pricing, inventory, purchases, analytics, clients, users, debts, ubicuoai")
        sys.exit(1)

if __name__ == "__main__":
    main()