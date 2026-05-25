# -*- coding: utf-8 -*-
"""
User Detail Dialog
Dialog for viewing and customizing user details
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Optional, Callable
from io import BytesIO

from ...domain.models import User
from ...business.user_service import UserService


class UserDetailDialog:
    """Dialog for viewing user details and customizing avatar"""
    
    AVATAR_COLORS = [
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
    
    def __init__(
        self,
        parent,
        user: User,
        service: UserService,
        on_action: Optional[Callable] = None,
        colors: Optional[dict] = None
    ):
        """
        Initialize dialog
        
        Args:
            parent: Parent window
            user: User to display
            service: UserService instance
            on_action: Callback for actions (edit, delete, reload)
            colors: Theme colors dict
        """
        self.parent = parent
        self.user = user
        self.service = service
        self.on_action = on_action
        
        self.colors = colors or {
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'success': '#10b981',
            'success_hover': '#059669',
            'accent': '#ef4444'
        }
        
        # Avatar state
        self.selected_color = None
        self.selected_image = None
        self.color_buttons = []
        
        self._load_avatar_data()
        self._create_dialog()
    
    def _load_avatar_data(self):
        """Load user avatar data"""
        try:
            avatar_data = self.service.get_avatar_data(self.user.username)
            self.selected_color = avatar_data.get('color') or self.user.default_avatar_color
            self.selected_image = avatar_data.get('imagen')
        except Exception as e:
            print(f"Error loading avatar data: {e}")
            self.selected_color = self.user.default_avatar_color
    
    def _create_dialog(self):
        """Create and show dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Detalles del Usuario")
        self.dialog.geometry("800x650")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"800x650+{x}+{y}")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI"""
        main_frame = ctk.CTkFrame(self.dialog, fg_color=("#2a2a2a", "#2a2a2a"))
        main_frame.pack(fill="both", expand=True)
        
        content = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header with avatar
        self._create_header(content)
        
        # Color picker section
        self._create_color_picker(content)
        
        # User info section
        self._create_info_section(content)
        
        # Action buttons
        self._create_action_buttons(content)
    
    def _create_header(self, parent):
        """Create header with avatar"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 30))
        
        # Avatar container
        avatar_container = ctk.CTkFrame(header, fg_color="transparent")
        avatar_container.pack()
        
        self.avatar_frame = ctk.CTkFrame(
            avatar_container,
            fg_color=self.selected_color,
            corner_radius=80,
            width=160,
            height=160
        )
        self.avatar_frame.pack()
        self.avatar_frame.pack_propagate(False)
        
        self._update_avatar_display()
        
        # User name
        ctk.CTkLabel(
            header,
            text=self.user.nombre_completo,
            font=("Arial", 24, "bold"),
            text_color="white"
        ).pack(pady=(20, 5))
        
        # Username
        ctk.CTkLabel(
            header,
            text=f"@{self.user.username}",
            font=("Arial", 14),
            text_color="gray60"
        ).pack()
    
    def _update_avatar_display(self):
        """Update avatar display with current image or initials"""
        # Clear existing content
        for widget in self.avatar_frame.winfo_children():
            widget.destroy()
        
        self.avatar_frame.configure(fg_color=self.selected_color)
        
        if self.selected_image:
            try:
                from PIL import Image, ImageDraw
                
                img = Image.open(BytesIO(self.selected_image))
                img = img.resize((160, 160), Image.Resampling.LANCZOS)
                
                # Create circular mask
                mask = Image.new('L', (160, 160), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 160, 160), fill=255)
                
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img.putalpha(mask)
                
                ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 160))
                
                ctk.CTkLabel(
                    self.avatar_frame,
                    image=ctk_image,
                    text=""
                ).place(relx=0.5, rely=0.5, anchor="center")
                
            except Exception as e:
                print(f"Error loading avatar image: {e}")
                self._show_initials()
        else:
            self._show_initials()
    
    def _show_initials(self):
        """Show initials in avatar"""
        ctk.CTkLabel(
            self.avatar_frame,
            text=self.user.initials,
            font=("Arial", 56, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
    
    def _create_color_picker(self, parent):
        """Create color picker section"""
        section = ctk.CTkFrame(parent, fg_color=("#1a1a1a", "#1a1a1a"), corner_radius=15)
        section.pack(fill="x", pady=(0, 20))
        
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=20)
        
        # Title row
        title_row = ctk.CTkFrame(content, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            title_row,
            text="Personalizar Avatar",
            font=("Arial", 16, "bold"),
            text_color="white",
            anchor="w"
        ).pack(side="left")
        
        # Buttons
        buttons_frame = ctk.CTkFrame(title_row, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        # Remove image button (only if image exists)
        if self.selected_image:
            ctk.CTkButton(
                buttons_frame,
                text="🗑️ Eliminar Foto",
                width=130,
                height=35,
                corner_radius=10,
                fg_color=self.colors['accent'],
                hover_color="#c53030",
                command=self._remove_image
            ).pack(side="left", padx=(0, 10))
        
        # Upload image button
        ctk.CTkButton(
            buttons_frame,
            text="📷 Subir Foto",
            width=120,
            height=35,
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            command=self._upload_image
        ).pack(side="left")
        
        # Color palette (only if no image)
        if not self.selected_image:
            ctk.CTkLabel(
                content,
                text="Color de Fondo:",
                font=("Arial", 12),
                text_color="gray60",
                anchor="w"
            ).pack(anchor="w", pady=(10, 10))
            
            palette = ctk.CTkFrame(content, fg_color="transparent")
            palette.pack(fill="x")
            
            self.color_buttons = []
            
            for i, color in enumerate(self.AVATAR_COLORS):
                col = i % 5
                row = i // 5
                
                btn = ctk.CTkFrame(
                    palette,
                    fg_color=color,
                    corner_radius=35,
                    width=70,
                    height=70,
                    cursor="hand2"
                )
                btn.grid(row=row, column=col, padx=10, pady=10)
                btn.grid_propagate(False)
                
                # Selection indicator
                if color == self.selected_color:
                    indicator = ctk.CTkFrame(
                        btn,
                        fg_color="transparent",
                        border_color="white",
                        border_width=4,
                        corner_radius=35,
                        width=70,
                        height=70
                    )
                    indicator.place(relx=0, rely=0)
                    btn.indicator = indicator
                
                btn.bind("<Button-1>", lambda e, c=color, b=btn: self._select_color(c, b))
                self.color_buttons.append(btn)
        else:
            ctk.CTkLabel(
                content,
                text="✓ Imagen de avatar personalizada cargada",
                font=("Arial", 12),
                text_color=self.colors['success'],
                anchor="w"
            ).pack(anchor="w", pady=(10, 10))
        
        # Save button
        ctk.CTkButton(
            content,
            text="💾 Guardar Cambios",
            height=40,
            font=("Arial", 13, "bold"),
            corner_radius=10,
            fg_color=self.colors['success'],
            hover_color=self.colors['success_hover'],
            command=self._save_avatar
        ).pack(fill="x", pady=(15, 0))
    
    def _select_color(self, color: str, button):
        """Handle color selection"""
        # Remove previous selection
        for btn in self.color_buttons:
            if hasattr(btn, 'indicator'):
                btn.indicator.destroy()
                delattr(btn, 'indicator')
        
        # Add selection to new button
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
        
        self.selected_color = color
        self.avatar_frame.configure(fg_color=color)
    
    def _upload_image(self):
        """Upload avatar image"""
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
                
                img = Image.open(file_path)
                img = img.resize((300, 300), Image.Resampling.LANCZOS)
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save to bytes
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                self.selected_image = buffer.getvalue()
                
                # Update display
                self._update_avatar_display()
                
                # Refresh dialog to show/hide color picker
                messagebox.showinfo("Éxito", "Imagen cargada. Presiona 'Guardar Cambios' para aplicar.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar imagen: {e}")
    
    def _remove_image(self):
        """Remove avatar image"""
        if messagebox.askyesno("Confirmar", "¿Eliminar la imagen del avatar?"):
            result = self.service.remove_avatar_image(self.user.username)
            
            if result['success']:
                self.selected_image = None
                messagebox.showinfo("Éxito", "Imagen eliminada. Reabre el panel para seleccionar un color.")
                
                if self.on_action:
                    self.on_action('reload', None)
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", result['message'])
    
    def _save_avatar(self):
        """Save avatar changes"""
        try:
            if self.selected_image:
                result = self.service.update_avatar_image(self.user.username, self.selected_image)
            else:
                result = self.service.update_avatar_color(self.user.username, self.selected_color)
            
            if result['success']:
                messagebox.showinfo("Éxito", result['message'])
                if self.on_action:
                    self.on_action('reload', None)
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", result['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
    
    def _create_info_section(self, parent):
        """Create user info section"""
        section = ctk.CTkFrame(parent, fg_color=("#1a1a1a", "#1a1a1a"), corner_radius=15)
        section.pack(fill="x", pady=(0, 20))
        
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            content,
            text="Información del Usuario",
            font=("Arial", 16, "bold"),
            text_color="white",
            anchor="w"
        ).pack(anchor="w", pady=(0, 15))
        
        # Info grid
        info_data = [
            ("Rol", self.user.rol.upper()),
            ("Estado", self.user.status),
            ("Último acceso", str(self.user.ultimo_acceso) if self.user.ultimo_acceso else "Nunca"),
            ("Intentos fallidos", str(self.user.intentos_fallidos)),
        ]
        
        for label, value in info_data:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=("Arial", 12),
                text_color="gray60",
                width=150,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=("Arial", 12, "bold"),
                text_color="white",
                anchor="w"
            ).pack(side="left")
    
    def _create_action_buttons(self, parent):
        """Create action buttons"""
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Edit button
        ctk.CTkButton(
            buttons_frame,
            text="✏️ Editar Usuario",
            height=45,
            font=("Arial", 13, "bold"),
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            command=self._edit_user
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        # Delete button
        ctk.CTkButton(
            buttons_frame,
            text="🗑️ Eliminar",
            height=45,
            font=("Arial", 13, "bold"),
            corner_radius=10,
            fg_color=self.colors['accent'],
            hover_color="#c53030",
            command=self._delete_user
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        # Close button
        ctk.CTkButton(
            buttons_frame,
            text="Cerrar",
            height=45,
            font=("Arial", 13, "bold"),
            corner_radius=10,
            fg_color="gray50",
            hover_color="gray40",
            command=self.dialog.destroy
        ).pack(side="right", expand=True, fill="x")
    
    def _edit_user(self):
        """Trigger edit action"""
        self.dialog.destroy()
        if self.on_action:
            self.on_action('edit', self.user)
    
    def _delete_user(self):
        """Trigger delete action"""
        self.dialog.destroy()
        if self.on_action:
            self.on_action('delete', self.user)
