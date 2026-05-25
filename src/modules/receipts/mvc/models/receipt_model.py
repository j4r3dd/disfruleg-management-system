# -*- coding: utf-8 -*-
"""
Receipt Model - Data and Business Logic Layer
Handles all database operations and business rules
"""

from typing import Optional, Dict, List, Any, Tuple
import traceback

from src.modules.receipts.components import database
from src.modules.receipts.components.orden_manager import obtener_manager
from src.config import debug_print
from src.modules.receipts.constants import OrderState, SectionNames


# Constants
DEFAULT_SECTION_NAME = SectionNames.GENERAL


class ReciboModel:
    """
    Model layer for receipt management

    Responsibilities:
    - Database operations (CRUD)
    - Business logic and validation
    - Data transformation
    - Order management
    """

    def __init__(self):
        self.orden_manager = obtener_manager()
        self.grupos_data: Dict[str, int] = {}
        self.clientes_grupo: List[Dict] = []
        self.clientes_map: Dict[str, int] = {}
        self.cliente_data: Dict[str, Any] = {}
        self.productos_filtrados: List[Dict] = []

        # Load initial data
        self._cargar_grupos()

    # ==================== DATA LOADING ====================

    def _cargar_grupos(self):
        """Load client groups from database"""
        try:
            grupos_raw = database.obtener_grupos()
            self.grupos_data = {}

            for grupo in grupos_raw:
                if isinstance(grupo, dict):
                    clave = grupo.get('clave_grupo', '')
                    id_grupo = grupo.get('id_grupo', 0)
                else:
                    id_grupo, clave = grupo[0], grupo[1]

                self.grupos_data[clave] = id_grupo

            debug_print(f"✅ Grupos cargados: {list(self.grupos_data.keys())}")

        except Exception as e:
            debug_print(f"❌ Error al cargar grupos: {e}")
            self.grupos_data = {}
            raise

    def cargar_clientes_por_grupo(self, clave_grupo: str) -> List[Dict[str, Any]]:
        """
        Load clients for a specific group

        Args:
            clave_grupo: Group key

        Returns:
            List of client dictionaries
        """
        if clave_grupo not in self.grupos_data:
            return []

        id_grupo = self.grupos_data[clave_grupo]

        try:
            clientes = database.obtener_clientes_por_grupo(id_grupo)
            self.clientes_grupo = []
            self.clientes_map = {}

            for cliente in clientes:
                if isinstance(cliente, dict):
                    self.clientes_grupo.append(cliente)
                    nombre = cliente.get('nombre_completo', cliente.get('nombre_cliente', ''))
                    self.clientes_map[nombre] = cliente.get('id_cliente', 0)
                else:
                    cliente_dict = {
                        'id_cliente': cliente[0],
                        'nombre_completo': cliente[1],
                        'id_grupo': cliente[2]
                    }
                    self.clientes_grupo.append(cliente_dict)
                    self.clientes_map[cliente[1]] = cliente[0]

            debug_print(f"✅ {len(self.clientes_grupo)} clientes cargados para grupo: {clave_grupo}")
            return self.clientes_grupo

        except Exception as e:
            debug_print(f"❌ Error al cargar clientes: {e}")
            traceback.print_exc()
            raise

    def obtener_cliente_por_nombre(self, nombre_cliente: str) -> Optional[Dict[str, Any]]:
        """
        Get client data by name

        Args:
            nombre_cliente: Client name

        Returns:
            Client dictionary or None
        """
        for cliente in self.clientes_grupo:
            nombre = cliente.get('nombre_completo', cliente.get('nombre_cliente', ''))
            if nombre == nombre_cliente:
                self.cliente_data = cliente
                return cliente
        return None

    def buscar_productos(self, clave_grupo: str, texto_busqueda: str):
        """
        Search products by text

        Args:
            clave_grupo: Group key for pricing
            texto_busqueda: Search text (matches start of product name)

        Returns:
            List of matching products
        """
        if not clave_grupo or clave_grupo not in self.grupos_data:
            return []

        if not texto_busqueda or len(texto_busqueda) < 2:
            return []

        id_grupo = self.grupos_data[clave_grupo]
        texto = texto_busqueda.lower().strip()

        try:
            # ✅ USE CONTEXT MANAGER - Auto-returns connection to pool
            from src.database.conexion import get_pooled_connection
            
            with get_pooled_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT
                        p.id_producto,
                        p.nombre_producto,
                        p.unidad_producto as unidad,
                        p.stock,
                        COALESCE(ppg.precio_base, 0) as precio_base,
                        COALESCE(tc.descuento, 0) as descuento,
                        ROUND(COALESCE(ppg.precio_base * (1 - tc.descuento/100), 0), 2) as precio
                    FROM producto p
                    LEFT JOIN precio_por_grupo ppg ON p.id_producto = ppg.id_producto
                        AND ppg.id_grupo = %s
                    LEFT JOIN grupo g ON ppg.id_grupo = g.id_grupo
                    LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                    WHERE LOWER(p.nombre_producto) LIKE %s
                    ORDER BY p.nombre_producto
                ''', (id_grupo, f'{texto}%'))

                productos_bd = []
                for row in cursor.fetchall():
                    if isinstance(row, dict):
                        productos_bd.append(row)
                    else:
                        productos_bd.append({
                            'id_producto': row[0],
                            'nombre_producto': row[1],
                            'unidad': row[2],
                            'stock': row[3],
                            'precio_base': row[4],
                            'descuento': row[5],
                            'precio': row[6]
                        })

                cursor.close()
                # ✅ Connection automatically returned to pool when exiting 'with' block

            self.productos_filtrados = [
                p for p in productos_bd
                if p['nombre_producto'].lower().startswith(texto)
            ]

            debug_print(f"🔍 {len(self.productos_filtrados)} productos encontrados")
            return self.productos_filtrados

        except Exception as e:
            debug_print(f"❌ Error al filtrar productos: {e}")
            traceback.print_exc()
            return []

    # ==================== ORDER MANAGEMENT ====================

    def cargar_orden(self, folio: int) -> Optional[Dict[str, Any]]:
        """
        Load order from database

        Args:
            folio: Order folio number

        Returns:
            Order data or None
        """
        try:
            orden_data = self.orden_manager.cargar_orden(folio)
            debug_print(f"✅ Orden {folio} cargada desde DB")
            return orden_data
        except Exception as e:
            debug_print(f"❌ Error al cargar orden {folio}: {e}")
            traceback.print_exc()
            return None

    def _convertir_carrito_para_guardar(self, carrito_data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to convert cart data to database format"""
        # Check if carrito_data is in new CartModel format or legacy format
        if 'items' in carrito_data and 'sections' in carrito_data:
            # CartModel new format - convert to legacy for database compatibility
            secciones_data = {}
            for item in carrito_data.get('items', []):
                seccion = item.get('seccion', 'GENERAL')
                if seccion not in secciones_data:
                    secciones_data[seccion] = []
                
                secciones_data[seccion].append({
                    'id_producto': item['id_producto'],
                    'nombre_producto': item['nombre'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio_unitario'],
                    'unidad': item['unidad'],
                    'seccion': seccion,
                    'es_especial': item.get('es_especial', False)
                })
            
            return {
                'secciones': secciones_data,
                'total': carrito_data.get('total', 0)
            }
        else:
            # Already in legacy format - use as-is
            return carrito_data

    def guardar_orden(
        self,
        id_cliente: int,
        carrito_data: Dict[str, Any],
        total: float,
        usuario: str = "Usuario",
        folio_existente: Optional[int] = None
    ) -> Tuple[Optional[int], List[str]]:
        """
        Save order to database
        
        Returns:
            Tuple of (folio, list of warnings)
        """
        try:
            # Convert cart to JSON-compatible format
            datos_para_guardar = self._convertir_carrito_para_guardar(carrito_data)
            warnings = []
            
            # Check for legacy format
            if 'secciones' in datos_para_guardar:
                debug_print(f"✅ Guardando en formato legacy")
            
            if folio_existente:
                # Update existing order
                # Note: Price recalculation is now handled in ClientSelectionController
                exito = self.orden_manager.actualizar_orden(
                    folio=folio_existente,
                    datos_carrito=datos_para_guardar,
                    total=total,
                    id_cliente=id_cliente
                )
                return (folio_existente, warnings) if exito else (None, [])
            else:
                # Create new order
                # Get next available folio
                nuevo_folio = self.orden_manager.obtener_siguiente_folio_disponible()

                if not nuevo_folio:
                    raise Exception("No se pudo obtener un folio disponible")

                # Reserve folio (creates order in database)
                exito = self.orden_manager.reservar_folio(
                    folio=nuevo_folio,
                    id_cliente=id_cliente,
                    usuario=usuario,
                    datos_carrito=datos_para_guardar,
                    total=total
                )

                if exito:
                    debug_print(f"✅ Nueva orden creada: Folio {nuevo_folio}")
                    return nuevo_folio, []
                else:
                    raise Exception(f"No se pudo reservar el folio {nuevo_folio}")

        except Exception as e:
            debug_print(f"❌ Error al guardar orden: {e}")
            traceback.print_exc()
            return None, []

    def obtener_cliente_por_id(self, id_cliente: int) -> Optional[Dict[str, Any]]:
        """
        Get client data by ID

        Args:
            id_cliente: Client ID

        Returns:
            Client dictionary or None
        """
        try:
            return database.obtener_cliente_por_id(id_cliente)
        except Exception as e:
            debug_print(f"❌ Error al obtener cliente {id_cliente}: {e}")
            return None

    # ==================== VALIDATION ====================

    def validar_orden_datos(self, orden_data: Optional[Dict]) -> bool:
        """
        Validate that order data exists

        Args:
            orden_data: Order data to validate

        Returns:
            True if valid, False otherwise
        """
        return orden_data is not None

    def validar_cliente_seleccionado(self) -> bool:
        """
        Validate that a client is selected

        Returns:
            True if client is selected
        """
        return bool(self.cliente_data and self.cliente_data.get('id_cliente'))

    # ==================== DATA TRANSFORMATION ====================

    def preparar_carrito_para_guardar(self, carrito) -> Dict[str, Any]:
        """
        Convert cart object to format for saving

        Args:
            carrito: CarritoConSeccionesV2 instance

        Returns:
            Dictionary with cart data ready for database
        """
        return self.orden_manager.carrito_a_json(carrito)

    def convertir_items_para_pdf(self, items_carrito: List[Dict]) -> List[tuple]:
        """
        Convert cart items to PDF format

        Args:
            items_carrito: List of cart items

        Returns:
            List of tuples for PDF generation
        """
        items_pdf = []
        for item in items_carrito:
            items_pdf.append((
                item.get('nombre_producto', ''),
                item.get('cantidad', 0),
                item.get('unidad', 'unidad'),
                item.get('precio_unitario', 0),
                item.get('subtotal', 0)
            ))
        return items_pdf

    # ==================== GETTERS ====================

    def get_grupos(self) -> Dict[str, int]:
        """Get all loaded groups"""
        return self.grupos_data

    def get_cliente_actual(self) -> Dict[str, Any]:
        """Get currently selected client"""
        return self.cliente_data

    def get_productos_filtrados(self) -> List[Dict[str, Any]]:
        """Get filtered products list"""
        return self.productos_filtrados

    def get_grupo_clave_por_id(self, id_grupo: int) -> Optional[str]:
        """
        Get grupo clave by ID

        Args:
            id_grupo: Group ID

        Returns:
            Group key or None if not found
        """
        for clave, gid in self.grupos_data.items():
            if gid == id_grupo:
                return clave
        return None

    def procesar_venta(self, items_bd: List[Dict], folio_numero: Optional[int] = None) -> Dict[str, Any]:
        """
        Process a sale (complete transaction)

        Args:
            items_bd: List of cart items formatted for database
            folio_numero: Optional folio number to use

        Returns:
            Dict with 'folio_factura' and 'id_factura'
        """
        from datetime import datetime

        if not self.validar_cliente_seleccionado():
            raise ValueError("No hay cliente seleccionado")

        id_cliente = self.cliente_data.get('id_cliente')
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')

        # Register sale in database
        resultado = database.crear_factura_completa(
            id_cliente=id_cliente,
            items_orden=items_bd,
            fecha_compra=fecha_hoy,
            fecha_registro=fecha_hoy,
            folio_numero=folio_numero
        )

        debug_print(f"✅ Venta procesada en base de datos")

        # Return format expected by controller
        if resultado:
            return {
                'folio_factura': resultado['folio_numero'],
                'id_factura': resultado['id_factura']
            }
        else:
            raise Exception("No se pudo crear la factura en la base de datos")

    def recalcular_precios_carrito(self, carrito_data: Dict[str, Any], id_cliente: int) -> Dict[str, Any]:
        """
        Recalculate prices for all items in cart based on client's group
        
        Args:
            carrito_data: Cart data dictionary
            id_cliente: New client ID
            
        Returns:
            Updated cart data
        """
        try:
            # 1. Get client's group
            cliente = self.obtener_cliente_por_id(id_cliente)
            if not cliente or not cliente.get('id_grupo'):
                debug_print(f"⚠️ No se pudo obtener grupo para cliente {id_cliente}")
                return carrito_data
                
            id_grupo = cliente['id_grupo']
            debug_print(f"🔄 Recalculando precios para grupo {id_grupo} (Cliente {id_cliente})")
            
            # 2. Extract product IDs
            product_ids = []
            items_list = []
            
            # Handle both formats
            if 'items' in carrito_data:
                items_list = carrito_data['items']
                product_ids = [item['id_producto'] for item in items_list]
            elif 'secciones' in carrito_data:
                # Legacy format - flatten items
                for seccion_items in carrito_data['secciones'].values():
                    for item in seccion_items:
                        items_list.append(item)
                        product_ids.append(item['id_producto'])
            
            if not product_ids:
                return carrito_data
                
            # 3. Batch fetch new prices
            from src.modules.receipts.components.database import _get_product_repo
            repo = _get_product_repo()
            new_prices = repo.get_products_prices_by_ids(product_ids, id_grupo)
            
            # 4. Update items
            total_actualizado = 0.0
            productos_sin_precio = []
            
            for item in items_list:
                id_prod = item['id_producto']
                
                if id_prod in new_prices:
                    nuevo_precio = new_prices[id_prod]
                    precio_anterior = float(item.get('precio_unitario', 0))
                    
                    if abs(nuevo_precio - precio_anterior) > 0.01:
                        debug_print(f"  - {item.get('nombre_producto', 'Producto')}: ${precio_anterior} -> ${nuevo_precio}")
                        
                    item['precio_unitario'] = nuevo_precio
                    item['subtotal'] = nuevo_precio * float(item.get('cantidad', 0))
                else:
                    # Keep old price but warn
                    productos_sin_precio.append(item.get('nombre_producto', f'ID {id_prod}'))
                    debug_print(f"⚠️ {item.get('nombre_producto')}: SIN PRECIO en el nuevo grupo (mantiene ${item.get('precio_unitario')})")
                
                total_actualizado += float(item.get('subtotal', 0))
            
            # Update total in main dict
            carrito_data['total'] = total_actualizado
            
            if productos_sin_precio:
                debug_print(f"⚠️ ADVERTENCIA: {len(productos_sin_precio)} producto(s) sin precio en el nuevo grupo:")
                for p in productos_sin_precio:
                    debug_print(f"  - {p}")
                debug_print("  → Estos productos mantienen su precio anterior. Puede editarlos manualmente si es necesario.")
            
            return carrito_data, productos_sin_precio
            
        except Exception as e:
            debug_print(f"❌ Error recalculando precios: {e}")
            traceback.print_exc()
            return carrito_data, []