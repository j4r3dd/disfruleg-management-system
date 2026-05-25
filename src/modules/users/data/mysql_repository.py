# -*- coding: utf-8 -*-
"""
MySQL Repository - Data Layer
All database operations for user management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..domain.models import User


class MySQLUserRepository:
    """
    MySQL implementation for user data access
    Single point of contact with database
    """
    
    def __init__(self, connection):
        """
        Initialize repository with database connection
        
        Args:
            connection: Active database connection
        """
        self.conn = connection
    
    def get_all_users(self) -> List[User]:
        """
        Get all users from database
        
        Returns:
            List of User objects
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    id_usuario, 
                    username, 
                    nombre_completo, 
                    rol, 
                    activo,
                    ultimo_acceso, 
                    intentos_fallidos, 
                    bloqueado_hasta
                FROM usuarios_sistema
                ORDER BY nombre_completo
            """)
            
            rows = cursor.fetchall()
            
            users = []
            for row in (rows or []):
                users.append(User(
                    id_usuario=row['id_usuario'],
                    username=row['username'],
                    nombre_completo=row['nombre_completo'],
                    rol=row['rol'],
                    activo=row['activo'],
                    ultimo_acceso=row['ultimo_acceso'],
                    intentos_fallidos=row['intentos_fallidos'],
                    bloqueado_hasta=row['bloqueado_hasta']
                ))
            
            return users
            
        finally:
            cursor.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    id_usuario, 
                    username, 
                    nombre_completo, 
                    rol, 
                    activo,
                    ultimo_acceso, 
                    intentos_fallidos, 
                    bloqueado_hasta
                FROM usuarios_sistema
                WHERE id_usuario = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                return User(
                    id_usuario=row['id_usuario'],
                    username=row['username'],
                    nombre_completo=row['nombre_completo'],
                    rol=row['rol'],
                    activo=row['activo'],
                    ultimo_acceso=row['ultimo_acceso'],
                    intentos_fallidos=row['intentos_fallidos'],
                    bloqueado_hasta=row['bloqueado_hasta']
                )
            
            return None
            
        finally:
            cursor.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username to find
            
        Returns:
            User object or None
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    id_usuario, 
                    username, 
                    nombre_completo, 
                    rol, 
                    activo,
                    ultimo_acceso, 
                    intentos_fallidos, 
                    bloqueado_hasta
                FROM usuarios_sistema
                WHERE username = %s
            """, (username,))
            
            row = cursor.fetchone()
            
            if row:
                return User(
                    id_usuario=row['id_usuario'],
                    username=row['username'],
                    nombre_completo=row['nombre_completo'],
                    rol=row['rol'],
                    activo=row['activo'],
                    ultimo_acceso=row['ultimo_acceso'],
                    intentos_fallidos=row['intentos_fallidos'],
                    bloqueado_hasta=row['bloqueado_hasta']
                )
            
            return None
            
        finally:
            cursor.close()
    
    def username_exists(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if username already exists
        
        Args:
            username: Username to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if username exists
        """
        cursor = self.conn.cursor()
        
        try:
            if exclude_id:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM usuarios_sistema WHERE username = %s AND id_usuario != %s",
                    (username, exclude_id)
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM usuarios_sistema WHERE username = %s",
                    (username,)
                )
            
            result = cursor.fetchone()
            return result['count'] > 0
            
        finally:
            cursor.close()
    
    def unblock_user(self, user_id: int) -> bool:
        """
        Unblock a user and reset failed attempts
        
        Args:
            user_id: User ID to unblock
            
        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE usuarios_sistema 
                SET bloqueado_hasta = NULL, intentos_fallidos = 0
                WHERE id_usuario = %s
            """, (user_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user from database
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM usuarios_sistema WHERE id_usuario = %s",
                (user_id,)
            )
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def get_avatar_data(self, username: str) -> Dict[str, Any]:
        """
        Get user avatar data (color and image)
        
        Args:
            username: Username
            
        Returns:
            Dict with 'color' and 'imagen' keys
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                SELECT avatar_color, avatar_imagen
                FROM usuarios_sistema
                WHERE username = %s
            """, (username,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'color': row.get('avatar_color'),
                    'imagen': row.get('avatar_imagen')
                }
            
            return {'color': None, 'imagen': None}
            
        finally:
            cursor.close()
    
    def update_avatar_color(self, username: str, color: str) -> bool:
        """
        Update user avatar color
        
        Args:
            username: Username
            color: Hex color string
            
        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE usuarios_sistema 
                SET avatar_color = %s
                WHERE username = %s
            """, (color, username))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def update_avatar_image(self, username: str, image_data: bytes) -> bool:
        """
        Update user avatar image
        
        Args:
            username: Username
            image_data: Image binary data
            
        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE usuarios_sistema 
                SET avatar_imagen = %s
                WHERE username = %s
            """, (image_data, username))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def remove_avatar_image(self, username: str) -> bool:
        """
        Remove user avatar image
        
        Args:
            username: Username
            
        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE usuarios_sistema 
                SET avatar_imagen = NULL
                WHERE username = %s
            """, (username,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
