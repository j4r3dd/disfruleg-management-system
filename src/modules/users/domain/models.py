# -*- coding: utf-8 -*-
"""
Domain Models - User Management Module
Core business entities
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class User:
    """Represents a system user"""
    id_usuario: int
    username: str
    nombre_completo: str
    rol: str
    activo: bool
    ultimo_acceso: Optional[datetime] = None
    intentos_fallidos: int = 0
    bloqueado_hasta: Optional[datetime] = None
    avatar_color: Optional[str] = None
    avatar_imagen: Optional[bytes] = None
    
    @property
    def is_blocked(self) -> bool:
        """Check if user is currently blocked"""
        if self.bloqueado_hasta is None:
            return False
        return self.bloqueado_hasta > datetime.now()
    
    @property
    def is_active(self) -> bool:
        """Check if user is active (not blocked and activo=True)"""
        return self.activo and not self.is_blocked
    
    @property
    def status(self) -> str:
        """Get user status string"""
        if self.is_blocked:
            return "Bloqueado"
        elif self.activo:
            return "Activo"
        return "Inactivo"
    
    @property
    def status_color(self) -> str:
        """Get status color for UI"""
        if self.is_blocked:
            return "#ef4444"  # Red
        elif self.activo:
            return "#10b981"  # Green
        return "#6b7280"  # Gray
    
    @property
    def status_icon(self) -> str:
        """Get status icon"""
        if self.is_blocked:
            return "🔒"
        elif self.activo:
            return "✓"
        return "⚠"
    
    @property
    def role_color(self) -> str:
        """Get role badge color"""
        colors = {
            'admin': '#a855f7',
            'usuario': '#f97316',
            'supervisor': '#3b82f6'
        }
        return colors.get(self.rol, '#6b7280')
    
    @property
    def default_avatar_color(self) -> str:
        """Get default avatar color based on role"""
        colors = {
            'admin': '#a855f7',
            'usuario': '#f97316',
            'supervisor': '#06b6d4'
        }
        return self.avatar_color or colors.get(self.rol, '#6b7280')
    
    @property
    def initials(self) -> str:
        """Get user initials for avatar"""
        parts = self.nombre_completo.split()[:2]
        return ''.join([p[0].upper() for p in parts if p])
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id_usuario': self.id_usuario,
            'username': self.username,
            'nombre_completo': self.nombre_completo,
            'rol': self.rol,
            'activo': self.activo,
            'ultimo_acceso': self.ultimo_acceso,
            'intentos_fallidos': self.intentos_fallidos,
            'bloqueado_hasta': self.bloqueado_hasta
        }


@dataclass
class UserStats:
    """Statistics about users"""
    total: int = 0
    active: int = 0
    blocked: int = 0
    admins: int = 0
    
    @classmethod
    def from_users(cls, users: list) -> 'UserStats':
        """Calculate stats from user list"""
        now = datetime.now()
        return cls(
            total=len(users),
            active=sum(1 for u in users if u.is_active),
            blocked=sum(1 for u in users if u.is_blocked),
            admins=sum(1 for u in users if u.rol == 'admin')
        )


@dataclass
class UserCreateData:
    """Data for creating a new user"""
    username: str
    password: str
    nombre_completo: str
    rol: str = 'usuario'


@dataclass
class UserUpdateData:
    """Data for updating a user"""
    username: str
    nombre_completo: str
    rol: str
    activo: bool
    new_password: Optional[str] = None
