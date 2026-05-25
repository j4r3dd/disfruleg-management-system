# -*- coding: utf-8 -*-
"""
Data Layer - Repository Interfaces (Protocols)
These define the contracts for data access without implementation details.
"""

from typing import Protocol, List, Optional
from decimal import Decimal
from ..domain.models import Client, Group, ClientType, ClientSearchCriteria


class IClientRepository(Protocol):
    """Interface for client data access"""

    def get_by_id(self, client_id: int) -> Optional[Client]:
        """Get client by ID"""
        ...

    def get_all(self) -> List[Client]:
        """Get all clients"""
        ...

    def search(self, criteria: ClientSearchCriteria) -> List[Client]:
        """Search clients with filters"""
        ...

    def create(self, client: Client) -> int:
        """Create a new client, returns the new client ID"""
        ...

    def update(self, client: Client) -> None:
        """Update existing client"""
        ...

    def delete(self, client_id: int) -> None:
        """Delete client"""
        ...

    def toggle_status(self, client_id: int, active: bool) -> None:
        """Toggle client active/inactive status"""
        ...

    def count_by_group(self, group_id: int) -> int:
        """Count clients in a group"""
        ...

    def has_invoices(self, client_id: int) -> tuple[bool, int]:
        """Check if client has invoices, returns (has_invoices, count)"""
        ...


class IGroupRepository(Protocol):
    """Interface for group data access"""

    def get_by_id(self, group_id: int) -> Optional[Group]:
        """Get group by ID"""
        ...

    def get_all(self) -> List[Group]:
        """Get all groups with type information"""
        ...

    def create(self, group: Group) -> int:
        """Create a new group, returns the new group ID"""
        ...

    def update(self, group: Group) -> None:
        """Update existing group"""
        ...

    def delete(self, group_id: int) -> None:
        """Delete group"""
        ...

    def is_in_use(self, group_id: int) -> tuple[bool, int]:
        """Check if group is used by clients, returns (in_use, count)"""
        ...


class IClientTypeRepository(Protocol):
    """Interface for client type data access"""

    def get_by_id(self, type_id: int) -> Optional[ClientType]:
        """Get client type by ID"""
        ...

    def get_all(self) -> List[ClientType]:
        """Get all client types"""
        ...

    def create(self, client_type: ClientType) -> int:
        """Create a new client type, returns the new type ID"""
        ...

    def update(self, client_type: ClientType) -> None:
        """Update existing client type"""
        ...

    def delete(self, type_id: int) -> None:
        """Delete client type"""
        ...

    def is_in_use(self, type_id: int) -> tuple[bool, int]:
        """Check if type is used by groups, returns (in_use, count)"""
        ...
