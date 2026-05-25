"""
Ubicuo AI - Parser Inteligente (COMPLETO Y CORREGIDO)
Versión mejorada con corrección del problema de la letra L
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import yaml


@dataclass
class ParsedItem:
    """Representa un producto parseado del texto"""
    raw_text: str
    product_name: str
    quantity: float
    unit: str
    confidence: float
    line_number: int
    
    def to_dict(self) -> dict:
        return {
            'raw_text': self.raw_text,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'confidence': self.confidence,
            'line_number': self.line_number
        }


class UbicuoParser:
    """Parser inteligente MEJORADO de pedidos de WhatsApp"""
    
    def __init__(self, config_path: str = "config/configuracion.yaml"):
        self.config = self._load_config(config_path)
        self.quantity_patterns = self._compile_patterns()
        self.unit_map = self._create_unit_map()
        self.current_header = None
        
    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {
                'parser': {
                    'options': {
                        'case_sensitive': False,
                        'strip_accents': True,
                        'remove_extra_spaces': True
                    },
                    'unit_normalization': {
                        'kg': ['kg', 'kgs', 'k', 'kilo', 'kilos'],
                        'gr': ['gr', 'g', 'gramos', 'gramo'],
                        'pz': ['pz', 'pza', 'pieza', 'piezas', 'pzas'],
                        'manojo': ['manojo', 'manojos'],
                        'caja': ['caja', 'cajas'],
                        'litro': ['litro', 'litros', 'lt', 'l'],
                        'bolsa': ['bolsa', 'bolsas'],
                        'paquete': ['paquete', 'paquetes']
                    }
                }
            }
    
    def _compile_patterns(self) -> List[Dict[str, any]]:
        patterns = [
            {
                'regex': re.compile(r'^\*?(\d+(?:[.,]\d+)?)\s*(kg|kgs|k|kilo|kilos|gr|g|gramos?|pz|pza|pzas|piezas?|manojo|manojos|caja|cajas|litro|litros?|lt|l|bolsas?|paquetes?)\s+(?:de\s+)?(.+)', re.IGNORECASE),
                'type': 'inicio_con_de',
                'priority': 1,
                'groups': {'quantity': 1, 'unit': 2, 'product': 3}
            },
            {
                'regex': re.compile(r'(.+?)\s+(\d+(?:[.,]\d+)?)\s*(kg|kgs|k|kilo|kilos|gr|g|gramos?|pz|pza|pzas|piezas?|manojo|manojos|caja|cajas|litro|litros?|lt|l|bolsas?|paquetes?)$', re.IGNORECASE),
                'type': 'final',
                'priority': 2,
                'groups': {'product': 1, 'quantity': 2, 'unit': 3}
            },
            {
                'regex': re.compile(r'(\d+)/(\d+)\s+(?:de\s+)?(.+)', re.IGNORECASE),
                'type': 'fraccion',
                'priority': 1,
                'groups': {'numerator': 1, 'denominator': 2, 'product': 3}
            },
            {
                'regex': re.compile(r'(.+?)\s+(\d+(?:[.,]\d+)?)$'),
                'type': 'numero_solo',
                'priority': 3,
                'groups': {'product': 1, 'quantity': 2}
            }
        ]
        return sorted(patterns, key=lambda x: x['priority'])
    
    def _create_unit_map(self) -> Dict[str, str]:
        unit_norm = self.config.get('parser', {}).get('unit_normalization', {})
        unit_map = {}
        for normalized, variants in unit_norm.items():
            for variant in variants:
                unit_map[variant.lower()] = normalized
        return unit_map
    
    def parse_text(self, text: str) -> List[ParsedItem]:
        lines = text.strip().split('\n')
        parsed_items = []
        self.current_header = None
        
        for i, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue
            
            if self._is_header(line):
                self.current_header = self._clean_header(line)
                continue
            
            item = self._parse_line(line, i)
            if item:
                parsed_items.append(item)
        
        return parsed_items
    
    def _is_header(self, line: str) -> bool:
        if len(line) > 30:
            return False
        if line.endswith(':'):
            return True
        if line.isupper() and not any(c.isdigit() for c in line):
            return True
        header_keywords = ['comida', 'personal', 'pedido', 'orden', 'cliente']
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in header_keywords):
            return True
        return False
    
    def _clean_header(self, header: str) -> str:
        header = header.strip()
        if header.endswith(':'):
            header = header[:-1].strip()
        return header
    
    def _parse_line(self, line: str, line_number: int) -> Optional[ParsedItem]:
        clean_line = line.lstrip('*• -')
        
        for pattern_info in self.quantity_patterns:
            result = self._try_pattern(clean_line, line, line_number, pattern_info)
            if result:
                return result
        
        return None
    
    def _try_pattern(self, clean_line: str, original_line: str, line_number: int, 
                    pattern_info: Dict) -> Optional[ParsedItem]:
        
        match = pattern_info['regex'].search(clean_line)
        if not match:
            return None
        
        pattern_type = pattern_info['type']
        groups = pattern_info['groups']
        
        if pattern_type == 'fraccion':
            numerator = int(match.group(groups['numerator']))
            denominator = int(match.group(groups['denominator']))
            quantity = numerator / denominator
            product_name = match.group(groups['product']).strip()
            unit = 'kg'  # Default: kilogramo
            confidence = 0.85
            
        elif pattern_type == 'numero_solo':
            product_name = match.group(groups['product']).strip()
            quantity_str = match.group(groups['quantity'])
            quantity = float(quantity_str.replace(',', '.'))
            unit = 'kg'  # Default: kilogramo
            confidence = 0.7
            
        else:
            product_name = match.group(groups['product']).strip()
            quantity_str = match.group(groups['quantity'])
            quantity = float(quantity_str.replace(',', '.'))
            unit_raw = match.group(groups['unit']).strip()
            unit = self.unit_map.get(unit_raw.lower(), unit_raw.lower())
            confidence = 0.9
        
        product_name = self._clean_product_name(product_name)
        
        if not product_name or len(product_name) < 2:
            return None
        
        confidence = self._calculate_confidence(product_name, quantity, unit, confidence)
        
        return ParsedItem(
            raw_text=original_line,
            product_name=product_name,
            quantity=quantity,
            unit=unit,
            confidence=confidence,
            line_number=line_number
        )
    
    def _clean_product_name(self, name: str) -> str:
        """CORREGIDO: Limpieza más cuidadosa para no eliminar letras válidas"""
        # Eliminar "de" al inicio si existe
        name = re.sub(r'^de\s+', '', name, flags=re.IGNORECASE)
        
        # Eliminar números
        name = re.sub(r'\b\d+(?:[.,]\d+)?\b', '', name)
        
        # Eliminar unidades SOLO como palabras completas, no letras dentro de palabras
        # El \b asegura que solo se eliminen unidades completas, no letras como "l" en "Lala"
        name = re.sub(r'\b(?:kg|kgs|kilo|kilos|gr|gramos?|gramo|pz|pza|pzas|pieza|piezas|manojo|manojos|caja|cajas|litro|litros|lt|bolsa|bolsas|paquete|paquetes)\b\s*', '', name, flags=re.IGNORECASE)
        
        # Limpiar espacios múltiples
        name = ' '.join(name.split())
        
        # Capitalizar primera letra de cada palabra
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name.strip()
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza el texto según configuración"""
        options = self.config.get('parser', {}).get('options', {})
        
        if not options.get('case_sensitive', False):
            text = text.lower()
        
        if options.get('remove_extra_spaces', True):
            text = ' '.join(text.split())
        
        if options.get('strip_accents', True):
            text = self._remove_accents(text)
        
        return text
    
    def _remove_accents(self, text: str) -> str:
        """Elimina acentos del texto"""
        accents = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
        for accented, unaccented in accents.items():
            text = text.replace(accented, unaccented)
        return text
    
    def _extract_quantity(self, text: str) -> Optional[Tuple[float, str, int]]:
        """
        Extrae cantidad y unidad del texto (MÉTODO DE COMPATIBILIDAD)
        """
        for pattern_info in self.quantity_patterns:
            match = pattern_info['regex'].search(text)
            if match:
                groups = pattern_info['groups']
                if pattern_info['type'] == 'fraccion':
                    quantity = int(match.group(groups['numerator'])) / int(match.group(groups['denominator']))
                    unit = 'kg'  # Default: kilogramo
                else:
                    quantity_str = match.group(groups['quantity'])
                    quantity = float(quantity_str.replace(',', '.'))
                    unit = match.group(groups['unit']).strip() if 'unit' in groups else 'kg'  # Default: kilogramo
                    unit = self.unit_map.get(unit.lower(), unit.lower())
                return quantity, unit, match.start()
        return None
    
    def _parse_without_unit(self, line: str, line_number: int) -> Optional[ParsedItem]:
        """
        Intenta parsear líneas sin unidad explícita (MÉTODO DE COMPATIBILIDAD)
        """
        number_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*$')
        match = number_pattern.search(line)
        
        if match:
            quantity = float(match.group(1).replace(',', '.'))
            product_name = line[:match.start()].strip()
            
            if product_name:
                return ParsedItem(
                    raw_text=line,
                    product_name=product_name,
                    quantity=quantity,
                    unit='kg',  # Default: kilogramo
                    confidence=0.6,
                    line_number=line_number
                )
        
        return None
    
    def _calculate_confidence(self, product_name: str, quantity: float, 
                             unit: str, base_confidence: float = 0.5) -> float:
        confidence = base_confidence
        
        if len(product_name) >= 3:
            confidence += 0.2
        
        if 0 < quantity < 10000:
            confidence += 0.2
        
        if unit in self.unit_map.values():
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_statistics(self, parsed_items: List[ParsedItem]) -> dict:
        if not parsed_items:
            return {
                'total_items': 0,
                'avg_confidence': 0.0,
                'units_distribution': {},
                'low_confidence_items': []
            }
        
        units_dist = {}
        low_conf = []
        
        for item in parsed_items:
            units_dist[item.unit] = units_dist.get(item.unit, 0) + 1
            if item.confidence < 0.7:
                low_conf.append(item.to_dict())
        
        avg_conf = sum(item.confidence for item in parsed_items) / len(parsed_items)
        
        return {
            'total_items': len(parsed_items),
            'avg_confidence': round(avg_conf, 2),
            'units_distribution': units_dist,
            'low_confidence_items': low_conf
        }


if __name__ == "__main__":
    sample_text = """
HABANERO:
6 kg de cebolla blanca
1 manojos de cilantro
4 kg de papa blanca
3 kg de aguacate
2 kg de chile Perón
2 pz de piña
6 kg de pepino
6 kg de limón

COMIDA PERSONAL
1 kg de Maseca
1 pz de lechuga
1/2 de crema Lala
1/4 de queso ranchero
2 bolsas de frijoles refritos(Isadora)
1/2 pechuga de pollo entera
"""
    
    parser = UbicuoParser()
    results = parser.parse_text(sample_text)
    
    print("=" * 60)
    print("UBICUO AI - PARSER COMPLETO Y CORREGIDO")
    print("=" * 60)
    
    for item in results:
        print(f"\n[Línea {item.line_number}] {item.raw_text}")
        print(f"  → Producto: {item.product_name}")
        print(f"  → Cantidad: {item.quantity} {item.unit}")
        print(f"  → Confianza: {item.confidence:.1%}")
    
    stats = parser.get_statistics(results)
    print(f"\n{'=' * 60}")
    print("ESTADÍSTICAS")
    print(f"{'=' * 60}")
    print(f"Total items: {stats['total_items']}")
    print(f"Confianza promedio: {stats['avg_confidence']:.1%}")
    print(f"Distribución de unidades: {stats['units_distribution']}")