import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime
import os
from pathlib import Path
import platform
import tkinter.font as tkfont
import time
from PIL import Image
from src.security.device_manager import device_manager
import sys
import logging

logger = logging.getLogger(__name__)

# AJUSTE PARA macOS - Detectar y ajustar scaling
if platform.system() == "Darwin":  # macOS
    try:
        pass 
    except:
        pass

# Importación segura del spinner con función helper
try:
    from src.ui.animated_components import LoadingSpinner, create_spinner_safe
    SPINNER_AVAILABLE = True
except ImportError as e:
    SPINNER_AVAILABLE = False
    print(f"[WARNING] LoadingSpinner no disponible: {e}")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

try:
    from src.database.db_manager import db_manager
    from src.auth.session_manager import session_manager
    from src.database.conexion import db_available
    DB_AVAILABLE = db_available
except ImportError:
    print("Warning: DB components not available. Running in simulated mode.")
    DB_AVAILABLE = False

class ModernLoginWindow:
    def __init__(self, on_success_callback=None):
        self.root = ctk.CTk()
        
        self.on_success_callback = on_success_callback
        self.login_successful = False
        self.user_data = None
        
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.remember_var = ctk.BooleanVar()
        self.theme_mode = ctk.StringVar(value=ctk.get_appearance_mode().lower())
        
        # ✅✅✅ SISTEMA DE GESTIÓN DE CALLBACKS
        self._after_callbacks = set()
        self._is_closing = False
        self._time_update_id = None
        
        # 🎨 PALETA CONSISTENTE CON LA APP PRINCIPAL
        self.colors = {
            'bg_primary': '#1E1E1E',         # Negro gris principal (igual que la app)
            'bg_secondary': '#2B2B2B',       # Card principal (gris oscuro)
            'bg_tertiary': '#333333',        # Elementos hover
            'border_subtle': '#3A3A3A',      # Bordes sutiles
            'border_focus': '#4A4A4A',       # Bordes en focus
            
            'primary': '#1F7A5C',            # Verde apagado
            'primary_hover': '#1A6550',      # Verde más oscuro
            
            'accent': '#E84855',             # Rojo vibrante (como el botón JA)
            'accent_hover': '#D63A47',       # Rojo más oscuro
            'accent_light': '#2A1F20',       # Fondo rojo suave
            
            'success': '#1F7A5C',
            'error': '#E74C3C',
            
            'text_primary': '#FFFFFF',       # Texto blanco puro
            'text_secondary': '#A0A0A0',     # Gris claro
            'text_muted': '#6B6B6B',         # Gris medio
            
            'ubicuo_green': '#00D9A3',       # Verde tecnológico para Ubicuo Studio
            
            'overlay_bg_dark': '#1A1A1A',    # Overlay oscuro
            'overlay_bg_light': '#FAFAFA'
        }
        
        # Inicializar atributos de UI a None
        self.spinner_loading = None
        self.overlay = None
        self.loading_label = None
        self.time_label = None
        
        # Iconos
        self.sol_icon = None
        self.luna_icon = None
        self.mostrar_icon = None
        self.ocultar_icon = None
        
        # Cargar iconos
        self._load_icons()

        self.setup_window()
        self.create_interface()
        self.center_window()
        self.load_remembered_credentials()
    
    # ✅✅✅ MÉTODOS PARA GESTIÓN SEGURA DE CALLBACKS
    def _schedule_after(self, delay, callback):
        """Programa un after() y lo registra para limpieza posterior"""
        if self._is_closing:
            return None
        
        try:
            after_id = self.root.after(delay, callback)
            self._after_callbacks.add(after_id)
            return after_id
        except:
            return None
    
    def _cancel_all_callbacks(self):
        """Cancela todos los callbacks pendientes"""
        # Cancelar callbacks registrados
        for after_id in list(self._after_callbacks):
            try:
                self.root.after_cancel(after_id)
            except:
                pass
        self._after_callbacks.clear()
        
        # Obtener y cancelar callbacks huérfanos de tkinter/CustomTkinter
        try:
            after_ids = self.root.tk.call('after', 'info')
            if after_ids:
                for after_id in after_ids:
                    try:
                        self.root.after_cancel(after_id)
                    except:
                        pass
        except:
            pass
        
        # Cancelar específicamente el update_time
        if self._time_update_id is not None:
            try:
                self.root.after_cancel(self._time_update_id)
            except:
                pass
            self._time_update_id = None
        
    def _load_icons(self):
        """Carga todos los iconos necesarios para la ventana."""
        try:
            # Iconos de tema
            sol_path = self.get_asset_path('icons/SOL.png')
            luna_path = self.get_asset_path('icons/LUNA.png')
            if sol_path and luna_path and os.path.exists(sol_path) and os.path.exists(luna_path):
                sol_img = Image.open(sol_path).resize((20, 20), Image.Resampling.LANCZOS)
                luna_img = Image.open(luna_path).resize((20, 20), Image.Resampling.LANCZOS)
                self.sol_icon = ctk.CTkImage(light_image=sol_img, dark_image=sol_img, size=(20, 20))
                self.luna_icon = ctk.CTkImage(light_image=luna_img, dark_image=luna_img, size=(20, 20))

            # Iconos de visibilidad de contraseña
            mostrar_path = self.get_asset_path('icons/mostrar.png')
            ocultar_path = self.get_asset_path('icons/ocultar.png')
            if mostrar_path and ocultar_path and os.path.exists(mostrar_path) and os.path.exists(ocultar_path):
                mostrar_img = Image.open(mostrar_path).resize((20, 20), Image.Resampling.LANCZOS)
                ocultar_img = Image.open(ocultar_path).resize((20, 20), Image.Resampling.LANCZOS)
                self.mostrar_icon = ctk.CTkImage(light_image=mostrar_img, dark_image=mostrar_img, size=(20, 20))
                self.ocultar_icon = ctk.CTkImage(light_image=ocultar_img, dark_image=ocultar_img, size=(20, 20))
        except Exception as e:
            print(f"Error cargando iconos: {e}")
            
    def setup_window(self):
        self.root.title("DISFRULEG - Iniciar Sesión")
        
        # 🎯 CONFIGURACIÓN RESPONSIVE PARA LOGIN
        login_config = {
            'width_ratio': 0.40,
            'height_ratio': 0.85,
            'max_width': 650,
            'max_height': 850,
            'min_width': 550,
            'min_height': 750
        }
        
        # Calcular dimensiones responsive
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        width = int(screen_width * login_config['width_ratio'])
        height = int(screen_height * login_config['height_ratio'])
        
        # Aplicar límites
        width = max(login_config['min_width'], min(width, login_config['max_width']))
        height = max(login_config['min_height'], min(height, login_config['max_height']))
        
        # Centrar en pantalla
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(login_config['min_width'], login_config['min_height'])
        self.root.resizable(True, True)
        self.root.configure(fg_color=self.colors['bg_primary'])
        
        logger.info(f"✅ Login window responsive: {width}x{height}")
        
        try:
            icon_path_ico = self.get_asset_path('logos/ubicuo_icon.ico')
            icon_path_icns = self.get_asset_path('logos/ubicuo_icon.icns')
            icon_path_png = self.get_asset_path('logos/ubicuo_icon.png')
            
            if platform.system() == "Windows" and icon_path_ico and os.path.exists(icon_path_ico):
                self.root.iconbitmap(icon_path_ico)
            elif platform.system() == "Darwin" and icon_path_icns and os.path.exists(icon_path_icns):
                 self.root.iconbitmap(icon_path_icns)
            elif platform.system() == "Linux" and icon_path_png and os.path.exists(icon_path_png):
                self.root.iconphoto(True, Image.open(icon_path_png))

        except Exception as e:
            print(f"No se pudo cargar el icono de la ventana: {e}")
        
        self.root.transient()
        self.root.grab_set()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def get_asset_path(self, relative_path):
        """Busca assets en diferentes ubicaciones (desarrollo y empaquetado)"""
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
                asset_path = Path(base_path) / 'assets' / relative_path
                if asset_path.exists():
                    return str(asset_path)
            
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            asset_path = project_root / 'assets' / relative_path
            if asset_path.exists():
                return str(asset_path)

            asset_path = Path.cwd() / 'assets' / relative_path
            if asset_path.exists():
                return str(asset_path)
            
        except Exception as e:
            print(f"Error buscando asset '{relative_path}': {e}")
        
        return None
        
    def center_window(self):
        """Ya no es necesario - el centrado se hace en setup_window()"""
        pass
        
    def create_interface(self):
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=25)
        
        self.create_header(main_frame)
        self.create_login_card(main_frame)
        self.create_footer(main_frame)
        
    def create_header(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(side="left")
        
        try:
            logo_path = self.get_asset_path('logos/ubicuo_logo.png')
            if logo_path and os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                self.ubicuo_photo = ctk.CTkImage(
                    light_image=logo_img,
                    dark_image=logo_img,
                    size=(24, 24)
                )
                ctk.CTkLabel(logo_frame, image=self.ubicuo_photo, text="").pack(side="left", padx=(0, 8))
        except Exception as e:
            print(f"Error cargando logo Ubicuo: {e}")
        
        ctk.CTkLabel(
            logo_frame,
            text="UBICUO STUDIO",
            font=("Segoe UI", 10),
            text_color=self.colors['ubicuo_green']
        ).pack(side="left")
        
        theme_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_frame.pack(side="right")
        
        self.time_label = ctk.CTkLabel(
            theme_frame,
            text="",
            font=("Segoe UI", 10),
            text_color=self.colors['text_muted']
        )
        self.time_label.pack(side="left", padx=12)
        
        # Iniciar actualización del reloj
        self.update_time()
        
    def create_login_card(self, parent):
        card_container = ctk.CTkFrame(parent, fg_color="transparent")
        card_container.pack(fill="both", expand=True, pady=3)
        
        # Card con efecto glassmorphism
        self.login_card = ctk.CTkFrame(
            card_container, 
            corner_radius=24,
            border_width=1,
            border_color=self.colors['border_subtle'],
            fg_color=self.colors['bg_secondary']
        )
        self.login_card.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Espaciador superior reducido
        ctk.CTkFrame(self.login_card, fg_color="transparent", height=25).pack()
        
        # Logo DISFRULEG con más protagonismo
        logo_container = ctk.CTkFrame(self.login_card, fg_color="transparent")
        logo_container.pack(pady=(0, 20))
        
        self.disfruleg_photo = None
        try:
            logo_filename = 'disfruleg_rojo.png' if self.theme_mode.get() == "dark" else 'disfruleg_negro.png'
            logo_path = self.get_asset_path(f'logos/{logo_filename}')
            
            if logo_path and os.path.exists(logo_path):
                logo_img = Image.open(logo_path).resize((350, 70), Image.Resampling.LANCZOS)
                self.disfruleg_photo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(350, 70))
                self.disfruleg_label = ctk.CTkLabel(logo_container, image=self.disfruleg_photo, text="")
                self.disfruleg_label.pack()
            else:
                self.disfruleg_label = ctk.CTkLabel(
                    logo_container, 
                    text="DISFRULEG", 
                    font=("Segoe UI", 38, "bold"), 
                    text_color=self.colors['text_primary']
                )
                self.disfruleg_label.pack()
        except Exception as e:
            print(f"Error cargando logo DISFRULEG: {e}")
            self.disfruleg_label = ctk.CTkLabel(
                logo_container, 
                text="DISFRULEG", 
                font=("Segoe UI", 38, "bold"), 
                text_color=self.colors['text_primary']
            )
            self.disfruleg_label.pack()
        
        # Subtítulo minimalista
        ctk.CTkLabel(
            self.login_card, 
            text="Iniciar Sesión", 
            font=("Segoe UI", 16),
            text_color=self.colors['text_secondary']
        ).pack(pady=(0, 25))
        
        # Form frame
        form_frame = ctk.CTkFrame(self.login_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=50, pady=0)
        
        # Campo Usuario
        ctk.CTkLabel(
            form_frame, 
            text="Usuario", 
            font=("Segoe UI", 11),
            text_color=self.colors['text_secondary'],
            anchor="w"
        ).pack(fill="x", pady=(0, 8))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.username_var,
            height=44,
            font=("Segoe UI", 12),
            placeholder_text="Ingrese su usuario",
            corner_radius=12,
            border_width=1,
            border_color=self.colors['border_subtle'],
            fg_color=self.colors['bg_tertiary'],
            text_color=self.colors['text_primary'],
            placeholder_text_color=self.colors['text_muted']
        )
        self.username_entry.pack(fill="x", pady=(0, 20))
        self.username_entry.bind("<FocusIn>", lambda e: self.on_entry_focus(self.username_entry, True))
        self.username_entry.bind("<FocusOut>", lambda e: self.on_entry_focus(self.username_entry, False))
        
        # Campo Contraseña
        ctk.CTkLabel(
            form_frame, 
            text="Contraseña", 
            font=("Segoe UI", 11),
            text_color=self.colors['text_secondary'],
            anchor="w"
        ).pack(fill="x", pady=(0, 8))
        
        password_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_container.pack(fill="x", pady=(0, 20))
        
        self.password_entry = ctk.CTkEntry(
            password_container,
            textvariable=self.password_var,
            height=44,
            font=("Segoe UI", 12),
            placeholder_text="Ingrese su contraseña",
            show="●",
            corner_radius=12,
            border_width=1,
            border_color=self.colors['border_subtle'],
            fg_color=self.colors['bg_tertiary'],
            text_color=self.colors['text_primary'],
            placeholder_text_color=self.colors['text_muted']
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.password_entry.bind("<FocusIn>", lambda e: self.on_entry_focus(self.password_entry, True))
        self.password_entry.bind("<FocusOut>", lambda e: self.on_entry_focus(self.password_entry, False))
        
        self.show_pass_btn = ctk.CTkButton(
            password_container,
            image=self.ocultar_icon if self.ocultar_icon else None,
            text="" if self.ocultar_icon else "👁",
            width=44,
            height=44,
            font=("Arial", 14) if not self.ocultar_icon else None,
            command=self.toggle_password_visibility,
            fg_color=self.colors['bg_tertiary'],
            hover_color=self.colors['border_focus'],
            corner_radius=12,
            border_width=1,
            border_color=self.colors['border_subtle']
        )
        self.show_pass_btn.pack(side="right")
        
        # Checkbox con estilo minimalista
        remember_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        remember_frame.pack(fill="x", pady=(0, 25))
        
        self.remember_check = ctk.CTkCheckBox(
            remember_frame,
            text="Recordar credenciales",
            variable=self.remember_var,
            font=("Segoe UI", 10),
            text_color=self.colors['text_secondary'],
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            border_color=self.colors['border_subtle']
        )
        self.remember_check.pack(side="left")
        
        # Botón de login premium
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="INICIAR SESIÓN",
            command=self.handle_login,
            height=48,
            font=("Segoe UI", 12, "bold"),
            corner_radius=12,
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            border_width=0,
            text_color=self.colors['text_primary']
        )
        self.login_btn.pack(fill="x", pady=(0, 15))
        
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=("Segoe UI", 10),
            text_color=self.colors['error'],
            wraplength=350
        )
        self.status_label.pack(pady=(5, 15))
        
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        self.username_entry.focus_set()
        
    def on_entry_focus(self, entry, focused):
        """Efecto de focus en inputs"""
        if focused:
            entry.configure(border_color=self.colors['accent'])
        else:
            entry.configure(border_color=self.colors['border_subtle'])
        
    def create_footer(self, parent):
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(15, 5))
        
        # Línea decorativa sutil
        separator = ctk.CTkFrame(footer_frame, fg_color=self.colors['border_subtle'], height=1)
        separator.pack(fill="x", pady=(0, 12))
        
        # Texto de seguridad más discreto
        ctk.CTkLabel(
            footer_frame, 
            text="Sistema de Autenticación Segura", 
            font=("Segoe UI", 9), 
            text_color=self.colors['text_muted']
        ).pack(pady=(0, 6))
        
        # Copyright con más énfasis en Ubicuo Studio
        copyright_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        copyright_frame.pack()
        
        ctk.CTkLabel(
            copyright_frame,
            text=f"© {datetime.now().year} DISFRULEG",
            font=("Segoe UI", 9),
            text_color=self.colors['text_muted']
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            copyright_frame,
            text="•",
            font=("Segoe UI", 9),
            text_color=self.colors['text_muted']
        ).pack(side="left", padx=3)
        
        ctk.CTkLabel(
            copyright_frame,
            text="Desarrollado por",
            font=("Segoe UI", 9),
            text_color=self.colors['text_muted']
        ).pack(side="left", padx=(3, 5))
        
        # Ubicuo Studio destacado
        ctk.CTkLabel(
            copyright_frame,
            text="Ubicuo Studio",
            font=("Segoe UI", 10, "bold"),
            text_color=self.colors['ubicuo_green']
        ).pack(side="left")
        
    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self.theme_mode.set(new_mode)
        
        if self.sol_icon and self.luna_icon:
            self.theme_label.configure(image=self.sol_icon if new_mode == "light" else self.luna_icon)
        
        if self.disfruleg_photo:
            try:
                logo_filename = 'disfruleg_rojo.png' if new_mode == "dark" else 'disfruleg_negro.png'
                logo_path = self.get_asset_path(f'logos/{logo_filename}')
                
                if logo_path and os.path.exists(logo_path):
                    logo_img = Image.open(logo_path).resize((350, 70), Image.Resampling.LANCZOS)
                    self.disfruleg_photo.configure(light_image=logo_img, dark_image=logo_img)
            except Exception as e:
                print(f"Error actualizando logo: {e}")
        
        if self.overlay:
            overlay_fg_color = (self.colors['overlay_bg_light'], self.colors['overlay_bg_dark'])
            self.overlay.configure(fg_color=overlay_fg_color)
        
        if SPINNER_AVAILABLE and self.spinner_loading:
            try:
                self.spinner_loading.update_theme()
            except:
                pass
        
    def update_time(self):
        """✅ Actualiza el reloj - VERSIÓN ULTRA SEGURA"""
        if self._is_closing:
            return
        
        try:
            if not hasattr(self, 'time_label'):
                return
            
            if not hasattr(self, 'root'):
                return
                
            if not self.root.winfo_exists():
                return
            
            if not self.time_label or not self.time_label.winfo_exists():
                return
        except:
            return
        
        try:
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%d/%m/%Y")
            self.time_label.configure(text=f"{date_str} • {time_str}")
            
            if not self._is_closing:
                self._time_update_id = self._schedule_after(1000, self.update_time)
        except:
            pass
        
    def toggle_password_visibility(self):
        if self.password_entry.cget("show") == "●":
            self.password_entry.configure(show="")
            if self.mostrar_icon:
                self.show_pass_btn.configure(image=self.mostrar_icon, text="")
            else:
                self.show_pass_btn.configure(text="🙈")
        else:
            self.password_entry.configure(show="●")
            if self.ocultar_icon:
                self.show_pass_btn.configure(image=self.ocultar_icon, text="")
            else:
                self.show_pass_btn.configure(text="👁")
    
    def handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username:
            self.show_error("Por favor, ingrese su usuario")
            self.username_entry.focus_set()
            return
            
        if not password:
            self.show_error("Por favor, ingrese su contraseña")
            self.password_entry.focus_set()
            return
        
        self.login_btn.configure(state="disabled")
        
        # Crear overlay con transparencia
        self.overlay = ctk.CTkFrame(
            self.login_card,
            fg_color=self.colors['overlay_bg_dark'],
            corner_radius=24
        )
        self.overlay.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Container para spinner
        loading_container = ctk.CTkFrame(self.overlay, fg_color="transparent")
        loading_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Crear spinner de forma segura
        if SPINNER_AVAILABLE:
            try:
                self.spinner_loading = create_spinner_safe(
                    loading_container,
                    size=70,
                    fg_color="transparent",
                    progress_color=self.colors['accent'],
                    bg_overlay_color=self.colors['overlay_bg_dark'],
                    bar_width=6,
                    speed=0.08,
                    direction="right"
                )
                
                if self.spinner_loading:
                    self.spinner_loading.pack()
                    self.spinner_loading.start()
                else:
                    ctk.CTkLabel(
                        loading_container,
                        text="⏳",
                        font=("Arial", 60),
                        fg_color="transparent"
                    ).pack()
            except Exception as e:
                print(f"Error creando spinner: {e}")
                ctk.CTkLabel(
                    loading_container,
                    text="⏳",
                    font=("Arial", 60),
                    fg_color="transparent"
                ).pack()
        else:
            ctk.CTkLabel(
                loading_container,
                text="⏳",
                font=("Arial", 60),
                fg_color="transparent"
            ).pack()
        
        self.loading_label = ctk.CTkLabel(
            loading_container,
            text="Verificando credenciales...",
            font=("Segoe UI", 13),
            text_color=self.colors['text_primary']
        )
        self.loading_label.pack(pady=(20, 0))
        
        self.root.update_idletasks()
        
        # Iniciar autenticación en thread
        auth_thread = threading.Thread(target=self.authenticate_user, args=(username, password))
        auth_thread.daemon = True
        auth_thread.start()
    
    def authenticate_user(self, username, password):
        try:
            time.sleep(1.2)
            
            if DB_AVAILABLE:
                result = db_manager.authenticate_and_connect(username, password)
                
                if result['success']:
                    device_auth = device_manager.verify_device_authorization()
                    
                    if device_auth['needs_registration']:
                        reg_result = device_manager.register_device(username)
                        result = {
                            'success': False,
                            'message': reg_result['message']
                        }
                    elif not device_auth['authorized']:
                        result = {
                            'success': False,
                            'message': device_auth['message']
                        }
                    else:
                        device_manager.log_access(
                            username=username,
                            modulo='Login',
                            accion='Inicio de sesión exitoso',
                            exito=True
                        )
            else:
                if username.lower() in ['jared', 'valeria', 'test', 'antonio'] and password:
                    result = {
                        'success': True,
                        'user_data': {
                            'username': username,
                            'nombre_completo': f'{username.title()} (Modo Demo - Sin BD)',
                            'rol': 'admin'
                        }
                    }
                else:
                    result = {'success': False, 'message': 'Credenciales incorrectas'}
            
            self.root.after(0, self.handle_auth_result, result)
            
        except Exception as e:
            error_result = {'success': False, 'message': f'Error de conexión: {str(e)}'}
            self.root.after(0, self.handle_auth_result, error_result)

    def handle_auth_result(self, result):
        # Detener y destruir spinner de forma segura
        if self.spinner_loading:
            try:
                self.spinner_loading.stop()
                self.spinner_loading.destroy()
                self.spinner_loading = None
            except:
                pass

        if result['success']:
            # Destruir overlay anterior
            if self.overlay:
                try:
                    self.overlay.destroy()
                except:
                    pass
            
            # Crear overlay de éxito
            self.overlay = ctk.CTkFrame(
                self.login_card,
                fg_color=self.colors['overlay_bg_dark'],
                corner_radius=24
            )
            self.overlay.place(x=0, y=0, relwidth=1, relheight=1)

            success_container = ctk.CTkFrame(self.overlay, fg_color="transparent")
            success_container.place(relx=0.5, rely=0.5, anchor="center")
            
            ctk.CTkLabel(
                success_container,
                text="✓",
                font=("Segoe UI", 80, "bold"),
                text_color=self.colors['success']
            ).pack()
            
            self.user_data = result['user_data']
            ctk.CTkLabel(
                success_container,
                text="¡Bienvenido!",
                font=("Segoe UI", 24),
                text_color=self.colors['text_primary']
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                success_container,
                text=self.user_data['nombre_completo'],
                font=("Segoe UI", 14),
                text_color=self.colors['text_secondary']
            ).pack()
            
            if DB_AVAILABLE:
                session_manager.start_session(self.user_data)
            
            if self.remember_var.get():
                self.save_credentials()
            else:
                self.clear_saved_credentials()
            
            self._schedule_after(1500, self.close_with_success_animation)
            
        else:
            # Destruir overlay en caso de error
            if self.overlay:
                try:
                    self.overlay.destroy()
                    self.overlay = None
                except:
                    pass
            
            self.login_btn.configure(state="normal")
            self.show_error(result['message'])
    
    def close_with_success_animation(self):
        if self.overlay:
            try:
                self.overlay.destroy()
            except:
                pass
        self.close_with_success()
    
    def show_error(self, message):
        self.status_label.configure(text=message, text_color=self.colors['error'])
        self._schedule_after(5000, lambda: self.status_label.configure(text="") if self.status_label.winfo_exists() else None)
    
    def show_success(self, message):
        self.status_label.configure(text=message, text_color=self.colors['success'])
    
    def close_with_success(self):
        self.login_successful = True
        self._is_closing = True
        self._cancel_all_callbacks()
        if self.on_success_callback:
            self.on_success_callback(self.user_data)
        self.root.destroy()
    
    def save_credentials(self):
        try:
            with open(".disfruleg_remember", "w") as f:
                f.write(self.username_var.get())
        except Exception as e:
            print(f"Error al guardar credenciales: {e}")
    
    def load_remembered_credentials(self):
        try:
            with open(".disfruleg_remember", "r") as f:
                username = f.read().strip()
                if username:
                    self.username_var.set(username)
                    self.remember_var.set(True)
                    self.password_entry.focus_set()
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error al cargar credenciales: {e}")
    
    def clear_saved_credentials(self):
        try:
            if os.path.exists(".disfruleg_remember"):
                os.remove(".disfruleg_remember")
        except Exception as e:
            print(f"Error al limpiar credenciales: {e}")
    
    def on_closing(self):
        """✅ Limpieza total al cerrar la ventana"""
        self._is_closing = True
        self._cancel_all_callbacks()
        
        if self.spinner_loading:
            try:
                self.spinner_loading.stop()
                self.spinner_loading.destroy()
                self.spinner_loading = None
            except:
                pass
        
        if self.overlay:
            try:
                self.overlay.destroy()
                self.overlay = None
            except:
                pass
        
        try:
            self.root.update_idletasks()
            self.root.update()
        except:
            pass
        
        try:
            time.sleep(0.05)
        except:
            pass
        
        try:
            if not self.login_successful:
                self.root.quit()
            else:
                self.root.destroy()
        except:
            pass
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            if hasattr(self, '_is_closing') and not self._is_closing:
                self.on_closing()
        
        return self.login_successful, self.user_data

def show_login(on_success_callback=None):
    return ModernLoginWindow(on_success_callback).run()

if __name__ == "__main__":
    success, user_data = show_login()
    if success:
        print(f"Login successful: {user_data}")
    else:
        print("Login cancelled or failed")