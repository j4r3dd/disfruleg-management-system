"""
Ubicuo AI - Database Connector para Disfruleg
Conecta Ubicuo AI con la base de datos existente
"""

import mysql.connector
from typing import List, Dict, Optional
import yaml


class DisfrulegDatabaseConnector:
    """Conector para la base de datos disfruleg"""
    
    def __init__(self, config_path: str = "config/configuracion.yaml"):
        """
        Inicializa el conector
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_path)
        self.connection = None
        self.cursor = None
    
    def _load_config(self, config_path: str) -> dict:
        """Carga la configuración desde YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Configuración por defecto
            return {
                'database': {
                    'host': 'localhost',
                    'port': 3306,
                    'database': 'disfruleg',
                    'user': 'root',
                    'password': ''
                }
            }
    
    def connect(self) -> bool:
        """
        Establece conexión con la base de datos
        
        Returns:
            True si la conexión fue exitosa
        """
        try:
            db_config = self.config.get('database', {})
            
            self.connection = mysql.connector.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 3306),
                database=db_config.get('database', 'disfruleg'),
                user=db_config.get('user', 'root'),
                password=db_config.get('password', ''),
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            
            self.cursor = self.connection.cursor(dictionary=True)
            return True
            
        except mysql.connector.Error as e:
            print(f"Error conectando a BD: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def get_all_products(self) -> List[Dict]:
        """
        Obtiene todos los productos de la base de datos
        
        Returns:
            Lista de diccionarios con información de productos
        """
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            # Query adaptada a tu estructura
            query = """
                SELECT 
                    id_producto as id,
                    nombre_producto as nombre,
                    unidad_producto as unidad,
                    stock,
                    es_especial,
                    COALESCE(
                        (SELECT precio 
                         FROM precio_por_grupo 
                         WHERE id_producto = producto.id_producto 
                         LIMIT 1), 
                        0
                    ) as precio
                FROM producto
                WHERE activo = TRUE
                ORDER BY nombre_producto
            """
            
            self.cursor.execute(query)
            productos = self.cursor.fetchall()
            
            # Formatear para Ubicuo AI
            productos_formatted = []
            for p in productos:
                productos_formatted.append({
                    'id': p['id'],
                    'nombre': p['nombre'],
                    'unidad': p['unidad'] or 'pz',
                    'precio': float(p['precio']) if p['precio'] else 0.0,
                    'categoria': 'Especial' if p.get('es_especial') else 'General',
                    'stock': float(p['stock']) if p.get('stock') else 0.0
                })
            
            return productos_formatted
            
        except mysql.connector.Error as e:
            print(f"Error obteniendo productos: {e}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """
        Obtiene un producto específico por ID
        
        Args:
            product_id: ID del producto
            
        Returns:
            Dict con información del producto o None
        """
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            query = """
                SELECT 
                    id_producto as id,
                    nombre_producto as nombre,
                    unidad_producto as unidad,
                    stock,
                    es_especial
                FROM producto
                WHERE id_producto = %s AND activo = TRUE
            """
            
            self.cursor.execute(query, (product_id,))
            producto = self.cursor.fetchone()
            
            if producto:
                return {
                    'id': producto['id'],
                    'nombre': producto['nombre'],
                    'unidad': producto['unidad'] or 'pz',
                    'stock': float(producto['stock']) if producto.get('stock') else 0.0,
                    'es_especial': producto.get('es_especial', False)
                }
            
            return None
            
        except mysql.connector.Error as e:
            print(f"Error obteniendo producto: {e}")
            return None
    
    def search_products(self, search_term: str, limit: int = 50) -> List[Dict]:
        """
        Busca productos por nombre
        
        Args:
            search_term: Término de búsqueda
            limit: Número máximo de resultados
            
        Returns:
            Lista de productos que coinciden
        """
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            query = """
                SELECT 
                    id_producto as id,
                    nombre_producto as nombre,
                    unidad_producto as unidad,
                    stock
                FROM producto
                WHERE nombre_producto LIKE %s 
                  AND activo = TRUE
                ORDER BY nombre_producto
                LIMIT %s
            """
            
            search_pattern = f"%{search_term}%"
            self.cursor.execute(query, (search_pattern, limit))
            productos = self.cursor.fetchall()
            
            return [{
                'id': p['id'],
                'nombre': p['nombre'],
                'unidad': p['unidad'] or 'pz',
                'stock': float(p['stock']) if p.get('stock') else 0.0
            } for p in productos]
            
        except mysql.connector.Error as e:
            print(f"Error buscando productos: {e}")
            return []
    
    def get_product_price(self, product_id: int, group_id: Optional[int] = None) -> float:
        """
        Obtiene el precio de un producto (opcionalmente por grupo)
        
        Args:
            product_id: ID del producto
            group_id: ID del grupo (opcional)
            
        Returns:
            Precio del producto
        """
        if not self.connection:
            if not self.connect():
                return 0.0
        
        try:
            if group_id:
                # Precio específico para el grupo
                query = """
                    SELECT precio
                    FROM precio_por_grupo
                    WHERE id_producto = %s AND id_grupo = %s
                """
                self.cursor.execute(query, (product_id, group_id))
            else:
                # Precio general (primer grupo o default)
                query = """
                    SELECT precio
                    FROM precio_por_grupo
                    WHERE id_producto = %s
                    LIMIT 1
                """
                self.cursor.execute(query, (product_id,))
            
            result = self.cursor.fetchone()
            return float(result['precio']) if result else 0.0
            
        except mysql.connector.Error as e:
            print(f"Error obteniendo precio: {e}")
            return 0.0
    
    def test_connection(self) -> Dict:
        """
        Prueba la conexión y retorna información
        
        Returns:
            Dict con información de la prueba
        """
        result = {
            'connected': False,
            'database': None,
            'products_count': 0,
            'error': None
        }
        
        try:
            if self.connect():
                result['connected'] = True
                result['database'] = self.config.get('database', {}).get('database', 'disfruleg')
                
                # Contar productos
                self.cursor.execute("SELECT COUNT(*) as count FROM producto WHERE activo = TRUE")
                count_result = self.cursor.fetchone()
                result['products_count'] = count_result['count'] if count_result else 0
                
        except Exception as e:
            result['error'] = str(e)
        
        return result


# Función de prueba
def test_connector():
    """Prueba el conector de base de datos"""
    print("=" * 60)
    print("🔌 PROBANDO CONECTOR DE BASE DE DATOS")
    print("=" * 60)
    
    connector = DisfrulegDatabaseConnector()
    
    # Test de conexión
    print("\n1️⃣ Probando conexión...")
    test_result = connector.test_connection()
    
    if test_result['connected']:
        print(f"   ✅ Conexión exitosa!")
        print(f"   📊 Base de datos: {test_result['database']}")
        print(f"   📦 Productos activos: {test_result['products_count']}")
    else:
        print(f"   ❌ Error de conexión: {test_result['error']}")
        return
    
    # Test de obtener productos
    print("\n2️⃣ Obteniendo productos...")
    productos = connector.get_all_products()
    print(f"   ✅ {len(productos)} productos cargados")
    
    if productos:
        print("\n   📋 Primeros 5 productos:")
        for i, p in enumerate(productos[:5], 1):
            print(f"      {i}. {p['nombre']} - {p['unidad']} - ${p['precio']:.2f}")
    
    # Test de búsqueda
    print("\n3️⃣ Probando búsqueda de 'chile'...")
    resultados = connector.search_products('chile')
    print(f"   ✅ {len(resultados)} resultados encontrados")
    
    if resultados:
        print("\n   🔍 Resultados:")
        for i, r in enumerate(resultados[:5], 1):
            print(f"      {i}. {r['nombre']} ({r['unidad']})")
    
    connector.disconnect()
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("=" * 60)


if __name__ == "__main__":
    test_connector()