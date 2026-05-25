# -*- coding: utf-8 -*-
"""
User Service - Business Logic Layer
All business operations for user management
"""

import re
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..domain.models import User, UserStats, UserCreateData, UserUpdateData
from ..data.mysql_repository import MySQLUserRepository


class UserService:
    """
    Business logic service for user management
    Coordinates between UI and data layer
    """
    
    def __init__(self, repository: MySQLUserRepository, auth_manager=None):
        """
        Initialize service with dependencies
        
        Args:
            repository: User repository instance
            auth_manager: AuthManager instance for create/update operations
        """
        self.repository = repository
        self.auth_manager = auth_manager
    
    # ==================== READ OPERATIONS ====================
    
    def get_all_users(self) -> List[User]:
        """
        Get all users
        
        Returns:
            List of User objects
        """
        return self.repository.get_all_users()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        return self.repository.get_user_by_id(user_id)
    
    def get_statistics(self, users: Optional[List[User]] = None) -> UserStats:
        """
        Get user statistics
        
        Args:
            users: Optional list of users (fetches if not provided)
            
        Returns:
            UserStats object
        """
        if users is None:
            users = self.get_all_users()
        return UserStats.from_users(users)
    
    def filter_users(
        self,
        users: List[User],
        search_text: str = "",
        role_filter: str = "",
        status_filter: str = ""
    ) -> List[User]:
        """
        Filter users by search text, role, and status
        
        Args:
            users: List of users to filter
            search_text: Text to search in username and name
            role_filter: Role to filter by
            status_filter: Status to filter by
            
        Returns:
            Filtered list of users
        """
        filtered = []
        search_lower = search_text.lower().strip()
        
        for user in users:
            # Search filter
            if search_lower:
                if (search_lower not in user.username.lower() and 
                    search_lower not in user.nombre_completo.lower()):
                    continue
            
            # Role filter
            if role_filter and role_filter.lower() not in ("todos", "todos los roles", ""):
                if user.rol.lower() != role_filter.lower():
                    continue
            
            # Status filter
            if status_filter and status_filter.lower() not in ("todos", "todos los estados", ""):
                status_lower = status_filter.lower()
                if status_lower == "activo" and not user.is_active:
                    continue
                elif status_lower == "inactivo" and (user.is_active or user.is_blocked):
                    continue
                elif status_lower == "bloqueado" and not user.is_blocked:
                    continue
            
            filtered.append(user)
        
        return filtered
    
    # ==================== WRITE OPERATIONS ====================
    
    def create_user(self, data: UserCreateData) -> Dict[str, Any]:
        """
        Create a new user
        
        Args:
            data: UserCreateData object
            
        Returns:
            Dict with 'success' and 'message' keys
        """
        # Validate input
        validation = self._validate_user_input(
            username=data.username,
            fullname=data.nombre_completo,
            password=data.password,
            is_new=True
        )
        
        if not validation['valid']:
            return {'success': False, 'message': validation['message']}
        
        # Check username availability
        if self.repository.username_exists(data.username):
            return {'success': False, 'message': 'El nombre de usuario ya existe.'}
        
        # Create via auth_manager
        if self.auth_manager:
            result = self.auth_manager.create_user(
                data.username,
                data.password,
                data.nombre_completo,
                data.rol
            )
            return result
        
        return {'success': False, 'message': 'AuthManager no configurado'}
    
    def update_user(self, data: UserUpdateData) -> Dict[str, Any]:
        """
        Update an existing user
        
        Args:
            data: UserUpdateData object
            
        Returns:
            Dict with 'success' and 'message' keys
        """
        # Validate input
        validation = self._validate_user_input(
            username=data.username,
            fullname=data.nombre_completo,
            password=data.new_password,
            is_new=False,
            change_password=data.new_password is not None
        )
        
        if not validation['valid']:
            return {'success': False, 'message': validation['message']}
        
        # Update via auth_manager
        if self.auth_manager:
            result = self.auth_manager.update_user(
                data.username,
                data.nombre_completo,
                data.rol,
                data.activo,
                data.new_password
            )
            return result
        
        return {'success': False, 'message': 'AuthManager no configurado'}
    
    def delete_user(self, user_id: int, current_username: str) -> Dict[str, Any]:
        """
        Delete a user
        
        Args:
            user_id: User ID to delete
            current_username: Username of current logged user (to prevent self-deletion)
            
        Returns:
            Dict with 'success' and 'message' keys
        """
        # Get user to delete
        user = self.repository.get_user_by_id(user_id)
        
        if not user:
            return {'success': False, 'message': 'Usuario no encontrado.'}
        
        # Prevent self-deletion
        if user.username == current_username:
            return {'success': False, 'message': 'No puede eliminar su propia cuenta.'}
        
        try:
            self.repository.delete_user(user_id)
            return {'success': True, 'message': f"Usuario '{user.username}' eliminado exitosamente."}
        except Exception as e:
            return {'success': False, 'message': f'Error al eliminar: {str(e)}'}
    
    def unblock_user(self, user_id: int) -> Dict[str, Any]:
        """
        Unblock a user
        
        Args:
            user_id: User ID to unblock
            
        Returns:
            Dict with 'success' and 'message' keys
        """
        try:
            self.repository.unblock_user(user_id)
            return {'success': True, 'message': 'Usuario desbloqueado correctamente.'}
        except Exception as e:
            return {'success': False, 'message': f'Error al desbloquear: {str(e)}'}
    
    # ==================== AVATAR OPERATIONS ====================
    
    def get_avatar_data(self, username: str) -> Dict[str, Any]:
        """
        Get user avatar data
        
        Args:
            username: Username
            
        Returns:
            Dict with 'color' and 'imagen' keys
        """
        return self.repository.get_avatar_data(username)
    
    def update_avatar_color(self, username: str, color: str) -> Dict[str, Any]:
        """
        Update avatar color
        
        Args:
            username: Username
            color: Hex color string
            
        Returns:
            Dict with 'success' and 'message' keys
        """
        try:
            self.repository.update_avatar_color(username, color)
            return {'success': True, 'message': 'Color actualizado correctamente.'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def update_avatar_image(self, username: str, image_data: bytes) -> Dict[str, Any]:
        """
        Update avatar image
        
        Args:
            username: Username
            image_data: Image binary data
            
        Returns:
            Dict with 'success' and 'message' keys
        """
        try:
            self.repository.update_avatar_image(username, image_data)
            return {'success': True, 'message': 'Imagen actualizada correctamente.'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def remove_avatar_image(self, username: str) -> Dict[str, Any]:
        """
        Remove avatar image
        
        Args:
            username: Username
            
        Returns:
            Dict with 'success' and 'message' keys
        """
        try:
            self.repository.remove_avatar_image(username)
            return {'success': True, 'message': 'Imagen eliminada correctamente.'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    # ==================== VALIDATION ====================
    
    def _validate_user_input(
        self,
        username: str,
        fullname: str,
        password: Optional[str] = None,
        is_new: bool = True,
        change_password: bool = False
    ) -> Dict[str, Any]:
        """
        Validate user input data
        
        Args:
            username: Username to validate
            fullname: Full name to validate
            password: Password to validate (if applicable)
            is_new: True if creating new user
            change_password: True if changing password on existing user
            
        Returns:
            Dict with 'valid' (bool) and 'message' (str) keys
        """
        # Username validation
        if not username or not username.strip():
            return {'valid': False, 'message': 'El nombre de usuario es requerido.'}
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return {
                'valid': False, 
                'message': 'El nombre de usuario solo puede contener letras, números y guiones bajos.'
            }
        
        if len(username) < 3:
            return {
                'valid': False, 
                'message': 'El nombre de usuario debe tener al menos 3 caracteres.'
            }
        
        # Full name validation
        if not fullname or not fullname.strip():
            return {'valid': False, 'message': 'El nombre completo es requerido.'}
        
        # Password validation (only if needed)
        need_password = is_new or change_password
        
        if need_password:
            if not password:
                return {'valid': False, 'message': 'La contraseña es requerida.'}
            
            if len(password) < 8:
                return {
                    'valid': False, 
                    'message': 'La contraseña debe tener al menos 8 caracteres.'
                }
        
        return {'valid': True, 'message': ''}
