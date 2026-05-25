# -*- coding: utf-8 -*-
"""
window_dialog_handlers.py - Maneja los diálogos de secciones y eliminación
Muestra diálogos para confirmar secciones y marcar items para eliminar
"""

import logging

from .section_dialogs import SectionManagementDialog, RemovalDialog
from .custom_dialogs import show_info, show_error

logger = logging.getLogger(__name__)


class WindowDialogHandlers:
    """Maneja los diálogos de usuario (secciones, eliminación, etc)"""

    def show_section_management(self):
        """Muestra el diálogo de gestión de secciones"""
        try:
            # Obtener secciones detectadas
            sections = self.controller.get_detected_sections()
            
            if not sections:
                show_info(
                    self,
                    "Sin Secciones",
                    "No se detectaron secciones en este pedido.\n\n"
                    "Las secciones son líneas en MAYÚSCULAS sin números que "
                    "organizan el pedido (ej: COCINA, BARRA, COMIDA PERSONAL)."
                )
                return
            
            logger.info(f"📁 Abriendo diálogo de {len(sections)} secciones")
            
            # Crear y mostrar diálogo con todos los callbacks
            dialog = SectionManagementDialog(
                parent=self,
                sections=sections,
                on_confirm=self._on_section_confirm,
                on_rename=self._on_section_rename,
                on_remove=self._on_section_remove,
                on_close=self._on_section_dialog_close,
                on_apply_all=self._on_apply_all_section_changes
            )
            
            # Esperar a que se cierre
            self.wait_window(dialog)
            
            # Refrescar después de cerrar
            self.display_results()
            self._update_sections_button()
            
        except Exception as e:
            logger.error(f"Error mostrando diálogo de secciones: {e}")
            import traceback
            traceback.print_exc()
            show_error(
                self,
                "Error",
                f"No se pudo mostrar el diálogo de secciones:\n{str(e)}"
            )

    def show_removal_dialog(self):
        """Muestra el diálogo para marcar items para eliminación"""
        try:
            # Obtener items que necesitan revisión
            stats = self.controller.current_statistics
            items_to_review = stats.get('needs_review', [])
            
            if not items_to_review:
                show_info(
                    self,
                    "Sin Items para Revisar",
                    "Todos los items fueron procesados correctamente.\n\n"
                    "No hay líneas que necesiten revisión."
                )
                return
            
            logger.info(f"🗑️ Abriendo diálogo para {len(items_to_review)} items")
            
            # Crear y mostrar diálogo
            dialog = RemovalDialog(
                parent=self,
                items_to_review=items_to_review,
                on_mark_removal=self._on_mark_removal,
                on_close=self._on_removal_dialog_close
            )
            
            # Esperar a que se cierre
            self.wait_window(dialog)
            
            # Refrescar después de cerrar
            self.display_results()
            self._update_sections_button()
            
        except Exception as e:
            logger.error(f"Error mostrando diálogo de eliminación: {e}")
            import traceback
            traceback.print_exc()
            show_error(
                self,
                "Error",
                f"No se pudo mostrar el diálogo de eliminación:\n{str(e)}"
            )

    def _on_section_confirm(self, section_name: str, confirmed: bool):
        """Callback: Usuario confirma o rechaza una sección individual"""
        try:
            self.controller.confirm_section(section_name, confirmed)
            status = "Confirmada" if confirmed else "Rechazada"
            logger.info(f"✓ Sección '{section_name}': {status}")
        except Exception as e:
            logger.error(f"Error confirmando sección: {e}")

    def _on_section_rename(self, old_name: str, new_name: str):
        """Callback: Usuario renombra una sección"""
        try:
            self.controller.rename_section(old_name, new_name)
            logger.info(f"✏️ Sección renombrada: {old_name} → {new_name}")
        except Exception as e:
            logger.error(f"Error renombrando sección: {e}")

    def _on_section_remove(self, section_name: str):
        """Callback: Usuario elimina una sección"""
        try:
            self.controller.remove_section(section_name)
            logger.info(f"✗ Sección eliminada: {section_name}")
        except Exception as e:
            logger.error(f"Error eliminando sección: {e}")

    def _on_apply_all_section_changes(self, changes: list):
        """Callback: Aplica todos los cambios de secciones de una vez"""
        try:
            self.controller.apply_section_changes(changes)
            logger.info(f"💾 Aplicados {len(changes)} cambios de secciones")
        except Exception as e:
            logger.error(f"Error aplicando cambios de secciones: {e}")

    def _on_confirm_all_sections(self):
        """Callback: Usuario confirma todas las secciones"""
        try:
            self.controller.confirm_all_sections()
            logger.info("✓ Todas las secciones confirmadas")
        except Exception as e:
            logger.error(f"Error confirmando todas las secciones: {e}")

    def _on_reject_all_sections(self):
        """Callback: Usuario rechaza todas las secciones"""
        try:
            self.controller.reject_all_sections()
            logger.info("✓ Todas las secciones rechazadas")
        except Exception as e:
            logger.error(f"Error rechazando todas las secciones: {e}")

    def _on_section_dialog_close(self):
        """Callback: Se cierra el diálogo de secciones"""
        logger.info("📁 Diálogo de secciones cerrado")

    def _on_mark_removal(self, line_number: int, mark: bool = True):
        """Callback: Usuario marca o desmarca item para eliminación"""
        try:
            if mark:
                self.controller.mark_item_for_removal(line_number)
                logger.info(f"✓ Línea {line_number} marcada para remoción")
            else:
                self.controller.unmark_item_for_removal(line_number)
                logger.info(f"✓ Línea {line_number} desmarcada")
        except Exception as e:
            logger.error(f"Error marcando remoción: {e}")

    def _on_removal_dialog_close(self):
        """Callback: Se cierra el diálogo de remoción"""
        logger.info("🗑️ Diálogo de remoción cerrado")

    def _update_sections_button(self):
        """Actualiza el estado y texto del botón de secciones"""
        try:
            summary = self.controller.get_section_summary()
            total = summary.get('total_detected', 0)
            confirmed = summary.get('confirmed', 0)
            removed = summary.get('removed', 0)

            if total > 0:
                self.sections_btn.configure(
                    state="normal",
                    text=f"📁 Secciones ({confirmed}/{total})"
                )
                logger.debug(f"Botón actualizado: {confirmed}/{total} confirmadas")
            else:
                self.sections_btn.configure(
                    state="disabled",
                    text="📁 Secciones"
                )
            
            if removed > 0:
                logger.info(f"⚠️ {removed} items marcados para remoción")
            
        except Exception as e:
            logger.error(f"Error actualizando botón de secciones: {e}")
