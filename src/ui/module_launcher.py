"""
DISFRULEG - Module Launcher
Handles module definitions, launching, and management
"""

import os
import sys
import json
import time
import threading
import subprocess
import importlib.util
from contextlib import contextmanager
from tkinter import messagebox
from typing import Optional, Dict, List, Any, Set

from src.config import debug_print, USE_SESSION_MANAGER
from src.ui.loading_indicator import LoadingIndicator


# Constants
MODULE_RELAUNCH_DELAY_SECONDS = 2.0
MODULE_CLEANUP_DELAY_SECONDS = 3.0

# ==================== DEBUG CONFIGURATION ====================
# Set to True to show console windows (for debugging)
# Set to False to hide console windows (for production)
SHOW_MODULE_CONSOLE = False # ⬅️ CHANGE THIS TO True/False
# ============================================================


class WindowRegistry:
    """Centralized registry for managing parent windows"""

    _main_window = None

    @classmethod
    def set_main_window(cls, window):
        """Register the main application window"""
        cls._main_window = window

    @classmethod
    def get_main_window(cls):
        """Get the main window, attempting to find it if not registered"""
        if cls._main_window:
            return cls._main_window

        # Fallback: try to find the main window
        try:
            import customtkinter as ctk
            # Check customtkinter windows
            for window in ctk.windows.values():
                if isinstance(window, ctk.CTk):
                    cls._main_window = window
                    return cls._main_window
        except (ImportError, AttributeError):
            pass

        # Last resort: check tkinter default root
        try:
            import tkinter as tk
            if hasattr(tk, '_default_root') and tk._default_root:
                cls._main_window = tk._default_root
                return cls._main_window
        except (ImportError, AttributeError):
            pass

        return None


class ModuleLauncher:
    """Class for managing and launching application modules"""

    def __init__(self):
        self.modules = self._get_module_definitions()
        self.project_root = self._calculate_project_root()
        self.launcher_script_path = os.path.join(self.project_root, "launch_module.py")

        # Track currently open modules to prevent duplicates
        self.open_modules: Set[str] = set()
        self.module_launch_times: Dict[str, float] = {}

        debug_print(f"ModuleLauncher initialized:")
        debug_print(f"  Project root: {self.project_root}")
        debug_print(f"  Launcher exists: {os.path.exists(self.launcher_script_path)}")

    @staticmethod
    def _calculate_project_root() -> str:
        """Calculate absolute path to project root"""
        current_file = os.path.abspath(__file__)
        # Go up three directories: module_launcher.py -> ui -> src -> project_root
        return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    def _get_module_definitions(self) -> List[Dict[str, Any]]:
        """Get all module definitions"""
        return [
            {
                'title': 'Generar Recibos',
                'description': 'Crear recibos para clientes\ny gestionar facturación',
                'module_key': 'receipts',
                'icon': 'receipts',
                'bg_color': '#FF00A0',
                'hover_color': '#E6008F',
                'requires_admin': False
            },
            {
                'title': 'Editor de Precios',
                'description': 'Gestionar productos\ny precios por tipo de cliente',
                'module_key': 'pricing',
                'icon': 'pricing',
                'bg_color': '#FF8C00',
                'hover_color': '#E67E00',
                'requires_admin': True
            },
            {
                'title': 'Registro de Compras',
                'description': 'Registrar compras\ny gestionar inventario',
                'module_key': 'purchases',
                'icon': 'purchases',
                'bg_color': '#20B2AA',
                'hover_color': '#1C9B95',
                'requires_admin': False
            },
            {
                'title': 'Análisis de Ventas',
                'description': 'Ver reportes detallados\nde ventas y estadísticas',
                'module_key': 'reports',
                'icon': 'reports',
                'bg_color': '#FFD700',
                'hover_color': '#E6C200',
                'requires_admin': True
            },
            {
                'title': 'Administrar Clientes',
                'description': 'Gestionar clientes\ny tipos de cliente',
                'module_key': 'clients',
                'icon': 'clients',
                'bg_color': '#00BFFF',
                'hover_color': '#00ABEB',
                'requires_admin': True
            },
            {
                'title': 'Administrar Usuarios',
                'description': 'Gestionar usuarios del sistema\ny permisos de acceso',
                'module_key': 'users',
                'icon': 'users',
                'bg_color': '#8A2BE2',
                'hover_color': '#7A26CA',
                'requires_admin': True
            },
            {
                'title': 'Gestión de Deudas',
                'description': 'Control de cuentas por cobrar\ny seguimiento de pagos',
                'module_key': 'debts',
                'icon': 'debts',
                'bg_color': '#FF4040',
                'hover_color': '#E63939',
                'requires_admin': True
            },
            {
                'title': 'Administración de Dispositivos',
                'description': 'Control y autorización\nde dispositivos del sistema',
                'module_key': 'devices',
                'icon': 'devices',
                'bg_color': '#32CD32',
                'hover_color': '#2DB82D',
                'requires_admin': True
            },
            {
                'title': 'Importar Cotización',
                'description': 'Actualizar precios masivamente\ndesde archivos PDF',
                'module_key': 'import_cotizaciones',
                'icon': 'import_cotizaciones',
                'bg_color': '#FF1493',
                'hover_color': '#E01283',
                'requires_admin': True
            },
            {
                'title': 'Ubicuo AI',
                'description': 'Procesamiento inteligente de pedidos\ncon aprendizaje automático',
                'module_key': 'ubicuoai',
                'icon': 'ubicuoai',
                'bg_color': '#9C27B0',
                'hover_color': '#8A24A0',
                'requires_admin': False
            }
        ]

    def get_available_modules(self, user_role: str) -> List[Dict[str, Any]]:
        """Get modules available for the given user role"""
        available_modules = [
            module for module in self.modules
            if not module['requires_admin'] or user_role == 'admin'
        ]

        debug_print(f"Found {len(available_modules)} modules for role: {user_role}")
        return available_modules

    @contextmanager
    def _track_module_launch(self, module_key: str):
        """Context manager for tracking module launch status"""
        try:
            self.open_modules.add(module_key)
            self.module_launch_times[module_key] = time.time()
            debug_print(f"Module {module_key} marked as open")
            yield
        except Exception:
            # Remove from open modules on error
            self.open_modules.discard(module_key)
            raise
        finally:
            # Schedule automatic cleanup
            self._schedule_module_cleanup(module_key)

    def _check_duplicate_launch(self, module_key: str) -> bool:
        """
        Check if module is already open and handle duplicate launches

        Returns:
            True if launch should proceed, False if it should be blocked
        """
        if module_key not in self.open_modules:
            return True

        current_time = time.time()
        last_launch = self.module_launch_times.get(module_key, 0)

        if current_time - last_launch < MODULE_RELAUNCH_DELAY_SECONDS:
            debug_print(f"Module {module_key} is already open. Ignoring duplicate launch.")
            return False

        # Enough time passed, allow re-launch
        debug_print(f"Module {module_key} timeout elapsed. Allowing re-launch.")
        self.open_modules.discard(module_key)
        return True

    def _schedule_module_cleanup(self, module_key: str):
        """Schedule automatic cleanup of module after delay"""
        def cleanup():
            time.sleep(MODULE_CLEANUP_DELAY_SECONDS)
            if module_key in self.open_modules:
                self.open_modules.discard(module_key)
                debug_print(f"Module {module_key} auto-cleaned from tracking")

        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()

    def _wait_for_module_window(self, pid: int, module_key: str, max_wait: float = 15.0):
        """
        Wait until the module's window appears or timeout
        
        Args:
            pid: Process ID of the launched module
            module_key: Key of the module (for logging)
            max_wait: Maximum time to wait in seconds
        """
        start_time = time.time()
        window_found = False
        
        # Try Windows-specific detection first
        if sys.platform.startswith('win'):
            try:
                window_found = self._wait_for_window_win32(pid, max_wait)
            except Exception as e:
                debug_print(f"Win32 window detection failed: {e}, using fallback")
        
        # Fallback: simple polling with process check
        if not window_found:
            while time.time() - start_time < max_wait:
                try:
                    # Check if process is still running
                    import psutil
                    if not psutil.pid_exists(pid):
                        debug_print(f"Process {pid} ended before window appeared")
                        break
                    
                    proc = psutil.Process(pid)
                    
                    # Check if process has any windows (heuristic: CPU usage drops after window init)
                    # Or check for child processes which might indicate GUI initialization
                    children = proc.children(recursive=True)
                    
                    # Give initial startup time
                    elapsed = time.time() - start_time
                    if elapsed > 1.0:
                        # After 1 second, start checking CPU usage
                        cpu = proc.cpu_percent(interval=0.1)
                        # If CPU dropped significantly, window likely appeared
                        if elapsed > 2.0 and cpu < 10:
                            debug_print(f"Module {module_key} window likely ready (low CPU)")
                            window_found = True
                            break
                    
                    time.sleep(0.3)
                    
                except ImportError:
                    # psutil not available, use simple time-based fallback
                    debug_print("psutil not available, using time-based wait")
                    time.sleep(min(3.0, max_wait))
                    break
                except Exception as e:
                    debug_print(f"Error checking process: {e}")
                    time.sleep(0.5)
        
        elapsed = time.time() - start_time
        debug_print(f"Module {module_key} window wait completed in {elapsed:.1f}s (found: {window_found})")
    
    def _wait_for_window_win32(self, pid: int, max_wait: float) -> bool:
        """
        Windows-specific: Wait for a window belonging to the process
        
        Args:
            pid: Process ID
            max_wait: Maximum wait time
            
        Returns:
            True if window found, False otherwise
        """
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            
            # EnumWindows callback
            EnumWindowsProc = ctypes.WINFUNCTYPE(
                wintypes.BOOL, 
                wintypes.HWND, 
                wintypes.LPARAM
            )
            
            found_window = [False]
            
            def enum_callback(hwnd, lparam):
                # Get process ID of window
                window_pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
                
                if window_pid.value == pid:
                    # Check if window is visible
                    if user32.IsWindowVisible(hwnd):
                        found_window[0] = True
                        return False  # Stop enumeration
                return True  # Continue enumeration
            
            callback = EnumWindowsProc(enum_callback)
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                found_window[0] = False
                user32.EnumWindows(callback, 0)
                
                if found_window[0]:
                    # Window found! Wait a tiny bit more for it to fully render
                    time.sleep(0.3)
                    return True
                
                time.sleep(0.2)
            
            return False
            
        except Exception as e:
            debug_print(f"Win32 EnumWindows failed: {e}")
            return False

    def _update_session_activity(self):
        """Update session manager activity if enabled"""
        if not USE_SESSION_MANAGER:
            return

        try:
            from src.auth.session_manager import session_manager
            session_manager.update_activity()
        except ImportError:
            debug_print("Session manager not available")

    def _validate_admin_permission(self, user_data: Optional[Dict[str, Any]]) -> bool:
        """
        Validate if user has admin permissions

        Returns:
            True if user is admin, False otherwise
        """
        user_role = user_data.get('rol', 'usuario') if user_data else 'usuario'
        if user_role != 'admin':
            messagebox.showwarning(
                "Acceso Denegado",
                "Solo los administradores pueden acceder a este módulo."
            )
            return False
        return True

    def _ensure_project_in_path(self):
        """Ensure project root is in Python path"""
        if self.project_root not in sys.path:
            sys.path.insert(0, self.project_root)

    def _get_database_connection(self, db_connection):
        """Get or create database connection"""
        if db_connection is not None:
            return db_connection

        try:
            from database.conexion import conectar
            db_connection = conectar()

            if not db_connection:
                raise ConnectionError("Failed to connect to database")

            # Validate connection
            cursor = db_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()

            return db_connection

        except Exception as e:
            messagebox.showerror(
                "Error de Conexión",
                f"No se pudo obtener conexión a la base de datos:\n{str(e)}"
            )
            raise

    def _launch_device_module(self, user_data: Optional[Dict[str, Any]]) -> bool:
        """
        Launch the device administration module directly

        Args:
            user_data: User information dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_project_in_path()

            from src.modules.device_admin_module import launch_device_admin_module

            parent_window = WindowRegistry.get_main_window()
            success = launch_device_admin_module(parent_window, user_data)

            debug_print(f"Device module launched: {success}")
            return success

        except ImportError as e:
            messagebox.showerror(
                "Error de Importación",
                f"No se pudo importar el módulo de dispositivos:\n{str(e)}"
            )
            return False

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el módulo de dispositivos:\n{str(e)}"
            )
            return False

    def _launch_clients_module(self, user_data: Optional[Dict[str, Any]]) -> bool:
        """
        Launch the client manager module directly

        Args:
            user_data: User information dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_project_in_path()

            from src.modules.clients.client_manager_refactored import launch_client_manager

            parent_window = WindowRegistry.get_main_window()
            success = launch_client_manager(parent_window, user_data)

            debug_print(f"Clients module launched: {success}")
            return success

        except ImportError as e:
            messagebox.showerror(
                "Error de Importación",
                f"No se pudo importar el módulo de clientes:\n{str(e)}"
            )
            return False

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el módulo de clientes:\n{str(e)}"
            )
            return False

    def _launch_import_cotizaciones_module(
        self,
        user_data: Optional[Dict[str, Any]],
        db_connection
    ) -> bool:
        """
        Launch the cotizaciones import module directly using Clean Architecture

        Args:
            user_data: User information dictionary
            db_connection: Database connection object

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate admin permissions
            if not self._validate_admin_permission(user_data):
                return False

            # Ensure paths are set up
            src_path = os.path.join(self.project_root, 'src')
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            # Import using Clean Architecture entry point
            try:
                from src.modules.importacion import abrir_importador_cotizaciones
                debug_print("Successfully imported importacion module")
            except ImportError as e:
                messagebox.showerror(
                    "Error de Importación",
                    f"No se pudo importar el módulo de importación:\n{str(e)}"
                )
                return False

            # Get database connection
            try:
                db_connection = self._get_database_connection(db_connection)
            except Exception:
                return False

            # Get parent window
            parent_window = WindowRegistry.get_main_window()

            # Launch using the public API
            try:
                abrir_importador_cotizaciones(parent_window, db_connection, user_data)
                debug_print("Import module launched successfully")
                return True

            except Exception as create_error:
                messagebox.showerror(
                    "Error",
                    f"Error al crear el importador:\n{str(create_error)}"
                )
                import traceback
                traceback.print_exc()
                return False

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error inesperado al lanzar módulo de importación:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()
            return False

    def _launch_subprocess_module(
        self,
        module_key: str,
        user_data: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Launch a module using subprocess (for development mode)

        Args:
            module_key: Key identifying the module
            user_data: User information dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            self._update_session_activity()

            # Check if running as bundled executable
            is_frozen = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

            if is_frozen:
                # Running as PyInstaller bundle - use direct import
                debug_print(f"Detected bundled mode, using direct launch")
                return self._launch_direct_module(module_key, user_data)

            # Running in development - use subprocess
            # Check launcher script exists
            if not os.path.exists(self.launcher_script_path):
                messagebox.showerror(
                    "Error",
                    f"No se encontró el launcher: {self.launcher_script_path}"
                )
                return False

            # Prepare user data
            user_data_json = json.dumps(user_data, ensure_ascii=False) if user_data else ""

            # Prepare command
            cmd = [sys.executable, self.launcher_script_path, module_key]
            if user_data_json:
                cmd.append(user_data_json)

            debug_print(f"Launching: {module_key}")

            # Get module name for display
            module_info = self.get_module_by_key(module_key)
            module_title = module_info.get('title', 'Módulo') if module_info else 'Módulo'

            # Show loading indicator
            parent_window = WindowRegistry.get_main_window()
            loading = None
            if parent_window:
                try:
                    loading = LoadingIndicator.show(
                        parent_window,
                        f"Cargando {module_title}...",
                        timeout=10
                    )
                except Exception as e:
                    debug_print(f"Could not show loading indicator: {e}")

            # Launch subprocess in background thread
            def launch_and_close_loading():
                try:
                    if sys.platform.startswith('win'):
                        # Choose console visibility based on DEBUG flag
                        if SHOW_MODULE_CONSOLE:
                            # Show console window (useful for debugging)
                            debug_print(f"Launching {module_key} WITH console (debug mode)")
                            CREATE_NEW_CONSOLE = 0x00000010
                            process = subprocess.Popen(
                                cmd,
                                cwd=self.project_root,
                                creationflags=CREATE_NEW_CONSOLE
                            )
                        else:
                            # Hide console window (production mode)
                            debug_print(f"Launching {module_key} WITHOUT console")
                            CREATE_NO_WINDOW = 0x08000000
                            process = subprocess.Popen(
                                cmd,
                                cwd=self.project_root,
                                creationflags=CREATE_NO_WINDOW
                            )
                    else:
                        process = subprocess.Popen(cmd, cwd=self.project_root)

                    debug_print(f"Module {module_key} launched (PID: {process.pid})")

                    # ✅ IMPROVED: Wait until module window appears or timeout
                    self._wait_for_module_window(process.pid, module_key, max_wait=15)

                finally:
                    # Close loading indicator
                    if loading:
                        try:
                            loading.close()
                        except:
                            pass

            # Start launch thread
            launch_thread = threading.Thread(target=launch_and_close_loading, daemon=True)
            launch_thread.start()

            return True

        except FileNotFoundError as e:
            messagebox.showerror(
                "Error",
                f"No se pudo encontrar el archivo: {str(e)}"
            )
            return False

        except subprocess.SubprocessError as e:
            messagebox.showerror(
                "Error",
                f"Error al lanzar el módulo: {str(e)}"
            )
            return False

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el módulo '{module_key}': {str(e)}"
            )
            return False

    def launch_module(
        self,
        module_key: str,
        user_data: Optional[Dict[str, Any]] = None,
        db_connection=None
    ) -> bool:
        """
        Launch a module using the appropriate method

        Args:
            module_key: Key identifying the module to launch
            user_data: User information dictionary
            db_connection: Database connection (optional, used for some modules)

        Returns:
            True if module launched successfully, False otherwise
        """
        debug_print(f"Launching module: {module_key}")

        # Check for duplicate launches
        if not self._check_duplicate_launch(module_key):
            return False

        # Track module launch
        with self._track_module_launch(module_key):
            # Route to appropriate launcher based on module type
            if module_key == 'devices':
                return self._launch_device_module(user_data)

            elif module_key == 'clients':
                return self._launch_clients_module(user_data)

            elif module_key == 'import_cotizaciones':
                return self._launch_import_cotizaciones_module(user_data, db_connection)

            else:
                return self._launch_subprocess_module(module_key, user_data)

    def mark_module_closed(self, module_key: str):
        """Mark a module as closed so it can be opened again"""
        if module_key in self.open_modules:
            self.open_modules.discard(module_key)
            debug_print(f"Module {module_key} marked as closed")

    def validate_module_launcher(self) -> tuple[bool, List[str]]:
        """
        Validate that the module launcher exists

        Returns:
            Tuple of (exists, missing_files)
        """
        exists = os.path.exists(self.launcher_script_path)
        debug_print(f"Module launcher validated: {exists}")
        return exists, [] if exists else [self.launcher_script_path]

    def get_module_by_key(self, module_key: str) -> Optional[Dict[str, Any]]:
        """Get module definition by module key"""
        return next(
            (m for m in self.modules if m['module_key'] == module_key),
            None
        )

    def get_launcher_status(self) -> Dict[str, Any]:
        """Get detailed status information for debugging"""
        return {
            "launcher_exists": os.path.exists(self.launcher_script_path),
            "launcher_path": self.launcher_script_path,
            "project_root": self.project_root,
            "current_working_directory": os.getcwd(),
            "python_executable": sys.executable,
            "open_modules": list(self.open_modules)
        }