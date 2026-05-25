# -*- coding: utf-8 -*-
"""
Orden Manager - Enhanced Order Management System
CORREGIDO: Formatea fechas en Python en lugar de SQL DATE_FORMAT
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from src.database.conexion import get_pooled_connection

_orden_manager_instance = None


def obtener_manager():
    """Get or create the singleton OrdenManager instance"""
    global _orden_manager_instance
    if _orden_manager_instance is None:
        _orden_manager_instance = OrdenManager()
    return _orden_manager_instance


class OrdenManager:
    """
    Manages order lifecycle and state transitions
    
    Order States (según BD):
    - guardada: Order created, not yet confirmed
    - registrada: Order converted to invoice
    """
    
    def __init__(self):
        """Initialize the order manager"""
        pass
    
    # ==================== FOLIO MANAGEMENT ====================
    
    def obtener_siguiente_folio_disponible(self) -> Optional[int]:
        """Get next available folio number"""
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT MAX(folio_numero) as max_folio FROM ordenes_guardadas WHERE activo = TRUE")
                result_orden = cursor.fetchone()
                max_orden = result_orden.get('max_folio', 0) if result_orden and result_orden.get('max_folio') else 0
                
                cursor.execute("SELECT MAX(folio_numero) as max_folio FROM factura")
                result_factura = cursor.fetchone()
                max_factura = result_factura.get('max_folio', 0) if result_factura and result_factura.get('max_folio') else 0
                
                max_folio = max(max_orden, max_factura)
                siguiente = max_folio + 1 if max_folio > 0 else 1
                
                cursor.close()
                
            return siguiente
            
        except Exception as e:
            print(f"❌ Error obteniendo siguiente folio: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def reservar_folio(
        self,
        folio: int,
        id_cliente: int,
        usuario: str,
        datos_carrito: Dict[str, Any],
        total: float
    ) -> bool:
        """Reserve a folio by creating an order in 'guardada' state"""
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()
                
                carrito_json = json.dumps(datos_carrito, ensure_ascii=False)
                fecha_actual = datetime.now()
                
                cursor.execute('''
                    INSERT INTO ordenes_guardadas (
                        folio_numero,
                        id_cliente,
                        usuario_creador,
                        datos_carrito,
                        total_estimado,
                        estado,
                        activo,
                        fecha_creacion,
                        fecha_modificacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    folio,
                    id_cliente,
                    usuario,
                    carrito_json,
                    total,
                    'guardada',
                    True,
                    fecha_actual,
                    fecha_actual
                ))
                
                conn.commit()
                cursor.close()
                
            print(f"✅ Folio {folio} reservado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al reservar folio {folio}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ==================== ORDER OPERATIONS ====================
    
    def cargar_orden(self, folio: int) -> Optional[Dict[str, Any]]:
        """Load order from database"""
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        o.id_orden,
                        o.folio_numero,
                        o.id_cliente,
                        o.fecha_creacion,
                        o.estado,
                        o.total_estimado as total,
                        o.datos_carrito,
                        o.usuario_creador as usuario,
                        c.nombre_cliente,
                        c.id_grupo
                    FROM ordenes_guardadas o
                    JOIN cliente c ON o.id_cliente = c.id_cliente
                    WHERE o.folio_numero = %s AND o.activo = TRUE
                ''', (folio,))
                
                row = cursor.fetchone()
                cursor.close()
                
            if not row:
                return None
                
            try:
                datos_carrito = json.loads(row['datos_carrito'])
            except:
                datos_carrito = {}
            
            datos_carrito = self._normalizar_estructura_carrito(datos_carrito)
            
            return {
                'id_orden': row['id_orden'],
                'folio': row['folio_numero'],
                'id_cliente': row['id_cliente'],
                'nombre_cliente': row['nombre_cliente'],
                'id_grupo': row['id_grupo'],
                'fecha': row['fecha_creacion'],
                'estado': row['estado'],
                'total': float(row['total']),
                'datos_carrito': datos_carrito,
                'usuario': row['usuario']
            }
            
        except Exception as e:
            print(f"❌ Error cargando orden {folio}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def actualizar_orden(
        self,
        folio: int,
        datos_carrito: Dict[str, Any],
        total: float,
        id_cliente: Optional[int] = None
    ) -> bool:
        """Update existing order"""
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()
                
                carrito_json = json.dumps(datos_carrito, ensure_ascii=False)
                fecha_actual = datetime.now()
                
                if id_cliente:
                    cursor.execute('''
                        UPDATE ordenes_guardadas 
                        SET datos_carrito = %s,
                            total_estimado = %s,
                            fecha_modificacion = %s,
                            id_cliente = %s
                        WHERE folio_numero = %s AND activo = TRUE
                    ''', (carrito_json, total, fecha_actual, id_cliente, folio))
                else:
                    cursor.execute('''
                        UPDATE ordenes_guardadas 
                        SET datos_carrito = %s,
                            total_estimado = %s,
                            fecha_modificacion = %s
                        WHERE folio_numero = %s AND activo = TRUE
                    ''', (carrito_json, total, fecha_actual, folio))
                
                conn.commit()
                affected = cursor.rowcount
                cursor.close()
                
            if affected > 0:
                print(f"✅ Orden {folio} actualizada")
                return True
            else:
                print(f"⚠️ No se encontró orden con folio {folio}")
                return False
                
        except Exception as e:
            print(f"❌ Error actualizando orden {folio}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def confirmar_orden(self, folio: int) -> bool:
        """Change order state to 'registrada'"""
        return self._cambiar_estado_orden(folio, 'registrada')
    
    def cancelar_orden(self, folio: int) -> bool:
        """Cancel order by setting activo = FALSE"""
        return self.eliminar_orden(folio)
    
    def _cambiar_estado_orden(self, folio: int, nuevo_estado: str) -> bool:
        """Change order state"""
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE ordenes_guardadas 
                    SET estado = %s,
                        fecha_modificacion = %s
                    WHERE folio_numero = %s AND activo = TRUE
                ''', (nuevo_estado, datetime.now(), folio))
                
                conn.commit()
                affected = cursor.rowcount
                cursor.close()
                
            if affected > 0:
                print(f"✅ Orden {folio} -> {nuevo_estado}")
                return True
            else:
                print(f"⚠️ No se encontró orden {folio}")
                return False
                
        except Exception as e:
            print(f"❌ Error cambiando estado de orden {folio}: {e}")
            return False
    
    def eliminar_orden(self, folio: int) -> bool:
        """
        Delete order permanently (physical delete)

        Only deletes orders with estado='guardada'.
        Protected by database trigger 'before_orden_delete'.
        """
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()

                # Physical delete - trigger prevents deletion of registered orders
                cursor.execute('''
                    DELETE FROM ordenes_guardadas
                    WHERE folio_numero = %s
                        AND estado = 'guardada'
                ''', (folio,))

                conn.commit()
                affected = cursor.rowcount
                cursor.close()

            if affected > 0:
                print(f"✅ Orden {folio} eliminada permanentemente (folio liberado)")
                return True
            else:
                print(f"⚠️ No se encontró orden {folio} o está registrada")
                return False

        except Exception as e:
            print(f"❌ Error eliminando orden {folio}: {e}")
            return False
    
    def liberar_folio(self, folio: int) -> bool:
        """Alias para eliminar_orden - mantiene compatibilidad"""
        return self.eliminar_orden(folio)
    
    # ==================== QUERY HELPERS ====================
    
    def obtener_ordenes_activas(self, username: str, es_admin: bool = False) -> List[Dict[str, Any]]:
        """Obtiene todas las órdenes activas (estado='guardada')"""
        try:
            with get_pooled_connection() as conn:
                # Commit to ensure fresh snapshot (REPEATABLE READ)
                conn.commit()
                cursor = conn.cursor()
                
                # ✅ Sin DATE_FORMAT - formatear en Python
                query = '''
                    SELECT 
                        o.id_orden,
                        o.folio_numero,
                        o.id_cliente,
                        o.fecha_creacion,
                        o.fecha_modificacion,
                        o.estado,
                        o.total_estimado,
                        o.datos_carrito,
                        o.usuario_creador,
                        c.nombre_cliente,
                        c.id_grupo
                    FROM ordenes_guardadas o
                    JOIN cliente c ON o.id_cliente = c.id_cliente
                    WHERE o.activo = TRUE AND o.estado = 'guardada'
                '''
                
                if not es_admin:
                    query += ' AND o.usuario_creador = %s'
                    cursor.execute(query + ' ORDER BY o.fecha_modificacion DESC', (username,))
                else:
                    cursor.execute(query + ' ORDER BY o.fecha_modificacion DESC')
                
                ordenes = []
                for row in cursor.fetchall():
                    try:
                        datos_carrito = json.loads(row['datos_carrito']) if row['datos_carrito'] else {}
                    except:
                        datos_carrito = {}
                    
                    datos_carrito = self._normalizar_estructura_carrito(datos_carrito)
                    
                    # ✅ Formatear fechas en Python
                    fecha_creacion_str = row['fecha_creacion'].strftime('%Y-%m-%d %H:%M') if row['fecha_creacion'] else 'N/A'
                    fecha_modificacion_str = row['fecha_modificacion'].strftime('%Y-%m-%d %H:%M') if row['fecha_modificacion'] else 'N/A'
                    
                    ordenes.append({
                        'id_orden': row['id_orden'],
                        'folio_numero': row['folio_numero'],
                        'id_cliente': row['id_cliente'],
                        'nombre_cliente': row['nombre_cliente'],
                        'id_grupo': row['id_grupo'],
                        'fecha_creacion': row['fecha_creacion'],
                        'fecha_modificacion': row['fecha_modificacion'],
                        'fecha_creacion_str': fecha_creacion_str,
                        'fecha_modificacion_str': fecha_modificacion_str,
                        'estado': row['estado'],
                        'total_estimado': float(row['total_estimado']),
                        'datos_carrito': datos_carrito,
                        'usuario_creador': row['usuario_creador']
                    })
                
                cursor.close()
                
            return ordenes
            
        except Exception as e:
            print(f"❌ Error obteniendo órdenes activas: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def obtener_historial(self, username: str, es_admin: bool = False, limite: int = 100) -> List[Dict[str, Any]]:
        """Obtiene el historial de órdenes (estado='registrada' o activo=FALSE)"""
        try:
            with get_pooled_connection() as conn:
                # Commit to ensure fresh snapshot
                conn.commit()
                cursor = conn.cursor()
                
                # ✅ Sin DATE_FORMAT - formatear en Python
                query = '''
                    SELECT 
                        o.id_orden,
                        o.folio_numero,
                        o.id_cliente,
                        o.fecha_creacion,
                        o.fecha_modificacion,
                        o.estado,
                        o.total_estimado,
                        o.datos_carrito,
                        o.usuario_creador,
                        o.activo,
                        c.nombre_cliente,
                        c.id_grupo
                    FROM ordenes_guardadas o
                    JOIN cliente c ON o.id_cliente = c.id_cliente
                    WHERE (o.estado = 'registrada' OR o.activo = FALSE)
                '''
                
                if not es_admin:
                    query += ' AND o.usuario_creador = %s'
                    cursor.execute(
                        query + ' ORDER BY o.fecha_modificacion DESC LIMIT %s', 
                        (username, limite)
                    )
                else:
                    cursor.execute(query + ' ORDER BY o.fecha_modificacion DESC LIMIT %s', (limite,))
                
                historial = []
                for row in cursor.fetchall():
                    try:
                        datos_carrito = json.loads(row['datos_carrito']) if row['datos_carrito'] else {}
                    except:
                        datos_carrito = {}
                    
                    datos_carrito = self._normalizar_estructura_carrito(datos_carrito)
                    
                    # ✅ Formatear fechas en Python
                    fecha_creacion_str = row['fecha_creacion'].strftime('%Y-%m-%d %H:%M') if row['fecha_creacion'] else 'N/A'
                    fecha_modificacion_str = row['fecha_modificacion'].strftime('%Y-%m-%d %H:%M') if row['fecha_modificacion'] else 'N/A'
                    
                    historial.append({
                        'id_orden': row['id_orden'],
                        'folio_numero': row['folio_numero'],
                        'id_cliente': row['id_cliente'],
                        'nombre_cliente': row['nombre_cliente'],
                        'id_grupo': row['id_grupo'],
                        'fecha_creacion': row['fecha_creacion'],
                        'fecha_modificacion': row['fecha_modificacion'],
                        'fecha_creacion_str': fecha_creacion_str,
                        'fecha_modificacion_str': fecha_modificacion_str,
                        'estado': row['estado'],
                        'total_estimado': float(row['total_estimado']),
                        'datos_carrito': datos_carrito,
                        'usuario_creador': row['usuario_creador'],
                        'activo': row['activo']
                    })
                
                cursor.close()
                
            return historial
            
        except Exception as e:
            print(f"❌ Error obteniendo historial: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def listar_ordenes_por_cliente(self, id_cliente: int) -> List[Dict[str, Any]]:
        """List all active orders for a client"""
        try:
            with get_pooled_connection() as conn:
                conn.commit()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        folio_numero,
                        fecha_creacion,
                        estado,
                        total_estimado as total
                    FROM ordenes_guardadas
                    WHERE id_cliente = %s AND activo = TRUE
                    ORDER BY fecha_creacion DESC
                ''', (id_cliente,))
                
                ordenes = []
                for row in cursor.fetchall():
                    ordenes.append({
                        'folio': row['folio_numero'],
                        'fecha': row['fecha_creacion'],
                        'estado': row['estado'],
                        'total': float(row['total'])
                    })
                
                cursor.close()
                
            return ordenes
            
        except Exception as e:
            print(f"❌ Error listando órdenes del cliente {id_cliente}: {e}")
            return []
    
    # ==================== CART SERIALIZATION ====================
    
    def _normalizar_estructura_carrito(self, datos_carrito: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza la estructura del carrito para compatibilidad entre formatos"""
        if not isinstance(datos_carrito, dict):
            return {'secciones': {}, 'total': 0}
        
        if 'secciones' in datos_carrito:
            return datos_carrito
        
        if 'items' in datos_carrito:
            items = datos_carrito.get('items', [])
            total = datos_carrito.get('total', 0)
            
            secciones = {}
            for item in items:
                nombre_seccion = item.get('seccion', 'GENERAL')
                
                if nombre_seccion not in secciones:
                    secciones[nombre_seccion] = []
                
                item_convertido = {
                    'id_producto': item.get('id_producto'),
                    'nombre_producto': item.get('nombre', ''),
                    'cantidad': float(item.get('cantidad', 0)),
                    'unidad': item.get('unidad', ''),
                    'precio_unitario': float(item.get('precio_unitario', 0)),
                    'subtotal': float(item.get('subtotal', 0))
                }
                
                secciones[nombre_seccion].append(item_convertido)
            
            return {
                'secciones': secciones,
                'total': float(total)
            }
        
        return {'secciones': {}, 'total': 0}
    
    def carrito_a_json(self, carrito) -> Dict[str, Any]:
        """Convert CarritoConSeccionesV2 to JSON-serializable dict"""
        try:
            secciones_data = {}
            
            for seccion_nombre in carrito.secciones.keys():
                items = carrito.obtener_items_seccion(seccion_nombre)
                
                items_serializables = []
                for item in items:
                    items_serializables.append({
                        'id_producto': item.id_producto,
                        'nombre_producto': item.nombre_producto,
                        'cantidad': float(item.cantidad),
                        'unidad': item.unidad,
                        'precio_unitario': float(item.precio_unitario),
                        'subtotal': float(item.subtotal)
                    })
                
                secciones_data[seccion_nombre] = items_serializables
            
            return {
                'secciones': secciones_data,
                'total': float(carrito.calcular_total())
            }
            
        except Exception as e:
            print(f"❌ Error serializando carrito: {e}")
            import traceback
            traceback.print_exc()
            return {'secciones': {}, 'total': 0}