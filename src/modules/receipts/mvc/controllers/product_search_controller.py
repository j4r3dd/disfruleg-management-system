# -*- coding: utf-8 -*-
"""
Product Search Controller
Handles product search and cart addition logic
"""

from typing import Dict, Any

from src.modules.receipts.mvc.controllers.base_controller import BaseController
from src.modules.receipts.mvc.controllers.client_selection_controller import ClientSelectionController
from src.modules.receipts.mvc.models.receipt_model import ReciboModel
from src.modules.receipts.mvc.views.receipt_view import ReciboView
from src.modules.receipts.mvc.views.product_window import VentanaEdicionProducto
from src.modules.receipts.models.cart_model import CartModel
from src.modules.receipts.exceptions import (
    ClientNotSelectedError,
    InvalidQuantityError,
    InvalidPriceError,
    CartError,
)


class ProductSearchController(BaseController):
    """
    Controller for product search and addition

    Responsibilities:
    - Handle product search
    - Handle product addition to cart
    - Open product addition window
    - Validate client selection before adding
    """

    def __init__(
        self,
        view: ReciboView,
        model: ReciboModel,
        cart_model: CartModel,
        client_controller: ClientSelectionController,
        on_cart_updated_callback=None
    ):
        super().__init__(view, model, cart_model)
        self.client_controller = client_controller
        self.on_cart_updated_callback = on_cart_updated_callback

    # ==================== EVENT HANDLERS ====================

    def on_busqueda_changed(self, event):
        """
        Handle product search text change

        Workflow:
        1. Get search text from event
        2. Validate minimum requirements
        3. Search products in Model
        4. Update View with results

        Args:
            event: Tkinter event with widget
        """
        try:
            texto_busqueda = event.widget.get().strip()

            # Need group selected
            grupo_seleccionado = self.client_controller.get_selected_group()
            if not grupo_seleccionado:
                self.view.limpiar_productos()
                return

            # Need minimum 2 characters
            if len(texto_busqueda) < 2:
                self.view.limpiar_productos()
                return

            self.log_info(f"Buscando productos: '{texto_busqueda}'")

            # Search in model
            productos = self.model.buscar_productos(
                grupo_seleccionado,
                texto_busqueda
            )

            # Update view
            self.view.actualizar_productos(
                productos,
                on_producto_click=self.on_producto_click
            )

            self.log_success(f"{len(productos)} productos encontrados")

        except Exception as e:
            # Unexpected error - use global handler (non-critical, don't show to user)
            self.log_error(f"Error en búsqueda: {e}")

    def on_producto_click(self, producto: Dict[str, Any]):
        """
        Handle product card click

        Workflow:
        1. Validate client selected
        2. Open product addition window

        Args:
            producto: Product data dictionary
        """
        try:
            # Validate client selected
            if not self.client_controller.validate_client_selected():
                return

            self.log_info(f"Abriendo ventana para producto: {producto.get('nombre_producto')}")

            # Open product addition window
            self._open_product_addition_window(producto)

        except ClientNotSelectedError as e:
            # Client validation failed
            self.show_warning("Cliente Requerido", str(e))

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("hacer click en producto", e)

    # ==================== PRODUCT ADDITION ====================

    def _open_product_addition_window(self, producto: Dict[str, Any]):
        """
        Open window to add product to cart

        Opens VentanaEdicionProducto which allows user to:
        - Set quantity
        - Modify price
        - Choose section (if sectioning enabled)

        Args:
            producto: Product data dictionary
        """
        try:
            self.log_info(f"Abriendo ventana para: {producto.get('nombre_producto')}")

            # Convert Decimal to float for precio
            producto_converted = producto.copy()
            precio_raw = producto_converted.get('precio', 0)
            producto_converted['precio'] = float(precio_raw) if precio_raw is not None else 0.0

            # Create adapter for backward compatibility with VentanaEdicionProducto
            cart_adapter = self._create_cart_adapter()

            # Open product addition window
            VentanaEdicionProducto(
                parent=self.view.root,
                producto=producto_converted,
                carrito=cart_adapter,
                secciones=cart_adapter.secciones,
                callback=self._on_product_added
            )

            self.log_success("Ventana de producto abierta")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("abrir ventana de producto", e)

    def _create_cart_adapter(self):
        """
        Create adapter to make cart_model work with VentanaEdicionProducto

        Returns:
            CartAdapter instance
        """
        class CartAdapter:
            """Adapter to make cart_model work with VentanaEdicionProducto"""
            def __init__(self, cart_model, refresh_callback):
                self.cart_model = cart_model
                self.refresh_callback = refresh_callback
                self.secciones = {
                    s.section_id: s
                    for s in cart_model.sections.values()
                }
                self.sectioning_enabled = cart_model.sectioning_enabled

            def agregar_item(self, id_producto, nombre_producto, cantidad,
                           precio_unitario, unidad_producto, seccion_id=None):
                """Add item to cart (old interface)"""
                # Map section_id to section name
                seccion_nombre = None
                if seccion_id:
                    section = self.cart_model.sections.get(seccion_id)
                    if section:
                        seccion_nombre = section.nombre

                # Add to cart model
                self.cart_model.add_item(
                    id_producto=id_producto,
                    nombre=nombre_producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    unidad=unidad_producto,
                    seccion=seccion_nombre
                )

                # Trigger refresh
                if self.refresh_callback:
                    self.refresh_callback()

        return CartAdapter(self.cart_model, self._on_cart_updated)

    def _on_product_added(self):
        """Callback when product is added to cart"""
        self.log_info("Producto agregado al carrito")
        # Additional callback if provided
        if self.on_cart_updated_callback:
            self.on_cart_updated_callback()

    def _on_cart_updated(self):
        """Callback when cart is updated - refresh UI"""
        # Refresh cart UI
        if hasattr(self.view, 'cart_ui'):
            self.view.cart_ui.refresh()

        # Call external callback if provided
        if self.on_cart_updated_callback:
            self.on_cart_updated_callback()
