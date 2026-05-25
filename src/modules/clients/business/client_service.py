# -*- coding: utf-8 -*-
"""
Business Layer - Client Service
Contains all business logic for client management.
No direct database access - depends on repository interfaces.
"""

from typing import List, Optional
import logging
from ..domain.models import (
    Client,
    ClientSearchCriteria,
    ClientNotFoundError,
    ClientHasInvoicesError,
)
from ..data.repositories import IClientRepository, IGroupRepository

logger = logging.getLogger(__name__)


class ClientService:
    """
    Service for client business logic.
    Depends on repository interfaces (Dependency Injection).
    """

    def __init__(
        self,
        client_repo: IClientRepository,
        group_repo: IGroupRepository
    ):
        """
        Initialize service with dependencies.

        Args:
            client_repo: Client repository implementation
            group_repo: Group repository implementation
        """
        if client_repo is None:
            raise ValueError("Client repository cannot be None")
        if group_repo is None:
            raise ValueError("Group repository cannot be None")

        self.client_repo = client_repo
        self.group_repo = group_repo

    def get_client_by_id(self, client_id: int) -> Client:
        """
        Get client by ID.

        Args:
            client_id: Client ID

        Returns:
            Client entity

        Raises:
            ClientNotFoundError: If client doesn't exist
        """
        # Fail fast validation
        if client_id is None or client_id <= 0:
            raise ValueError("Client ID must be a positive integer")

        client = self.client_repo.get_by_id(client_id)
        if client is None:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")

        return client

    def get_all_clients(self) -> List[Client]:
        """
        Get all clients.

        Returns:
            List of all clients
        """
        return self.client_repo.get_all()

    def search_clients(self, criteria: ClientSearchCriteria) -> List[Client]:
        """
        Search clients with filters.

        Args:
            criteria: Search criteria

        Returns:
            List of filtered clients
        """
        if criteria is None:
            criteria = ClientSearchCriteria()

        return self.client_repo.search(criteria)

    def create_client(
        self,
        nombre_cliente: str,
        id_grupo: int,
        telefono: Optional[str] = None,
        correo: Optional[str] = None,
        rfc: Optional[str] = None,
        razon_social: Optional[str] = None,
        regimen_fiscal: Optional[str] = None,
        codigo_postal: Optional[str] = None,
        direccion_fiscal: Optional[str] = None,
        notas: Optional[str] = None
    ) -> Client:
        """
        Create a new client.

        Args:
            nombre_cliente: Client name (required)
            id_grupo: Group ID (required)
            telefono: Phone number (optional)
            correo: Email (optional)
            rfc: RFC (optional)
            razon_social: Legal name (optional)
            regimen_fiscal: Tax regime (optional)
            codigo_postal: Postal code (optional)
            direccion_fiscal: Fiscal address (optional)
            notas: Notes (optional)

        Returns:
            Created client with ID

        Raises:
            ValueError: If validation fails
        """
        # Fail fast validation
        if not nombre_cliente or not nombre_cliente.strip():
            raise ValueError("Client name cannot be empty")

        if id_grupo is None or id_grupo <= 0:
            raise ValueError("Group ID must be a positive integer")

        # Verify group exists
        group = self.group_repo.get_by_id(id_grupo)
        if group is None:
            raise ValueError(f"Group with ID {id_grupo} does not exist")

        # Create client entity (domain validation happens here)
        client = Client(
            id_cliente=None,
            nombre_cliente=nombre_cliente.strip(),
            id_grupo=id_grupo,
            telefono=telefono.strip() if telefono else None,
            correo=correo.strip() if correo else None,
            rfc=rfc.strip().upper() if rfc else None,
            razon_social=razon_social.strip() if razon_social else None,
            regimen_fiscal=regimen_fiscal.strip() if regimen_fiscal else None,
            codigo_postal=codigo_postal.strip() if codigo_postal else None,
            direccion_fiscal=direccion_fiscal.strip() if direccion_fiscal else None,
            notas=notas.strip() if notas else None,
            activo=True
        )

        # Save to repository
        new_id = self.client_repo.create(client)
        logger.info(f"Client created successfully: ID={new_id}, Name={nombre_cliente}")

        # Return the created client
        return self.get_client_by_id(new_id)

    def update_client(
        self,
        client_id: int,
        nombre_cliente: str,
        id_grupo: int,
        telefono: Optional[str] = None,
        correo: Optional[str] = None,
        rfc: Optional[str] = None,
        razon_social: Optional[str] = None,
        regimen_fiscal: Optional[str] = None,
        codigo_postal: Optional[str] = None,
        direccion_fiscal: Optional[str] = None,
        notas: Optional[str] = None
    ) -> Client:
        """
        Update existing client.

        Args:
            client_id: Client ID
            nombre_cliente: Client name
            id_grupo: Group ID
            telefono: Phone number
            correo: Email
            rfc: RFC
            razon_social: Legal name
            regimen_fiscal: Tax regime
            codigo_postal: Postal code
            direccion_fiscal: Fiscal address
            notas: Notes

        Returns:
            Updated client

        Raises:
            ClientNotFoundError: If client doesn't exist
            ValueError: If validation fails
        """
        # Fail fast validation
        if client_id is None or client_id <= 0:
            raise ValueError("Client ID must be a positive integer")

        if not nombre_cliente or not nombre_cliente.strip():
            raise ValueError("Client name cannot be empty")

        if id_grupo is None or id_grupo <= 0:
            raise ValueError("Group ID must be a positive integer")

        # Verify client exists
        existing_client = self.client_repo.get_by_id(client_id)
        if existing_client is None:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")

        # Verify group exists
        group = self.group_repo.get_by_id(id_grupo)
        if group is None:
            raise ValueError(f"Group with ID {id_grupo} does not exist")

        # Create updated client entity (domain validation happens here)
        updated_client = Client(
            id_cliente=client_id,
            nombre_cliente=nombre_cliente.strip(),
            id_grupo=id_grupo,
            telefono=telefono.strip() if telefono else None,
            correo=correo.strip() if correo else None,
            rfc=rfc.strip().upper() if rfc else None,
            razon_social=razon_social.strip() if razon_social else None,
            regimen_fiscal=regimen_fiscal.strip() if regimen_fiscal else None,
            codigo_postal=codigo_postal.strip() if codigo_postal else None,
            direccion_fiscal=direccion_fiscal.strip() if direccion_fiscal else None,
            notas=notas.strip() if notas else None,
            activo=existing_client.activo  # Preserve active status
        )

        # Save to repository
        self.client_repo.update(updated_client)
        logger.info(f"Client updated successfully: ID={client_id}, Name={nombre_cliente}")

        # Return the updated client
        return self.get_client_by_id(client_id)

    def activate_client(self, client_id: int) -> Client:
        """
        Activate a previously deactivated client.

        Args:
            client_id: Client ID

        Returns:
            Activated client

        Raises:
            ClientNotFoundError: If client doesn't exist
            ValueError: If client is already active
        """
        # Fail fast validation
        if client_id is None or client_id <= 0:
            raise ValueError("Client ID must be a positive integer")

        # Verify client exists
        client = self.client_repo.get_by_id(client_id)
        if client is None:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")

        # Check if already active
        if client.activo:
            raise ValueError(f"Client with ID {client_id} is already active")

        # Activate client
        self.client_repo.toggle_status(client_id, True)
        logger.info(f"Client activated: ID={client_id}")

        # Return the activated client
        return self.get_client_by_id(client_id)

    def toggle_client_status(self, client_id: int) -> Client:
        """
        Toggle client active/inactive status (for backwards compatibility).
        This method still exists for legacy code but deactivate_client()
        and activate_client() are preferred for clarity.

        Args:
            client_id: Client ID

        Returns:
            Updated client

        Raises:
            ClientNotFoundError: If client doesn't exist
        """
        # Fail fast validation
        if client_id is None or client_id <= 0:
            raise ValueError("Client ID must be a positive integer")

        # Verify client exists
        client = self.client_repo.get_by_id(client_id)
        if client is None:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")

        # Toggle status
        new_status = not client.activo
        self.client_repo.toggle_status(client_id, new_status)

        status_text = "activated" if new_status else "deactivated"
        logger.info(f"Client {status_text}: ID={client_id}")

        # Return the updated client
        return self.get_client_by_id(client_id)

    def deactivate_client(self, client_id: int) -> Client:
        """
        Deactivate a client (soft delete - data is preserved).
        This is the preferred method instead of permanent deletion.

        Args:
            client_id: Client ID

        Returns:
            Deactivated client

        Raises:
            ClientNotFoundError: If client doesn't exist
            ValueError: If client is already inactive
        """
        # Fail fast validation
        if client_id is None or client_id <= 0:
            raise ValueError("Client ID must be a positive integer")

        # Verify client exists
        client = self.client_repo.get_by_id(client_id)
        if client is None:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")

        # Check if already inactive
        if not client.activo:
            raise ValueError(f"Client with ID {client_id} is already inactive")

        # Deactivate client
        self.client_repo.toggle_status(client_id, False)
        logger.info(f"Client deactivated: ID={client_id}, Name={client.nombre_cliente}")

        # Return the deactivated client
        return self.get_client_by_id(client_id)

    def delete_client(self, client_id: int) -> None:
        """
        Delete client permanently (hard delete).
        WARNING: This permanently removes all client data and should only be used
        for test data or specific administrative scenarios.
        Consider using deactivate_client() instead for normal operations.

        Args:
            client_id: Client ID

        Raises:
            ClientNotFoundError: If client doesn't exist
            ClientHasInvoicesError: If client has invoices
        """
        # Fail fast validation
        if client_id is None or client_id <= 0:
            raise ValueError("Client ID must be a positive integer")

        # Verify client exists
        client = self.client_repo.get_by_id(client_id)
        if client is None:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")

        # Check for invoices
        has_invoices, count = self.client_repo.has_invoices(client_id)
        if has_invoices:
            raise ClientHasInvoicesError(
                f"Client has {count} invoices. Cannot delete client with invoices."
            )

        # Delete client
        self.client_repo.delete(client_id)
        logger.info(f"Client deleted permanently: ID={client_id}, Name={client.nombre_cliente}")

    def get_client_invoice_info(self, client_id: int) -> tuple[bool, int]:
        """
        Get client invoice information.

        Args:
            client_id: Client ID

        Returns:
            Tuple of (has_invoices, invoice_count)

        Raises:
            ClientNotFoundError: If client doesn't exist
        """
        # Fail fast validation
        if client_id is None or client_id <= 0:
            raise ValueError("Client ID must be a positive integer")

        # Verify client exists
        client = self.client_repo.get_by_id(client_id)
        if client is None:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")

        return self.client_repo.has_invoices(client_id)

    def get_statistics(self) -> dict:
        """
        Get client statistics.

        Returns:
            Dictionary with statistics:
            - total_clients: Total number of clients
            - active_clients: Number of active clients
            - inactive_clients: Number of inactive clients
        """
        all_clients = self.client_repo.get_all()

        total = len(all_clients)
        active = sum(1 for c in all_clients if c.activo)
        inactive = total - active

        return {
            'total_clients': total,
            'active_clients': active,
            'inactive_clients': inactive
        }