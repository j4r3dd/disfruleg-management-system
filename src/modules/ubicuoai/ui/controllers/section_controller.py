# -*- coding: utf-8 -*-
"""
Section Controller - Manejo de secciones del pedido
Extraído del controller principal para mejor organización
"""

import logging
from typing import List, Dict, Any, Optional

from ...business.section_manager import SectionManager

logger = logging.getLogger(__name__)


class SectionController:
    """
    Controller para manejo de secciones del pedido.
    Delega operaciones al SectionManager.
    """
    
    def __init__(self, on_status_update: callable = None):
        self.section_manager = SectionManager()
        self.sections_detected = False
        self.section_summary = None
        self.on_status_update = on_status_update or (lambda msg, lvl: None)
    
    def detect_sections(self, raw_text: str, parsed_items: list) -> List[Dict]:
        """
        Detecta secciones en el pedido procesado.
        
        Args:
            raw_text: Texto completo del pedido
            parsed_items: Items ya parseados (OrderItem objects o dicts)
            
        Returns:
            Lista de secciones detectadas
        """
        try:
            # Convertir a dict si son OrderItem objects
            items_as_dicts = []
            for item in parsed_items:
                if hasattr(item, 'line_number'):
                    items_as_dicts.append({
                        'line_number': item.line_number,
                        'producto': item.product_name,
                        'cantidad': float(item.quantity),
                        'raw_text': item.raw_text
                    })
                else:
                    items_as_dicts.append(item)
            
            sections = self.section_manager.detect_sections(raw_text, items_as_dicts)
            self.sections_detected = len(sections) > 0
            self._update_section_summary()
            
            logger.info(f"Detectadas {len(sections)} secciones")
            return sections
            
        except Exception as e:
            logger.exception(f"Error detectando secciones: {e}")
            self.sections_detected = False
            return []
    
    def get_detected_sections(self) -> List[Dict[str, Any]]:
        """Obtiene lista de secciones detectadas"""
        summary = self.section_manager.get_section_summary()
        return summary.get('sections', [])
    
    def confirm_section(self, section_name: str, confirmed: bool = True):
        """Confirma o rechaza una sección detectada"""
        self.section_manager.confirm_section(section_name, confirmed)
        
        status = "confirmada" if confirmed else "descartada"
        icon = "✓" if confirmed else "⊘"
        self.on_status_update(f"{icon} Sección {status}: {section_name}", "success" if confirmed else "info")
        
        self._update_section_summary()
    
    def rename_section(self, old_name: str, new_name: str) -> bool:
        """Renombra una sección"""
        success = self.section_manager.rename_section(old_name, new_name)
        if success:
            self.on_status_update(f"✏️ Sección renombrada: {old_name} → {new_name}", "success")
            self._update_section_summary()
        return success
    
    def remove_section(self, section_name: str) -> bool:
        """Elimina una sección completamente"""
        success = self.section_manager.remove_section(section_name)
        if success:
            self.on_status_update(f"🗑️ Sección eliminada: {section_name}", "info")
            self._update_section_summary()
        return success
    
    def apply_section_changes(self, changes: List[Dict]) -> bool:
        """
        Aplica todos los cambios de secciones de una vez.
        
        Args:
            changes: Lista de dicts con keys:
                - original_name: str
                - new_name: str  
                - confirmed: bool
                - deleted: bool
        """
        confirmed_count = 0
        renamed_count = 0
        deleted_count = 0
        
        for change in changes:
            original_name = change['original_name']
            new_name = change['new_name']
            confirmed = change['confirmed']
            deleted = change['deleted']
            
            if deleted:
                self.section_manager.remove_section(original_name)
                deleted_count += 1
            else:
                if new_name != original_name:
                    self.section_manager.rename_section(original_name, new_name)
                    renamed_count += 1
                    section_to_confirm = new_name
                else:
                    section_to_confirm = original_name
                
                self.section_manager.confirm_section(section_to_confirm, confirmed)
                if confirmed:
                    confirmed_count += 1
        
        # Mensaje de resumen
        parts = []
        if confirmed_count > 0:
            parts.append(f"{confirmed_count} confirmadas")
        if renamed_count > 0:
            parts.append(f"{renamed_count} renombradas")
        if deleted_count > 0:
            parts.append(f"{deleted_count} eliminadas")
        
        if parts:
            self.on_status_update(f"✓ Secciones: {', '.join(parts)}", "success")
        
        self._update_section_summary()
        return True
    
    def confirm_all_sections(self):
        """Confirma todas las secciones detectadas"""
        self.section_manager.confirm_all_sections()
        
        sections = self.section_manager.get_detected_sections()
        count = sum(1 for s in sections if bool(s.get("confirmed", False)))
        self.on_status_update(f"✓ {count} secciones confirmadas", "success")
        self._update_section_summary()
    
    def reject_all_sections(self):
        """Rechaza todas las secciones detectadas"""
        self.section_manager.reject_all_sections()
        
        sections = self.section_manager.get_detected_sections()
        count = len(sections)
        self.on_status_update(f"⊘ {count} secciones descartadas", "info")
        self._update_section_summary()
    
    def mark_item_for_removal(self, line_number: int):
        """Marca un item para ser eliminado del procesamiento"""
        self.section_manager.mark_for_removal(line_number)
        self.on_status_update(f"⊘ Línea {line_number} marcada para eliminar", "info")
    
    def unmark_item_for_removal(self, line_number: int):
        """Desmarca un item para eliminación"""
        self.section_manager.unmark_for_removal(line_number)
        self.on_status_update(f"✓ Línea {line_number} restaurada", "success")
    
    def get_section_summary(self) -> Dict[str, Any]:
        """Obtiene resumen del estado de secciones"""
        return self.section_manager.get_section_summary()
    
    def get_section_for_item(self, line_number: int) -> str:
        """Obtiene la sección a la que pertenece un item"""
        return self.section_manager.get_section_for_item(line_number)
    
    def organize_items_by_section(self, items: list) -> Dict[str, list]:
        """Organiza items por secciones"""
        items_as_dicts = []
        for item in items:
            if hasattr(item, 'line_number'):
                items_as_dicts.append({
                    'line_number': item.line_number,
                    'producto': item.product_name,
                    'cantidad': float(item.quantity),
                    'raw_text': item.raw_text
                })
            else:
                items_as_dicts.append(item)
        
        return self.section_manager.organize_items_by_section(items_as_dicts)
    
    def clear(self):
        """Limpia todas las secciones"""
        self.section_manager.clear()
        self.sections_detected = False
        self.section_summary = None
    
    def _update_section_summary(self):
        """Actualiza el resumen de secciones internamente"""
        self.section_summary = self.section_manager.get_section_summary()
