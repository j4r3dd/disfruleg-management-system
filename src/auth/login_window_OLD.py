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
        
        self.colors = {
            'primary': '#2D9B6C',
            'primary_hover': '#25845D',
            'secondary': '#2C3E50',
            'accent': '#E74C3C',
            'success': '#27AE60',
            'overlay_bg_dark': 'gray14',
            'overlay_bg_light': 'gray92'
        }
        
        # Sistema de gestión de callbacks
        self._after_callbacks = set()
        self._is_closing = False
        self._time_update_id = None
        
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
        
    def _load_icons(self):
        """Carga todos los iconos necesarios para la ventana."""
        try:
            # Iconos de tema
            sol_path = self.get_asset_path('icons/SOL.png')
            luna_path = self.get_asset_path('icons/LUNA.png')
            if sol_path and luna_path and os.path.exists(sol_path) and os.path.exists(luna_path):
                sol_img = Image.open(sol_path).resize((22, 22), Image.Resampling.LANCZOS)
                luna_img = Image.open(luna_path).resize((22, 22), Image.Resampling.LANCZOS)
                self.sol_icon = ctk.CTkImage(light_image=sol_img, dark_image=sol_img, size=(22, 22))
                self.luna_icon = ctk.CTkImage(light_image=luna_img, dark_image=luna_img, size=(22, 22))

            # Iconos de visibilidad de contraseña
            mostrar_path = self.get_asset_path('icons/mostrar.png')
            ocultar_path = self.get_asset_path('icons/ocultar.png')
            if mostrar_path and ocultar_path and os.path.exists(mostrar_path) and os.path.exists(ocultar_path):
                mostrar_img = Image.open(mostrar_path).resize((24, 24), Image.Resampling.LANCZOS)
                ocultar_img = Image.open(ocultar_path).resize((24, 24), Image.Resampling.LANCZOS)
                self.mostrar_icon = ctk.CTkImage(light_image=mostrar_img, dark_image=mostrar_img, size=(24, 24))
                self.ocultar_icon = ctk.CTkImage(light_image=ocultar_img, dark_image=ocultar_img, size=(24, 24))
        except Exception as e:
            print(f"Error cargando iconos: {e}")
    
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
            
    def setup_window(self):
        self.root.title("DISFRULEG - Iniciar Sesión")
        self.root.geometry("600x750")
        self.root.resizable(True, True)
        
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
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_interface(self):
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.create_header(main_frame)
        self.create_login_card(main_frame)
        self.create_footer(main_frame)
        
    def create_header(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(side="left")
        
        try:
            logo_path = self.get_asset_path('logos/ubicuo_logo.png')
            if logo_path and os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                self.ubicuo_photo = ctk.CTkImage(
                    light_image=logo_img,
                    dark_image=logo_img,
                    size=(28, 28)
                )
                ctk.CTkLabel(logo_frame, image=self.ubicuo_photo, text="").pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"Error cargando logo Ubicuo: {e}")
        
        ctk.CTkLabel(
            logo_frame,
            text="UBICUO STUDIO",
            font=("Arial", 11, "bold"),
            text_color=self.colors['primary']
        ).pack(side="left")
        
        theme_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_frame.pack(side="right")
        
        self.time_label = ctk.CTkLabel(
            theme_frame,
            text="",
            font=("Arial", 11),
            text_color="gray70"
        )
        self.time_label.pack(side="left", padx=10)
        
        # Iniciar actualización del reloj
        self.update_time()
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="",
            command=self.toggle_theme,
            width=50,
            progress_color=self.colors['primary'],
            state="disabled"
        )
        if self.theme_mode.get() == "dark":
            self.theme_switch.select()
        
    def create_login_card(self, parent):
        card_container = ctk.CTkFrame(parent, fg_color="transparent")
        card_container.pack(fill="both", expand=True, pady=5)
        
        self.login_card = ctk.CTkFrame(card_container, corner_radius=20, border_width=0)
        self.login_card.pack(fill="both", expand=True, padx=5, pady=5)
        
        logo_container = ctk.CTkFrame(self.login_card, fg_color="transparent")
        logo_container.pack(pady=(20, 10))
        
        self.disfruleg_photo = None
        try:
            logo_filename = 'disfruleg_rojo.png' if self.theme_mode.get() == "dark" else 'disfruleg_negro.png'
            logo_path = self.get_asset_path(f'logos/{logo_filename}')
            
            if logo_path and os.path.exists(logo_path):
                logo_img = Image.open(logo_path).resize((300, 60), Image.Resampling.LANCZOS)
                self.disfruleg_photo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(300, 60))
                self.disfruleg_label = ctk.CTkLabel(logo_container, image=self.disfruleg_photo, text="")
                self.disfruleg_label.pack()
            else:
                self.disfruleg_label = ctk.CTkLabel(logo_container, text="DISFRULEG", 
                                                    font=("Arial", 32, "bold"), 
                                                    text_color=self.colors['primary'])
                self.disfruleg_label.pack()
        except Exception as e:
            print(f"Error cargando logo DISFRULEG: {e}")
            self.disfruleg_label = ctk.CTkLabel(logo_container, text="DISFRULEG", 
                                                font=("Arial", 32, "bold"), 
                                                text_color=self.colors['primary'])
            self.disfruleg_label.pack()
        
        
        ctk.CTkLabel(self.login_card, text="Iniciar Sesión", 
                    font=("Arial", 20, "bold")).pack(pady=(5, 15))
        
        form_frame = ctk.CTkFrame(self.login_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=30, pady=5)
        
        ctk.CTkLabel(form_frame, text="Usuario", font=("Arial", 12, "bold"), 
                    anchor="w").pack(fill="x", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.username_var,
            height=40,
            font=("Arial", 12),
            placeholder_text="Ingrese su usuario",
            corner_radius=10,
            border_width=2
        )
        self.username_entry.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(form_frame, text="Contraseña", font=("Arial", 12, "bold"), 
                    anchor="w").pack(fill="x", pady=(0, 5))
        
        password_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_container.pack(fill="x", pady=(0, 10))
        
        self.password_entry = ctk.CTkEntry(
            password_container,
            textvariable=self.password_var,
            height=40,
            font=("Arial", 12),
            placeholder_text="Ingrese su contraseña",
            show="●",
            corner_radius=10,
            border_width=2
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        self.show_pass_btn = ctk.CTkButton(
            password_container,
            image=self.ocultar_icon if self.ocultar_icon else None,
            text="" if self.ocultar_icon else "👁",
            width=42,
            height=42,
            font=("Arial", 14) if not self.ocultar_icon else None,
            command=self.toggle_password_visibility,
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            corner_radius=10,
            border_width=2
        )
        self.show_pass_btn.pack(side="right")
        
        remember_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        remember_frame.pack(fill="x", pady=(0, 15))
        
        self.remember_check = ctk.CTkCheckBox(
            remember_frame,
            text="Recordar credenciales",
            variable=self.remember_var,
            font=("Arial", 11),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=6
        )
        self.remember_check.pack(side="left")
        
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="INICIAR SESIÓN",
            command=self.handle_login,
            height=45,
            font=("Arial", 13, "bold"),
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover']
        )
        self.login_btn.pack(fill="x", pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=("Arial", 10),
            text_color=self.colors['accent'],
            wraplength=300
        )
        self.status_label.pack(pady=(5, 10))
        
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        self.username_entry.focus_set()
        
    def create_footer(self, parent):
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(footer_frame, text="Sistema de Autenticación Segura", 
                    font=("Arial", 10), text_color="gray").pack()
        
        ctk.CTkLabel(
            footer_frame,
            text=f"© {datetime.now().year} DISFRULEG · Desarrollado por Ubicuo Studio",
            font=("Arial", 9),
            text_color="gray60"
        ).pack(pady=(5, 0))
        
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
                    logo_img = Image.open(logo_path).resize((300, 60), Image.Resampling.LANCZOS)
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
        """Actualiza el reloj en tiempo real"""
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
            self.time_label.configure(text=f" {date_str} • {time_str}")
            
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
        
        # Crear overlay
        overlay_fg_color_tuple = (self.colors['overlay_bg_light'], self.colors['overlay_bg_dark'])
        self.overlay = ctk.CTkFrame(
            self.login_card,
            fg_color=overlay_fg_color_tuple,
            corner_radius=20
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
                    size=80,
                    fg_color="transparent",
                    progress_color=self.colors['primary'],
                    bg_overlay_color=overlay_fg_color_tuple,
                    bar_width=8,
                    speed=0.08,
                    direction="right"
                )
                
                if self.spinner_loading:
                    self.spinner_loading.pack()
                    self.spinner_loading.start()
                else:
                    ctk.CTkLabel(
                        loading_container,
                        text="⌛",
                        font=("Arial", 60),
                        fg_color="transparent"
                    ).pack()
            except Exception as e:
                print(f"Error creando spinner: {e}")
                ctk.CTkLabel(
                    loading_container,
                    text="⌛",
                    font=("Arial", 60),
                    fg_color="transparent"
                ).pack()
        else:
            ctk.CTkLabel(
                loading_container,
                text="⌛",
                font=("Arial", 60),
                fg_color="transparent"
            ).pack()
        
        self.loading_label = ctk.CTkLabel(
            loading_container,
            text="Verificando credenciales...",
            font=("Arial", 14, "bold"),
            text_color=self.colors['primary']
        )
        self.loading_label.pack(pady=(15, 0))
        
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
                if username in ['jared', 'valeria', 'test'] and password:
                    result = {
                        'success': True,
                        'user_data': {
                            'username': username,
                            'nombre_completo': f'{username.title()} (Administrador)',
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
            overlay_fg_color_tuple = (self.colors['overlay_bg_light'], self.colors['overlay_bg_dark'])
            self.overlay = ctk.CTkFrame(
                self.login_card,
                fg_color=overlay_fg_color_tuple,
                corner_radius=20
            )
            self.overlay.place(x=0, y=0, relwidth=1, relheight=1)

            success_container = ctk.CTkFrame(self.overlay, fg_color="transparent")
            success_container.place(relx=0.5, rely=0.5, anchor="center")
            
            ctk.CTkLabel(
                success_container,
                text="✓",
                font=("Arial", 80, "bold"),
                text_color=self.colors['success']
            ).pack()
            
            self.user_data = result['user_data']
            ctk.CTkLabel(
                success_container,
                text="¡Bienvenido!",
                font=("Arial", 24, "bold"),
                text_color=self.colors['success']
            ).pack(pady=(10, 5))
            
            ctk.CTkLabel(
                success_container,
                text=self.user_data['nombre_completo'],
                font=("Arial", 16),
                text_color=self.colors['primary']
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
        self.status_label.configure(text=message, text_color=self.colors['accent'])
        self._schedule_after(5000, lambda: self.status_label.configure(text="") if self.status_label.winfo_exists() else None)
    
    def show_success(self, message):
        self.status_label.configure(text=message, text_color=self.colors['success'])
    
    def close_with_success(self):
        self.login_successful = True
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
        """Limpieza total al cerrar la ventana"""
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