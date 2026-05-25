"""
Módulo de normalización de datos
Proporciona funciones para normalizar texto, fechas, números y otros datos
"""
import unicodedata
import re
from datetime import datetime
from typing import Optional, Union

class Normalizador:
    """Clase para normalización de datos diversos"""
    
    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """
        Normaliza texto removiendo acentos y caracteres especiales
        
        Args:
            texto: Texto a normalizar
            
        Returns:
            Texto normalizado en minúsculas sin acentos
        """
        if not texto:
            return ""
        
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Remover acentos
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )
        
        return texto
    
    @staticmethod
    def normalizar_nombre_cliente(nombre: str) -> str:
        """
        Normaliza nombre de cliente para búsqueda
        
        Args:
            nombre: Nombre del cliente
            
        Returns:
            Nombre normalizado (sin acentos, minúsculas, sin espacios extras)
        """
        if not nombre:
            return ""
        
        # Normalizar texto base
        nombre = Normalizador.normalizar_texto(nombre)
        
        # Remover espacios múltiples
        nombre = re.sub(r'\s+', ' ', nombre)
        
        # Remover espacios al inicio y final
        nombre = nombre.strip()
        
        return nombre
    
    @staticmethod
    def normalizar_telefono(telefono: str) -> str:
        """
        Normaliza número de teléfono removiendo caracteres no numéricos
        
        Args:
            telefono: Número de teléfono
            
        Returns:
            Solo dígitos del teléfono
        """
        if not telefono:
            return ""
        
        # Remover todo excepto dígitos
        return re.sub(r'\D', '', str(telefono))
    
    @staticmethod
    def normalizar_precio(precio: Union[str, int, float]) -> float:
        """
        Normaliza precio a formato float
        
        Args:
            precio: Precio en cualquier formato
            
        Returns:
            Precio como float
        """
        if precio is None:
            return 0.0
        
        try:
            # Si es string, remover símbolos de moneda y comas
            if isinstance(precio, str):
                precio = precio.replace('$', '').replace(',', '').strip()
            
            return float(precio)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def normalizar_cantidad(cantidad: Union[str, int, float]) -> float:
        """
        Normaliza cantidad a formato float
        
        Args:
            cantidad: Cantidad en cualquier formato
            
        Returns:
            Cantidad como float
        """
        if cantidad is None:
            return 0.0
        
        try:
            # Si es string, limpiar
            if isinstance(cantidad, str):
                cantidad = cantidad.strip()
            
            return float(cantidad)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def normalizar_fecha(fecha: Union[str, datetime], formato_entrada: Optional[str] = None) -> Optional[datetime]:
        """
        Normaliza fecha a objeto datetime
        
        Args:
            fecha: Fecha como string o datetime
            formato_entrada: Formato del string de entrada (opcional)
            
        Returns:
            Objeto datetime o None si no se puede parsear
        """
        if fecha is None:
            return None
        
        if isinstance(fecha, datetime):
            return fecha
        
        # Formatos comunes de fecha
        formatos = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M:%S'
        ]
        
        if formato_entrada:
            formatos.insert(0, formato_entrada)
        
        for formato in formatos:
            try:
                return datetime.strptime(str(fecha).strip(), formato)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def normalizar_unidad(unidad: str) -> str:
        """
        Normaliza unidad de medida a formato estándar
        
        Args:
            unidad: Unidad de medida
            
        Returns:
            Unidad normalizada
        """
        if not unidad:
            return "UNIDAD"
        
        unidad = unidad.upper().strip()
        
        # Mapeo de unidades comunes
        mapeo = {
            'KG': 'KG',
            'KILO': 'KG',
            'KILOS': 'KG',
            'KILOGRAMO': 'KG',
            'KILOGRAMOS': 'KG',
            'G': 'G',
            'GR': 'G',
            'GRAMO': 'G',
            'GRAMOS': 'G',
            'L': 'L',
            'LT': 'L',
            'LITRO': 'L',
            'LITROS': 'L',
            'ML': 'ML',
            'MILILITRO': 'ML',
            'MILILITROS': 'ML',
            'PZ': 'PIEZA',
            'PZA': 'PIEZA',
            'PIEZA': 'PIEZA',
            'PIEZAS': 'PIEZA',
            'UNIDAD': 'UNIDAD',
            'UNIDADES': 'UNIDAD',
            'U': 'UNIDAD',
        }
        
        return mapeo.get(unidad, unidad)
    
    @staticmethod
    def es_email_valido(email: str) -> bool:
        """
        Valida si un email tiene formato correcto
        
        Args:
            email: Email a validar
            
        Returns:
            True si es válido, False si no
        """
        if not email:
            return False
        
        # Patrón simple de validación de email
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, email))
    
    @staticmethod
    def limpiar_sql_string(texto: str) -> str:
        """
        Limpia string para uso seguro en SQL (previene inyección básica)
        
        Args:
            texto: Texto a limpiar
            
        Returns:
            Texto limpio
        """
        if not texto:
            return ""
        
        # Remover caracteres peligrosos
        texto = texto.replace("'", "''")  # Escapar comillas simples
        texto = texto.replace(";", "")     # Remover punto y coma
        texto = texto.replace("--", "")    # Remover comentarios SQL
        
        return texto


# Funciones auxiliares para compatibilidad con código existente
def normalizar_texto(texto: str) -> str:
    """Función auxiliar para normalizar texto"""
    return Normalizador.normalizar_texto(texto)

def normalizar_nombre(nombre: str) -> str:
    """Función auxiliar para normalizar nombre"""
    return Normalizador.normalizar_nombre_cliente(nombre)

def normalizar_telefono(telefono: str) -> str:
    """Función auxiliar para normalizar teléfono"""
    return Normalizador.normalizar_telefono(telefono)

def normalizar_precio(precio: Union[str, int, float]) -> float:
    """Función auxiliar para normalizar precio"""
    return Normalizador.normalizar_precio(precio)

def normalizar_unidad(unidad: str) -> str:
    """Función auxiliar para normalizar unidad"""
    return Normalizador.normalizar_unidad(unidad)