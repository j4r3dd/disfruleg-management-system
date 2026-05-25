# -*- coding: utf-8 -*-
"""
Order Controller
Handles order management operations (new, save, load)
"""

from typing import Optional

from src.modules.receipts.mvc.controllers.base_controller import BaseController
from src.modules.receipts.mvc.controllers.client_selection_controller import ClientSelectionController
from src.modules.receipts.mvc.models.receipt_model import ReciboModel
from src.modules.receipts.mvc.views.receipt_view import ReciboView
from src.modules.receipts.models.cart_model import CartModel
from src.modules.receipts.components.ventana_ordenes import VentanaOrdenes
from src.modules.receipts.exceptions import (
    ClientNotSelectedError,
    EmptyCartError,
    OrderCreationError,
    OrderUpdateError,
    OrderNotFoundError,
    OrderLoadError,
)


class OrderController(BaseController):
    """
    Controller for order management

    Responsibilities:
    - Create new orders
    - Save orders
    - Load existing orders
    - Manage folio state
    - Handle order list window
    """

    def __init__(
        self,
        view: ReciboView,
        model: ReciboModel,
        cart_model: CartModel,
        client_controller: ClientSelectionController,
        username: str,
        on_pdf_generate_callback=None
    ):
        super().__init__(view, model, cart_model)
        self.client_controller = client_controller
        self.username = username
        self.on_pdf_generate_callback = on_pdf_generate_callback

        # State
        self.folio_orden_actual: Optional[int] = None

    # ==================== EVENT HANDLERS ====================

    def on_nueva_orden(self):
        """
        Handle 'Nueva Orden' button click

        Workflow:
        1. Confirm with user if cart has items
        2. Clear cart
        3. Reset state
        """
        try:
            self.log_info("Iniciando nueva orden")

            # Confirm if cart has items
            if not self.cart_model.is_empty():
                confirmar = self.confirm(
                    "Nueva Orden",
                    "¿Desea iniciar una nueva orden?\n\nSe perderán los datos no guardados del carrito actual."
                )

                if not confirmar:
                    return

            # Clear cart
            self.cart_model.clear()

            # Refresh UI
            if hasattr(self.view, 'cart_ui'):
                self.view.cart_ui.refresh()

            # Reset state
            self.folio_orden_actual = None
            self.view.actualizar_folio(None)
            self.client_controller.set_previous_client_id(None)

            self.log_success("Nueva orden iniciada")
            self.show_success("Nueva Orden", "Se ha iniciado una nueva orden.")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("crear nueva orden", e)

    def on_guardar_orden(self):
        """
        Handle 'Guardar Orden' button click

        Workflow:
        1. Validate client and cart
        2. Save to Model
        3. Update UI
        """
        try:
            self.log_info("Guardando orden")

            # Validate client
            if not self.client_controller.validate_client_selected():
                return

            # Validate cart has items
            if self.cart_model.is_empty():
                self.show_warning(
                    "Carrito Vacío",
                    "Por favor agregue productos antes de guardar."
                )
                return

            # Get client data
            cliente = self.client_controller.get_selected_client()
            if not cliente:
                self.show_error("Error", "No se pudo obtener datos del cliente")
                return

            id_cliente = cliente.get('id_cliente')

            # Get total from cart
            total = self.cart_model.get_total()

            # Prepare cart data for saving
            carrito_data = self.cart_model.to_dict()

            # Save to model
            result = self.model.guardar_orden(
                id_cliente=id_cliente,
                carrito_data=carrito_data,
                total=total,
                usuario=self.username,
                folio_existente=self.folio_orden_actual
            )

            # Handle result (tuple or single value for backward compatibility)
            if isinstance(result, tuple):
                folio, warnings = result
            else:
                folio = result
                warnings = []

            if not folio:
                self.show_error("Error", "No se pudo guardar la orden")
                return

            # Update state
            self.folio_orden_actual = folio
            self.view.actualizar_folio(folio)

            self.log_success(f"Orden guardada: Folio {folio}")

            message = f"Orden guardada exitosamente.\n\nFolio: {folio}"
            
            # Append warnings if any
            if warnings:
                message += "\n\n⚠️ ADVERTENCIA: PRECIOS NO ACTUALIZADOS\n"
                message += "Los siguientes productos no tienen precio en el nuevo grupo y mantuvieron su precio anterior:\n"
                for w in warnings:
                    message += f"- {w}\n"
                message += "\nPuede editarlos manualmente si es necesario."
                
                # Show as warning if there are price issues
                self.show_warning("Orden Guardada con Advertencias", message)
            else:
                self.show_success("Orden Guardada", message)

            # Close the window after saving - DISABLED per user request
            # self.view.root.destroy()

        except ClientNotSelectedError as e:
            # Client validation failed
            self.show_warning("Cliente Requerido", str(e))
            # Optionally highlight client field
            if hasattr(self.view, 'combo_clientes'):
                self.view.combo_clientes.focus_set()

        except EmptyCartError as e:
            # Cart is empty
            self.show_warning("Carrito Vacío", str(e))

        except OrderCreationError as e:
            # Order creation failed
            folio = e.details.get('folio', 'N/A')
            reason = e.details.get('reason', '')
            self.show_error(
                "Error al Crear Orden",
                f"No se pudo crear la orden {folio}\n\n{reason}"
            )
            self.log_error(f"Order creation failed: {e}")

        except OrderUpdateError as e:
            # Order update failed
            folio = e.details.get('folio', 'N/A')
            reason = e.details.get('reason', '')
            self.show_error(
                "Error al Actualizar Orden",
                f"No se pudo actualizar la orden {folio}\n\n{reason}"
            )
            self.log_error(f"Order update failed: {e}")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("guardar orden", e)

    def on_ver_ordenes(self):
        """
        Handle 'Ver Órdenes' button click

        Opens VentanaOrdenes to view/manage saved orders
        """
        try:
            self.log_info("Abriendo lista de órdenes")

            # Prepare user data
            user_data = {
                'username': self.username,
                'rol': 'admin'  # TODO: Get actual role from session/auth
            }

            # Open VentanaOrdenes with callbacks
            VentanaOrdenes(
                parent=self.view.root,
                user_data=user_data,
                on_nueva_orden=self.on_nueva_orden,
                on_editar_orden=self.cargar_orden_existente
            )

            self.log_success("Ventana de órdenes abierta")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("abrir ventana de órdenes", e)

    # ==================== ORDER OPERATIONS ====================

    def cargar_orden_existente(self, folio: int):
        """
        Load existing order

        Args:
            folio: Folio number to load
        """
        try:
            self.log_info(f"Cargando orden existente: Folio {folio}")

            # Load order from model
            orden = self.model.cargar_orden(folio)

            if not orden:
                self.show_error(
                    "Error",
                    f"No se pudo cargar la orden con folio {folio}"
                )
                return

            # Restore client selection
            cliente_id = orden.get('id_cliente')
            if cliente_id:
                # Load client by ID
                cliente = self.model.obtener_cliente_por_id(cliente_id)
                if cliente:
                    # Set client in model
                    self.model.cliente_data = cliente
                    # Get client name to update UI
                    nombre_cliente = cliente.get('nombre_completo', cliente.get('nombre_cliente', ''))
                    # Update client selection in controller state
                    self.client_controller.cliente_seleccionado = nombre_cliente
                    # Set previous client ID to avoid triggering recalculation on load
                    self.client_controller.set_previous_client_id(cliente_id)

                    # Restore group selection if available
                    id_grupo = cliente.get('id_grupo')
                    if id_grupo:
                        # Find group key by id
                        for clave_grupo, id_g in self.model.grupos_data.items():
                            if id_g == id_grupo:
                                self.client_controller.grupo_seleccionado = clave_grupo

                                # Update UI: set group in combobox
                                self.view.set_grupo_seleccionado(clave_grupo)

                                # Load clients for this group
                                clientes = self.model.cargar_clientes_por_grupo(clave_grupo)
                                nombres_clientes = [
                                    c.get('nombre_completo', c.get('nombre_cliente', ''))
                                    for c in clientes
                                ]
                                self.view.actualizar_clientes_combo(nombres_clientes)

                                # Update UI: set client in combobox
                                self.view.set_cliente_seleccionado(nombre_cliente)
                                break

            # Clear current cart
            self.cart_model.clear()

            # Load cart data from orden
            carrito_data = orden.get('datos_carrito', {})
            
            # DEBUG: Log what we received
            print(f"\n[DEBUG] Loading order folio {folio}:")
            print(f"  - carrito_data keys: {list(carrito_data.keys())}")
            print(f"  - Has 'items': {'items' in carrito_data}")
            print(f"  - Has 'sections': {'sections' in carrito_data}")
            print(f"  - Has 'secciones': {'secciones' in carrito_data}")
            if 'items' in carrito_data:
                print(f"  - items count: {len(carrito_data['items'])}")
            if 'sections' in carrito_data:
                print(f"  - sections count: {len(carrito_data['sections'])}")
                print(f"  - sections: {[s.get('nombre', s.get('name')) for s in carrito_data['sections']]}")
            
            # Check if it's the new format with 'items', 'sections', 'sectioning_enabled'
            if 'items' in carrito_data and 'sections' in carrito_data:
                # New format - use CartModel.from_dict() to restore everything
                self.log_info(f"Loading cart from new format (sectioning_enabled={carrito_data.get('sectioning_enabled', True)})")
                print(f"[DEBUG] Using NEW FORMAT - CartModel.from_dict()")
                
                # Create completely new CartModel from dict (this preserves all sections and items)
                restored_cart = CartModel.from_dict(carrito_data)
                
                print(f"[DEBUG] Restored cart:")
                print(f"  - items: {len(restored_cart.items)}")
                print(f"  - sections: {len(restored_cart.sections)}")
                print(f"  - section names: {[s.nombre for s in restored_cart.sections.values()]}")
                print(f"  - sectioning_enabled: {restored_cart.sectioning_enabled}")
                
                # Replace the entire cart model
                self.cart_model = restored_cart
                
            elif 'secciones' in carrito_data:
                # Old format - restore items manually
                self.log_info("Loading cart from legacy format")
                print(f"[DEBUG] Using LEGACY FORMAT - manual add_item()")
                for nombre_seccion, items in carrito_data['secciones'].items():
                    # Ensure section exists in cart
                    if not self.cart_model.get_section_by_name(nombre_seccion):
                        self.cart_model.add_section(nombre_seccion)
                    
                    for item_data in items:
                        self.cart_model.add_item(
                            id_producto=item_data['id_producto'],
                            nombre=item_data['nombre_producto'],
                            cantidad=item_data['cantidad'],
                            precio_unitario=item_data['precio_unitario'],
                            unidad=item_data['unidad'],
                            seccion=nombre_seccion,  # Use the section name from the dict key
                            es_especial=item_data.get('es_especial', False)
                        )

            # Update state
            self.folio_orden_actual = folio
            self.view.actualizar_folio(folio)

            # Refresh UI
            if hasattr(self.view, 'cart_ui'):
                self.view.cart_ui.refresh()

            self.log_success(f"Orden cargada: {len(self.cart_model)} items")

        except OrderNotFoundError as e:
            # Order not found in database
            folio_err = e.details.get('folio', folio)
            self.show_error(
                "Orden No Encontrada",
                f"No se encontró la orden con folio {folio_err}"
            )
            self.log_error(f"Order not found: {e}")

        except OrderLoadError as e:
            # Error loading order data
            folio_err = e.details.get('folio', folio)
            reason = e.details.get('reason', '')
            self.show_error(
                "Error al Cargar Orden",
                f"No se pudo cargar la orden {folio_err}\n\n{reason}"
            )
            self.log_error(f"Order load failed: {e}")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("cargar orden", e)

    # ==================== STATE ACCESS ====================

    def get_current_folio(self) -> Optional[int]:
        """Get current order folio"""
        return self.folio_orden_actual

    def set_current_folio(self, folio: Optional[int]):
        """Set current order folio"""
        self.folio_orden_actual = folio
        self.view.actualizar_folio(folio)