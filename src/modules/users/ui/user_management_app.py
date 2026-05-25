# -*- coding: utf-8 -*-
"""
User Management App - Main UI
Main application window for user management
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List, Dict, Any

from ..domain.models import User, UserStats
from ..business.user_service import UserService
from .components.stats_panel import StatsPanel
from .components.user_card import UserCard
from .dialogs.user_form_dialog import UserFormDialog
from .dialogs.user_detail_dialog import UserDetailDialog


class UserManagementApp:
    """Main user management application"""
    
    def __init__(
        self,
        root: ctk.CTk,
        service: UserService,
        user_data: Optional[Dict] = None,
        colors: Optional[Dict] = None,
        fonts: Optional[Dict] = None,
        on_close: Optional[callable] = None
    ):
        """
        Initialize application
        
        Args:
            root: CTk root window
            service: UserService instance
            user_data: Current logged user data
            colors: Theme colors
            fonts: Theme fonts
            on_close: Callback when window closes
        """
        self.root = root
        self.service = service
        self.user_data = user_data or {}
        self.on_close = on_close
        
        # Theme
        self.colors = colors or {
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'success': '#10b981',
            'success_hover': '#059669',
            'accent': '#ef4444'
        }
        self.fonts = fonts or {
            'title': ("Arial", 16, "bold"),
            'body': ("Arial", 12),
            'button': ("Arial", 13, "bold")
        }
        
        # State
        self.all_users: List[User] = []
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self._on_filter_change)
        self.role_filter_var = ctk.StringVar(value="Todos los roles")
        self.status_filter_var = ctk.StringVar(value="Todos los estados")
        
        # Check permissions
        if not self._check_admin_permission():
            return
        
        # Setup
        self._configure_window()
        self._setup_ui()
        self._load_users()
        
        # Window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _check_admin_permission(self) -> bool:
        """Check if current user has admin permissions"""
        if self.user_data.get('rol', '') != 'admin':
            messagebox.showerror("Acceso Denegado", "Este módulo requiere permisos de administrador.")
            self.root.destroy()
            return False
        return True
    
    def _configure_window(self):
        """Configure main window"""
        self.root.title("Administrador de Usuarios - Disfruleg")
        self.root.geometry("1400x900")
        
        # Bring to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()
    
    def _setup_ui(self):
        """Setup main UI"""
        # Main container
        main = ctk.CTkFrame(self.root, fg_color=("#1a1a1a", "#1a1a1a"))
        main.pack(fill="both", expand=True)
        
        # Header
        self._create_header(main)
        
        # Content
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Stats panel
        self.stats_panel = StatsPanel(content)
        self.stats_panel.pack(fill="x", pady=(0, 20))
        
        # Filters
        self._create_filters(content)
        
        # Users grid
        self._create_users_grid(content)
    
    def _create_header(self, parent):
        """Create header section"""
        header = ctk.CTkFrame(parent, fg_color=("#1a1a1a", "#1a1a1a"), height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        content = ctk.CTkFrame(header, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30)
        
        # Left side
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="y")
        
        # Back button
        ctk.CTkButton(
            left,
            text="⎋",
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors['accent'],
            font=("Arial", 20),
            text_color="white",
            command=self._on_closing
        ).pack(side="left", padx=(0, 15))
        
        # Logo
        ctk.CTkLabel(
            left,
            text="👤",
            font=("Arial", 28)
        ).pack(side="left", padx=(0, 15))
        
        # Title
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="ADMINISTRADOR DE USUARIOS",
            font=self.fonts['title'],
            text_color=self.colors['success'],
            anchor="w"
        ).pack(anchor="w")
        
        user_info = f"Usuario: {self.user_data.get('nombre_completo', 'Admin')} | Rol: {self.user_data.get('rol', 'admin').upper()}"
        ctk.CTkLabel(
            title_frame,
            text=user_info,
            font=("Arial", 10),
            text_color="gray60",
            anchor="w"
        ).pack(anchor="w")
        
        # Create user button
        ctk.CTkButton(
            content,
            text="Crear Usuario",
            width=160,
            height=45,
            corner_radius=10,
            fg_color=self.colors['success'],
            hover_color=self.colors['success_hover'],
            font=self.fonts['button'],
            command=self._create_user
        ).pack(side="right")
    
    def _create_filters(self, parent):
        """Create filters bar"""
        filters = ctk.CTkFrame(parent, fg_color=("#2a2a2a", "#2a2a2a"), corner_radius=15)
        filters.pack(fill="x", pady=(0, 20))
        
        content = ctk.CTkFrame(filters, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)
        
        # Search bar
        search_frame = ctk.CTkFrame(content, fg_color=("#1a1a1a", "#1a1a1a"), corner_radius=10)
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Arial", 14),
            text_color="gray"
        ).pack(side="left", padx=(15, 5))
        
        ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Buscar usuario...",
            fg_color="transparent",
            border_width=0,
            font=("Arial", 12),
            text_color="white"
        ).pack(side="left", fill="x", expand=True, padx=(0, 15), pady=10)
        
        # Role filter
        ctk.CTkLabel(
            content,
            text="Rol:",
            font=("Arial", 11),
            text_color="gray60"
        ).pack(side="left", padx=(0, 10))
        
        role_menu = ctk.CTkOptionMenu(
            content,
            values=["Todos los roles", "Admin", "Usuario", "Supervisor"],
            variable=self.role_filter_var,
            width=180,
            height=40,
            corner_radius=10,
            fg_color=("#1a1a1a", "#1a1a1a"),
            button_color=self.colors['primary'],
            button_hover_color=self.colors['primary_hover'],
            command=lambda x: self._on_filter_change()
        )
        role_menu.pack(side="left", padx=(0, 15))
        
        # Status filter
        ctk.CTkLabel(
            content,
            text="Estado:",
            font=("Arial", 11),
            text_color="gray60"
        ).pack(side="left", padx=(0, 10))
        
        status_menu = ctk.CTkOptionMenu(
            content,
            values=["Todos los estados", "Activo", "Inactivo", "Bloqueado"],
            variable=self.status_filter_var,
            width=180,
            height=40,
            corner_radius=10,
            fg_color=("#1a1a1a", "#1a1a1a"),
            button_color=self.colors['primary'],
            button_hover_color=self.colors['primary_hover'],
            command=lambda x: self._on_filter_change()
        )
        status_menu.pack(side="left")
    
    def _create_users_grid(self, parent):
        """Create scrollable users grid"""
        self.users_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.users_scroll.pack(fill="both", expand=True)
        
        # Configure grid columns
        for i in range(3):
            self.users_scroll.grid_columnconfigure(i, weight=1, uniform="column")
    
    def _load_users(self):
        """Load users from service"""
        try:
            self.all_users = self.service.get_all_users()
            
            # Update stats
            stats = self.service.get_statistics(self.all_users)
            self.stats_panel.update_stats(stats)
            
            # Display users
            self._display_users(self.all_users)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
    
    def _display_users(self, users: List[User]):
        """Display user cards in grid"""
        # Clear existing
        for widget in self.users_scroll.winfo_children():
            widget.destroy()
        
        row, col = 0, 0
        max_cols = 3
        
        for user in users:
            # Get avatar data
            avatar_data = self.service.get_avatar_data(user.username)
            
            card = UserCard(
                self.users_scroll,
                user=user,
                avatar_color=avatar_data.get('color'),
                avatar_image=avatar_data.get('imagen'),
                on_edit=self._show_user_detail,
                on_delete=self._delete_user,
                on_unblock=self._unblock_user,
                colors=self.colors
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def _on_filter_change(self, *args):
        """Handle filter changes"""
        filtered = self.service.filter_users(
            self.all_users,
            search_text=self.search_var.get(),
            role_filter=self.role_filter_var.get(),
            status_filter=self.status_filter_var.get()
        )
        self._display_users(filtered)
    
    def _show_user_detail(self, user: User):
        """Show user detail dialog"""
        def handle_action(action: str, data):
            if action == 'edit':
                self._edit_user(data)
            elif action == 'delete':
                self._delete_user(data)
            elif action == 'reload':
                self._load_users()
        
        UserDetailDialog(
            self.root,
            user=user,
            service=self.service,
            on_action=handle_action,
            colors=self.colors
        )
    
    def _create_user(self):
        """Create new user"""
        dialog = UserFormDialog(
            self.root,
            service=self.service,
            colors=self.colors,
            fonts=self.fonts
        )
        if dialog.result:
            self._load_users()
    
    def _edit_user(self, user: User):
        """Edit existing user"""
        dialog = UserFormDialog(
            self.root,
            service=self.service,
            user=user,
            colors=self.colors,
            fonts=self.fonts
        )
        if dialog.result:
            self._load_users()
    
    def _delete_user(self, user: User):
        """Delete user"""
        current_username = self.user_data.get('username', '')
        
        if user.username == current_username:
            messagebox.showwarning("Advertencia", "No puede eliminar su propia cuenta.")
            return
        
        if not messagebox.askyesno(
            "CONFIRMAR ELIMINACIÓN",
            f"¿Está ABSOLUTAMENTE SEGURO de que desea eliminar al usuario '{user.username}'?\n\n"
            "Esta acción NO SE PUEDE DESHACER."
        ):
            return
        
        result = self.service.delete_user(user.id_usuario, current_username)
        
        if result['success']:
            messagebox.showinfo("Éxito", result['message'])
            self._load_users()
        else:
            messagebox.showerror("Error", result['message'])
    
    def _unblock_user(self, user: User):
        """Unblock user"""
        if not messagebox.askyesno("Confirmar", f"¿Desbloquear usuario '{user.username}'?"):
            return
        
        result = self.service.unblock_user(user.id_usuario)
        
        if result['success']:
            messagebox.showinfo("Éxito", result['message'])
            self._load_users()
        else:
            messagebox.showerror("Error", result['message'])
    
    def _on_closing(self):
        """Handle window closing"""
        if self.on_close:
            self.on_close()
        self.root.destroy()
