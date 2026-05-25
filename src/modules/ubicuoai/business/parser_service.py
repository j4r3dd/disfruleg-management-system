# -*- coding: utf-8 -*-
"""
Enhanced Parser Service - Business Logic Layer
Captura TODAS las líneas del pedido, incluyendo secciones y productos sin formato estándar
"""

import re
from typing import List, Optional, Tuple
from decimal import Decimal

from ..domain.models import OrderItem, OrderParseResult
from ..domain.value_objects import Unit
from ..domain.exceptions import InvalidOrderFormatError, InvalidQuantityError


class EnhancedParserService:
    """
    Parser mejorado que captura TODO el contenido del pedido:
    - Productos con formato estándar (cantidad + unidad + nombre)
    - Productos sin unidad explícita
    - Secciones de texto (ej: "COMIDA DE PERSONAL", "Baldemar piso")
    - Cualquier línea que contenga texto relevante
    """

    # Palabras clave que indican que es una sección, no un producto
    SECTION_INDICATORS = [
        'comida', 'personal', 'piso', 'preparar', 'enviar', 
        'notas', 'nota', 'comentario', 'observaciones',
        'entregar', 'entrega', 'urgente', 'importante'
    ]

    def __init__(self):
        """Initialize parser with patterns"""
        self.quantity_patterns = self._compile_patterns()

    def _compile_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for quantity detection"""
        patterns = [
            # Patrones estándar
            r'(\d+(?:[.,]\d+)?)\s*(?:kg|kgs|k|kilo|kilos)',
            r'(\d+(?:[.,]\d+)?)\s*(?:gr|g|gramos?)',
            r'(\d+(?:[.,]\d+)?)\s*(?:pz|pza|piezas?|pieza)',
            r'(\d+(?:[.,]\d+)?)\s*(?:manojo|manojos)',
            r'(\d+(?:[.,]\d+)?)\s*(?:caja|cajas)',
            r'(\d+(?:[.,]\d+)?)\s*(?:litro|litros?|lt|l)',
            r'(\d+(?:[.,]\d+)?)\s*(?:paq|paquete|paquetes)',
            r'(\d+(?:[.,]\d+)?)\s*(?:bolsa|bolsas)',
            r'(\d+(?:[.,]\d+)?)\s*(?:burbuja|burbujas)',
            
            # Patrón para "X de Y" (ej: "2 cajas de fresa")
            r'(\d+(?:[.,]\d+)?)\s+(?:caja|cajas|paq|paquete|paquetes)\s+de\s+',
        ]

        return [re.compile(p, re.IGNORECASE) for p in patterns]

    def parse_order_text(self, text: str) -> OrderParseResult:
        """
        Parse complete order text - CAPTURA TODAS LAS LÍNEAS

        Args:
            text: Order text from WhatsApp or other source

        Returns:
            OrderParseResult with all parsed items and statistics

        Raises:
            InvalidOrderFormatError: If text format is invalid
        """
        # Fail fast: Validate input
        if not text or not text.strip():
            raise InvalidOrderFormatError("Order text cannot be empty")

        lines = text.strip().split('\n')
        parsed_items: List[OrderItem] = []
        current_section = None  # Track current section

        for i, line in enumerate(lines, start=1):
            line = line.strip()

            if not line or len(line) < 2:
                continue

            # Check if this is a section header
            if self._is_section_line(line):
                current_section = line
                # Create a special item for the section
                section_item = OrderItem(
                    raw_text=line,
                    product_name=line,
                    quantity=Decimal('0'),
                    unit=Unit.SECCION,  # Special unit for sections
                    confidence=1.0,
                    line_number=i,
                    is_section=True
                )
                parsed_items.append(section_item)
                continue

            # Try to parse as a product
            try:
                item = self._parse_line(line, i)
                if item:
                    # Add section context if we're inside a section
                    if current_section:
                        item.section = current_section
                    parsed_items.append(item)
                else:
                    # Si no se pudo parsear pero tiene contenido, créalo como producto sin formato
                    uncertain_item = self._create_uncertain_item(line, i, current_section)
                    parsed_items.append(uncertain_item)
            except Exception as e:
                # Si hay cualquier error, captura la línea de todas formas
                uncertain_item = self._create_uncertain_item(line, i, current_section)
                parsed_items.append(uncertain_item)

        if not parsed_items:
            raise InvalidOrderFormatError(
                "No valid items could be parsed from the order text"
            )

        # Calculate statistics
        valid_items = [item for item in parsed_items if not item.is_section and item.quantity > 0]
        if valid_items:
            avg_confidence = sum(item.confidence for item in valid_items) / len(valid_items)
        else:
            avg_confidence = 0.0
            
        low_confidence = [item for item in parsed_items if item.confidence < 0.7 and not item.is_section]

        return OrderParseResult(
            items=parsed_items,
            total_items=len(parsed_items),
            average_confidence=round(avg_confidence, 2),
            low_confidence_items=low_confidence
        )

    def _is_section_line(self, line: str) -> bool:
        """
        Detecta si una línea es una sección (encabezado)
        
        Criterios:
        - Está en mayúsculas (más del 60% de caracteres)
        - No tiene números o tiene muy pocos
        - Contiene palabras clave de sección
        - Es relativamente corta (< 50 caracteres)
        """
        # Clean the line
        clean_line = line.strip()
        
        # Si es muy corta o muy larga, probablemente no es sección
        if len(clean_line) < 5 or len(clean_line) > 50:
            return False
            
        # Contar caracteres en mayúsculas
        alpha_chars = [c for c in clean_line if c.isalpha()]
        if not alpha_chars:
            return False
            
        uppercase_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        
        # Contar números
        digit_count = sum(1 for c in clean_line if c.isdigit())
        
        # Check for section keywords
        line_lower = clean_line.lower()
        has_section_keyword = any(keyword in line_lower for keyword in self.SECTION_INDICATORS)
        
        # Criterio 1: Mayúsculas + sin números
        if uppercase_ratio > 0.6 and digit_count == 0:
            return True
            
        # Criterio 2: Tiene keyword de sección + sin formato de cantidad
        if has_section_keyword and not self._has_quantity_pattern(clean_line):
            return True
            
        # Criterio 3: Todo en mayúsculas + pocos números
        if uppercase_ratio > 0.8 and digit_count < 2:
            return True
            
        return False

    def _has_quantity_pattern(self, text: str) -> bool:
        """Check if text has a quantity pattern"""
        for pattern in self.quantity_patterns:
            if pattern.search(text):
                return True
        return False

    def _create_uncertain_item(
        self, 
        line: str, 
        line_number: int, 
        section: Optional[str] = None
    ) -> OrderItem:
        """
        Crea un item para líneas que no pudieron ser parseadas con el formato estándar
        Estos items tendrán baja confianza y necesitarán revisión manual
        """
        # Intenta extraer un número si existe
        numbers = re.findall(r'\d+(?:[.,]\d+)?', line)
        quantity = Decimal(numbers[0].replace(',', '.')) if numbers else Decimal('1')
        
        # Limpia el nombre del producto
        product_name = line
        # Remueve números del nombre si los encontramos
        if numbers:
            for num in numbers:
                product_name = product_name.replace(num, '')
        
        product_name = self._clean_product_name(product_name)
        
        # Si después de limpiar no queda nada útil, usa el texto original
        if len(product_name) < 2:
            product_name = line
        
        item = OrderItem(
            raw_text=line,
            product_name=product_name,
            quantity=quantity,
            unit=Unit.PZ,  # Default unit
            confidence=0.3,  # Baja confianza - necesita revisión
            line_number=line_number,
            is_section=False,
            needs_review=True
        )
        
        if section:
            item.section = section
            
        return item

    def _parse_line(self, line: str, line_number: int) -> Optional[OrderItem]:
        """
        Parse a single line with standard format

        Args:
            line: Line of text to parse
            line_number: Line number for reference

        Returns:
            OrderItem or None if line cannot be parsed
        """
        # Remove leading bullets, dashes, and special characters first
        line = re.sub(r'^[-•·*⁠\s]+', '', line).strip()

        if not line:
            return None

        # Normalize text
        normalized = self._normalize_text(line)

        # Try to extract quantity and unit
        quantity_data = self._extract_quantity(normalized, line)

        if not quantity_data:
            # Try parsing without explicit unit
            return self._parse_without_unit(line, line_number)

        quantity, unit, match_start, match_end = quantity_data

        # Extract product name (text before or after the quantity pattern)
        product_name = line[:match_start].strip()

        # If product is after (e.g., "6 kg Chile serrano")
        if not product_name or len(product_name) < 2:
            product_name = line[match_end:].strip()

        # Clean product name
        product_name = self._clean_product_name(product_name)

        if not product_name or len(product_name) < 2:
            return None

        # Calculate confidence
        confidence = self._calculate_confidence(product_name, quantity, unit)

        return OrderItem(
            raw_text=line,
            product_name=product_name,
            quantity=quantity,
            unit=unit,
            confidence=confidence,
            line_number=line_number
        )

    def _extract_quantity(
        self, 
        text: str, 
        original_line: str
    ) -> Optional[Tuple[Decimal, Unit, int, int]]:
        """
        Extract quantity and unit from text
        Automatically converts grams to kilograms for consistency

        Returns:
            Tuple (quantity, unit, match_start_position, match_end_position) or None
        """
        for pattern in self.quantity_patterns:
            match = pattern.search(text)
            if match:
                quantity_str = match.group(1)
                quantity = Decimal(quantity_str.replace(',', '.'))

                # Extract unit from the match
                unit_match = match.group(0)
                unit_str = unit_match.replace(quantity_str, '').strip()

                try:
                    unit = Unit.normalize(unit_str)
                    
                    # === CONVERSIÓN AUTOMÁTICA: Gramos a Kilogramos ===
                    # Los precios están en kg, así que convertimos g a kg
                    if unit == Unit.G:
                        quantity = quantity / Decimal('1000')  # 500g -> 0.5kg
                        unit = Unit.KG
                    
                    return quantity, unit, match.start(), match.end()
                except ValueError:
                    # Unit normalization failed, try next pattern
                    continue

        return None

    def _parse_without_unit(self, line: str, line_number: int) -> Optional[OrderItem]:
        """
        Parse line without explicit unit (e.g., "Aguacate 6")
        Assumes pieces (pz) as default unit
        """
        # Look for number at end of line
        number_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*$')
        match = number_pattern.search(line)

        if match:
            quantity = Decimal(match.group(1).replace(',', '.'))
            product_name = line[:match.start()].strip()

            product_name = self._clean_product_name(product_name)

            if product_name and len(product_name) >= 2:
                return OrderItem(
                    raw_text=line,
                    product_name=product_name,
                    quantity=quantity,
                    unit=Unit.PZ,  # Default unit
                    confidence=0.6,  # Lower confidence due to missing unit
                    line_number=line_number
                )
        
        # Look for number at beginning of line (e.g., "6 aguacates")
        number_pattern_start = re.compile(r'^(\d+(?:[.,]\d+)?)\s+')
        match = number_pattern_start.search(line)
        
        if match:
            quantity = Decimal(match.group(1).replace(',', '.'))
            product_name = line[match.end():].strip()
            
            product_name = self._clean_product_name(product_name)
            
            if product_name and len(product_name) >= 2:
                return OrderItem(
                    raw_text=line,
                    product_name=product_name,
                    quantity=quantity,
                    unit=Unit.PZ,  # Default unit
                    confidence=0.5,  # Lower confidence
                    line_number=line_number
                )

        return None

    def _normalize_text(self, text: str) -> str:
        """Normalize text for parsing"""
        # Convert to lowercase
        text = text.lower()

        # Remove extra spaces
        text = ' '.join(text.split())

        # Remove accents
        text = self._remove_accents(text)

        return text

    def _remove_accents(self, text: str) -> str:
        """Remove accents from text"""
        accents = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
        for accented, unaccented in accents.items():
            text = text.replace(accented, unaccented)
        return text

    def _clean_product_name(self, name: str) -> str:
        """Clean and normalize product name"""
        # Remove leading bullets, dashes, and special characters
        name = re.sub(r'^[-•·*⁠\s]+', '', name)

        # Remove trailing special characters
        name = re.sub(r'[-•·*⁠\s]+$', '', name)

        # Remove numbers and unit residuals
        name = re.sub(r'\d+(?:[.,]\d+)?', '', name)
        name = re.sub(
            r'\b(?:kg|kgs|kilo|kilos|gr|gramos?|gramo|pz|pza|pzas|pieza|piezas|manojo|manojos|caja|cajas|litro|litros|lt|bolsa|bolsas|paquete|paquetes|burbuja|burbujas)\b\s*',
            '',
            name,
            flags=re.IGNORECASE
        )

        # Remove "de" preposition that often appears after quantities
        name = re.sub(r'\bde\b', '', name, flags=re.IGNORECASE)

        # Clean spaces
        name = ' '.join(name.split())

        # Capitalize first letter of each word
        name = ' '.join(word.capitalize() for word in name.split())

        return name.strip()

    def _calculate_confidence(
        self,
        product_name: str,
        quantity: Decimal,
        unit: Unit
    ) -> float:
        """
        Calculate parsing confidence

        Returns:
            Float between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence

        # +0.2 if product name is reasonable length
        if len(product_name) >= 3:
            confidence += 0.2

        # +0.2 if quantity is reasonable
        if Decimal('0') < quantity < Decimal('10000'):
            confidence += 0.2

        # +0.1 if unit is standard
        if unit in [Unit.KG, Unit.G, Unit.PZ, Unit.LT]:
            confidence += 0.1

        return min(confidence, 1.0)
