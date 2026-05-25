# -*- coding: utf-8 -*-
"""
User Form Dialog
Dialog for creating and editing users
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, Any, Callable

from ...domain.models import User, UserCreateData, UserUpdateData
from ...business.user_service import UserService


class UserFormDialog:
    """Dialog for creating or editing users"""
    
    ROLE_DISPLAY_MAP = {
        "usuario": "Usuario",
        "admin": "Administrador",
        "supervisor": "Supervisor"
    }
    
    def __init__(
        self,
        parent,
        service: UserService,
        user: Optional[User] = None,
        colors: Optional[dict] = None,
        fonts: Optional[dict] = None
    ):
        """
        Initialize dialog
        
        Args:
            parent: Parent window
            service: UserService instance
            user: User to edit (None for create)
            colors: Theme colors dict
            fonts: Theme fonts dict
        """
        self.parent = parent
        self.service = service
        self.user = user
        self.editing = user is not None
        self.result = False
        
        self.colors = colors or {
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'success': '#10b981',
            'success_hover': '#059669',
            'accent': '#ef4444'
        }
        self.fonts = fonts or {
            'body': ("Arial", 12),
            'button': ("Arial", 13, "bold")
        }
        
        # Form variables
        self.username_var = ctk.StringVar(value=user.username if user else "")
        self.fullname_var = ctk.StringVar(value=user.nombre_completo if user else "")
        self.password_var = ctk.StringVar()
        self.confirm_password_var = ctk.StringVar()
        self.role_var = ctk.StringVar(value=user.rol if user else "usuario")
        self.active_var = ctk.BooleanVar(value=user.activo if user else True)
        
        # Entry references
        self.username_entry = None
        self.fullname_entry = None
        self.password_entry = None
        self.confirm_password_entry = None
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create and show dialog"""
        title = "Editar Usuario" if self.editing else "Crear Nuevo Usuario"
        
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("450x550")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"450x550+{x}+{y}")
        
        self._setup_ui()
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
    
    def _setup_ui(self):
        """Setup dialog UI"""
        main_frame = ctk.CTkFrame(self.dialog, fg_color=("#2a2a2a", "#2a2a2a"))
        main_frame.pack(fill="both", expand=True)
        
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title_text = "Editar Usuario" if self.editing else "Nuevo Usuario"
        ctk.CTkLabel(
            content,
            text=title_text,
            font=("Arial", 20, "bold"),
            text_color="white"
        ).pack(pady=(0, 25))
        
        # Username field
        self._create_field(content, "Nombre de Usuario:", self.username_var, 
                          "Ej: juan_perez", disabled=self.editing)
        
        # Full name field
        self._create_field(content, "Nombre Completo:", self.fullname_var, 
                          "Ej: Juan Pérez García")
        
        # Password fields
        if not self.editing:
            self._create_field(content, "Contraseña:", self.password_var, 
                              "Mínimo 8 caracteres", show="●")
            self._create_field(content, "Confirmar Contraseña:", self.confirm_password_var, 
                              "Repita la contraseña", show="●")
        else:
            # Change password checkbox
            self.change_password_var = ctk.BooleanVar()
            ctk.CTkCheckBox(
                content,
                text="Cambiar contraseña",
                variable=self.change_password_var,
                font=self.fonts['body'],
                command=self._toggle_password_fields
            ).pack(anchor="w", pady=(0, 10))
            
            self.password_frame = ctk.CTkFrame(content, fg_color="transparent")
            self.password_frame.pack(fill="x")
        
        # Role selection
        self._create_role_selector(content)
        
        # Active checkbox (only for edit)
        if self.editing:
            ctk.CTkCheckBox(
                content,
                text="Usuario activo",
                variable=self.active_var,
                font=self.fonts['body']
            ).pack(anchor="w", pady=(0, 15))
        
        # Buttons
        self._create_buttons(content)
    
    def _create_field(
        self,
        parent,
        label: str,
        variable: ctk.StringVar,
        placeholder: str,
        show: str = None,
        disabled: bool = False
    ):
        """Create a form field"""
        ctk.CTkLabel(
            parent,
            text=label,
            font=("Arial", 12, "bold"),
            text_color="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,
            placeholder_text=placeholder,
            height=45,
            corner_radius=10,
            font=self.fonts['body'],
            fg_color=("#1a1a1a", "#1a1a1a"),
            border_color=self.colors['primary'],
            show=show if show else ""
        )
        entry.pack(fill="x", pady=(0, 15))
        
        if disabled:
            entry.configure(state="disabled")
        
        # Store reference
        if "Usuario:" in label:
            self.username_entry = entry
        elif "Completo" in label:
            self.fullname_entry = entry
        elif "Contraseña:" in label and "Confirmar" not in label:
            self.password_entry = entry
        elif "Confirmar" in label:
            self.confirm_password_entry = entry
        
        return entry
    
    def _create_role_selector(self, parent):
        """Create role selection dropdown"""
        ctk.CTkLabel(
            parent,
            text="Rol:",
            font=("Arial", 12, "bold"),
            text_color="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        current_display = self.ROLE_DISPLAY_MAP.get(self.role_var.get(), "Usuario")
        
        role_menu = ctk.CTkOptionMenu(
            parent,
            values=list(self.ROLE_DISPLAY_MAP.values()),
            command=self._on_role_change,
            height=45,
            corner_radius=10,
            fg_color=("#1a1a1a", "#1a1a1a"),
            button_color=self.colors['primary'],
            button_hover_color=self.colors['primary_hover'],
            font=self.fonts['body']
        )
        role_menu.set(current_display)
        role_menu.pack(fill="x", pady=(0, 15))
    
    def _on_role_change(self, choice: str):
        """Handle role selection change"""
        for key, value in self.ROLE_DISPLAY_MAP.items():
            if value == choice:
                self.role_var.set(key)
                break
    
    def _toggle_password_fields(self):
        """Show/hide password fields when editing"""
        for widget in self.password_frame.winfo_children():
            widget.destroy()
        
        if self.change_password_var.get():
            ctk.CTkLabel(
                self.password_frame,
                text="Nueva Contraseña:",
                font=("Arial", 12, "bold"),
                text_color="white",
                anchor="w"
            ).pack(fill="x", pady=(0, 5))
            
            self.password_entry = ctk.CTkEntry(
                self.password_frame,
                textvariable=self.password_var,
                placeholder_text="Mínimo 8 caracteres",
                height=45,
                corner_radius=10,
                font=self.fonts['body'],
                fg_color=("#1a1a1a", "#1a1a1a"),
                border_color=self.colors['primary'],
                show="●"
            )
            self.password_entry.pack(fill="x", pady=(0, 10))
            
            ctk.CTkLabel(
                self.password_frame,
                text="Confirmar Nueva Contraseña:",
                font=("Arial", 12, "bold"),
                text_color="white",
                anchor="w"
            ).pack(fill="x", pady=(0, 5))
            
            self.confirm_password_entry = ctk.CTkEntry(
                self.password_frame,
                textvariable=self.confirm_password_var,
                placeholder_text="Repita la contraseña",
                height=45,
                corner_radius=10,
                font=self.fonts['body'],
                fg_color=("#1a1a1a", "#1a1a1a"),
                border_color=self.colors['primary'],
                show="●"
            )
            self.confirm_password_entry.pack(fill="x")
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.dialog.destroy,
            height=50,
            font=self.fonts['button'],
            corner_radius=10,
            fg_color="gray50",
            hover_color="gray40"
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        save_text = "Actualizar" if self.editing else "Crear"
        ctk.CTkButton(
            button_frame,
            text=save_text,
            command=self._save_user,
            height=50,
            font=self.fonts['button'],
            corner_radius=10,
            fg_color=self.colors['success'],
            hover_color=self.colors['success_hover']
        ).pack(side="right", expand=True, fill="x", padx=(5, 0))
    
    def _get_form_values(self) -> Dict[str, Any]:
        """Get current form values"""
        return {
            'username': self.username_entry.get().strip() if self.username_entry else self.username_var.get().strip(),
            'fullname': self.fullname_entry.get().strip() if self.fullname_entry else self.fullname_var.get().strip(),
            'password': self.password_entry.get() if self.password_entry else self.password_var.get(),
            'confirm_password': self.confirm_password_entry.get() if self.confirm_password_entry else self.confirm_password_var.get(),
            'role': self.role_var.get(),
            'active': self.active_var.get()
        }
    
    def _validate_form(self) -> bool:
        """Validate form data"""
        values = self._get_form_values()
        
        if not values['username']:
            messagebox.showerror("Error", "El nombre de usuario es requerido.")
            return False
        
        if not values['fullname']:
            messagebox.showerror("Error", "El nombre completo es requerido.")
            return False
        
        # Password validation
        need_password = not self.editing or (self.editing and hasattr(self, 'change_password_var') and self.change_password_var.get())
        
        if need_password:
            if not values['password']:
                messagebox.showerror("Error", "La contraseña es requerida.")
                return False
            
            if len(values['password']) < 8:
                messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres.")
                return False
            
            if values['password'] != values['confirm_password']:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return False
        
        return True
    
    def _save_user(self):
        """Save user data"""
        if not self._validate_form():
            return
        
        try:
            values = self._get_form_values()
            
            if self.editing:
                # Determine if password should change
                new_password = None
                if hasattr(self, 'change_password_var') and self.change_password_var.get():
                    new_password = values['password']
                
                data = UserUpdateData(
                    username=values['username'],
                    nombre_completo=values['fullname'],
                    rol=values['role'],
                    activo=values['active'],
                    new_password=new_password
                )
                result = self.service.update_user(data)
            else:
                data = UserCreateData(
                    username=values['username'],
                    password=values['password'],
                    nombre_completo=values['fullname'],
                    rol=values['role']
                )
                result = self.service.create_user(data)
            
            if result['success']:
                self.result = True
                messagebox.showinfo("Éxito", result['message'])
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", result['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar usuario: {e}")
