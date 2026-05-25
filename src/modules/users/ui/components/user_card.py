# -*- coding: utf-8 -*-
"""
User Card Component
Displays individual user information in card format
"""

import customtkinter as ctk
from typing import Callable, Optional
from io import BytesIO

from ...domain.models import User


class UserCard(ctk.CTkFrame):
    """Card component displaying user information"""
    
    def __init__(
        self,
        parent,
        user: User,
        avatar_color: Optional[str] = None,
        avatar_image: Optional[bytes] = None,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_unblock: Optional[Callable] = None,
        colors: Optional[dict] = None,
        **kwargs
    ):
        """
        Initialize user card
        
        Args:
            parent: Parent widget
            user: User object to display
            avatar_color: Custom avatar color
            avatar_image: Avatar image bytes
            on_edit: Callback for edit action
            on_delete: Callback for delete action
            on_unblock: Callback for unblock action
            colors: Theme colors dict
        """
        super().__init__(
            parent,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=20,
            border_width=0,
            **kwargs
        )
        
        self.user = user
        self.avatar_color = avatar_color or user.default_avatar_color
        self.avatar_image = avatar_image
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_unblock = on_unblock
        self.colors = colors or {
            'primary': '#3b82f6',
            'accent': '#ef4444',
            'success': '#10b981'
        }
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup card UI"""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Avatar section
        self._create_avatar(content)
        
        # User name
        ctk.CTkLabel(
            content,
            text=self.user.nombre_completo,
            font=("Arial", 16, "bold"),
            text_color="white",
            anchor="center"
        ).pack(pady=(15, 5))
        
        # Username
        ctk.CTkLabel(
            content,
            text=f"@{self.user.username}",
            font=("Arial", 11),
            text_color="gray60",
            anchor="center"
        ).pack(pady=(0, 10))
        
        # Status badge
        self._create_status_badge(content)
        
        # Role badge
        self._create_role_badge(content)
        
        # Action buttons
        self._create_action_buttons(content)
    
    def _create_avatar(self, parent):
        """Create avatar section"""
        avatar_section = ctk.CTkFrame(parent, fg_color="transparent")
        avatar_section.pack(fill="x")
        
        avatar_container = ctk.CTkFrame(avatar_section, fg_color="transparent")
        avatar_container.pack(anchor="center")
        
        if self.avatar_image:
            self._create_image_avatar(avatar_container)
        else:
            self._create_initials_avatar(avatar_container)
    
    def _create_image_avatar(self, parent):
        """Create avatar with image"""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.open(BytesIO(self.avatar_image))
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            img = img.resize((120, 120), Image.Resampling.LANCZOS)
            
            # Create circular mask
            mask = Image.new('L', (120, 120), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 120, 120), fill=255)
            
            output = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
            output.paste(img, (0, 0))
            output.putalpha(mask)
            
            ctk_image = ctk.CTkImage(
                light_image=output,
                dark_image=output,
                size=(120, 120)
            )
            
            ctk.CTkLabel(
                parent,
                image=ctk_image,
                text="",
                fg_color="transparent"
            ).pack()
            
        except Exception as e:
            print(f"Error loading avatar image: {e}")
            self._create_initials_avatar(parent)
    
    def _create_initials_avatar(self, parent):
        """Create avatar with initials"""
        avatar = ctk.CTkFrame(
            parent,
            fg_color=self.avatar_color,
            corner_radius=60,
            width=120,
            height=120
        )
        avatar.pack()
        avatar.pack_propagate(False)
        
        ctk.CTkLabel(
            avatar,
            text=self.user.initials,
            font=("Arial", 42, "bold"),
            text_color="white",
            fg_color="transparent"
        ).place(relx=0.5, rely=0.5, anchor="center")
    
    def _create_status_badge(self, parent):
        """Create status badge"""
        status_frame = ctk.CTkFrame(
            parent,
            fg_color=self.user.status_color,
            corner_radius=15,
            height=30
        )
        status_frame.pack(fill="x", pady=(0, 10))
        status_frame.pack_propagate(False)
        
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(expand=True)
        
        ctk.CTkLabel(
            status_content,
            text=self.user.status_icon,
            font=("Arial", 12),
            text_color="white"
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            status_content,
            text=self.user.status,
            font=("Arial", 11, "bold"),
            text_color="white"
        ).pack(side="left")
    
    def _create_role_badge(self, parent):
        """Create role badge"""
        role_frame = ctk.CTkFrame(
            parent,
            fg_color=self.user.role_color,
            corner_radius=15,
            height=30
        )
        role_frame.pack(fill="x", pady=(0, 15))
        role_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            role_frame,
            text=self.user.rol.upper(),
            font=("Arial", 10, "bold"),
            text_color="white"
        ).pack(expand=True)
    
    def _create_action_buttons(self, parent):
        """Create action buttons"""
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x")
        
        # Edit button
        ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#3a3a3a", "#3a3a3a"),
            hover_color=self.colors['primary'],
            font=("Arial", 16),
            command=lambda: self.on_edit(self.user) if self.on_edit else None
        ).pack(side="left", expand=True, padx=2)
        
        # Delete button
        ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#3a3a3a", "#3a3a3a"),
            hover_color=self.colors['accent'],
            font=("Arial", 16),
            command=lambda: self.on_delete(self.user) if self.on_delete else None
        ).pack(side="left", expand=True, padx=2)
        
        # Unblock button (only if blocked)
        if self.user.is_blocked and self.on_unblock:
            ctk.CTkButton(
                actions_frame,
                text="🔓",
                width=40,
                height=40,
                corner_radius=10,
                fg_color=("#3a3a3a", "#3a3a3a"),
                hover_color="#9B59B6",
                font=("Arial", 16),
                command=lambda: self.on_unblock(self.user)
            ).pack(side="left", expand=True, padx=2)
