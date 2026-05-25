# -*- coding: utf-8 -*-
"""
Business Layer - Client Type Service
Contains all business logic for client type management.
"""

from typing import List
from decimal import Decimal
import logging
from ..domain.models import ClientType, ClientTypeNotFoundError, ClientTypeInUseError
from ..data.repositories import IClientTypeRepository

logger = logging.getLogger(__name__)


class ClientTypeService:
    """Service for client type business logic"""

    def __init__(self, client_type_repo: IClientTypeRepository):
        """Initialize service with dependencies"""
        if client_type_repo is None:
            raise ValueError("Client type repository cannot be None")

        self.client_type_repo = client_type_repo

    def get_client_type_by_id(self, type_id: int) -> ClientType:
        """Get client type by ID"""
        # Fail fast validation
        if type_id is None or type_id <= 0:
            raise ValueError("Client type ID must be a positive integer")

        client_type = self.client_type_repo.get_by_id(type_id)
        if client_type is None:
            raise ClientTypeNotFoundError(f"Client type with ID {type_id} not found")

        return client_type

    def get_all_client_types(self) -> List[ClientType]:
        """Get all client types"""
        return self.client_type_repo.get_all()

    def create_client_type(
        self,
        nombre_tipo: str,
        descuento: Decimal
    ) -> ClientType:
        """
        Create a new client type.

        Args:
            nombre_tipo: Type name (required)
            descuento: Discount percentage (required, 0-100)

        Returns:
            Created client type with ID

        Raises:
            ValueError: If validation fails
        """
        # Fail fast validation
        if not nombre_tipo or not nombre_tipo.strip():
            raise ValueError("Client type name cannot be empty")

        if descuento is None:
            raise ValueError("Discount cannot be None")

        try:
            descuento = Decimal(str(descuento))
        except:
            raise ValueError("Discount must be a valid number")

        if descuento < 0 or descuento > 100:
            raise ValueError("Discount must be between 0 and 100")

        # Create client type entity (domain validation happens here)
        client_type = ClientType(
            id_tipo_cliente=None,
            nombre_tipo=nombre_tipo.strip(),
            descuento=descuento
        )

        # Save to repository
        new_id = self.client_type_repo.create(client_type)
        logger.info(f"Client type created successfully: ID={new_id}, Name={nombre_tipo}")

        # Return the created client type
        return self.get_client_type_by_id(new_id)

    def update_client_type(
        self,
        type_id: int,
        nombre_tipo: str,
        descuento: Decimal
    ) -> ClientType:
        """
        Update existing client type.

        Args:
            type_id: Client type ID
            nombre_tipo: Type name
            descuento: Discount percentage

        Returns:
            Updated client type

        Raises:
            ClientTypeNotFoundError: If client type doesn't exist
            ValueError: If validation fails
        """
        # Fail fast validation
        if type_id is None or type_id <= 0:
            raise ValueError("Client type ID must be a positive integer")

        if not nombre_tipo or not nombre_tipo.strip():
            raise ValueError("Client type name cannot be empty")

        if descuento is None:
            raise ValueError("Discount cannot be None")

        try:
            descuento = Decimal(str(descuento))
        except:
            raise ValueError("Discount must be a valid number")

        if descuento < 0 or descuento > 100:
            raise ValueError("Discount must be between 0 and 100")

        # Verify client type exists
        existing_type = self.client_type_repo.get_by_id(type_id)
        if existing_type is None:
            raise ClientTypeNotFoundError(f"Client type with ID {type_id} not found")

        # Create updated client type entity
        updated_type = ClientType(
            id_tipo_cliente=type_id,
            nombre_tipo=nombre_tipo.strip(),
            descuento=descuento
        )

        # Save to repository
        self.client_type_repo.update(updated_type)
        logger.info(f"Client type updated successfully: ID={type_id}, Name={nombre_tipo}")

        # Return the updated client type
        return self.get_client_type_by_id(type_id)

    def delete_client_type(self, type_id: int) -> None:
        """
        Delete client type permanently.

        Args:
            type_id: Client type ID

        Raises:
            ClientTypeNotFoundError: If client type doesn't exist
            ClientTypeInUseError: If client type is being used by groups
        """
        # Fail fast validation
        if type_id is None or type_id <= 0:
            raise ValueError("Client type ID must be a positive integer")

        # Verify client type exists
        client_type = self.client_type_repo.get_by_id(type_id)
        if client_type is None:
            raise ClientTypeNotFoundError(f"Client type with ID {type_id} not found")

        # Check if type is in use
        in_use, count = self.client_type_repo.is_in_use(type_id)
        if in_use:
            raise ClientTypeInUseError(
                f"Client type is being used by {count} groups. "
                f"Reassign or delete these groups first."
            )

        # Delete client type
        self.client_type_repo.delete(type_id)
        logger.info(f"Client type deleted: ID={type_id}, Name={client_type.nombre_tipo}")

    def get_client_type_usage_info(self, type_id: int) -> tuple[bool, int]:
        """
        Get client type usage information.

        Args:
            type_id: Client type ID

        Returns:
            Tuple of (is_in_use, group_count)

        Raises:
            ClientTypeNotFoundError: If client type doesn't exist
        """
        # Fail fast validation
        if type_id is None or type_id <= 0:
            raise ValueError("Client type ID must be a positive integer")

        # Verify client type exists
        client_type = self.client_type_repo.get_by_id(type_id)
        if client_type is None:
            raise ClientTypeNotFoundError(f"Client type with ID {type_id} not found")

        return self.client_type_repo.is_in_use(type_id)
