# -*- coding: utf-8 -*-
"""
DISFRULEG - Main Application Module (Modernized with CustomTkinter)
Dashboard principal del sistema - VERSIÓN MEJORADA
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import os
import platform

from src.config import (
    debug_print, get_app_config, USE_LOGIN, USE_SESSION_MANAGER
)
from src.theme import COLORS, FONTS
from src.ui.module_launcher import ModuleLauncher

class IconManager:
    """Gestor de iconos SVG con caché para máximo rendimiento"""
    
    def __init__(self):
        self.icons_cache = {}
        self.icons_path = "assets/icons"
        
        # Mapeo de claves a archivos SVG de Lucide
        self.icon_files = {
            # Módulos
            'receipts': 'file-text.svg',
            'pricing': 'tag.svg',
            'purchases': 'shopping-cart.svg',
            'inventory': 'shopping-cart.svg',
            'debts': 'credit-card.svg',
            'clients': 'users.svg',
            'users': 'user.svg',
            'reports': 'bar-chart-2.svg',
            'analytics': 'bar-chart-2.svg',
            'documents': 'folder.svg',
            'devices': 'smartphone.svg',
            'import_cotizaciones': 'file-up.svg',
            'ubicuoai': 'bot.svg',  # 🤖 Robot para IA
            
            # Header
            'notification': 'bell.svg',
            'settings': 'settings.svg',
            'moon': 'moon.svg',
            'sun': 'sun.svg',
            'logout': 'log-out.svg',
            'search': 'search.svg',
            
            # Adicionales
            'check': 'check-circle.svg',
            'alert': 'alert-circle.svg',
            'info': 'info.svg'
        }
    
    def load_icon(self, icon_name, size=(32, 32), color=None):
        """
        Carga un icono SVG y lo convierte a CTkImage
        
        Args:
            icon_name: Nombre del icono (key del diccionario)
            size: Tupla (ancho, alto) en píxeles
            color: Color opcional (no aplicable a SVG, pero se mantiene para futura implementación)
        
        Returns:
            CTkImage object o None si falla
        """
        cache_key = f"{icon_name}_{size[0]}x{size[1]}"
        
        # Retornar del caché si existe
        if cache_key in self.icons_cache:
            return self.icons_cache[cache_key]
        
        try:
            filename = self.icon_files.get(icon_name)
            if not filename:
                debug_print(f"Icon '{icon_name}' no encontrado en mapeo")
                return None
            
            icon_path = os.path.join(self.icons_path, filename)
            
            if not os.path.exists(icon_path):
                debug_print(f"Archivo de icono no existe: {icon_path}")
                return None
            
            # Cargar imagen con PIL
            light_image = Image.open(icon_path)
            dark_image = Image.open(icon_path)
            
            # Redimensionar manteniendo aspecto y usando LANCZOS para máxima calidad
            light_image = light_image.resize(size, Image.Resampling.LANCZOS)
            dark_image = dark_image.resize(size, Image.Resampling.LANCZOS)
            
            # Crear CTkImage (soporta modo claro/oscuro automáticamente)
            ctk_image = ctk.CTkImage(
                light_image=light_image,
                dark_image=dark_image,
                size=size
            )
            
            # Guardar en caché
            self.icons_cache[cache_key] = ctk_image
            
            debug_print(f"Icono '{icon_name}' cargado exitosamente")
            return ctk_image
            
        except Exception as e:
            debug_print(f"Error cargando icono '{icon_name}': {e}")
            return None
    
    def get_fallback_text(self, icon_name):
        """Retorna texto de respaldo si el icono no carga"""
        fallbacks = {
            'receipts': '📄',
            'pricing': '💰',
            'purchases': '🛒',
            'inventory': '🛒',
            'debts': '💳',
            'clients': '👥',
            'users': '👤',
            'reports': '📊',
            'analytics': '📊',
            'documents': '📁',
            'devices': '🖥️',
            'import_cotizaciones': '📥',
            'ubicuoai': '🤖',  # Robot IA
            'notification': '🔔',
            'settings': '⚙️',
            'moon': '🌙',
            'sun': '☀️',
            'logout': '⎋',
            'search': '🔍'
        }
        return fallbacks.get(icon_name, '◆')


class MainApplication:
    """Main application class - Modernized Dashboard"""
    
    def __init__(self):
        self.root = None
        self.user_data = None
        self.db_connection = None
        self.module_launcher = None
        self.config = get_app_config()
        self.search_var = None
        self.icon_manager = IconManager()
        self.current_platform = platform.system()
        
    def start(self):
        """Start the application"""
        debug_print("Starting application...")
        debug_print(f"Platform detected: {self.current_platform}")
        
        # Initialize module launcher
        self.module_launcher = ModuleLauncher()
        
        # Handle login
        if USE_LOGIN:
            if not self._handle_login():
                debug_print("Login cancelled")
                sys.exit(0)
        else:
            # Simulated user
            self.user_data = {
                'nombre_completo': 'Usuario de Prueba',
                'rol': 'admin',
                'username': 'test'
            }
            debug_print("Using simulated user")
        
        # Create main window
        try:
            self.create_main_window()
            self.run_main_loop()
        except Exception as e:
            debug_print(f"Error in main window execution: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _handle_login(self):
        """Handle user login"""
        try:
            debug_print("Importing login system...")
            from src.auth.login_window import show_login
            success, user_data = show_login(self.on_login_success)

            if success and user_data:
                self.user_data = user_data

                # ✅ VERIFICAR DISPONIBILIDAD DE BD (sin mantener conexión)
                try:
                    from src.database.conexion import get_last_error, db_available
                    from src.utils.resource_path import get_writable_path

                    # No longer hold connection - modules use pooling internally
                    debug_print(f"✅ BD disponible, módulos usarán connection pooling")

                    # Check if database connection failed
                    if not db_available:
                        log_file = get_writable_path('logs/database_connection.log')
                        error_msg = get_last_error() or "Error desconocido"

                        message = (
                            "⚠️ NO SE PUDO CONECTAR A LA BASE DE DATOS\n\n"
                            "La aplicación se abrirá pero no podrá cargar datos.\n\n"
                            f"Error: {error_msg}\n\n"
                            f"Los detalles completos se guardaron en:\n{log_file}\n\n"
                            "Posibles causas:\n"
                            "• Sin conexión a Internet\n"
                            "• Firewall bloqueando la conexión\n"
                            "• VirtualBox en modo NAT (cambiar a Bridge)\n"
                            "• Credenciales inválidas\n\n"
                            "¿Desea continuar sin base de datos?"
                        )

                        result = messagebox.askokcancel(
                            "Error de Conexión a Base de Datos",
                            message
                        )

                        if not result:
                            debug_print("Usuario canceló debido a error de BD")
                            return False

                except Exception as e:
                    debug_print(f"⚠️ Error obteniendo conexión: {e}")
                    self.db_connection = None
                    messagebox.showwarning(
                        "Advertencia",
                        f"Error al conectar con la base de datos:\n{e}\n\n"
                        "La aplicación continuará sin acceso a datos."
                    )

                debug_print(f"Login successful: {user_data}")
                return True
            else:
                return False
        except Exception as e:
            debug_print(f"Login error: {e}")
            messagebox.showerror("Error", f"Error en sistema de login: {e}")
            return False
    
    def on_login_success(self, user_data):
        """Callback executed when login is successful"""
        self.user_data = user_data
        debug_print(f"Login callback successful: {user_data['nombre_completo']}")
    
    def create_main_window(self):
        """Create main window with CustomTkinter - FULLSCREEN CROSS-PLATFORM"""
        debug_print("Creating main window...")
        
        try:
            self.root = ctk.CTk()
            self.root.withdraw()  # Ocultar ventana raíz inicialmente
            self.root.title(self.config['app_title'])
            
            # VENTANA COMPLETA MULTIPLATAFORMA
            self.set_fullscreen_window()
            
            # Permitir redimensionar
            self.root.resizable(True, True)
            
            # Configure close protocol
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Initialize variables after root window is created
            self.search_var = ctk.StringVar()
            
            # Initialize session manager
            if USE_SESSION_MANAGER:
                self._init_session_manager()
            
            # Create interface
            debug_print("Creating interface...")
            self.create_interface()
            
            # Bind resize event para ajustar contenido
            self.root.bind('<Configure>', self.on_window_resize)
            
        except Exception as e:
            debug_print(f"Error creating main window: {e}")
            raise
    
    def set_fullscreen_window(self):
        """Configura ventana completa según la plataforma"""
        try:
            # Obtener dimensiones de la pantalla ANTES de configurar
            self.root.update_idletasks()
            self.screen_width = self.root.winfo_screenwidth()
            self.screen_height = self.root.winfo_screenheight()

            debug_print(f"Screen dimensions: {self.screen_width}x{self.screen_height}")

            # Para Windows, usar geometry explícito Y state zoomed
            if self.current_platform == "Windows":
                debug_print("Applying Windows fullscreen...")
                # Primero establecer un tamaño visible
                self.root.geometry(f"1200x800+100+100")
                self.root.update()
                # Luego maximizar
                try:
                    self.root.state('zoomed')
                except Exception as e:
                    debug_print(f"Could not zoom window: {e}")

            elif self.current_platform == "Darwin":  # macOS
                debug_print("Applying macOS fullscreen...")
                self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
                try:
                    self.root.state('zoomed')
                except:
                    pass

            else:  # Linux
                debug_print("Applying Linux fullscreen...")
                self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
                try:
                    self.root.attributes('-zoomed', True)
                except:
                    try:
                        self.root.state('zoomed')
                    except:
                        pass

        except Exception as e:
            debug_print(f"Error setting fullscreen: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: Usar dimensiones generosas
            self.root.geometry("1200x800+100+100")
    
    def on_window_resize(self, event):
        """Callback cuando se redimensiona la ventana"""
        # Aquí puedes ajustar elementos dinámicamente si es necesario
        pass
    
    def _init_session_manager(self):
        """Initialize session manager"""
        try:
            debug_print("Initializing session manager...")
            from src.auth.session_manager import session_manager
            session_manager.add_callback(self.handle_session_event)
            session_manager.start_session(self.user_data)
        except Exception as e:
            debug_print(f"Session manager error: {e}")
            messagebox.showwarning("Advertencia", f"Session manager no disponible: {e}")
    
    def create_interface(self):
        """Create main interface with modern design"""
        debug_print("Creating interface components...")
        
        try:
            # Header
            debug_print("Creating header...")
            self.create_header()
            
            # Welcome section
            debug_print("Creating welcome section...")
            self.create_welcome_section()
            
            # Main content (modules grid)
            debug_print("Creating main content...")
            self.create_main_content()
            
            # Status bar
            debug_print("Creating status bar...")
            self.create_status_bar()
            
            debug_print("Interface created successfully")
            
        except Exception as e:
            debug_print(f"Error creating interface: {e}")
            raise
    
    def create_header(self):
        """Create modern header with synchronized user avatar"""
        header_frame = ctk.CTkFrame(self.root, fg_color=("#1a1a1a", "#1a1a1a"), height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=0)
        
        # Left: Logo and Title
        left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        left_frame.pack(side="left", fill="y")
        
        logo_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        logo_frame.pack(side="left", padx=(0, 15))
        
        # Logo
        ctk.CTkLabel(
            logo_frame,
            text="📈",
            font=("Arial", 28)
        ).pack()
        
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="DISFRULEG",
            font=("Arial", 16, "bold"),
            text_color="white",
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Sistema de Gestión",
            font=("Arial", 10),
            text_color="gray60",
            anchor="w"
        ).pack(anchor="w")
        
        # Center: Search bar
        center_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        center_frame.pack(side="left", fill="x", expand=True, padx=40)
        
        search_frame = ctk.CTkFrame(center_frame, fg_color=("#2a2a2a", "#2a2a2a"), corner_radius=25)
        search_frame.pack(fill="x", pady=15)
        
        # Search icon
        search_icon = self.icon_manager.load_icon('search', size=(18, 18))
        if search_icon:
            ctk.CTkLabel(
                search_frame,
                text="",
                image=search_icon,
                compound="left"
            ).pack(side="left", padx=(15, 5))
        else:
            ctk.CTkLabel(
                search_frame,
                text="🔍",
                font=("Arial", 14),
                text_color="gray"
            ).pack(side="left", padx=(15, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Buscar módulos...",
            fg_color="transparent",
            border_width=0,
            font=("Arial", 12),
            text_color="white"
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15), pady=10)
        self.search_var.trace("w", lambda *args: self.filter_modules())
        
        # Right: User info and logout
        right_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        right_frame.pack(side="right")
        
        # ========================================
        # 🎨 USER AVATAR (Sincronizado con BD)
        # ========================================
        if self.user_data:
            user_name = self.user_data.get('nombre_completo', 'Usuario')
            username = self.user_data.get('username', '')
            initials = ''.join([n[0].upper() for n in user_name.split()[:2]])
            
            # ✅ OBTENER DATOS ACTUALIZADOS DE LA BD
            avatar_image = None
            avatar_color = COLORS['success']  # Default color
            
            try:
                from src.auth.auth_manager import AuthManager
                auth_manager = AuthManager()
                avatar_data = auth_manager.get_user_avatar_data(username)
                
                if avatar_data:
                    avatar_image = avatar_data.get('imagen')
                    avatar_color = avatar_data.get('color', COLORS['success'])
                    
                    # 🔍 DEBUG: Ver qué datos llegan
                    debug_print(f"✅ Avatar data loaded:")
                    debug_print(f"   - Username: {username}")
                    debug_print(f"   - Color: {avatar_color}")
                    debug_print(f"   - Has image: {bool(avatar_image)}")
                    if avatar_image:
                        debug_print(f"   - Image size: {len(avatar_image)} bytes")
                else:
                    debug_print(f"⚠️ No avatar data found for user: {username}")
                    
            except Exception as e:
                debug_print(f"⚠️ Error loading avatar data: {e}")
                import traceback
                traceback.print_exc()
            
            if avatar_image:
                # ✅ Si hay imagen, mostrarla en círculo perfecto
                try:
                    from PIL import Image, ImageDraw
                    import io
                    
                    # Cargar imagen desde bytes
                    pil_image = Image.open(io.BytesIO(avatar_image))
                    
                    # Convertir a RGBA
                    if pil_image.mode != 'RGBA':
                        pil_image = pil_image.convert('RGBA')
                    
                    # Redimensionar
                    pil_image = pil_image.resize((45, 45), Image.Resampling.LANCZOS)
                    
                    # ✅ CREAR MÁSCARA CIRCULAR PERFECTA
                    mask = Image.new('L', (45, 45), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, 45, 45), fill=255)
                    
                    # Aplicar máscara
                    output = Image.new('RGBA', (45, 45), (0, 0, 0, 0))
                    output.paste(pil_image, (0, 0))
                    output.putalpha(mask)
                    
                    # Crear CTkImage
                    ctk_image = ctk.CTkImage(
                        light_image=output,
                        dark_image=output,
                        size=(45, 45)
                    )
                    
                    # ✅ Botón CON FONDO TRANSPARENTE (sin cuadrado)
                    user_button = ctk.CTkButton(
                        right_frame,
                        text="",
                        image=ctk_image,
                        width=45,
                        height=45,
                        corner_radius=25,
                        fg_color="transparent",
                        hover_color=("#2a2a2a", "#2a2a2a"),
                        border_width=0,
                        command=self.show_user_menu
                    )
                    
                    debug_print("✅ Avatar image displayed successfully")
                    
                except Exception as e:
                    debug_print(f"⚠️ Error displaying avatar image: {e}")
                    # Fallback a iniciales
                    user_button = ctk.CTkButton(
                        right_frame,
                        text=initials,
                        width=45,
                        height=45,
                        corner_radius=25,
                        fg_color=avatar_color,
                        hover_color=self._darken_color(avatar_color),
                        font=("Arial", 14, "bold"),
                        text_color="white",
                        border_width=0,
                        command=self.show_user_menu
                    )
            else:
                # ✅ Si NO hay imagen, usar iniciales con color
                user_button = ctk.CTkButton(
                    right_frame,
                    text=initials,
                    width=45,
                    height=45,
                    corner_radius=25,
                    fg_color=avatar_color,
                    hover_color=self._darken_color(avatar_color),
                    font=("Arial", 14, "bold"),
                    text_color="white",
                    border_width=0,
                    command=self.show_user_menu
                )
            
            user_button.pack(side="left", padx=(0, 10))
        
        # ========================================
        # 🚪 LOGOUT BUTTON
        # ========================================
        logout_icon = self.icon_manager.load_icon('logout', size=(20, 20))
        
        if logout_icon:
            logout_btn = ctk.CTkButton(
                right_frame,
                text="",
                image=logout_icon,
                width=35,
                height=35,
                corner_radius=8,
                fg_color="transparent",
                hover_color=COLORS['accent'],
                command=self.logout
            )
        else:
            logout_btn = ctk.CTkButton(
                right_frame,
                text="⎋",
                width=35,
                height=35,
                corner_radius=8,
                fg_color="transparent",
                hover_color=COLORS['accent'],
                font=("Arial", 18),
                command=self.logout
            )
        
        logout_btn.pack(side="left", padx=5)
    
    def _darken_color(self, hex_color, factor=0.8):
        """Darken a hex color for hover effect"""
        try:
            # Remove '#' if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Darken
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return COLORS['success_hover']
    
    def show_user_menu(self):
        """Show user menu (placeholder)"""
        pass
    
    def create_welcome_section(self):
        """Create welcome section"""
        welcome_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        welcome_frame.pack(fill="x", padx=30, pady=(20, 15))
        
        user_name = self.user_data.get('nombre_completo', 'Usuario') if self.user_data else 'Usuario'
        first_name = user_name.split()[0] if user_name else 'Usuario'
        
        ctk.CTkLabel(
            welcome_frame,
            text=f"Bienvenido, {first_name}",
            font=("Arial", 24, "bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            welcome_frame,
            text="Selecciona un módulo para comenzar a trabajar",
            font=("Arial", 12),
            text_color="gray60",
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))
    
    def create_main_content(self):
        """Create main content with scrollable modules grid"""
        try:
            # Main container with scroll
            main_frame = ctk.CTkScrollableFrame(
                self.root,
                fg_color="transparent"
            )
            main_frame.pack(fill="both", expand=True, padx=30, pady=(0, 15))
            
            # Create modules grid
            self.modules_container = main_frame
            self.create_modules_grid(main_frame)
                
        except Exception as e:
            debug_print(f"Error creating main content: {e}")
            raise
    
    def create_modules_grid(self, parent):
        """Create modern modules grid with cards and SVG icons"""
        debug_print("Creating modules grid...")
        
        try:
            # Get available modules for user role
            user_role = self.user_data.get('rol', 'usuario') if self.user_data else 'usuario'
            available_modules = self.module_launcher.get_available_modules(user_role)
            
            debug_print(f"Found {len(available_modules)} modules for role: {user_role}")
            
            # Store for filtering
            self.all_modules = available_modules
            
            # Create grid
            max_cols = 3
            row = 0
            col = 0
            
            for i, module in enumerate(available_modules):
                debug_print(f"Creating module {i+1}: {module.get('title', 'Unknown')}")
                self.create_module_card(parent, module, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Configure columns
            for i in range(max_cols):
                parent.grid_columnconfigure(i, weight=1, uniform="column")
                
            debug_print("Modules grid created successfully")
            
        except Exception as e:
            debug_print(f"Error creating modules grid: {e}")
            raise
    
    def create_module_card(self, parent, module, row, col):
        """Create a modern module card with SVG icon"""
        # Get module key - support multiple formats
        module_key = module.get('key') or module.get('module_key') or module.get('name', 'unknown')
        title = module.get('title') or module.get('name', 'Módulo')
        description = module.get('description', 'Módulo del sistema')
        icon_name = module.get('icon', 'documents')
        
        # Get icon color based on module
        icon_bg = self.get_module_color(module_key)
        
        debug_print(f"Creating card for module: {module_key}")
        
        # Module card
        card = ctk.CTkFrame(
            parent,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=20,
            border_width=0
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Card content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Icon button with SVG
        icon_frame = ctk.CTkFrame(
            content,
            fg_color=icon_bg,
            corner_radius=18,
            width=80,
            height=80
        )
        icon_frame.pack(anchor="w", pady=(0, 20))
        icon_frame.pack_propagate(False)
        
        # Load SVG icon
        icon_image = self.icon_manager.load_icon(module_key, size=(40, 40))
        
        if icon_image:
            icon_label = ctk.CTkLabel(
                icon_frame,
                text="",
                image=icon_image,
                compound="center"
            )
        else:
            # Fallback a emoji si no carga el SVG
            fallback = self.icon_manager.get_fallback_text(module_key)
            icon_label = ctk.CTkLabel(
                icon_frame,
                text=fallback,
                font=("Arial", 32),
                text_color="white"
            )
        
        icon_label.pack(expand=True)
        
        # Title
        ctk.CTkLabel(
            content,
            text=title,
            font=("Arial", 18, "bold"),
            text_color="white",
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))
        
        # Description
        ctk.CTkLabel(
            content,
            text=description,
            font=("Arial", 11),
            text_color="gray60",
            anchor="w",
            wraplength=280,
            justify="left"
        ).pack(anchor="w")
        
        # Make card clickable
        def on_enter(e):
            card.configure(fg_color=("#333333", "#333333"))
            
        def on_leave(e):
            card.configure(fg_color=("#2a2a2a", "#2a2a2a"))
        
        def on_click(e):
            self.launch_module(module_key)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Button-1>", on_click)
        
        # Make all children clickable too
        for widget in [content, icon_frame, icon_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
    
    def get_module_color(self, module_key):
        """Get color for module icon based on key"""
        colors = {
            'receipts': '#FF00A0',           # Fucsia fuerte
            'pricing': '#FF8C00',            # Naranja brillante
            'purchases': '#20B2AA',          # Azul verdoso (teal intenso)
            'inventory': '#20B2AA',          # Teal (alias)
            'debts': '#FF4040',              # Rojo coral
            'clients': '#00BFFF',            # Azul turquesa vibrante
            'users': '#8A2BE2',              # Morado eléctrico
            'reports': '#FFD700',            # Dorado brillante
            'analytics': '#FFD700',          # Dorado (alias)
            'documents': '#14b8a6',          # Teal
            'devices': '#32CD32',            # Verde lima neón
            'import_cotizaciones': '#FF1493' # Deep Pink
        }
        return colors.get(module_key, '#6b7280')  # Gray default
    
    def filter_modules(self):
        """Filter modules based on search"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            # Si está vacío, recrear todos los módulos
            for widget in self.modules_container.winfo_children():
                widget.destroy()
            
            max_cols = 3
            row = 0
            col = 0
            
            for module in self.all_modules:
                self.create_module_card(self.modules_container, module, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            return
        
        # Clear and recreate filtered grid
        for widget in self.modules_container.winfo_children():
            widget.destroy()
        
        max_cols = 3
        row = 0
        col = 0
        
        for module in self.all_modules:
            title = (module.get('title') or '').lower()
            description = (module.get('description') or '').lower()
            
            if search_text in title or search_text in description:
                self.create_module_card(self.modules_container, module, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_frame = ctk.CTkFrame(
            self.root, 
            fg_color=("#1a1a1a", "#1a1a1a"), 
            height=40
        )
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        status_content = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        status_content.pack(fill="both", expand=True, padx=30, pady=0)
        
        # Left: Status indicator
        left_frame = ctk.CTkFrame(status_content, fg_color="transparent")
        left_frame.pack(side="left")
        
        ctk.CTkLabel(
            left_frame,
            text="●",
            font=("Arial", 12),
            text_color=COLORS['success']
        ).pack(side="left", padx=(0, 8))
        
        self.status_label = ctk.CTkLabel(
            left_frame,
            text="Sesión activa",
            font=("Arial", 11),
            text_color="gray60"
        )
        self.status_label.pack(side="left")
        
        # Right: User info
        if self.user_data:
            user_name = self.user_data.get('nombre_completo', 'Usuario')
            role = self.user_data.get('rol', 'usuario')
            
            ctk.CTkLabel(
                status_content,
                text=f"Usuario: {user_name} ({role.upper()})",
                font=("Arial", 11),
                text_color="gray60"
            ).pack(side="right")
    
    def update_status(self, text):
        """Update status bar text"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=text)
    
    def launch_module(self, module_key):
        """Launch a module"""
        try:
            debug_print(f"Launching module: {module_key}")
            self.update_status(f"Abriendo módulo...")
            
            # Modules now use connection pooling internally - no need to pass connection
            success = self.module_launcher.launch_module(
                module_key,
                self.user_data,
                None  # Modules use pooling internally, pass None
            )
            
            if success:
                self.update_status(f"Sesión activa")
            else:
                self.update_status(f"Error abriendo módulo")
                
            return success
            
        except Exception as e:
            debug_print(f"Error launching module {module_key}: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al abrir módulo: {str(e)}")
            self.update_status(f"Error")
            return False

    def handle_session_event(self, event_type, user_data):
        """Handle session events"""
        debug_print(f"Session event: {event_type}")
    
        if event_type == 'session_timeout':
            messagebox.showwarning("Sesión Expirada", 
                                 "Su sesión ha expirado por inactividad.")
            self.force_logout()
        elif event_type == 'session_ended':
            self.close_application()
    
    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Cerrar Sesión", 
                             "¿Está seguro que desea cerrar su sesión?"):
            self.force_logout()
    
    def force_logout(self):
        """Force logout"""
        debug_print("Forcing logout...")

        if USE_SESSION_MANAGER:
            try:
                from src.auth.session_manager import session_manager
                session_manager.end_session()
            except:
                pass

        if USE_LOGIN:
            try:
                from src.database.db_manager import db_manager
                db_manager.close_connection()
            except:
                pass

        # Fallback: Return connection to pool if somehow still set
        if hasattr(self, 'db_connection') and self.db_connection is not None:
            try:
                from src.database.conexion import return_connection
                return_connection(self.db_connection)
                debug_print("Returned db_connection to pool")
            except:
                pass

        self.close_application()
    
    def close_application(self):
        """Close application"""
        debug_print("Closing application...")
        
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except:
            pass
        
        sys.exit(0)
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir del sistema?"):
            self.force_logout()
    
    def run_main_loop(self):
        """Run main application loop"""
        debug_print("Starting main loop...")

        if self.root:
            import time
            time.sleep(1)
            debug_print(f"Window exists: {self.root.winfo_exists()}")
            self.root.deiconify()  # Mostrar ventana
            self.root.lift()  # Bring to front
            self.root.focus_force()  # Force focus
            debug_print("Window should now be visible - entering mainloop")
            self.root.mainloop()
            debug_print("Mainloop exited")


# For testing
if __name__ == "__main__":
    app = MainApplication()
    app.start()