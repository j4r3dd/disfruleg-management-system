# -*- coding: utf-8 -*-
"""
Clients Module - Clean Architecture Implementation

Architecture Layers:
1. Domain Layer (domain/) - Pure business entities and rules
2. Data Layer (data/) - Repository interfaces and implementations
3. Business Layer (business/) - Service classes with business logic
4. UI Layer (ui/) - Controllers and views

Dependencies flow inward: UI -> Business -> Data -> Domain
"""

from .client_manager_refactored import launch_client_manager

__all__ = ['launch_client_manager']
