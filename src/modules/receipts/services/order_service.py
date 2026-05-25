# -*- coding: utf-8 -*-
"""
Order Service
Handles all order-related business logic
"""

from typing import Optional, Dict, Any, List
import json
from datetime import datetime

from src.modules.receipts.services.base_service import BaseService
from src.modules.receipts.database.repositories.orden_repository import OrdenRepository
from src.modules.receipts.database.repositories.client_repository import ClientRepository
from src.modules.receipts.constants import OrderState
from src.modules.receipts.logging_config import get_logger, PerformanceLogger, LogContext
from src.modules.receipts.exceptions import (
    ClientNotSelectedError,
    EmptyCartError,
    ClientNotFoundError,
    OrderNotFoundError,
    OrderCreationError,
    OrderUpdateError,
    OrderLoadError,
)
import logging


logger = get_logger(__name__)


class OrderService(BaseService):
    """Service for order management business logic"""

    def __init__(self):
        super().__init__()
        self.orden_repo = OrdenRepository()
        self.client_repo = ClientRepository()
        self.logger = logger
        self.perf = PerformanceLogger(logger)

    # ==================== VALIDATION ====================

    def validate_order_data(
        self,
        cliente_id: Optional[int],
        carrito_items: Optional[List[Any]],
        raise_exception: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Validate order data before saving

        Args:
            cliente_id: Client ID
            carrito_items: Cart items list
            raise_exception: If True, raise custom exceptions on validation failure

        Returns:
            Tuple of (is_valid, error_message)

        Raises:
            ClientNotSelectedError: If client is not selected
            EmptyCartError: If cart is empty
            ClientNotFoundError: If client doesn't exist in database
        """
        if not cliente_id:
            self.logger.warning("Validation failed: No client selected")
            if raise_exception:
                raise ClientNotSelectedError()
            return False, "Cliente no seleccionado"

        if not carrito_items or len(carrito_items) == 0:
            self.logger.warning("Validation failed: Cart is empty")
            if raise_exception:
                raise EmptyCartError()
            return False, "Carrito vacío"

        # Verify client exists
        cliente = self.client_repo.get_client_by_id(cliente_id)
        if not cliente:
            self.logger.error(f"Validation failed: Client not found | ID: {cliente_id}")
            if raise_exception:
                raise ClientNotFoundError(client_id=cliente_id)
            return False, f"Cliente con ID {cliente_id} no existe"

        return True, None

    # ==================== ORDER OPERATIONS ====================

    def create_or_update_order(
        self,
        folio: int,
        cliente_id: int,
        usuario: str,
        carrito_data: Dict[str, Any],
        total: float,
        folio_existente: Optional[int] = None
    ) -> Optional[int]:
        """
        Create new order or update existing one

        Args:
            folio: Folio number for new order
            cliente_id: Client ID
            usuario: Username who created the order
            carrito_data: Cart data dictionary
            total: Total amount
            folio_existente: Existing folio number (if updating)

        Returns:
            Folio number if successful, None otherwise
        """
        operation = "Update order" if folio_existente else "Create order"
        target_folio = folio_existente or folio
        operation_name = f"{operation} | Folio: {target_folio}"

        with LogContext(self.logger, operation_name, logging.INFO):
            try:
                num_items = len(carrito_data.get('items', []))
                self.logger.info(
                    f"Order request | Folio: {target_folio} | "
                    f"Client ID: {cliente_id} | Items: {num_items} | "
                    f"Total: ${total:.2f} | User: {usuario}"
                )

                # Validate order data
                self.perf.start_timer("validation")
                is_valid, error_msg = self.validate_order_data(
                    cliente_id,
                    carrito_data.get('items', []),
                    raise_exception=True
                )
                self.perf.end_timer("validation", logging.DEBUG)
                self.logger.debug("Order data validated successfully")

                if folio_existente:
                    # Update existing order
                    self.perf.start_timer("database_update")
                    success = self.orden_repo.update_order(
                        folio=folio_existente,
                        datos_carrito=carrito_data,
                        total=total
                    )
                    db_time = self.perf.end_timer("database_update", logging.DEBUG)

                    if success:
                        self.logger.info(
                            f"✅ Order updated successfully | Folio: {folio_existente} | "
                            f"DB time: {db_time:.2f}s"
                        )
                        return folio_existente
                    else:
                        self.logger.error(f"Failed to update order | Folio: {folio_existente}")
                        raise OrderUpdateError(
                            folio=folio_existente,
                            reason="Database update operation failed"
                        )
                else:
                    # Create new order
                    self.perf.start_timer("database_insert")
                    success = self.orden_repo.create_order(
                        folio=folio,
                        id_cliente=cliente_id,
                        usuario=usuario,
                        datos_carrito=carrito_data,
                        total=total
                    )
                    db_time = self.perf.end_timer("database_insert", logging.DEBUG)

                    if success:
                        self.logger.info(
                            f"✅ Order created successfully | Folio: {folio:06d} | "
                            f"DB time: {db_time:.2f}s"
                        )
                        return folio
                    else:
                        self.logger.error(f"Failed to create order | Folio: {folio}")
                        raise OrderCreationError(
                            folio=folio,
                            reason="Database insert operation failed"
                        )

            except (OrderCreationError, OrderUpdateError):
                # Re-raise our custom exceptions
                raise
            except (ClientNotSelectedError, EmptyCartError, ClientNotFoundError):
                # Re-raise validation exceptions
                raise
            except Exception as e:
                self.logger.error(
                    f"Unexpected error in create_or_update_order | Folio: {target_folio}",
                    exc_info=True
                )
                # Wrap unexpected errors in appropriate custom exception
                if folio_existente:
                    raise OrderUpdateError(folio=folio_existente, reason=str(e))
                else:
                    raise OrderCreationError(folio=folio, reason=str(e))

    def load_order(self, folio: int, raise_if_not_found: bool = False) -> Optional[Dict[str, Any]]:
        """
        Load order by folio number

        Args:
            folio: Folio number
            raise_if_not_found: If True, raise OrderNotFoundError when order doesn't exist

        Returns:
            Order data dict or None if not found (when raise_if_not_found=False)

        Raises:
            OrderNotFoundError: If order doesn't exist (when raise_if_not_found=True)
            OrderLoadError: If there's an error loading the order
        """
        operation_name = f"Load order | Folio: {folio}"

        with LogContext(self.logger, operation_name, logging.INFO):
            try:
                self.logger.info(f"Loading order from database | Folio: {folio:06d}")

                self.perf.start_timer("database_query")
                orden = self.orden_repo.find_by_folio(folio)
                db_time = self.perf.end_timer("database_query", logging.DEBUG)

                if orden:
                    num_items = len(json.loads(orden.get('datos_carrito', '{}')).get('items', []))
                    self.logger.info(
                        f"✅ Order loaded successfully | Folio: {folio:06d} | "
                        f"Items: {num_items} | DB time: {db_time:.2f}s"
                    )
                    return orden
                else:
                    self.logger.warning(f"Order not found | Folio: {folio:06d}")
                    if raise_if_not_found:
                        raise OrderNotFoundError(folio=folio)
                    return None

            except OrderNotFoundError:
                # Re-raise our custom exception
                raise
            except Exception as e:
                self.logger.error(
                    f"Error loading order | Folio: {folio:06d}",
                    exc_info=True
                )
                raise OrderLoadError(folio=folio, reason=str(e))

    def mark_order_as_registered(self, folio: int) -> bool:
        """
        Mark order as registered (sale completed)

        Args:
            folio: Folio number

        Returns:
            True if successful, False otherwise
        """
        try:
            self._log_info(f"Marcando orden {folio} como registrada")

            success = self.orden_repo.mark_as_registered(folio)

            if success:
                self._log_success(f"Orden {folio} marcada como registrada")
            else:
                self._log_warning(f"No se pudo marcar orden {folio} como registrada")

            return success

        except Exception as e:
            self._log_error(f"Error al marcar orden {folio} como registrada: {e}", e)
            return False

    def delete_order(self, folio: int) -> bool:
        """
        Delete order permanently from database

        Only deletes orders with estado='guardada'.
        Registered orders (estado='registrada') are protected by database trigger.

        Args:
            folio: Folio number

        Returns:
            True if successful, False otherwise

        Raises:
            Exception: If trying to delete a registered order
        """
        try:
            self._log_info(f"Eliminando orden: Folio {folio}")

            success = self.orden_repo.release_folio(folio)

            if success:
                self._log_success(f"Orden {folio} eliminada exitosamente")
            else:
                self._log_warning(f"No se pudo eliminar orden {folio}")

            return success

        except Exception as e:
            self._log_error(f"Error al eliminar orden {folio}: {e}", e)
            return False

    def get_active_orders(
        self,
        username: Optional[str] = None,
        is_admin: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all active (saved) orders

        Args:
            username: Filter by username (if not admin)
            is_admin: If True, return all orders

        Returns:
            List of order dictionaries
        """
        try:
            self._log_info("Obteniendo órdenes activas")

            orders = self.orden_repo.find_active_orders(username, is_admin)

            self._log_success(f"Se encontraron {len(orders)} órdenes activas")
            return orders

        except Exception as e:
            self._log_error(f"Error al obtener órdenes activas: {e}", e)
            return []

    # ==================== DATA PREPARATION ====================

    def prepare_cart_for_saving(self, carrito) -> Dict[str, Any]:
        """
        Prepare cart object for database storage

        Args:
            carrito: Cart object (CarritoConSeccionesV2)

        Returns:
            Dictionary ready for JSON serialization
        """
        try:
            self._log_info("Preparando datos del carrito para guardar")

            carrito_data = {
                'items': [],
                'sectioning_enabled': getattr(carrito, 'sectioning_enabled', False),
                'sections': []
            }

            # Process items
            for item in carrito.items:
                item_dict = {
                    'id_producto': item.id_producto,
                    'nombre': item.nombre,
                    'cantidad': item.cantidad,
                    'precio_unitario': item.precio_unitario,
                    'subtotal': item.subtotal,
                    'unidad': item.unidad,
                    'es_especial': item.es_especial,
                    'seccion': item.seccion
                }
                carrito_data['items'].append(item_dict)

            # Process sections if enabled
            if carrito.sectioning_enabled:
                for seccion in carrito.secciones:
                    seccion_dict = {
                        'nombre': seccion.nombre,
                        'orden': seccion.orden,
                        'color': seccion.color
                    }
                    carrito_data['sections'].append(seccion_dict)

            self._log_success(f"Carrito preparado: {len(carrito_data['items'])} items")
            return carrito_data

        except Exception as e:
            self._log_error(f"Error al preparar carrito: {e}", e)
            raise

    def prepare_items_for_pdf(
        self,
        carrito_items: List[Any]
    ) -> List[List[str]]:
        """
        Convert cart items to PDF format

        Args:
            carrito_items: List of cart items

        Returns:
            List of [quantity, product, price_unit, subtotal] for PDF
        """
        try:
            self._log_info("Preparando items para PDF")

            items_pdf = []
            for item in carrito_items:
                item_pdf = [
                    str(item.cantidad),
                    item.nombre,
                    f"${item.precio_unitario:.2f}",
                    f"${item.subtotal:.2f}"
                ]
                items_pdf.append(item_pdf)

            self._log_success(f"Items preparados para PDF: {len(items_pdf)} items")
            return items_pdf

        except Exception as e:
            self._log_error(f"Error al preparar items para PDF: {e}", e)
            return []

    def prepare_items_for_excel(
        self,
        carrito_items: List[Any]
    ) -> List[List[str]]:
        """
        Convert cart items to Excel format

        Args:
            carrito_items: List of cart items

        Returns:
            List of [quantity, product, price_unit, subtotal, unit] for Excel
        """
        try:
            self._log_info("Preparando items para Excel")

            items_excel = []
            for item in carrito_items:
                item_excel = [
                    str(item.cantidad),
                    item.nombre,
                    f"${item.precio_unitario:.2f}",
                    f"${item.subtotal:.2f}",
                    item.unidad
                ]
                items_excel.append(item_excel)

            self._log_success(f"Items preparados para Excel: {len(items_excel)} items")
            return items_excel

        except Exception as e:
            self._log_error(f"Error al preparar items para Excel: {e}", e)
            return []

    def prepare_sectioned_items_for_pdf(
        self,
        carrito
    ) -> tuple[Dict[str, Dict[str, Any]], float]:
        """
        Prepare sectioned cart data for PDF generation

        Args:
            carrito: Cart object with sections

        Returns:
            Tuple of (sections_dict, total)
        """
        try:
            self._log_info("Preparando items seccionados para PDF")

            items_por_seccion = {}
            total = 0.0

            # Get items organized by section
            if hasattr(carrito, 'obtener_items_por_seccion'):
                items_por_seccion_raw = carrito.obtener_items_por_seccion()

                for seccion_nombre, datos in items_por_seccion_raw.items():
                    # Convert items to PDF format
                    items_pdf = []
                    for item in datos['items']:
                        # item is already in format [qty, name, price, subtotal]
                        items_pdf.append(item)

                    items_por_seccion[seccion_nombre] = {
                        'items': items_pdf,
                        'subtotal': datos['subtotal']
                    }

                    total += datos['subtotal']

            self._log_success(f"Items seccionados preparados: {len(items_por_seccion)} secciones")
            return items_por_seccion, total

        except Exception as e:
            self._log_error(f"Error al preparar items seccionados: {e}", e)
            return {}, 0.0

    def prepare_sectioned_items_for_excel(
        self,
        carrito
    ) -> tuple[Dict[str, Dict[str, Any]], float]:
        """
        Prepare sectioned cart data for Excel generation

        Args:
            carrito: Cart object with sections

        Returns:
            Tuple of (sections_dict, total)
        """
        try:
            self._log_info("Preparando items seccionados para Excel")

            items_por_seccion = {}
            total = 0.0

            # Get items organized by section
            if hasattr(carrito, 'obtener_items_por_seccion_excel'):
                items_por_seccion_raw = carrito.obtener_items_por_seccion_excel()

                for seccion_nombre, datos in items_por_seccion_raw.items():
                    items_por_seccion[seccion_nombre] = {
                        'items': datos['items'],
                        'subtotal': datos['subtotal']
                    }
                    total += datos['subtotal']
            elif hasattr(carrito, 'obtener_items_por_seccion'):
                # Fallback: convert PDF format to Excel format
                items_por_seccion_raw = carrito.obtener_items_por_seccion()

                for seccion_nombre, datos in items_por_seccion_raw.items():
                    # Convert items: add 'unit' field (default 'pza')
                    items_excel = []
                    for item in datos['items']:
                        # item is [qty, name, price, subtotal]
                        # Excel needs [qty, name, price, subtotal, unit]
                        item_with_unit = item + ['pza']  # Default unit
                        items_excel.append(item_with_unit)

                    items_por_seccion[seccion_nombre] = {
                        'items': items_excel,
                        'subtotal': datos['subtotal']
                    }
                    total += datos['subtotal']

            self._log_success(f"Items seccionados preparados para Excel: {len(items_por_seccion)} secciones")
            return items_por_seccion, total

        except Exception as e:
            self._log_error(f"Error al preparar items seccionados para Excel: {e}", e)
            return {}, 0.0

    # ==================== UTILITY METHODS ====================

    def calculate_order_total(self, carrito_items: List[Any]) -> float:
        """
        Calculate total from cart items

        Args:
            carrito_items: List of cart items

        Returns:
            Total amount
        """
        try:
            total = sum(item.subtotal for item in carrito_items)
            return float(total)
        except Exception as e:
            self._log_error(f"Error al calcular total: {e}", e)
            return 0.0

    def get_order_summary(self, folio: int) -> Optional[Dict[str, Any]]:
        """
        Get order summary for display

        Args:
            folio: Folio number

        Returns:
            Order summary dict or None
        """
        try:
            orden = self.load_order(folio)
            if not orden:
                return None

            summary = {
                'folio': orden['folio_numero'],
                'cliente': orden.get('nombre_cliente', 'N/A'),
                'usuario': orden.get('usuario_creador', 'N/A'),
                'fecha': orden.get('fecha_creacion'),
                'total': orden.get('total_estimado', 0.0),
                'estado': orden.get('estado', 'N/A'),
                'num_items': len(orden.get('datos_carrito_obj', {}).get('items', []))
            }

            return summary

        except Exception as e:
            self._log_error(f"Error al obtener resumen de orden: {e}", e)
            return None
