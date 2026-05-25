# -*- coding: utf-8 -*-
"""
UI Layer - Purchase Application
Coordinates View and Controller following MVC pattern
ACTUALIZADO: Incluye búsqueda avanzada con filtros
"""

from decimal import Decimal
from datetime import date, datetime
import re
from typing import Dict, Any, List

from .purchase_view import PurchaseView
from .purchase_history_dialog import PurchaseHistoryDialog
from ..business.purchase_service import PurchaseService
from ..business.product_service import ProductService
from ..models.purchase_cart import PurchaseCart, PurchaseCartItem
from ..domain.models import (
    BusinessLogicError,
    ProductNotFoundError,
    InvalidDateError,
    DuplicateProductError,
    PurchaseSearchCriteria
)


class PurchaseApplication:
    """
    Main Application Controller
    Coordinates View with Business Services
    NO direct database access - uses services only!
    """

    def __init__(
        self,
        root,
        user_data: dict,
        purchase_service: PurchaseService,
        product_service: ProductService
    ):
        """
        Initialize application

        Args:
            root: CTk root window
            user_data: User information
            purchase_service: Purchase business service
            product_service: Product business service
        """
        self.user_data = user_data
        self.purchase_service = purchase_service
        self.product_service = product_service

        # Initialize shopping cart
        self.cart = PurchaseCart()
        self.cart.add_listener(self._on_cart_change)

        # Create view
        self.view = PurchaseView(root, user_data)

        # Connect view callbacks to controller methods
        self._connect_callbacks()

        # Load initial data
        self._load_initial_data()

    def _connect_callbacks(self):
        """Connect view callbacks to controller methods"""
        self.view.on_register_purchase = self.handle_register_purchase
        self.view.on_edit_purchase = self.handle_edit_purchase
        self.view.on_delete_purchase = self.handle_delete_purchase
        self.view.on_create_product = self.handle_create_product
        self.view.on_refresh = self.handle_refresh
        
        # NUEVO: Callback para historial avanzado
        self.view.on_open_advanced_history = self.handle_open_advanced_history

        # Cart callbacks
        self.view.on_add_to_cart = self.handle_add_to_cart
        self.view.on_remove_from_cart = self.handle_remove_from_cart
        self.view.on_batch_register = self.handle_batch_register

        # Connect product search to filtering
        self.view.producto_search_entry.bind("<KeyRelease>", lambda e: self.handle_product_search())
        self.view.producto_search_var.trace("w", lambda *args: self.handle_product_search())

        # Connect quantity/price changes to total calculation
        self.view.cantidad_var.trace("w", lambda *args: self.calculate_totals())
        self.view.precio_var.trace("w", lambda *args: self.calculate_totals())
        self.view.incluir_iva_var.trace("w", lambda *args: self.calculate_totals())
        self.view.ieps_var.trace("w", lambda *args: self.calculate_totals())

    def _load_initial_data(self):
        """Load initial data from services"""
        try:
            # Load products
            products = self.product_service.get_all_products()
            product_list = [f"{p.nombre_producto} ({p.unidad_producto})" for p in products]
            self.view.set_products(product_list)

            # Store product mapping
            self.product_map = {
                f"{p.nombre_producto} ({p.unidad_producto})": p
                for p in products
            }

            # Load purchases
            self.handle_refresh()

            self.view.update_status("Datos cargados correctamente")

        except Exception as e:
            self.view.show_message("Error", f"Error cargando datos: {str(e)}", "error")

    # ==================== EVENT HANDLERS ====================

    def handle_product_search(self):
        """Handle product search/filter"""
        try:
            # Get search text directly from widget (PyInstaller compatible)
            search_text = self.view.producto_search_entry.get()
            self.view.filter_products(search_text)
        except Exception as e:
            print(f"Error filtering products: {e}")

    def calculate_totals(self):
        """Calculate and update totals"""
        try:
            cantidad_str = self.view.cantidad_var.get()
            precio_str = self.view.precio_var.get()
            ieps_str = self.view.ieps_var.get() or "0"
            incluir_iva = self.view.incluir_iva_var.get()

            if not cantidad_str or not precio_str:
                self.view.update_totals(Decimal("0"), Decimal("0"), Decimal("0"))
                return

            cantidad = Decimal(cantidad_str)
            precio = Decimal(precio_str)
            ieps = Decimal(ieps_str)

            subtotal = cantidad * precio
            iva = subtotal * Decimal("0.16") if incluir_iva else Decimal("0")
            total = subtotal + iva + ieps

            self.view.update_totals(subtotal, iva, total)

        except (ValueError, ArithmeticError):
            self.view.update_totals(Decimal("0"), Decimal("0"), Decimal("0"))

    def handle_register_purchase(self):
        """Handle purchase registration"""
        try:
            # Get form data
            data = self.view.get_form_data()

            # Validate required fields
            if not data['producto']:
                self.view.show_message("Error", "Debe seleccionar un producto", "error")
                return

            if not data['cantidad'] or not data['precio']:
                self.view.show_message("Error", "Cantidad y precio son obligatorios", "error")
                return

            # Get product ID
            product = self.product_map.get(data['producto'])
            if not product:
                self.view.show_message("Error", "Producto no válido", "error")
                return

            # Create purchase using service
            purchase_id = self.purchase_service.create_purchase(
                id_producto=product.id_producto,
                cantidad_compra=Decimal(data['cantidad']),
                precio_unitario_compra=Decimal(data['precio']),
                fecha_compra=date.fromisoformat(data['fecha_compra']),
                fecha_registro=date.fromisoformat(data['fecha_registro']),
                incluir_iva=data['incluir_iva'],
                folio_factura=data['folio'] if data['folio'] else None,
                proveedor=data['proveedor'] if data['proveedor'] else None,
                rfc_proveedor=data['rfc'] if data['rfc'] else None,
                importe_ieps=Decimal(data['ieps']) if data['ieps'] else Decimal("0"),
                tasa_interes=Decimal(data['tasa_interes']) if data['tasa_interes'] else Decimal("0"),
                metodo_pago=data['metodo_pago'],
                forma_pago=data['forma_pago'],
                usuario_registro=self.user_data.get('username', 'Usuario'),
                notas=data['notas'] if data['notas'] else None
            )

            self.view.show_message(
                "Éxito",
                f"Compra registrada exitosamente (ID: {purchase_id})",
                "success"
            )

            # Clear form and refresh
            self.view.clear_form()
            self.handle_refresh()
            self.view.update_status(f"Compra {purchase_id} registrada")

        except InvalidDateError as e:
            self.view.show_message("Error de Fecha", str(e), "error")
        except BusinessLogicError as e:
            self.view.show_message("Error de Validación", str(e), "warning")
        except Exception as e:
            self.view.show_message("Error", f"Error al registrar compra: {str(e)}", "error")
            import traceback
            traceback.print_exc()

    def handle_edit_purchase(self, compra: Dict):
        """Handle purchase edit"""
        # TODO: Implement edit functionality
        self.view.show_message("Info", "Funcionalidad de edición próximamente", "info")

    def handle_delete_purchase(self, compra: Dict):
        """Handle purchase deletion"""
        try:
            purchase_id = compra['id_compra']

            # Confirm deletion
            from tkinter import messagebox
            confirm = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro de eliminar la compra #{purchase_id}?\n\n"
                f"Producto: {compra['nombre_producto']}\n"
                f"Cantidad: {compra['cantidad_compra']} {compra['unidad_producto']}\n"
                f"Total: ${compra['total_con_impuestos']:,.2f}",
                parent=self.view.root
            )

            if not confirm:
                return

            # Delete using service
            self.purchase_service.delete_purchase(purchase_id)

            self.view.show_message(
                "Éxito",
                "Compra eliminada exitosamente",
                "success"
            )

            # Refresh list
            self.handle_refresh()
            self.view.update_status(f"Compra {purchase_id} eliminada")

        except Exception as e:
            self.view.show_message("Error", f"Error al eliminar compra: {str(e)}", "error")

    def handle_create_product(self):
        """Handle product creation dialog"""
        from .product_dialog import create_product_dialog

        success, product_data = create_product_dialog(self.view.root)

        if success:
            try:
                product_id = self.product_service.create_product(
                    nombre_producto=product_data['nombre'],
                    unidad_producto=product_data['unidad']
                )

                self.view.show_message(
                    "Éxito",
                    f"Producto '{product_data['nombre']}' creado exitosamente",
                    "success"
                )

                # Reload products
                self._load_initial_data()

            except DuplicateProductError as e:
                self.view.show_message("Error", str(e), "warning")
            except Exception as e:
                self.view.show_message("Error", f"Error al crear producto: {str(e)}", "error")

    def handle_refresh(self):
        """Refresh purchase list"""
        try:
            # Get all purchases from service
            purchases = self.purchase_service.get_all_purchases()

            # Convert to dict format for view
            purchases_dict = [
                {
                    'id_compra': p.id_compra,
                    'nombre_producto': p.nombre_producto,
                    'unidad_producto': p.unidad_producto,
                    'cantidad_compra': p.cantidad_compra,
                    'precio_unitario_compra': p.precio_unitario_compra,
                    'fecha_compra': p.fecha_compra,
                    'total_con_impuestos': p.total_con_impuestos,
                    'proveedor': p.proveedor,
                    'folio_factura': p.folio_factura
                }
                for p in purchases
            ]

            # Update view
            self.view.display_purchases(purchases_dict)
            self.view.update_status(f"{len(purchases)} compras encontradas")

        except Exception as e:
            self.view.show_message("Error", f"Error al cargar compras: {str(e)}", "error")

    # ==================== NUEVO: HISTORIAL AVANZADO ====================

    def handle_open_advanced_history(self):
        """Open advanced purchase history dialog"""
        try:
            # Create dialog
            dialog = PurchaseHistoryDialog(
                parent=self.view.root,
                on_search=self.handle_advanced_search,
                on_delete=self.handle_delete_purchase
            )

            # Get all data
            purchases = self.purchase_service.get_all_purchases()
            products = self.product_service.get_all_products()

            # Prepare data
            purchases_dict = [
                {
                    'id_compra': p.id_compra,
                    'id_producto': p.id_producto,
                    'nombre_producto': p.nombre_producto,
                    'unidad_producto': p.unidad_producto,
                    'cantidad_compra': p.cantidad_compra,
                    'precio_unitario_compra': p.precio_unitario_compra,
                    'fecha_compra': p.fecha_compra,
                    'fecha_registro': p.fecha_registro,
                    'subtotal': p.subtotal,
                    'iva': p.iva,
                    'total_con_impuestos': p.total_con_impuestos,
                    'proveedor': p.proveedor,
                    'rfc_proveedor': p.rfc_proveedor,
                    'folio_factura': p.folio_factura,
                    'usuario_registro': p.usuario_registro
                }
                for p in purchases
            ]

            products_list = [p.nombre_producto for p in products]
            suppliers_list = list(set([p.proveedor for p in purchases if p.proveedor]))

            # Set data in dialog
            dialog.set_purchases_data(purchases_dict, products_list, suppliers_list)

        except Exception as e:
            self.view.show_message("Error", f"Error al abrir historial: {str(e)}", "error")
            import traceback
            traceback.print_exc()

    def handle_advanced_search(self, filters: Dict) -> List[Dict]:
        """Handle advanced search with filters"""
        try:
            # Get all purchases
            purchases = self.purchase_service.get_all_purchases()

            # Convert to dict
            results = [
                {
                    'id_compra': p.id_compra,
                    'id_producto': p.id_producto,
                    'nombre_producto': p.nombre_producto,
                    'unidad_producto': p.unidad_producto,
                    'cantidad_compra': p.cantidad_compra,
                    'precio_unitario_compra': p.precio_unitario_compra,
                    'fecha_compra': p.fecha_compra,
                    'fecha_registro': p.fecha_registro,
                    'subtotal': p.subtotal,
                    'iva': p.iva,
                    'total_con_impuestos': p.total_con_impuestos,
                    'proveedor': p.proveedor,
                    'rfc_proveedor': p.rfc_proveedor,
                    'folio_factura': p.folio_factura,
                    'usuario_registro': p.usuario_registro
                }
                for p in purchases
            ]

            # Apply filters
            results = self._apply_custom_filters(results, filters)

            return results

        except Exception as e:
            print(f"Error in advanced search: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _apply_custom_filters(self, purchases: List[Dict], filters: Dict) -> List[Dict]:
        """Apply custom filters to purchase list"""
        # Search text
        if filters.get('search_text'):
            search_lower = filters['search_text'].lower()
            purchases = [p for p in purchases if (
                search_lower in (p.get('nombre_producto') or '').lower() or
                search_lower in (p.get('proveedor') or '').lower() or
                search_lower in (p.get('folio_factura') or '').lower() or
                search_lower in (p.get('rfc_proveedor') or '').lower()
            )]

        # Product filter
        if filters.get('producto'):
            purchases = [p for p in purchases if p.get('nombre_producto') == filters['producto']]

        # Supplier filter
        if filters.get('proveedor'):
            purchases = [p for p in purchases if p.get('proveedor') == filters['proveedor']]

        # Date filters
        if filters.get('fecha_inicio'):
            try:
                fecha_inicio = date.fromisoformat(filters['fecha_inicio'])
                purchases = [p for p in purchases if p.get('fecha_compra') >= fecha_inicio]
            except:
                pass

        if filters.get('fecha_fin'):
            try:
                fecha_fin = date.fromisoformat(filters['fecha_fin'])
                purchases = [p for p in purchases if p.get('fecha_compra') <= fecha_fin]
            except:
                pass

        # Quantity filters
        if filters.get('cantidad_min'):
            try:
                min_qty = Decimal(filters['cantidad_min'])
                purchases = [p for p in purchases if p.get('cantidad_compra', 0) >= min_qty]
            except:
                pass

        if filters.get('cantidad_max'):
            try:
                max_qty = Decimal(filters['cantidad_max'])
                purchases = [p for p in purchases if p.get('cantidad_compra', 0) <= max_qty]
            except:
                pass

        # Price filters
        if filters.get('precio_min'):
            try:
                min_price = Decimal(filters['precio_min'])
                purchases = [p for p in purchases if p.get('precio_unitario_compra', 0) >= min_price]
            except:
                pass

        if filters.get('precio_max'):
            try:
                max_price = Decimal(filters['precio_max'])
                purchases = [p for p in purchases if p.get('precio_unitario_compra', 0) <= max_price]
            except:
                pass

        # Fiscal filters
        if filters.get('solo_fiscales'):
            purchases = [p for p in purchases if (
                p.get('folio_factura') and
                p.get('proveedor') and
                p.get('rfc_proveedor')
            )]

        if filters.get('solo_informales'):
            purchases = [p for p in purchases if not (
                p.get('folio_factura') and
                p.get('proveedor') and
                p.get('rfc_proveedor')
            )]

        return purchases

    # ==================== CART HANDLERS ====================

    def handle_add_to_cart(self):
        """Add current form data to cart"""
        try:
            # Get and validate form data
            form_data = self.view.get_form_data()

            # Extract product info
            producto_str = form_data['producto']
            if not producto_str or producto_str not in self.product_map:
                self.view.show_message("Error", "Por favor selecciona un producto válido", "error")
                return

            product = self.product_map[producto_str]

            # Validate quantity
            try:
                cantidad = Decimal(form_data['cantidad'])
                if cantidad <= 0:
                    self.view.show_message("Error", "La cantidad debe ser mayor a 0", "error")
                    return
            except:
                self.view.show_message("Error", "Cantidad inválida", "error")
                return

            # Validate price
            try:
                precio = Decimal(form_data['precio'])
                if precio <= 0:
                    self.view.show_message("Error", "El precio debe ser mayor a 0", "error")
                    return
            except:
                self.view.show_message("Error", "Precio inválido", "error")
                return

            # Get optional fields
            try:
                ieps = Decimal(form_data['ieps']) if form_data['ieps'] else Decimal("0")
            except:
                ieps = Decimal("0")

            # Create cart item
            cart_item = PurchaseCartItem(
                id_producto=product.id_producto,
                nombre_producto=product.nombre_producto,
                unidad_producto=product.unidad_producto,
                cantidad=cantidad,
                precio_unitario=precio,
                folio_factura=form_data['folio'] or None,
                proveedor=form_data['proveedor'] or None,
                rfc_proveedor=form_data['rfc'] or None,
                incluir_iva=form_data['incluir_iva'],
                importe_ieps=ieps
            )

            # Add to cart
            self.cart.add_item(cart_item)

            # Clear form
            self.view.clear_form()

            # Show success
            self.view.update_status(f"✅ {product.nombre_producto} agregado al carrito")

        except Exception as e:
            self.view.show_message("Error", f"Error al agregar al carrito: {str(e)}", "error")

    def handle_remove_from_cart(self, cart_id: str):
        """Remove item from cart"""
        try:
            if self.cart.remove_item(cart_id):
                self.view.update_status("Item eliminado del carrito")
            else:
                self.view.show_message("Error", "No se encontró el item en el carrito", "error")
        except Exception as e:
            self.view.show_message("Error", f"Error al eliminar del carrito: {str(e)}", "error")

    def handle_batch_register(self):
        """Register all items in cart"""
        try:
            # Validate cart
            is_valid, error_msg = self.cart.validate_cart()
            if not is_valid:
                self.view.show_message("Error", error_msg, "error")
                return

            # Confirm action
            from tkinter import messagebox
            items_count = self.cart.get_item_count()
            totals = self.cart.get_totals()

            confirm = messagebox.askyesno(
                "Confirmar Registro",
                f"¿Deseas registrar {items_count} compras?\n\n"
                f"Total: ${float(totals['total']):,.2f}\n"
                f"(Subtotal: ${float(totals['subtotal']):,.2f} + "
                f"IVA: ${float(totals['iva']):,.2f})",
                parent=self.view.root
            )

            if not confirm:
                return

            # Register each item
            registered_count = 0
            failed_items = []

            for item in self.cart.get_items():
                try:
                    # Parse dates
                    fecha_compra = date.today()
                    fecha_registro = date.today()

                    # Register purchase
                    self.purchase_service.create_purchase(
                        id_producto=item.id_producto,
                        cantidad_compra=item.cantidad,
                        precio_unitario_compra=item.precio_unitario,
                        fecha_compra=fecha_compra,
                        fecha_registro=fecha_registro,
                        incluir_iva=item.incluir_iva,
                        importe_ieps=item.importe_ieps,
                        folio_factura=item.folio_factura,
                        proveedor=item.proveedor,
                        rfc_proveedor=item.rfc_proveedor,
                        usuario_registro=self.user_data.get('nombre_completo', 'Sistema')
                    )
                    registered_count += 1

                except Exception as e:
                    failed_items.append(f"{item.nombre_producto}: {str(e)}")

            # Clear cart
            self.cart.clear()

            # Show results
            if failed_items:
                error_msg = "\n".join(failed_items)
                self.view.show_message(
                    "Registro Parcial",
                    f"Se registraron {registered_count} de {items_count} compras.\n\n"
                    f"Errores:\n{error_msg}",
                    "warning"
                )
            else:
                self.view.show_message(
                    "Éxito",
                    f"Se registraron exitosamente {registered_count} compras",
                    "success"
                )

            # Refresh purchase list
            self.handle_refresh()

        except Exception as e:
            self.view.show_message("Error", f"Error al registrar compras: {str(e)}", "error")

    def _on_cart_change(self):
        """Called when cart changes"""
        # Update cart display in view
        items = self.cart.get_items()
        items_dict = [item.to_dict() for item in items]
        self.view.update_cart_display(items_dict)