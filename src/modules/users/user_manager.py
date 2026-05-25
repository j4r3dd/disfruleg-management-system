import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import re
from src.auth.auth_manager import AuthManager
from src.auth.session_manager import session_manager
from src.database.conexion import conectar, return_connection
from src.theme import COLORS, FONTS, create_button, create_label, create_entry

class UserManagerApp:
    def __init__(self, root, user_data=None):
        self.root = root
        self.root.title("Administrador de Usuarios - Disfruleg")
        self.root.geometry("1400x900")
        
        # ✅ FIX: Hacer que la ventana se abra ENCIMA de main_application
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()
        
        # User data and permissions
        self.user_data = user_data if isinstance(user_data, dict) else {}
        self.current_user_is_admin = (self.user_data.get('rol', '') == 'admin')

        # Initialize AuthManager
        self.auth_manager = AuthManager()

        # Connect to database
        try:
            self.conn = conectar()
            if self.conn:
                self.cursor = self.conn.cursor()
            else:
                raise Exception("No se pudo establecer conexión")
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {e}")
            # Return connection to pool before destroying
            if hasattr(self, 'conn') and self.conn:
                return_connection(self.conn)
            self.root.destroy()
            return
        
        # Variables
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_users)
        self.role_filter_var = ctk.StringVar(value="todos")
        self.status_filter_var = ctk.StringVar(value="todos")
        
        # User list storage
        self.all_users = []
        
        # Check admin permissions
        if not self.current_user_is_admin:
            messagebox.showerror("Acceso Denegado", "Este módulo requiere permisos de administrador.")
            # Return connection to pool before destroying
            if hasattr(self, 'conn') and self.conn:
                return_connection(self.conn)
            self.root.destroy()
            return

        # Setup interface - wrap in try-catch to handle any errors during initialization
        try:
            self.setup_interface()
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error de Inicialización", f"Error al inicializar la interfaz: {e}")
            # Return connection to pool before destroying
            if hasattr(self, 'conn') and self.conn:
                return_connection(self.conn)
            self.root.destroy()
            return
        
        # Protocol for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_interface(self):
        """Setup the main interface with modern design"""
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color=("#1a1a1a", "#1a1a1a"))
        main_container.pack(fill="both", expand=True)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        content_area = ctk.CTkFrame(main_container, fg_color="transparent")
        content_area.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Stats cards
        self.create_stats_cards(content_area)
        
        # Filters bar
        self.create_filters_bar(content_area)
        
        # Users grid (scrollable)
        self.create_users_grid(content_area)
    
    def create_header(self, parent):
        """Create modern header with back button"""
        header_frame = ctk.CTkFrame(parent, fg_color=("#1a1a1a", "#1a1a1a"), height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=0)
        
        # Left: Back button + Logo + Title
        left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        left_frame.pack(side="left", fill="y")
        
        # ✅ BACK BUTTON MEJORADO (similar al logout)
        back_btn = ctk.CTkButton(
            left_frame,
            text="⎋",  # Símbolo de escape/salir
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['accent'],
            font=("Arial", 20),
            text_color="white",
            border_width=0,
            command=self.on_closing
        )
        back_btn.pack(side="left", padx=(0, 15))
        
        # Logo
        logo_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        logo_frame.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(
            logo_frame,
            text="👤",
            font=("Arial", 28)
        ).pack()
        
        # Title
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="ADMINISTRADOR DE USUARIOS",
            font=("Arial", 16, "bold"),
            text_color=COLORS['success'],
            anchor="w"
        ).pack(anchor="w")
        
        user_info = f"Usuario: {self.user_data.get('nombre_completo', 'test')} | Rol: {self.user_data.get('rol', 'ADMIN').upper()}"
        ctk.CTkLabel(
            title_frame,
            text=user_info,
            font=("Arial", 10),
            text_color="gray60",
            anchor="w"
        ).pack(anchor="w")
        
        # Right: Create User button
        ctk.CTkButton(
            header_content,
            text="Crear Usuario",
            width=160,
            height=45,
            corner_radius=10,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            font=FONTS['button'],
            command=self.create_new_user
        ).pack(side="right")
    
    def create_stats_cards(self, parent):
        """Create statistics cards"""
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Stats data will be populated dynamically
        self.stats = {
            'total': {'label': 'Total Usuarios', 'value': '0', 'icon': '👥', 'color': '#3b82f6'},
            'active': {'label': 'Usuarios Activos', 'value': '0', 'icon': '📈', 'color': '#10b981'},
            'blocked': {'label': 'Bloqueados', 'value': '0', 'icon': '🛡️', 'color': '#ef4444'},
            'admins': {'label': 'Administradores', 'value': '0', 'icon': '👨‍💼', 'color': '#a855f7'}
        }
        
        self.stat_labels = {}
        
        for i, (key, data) in enumerate(self.stats.items()):
            card = self.create_stat_card(stats_frame, data)
            card.grid(row=0, column=i, padx=10, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)
    
    def create_stat_card(self, parent, data):
        """Create a single stat card"""
        card = ctk.CTkFrame(parent, fg_color=("#2a2a2a", "#2a2a2a"), corner_radius=15)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with label and icon
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text=data['label'],
            font=("Arial", 11),
            text_color="gray60",
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=data['icon'],
            font=("Arial", 18),
            text_color=data['color']
        ).pack(side="right")
        
        # Value
        value_label = ctk.CTkLabel(
            content,
            text=data['value'],
            font=("Arial", 32, "bold"),
            text_color="white",
            anchor="w"
        )
        value_label.pack(anchor="w", pady=(10, 0))
        
        # Store reference for updates
        key = data['label'].split()[0].lower()
        self.stat_labels[key] = value_label
        
        return card
    
    def create_filters_bar(self, parent):
        """Create filters bar"""
        filters_frame = ctk.CTkFrame(parent, fg_color=("#2a2a2a", "#2a2a2a"), corner_radius=15)
        filters_frame.pack(fill="x", pady=(0, 20))
        
        filters_content = ctk.CTkFrame(filters_frame, fg_color="transparent")
        filters_content.pack(fill="x", padx=20, pady=15)
        
        # Search bar
        search_frame = ctk.CTkFrame(filters_content, fg_color=("#1a1a1a", "#1a1a1a"), corner_radius=10)
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Arial", 14),
            text_color="gray"
        ).pack(side="left", padx=(15, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Buscar usuario...",
            fg_color="transparent",
            border_width=0,
            font=("Arial", 12),
            text_color="white"
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15), pady=10)
        
        # Role filter
        ctk.CTkLabel(
            filters_content,
            text="Rol:",
            font=("Arial", 11),
            text_color="gray60"
        ).pack(side="left", padx=(0, 10))
        
        role_menu = ctk.CTkOptionMenu(
            filters_content,
            values=["Todos los roles", "Admin", "Usuario", "Supervisor"],
            variable=self.role_filter_var,
            width=180,
            height=40,
            corner_radius=10,
            fg_color=("#1a1a1a", "#1a1a1a"),
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_hover'],
            command=lambda x: self.filter_users()
        )
        role_menu.set("Todos los roles")
        role_menu.pack(side="left", padx=(0, 15))
        
        # Status filter
        ctk.CTkLabel(
            filters_content,
            text="Estado:",
            font=("Arial", 11),
            text_color="gray60"
        ).pack(side="left", padx=(0, 10))
        
        status_menu = ctk.CTkOptionMenu(
            filters_content,
            values=["Todos los estados", "Activo", "Inactivo", "Bloqueado"],
            variable=self.status_filter_var,
            width=180,
            height=40,
            corner_radius=10,
            fg_color=("#1a1a1a", "#1a1a1a"),
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_hover'],
            command=lambda x: self.filter_users()
        )
        status_menu.set("Todos los estados")
        status_menu.pack(side="left")
    
    def create_users_grid(self, parent):
        """Create scrollable users grid"""
        # Scrollable frame for users
        self.users_scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        self.users_scroll.pack(fill="both", expand=True)
        
        # Configure grid
        for i in range(3):
            self.users_scroll.grid_columnconfigure(i, weight=1, uniform="column")
    
    def load_users(self):
        """Load all users from database"""
        try:
            # Clear existing cards
            for widget in self.users_scroll.winfo_children():
                widget.destroy()
            
            # Fetch users
            self.cursor.execute("""
                SELECT id_usuario, username, nombre_completo, rol, activo, 
                       ultimo_acceso, intentos_fallidos, bloqueado_hasta
                FROM usuarios_sistema
                ORDER BY nombre_completo
            """)
            
            self.all_users = self.cursor.fetchall()
            
            # Update stats
            self.update_stats()
            
            # Create user cards
            self.display_users(self.all_users)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
    
    def update_stats(self):
        """Update statistics cards"""
        total = len(self.all_users)
        active = sum(1 for u in self.all_users if u['activo'] and not (u['bloqueado_hasta'] and u['bloqueado_hasta'] > datetime.now()))
        blocked = sum(1 for u in self.all_users if u['bloqueado_hasta'] and u['bloqueado_hasta'] > datetime.now())
        admins = sum(1 for u in self.all_users if u['rol'] == 'admin')
        
        if 'total' in self.stat_labels:
            self.stat_labels['total'].configure(text=str(total))
        if 'usuarios' in self.stat_labels:
            self.stat_labels['usuarios'].configure(text=str(active))
        if 'bloqueados' in self.stat_labels:
            self.stat_labels['bloqueados'].configure(text=str(blocked))
        if 'administradores' in self.stat_labels:
            self.stat_labels['administradores'].configure(text=str(admins))
    
    def display_users(self, users):
        """Display user cards in grid"""
        row = 0
        col = 0
        max_cols = 3
        
        for user in users:
            self.create_user_card(user, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    def create_user_card(self, user, row, col):
        """Create a modern user card with perfect circular avatar"""
        # Determine status
        is_blocked = user['bloqueado_hasta'] and user['bloqueado_hasta'] > datetime.now()
        is_active = user['activo'] and not is_blocked
        
        if is_blocked:
            status = "Bloqueado"
            status_color = COLORS['accent']
            status_icon = "🔒"
        elif is_active:
            status = "Activo"
            status_color = COLORS['success']
            status_icon = "✓"
        else:
            status = "Inactivo"
            status_color = "gray"
            status_icon = "⚠"
        
        # Get avatar color based on role (default colors)
        avatar_colors = {
            'admin': '#a855f7',
            'usuario': '#f97316',
            'supervisor': '#06b6d4'
        }
        default_avatar_color = avatar_colors.get(user['rol'], '#6b7280')
        
        # Role badge color
        role_colors = {
            'admin': '#a855f7',
            'usuario': '#f97316',
            'supervisor': '#3b82f6'
        }
        role_color = role_colors.get(user['rol'], '#6b7280')
        
        # Card container
        card = ctk.CTkFrame(
            self.users_scroll,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=20,
            border_width=0
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Card content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # ✅ OBTENER DATOS DEL AVATAR (color e imagen) desde BD
        try:
            avatar_data = self.auth_manager.get_user_avatar_data(user['username'])
            user_avatar_color = avatar_data.get('color') or default_avatar_color
            user_avatar_image = avatar_data.get('imagen')
        except:
            user_avatar_color = default_avatar_color
            user_avatar_image = None
        
        # Avatar section
        avatar_section = ctk.CTkFrame(content, fg_color="transparent")
        avatar_section.pack(fill="x")
        
        # Avatar container (CENTRADO)
        avatar_container = ctk.CTkFrame(avatar_section, fg_color="transparent")
        avatar_container.pack(anchor="center")
        
        # ✅ MOSTRAR IMAGEN O INICIALES (NO AMBAS)
        if user_avatar_image:
            # ========================================
            # SI HAY IMAGEN: Mostrar en círculo limpio
            # ========================================
            try:
                from PIL import Image, ImageDraw
                from io import BytesIO
                
                # Cargar imagen
                img = Image.open(BytesIO(user_avatar_image))
                
                # Convertir a RGBA
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Redimensionar
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                
                # ✅ CREAR MÁSCARA CIRCULAR PERFECTA
                mask = Image.new('L', (120, 120), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 120, 120), fill=255)
                
                # Aplicar máscara a la imagen
                output = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
                output.paste(img, (0, 0))
                output.putalpha(mask)
                
                # Crear CTkImage
                ctk_image = ctk.CTkImage(
                    light_image=output,
                    dark_image=output,
                    size=(120, 120)
                )
                
                # ✅ LABEL CON FONDO TRANSPARENTE (sin cuadrado visible)
                avatar_label = ctk.CTkLabel(
                    avatar_container,
                    image=ctk_image,
                    text="",
                    fg_color="transparent"
                )
                avatar_label.pack()
                
            except Exception as e:
                print(f"Error loading image for {user['username']}: {e}")
                # Fallback a iniciales
                avatar = ctk.CTkFrame(
                    avatar_container,
                    fg_color=user_avatar_color,
                    corner_radius=60,
                    width=120,
                    height=120
                )
                avatar.pack()
                avatar.pack_propagate(False)
                
                initials = ''.join([n[0].upper() for n in user['nombre_completo'].split()[:2]])
                ctk.CTkLabel(
                    avatar,
                    text=initials,
                    font=("Arial", 42, "bold"),
                    text_color="white",
                    fg_color="transparent"
                ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            # ========================================
            # SI NO HAY IMAGEN: Mostrar iniciales con color
            # ========================================
            avatar = ctk.CTkFrame(
                avatar_container,
                fg_color=user_avatar_color,
                corner_radius=60,
                width=120,
                height=120
            )
            avatar.pack()
            avatar.pack_propagate(False)
            
            initials = ''.join([n[0].upper() for n in user['nombre_completo'].split()[:2]])
            ctk.CTkLabel(
                avatar,
                text=initials,
                font=("Arial", 42, "bold"),
                text_color="white",
                fg_color="transparent"
            ).place(relx=0.5, rely=0.5, anchor="center")
        
        # User name
        ctk.CTkLabel(
            content,
            text=user['nombre_completo'],
            font=("Arial", 16, "bold"),
            text_color="white",
            anchor="center"
        ).pack(pady=(15, 5))
        
        # Username
        ctk.CTkLabel(
            content,
            text=f"@{user['username']}",
            font=("Arial", 11),
            text_color="gray60",
            anchor="center"
        ).pack(pady=(0, 10))
        
        # Status badge
        status_frame = ctk.CTkFrame(
            content,
            fg_color=status_color,
            corner_radius=15,
            height=30
        )
        status_frame.pack(fill="x", pady=(0, 10))
        status_frame.pack_propagate(False)
        
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(expand=True)
        
        ctk.CTkLabel(
            status_content,
            text=status_icon,
            font=("Arial", 12),
            text_color="white"
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            status_content,
            text=status,
            font=("Arial", 11, "bold"),
            text_color="white"
        ).pack(side="left")
        
        # Role badge
        role_frame = ctk.CTkFrame(
            content,
            fg_color=role_color,
            corner_radius=15,
            height=30
        )
        role_frame.pack(fill="x", pady=(0, 15))
        role_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            role_frame,
            text=user['rol'].upper(),
            font=("Arial", 10, "bold"),
            text_color="white"
        ).pack(expand=True)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(fill="x")
        
        # Edit button
        ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#3a3a3a", "#3a3a3a"),
            hover_color=COLORS['primary'],
            font=("Arial", 16),
            command=lambda u=user: self.show_user_detail(u)
        ).pack(side="left", expand=True, padx=2)
        
        # Delete button
        ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#3a3a3a", "#3a3a3a"),
            hover_color=COLORS['accent'],
            font=("Arial", 16),
            command=lambda u=user: self.delete_user_action(u)
        ).pack(side="left", expand=True, padx=2)
        
        # Reset button (if blocked)
        if is_blocked:
            ctk.CTkButton(
                actions_frame,
                text="🔓",
                width=40,
                height=40,
                corner_radius=10,
                fg_color=("#3a3a3a", "#3a3a3a"),
                hover_color="#9B59B6",
                font=("Arial", 16),
                command=lambda u=user: self.reset_user_block(u)
            ).pack(side="left", expand=True, padx=2)
    
    def filter_users(self, *args):
        """Filter users based on search text and filters"""
        search_text = self.search_var.get().lower()
        role_filter = self.role_filter_var.get()
        status_filter = self.status_filter_var.get()
        
        filtered_users = []
        
        for user in self.all_users:
            # Search filter
            if search_text:
                if search_text not in user['username'].lower() and search_text not in user['nombre_completo'].lower():
                    continue
            
            # Role filter
            if role_filter and role_filter != "Todos los roles":
                if user['rol'] != role_filter.lower():
                    continue
            
            # Status filter
            if status_filter and status_filter != "Todos los estados":
                is_blocked = user['bloqueado_hasta'] and user['bloqueado_hasta'] > datetime.now()
                is_active = user['activo'] and not is_blocked
                
                if status_filter == "Activo" and not is_active:
                    continue
                elif status_filter == "Inactivo" and (is_active or is_blocked):
                    continue
                elif status_filter == "Bloqueado" and not is_blocked:
                    continue
            
            filtered_users.append(user)
        
        # Clear and display filtered users
        for widget in self.users_scroll.winfo_children():
            widget.destroy()
        
        self.display_users(filtered_users)
    
    def show_user_detail(self, user):
        """Show user detail dialog"""
        def handle_callback(action, data):
            if action == 'edit':
                self.edit_user(data)
            elif action == 'delete':
                self.delete_user_action(data)
            elif action == 'reload':
                self.load_users()
        
        UserDetailDialog(self.root, user, self.auth_manager, handle_callback)
    
    def create_new_user(self):
        """Create a new user"""
        dialog = UserDialog(self.root, "Crear Nuevo Usuario", self.auth_manager)
        if dialog.result:
            self.load_users()
    
    def edit_user(self, user):
        """Edit the selected user"""
        try:
            user_info = self.auth_manager.get_user_info_by_id(user['id_usuario'])
            if user_info:
                dialog = UserDialog(self.root, "Editar Usuario", self.auth_manager, user_info)
                if dialog.result:
                    self.load_users()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuario: {e}")
    
    def reset_user_block(self, user):
        """Reset user block"""
        if messagebox.askyesno("Confirmar", f"¿Desbloquear usuario '{user['username']}'?"):
            try:
                self.cursor.execute("""
                    UPDATE usuarios_sistema 
                    SET bloqueado_hasta = NULL, intentos_fallidos = 0
                    WHERE id_usuario = %s
                """, (user['id_usuario'],))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Usuario desbloqueado correctamente.")
                self.load_users()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Error", f"Error al desbloquear usuario: {e}")
    
    def delete_user_action(self, user):
        """Delete selected user"""
        username = user['username']
        
        # Prevent self-deletion
        if username == self.user_data.get('username', ''):
            messagebox.showwarning("Advertencia", "No puede eliminar su propia cuenta.")
            return
        
        # Double confirmation
        if not messagebox.askyesno("CONFIRMAR ELIMINACIÓN", 
                                  f"¿Está ABSOLUTAMENTE SEGURO de que desea eliminar al usuario '{username}'?\n\n" +
                                  "Esta acción NO SE PUEDE DESHACER."):
            return
        
        try:
            self.cursor.execute("DELETE FROM usuarios_sistema WHERE id_usuario = %s", (user['id_usuario'],))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", f"Usuario '{username}' eliminado exitosamente.")
            self.load_users()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al eliminar usuario: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        try:
            if hasattr(self, 'conn') and self.conn:
                # Return connection to pool instead of closing it
                return_connection(self.conn)
        except Exception as e:
            print(f"Error returning connection to pool: {e}")
        self.root.destroy()

class UserDetailDialog:
    """Modal de detalles del usuario con opciones de personalización"""
    
    def __init__(self, parent, user, auth_manager, on_update_callback=None):
        self.user = user
        self.auth_manager = auth_manager
        self.on_update_callback = on_update_callback
        self.selected_color = None
        self.selected_image = None
        self.image_path = None
        
        # Avatar colors palette
        self.avatar_colors = [
            '#10b981',  # Green
            '#3b82f6',  # Blue
            '#a855f7',  # Purple
            '#ec4899',  # Pink
            '#f97316',  # Orange
            '#06b6d4',  # Cyan
            '#ef4444',  # Red
            '#6366f1',  # Indigo
            '#8b5cf6',  # Violet
            '#14b8a6',  # Teal
        ]
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Detalles del Usuario")
        self.dialog.geometry("800x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Get current user avatar data
        self.load_avatar_data()
        
        self.setup_dialog()
        self.center_dialog()
    
    def load_avatar_data(self):
        """Load user avatar data from database"""
        try:
            avatar_data = self.auth_manager.get_user_avatar_data(self.user['username'])
            
            # Load color
            if avatar_data.get('color'):
                self.selected_color = avatar_data['color']
            else:
                # Use default based on role
                role_colors = {
                    'admin': '#a855f7',
                    'usuario': '#f97316',
                    'supervisor': '#06b6d4'
                }
                self.selected_color = role_colors.get(self.user['rol'], '#6b7280')
            
            # Load image
            self.selected_image = avatar_data.get('imagen')
            
        except Exception as e:
            print(f"Error loading avatar data: {e}")
            # Default color
            role_colors = {
                'admin': '#a855f7',
                'usuario': '#f97316',
                'supervisor': '#06b6d4'
            }
            self.selected_color = role_colors.get(self.user['rol'], '#6b7280')
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"800x650+{x}+{y}")
    
    def setup_dialog(self):
        """Setup dialog interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.dialog, fg_color=("#2a2a2a", "#2a2a2a"))
        main_frame.pack(fill="both", expand=True)
        
        # Content with scrollable area
        content = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header with avatar
        self.create_header_section(content)
        
        # Color picker section
        self.create_color_picker_section(content)
        
        # User info section
        self.create_user_info_section(content)
        
        # Action buttons
        self.create_action_buttons(content)
    
    def create_header_section(self, parent):
        """Create header with large avatar"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        # Avatar container
        avatar_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        avatar_container.pack()
        
        # Large avatar (will be updated when color/image changes)
        self.avatar_frame = ctk.CTkFrame(
            avatar_container,
            fg_color=self.selected_color,
            corner_radius=80,
            width=160,
            height=160
        )
        self.avatar_frame.pack()
        self.avatar_frame.pack_propagate(False)
        
        # Check if there's an image
        if self.selected_image:
            try:
                from PIL import Image
                from io import BytesIO
                
                img = Image.open(BytesIO(self.selected_image))
                img = img.resize((160, 160), Image.Resampling.LANCZOS)
                
                # Create circular mask
                from PIL import ImageDraw
                mask = Image.new('L', (160, 160), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 160, 160), fill=255)
                img.putalpha(mask)
                
                ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 160))
                
                self.avatar_label = ctk.CTkLabel(
                    self.avatar_frame,
                    image=ctk_image,
                    text=""
                )
                self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")
            except Exception as e:
                print(f"Error loading image: {e}")
                self.show_initials_avatar()
        else:
            self.show_initials_avatar()
        
        # User name
        ctk.CTkLabel(
            header_frame,
            text=self.user['nombre_completo'],
            font=("Arial", 24, "bold"),
            text_color="white"
        ).pack(pady=(20, 5))
        
        # Username
        ctk.CTkLabel(
            header_frame,
            text=f"@{self.user['username']}",
            font=("Arial", 14),
            text_color="gray60"
        ).pack()
    
    def show_initials_avatar(self):
        """Show initials in avatar"""
        initials = ''.join([n[0].upper() for n in self.user['nombre_completo'].split()[:2]])
        self.avatar_label = ctk.CTkLabel(
            self.avatar_frame,
            text=initials,
            font=("Arial", 56, "bold"),
            text_color="white"
        )
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def create_color_picker_section(self, parent):
        """Create color picker section"""
        color_section = ctk.CTkFrame(parent, fg_color=("#1a1a1a", "#1a1a1a"), corner_radius=15)
        color_section.pack(fill="x", pady=(0, 20))
        
        color_content = ctk.CTkFrame(color_section, fg_color="transparent")
        color_content.pack(fill="x", padx=20, pady=20)
        
        # Title with icon
        title_frame = ctk.CTkFrame(color_content, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            title_frame,
            text="Personalizar Avatar",
            font=("Arial", 16, "bold"),
            text_color="white",
            anchor="w"
        ).pack(side="left")
        
        # Buttons container
        buttons_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        # ✅ Botón para ELIMINAR imagen (solo si hay imagen)
        if self.selected_image:
            ctk.CTkButton(
                buttons_frame,
                text="🗑️ Eliminar Foto",
                width=130,
                height=35,
                corner_radius=10,
                fg_color=COLORS['accent'],
                hover_color="#c53030",
                command=self.remove_avatar_image
            ).pack(side="left", padx=(0, 10))
        
        # Camera button for image upload
        camera_btn = ctk.CTkButton(
            buttons_frame,
            text="📷 Subir Foto",
            width=120,
            height=35,
            corner_radius=10,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover'],
            command=self.upload_avatar_image
        )
        camera_btn.pack(side="left")
        
        # ✅ Mostrar selector de color SOLO si NO hay imagen
        if not self.selected_image:
            # Color palette
            ctk.CTkLabel(
                color_content,
                text="Color de Fondo:",
                font=("Arial", 12),
                text_color="gray60",
                anchor="w"
            ).pack(anchor="w", pady=(10, 10))
            
            palette_frame = ctk.CTkFrame(color_content, fg_color="transparent")
            palette_frame.pack(fill="x")
            
            self.color_buttons = []
            
            for i, color in enumerate(self.avatar_colors):
                col = i % 5
                row = i // 5
                
                # Color button
                color_btn = ctk.CTkFrame(
                    palette_frame,
                    fg_color=color,
                    corner_radius=35,
                    width=70,
                    height=70,
                    cursor="hand2"
                )
                color_btn.grid(row=row, column=col, padx=10, pady=10)
                color_btn.grid_propagate(False)
                
                # Selection indicator (if current color)
                if color == self.selected_color:
                    indicator = ctk.CTkFrame(
                        color_btn,
                        fg_color="transparent",
                        border_color="white",
                        border_width=4,
                        corner_radius=35,
                        width=70,
                        height=70
                    )
                    indicator.place(relx=0, rely=0)
                    color_btn.indicator = indicator
                
                # Bind click event
                color_btn.bind("<Button-1>", lambda e, c=color, btn=color_btn: self.select_color(c, btn))
                
                self.color_buttons.append(color_btn)
        else:
            # Mostrar mensaje si hay imagen
            ctk.CTkLabel(
                color_content,
                text="✓ Imagen de avatar personalizada cargada",
                font=("Arial", 12),
                text_color=COLORS['success'],
                anchor="w"
            ).pack(anchor="w", pady=(10, 10))
        
        # Save button
        ctk.CTkButton(
            color_content,
            text="💾 Guardar Cambios",
            height=40,
            font=("Arial", 13, "bold"),
            corner_radius=10,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            command=self.save_avatar_changes
        ).pack(fill="x", pady=(15, 0))
    
    def remove_avatar_image(self):
        """Eliminar imagen de avatar y volver a color"""
        if messagebox.askyesno("Confirmar", "¿Eliminar la imagen del avatar y usar color sólido?"):
            try:
                # Eliminar de la base de datos
                username = self.user['username']
                result = self.auth_manager.remove_user_avatar_image(username)
                
                if result['success']:
                    # Limpiar variables locales
                    self.selected_image = None
                    self.image_path = None
                    
                    # Actualizar preview
                    self.update_avatar_preview()
                    
                    # Recrear la sección de color picker para mostrar los colores
                    # Necesitamos recrear todo el diálogo
                    messagebox.showinfo("Éxito", "Imagen eliminada. Vuelve a abrir este panel para seleccionar un color.")
                    
                    # Recargar y cerrar
                    if self.on_update_callback:
                        self.on_update_callback('reload', None)
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", result.get('message', 'Error al eliminar imagen'))
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar imagen: {e}")
    
    def upload_avatar_image(self):
        """Upload avatar image from device"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen de avatar",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            try:
                from PIL import Image
                from io import BytesIO
                
                # Load and resize image
                img = Image.open(file_path)
                img = img.convert('RGB')  # Ensure RGB mode
                
                # Resize to 300x300 to save space
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Convert to bytes
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=85)
                img_bytes = img_byte_arr.getvalue()
                
                # Store temporarily
                self.selected_image = img_bytes
                self.image_path = file_path
                
                # Update avatar preview
                self.update_avatar_preview()
                
                messagebox.showinfo("Éxito", "Imagen cargada. Presiona 'Guardar Cambios' para aplicar.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar imagen: {e}")
    
    def update_avatar_preview(self):
        """Update avatar preview with new image"""
        try:
            from PIL import Image, ImageDraw
            from io import BytesIO
            
            # Destroy old label
            if hasattr(self, 'avatar_label'):
                self.avatar_label.destroy()
            
            if self.selected_image:
                img = Image.open(BytesIO(self.selected_image))
                img = img.resize((160, 160), Image.Resampling.LANCZOS)
                
                # Create circular mask
                mask = Image.new('L', (160, 160), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 160, 160), fill=255)
                img.putalpha(mask)
                
                ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 160))
                
                self.avatar_label = ctk.CTkLabel(
                    self.avatar_frame,
                    image=ctk_image,
                    text=""
                )
                self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                self.show_initials_avatar()
                
        except Exception as e:
            print(f"Error updating preview: {e}")
            self.show_initials_avatar()
    
    def select_color(self, color, button):
        """Handle color selection"""
        self.selected_color = color
        
        # Update avatar color
        self.avatar_frame.configure(fg_color=color)
        
        # Remove all selection indicators
        for btn in self.color_buttons:
            if hasattr(btn, 'indicator'):
                btn.indicator.destroy()
                delattr(btn, 'indicator')
        
        # Add selection indicator to clicked button
        indicator = ctk.CTkFrame(
            button,
            fg_color="transparent",
            border_color="white",
            border_width=4,
            corner_radius=35,
            width=70,
            height=70
        )
        indicator.place(relx=0, rely=0)
        button.indicator = indicator
    
    def save_avatar_changes(self):
        """Save avatar color and image to database"""
        try:
            username = self.user['username']
            
            print(f"🔄 Guardando cambios de avatar para: {username}")
            print(f"   - Color seleccionado: {self.selected_color}")
            print(f"   - Tiene nueva imagen: {bool(self.image_path)}")
            print(f"   - Tiene imagen actual: {bool(self.selected_image)}")
            
            # Save color
            color_result = self.auth_manager.update_user_avatar_color(username, self.selected_color)
            print(f"   - Resultado guardar color: {color_result}")
            
            # Save image if changed
            if self.image_path:  # New image was selected
                print(f"   - Guardando nueva imagen ({len(self.selected_image)} bytes)...")
                image_result = self.auth_manager.update_user_avatar_image(username, self.selected_image)
                print(f"   - Resultado guardar imagen: {image_result}")
                
                if image_result['success'] and color_result['success']:
                    messagebox.showinfo("Éxito", "Avatar actualizado correctamente")
                    if self.on_update_callback:
                        self.on_update_callback('reload', None)
                else:
                    messagebox.showerror("Error", "Error al guardar algunos cambios")
            else:
                # Only color was changed
                if color_result['success']:
                    messagebox.showinfo("Éxito", "Color de avatar actualizado")
                    if self.on_update_callback:
                        self.on_update_callback('reload', None)
                else:
                    messagebox.showerror("Error", color_result['message'])
                    
        except Exception as e:
            print(f"❌ Error al guardar cambios: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al guardar cambios: {e}")
    
    def create_user_info_section(self, parent):
        """Create user information section"""
        info_section = ctk.CTkFrame(parent, fg_color=("#1a1a1a", "#1a1a1a"), corner_radius=15)
        info_section.pack(fill="x", pady=(0, 20))
        
        info_content = ctk.CTkFrame(info_section, fg_color="transparent")
        info_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Info items
        info_items = [
            ("📅", "Fecha de Creación", self.user.get('fecha_creacion', 'N/A')),
            ("🕐", "Último Acceso", self.format_datetime(self.user.get('ultimo_acceso'))),
            ("🛡️", "Intentos Fallidos", str(self.user.get('intentos_fallidos', 0))),
            ("👥", "ID de Usuario", f"#{self.user['id_usuario']}")
        ]
        
        for icon, label, value in info_items:
            self.create_info_item(info_content, icon, label, value)
    
    def create_info_item(self, parent, icon, label, value):
        """Create an info item row"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", pady=8)
        
        # Icon and label
        left_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        left_frame.pack(side="left")
        
        ctk.CTkLabel(
            left_frame,
            text=icon,
            font=("Arial", 16),
            text_color="gray60"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            left_frame,
            text=label,
            font=("Arial", 12),
            text_color="gray60"
        ).pack(side="left")
        
        # Value
        ctk.CTkLabel(
            item_frame,
            text=str(value),
            font=("Arial", 12, "bold"),
            text_color="white"
        ).pack(side="right")
    
    def format_datetime(self, dt):
        """Format datetime for display"""
        if dt and isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M")
        return "Nunca"
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        # Edit button
        ctk.CTkButton(
            parent,
            text="✏️  Editar Usuario",
            height=55,
            font=("Arial", 14, "bold"),
            corner_radius=12,
            fg_color=("#3a3a3a", "#3a3a3a"),
            hover_color=COLORS['primary'],
            command=self.open_edit_dialog
        ).pack(fill="x", pady=(0, 10))
        
        # Deactivate button (if user is active)
        if self.user['activo']:
            ctk.CTkButton(
                parent,
                text="🎯  Desactivar Usuario",
                height=55,
                font=("Arial", 14, "bold"),
                corner_radius=12,
                fg_color=("#8b7a3d", "#8b7a3d"),
                hover_color=("#9b8a4d", "#9b8a4d"),
                text_color="#FFD700",
                command=self.toggle_user_status
            ).pack(fill="x", pady=(0, 10))
        else:
            ctk.CTkButton(
                parent,
                text="✅  Activar Usuario",
                height=55,
                font=("Arial", 14, "bold"),
                corner_radius=12,
                fg_color=COLORS['success'],
                hover_color=COLORS['success_hover'],
                command=self.toggle_user_status
            ).pack(fill="x", pady=(0, 10))
        
        # Delete button
        ctk.CTkButton(
            parent,
            text="🗑️  Eliminar Usuario",
            height=55,
            font=("Arial", 14, "bold"),
            corner_radius=12,
            fg_color=("#6b2020", "#6b2020"),
            hover_color=COLORS['accent'],
            text_color="#ff6b6b",
            command=self.delete_user
        ).pack(fill="x")
    
    def open_edit_dialog(self):
        """Open the edit user dialog"""
        self.dialog.destroy()
        if self.on_update_callback:
            self.on_update_callback('edit', self.user)
    
    def toggle_user_status(self):
        """Toggle user active/inactive status"""
        new_status = not self.user['activo']
        status_text = "activar" if new_status else "desactivar"
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de {status_text} a '{self.user['username']}'?"):
            messagebox.showinfo("Éxito", f"Usuario {status_text}do correctamente.")
            self.dialog.destroy()
            if self.on_update_callback:
                self.on_update_callback('reload', None)
    
    def delete_user(self):
        """Delete user"""
        if messagebox.askyesno("CONFIRMAR ELIMINACIÓN", 
                              f"¿Está ABSOLUTAMENTE SEGURO de que desea eliminar al usuario '{self.user['username']}'?\n\n" +
                              "Esta acción NO SE PUEDE DESHACER."):
            if self.on_update_callback:
                self.dialog.destroy()
                self.on_update_callback('delete', self.user)


class UserDialog:
    """Modern dialog for creating/editing users"""
    
    def __init__(self, parent, title, auth_manager, user_data=None):
        self.result = False
        self.auth_manager = auth_manager
        self.editing = user_data is not None
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.username_var = ctk.StringVar(value=user_data.get('username', '') if user_data else '')
        self.fullname_var = ctk.StringVar(value=user_data.get('nombre_completo', '') if user_data else '')
        self.password_var = ctk.StringVar()
        self.confirm_password_var = ctk.StringVar()
        self.role_var = ctk.StringVar(value=user_data.get('rol', 'usuario') if user_data else 'usuario')
        self.active_var = ctk.BooleanVar(value=user_data.get('activo', True) if user_data else True)

        # ✅ FIX: Store widget references for PyInstaller compatibility
        self.username_entry = None
        self.fullname_entry = None
        self.password_entry = None
        self.confirm_password_entry = None

        self.setup_dialog()
        self.center_dialog()
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
    
    def setup_dialog(self):
        """Setup dialog interface"""
        main_frame = ctk.CTkFrame(self.dialog, fg_color=("#2a2a2a", "#2a2a2a"))
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title_text = "Editar Usuario" if self.editing else "Crear Nuevo Usuario"
        ctk.CTkLabel(
            content,
            text=title_text,
            font=("Arial", 24, "bold"),
            text_color="white"
        ).pack(pady=(0, 25))
        
        # Username field
        ctk.CTkLabel(content, text="Nombre de Usuario:", font=("Arial", 12, "bold"), text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        self.username_entry = create_entry(content, self.username_var, "Ingrese username")
        self.username_entry.pack(fill="x", pady=(0, 15))

        if self.editing:
            self.username_entry.configure(state="disabled")

        # Full name field
        ctk.CTkLabel(content, text="Nombre Completo:", font=("Arial", 12, "bold"), text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
        self.fullname_entry = create_entry(content, self.fullname_var, "Ingrese nombre completo")
        self.fullname_entry.pack(fill="x", pady=(0, 15))

        # Password fields
        if not self.editing:
            ctk.CTkLabel(content, text="Contraseña:", font=("Arial", 12, "bold"), text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
            self.password_entry = create_entry(content, self.password_var, "Mínimo 8 caracteres", show="●")
            self.password_entry.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(content, text="Confirmar Contraseña:", font=("Arial", 12, "bold"), text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
            self.confirm_password_entry = create_entry(content, self.confirm_password_var, "Repita la contraseña", show="●")
            self.confirm_password_entry.pack(fill="x", pady=(0, 15))
        else:
            # Option to change password
            self.change_password_var = ctk.BooleanVar()
            ctk.CTkCheckBox(
                content,
                text="Cambiar contraseña",
                variable=self.change_password_var,
                font=FONTS['body'],
                command=self.toggle_password_fields
            ).pack(anchor="w", pady=(0, 10))
            
            self.password_frame = ctk.CTkFrame(content, fg_color="transparent")
            self.password_frame.pack(fill="x")
        
        # Role selection (usando CTkOptionMenu para compatibilidad con PyInstaller)
        ctk.CTkLabel(content, text="Rol:", font=("Arial", 12, "bold"), text_color="white", anchor="w").pack(fill="x", pady=(0, 5))

        # Mapeo de valores para el dropdown
        role_display_map = {
            "usuario": "Usuario",
            "admin": "Administrador",
            "supervisor": "Supervisor"
        }

        # Valor actual para mostrar
        current_role_display = role_display_map.get(self.role_var.get(), "Usuario")

        role_menu = ctk.CTkOptionMenu(
            content,
            values=list(role_display_map.values()),
            command=lambda choice: self.role_var.set(
                [k for k, v in role_display_map.items() if v == choice][0]
            ),
            height=45,
            corner_radius=10,
            fg_color=("#1a1a1a", "#1a1a1a"),
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_hover'],
            font=FONTS['body']
        )
        role_menu.set(current_role_display)
        role_menu.pack(fill="x", pady=(0, 15))
        
        # Active checkbox
        if self.editing:
            ctk.CTkCheckBox(
                content,
                text="Usuario activo",
                variable=self.active_var,
                font=FONTS['body']
            ).pack(anchor="w", pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.dialog.destroy,
            height=50,
            font=FONTS['button'],
            corner_radius=10,
            fg_color="gray50",
            hover_color="gray40"
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        save_text = "Actualizar" if self.editing else "Crear"
        ctk.CTkButton(
            button_frame,
            text=save_text,
            command=self.save_user,
            height=50,
            font=FONTS['button'],
            corner_radius=10,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover']
        ).pack(side="right", expand=True, fill="x", padx=(5, 0))
    
    def toggle_password_fields(self):
        """Show/hide password fields when editing"""
        if not self.editing:
            return
        
        for widget in self.password_frame.winfo_children():
            widget.destroy()
        
        if self.change_password_var.get():
            ctk.CTkLabel(self.password_frame, text="Nueva Contraseña:", font=("Arial", 12, "bold"), text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
            create_entry(self.password_frame, self.password_var, "Mínimo 8 caracteres", show="●").pack(fill="x", pady=(0, 10))
            
            ctk.CTkLabel(self.password_frame, text="Confirmar Nueva Contraseña:", font=("Arial", 12, "bold"), text_color="white", anchor="w").pack(fill="x", pady=(0, 5))
            create_entry(self.password_frame, self.confirm_password_var, "Repita la contraseña", show="●").pack(fill="x")
    
    def validate_input(self):
        """Validate user input"""
        # ✅ FIX: Read directly from entry widgets for PyInstaller compatibility
        username = self.username_entry.get().strip() if self.username_entry else self.username_var.get().strip()
        fullname = self.fullname_entry.get().strip() if self.fullname_entry else self.fullname_var.get().strip()
        password = self.password_entry.get() if self.password_entry else self.password_var.get()
        confirm_password = self.confirm_password_entry.get() if self.confirm_password_entry else self.confirm_password_var.get()

        if not username:
            messagebox.showerror("Error", "El nombre de usuario es requerido.")
            return False

        if not fullname:
            messagebox.showerror("Error", "El nombre completo es requerido.")
            return False
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            messagebox.showerror("Error", "El nombre de usuario solo puede contener letras, números y guiones bajos.")
            return False
        
        if len(username) < 3:
            messagebox.showerror("Error", "El nombre de usuario debe tener al menos 3 caracteres.")
            return False
        
        need_password = not self.editing or (self.editing and hasattr(self, 'change_password_var') and self.change_password_var.get())
        
        if need_password:
            if not password:
                messagebox.showerror("Error", "La contraseña es requerida.")
                return False
            
            if len(password) < 8:
                messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres.")
                return False
            
            if password != confirm_password:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return False
        
        return True
    
    def save_user(self):
        """Save user data"""
        if not self.validate_input():
            return

        try:
            # ✅ FIX: Read directly from entry widgets for PyInstaller compatibility
            username = self.username_entry.get().strip() if self.username_entry else self.username_var.get().strip()
            fullname = self.fullname_entry.get().strip() if self.fullname_entry else self.fullname_var.get().strip()
            password = self.password_entry.get() if self.password_entry else self.password_var.get()
            role = self.role_var.get()
            active = self.active_var.get() if self.editing else True
            
            if self.editing:
                result = self.auth_manager.update_user(
                    username, fullname, role, active,
                    password if hasattr(self, 'change_password_var') and self.change_password_var.get() else None
                )
            else:
                result = self.auth_manager.create_user(username, password, fullname, role)
            
            if result['success']:
                self.result = True
                messagebox.showinfo("Éxito", result['message'])
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", result['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar usuario: {e}")


def main(user_data=None):
    """Main function to run the user manager"""
    if isinstance(user_data, str):
        import json
        try:
            user_data = json.loads(user_data)
        except:
            user_data = {}
    
    root = ctk.CTk()
    app = UserManagerApp(root, user_data)
    root.mainloop()


if __name__ == "__main__":
    test_user_data = {
        'username': 'jared',
        'nombre_completo': 'Jared (Administrador)',
        'rol': 'admin'
    }
    main(test_user_data)