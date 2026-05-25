# -*- coding: utf-8 -*-
"""
Sales Controller
Handles sales transaction processing
"""

from src.modules.receipts.mvc.controllers.base_controller import BaseController
from src.modules.receipts.mvc.controllers.client_selection_controller import ClientSelectionController
from src.modules.receipts.mvc.controllers.order_controller import OrderController
from src.modules.receipts.mvc.controllers.export_controller import ExportController
from src.modules.receipts.mvc.models.receipt_model import ReciboModel
from src.modules.receipts.mvc.views.receipt_view import ReciboView
from src.modules.receipts.models.cart_model import CartModel
from src.modules.receipts.exceptions import (
    ClientNotSelectedError,
    EmptyCartError,
    SaleProcessingError,
    PDFGenerationError,
)


class SalesController(BaseController):
    """
    Controller for sales processing

    Responsibilities:
    - Process sales transactions
    - Validate sale data
    - Generate receipts after sale
    - Clear cart after successful sale
    """

    def __init__(
        self,
        view: ReciboView,
        model: ReciboModel,
        cart_model: CartModel,
        client_controller: ClientSelectionController,
        order_controller: OrderController,
        export_controller: ExportController
    ):
        super().__init__(view, model, cart_model)
        self.client_controller = client_controller
        self.order_controller = order_controller
        self.export_controller = export_controller

    # ==================== EVENT HANDLERS ====================

    def on_procesar_venta(self):
        """
        Handle 'Procesar Venta' button click

        Workflow:
        1. Validate client and cart
        2. Confirm with user
        3. Process sale in database
        4. Generate PDF
        5. Clear cart and reset state
        """
        try:
            self.log_info("Procesando venta")

            # Validate client
            if not self.client_controller.validate_client_selected():
                return

            # Validate cart has items
            if self.cart_model.is_empty():
                self.show_warning(
                    "Carrito Vacío",
                    "No hay productos para procesar."
                )
                return

            # Confirm with custom 2-step dialog
            total = self.cart_model.get_total()
            items_count = len(self.cart_model.get_items())
            cliente = self.client_controller.get_selected_client()
            client_name = cliente.get('nombre_cliente', 'Cliente')

            confirmar = self.view.confirmar_venta(
                total=total,
                items_count=items_count,
                client_name=client_name
            )

            if not confirmar:
                return

            # Process sale
            folio_numero = self._process_sale()

            if not folio_numero:
                self.show_error(
                    "Error",
                    "No se pudo procesar la venta."
                )
                return

            # Generate PDF
            pdf_path = self.export_controller.generate_pdf(folio_numero)

            # Clear cart and reset state
            self.cart_model.clear()
            if hasattr(self.view, 'cart_ui'):
                self.view.cart_ui.refresh()

            self.order_controller.set_current_folio(None)

            # Trigger order change event to refresh VentanaOrdenes
            if hasattr(self.view, 'root'):
                self.view.root.event_generate("<<OrdenCambiada>>")

            self.log_success(f"Venta procesada: Folio {folio_numero}")

            # Show success message
            self.show_success(
                "Venta Procesada",
                f"✅ Venta registrada exitosamente\n\nFOLIO: {folio_numero:06d}"
            )

        except ClientNotSelectedError as e:
            # Client validation failed
            self.show_warning("Cliente Requerido", str(e))

        except EmptyCartError as e:
            # Cart is empty
            self.show_warning("Carrito Vacío", str(e))

        except SaleProcessingError as e:
            # Sale processing failed
            folio = e.details.get('folio', 'N/A')
            reason = e.details.get('reason', '')
            self.show_error(
                "Error al Procesar Venta",
                f"No se pudo procesar la venta\n\nFolio: {folio}\n{reason}"
            )
            self.log_error(f"Sale processing failed: {e}")

        except PDFGenerationError as e:
            # PDF generation failed (but sale was processed)
            client_name = e.details.get('client_name', 'Unknown')
            self.show_warning(
                "Venta Procesada - Error en PDF",
                f"La venta se procesó exitosamente pero hubo un error al generar el PDF para {client_name}."
            )
            self.log_error(f"PDF generation failed after sale: {e}")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("procesar venta", e)

    # ==================== SALE OPERATIONS ====================

    def _process_sale(self) -> int:
        """
        Process sale transaction

        Returns:
            Folio number

        Raises:
            ClientNotSelectedError: If no client is selected
            SaleProcessingError: If sale processing fails
        """
        # Get client data
        cliente = self.client_controller.get_selected_client()
        if not cliente:
            raise ClientNotSelectedError()

        id_cliente = cliente.get('id_cliente')

        # Convert cart items to sale format
        items_orden = []
        for item in self.cart_model.get_items():
            items_orden.append({
                'id_producto': item.id_producto,
                'cantidad': item.cantidad,
                'precio_unitario': item.precio_unitario
            })

        # Process in model
        resultado = self.model.procesar_venta(
            items_bd=items_orden,
            folio_numero=self.order_controller.get_current_folio()
        )

        return resultado.get('folio_factura')
