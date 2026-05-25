# -*- coding: utf-8 -*-
"""
window_event_handlers.py - Manejadores de eventos de usuario
Selección de grupo, cliente y procesamiento de pedidos
"""

import logging

logger = logging.getLogger(__name__)


class WindowEventHandlers:
    """Maneja los eventos de usuario en la ventana"""

    def on_group_selected(self, selected_value: str):
        """Evento: Se selecciona un grupo de clientes"""
        try:
            if selected_value in ["-- Seleccionar Grupo --", ""]:
                self.client_selector.set("-- Primero selecciona un grupo --")
                self.client_selector.configure(state="disabled")
                self.client_info_label.configure(text="")
                
                if self.controller and hasattr(self.controller, 'select_client'):
                    self.controller.select_client(None)
            else:
                # Obtener clientes del grupo
                clients_in_group = self.groups_dict.get(selected_value, [])
                
                # Construir opciones de cliente
                client_options = ["-- Seleccionar Cliente --"]
                self.clients_by_group = {}
                
                for client in clients_in_group:
                    label = client['nombre_cliente']
                    client_options.append(label)
                    self.clients_by_group[label] = client
                
                # Actualizar selector de cliente
                self.client_selector.configure(
                    values=client_options,
                    state="readonly"
                )
                self.client_selector.set("-- Seleccionar Cliente --")
                self.client_info_label.configure(text="")
                
                logger.info(f"✓ Grupo seleccionado: {selected_value} ({len(clients_in_group)} clientes)")
        except Exception as e:
            logger.error(f"Error en on_group_selected: {e}")

    def on_client_selected(self, selected_value: str):
        """Evento: Se selecciona un cliente"""
        try:
            if selected_value in ["-- Seleccionar Cliente --", "-- Primero selecciona un grupo --"]:
                if self.controller and hasattr(self.controller, 'select_client'):
                    self.controller.select_client(None)
                self.client_info_label.configure(text="")
                # Refrescar precios si hay resultados
                self._refresh_prices_after_client_change()
            else:
                # Obtener datos del cliente
                client = self.clients_by_group.get(selected_value)
                
                if client and self.controller and hasattr(self.controller, 'select_client'):
                    if self.controller.select_client(client['id_cliente']):
                        # Mostrar info del cliente
                        discount = float(client.get('descuento', 0))
                        info = f"Grupo: {client['clave_grupo']} | {client['nombre_tipo']}"
                        if discount > 0:
                            info += f" | -{discount}%"
                        
                        self.client_info_label.configure(text=info)
                        logger.info(f"✓ Cliente seleccionado: {client['nombre_cliente']}")
                        
                        # Refrescar precios automáticamente
                        self._refresh_prices_after_client_change()
        except Exception as e:
            logger.error(f"Error en on_client_selected: {e}")

    def _refresh_prices_after_client_change(self):
        """Refresca los precios mostrados cuando cambia el cliente"""
        try:
            if not self.controller:
                return
            
            # Verificar si hay resultados para actualizar
            if not hasattr(self.controller, 'current_parse_result') or not self.controller.current_parse_result:
                return
            
            if not self.controller.current_parse_result.items:
                return
            
            logger.info("🔄 Refrescando precios para nuevo cliente/grupo...")
            
            # Recalcular matches con nuevos precios del grupo
            if hasattr(self.controller, 'refresh_prices_for_current_results'):
                success = self.controller.refresh_prices_for_current_results()
                if success:
                    # Refrescar la vista
                    if hasattr(self, 'display_results'):
                        self.display_results()
                    logger.info("✓ Precios actualizados correctamente")
            else:
                # Fallback: solo refrescar display (sin recalcular)
                if hasattr(self, 'display_results'):
                    self.display_results()
                logger.warning("⚠️ refresh_prices_for_current_results no disponible")
        except Exception as e:
            logger.error(f"Error refrescando precios: {e}")

    def process_order(self):
        """Evento: Se presiona botón de procesar pedido"""
        try:
            # Obtener texto del pedido
            text = self.text_area.get("1.0", "end-1c").strip()
            
            # Validar entrada
            if not text or text.startswith("📝 Pega"):
                self.update_status("⚠️ Por favor, pega un pedido primero", "warning")
                return
            
            logger.info(f"🔍 Procesando pedido ({len(text)} caracteres)...")
            
            # Limpiar overrides anteriores
            self.manual_overrides.clear()
            logger.info("🔄 Manual overrides limpiados")
            
            # Validar controller
            if not self.controller or not hasattr(self.controller, 'process_order'):
                self.update_status("❌ Controller no disponible", "error")
                logger.error("Controller no tiene método process_order")
                return
            
            # Procesar
            self.update_status("⏳ Procesando...", "info")
            self.update()
            
            result = self.controller.process_order(text)
            
            if result:
                logger.info("✅ Pedido procesado exitosamente")
                self.display_results()
                
                # Actualizar botón de secciones y mostrar diálogo si hay
                self._update_sections_button()
                sections = self.controller.get_detected_sections()
                if sections:
                    self.after(500, self.show_section_management)
                
                self.update_status("✅ Pedido procesado correctamente", "success")
            else:
                logger.error("❌ Error al procesar pedido")
                self.update_status("❌ Error al procesar el pedido", "error")
                
        except Exception as e:
            logger.error(f"❌ Error en process_order: {e}")
            import traceback
            traceback.print_exc()
            self.update_status(f"❌ Error: {str(e)}", "error")
