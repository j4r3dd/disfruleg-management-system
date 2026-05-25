"""
📁 Section Manager - Gestión de Secciones para UbicuoAI
Detecta, gestiona y organiza secciones en pedidos de WhatsApp
"""

import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Section:
    """Representa una sección detectada en el pedido"""
    name: str
    line_number: int
    confirmed: bool = False
    items: List[Dict[str, Any]] = field(default_factory=list)
    marked_for_removal: bool = False
    
    @property
    def item_count(self) -> int:
        """Retorna el número de items en esta sección"""
        return len(self.items)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la sección a diccionario"""
        return {
            'name': self.name,
            'line': self.line_number,
            'confirmed': bool(self.confirmed),
            'item_count': self.item_count,
            'marked_for_removal': self.marked_for_removal
        }


class SectionManager:
    """
    Gestiona la detección y organización de secciones en pedidos.
    
    Detecta automáticamente secciones basándose en:
    - Líneas en MAYÚSCULAS sin números
    - Palabras clave (comida, personal, piso, barra, cocina, etc.)
    - Formato de encabezado
    """
    
    # Palabras clave que indican posibles secciones
    SECTION_KEYWORDS = [
        'comida', 'personal', 'piso', 'barra', 'cocina', 'postres',
        'guardia', 'nacional', 'entregar', 'llevar', 'delivery'
    ]
    
    # Palabras que NO son secciones (información extra)
    EXCLUSION_KEYWORDS = [
        'entregar', 'llevar', 'llamar', 'avisar', 'nota', 'observación',
        'viernes', 'lunes', 'martes', 'miércoles', 'jueves', 'sábado', 'domingo'
    ]
    
    def __init__(self):
        self.sections: List[Section] = []
        self.current_section: Optional[str] = "GENERAL"
        self._line_to_section: Dict[int, str] = {}
    
    def detect_sections(self, raw_text: str, parsed_items: List[Dict[str, Any]]) -> List[Section]:
        """
        Detecta secciones en el texto raw del pedido.
        
        Args:
            raw_text: Texto completo del pedido
            parsed_items: Items ya parseados con números de línea
            
        Returns:
            Lista de secciones detectadas
        """
        self.sections = []
        self._line_to_section = {}
        
        lines = raw_text.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            # Verificar si es una sección potencial
            if self._is_potential_section(line_stripped):
                section_name = line_stripped.upper()
                
                # Contar items que pertenecen a esta sección
                section_items = self._get_items_for_section(
                    line_num, parsed_items, lines
                )
                
                if section_items:  # Solo agregar si tiene items
                    section = Section(
                        name=section_name,
                        line_number=line_num,
                        items=section_items
                    )
                    self.sections.append(section)
                    
                    # Mapear línea a sección
                    self._line_to_section[line_num] = section_name
        
        return self.sections
    
    def _is_potential_section(self, line: str) -> bool:
        """
        Determina si una línea es potencialmente una sección.
        
        Criterios:
        1. Está en mayúsculas o tiene palabra clave
        2. NO contiene números (precios, cantidades)
        3. NO está en la lista de exclusión
        4. Tiene más de 3 caracteres
        """
        # Muy corta
        if len(line) < 3:
            return False
        
        # Contiene números (probablemente es un item)
        if re.search(r'\d', line):
            return False
        
        # Está en lista de exclusión
        line_lower = line.lower()
        if any(excl in line_lower for excl in self.EXCLUSION_KEYWORDS):
            return False
        
        # Está completamente en mayúsculas
        if line.isupper() and len(line.split()) <= 4:
            return True
        
        # Contiene palabra clave
        if any(keyword in line_lower for keyword in self.SECTION_KEYWORDS):
            return True
        
        return False
    
    def _get_items_for_section(
        self, 
        section_line: int, 
        parsed_items: List[Dict[str, Any]],
        all_lines: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Obtiene los items que pertenecen a una sección específica.
        
        Los items pertenecen a una sección si:
        - Están después de la línea de la sección
        - Están antes de la siguiente sección o del final
        """
        section_items = []
        
        # Encontrar la siguiente sección
        next_section_line = None
        for line_num in range(section_line + 1, len(all_lines) + 1):
            if line_num == len(all_lines) + 1:
                next_section_line = line_num
                break
            
            line = all_lines[line_num - 1].strip()
            if self._is_potential_section(line):
                next_section_line = line_num
                break
        
        if next_section_line is None:
            next_section_line = len(all_lines) + 1
        
        # Filtrar items en el rango
        for item in parsed_items:
            item_line = item.get('line_number', 0)
            if section_line < item_line < next_section_line:
                section_items.append(item)
        
        return section_items
    
    def get_detected_sections(self) -> List[Dict[str, Any]]:
        """
        Retorna las secciones detectadas en formato dict.
        
        Returns:
            Lista de diccionarios con información de secciones
        """
        return [section.to_dict() for section in self.sections]
    
    def confirm_section(self, section_name: str, confirmed: bool = True) -> bool:
        """
        Confirma o rechaza una sección.
        
        Args:
            section_name: Nombre de la sección
            confirmed: True para confirmar, False para rechazar
            
        Returns:
            True si se encontró y actualizó la sección
        """
        for section in self.sections:
            if section.name == section_name:
                section.confirmed = confirmed
                return True
        return False
    
    def rename_section(self, old_name: str, new_name: str) -> bool:
        """
        Renombra una sección.
        
        Args:
            old_name: Nombre actual de la sección
            new_name: Nuevo nombre para la sección
            
        Returns:
            True si se encontró y renombró la sección
        """
        for section in self.sections:
            if section.name == old_name:
                section.name = new_name.upper().strip()
                # Actualizar el mapeo de línea a sección
                if section.line_number in self._line_to_section:
                    self._line_to_section[section.line_number] = section.name
                return True
        return False
    
    def remove_section(self, section_name: str) -> bool:
        """
        Elimina una sección de la lista.
        
        Args:
            section_name: Nombre de la sección a eliminar
            
        Returns:
            True si se encontró y eliminó la sección
        """
        for i, section in enumerate(self.sections):
            if section.name == section_name:
                # Eliminar del mapeo
                if section.line_number in self._line_to_section:
                    del self._line_to_section[section.line_number]
                # Eliminar de la lista
                self.sections.pop(i)
                return True
        return False
    
    def confirm_all_sections(self):
        """Confirma todas las secciones detectadas"""
        for section in self.sections:
            section.confirmed = True
    
    def reject_all_sections(self):
        """Rechaza todas las secciones detectadas"""
        for section in self.sections:
            section.confirmed = False
    
    def mark_line_for_removal(self, line_number: int) -> bool:
        """
        Marca una línea para ser eliminada del procesamiento.
        
        Args:
            line_number: Número de línea a marcar
            
        Returns:
            True si se marcó correctamente
        """
        for section in self.sections:
            if section.line_number == line_number:
                section.marked_for_removal = True
                return True
        return False
    
    def get_section_for_item(self, line_number: int) -> str:
        """
        Obtiene la sección a la que pertenece un item por su línea.
        
        Args:
            line_number: Número de línea del item
            
        Returns:
            Nombre de la sección o "GENERAL" si no pertenece a ninguna
        """
        # Buscar en qué sección está el item
        for section in self.sections:
            if not section.confirmed:
                continue
            
            # Verificar si el item está en los items de esta sección
            for item in section.items:
                if item.get('line_number') == line_number:
                    return section.name
        
        return "GENERAL"
    
    def get_section_summary(self) -> Dict[str, Any]:
        """
        Genera un resumen del estado de las secciones.
        
        Returns:
            Diccionario con estadísticas de secciones
        """
        total = len(self.sections)
        confirmed = sum(1 for s in self.sections if s.confirmed)
        unconfirmed = total - confirmed
        marked_removal = sum(1 for s in self.sections if s.marked_for_removal)
        
        total_items = sum(s.item_count for s in self.sections if s.confirmed)
        
        return {
            'total_detected': total,
            'confirmed': confirmed,
            'unconfirmed': unconfirmed,
            'marked_for_removal': marked_removal,
            'total_items_in_sections': total_items,
            'sections': self.get_detected_sections()
        }
    
    def organize_items_by_section(
        self, 
        parsed_items: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organiza los items parseados por sus secciones confirmadas.
        
        Args:
            parsed_items: Lista de items parseados
            
        Returns:
            Diccionario con secciones como keys y sus items como values
        """
        organized = {}
        
        # Inicializar secciones confirmadas
        for section in self.sections:
            if section.confirmed:
                organized[section.name] = []
        
        # Siempre incluir GENERAL
        if "GENERAL" not in organized:
            organized["GENERAL"] = []
        
        # Asignar items a secciones
        for item in parsed_items:
            section_name = self.get_section_for_item(item.get('line_number', 0))
            
            if section_name in organized:
                organized[section_name].append(item)
            else:
                organized["GENERAL"].append(item)
        
        # Eliminar secciones vacías excepto GENERAL
        organized = {
            k: v for k, v in organized.items() 
            if v or k == "GENERAL"
        }
        
        return organized
    
    def clear(self):
        """Limpia todas las secciones"""
        self.sections = []
        self.current_section = "GENERAL"
        self._line_to_section = {}
    
    def __repr__(self) -> str:
        return f"<SectionManager: {len(self.sections)} sections detected>"


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de texto de pedido
    sample_text = """BALDEMAR
3 kg pimiento rojo
3 kg pimiento amarillo
5 kg de calabazas

COMIDA DE PERSONAL
15 paq de espaguetis
2 pechugas de pollo

Baldemar piso
5 kg limon
"""
    
    # Items parseados (simulados)
    sample_items = [
        {'line_number': 2, 'producto': 'pimiento rojo', 'cantidad': 3},
        {'line_number': 3, 'producto': 'pimiento amarillo', 'cantidad': 3},
        {'line_number': 4, 'producto': 'calabazas', 'cantidad': 5},
        {'line_number': 7, 'producto': 'espaguetis', 'cantidad': 15},
        {'line_number': 8, 'producto': 'pechugas pollo', 'cantidad': 2},
        {'line_number': 11, 'producto': 'limon', 'cantidad': 5},
    ]
    
    # Crear manager y detectar
    manager = SectionManager()
    sections = manager.detect_sections(sample_text, sample_items)
    
    print("🔍 Secciones Detectadas:")
    for section in sections:
        print(f"  📁 {section.name} (Línea {section.line_number})")
        print(f"     Items: {section.item_count}")
        print()
    
    # Confirmar todas
    manager.confirm_all_sections()
    
    # Organizar items
    organized = manager.organize_items_by_section(sample_items)
    
    print("📦 Items Organizados:")
    for section_name, items in organized.items():
        print(f"\n📁 {section_name}:")
        for item in items:
            print(f"  - {item['producto']}: {item['cantidad']}")
    
    # Resumen
    summary = manager.get_section_summary()
    print(f"\n📊 Resumen:")
    print(f"  Total detectadas: {summary['total_detected']}")
    print(f"  Confirmadas: {summary['confirmed']}")
    print(f"  Items en secciones: {summary['total_items_in_sections']}")