# -*- coding: utf-8 -*-
"""
UbicuoAI Controller - UI Layer (Refactorizado)
Coordina interacciones de usuario con servicios de negocio.
Patrón MVC - Separa UI de lógica de negocio.
"""

import logging
from typing import Optional, List, Tuple, Dict, Any
from decimal import Decimal

from ...business.ubicuoai_service import EnhancedUbicuoAIService
from ...domain.models import OrderItem, ProductMatch, OrderParseResult
from ...domain.value_objects import Unit
from ...domain.exceptions import (
    InvalidOrderFormatError,
    InvalidQuantityError,
    UbicuoAIError
)

from .section_controller import SectionController

logger = logging.getLogger(__name__)


class ControllerError(Exception):
    """Excepción base para errores del controller"""
    pass


class ClientNotSelectedError(ControllerError):
    """Error cuando no hay cliente seleccionado"""
    pass


class NoResultsError(ControllerError):
    """Error cuando no hay resultados para procesar"""
    pass


class UbicuoAIController:
    """
    Controller principal para interfaz UbicuoAI.
    Coordina entre UI y servicios de negocio.
    """

    def __init__(
        self,
        service: EnhancedUbicuoAIService,
        on_status_update: callable,
        on_stats_update: callable,
        on_client_changed: callable = None,
        product_service = None,
        user_data: Optional[Dict] = None
    ):
        """
        Inicializa el controller.
        
        Args:
            service: Servicio principal de UbicuoAI
            on_status_update: Callback para actualizar status (msg, level)
            on_stats_update: Callback para actualizar stats (total, matched)
            on_client_changed: Callback cuando cambia el cliente
            product_service: Servicio de productos (opcional)
            user_data: Datos del usuario logueado
        """
        self.service = service
        self.on_status_update = on_status_update
        self.on_stats_update = on_stats_update
        self.on_client_changed = on_client_changed
        self.product_service = product_service
        self.user_data = user_data or {'username': 'system'}

        # Estado actual
        self.current_parse_result: Optional[OrderParseResult] = None
        self.current_matches: List[Optional[ProductMatch]] = []
        self.current_statistics: Dict = {}
        
        # Controller de secciones (composición)
        self._section_ctrl = SectionController(on_status_update)
        
        logger.info("UbicuoAIController inicializado")

    # ==================== PROCESAMIENTO DE PEDIDOS ====================

    def process_order(self, order_text: str) -> bool:
        """
        Procesa texto de pedido.
        
        Args:
            order_text: Texto del pedido a procesar
            
        Returns:
            True si el procesamiento fue exitoso
            
        Raises:
            InvalidOrderFormatError: Si el formato es inválido
            UbicuoAIError: Para otros errores de dominio
        """
        if not order_text or not order_text.strip():
            self.on_status_update("⚠️ Por favor ingresa un pedido primero", "warning")
            return False

        self.on_status_update("🔄 Procesando pedido...", "info")

        try:
            # Procesar a través del servicio
            parse_result, matches, statistics = self.service.process_order(order_text)

            # Guardar resultados
            self.current_parse_result = parse_result
            self.current_matches = matches
            self.current_statistics = statistics

            # Validar y corregir unidades
            self._validate_units(parse_result, matches)

            # Detectar secciones
            if parse_result and parse_result.items:
                detected_sections = self._section_ctrl.detect_sections(
                    order_text, 
                    parse_result.items
                )
                self.current_statistics['sections_detected'] = len(detected_sections)

            # Actualizar estadísticas en UI
            matched_count = statistics.get('matched_products', 0)
            total_products = statistics.get('total_products', 0)
            self.on_stats_update(total_products, matched_count)

            # Mensaje de status
            status_msg = f"✓ Procesamiento completo: {matched_count}/{total_products} productos identificados"
            if statistics.get('sections_detected', 0) > 0:
                status_msg += f" | {statistics['sections_detected']} secciones"
            if statistics.get('unmatched_products', 0) > 0:
                status_msg += f" | {statistics['unmatched_products']} sin match"
            
            self.on_status_update(status_msg, "success")
            logger.info(f"Pedido procesado: {matched_count}/{total_products} productos")

            return True

        except InvalidOrderFormatError as e:
            self.on_status_update(f"❌ Formato inválido: {str(e)}", "error")
            logger.warning(f"Formato de pedido inválido: {e}")
            raise

        except UbicuoAIError as e:
            self.on_status_update(f"❌ Error: {str(e)}", "error")
            logger.error(f"Error de dominio: {e}")
            raise

        except Exception as e:
            self.on_status_update(f"❌ Error inesperado: {str(e)}", "error")
            logger.exception(f"Error inesperado procesando pedido: {e}")
            raise UbicuoAIError(f"Error procesando pedido: {str(e)}") from e

    def _validate_units(
        self,
        parse_result: OrderParseResult,
        matches: List[Optional[ProductMatch]]
    ) -> List[Dict]:
        """
        Valida que las unidades parseadas coincidan con las del producto.
        
        Returns:
            Lista de discrepancias encontradas
        """
        discrepancies = []
        
        for i, (item, match) in enumerate(zip(parse_result.items, matches)):
            if item.is_section or match is None:
                continue

            parsed_unit = item.unit
            product_unit = match.unit

            if parsed_unit and product_unit:
                try:
                    if Unit.are_equivalent(parsed_unit.value, product_unit.value):
                        continue
                except AttributeError:
                    pass

            # Registrar discrepancia
            discrepancies.append({
                'line': item.line_number,
                'product': item.product_name,
                'parsed_unit': str(parsed_unit) if parsed_unit else None,
                'product_unit': str(product_unit) if product_unit else None
            })
            
            # Corregir unidad en el item
            item.unit = product_unit
        
        if discrepancies:
            logger.info(f"Corregidas {len(discrepancies)} unidades")
        
        return discrepancies

    # ==================== SUGERENCIAS Y CORRECCIONES ====================

    def get_suggestions(self, product_name: str, limit: int = 5) -> List[ProductMatch]:
        """Obtiene sugerencias de productos"""
        try:
            return self.service.get_product_suggestions(product_name, limit)
        except Exception as e:
            logger.exception(f"Error obteniendo sugerencias: {e}")
            return []

    def accept_suggestion(self, incorrect: str, correct: str) -> bool:
        """Acepta una sugerencia y aprende la corrección"""
        try:
            success = self.service.learn_correction(incorrect, correct)
            if success:
                self.on_status_update(
                    f"✓ Corrección aprendida: {incorrect} → {correct}",
                    "success"
                )
                logger.info(f"Corrección aprendida: {incorrect} → {correct}")
            return success
        except ValueError as e:
            logger.warning(f"Error de validación en corrección: {e}")
            raise
        except Exception as e:
            logger.exception(f"Error guardando corrección: {e}")
            raise UbicuoAIError(f"Error guardando corrección: {str(e)}") from e

    def learn_correction(self, incorrect: str, correct: str) -> bool:
        """Alias para accept_suggestion (compatibilidad)"""
        return self.accept_suggestion(incorrect, correct)

    # ==================== RESULTADOS ====================

    def get_current_results(self) -> Tuple[Optional[OrderParseResult], List[Optional[ProductMatch]]]:
        """Obtiene resultados actuales de parseo y matches"""
        return self.current_parse_result, self.current_matches

    def clear_results(self):
        """Limpia resultados actuales"""
        self.current_parse_result = None
        self.current_matches = []
        self.current_statistics = {}
        self._section_ctrl.clear()
        self.on_stats_update(0, 0)
        logger.debug("Resultados limpiados")

    def get_statistics(self) -> Dict:
        """Obtiene estadísticas del sistema"""
        return self.service.get_system_statistics()

    # ==================== CLIENTES ====================

    def get_all_clients(self) -> List[Dict]:
        """Obtiene todos los clientes"""
        try:
            return self.service.get_all_clients()
        except Exception as e:
            logger.exception(f"Error obteniendo clientes: {e}")
            return []

    def select_client(self, client_id: Optional[int]) -> bool:
        """
        Selecciona un cliente para precios.
        Refresca automáticamente precios si hay resultados.
        """
        try:
            client = self.service.set_selected_client(client_id)

            if client_id and client:
                self.on_status_update(
                    f"✓ Cliente seleccionado: {client['nombre_cliente']} ({client['clave_grupo']})",
                    "success"
                )
                if self.on_client_changed:
                    self.on_client_changed(client)
                
                # Auto-refresh precios
                if self.current_parse_result and self.current_parse_result.items:
                    self.refresh_prices_for_current_results()

            elif client_id is None:
                self.on_status_update("Cliente deseleccionado", "info")
                if self.on_client_changed:
                    self.on_client_changed(None)
                if self.current_parse_result and self.current_parse_result.items:
                    self.refresh_prices_for_current_results()
            else:
                self.on_status_update("⚠️ Cliente no encontrado", "warning")
                return False

            return True

        except Exception as e:
            logger.exception(f"Error seleccionando cliente: {e}")
            raise UbicuoAIError(f"Error seleccionando cliente: {str(e)}") from e

    def get_selected_client(self) -> Optional[Dict]:
        """Obtiene cliente actualmente seleccionado"""
        return self.service.get_selected_client()

    def refresh_prices_for_current_results(self) -> bool:
        """Refresca precios para resultados actuales después de cambio de cliente/grupo"""
        if not self.current_parse_result or not self.current_parse_result.items:
            return False
        
        try:
            self.on_status_update("🔄 Actualizando precios...", "info")
            
            new_matches = []
            for item in self.current_parse_result.items:
                if item.is_section_header:
                    new_matches.append(None)
                    continue
                
                match = self.service.match_single_product(item.product_name, item.unit)
                new_matches.append(match)
            
            self.current_matches = new_matches
            
            matched_count = sum(1 for m in new_matches if m is not None)
            total_count = len([i for i in self.current_parse_result.items if not i.is_section_header])
            self.on_stats_update(total_count, matched_count)
            
            client = self.get_selected_client()
            if client:
                self.on_status_update(f"✓ Precios actualizados para {client['nombre_cliente']}", "success")
            else:
                self.on_status_update("✓ Precios actualizados (sin cliente)", "info")
            
            return True
            
        except Exception as e:
            self.on_status_update(f"❌ Error actualizando precios: {str(e)}", "error")
            logger.exception(f"Error actualizando precios: {e}")
            return False

    # ==================== ENVÍO A RECEIPT GENERATOR ====================

    def send_to_receipt_generator(
        self,
        results: List[Tuple[OrderItem, Optional[ProductMatch]]],
        quantity_overrides: Optional[Dict[int, Dict[str, Any]]] = None
    ) -> Tuple[bool, Optional[int]]:
        """
        Envía productos a receipt generator.
        
        Args:
            results: Lista de (OrderItem, ProductMatch) tuples
            quantity_overrides: Dict opcional {line_number: {'quantity': float, 'unit': str}}
            
        Returns:
            Tuple (success: bool, folio: Optional[int])
            
        Raises:
            ClientNotSelectedError: Si no hay cliente seleccionado
            NoResultsError: Si no hay resultados válidos
        """
        # Validar cliente
        client = self.get_selected_client()
        if not client:
            raise ClientNotSelectedError("Por favor selecciona un cliente antes de enviar")

        # Validar resultados
        if not results:
            raise NoResultsError("No hay productos para enviar")

        valid_results = [(item, match) for item, match in results if match is not None]
        if not valid_results:
            raise NoResultsError("No hay productos identificados para enviar")

        # Preparar items con secciones
        items_to_send = self._prepare_items_for_receipt(valid_results, quantity_overrides)

        try:
            # Importar componentes de Receipt Generator
            from src.modules.receipts.models.cart_model import CartModel
            from src.modules.receipts.mvc.models.receipt_model import ReciboModel

            id_cliente = client['id_cliente']
            clave_grupo = client.get('clave_grupo', '')

            if not clave_grupo:
                raise ValueError("Cliente no tiene grupo asignado")

            receipt_model = ReciboModel()
            cart = CartModel()

            # Crear secciones en el cart
            if self._section_ctrl.sections_detected:
                sections = self._section_ctrl.get_detected_sections()
                for section in sections:
                    if section.get("confirmed", False):
                        section_name = section["name"]
                        if section_name != "GENERAL":
                            cart.add_section(section_name)

            # Agregar items al cart
            self.on_status_update("🔄 Obteniendo precios...", "info")
            productos_sin_precio = []

            for item_data in items_to_send:
                product_id = item_data['matched_id']
                product_name = item_data['matched_name']
                order_quantity = item_data['quantity']
                section_name = item_data.get('seccion', 'GENERAL')

                productos = receipt_model.buscar_productos(
                    clave_grupo=clave_grupo,
                    texto_busqueda=product_name
                )

                producto_data = next(
                    (p for p in productos if p['id_producto'] == product_id),
                    None
                )

                if not producto_data:
                    productos_sin_precio.append(product_name)
                    continue

                cart.add_item(
                    id_producto=producto_data['id_producto'],
                    nombre=producto_data['nombre_producto'],
                    cantidad=float(order_quantity),
                    precio_unitario=float(producto_data.get('precio', 0)),
                    unidad=producto_data['unidad'],
                    seccion=section_name,
                    es_especial=False
                )

            if cart.is_empty():
                error_msg = "No se pudieron agregar productos al carrito"
                if productos_sin_precio:
                    error_msg += f". Sin precio: {', '.join(productos_sin_precio)}"
                raise NoResultsError(error_msg)

            # Guardar orden
            self.on_status_update("💾 Guardando orden...", "info")

            carrito_data = cart.to_dict()
            total = cart.get_total()
            username = self.user_data.get('username', 'system')

            logger.debug(f"Guardando cart: {len(carrito_data.get('items', []))} items, total=${total:.2f}")

            folio_result = receipt_model.guardar_orden(
                id_cliente=id_cliente,
                carrito_data=carrito_data,
                total=total,
                usuario=username,
                folio_existente=None
            )

            folio = folio_result[0] if isinstance(folio_result, tuple) else folio_result

            if not folio:
                raise Exception("No se pudo guardar la orden")

            self.on_status_update(f"✅ Orden guardada: Folio #{folio:06d}", "success")
            logger.info(f"Orden guardada con folio {folio}")

            return (True, folio)

        except (ClientNotSelectedError, NoResultsError):
            raise
        except Exception as e:
            logger.exception(f"Error enviando a receipt generator: {e}")
            raise UbicuoAIError(f"Error al enviar: {str(e)}") from e

    def _prepare_items_for_receipt(
        self,
        valid_results: List[Tuple[OrderItem, ProductMatch]],
        quantity_overrides: Optional[Dict]
    ) -> List[Dict]:
        """Prepara items para enviar al receipt generator"""
        items_to_send = []
        
        for order_item, product_match in valid_results:
            seccion = 'GENERAL'
            if self._section_ctrl.sections_detected:
                seccion = self._section_ctrl.get_section_for_item(order_item.line_number)
            
            line_num = order_item.line_number
            if quantity_overrides and line_num in quantity_overrides:
                quantity = quantity_overrides[line_num].get('quantity', order_item.quantity)
                unit_override = quantity_overrides[line_num].get('unit')
            else:
                quantity = order_item.quantity
                unit_override = None
            
            items_to_send.append({
                'line_number': line_num,
                'quantity': quantity,
                'unit_override': unit_override,
                'raw_text': order_item.raw_text,
                'matched_id': product_match.matched_id,
                'matched_name': product_match.matched_name,
                'seccion': seccion
            })
        
        return items_to_send

    # ==================== CREACIÓN DE PRODUCTOS ====================

    def create_product(self, nombre_producto: str, unidad_producto: str) -> Optional[int]:
        """Crea un nuevo producto usando el servicio de inventario"""
        if not self.product_service:
            raise ControllerError("Servicio de productos no disponible")

        try:
            from src.modules.inventory.domain.models import DuplicateProductError, BusinessLogicError
            
            product_id = self.product_service.create_product(
                nombre_producto=nombre_producto,
                unidad_producto=unidad_producto,
                stock=Decimal("0"),
                es_especial=False
            )

            self._reload_matcher_cache()
            self.on_status_update(f"✓ Producto '{nombre_producto}' creado", "success")
            logger.info(f"Producto creado: {nombre_producto} (ID: {product_id})")

            return product_id

        except Exception as e:
            logger.exception(f"Error creando producto: {e}")
            raise ControllerError(f"Error al crear producto: {str(e)}") from e

    def _reload_matcher_cache(self):
        """Recarga caché del matcher después de crear producto"""
        try:
            self.service.reload_products()
        except Exception as e:
            logger.warning(f"Error recargando caché de productos: {e}")

    # ==================== DELEGACIÓN A SECTION CONTROLLER ====================
    
    @property
    def sections_detected(self) -> bool:
        return self._section_ctrl.sections_detected
    
    @sections_detected.setter
    def sections_detected(self, value: bool):
        self._section_ctrl.sections_detected = value
    
    @property
    def section_manager(self):
        """Acceso directo al section manager (compatibilidad)"""
        return self._section_ctrl.section_manager
    
    def detect_sections(self, raw_text: str, parsed_items: list) -> list:
        return self._section_ctrl.detect_sections(raw_text, parsed_items)
    
    def get_detected_sections(self) -> List[Dict]:
        return self._section_ctrl.get_detected_sections()
    
    def confirm_section(self, section_name: str, confirmed: bool = True):
        self._section_ctrl.confirm_section(section_name, confirmed)
    
    def rename_section(self, old_name: str, new_name: str) -> bool:
        return self._section_ctrl.rename_section(old_name, new_name)
    
    def remove_section(self, section_name: str) -> bool:
        return self._section_ctrl.remove_section(section_name)
    
    def apply_section_changes(self, changes: List[Dict]) -> bool:
        return self._section_ctrl.apply_section_changes(changes)
    
    def confirm_all_sections(self):
        self._section_ctrl.confirm_all_sections()
    
    def reject_all_sections(self):
        self._section_ctrl.reject_all_sections()
    
    def mark_item_for_removal(self, line_number: int):
        self._section_ctrl.mark_item_for_removal(line_number)
    
    def unmark_item_for_removal(self, line_number: int):
        self._section_ctrl.unmark_item_for_removal(line_number)
    
    def get_section_summary(self) -> Dict:
        return self._section_ctrl.get_section_summary()
    
    def get_section_for_item(self, line_number: int) -> str:
        return self._section_ctrl.get_section_for_item(line_number)
    
    def organize_items_by_section(self) -> Dict:
        if not self.current_parse_result:
            return {}
        return self._section_ctrl.organize_items_by_section(self.current_parse_result.items)
    
    def clear_sections(self):
        self._section_ctrl.clear()
