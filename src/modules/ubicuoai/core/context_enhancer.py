"""
Context Enhancer - Mejora rápida para mensajes sin estructura clara
Detecta cantidades implícitas y sinónimos comunes
Tiempo: < 15 minutos de integración
"""

import re
from typing import Dict, List, Tuple

class ContextEnhancer:
    """Enriquece mensajes poco estructurados con cantidad estándar"""
    
    def __init__(self):
        # Palabras clave que indican cantidad sin número
        # NOTA: El diccionario mantiene el orden de Python 3.7+
        self.implicit_quantity_map = {
            r'\b(manojo|manojos|cilantro|perejil|epazote)\b': (1, 'manojo'),
            r'\b(puñado|puñadito)\b': (0.25, 'kg'),
            r'\b(poco|poca)\b': (0.5, 'kg'),
            r'\b(bastante|harto|mucho)\b': (2, 'kg'),
            r'\b(uno|un|una)\b': (1, 'pz'),
            r'\b(dos)\b': (2, 'pz'),
            r'\b(tres)\b': (3, 'pz'),
            r'\b(cuatro)\b': (4, 'pz'),
            r'\b(cinco)\b': (5, 'pz'),
            r'\b(varios|varias)\b': (3, 'pz'),
        }
        
        # Sinónimos de productos comunes (agregar según tu BD)
        self.product_synonyms = {
            'cebolla': ['cebolla blanca', 'cebolla morada', 'cebollas'],
            'tomate': ['tomate rojo', 'jitomate', 'tomates'],
            'papa': ['papa blanca', 'papa roja', 'papas'],
            'chile': ['chile verde', 'chile rojo', 'chile jalapeño'],
            'lechuga': ['lechuga romana', 'lechuga orejona', 'lechugas'],
            'cilantro': ['cilantro fresco', 'cilantros'],
            'crema': ['crema Lala', 'crema fresca', 'crema'],
            'queso': ['queso fresco', 'queso ranchero', 'quesos'],
            'leche': ['leche', 'leche entera', 'leche descremada'],
            'huevo': ['huevos', 'huevo'],
            'pollo': ['pechuga de pollo', 'pollo entero', 'pollo'],
            'carne': ['carne molida', 'carne roja', 'carnes'],
        }
    
    def enhance_message(self, text: str) -> str:
        """
        Mejora un mensaje sin estructura clara agregando cantidades estándar
        
        Args:
            text: Mensaje original
            
        Returns:
            Mensaje mejorado con cantidad estándar agregada
            
        Ejemplo:
            "dame cilantro" → "1 manojo de cilantro"
            "necesito dos cebollas" → "2 pz de cebolla"
        """
        lines = text.strip().split('\n')
        enhanced_lines = []
        
        for line in lines:
            # Si la línea ya tiene formato estructurado, déjala como está
            if self._has_structure(line):
                enhanced_lines.append(line)
            else:
                # Intenta mejorarla
                improved = self._enhance_line(line)
                enhanced_lines.append(improved)
        
        return '\n'.join(enhanced_lines)
    
    def _has_structure(self, line: str) -> bool:
        """Detecta si la línea ya tiene formato cantidad+unidad+producto"""
        # Patrón: número + unidad + palabra
        pattern = r'\d+(?:[.,]\d+)?\s*(?:kg|gr|pz|litro|bolsa|caja|manojo)'
        return bool(re.search(pattern, line, re.IGNORECASE))
    
    def _enhance_line(self, line: str) -> str:
        """
        Mejora una línea sin estructura
        
        Proceso:
        1. Detecta cantidad implícita (uno, dos, poco, etc)
        2. Detecta producto
        3. Reformatea como: "CANTIDAD UNIDAD de PRODUCTO"
        """
        clean_line = line.strip().lstrip('*•- ')
        
        # Paso 1: Buscar cantidad implícita
        quantity, unit = self._extract_implicit_quantity(clean_line)
        
        # Paso 2: Limpiar y normalizar nombre del producto
        product_name = self._extract_product_name(clean_line)
        
        # Si no encontramos producto, devolver línea original
        if not product_name:
            return line
        
        # Paso 3: Reformatear
        if quantity and unit:
            return f"{quantity} {unit} de {product_name}"
        
        # Si no encontramos cantidad, usar default (1 kg)
        return f"1 kg de {product_name}"
    
    def _extract_implicit_quantity(self, text: str) -> Tuple[float, str]:
        """Detecta palabras como 'uno', 'dos', 'poco', etc"""
        text_lower = text.lower()
        
        for pattern, (qty, unit) in self.implicit_quantity_map.items():
            if re.search(pattern, text_lower):
                return qty, unit
        
        return None, None
    
    def _extract_product_name(self, text: str) -> str:
        """
        Extrae el nombre del producto, limpiando palabras funcionales
        """
        # Eliminar palabras funcionales
        funcional_words = [
            'dame', 'necesito', 'quiero', 'traes', 'trae', 'dame',
            'de', 'que', 'o', 'y', 'la', 'el', 'un', 'una',
            'uno', 'dos', 'tres', 'cuatro', 'cinco',
            'poco', 'mucho', 'bastante', 'varios',
            'por favor', 'porfa', 'porfis',
        ]
        
        # Remover números sueltos
        text = re.sub(r'\b\d+\b', '', text)
        
        # Remover palabras funcionales
        words = text.split()
        product_words = [w for w in words if w.lower() not in funcional_words]
        
        product_name = ' '.join(product_words).strip()
        
        # Si está vacío, devolver None
        if not product_name or len(product_name) < 2:
            return None
        
        # Normalizar: primera mayúscula
        product_name = ' '.join(w.capitalize() for w in product_name.split())
        
        return product_name
    
    def get_synonym_variants(self, product_name: str) -> List[str]:
        """
        Retorna variantes de un producto para mejorar búsqueda en BD
        
        Ejemplo: 'cebolla' retorna ['cebolla', 'cebolla blanca', 'cebolla morada']
        """
        name_lower = product_name.lower().strip()
        
        # Buscar en sinónimos
        for base, variants in self.product_synonyms.items():
            if name_lower == base.lower() or name_lower in [v.lower() for v in variants]:
                return [base] + variants
        
        # Si no está en sinónimos, retornar solo el original
        return [product_name]


# Ejemplo de uso
if __name__ == "__main__":
    enhancer = ContextEnhancer()
    
    test_messages = [
        "dame cilantro",
        "necesito dos cebollas",
        "quiero poco tomate",
        "traes varios chiles",
        "crema Lala",
        "1 kg de papa blanca",  # Ya estructurado, no se modifica
        "dame uno de queso",
    ]
    
    print("=" * 60)
    print("CONTEXT ENHANCER - MEJORA DE MENSAJES")
    print("=" * 60)
    
    for msg in test_messages:
        enhanced = enhancer.enhance_message(msg)
        print(f"\nOriginal:  {msg}")
        print(f"Mejorado:  {enhanced}")
        
        # Mostrar variantes si es necesario
        product = enhancer._extract_product_name(msg)
        if product:
            variants = enhancer.get_synonym_variants(product)
            print(f"Variantes: {variants}")