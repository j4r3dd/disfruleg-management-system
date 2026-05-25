"""
Ubicuo AI - Matcher Inteligente (CORREGIDO + OPTIMIZADO)
Sistema de matching con fuzzy logic mejorado y caché LRU
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache
import yaml

logger = logging.getLogger(__name__)

try:
    from rapidfuzz import fuzz, process
    FUZZY_LIBRARY = 'rapidfuzz'
except ImportError:
    try:
        from fuzzywuzzy import fuzz, process
        FUZZY_LIBRARY = 'fuzzywuzzy'
    except ImportError:
        raise ImportError("Se requiere 'rapidfuzz' o 'fuzzywuzzy'. Instala con: pip install rapidfuzz")


@dataclass
class MatchResult:
    """Resultado de un matching"""
    query: str
    matched_product: str
    matched_id: int
    confidence: float
    method: str  # 'exact', 'fuzzy', 'learned'
    category: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            'query': self.query,
            'matched_product': self.matched_product,
            'matched_id': self.matched_id,
            'confidence': self.confidence,
            'method': self.method,
            'category': self.category,
            'unit': self.unit,
            'price': self.price
        }


class UbicuoMatcher:
    """Sistema de matching inteligente con fuzzy logic"""
    
    def __init__(self, config_path: str = "config/configuracion.yaml"):
        """
        Inicializa el matcher
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_path)
        # CORRECCIÓN: Threshold más estricto
        self.threshold = self.config.get('matching', {}).get('threshold', 0.80)
        self.products_cache: Dict[str, dict] = {}
        self.learning_dict: Dict[str, str] = {}
        # Versión de caché para invalidación
        self._cache_version = 0
        
    def _load_config(self, config_path: str) -> dict:
        """Carga configuración desde YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {
                'matching': {
                    'threshold': 0.80,  # CORRECCIÓN: Más estricto
                    'algorithm': 'rapidfuzz',
                    'options': {
                        'case_sensitive': False,
                        'partial_match': False,  # CORRECCIÓN: Desactivado
                        'token_sort': True,
                        'token_set': False
                    }
                }
            }
    
    def set_products_db(self, products: List[Dict]) -> None:
        """
        Carga los productos desde la base de datos al cache
        
        Args:
            products: Lista de diccionarios con info de productos
                     Cada dict debe tener: id, nombre, categoria, unidad, precio
        """
        self.products_cache = {}
        for product in products:
            product_id = product.get('id')
            name = product.get('nombre', '').strip()
            
            if product_id and name:
                self.products_cache[name.lower()] = {
                    'id': product_id,
                    'nombre': name,
                    'categoria': product.get('categoria', ''),
                    'unidad': product.get('unidad', ''),
                    'precio': product.get('precio', 0.0)
                }
        
        # Invalidar caché de matches al recargar productos
        self._cache_version += 1
        self._cached_match.cache_clear()
        logger.info(f"Productos cargados: {len(self.products_cache)} items (caché v{self._cache_version})")
    
    def set_learning_dictionary(self, learning_dict: Dict[str, str]) -> None:
        """
        Carga el diccionario de aprendizaje
        
        Args:
            learning_dict: Dict con mapeo de errores -> nombres correctos
        """
        self.learning_dict = {k.lower(): v.lower() for k, v in learning_dict.items()}
        # Invalidar caché al actualizar diccionario
        self._cache_version += 1
        self._cached_match.cache_clear()
        logger.debug(f"Diccionario de aprendizaje actualizado: {len(self.learning_dict)} entradas")
    
    @lru_cache(maxsize=1000)
    def _cached_match(self, query: str, unit_hint: Optional[str], cache_version: int) -> Optional[tuple]:
        """
        Match con caché LRU.
        El cache_version fuerza invalidación cuando cambian los datos.
        Retorna tuple para ser hasheable (luego se convierte a MatchResult).
        """
        query_lower = query.strip().lower()
        
        # Nivel 1: Matching Exacto
        exact_match = self._exact_match(query_lower)
        if exact_match:
            result = self._create_result(query, exact_match, 1.0, 'exact', unit_hint)
            return self._result_to_tuple(result) if result else None
        
        # Nivel 2: Diccionario de Aprendizaje
        learned_match = self._learned_match(query_lower)
        if learned_match:
            result = self._create_result(query, learned_match, 0.95, 'learned', unit_hint)
            return self._result_to_tuple(result) if result else None
        
        # Nivel 3: Fuzzy Matching (MEJORADO)
        fuzzy_match = self._fuzzy_match(query_lower, unit_hint)
        if fuzzy_match:
            return self._result_to_tuple(fuzzy_match)
        
        return None
    
    def _result_to_tuple(self, result: 'MatchResult') -> tuple:
        """Convierte MatchResult a tuple para caché"""
        return (
            result.query,
            result.matched_product,
            result.matched_id,
            result.confidence,
            result.method,
            result.category,
            result.unit,
            result.price
        )
    
    def _tuple_to_result(self, t: tuple) -> 'MatchResult':
        """Convierte tuple a MatchResult"""
        return MatchResult(
            query=t[0],
            matched_product=t[1],
            matched_id=t[2],
            confidence=t[3],
            method=t[4],
            category=t[5],
            unit=t[6],
            price=t[7]
        )
    
    def match(self, query: str, unit_hint: Optional[str] = None) -> Optional[MatchResult]:
        """
        Busca el mejor match para un producto (con caché)
        
        Args:
            query: Nombre del producto a buscar
            unit_hint: Unidad del producto (para boost de confianza)
            
        Returns:
            MatchResult con el mejor match o None si no se encuentra
        """
        if not self.products_cache:
            return None
        
        # Usar versión de caché para invalidación automática
        cached = self._cached_match(query, unit_hint, self._cache_version)
        if cached:
            return self._tuple_to_result(cached)
        return None
    
    def _exact_match(self, query: str) -> Optional[dict]:
        """Busca coincidencia exacta"""
        return self.products_cache.get(query)
    
    def _learned_match(self, query: str) -> Optional[dict]:
        """Busca en el diccionario de aprendizaje"""
        if query in self.learning_dict:
            corrected_name = self.learning_dict[query]
            return self.products_cache.get(corrected_name)
        return None
    
    def _fuzzy_match(self, query: str, unit_hint: Optional[str] = None) -> Optional[MatchResult]:
        """Realiza fuzzy matching MEJORADO con múltiples scorers"""
        product_names = list(self.products_cache.keys())
        
        # CORRECCIÓN: Usar múltiples scorers y promediar
        scorers = [
            ('WRatio', fuzz.WRatio),  # Weighted Ratio (mejor balance)
            ('token_sort', fuzz.token_sort_ratio),
            ('ratio', fuzz.ratio)
        ]
        
        best_overall = None
        best_confidence = 0
        
        for scorer_name, scorer in scorers:
            results = process.extract(
                query,
                product_names,
                scorer=scorer,
                limit=3
            )
            
            if not results:
                continue
            
            # Obtener el mejor resultado de este scorer
            if FUZZY_LIBRARY == 'rapidfuzz':
                best_match, score, _ = results[0]
            else:
                best_match, score = results[0][0], results[0][1]
            
            confidence = score / 100.0
            
            # Verificar si este es mejor que el anterior
            if confidence > best_confidence:
                best_confidence = confidence
                best_overall = best_match
        
        if not best_overall:
            return None
        
        # Aplicar boosts de confianza
        product_data = self.products_cache[best_overall]
        final_confidence = self._apply_confidence_boosts(
            best_confidence,
            product_data,
            unit_hint,
            query
        )
        
        # CORRECCIÓN: Verificar threshold más estricto
        if final_confidence < self.threshold:
            return None
        
        return self._create_result(query, product_data, final_confidence, 'fuzzy', unit_hint)
    
    def _apply_confidence_boosts(
        self,
        base_confidence: float,
        product_data: dict,
        unit_hint: Optional[str],
        query: str
    ) -> float:
        """Aplica boosts y penalizaciones de confianza"""
        boost_config = self.config.get('matching', {}).get('boost', {})
        
        confidence = base_confidence
        
        # CORRECCIÓN: Boost por coincidencia de unidad
        if unit_hint and product_data.get('unidad'):
            if self._units_match(unit_hint, product_data['unidad']):
                confidence += boost_config.get('exact_unit_match', 0.10)
        
        # NUEVO: Penalización si la longitud es muy diferente
        query_len = len(query.split())
        product_len = len(product_data['nombre'].lower().split())
        len_diff = abs(query_len - product_len)
        
        if len_diff > 2:
            confidence -= 0.15  # Penalizar diferencias grandes
        
        # NUEVO: Boost si contiene palabras clave exactas
        query_words = set(query.split())
        product_words = set(product_data['nombre'].lower().split())
        common_words = query_words & product_words
        
        if len(common_words) >= len(query_words) * 0.7:  # 70% de palabras coinciden
            confidence += 0.10
        
        # Limitar al máximo de 1.0
        return min(confidence, 1.0)
    
    def _units_match(self, unit1: str, unit2: str) -> bool:
        """Compara si dos unidades son equivalentes"""
        unit_equivalents = {
            'kg': ['kg', 'kgs', 'kilo', 'kilos'],
            'gr': ['gr', 'g', 'gramo', 'gramos'],
            'pz': ['pz', 'pza', 'pieza', 'piezas'],
            'manojo': ['manojo', 'manojos'],
            'caja': ['caja', 'cajas'],
            'litro': ['litro', 'litros', 'lt', 'l'],
            'bolsa': ['bolsa', 'bolsas'],
            'paquete': ['paquete', 'paquetes']
        }
        
        u1 = unit1.lower()
        u2 = unit2.lower()
        
        if u1 == u2:
            return True
        
        for equivalents in unit_equivalents.values():
            if u1 in equivalents and u2 in equivalents:
                return True
        
        return False
    
    def _create_result(
        self,
        query: str,
        product_data: dict,
        confidence: float,
        method: str,
        unit_hint: Optional[str]
    ) -> MatchResult:
        """Crea un MatchResult a partir de los datos"""
        return MatchResult(
            query=query,
            matched_product=product_data['nombre'],
            matched_id=product_data['id'],
            confidence=confidence,
            method=method,
            category=product_data.get('categoria'),
            unit=product_data.get('unidad'),
            price=product_data.get('precio')
        )
    
    def match_batch(
        self,
        queries: List[Tuple[str, Optional[str]]]
    ) -> List[Optional[MatchResult]]:
        """
        Realiza matching en batch para múltiples queries
        
        Args:
            queries: Lista de tuplas (producto, unidad_hint)
            
        Returns:
            Lista de MatchResult (o None para cada uno)
        """
        results = []
        for query, unit_hint in queries:
            result = self.match(query, unit_hint)
            results.append(result)
        return results
    
    def get_suggestions(
        self,
        query: str,
        limit: int = 5
    ) -> List[MatchResult]:
        """
        Obtiene múltiples sugerencias para un query (MEJORADO)
        
        Args:
            query: Producto a buscar
            limit: Número máximo de sugerencias
            
        Returns:
            Lista de MatchResult ordenada por confianza
        """
        if not self.products_cache:
            return []
        
        query_lower = query.strip().lower()
        product_names = list(self.products_cache.keys())
        
        # CORRECCIÓN: Usar WRatio para mejores sugerencias
        results = process.extract(
            query_lower,
            product_names,
            scorer=fuzz.WRatio,
            limit=limit * 2  # Obtener más para filtrar mejor
        )
        
        suggestions = []
        seen_products = set()
        
        for item in results:
            if FUZZY_LIBRARY == 'rapidfuzz':
                name, score, _ = item
            else:
                name, score = item[0], item[1]
            
            confidence = score / 100.0
            
            # CORRECCIÓN: Umbral mínimo más alto para sugerencias
            if confidence >= 0.60 and name not in seen_products:
                product_data = self.products_cache[name]
                suggestions.append(
                    self._create_result(query, product_data, confidence, 'suggestion', None)
                )
                seen_products.add(name)
                
                if len(suggestions) >= limit:
                    break
        
        return suggestions
    
    def add_to_learning_dict(self, incorrect: str, correct: str) -> None:
        """
        Agrega una corrección al diccionario de aprendizaje
        
        Args:
            incorrect: Texto incorrecto que escribió el usuario
            correct: Nombre correcto del producto en BD
        """
        self.learning_dict[incorrect.lower()] = correct.lower()
    
    def get_statistics(self) -> dict:
        """Obtiene estadísticas del matcher"""
        return {
            'products_in_cache': len(self.products_cache),
            'learning_entries': len(self.learning_dict),
            'threshold': self.threshold,
            'fuzzy_library': FUZZY_LIBRARY
        }