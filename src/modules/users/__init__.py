# -*- coding: utf-8 -*-
"""
Users Module - User Management System
Clean Architecture Implementation

Structure:
- domain/: Business entities and models
- data/: Repository implementations  
- business/: Business logic services
- ui/: User interface components

Usage:
    from users import main
    main(user_data)
    
    # Or use launcher directly:
    from users import UserManagerLauncher
    launcher = UserManagerLauncher(user_data)
    launcher.launch()
"""

from .user_launcher import main, UserManagerLauncher
from .domain import User, UserStats, UserCreateData, UserUpdateData
from .data import MySQLUserRepository
from .business import UserService
from .ui import UserManagementApp

__all__ = [
    # Entry points
    'main',
    'UserManagerLauncher',
    
    # Domain
    'User',
    'UserStats',
    'UserCreateData', 
    'UserUpdateData',
    
    # Data
    'MySQLUserRepository',
    
    # Business
    'UserService',
    
    # UI
    'UserManagementApp'
]

__version__ = '2.0.0'
__author__ = 'Disfruleg'
