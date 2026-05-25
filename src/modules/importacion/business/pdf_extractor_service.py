# -*- coding: utf-8 -*-
"""
PDF Extractor Service - Business Logic (MEJORADO)
Handles extraction of products from PDF files
Soporta múltiples formatos de PDFs
NO direct database access - pure business logic!

✅ VERSIÓN MEJORADA - 29 Nov 2025
Características:
- Detección automática de formato PDF
- Soporte para 3+ formatos diferentes
- Normalización de unidades expandida
- Manejo robusto de caracteres especiales
- Validación exhaustiva de datos
"""

from typing import List, Tuple
from decimal import Decimal
import re
from pathlib import Path
import fitz  # PyMuPDF

from ..domain.models import ExtractedProduct
from ..domain.exceptions import PDFExtractionError


class PDFExtractorService:
    """
    Service for extracting product data from PDF files
    
    VERSIÓN MEJORADA: Detecta y procesa múltiples formatos de PDFs
    - Formato tabla simple (PRODUCTO | UNIDAD | PRECIO)
    - Formato precio neto (PRODUCTO | UNIDAD | PRECIO | DESCUENTO | PRECIO NETO)
    - Formato SKU/CSC (SKU | CSC | DESCRIPCION | UM | COSTO)
    - Formato REGEX (línea única: NOMBRE UNIDAD PRECIO)
    """

    def __init__(self):
        """Initialize PDF extractor service"""
        self.formato_detectado = None
        self.unidades_validas = {
            'KILO', 'KG', 'KILOS', 'LIBRA', 'LB', 'LIBRAS',
            'HECTOGRAMO', 'HG', 'HECTOGRAMOS', 'GRAMO', 'G', 'GRAMOS', 'GR',
            'PIEZA', 'PZ', 'PZA', 'PIEZAS', 'UNIDAD', 'DOCENA', 'PAZ', 'N',
            'LITRO', 'LT', 'LITROS', 'L', 'MILILITRO', 'ML', 'MJO', 'MJ',
            'LATA', 'BOTELLA', 'BOTE', 'CAJA', 'BOLSA', 'PAQUETE', 'PAQ', 'PQ',
            'MANOJO', 'CHAROLA', 'COSTAL', 'ROLLO', 'BURBUJA', 'GRANEL', 'CUBETA',
            'TABLETA', 'UN', 'UNIDAD', 'CJ', 'CAJA'
        }

    def extract_products(self, pdf_path: str) -> List[ExtractedProduct]:
        """
        Extract products from PDF file - Detecta formato automáticamente

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of extracted products

        Raises:
            PDFExtractionError: If extraction fails
        """
        if not pdf_path:
            raise ValueError("PDF path cannot be empty")

        try:
            # Detectar formato del PDF
            doc = fitz.open(pdf_path)
            page = doc[0]
            texto_sample = page.get_text()
            doc.close()

            # Intentar múltiples estrategias en orden de especificidad
            productos = []

            # 1. Intentar formato SKU/CSC (OCTUBRE OFICIAL)
            if "SKU" in texto_sample and "C.S.C" in texto_sample and "DESCRIPCION" in texto_sample:
                print("📋 Formato detectado: SKU/CSC (OCTUBRE OFICIAL)")
                self.formato_detectado = "octubre"
                productos = self._extraer_formato_octubre(pdf_path)

            # 2. Intentar formato PRECIO NETO (25 NOV - 01 DIC)
            elif "PRECIO NETO" in texto_sample and "DESCUENTO" in texto_sample:
                print("📋 Formato detectado: PRECIO NETO (25 NOV - 01 DIC)")
                self.formato_detectado = "precio_neto"
                productos = self._extraer_formato_precio_neto(pdf_path)

            # 3. Intentar formato tabla simple (PRECIOS_TIENDAS)
            elif "PRECIO ($)" in texto_sample or "PRECIO" in texto_sample:
                print("📋 Formato detectado: TABLA SIMPLE")
                self.formato_detectado = "tabla_simple"
                productos = self._extraer_formato_tabla_simple(pdf_path)

            # 4. Fallback: Intentar REGEX (formato una línea)
            else:
                print("📋 Formato detectado: REGEX (una línea)")
                self.formato_detectado = "regex"
                productos = self._extraer_formato_regex(pdf_path)

            if not productos:
                raise PDFExtractionError("No se pudieron extraer productos de ningún formato")

            # Eliminar duplicados
            productos_unicos = self._eliminar_duplicados_inteligente(productos)

            print(f"✅ Extracción completada: {len(productos_unicos)} productos únicos")
            return productos_unicos

        except Exception as e:
            raise PDFExtractionError(f"Error extracting products from PDF: {e}")

    def _extraer_formato_tabla_simple(self, pdf_path: str) -> List[ExtractedProduct]:
        """
        Extrae formato: PRODUCTO | UNIDAD | PRECIO (en líneas separadas)
        Estructura: Línea N: PRODUCTO, Línea N+1: UNIDAD, Línea N+2: PRECIO ($)
        
        Procesa todo el PDF y agrupa tríadas inteligentemente
        """
        doc = fitz.open(pdf_path)
        lineas_totales = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            texto = page.get_text()
            lineas = [l.strip() for l in texto.split('\n') if l.strip()]
            lineas_totales.extend(lineas)

        doc.close()

        # Saltar encabezado: buscar donde empieza el primer producto
        inicio = 0
        for i, linea in enumerate(lineas_totales):
            if linea == "PRECIO ($)" or linea == "PRECIO":
                inicio = i + 1
                break

        productos = []
        i = inicio
        
        while i < len(lineas_totales) - 2:
            nombre = lineas_totales[i].strip()
            unidad = lineas_totales[i + 1].strip()
            precio_str = lineas_totales[i + 2].strip()

            # Validar que tenemos un patrón válido
            if (self._es_nombre_valido(nombre) and 
                self._es_unidad_valida(unidad) and 
                (self._es_precio_valido(precio_str) or precio_str.startswith("$"))):

                try:
                    precio = self._parsear_precio(precio_str)

                    producto = ExtractedProduct(
                        nombre=self._limpiar_nombre_producto(nombre),
                        unidad=self._normalizar_unidad(unidad),
                        precio=precio,
                        tiene_precio=precio > 0
                    )
                    productos.append(producto)
                    i += 3  # Avanzar a la siguiente tríada
                except:
                    i += 1  # Si hay error, avanzar una línea
            else:
                i += 1

        return productos

    def _extraer_formato_precio_neto(self, pdf_path: str) -> List[ExtractedProduct]:
        """
        Extrae formato: PRODUCTO | UNIDAD | PRECIO | % | DESCUENTO | PRECIO NETO
        Usa: PRODUCTO, UNIDAD, PRECIO (sin descuento)
        
        Estructura:
        Línea N:   PRODUCTO
        Línea N+1: UNIDAD
        Línea N+2: PRECIO ← USAMOS ESTE
        Línea N+3: $
        Línea N+4: %
        Línea N+5: DESCUENTO
        Línea N+6: $
        Línea N+7: PRECIO NETO
        Línea N+8: $
        """
        doc = fitz.open(pdf_path)
        lineas_totales = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            texto = page.get_text()
            lineas = [l.strip() for l in texto.split('\n') if l.strip()]
            lineas_totales.extend(lineas)

        doc.close()

        # Buscar donde empieza: después de "PRECIO NETO"
        inicio = 0
        for i, linea in enumerate(lineas_totales):
            if "PRECIO NETO" in linea or "PRECIO" in linea and "%" in lineas_totales[i + 1] if i + 1 < len(lineas_totales) else False:
                inicio = i + 1
                break

        productos = []
        i = inicio

        while i < len(lineas_totales) - 8:
            nombre = lineas_totales[i].strip()
            unidad = lineas_totales[i + 1].strip()
            precio_str = lineas_totales[i + 2].strip()  # PRECIO (no PRECIO NETO)

            if (self._es_nombre_valido(nombre) and 
                self._es_unidad_valida(unidad) and 
                self._es_numero(precio_str)):

                try:
                    precio = self._parsear_precio(precio_str)

                    producto = ExtractedProduct(
                        nombre=self._limpiar_nombre_producto(nombre),
                        unidad=self._normalizar_unidad(unidad),
                        precio=precio,
                        tiene_precio=precio > 0
                    )
                    productos.append(producto)
                    i += 9  # Avanzar a siguiente tríada (9 líneas por producto)
                except:
                    i += 1
            else:
                i += 1

        return productos

    def _extraer_formato_octubre(self, pdf_path: str) -> List[ExtractedProduct]:
        """
        Extrae formato: SKU | C.S.C | DESCRIPCION | UM | COSTO
        Usa solo: DESCRIPCION, UM, COSTO
        """
        doc = fitz.open(pdf_path)
        lineas_totales = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            texto = page.get_text()
            lineas = [l.strip() for l in texto.split('\n') if l.strip()]
            lineas_totales.extend(lineas)

        doc.close()

        inicio = 0
        for i, linea in enumerate(lineas_totales):
            if "COSTO" in linea:
                inicio = i + 1
                break

        productos = []
        i = inicio

        while i < len(lineas_totales) - 5:
            # SKU (i), C.S.C (i+1), DESCRIPCION (i+2), UM (i+3), COSTO (i+4)
            descripcion = lineas_totales[i + 2].strip()
            unidad = lineas_totales[i + 3].strip()
            costo_str = lineas_totales[i + 4].strip()

            # Limpiar descripción (remover códigos entre paréntesis)
            nombre = re.sub(r'\s*\([^)]*\)\s*', ' ', descripcion).strip()

            if (self._es_nombre_valido(nombre) and 
                self._es_unidad_valida(unidad) and 
                self._es_numero(costo_str)):

                precio = self._parsear_precio(costo_str)

                producto = ExtractedProduct(
                    nombre=self._limpiar_nombre_producto(nombre),
                    unidad=self._normalizar_unidad(unidad),
                    precio=precio,
                    tiene_precio=precio > 0
                )
                productos.append(producto)
                i += 6
            else:
                i += 1

        return productos

    def _extraer_formato_regex(self, pdf_path: str) -> List[ExtractedProduct]:
        """
        Formato REGEX: Una línea con NOMBRE UNIDAD PRECIO
        Fallback para formatos desconocidos
        """
        doc = fitz.open(pdf_path)
        productos = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            texto = page.get_text()

            # Patrón flexible para detectar: NOMBRE UNIDAD PRECIO
            patron = r"([A-ZÀ-ÿÑñÜü'][A-Za-zÀ-ÿÑñÜü'\s/]+?)\s+(" + \
                     "|".join(self.unidades_validas) + \
                     r")\s+\$?\s*([\d,]+\.?\d*|-)"

            matches = re.finditer(patron, texto, re.MULTILINE | re.IGNORECASE)

            for match in matches:
                nombre = match.group(1).strip()
                unidad = match.group(2).strip()
                precio_str = match.group(3).strip()

                if precio_str == '-' or precio_str == '':
                    precio = Decimal('0.00')
                    tiene_precio = False
                else:
                    try:
                        precio_str = precio_str.replace(',', '')
                        precio = Decimal(precio_str)
                        tiene_precio = precio > 0
                    except:
                        continue

                producto = ExtractedProduct(
                    nombre=self._limpiar_nombre_producto(nombre),
                    unidad=self._normalizar_unidad(unidad),
                    precio=precio,
                    tiene_precio=tiene_precio
                )
                productos.append(producto)

        doc.close()
        return productos

    def _es_nombre_valido(self, texto: str) -> bool:
        """Valida si el texto es un nombre de producto válido"""
        if not texto or len(texto) < 2:
            return False
        if texto.replace(',', '').replace('.', '').replace('$', '').replace('-', '').isdigit():
            return False
        return True

    def _es_unidad_valida(self, texto: str) -> bool:
        """Valida si es una unidad conocida"""
        return texto.upper() in self.unidades_validas

    def _es_numero(self, texto: str) -> bool:
        """Verifica si es un número válido"""
        try:
            float(texto.replace(',', ''))
            return True
        except:
            return False

    def _es_precio_valido(self, texto: str) -> bool:
        """Valida si es un precio válido (con o sin $)"""
        if not texto or texto == '-':
            return True
        # Permitir precios con o sin símbolo $
        texto_limpio = texto.replace('$', '').replace(' ', '').strip()
        if not texto_limpio:
            return True
        try:
            float(texto_limpio.replace(',', ''))
            return True
        except:
            return False

    def _parsear_precio(self, texto: str) -> Decimal:
        """Convierte string de precio a Decimal"""
        if texto == '-' or not texto:
            return Decimal('0.00')

        texto = texto.replace('$', '').replace(' ', '').strip()
        try:
            texto = texto.replace(',', '')
            return Decimal(texto)
        except:
            return Decimal('0.00')

    def _limpiar_nombre_producto(self, nombre: str) -> str:
        """
        Clean and normalize product name
        ✅ Preserva caracteres especiales (ñ, á, é, etc.)
        """
        nombre = nombre.upper()
        nombre = re.sub(r'\s+', ' ', nombre)
        nombre = nombre.strip('.,;:')
        return nombre.strip()

    def _normalizar_unidad(self, unidad: str) -> str:
        """Normalize product unit to standard form"""
        unidad = unidad.upper().strip()

        normalizaciones = {
            'KILO': 'kg', 'KG': 'kg', 'KILOS': 'kg', 'K': 'kg',
            'PIEZA': 'pz', 'PZ': 'pz', 'PZA': 'pz', 'PIEZAS': 'pz', 'PAZ': 'pz',
            'UNIDAD': 'pz', 'UN': 'pz', 'N': 'pz',
            'LIBRA': 'lb', 'LB': 'lb', 'LIBRAS': 'lb',
            'MANOJO': 'mjo', 'MJO': 'mjo', 'MJ': 'mjo', 'MANOJOS': 'mjo',
            'PAQUETE': 'paq', 'PAQ': 'paq', 'PQ': 'paq', 'PAQUETES': 'paq',
            'LITRO': 'lt', 'LT': 'lt', 'LITROS': 'lt', 'L': 'lt',
            'MILILITRO': 'ml', 'ML': 'ml',
            'HECTOGRAMO': 'hg', 'HG': 'hg', 'HECTOGRAMOS': 'hg',
            'GRAMO': 'g', 'G': 'g', 'GRAMOS': 'g', 'GR': 'g',
            'BURBUJA': 'burbuja', 'GRANEL': 'granel', 'CUBETA': 'cubeta',
            'CAJA': 'caja', 'CJ': 'caja', 'COSTAL': 'costal', 'CHAROLA': 'charola',
            'BOLSA': 'bolsa', 'LATA': 'lata', 'BOTELLA': 'botella', 'BOTE': 'bote',
            'ROLLO': 'rollo', 'TABLETA': 'tableta', 'DOCENA': 'docena',
        }

        return normalizaciones.get(unidad, unidad.lower())

    def _eliminar_duplicados_inteligente(
        self,
        productos: List[ExtractedProduct]
    ) -> List[ExtractedProduct]:
        """
        Remove duplicates, prioritizing products with prices

        Args:
            productos: List of extracted products

        Returns:
            List of unique products
        """
        productos_map = {}

        for p in productos:
            key = f"{p.nombre.lower()}_{p.unidad.lower()}"

            if key not in productos_map:
                productos_map[key] = p
            else:
                # If current product has price and stored one doesn't, replace
                if p.tiene_precio and not productos_map[key].tiene_precio:
                    productos_map[key] = p

        return list(productos_map.values())