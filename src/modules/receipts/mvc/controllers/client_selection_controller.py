# -*- coding: utf-8 -*-
"""
Client Selection Controller
Handles group and client selection logic
"""

from typing import Optional, Dict, Any

from src.modules.receipts.mvc.controllers.base_controller import BaseController
from src.modules.receipts.mvc.models.receipt_model import ReciboModel
from src.modules.receipts.mvc.views.receipt_view import ReciboView
from src.modules.receipts.models.cart_model import CartModel
from src.modules.receipts.exceptions import (
    ClientNotFoundError,
    DatabaseError,
)


class ClientSelectionController(BaseController):
    """
    Controller for client and group selection

    Responsibilities:
    - Handle group selection
    - Handle client selection
    - Maintain current selection state
    - Provide access to current client/group
    """

    def __init__(self, view: ReciboView, model: ReciboModel, cart_model: CartModel):
        super().__init__(view, model, cart_model)

        # State
        self.grupo_seleccionado: Optional[str] = None
        self.cliente_seleccionado: Optional[str] = None
        self.previous_client_id: Optional[int] = None  # Track previous client for change detection

    def set_previous_client_id(self, client_id: Optional[int]):
        """Set the previous client ID (used when loading an order)"""
        self.previous_client_id = client_id

    # ==================== EVENT HANDLERS ====================

    def on_grupo_seleccionado(self, grupo_clave: str):
        """
        Handle group selection event

        Workflow:
        1. Load clients from Model
        2. Update View with client list
        3. Update state

        Args:
            grupo_clave: Group key/code
        """
        try:
            self.log_info(f"Grupo seleccionado: {grupo_clave}")

            # Load clients from model
            clientes = self.model.cargar_clientes_por_grupo(grupo_clave)

            # Extract names for combobox
            nombres_clientes = [
                c.get('nombre_completo', c.get('nombre_cliente', ''))
                for c in clientes
            ]

            # Update view
            self.view.actualizar_clientes_combo(nombres_clientes)

            # Update state
            self.grupo_seleccionado = grupo_clave
            self.cliente_seleccionado = None  # Reset client selection

            self.log_success(f"{len(nombres_clientes)} clientes cargados para {grupo_clave}")

        except DatabaseError as e:
            # Database error loading clients
            self.show_error(
                "Error de Base de Datos",
                f"No se pudieron cargar los clientes del grupo {grupo_clave}"
            )
            self.log_error(f"Database error loading clients: {e}")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("cargar clientes", e)

    def on_cliente_seleccionado(self, nombre_cliente: str):
        """
        Handle client selection event

        Workflow:
        1. Get client data from Model
        2. Update state
        3. Check for change and recalculate prices if needed

        Args:
            nombre_cliente: Client name
        """
        try:
            self.log_info(f"Cliente seleccionado: {nombre_cliente}")

            # Get client data from model
            cliente = self.model.obtener_cliente_por_nombre(nombre_cliente)

            if not cliente:
                raise ClientNotFoundError(client_name=nombre_cliente)

            # Update state
            self.cliente_seleccionado = nombre_cliente
            new_client_id = cliente.get('id_cliente')

            self.log_success(f"Cliente cargado: {new_client_id}")

            # Check if client changed and we have items in cart
            print(f"[DEBUG] Check change: Prev={self.previous_client_id}, New={new_client_id}, CartEmpty={self.cart_model.is_empty()}")
            if (self.previous_client_id is not None and
                new_client_id != self.previous_client_id and
                not self.cart_model.is_empty()):

                self.log_info(f"Cambio de cliente detectado: {self.previous_client_id} -> {new_client_id}")

                # Recalculate prices
                carrito_data = self.cart_model.to_dict()
                carrito_actualizado, warnings = self.model.recalcular_precios_carrito(carrito_data, new_client_id)

                # Update cart model with new prices
                # We need to rebuild the cart model from the updated data
                # Since CartModel.from_dict creates a new instance, we might need to update the current instance
                # or replace it. For now, let's try to update items in place or clear and re-add.
                # Actually, CartModel doesn't have a bulk update.
                # Let's use the controller's cart_model reference.

                # Option 1: Clear and re-add (safest for consistency)
                self.cart_model.clear()

                # Restore from updated data
                if 'items' in carrito_actualizado and 'sections' in carrito_actualizado:
                     # New format
                     temp_cart = CartModel.from_dict(carrito_actualizado)
                     # Copy data to current cart_model instance to preserve references
                     self.cart_model.items = temp_cart.items
                     self.cart_model.sections = temp_cart.sections
                     self.cart_model.sectioning_enabled = temp_cart.sectioning_enabled
                else:
                    # Legacy format fallback (shouldn't happen with new model but safe to handle)
                    pass

                # Refresh UI
                if hasattr(self.view, 'cart_ui'):
                    self.view.cart_ui.refresh()

                # Show warnings if any
                if warnings:
                    message = "Los siguientes productos no tienen precio en el nuevo grupo y mantuvieron su precio anterior:\n"
                    for w in warnings:
                        message += f"- {w}\n"
                    message += "\nPuede editarlos manualmente si es necesario."
                    self.show_warning("Precios No Actualizados", message)
                else:
                    # Optional: Show success toast/message? Maybe too intrusive.
                    pass

            # Update previous client ID to current
            self.previous_client_id = new_client_id

        except ClientNotFoundError as e:
            # Client not found in database
            self.show_error(
                "Cliente No Encontrado",
                f"No se encontró el cliente: {nombre_cliente}"
            )
            self.log_error(f"Client not found: {e}")

        except DatabaseError as e:
            # Database error loading client
            self.show_error(
                "Error de Base de Datos",
                f"No se pudo cargar el cliente: {nombre_cliente}"
            )
            self.log_error(f"Database error loading client: {e}")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("seleccionar cliente", e)

    # ==================== STATE ACCESS ====================

    def get_selected_group(self) -> Optional[str]:
        """Get currently selected group"""
        return self.grupo_seleccionado

    def get_selected_client_name(self) -> Optional[str]:
        """Get currently selected client name"""
        return self.cliente_seleccionado

    def get_selected_client(self) -> Optional[Dict[str, Any]]:
        """
        Get currently selected client data

        Returns:
            Client dictionary or None
        """
        try:
            if not self.cliente_seleccionado:
                return None
            return self.model.get_cliente_actual()
        except Exception as e:
            self.log_error(f"Error al obtener cliente actual: {e}")
            return None

    def is_client_selected(self) -> bool:
        """Check if a client is currently selected"""
        return self.model.validar_cliente_seleccionado()

    def get_client_id(self) -> Optional[int]:
        """Get ID of currently selected client"""
        cliente = self.get_selected_client()
        return cliente.get('id_cliente') if cliente else None

    # ==================== VALIDATION ====================

    def validate_client_selected(self) -> bool:
        """
        Validate that a client is selected

        Returns:
            True if client is selected, False otherwise (shows warning)
        """
        if not self.is_client_selected():
            self.show_warning(
                "Cliente Requerido",
                "Por favor seleccione un cliente antes de continuar."
            )
            return False
        return True
