# -*- coding: utf-8 -*-
"""
Business Layer - Group Service
Contains all business logic for group management.
"""

from typing import List, Optional
import logging
from ..domain.models import Group, GroupNotFoundError, GroupInUseError
from ..data.repositories import IGroupRepository, IClientTypeRepository

logger = logging.getLogger(__name__)


class GroupService:
    """Service for group business logic"""

    def __init__(
        self,
        group_repo: IGroupRepository,
        client_type_repo: IClientTypeRepository
    ):
        """Initialize service with dependencies"""
        if group_repo is None:
            raise ValueError("Group repository cannot be None")
        if client_type_repo is None:
            raise ValueError("Client type repository cannot be None")

        self.group_repo = group_repo
        self.client_type_repo = client_type_repo

    def get_group_by_id(self, group_id: int) -> Group:
        """Get group by ID"""
        # Fail fast validation
        if group_id is None or group_id <= 0:
            raise ValueError("Group ID must be a positive integer")

        group = self.group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFoundError(f"Group with ID {group_id} not found")

        return group

    def get_all_groups(self) -> List[Group]:
        """Get all groups"""
        return self.group_repo.get_all()

    def create_group(
        self,
        clave_grupo: str,
        id_tipo_cliente: int,
        descripcion: Optional[str] = None
    ) -> Group:
        """
        Create a new group.

        Args:
            clave_grupo: Group key (required)
            id_tipo_cliente: Client type ID (required)
            descripcion: Description (optional)

        Returns:
            Created group with ID

        Raises:
            ValueError: If validation fails
        """
        # Fail fast validation
        if not clave_grupo or not clave_grupo.strip():
            raise ValueError("Group key cannot be empty")

        if id_tipo_cliente is None or id_tipo_cliente <= 0:
            raise ValueError("Client type ID must be a positive integer")

        # Verify client type exists
        client_type = self.client_type_repo.get_by_id(id_tipo_cliente)
        if client_type is None:
            raise ValueError(f"Client type with ID {id_tipo_cliente} does not exist")

        # Create group entity (domain validation happens here)
        group = Group(
            id_grupo=None,
            clave_grupo=clave_grupo.strip(),
            descripcion=descripcion.strip() if descripcion else None,
            id_tipo_cliente=id_tipo_cliente
        )

        # Save to repository
        new_id = self.group_repo.create(group)
        logger.info(f"Group created successfully: ID={new_id}, Key={clave_grupo}")

        # Return the created group
        return self.get_group_by_id(new_id)

    def update_group(
        self,
        group_id: int,
        clave_grupo: str,
        id_tipo_cliente: int,
        descripcion: Optional[str] = None
    ) -> Group:
        """
        Update existing group.

        Args:
            group_id: Group ID
            clave_grupo: Group key
            id_tipo_cliente: Client type ID
            descripcion: Description

        Returns:
            Updated group

        Raises:
            GroupNotFoundError: If group doesn't exist
            ValueError: If validation fails
        """
        # Fail fast validation
        if group_id is None or group_id <= 0:
            raise ValueError("Group ID must be a positive integer")

        if not clave_grupo or not clave_grupo.strip():
            raise ValueError("Group key cannot be empty")

        if id_tipo_cliente is None or id_tipo_cliente <= 0:
            raise ValueError("Client type ID must be a positive integer")

        # Verify group exists
        existing_group = self.group_repo.get_by_id(group_id)
        if existing_group is None:
            raise GroupNotFoundError(f"Group with ID {group_id} not found")

        # Verify client type exists
        client_type = self.client_type_repo.get_by_id(id_tipo_cliente)
        if client_type is None:
            raise ValueError(f"Client type with ID {id_tipo_cliente} does not exist")

        # Create updated group entity
        updated_group = Group(
            id_grupo=group_id,
            clave_grupo=clave_grupo.strip(),
            descripcion=descripcion.strip() if descripcion else None,
            id_tipo_cliente=id_tipo_cliente
        )

        # Save to repository
        self.group_repo.update(updated_group)
        logger.info(f"Group updated successfully: ID={group_id}, Key={clave_grupo}")

        # Return the updated group
        return self.get_group_by_id(group_id)

    def delete_group(self, group_id: int) -> None:
        """
        Delete group permanently.

        Args:
            group_id: Group ID

        Raises:
            GroupNotFoundError: If group doesn't exist
            GroupInUseError: If group is being used by clients
        """
        # Fail fast validation
        if group_id is None or group_id <= 0:
            raise ValueError("Group ID must be a positive integer")

        # Verify group exists
        group = self.group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFoundError(f"Group with ID {group_id} not found")

        # Check if group is in use
        in_use, count = self.group_repo.is_in_use(group_id)
        if in_use:
            raise GroupInUseError(
                f"Group is being used by {count} clients. "
                f"Reassign or delete these clients first."
            )

        # Delete group
        self.group_repo.delete(group_id)
        logger.info(f"Group deleted: ID={group_id}, Key={group.clave_grupo}")

    def get_group_usage_info(self, group_id: int) -> tuple[bool, int]:
        """
        Get group usage information.

        Args:
            group_id: Group ID

        Returns:
            Tuple of (is_in_use, client_count)

        Raises:
            GroupNotFoundError: If group doesn't exist
        """
        # Fail fast validation
        if group_id is None or group_id <= 0:
            raise ValueError("Group ID must be a positive integer")

        # Verify group exists
        group = self.group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFoundError(f"Group with ID {group_id} not found")

        return self.group_repo.is_in_use(group_id)
