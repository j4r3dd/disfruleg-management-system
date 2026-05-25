# database.py - VERSIÓN ACTUALIZADA PARA CLOUD SQL CONNECTOR
# Compatible con src/database/conexion.py (Cloud SQL + pymysql)
# REEMPLAZAR COMPLETAMENTE tu archivo actual

import json
from datetime import date
from typing import List, Dict, Any, Optional
from decimal import Decimal

# ==================== IMPORTAR CONEXIÓN DEL SISTEMA PRINCIPAL ====================
from src.database.conexion import conectar, return_connection

def _dict_or_tuple(row, keys):
    """Convierte resultado de cursor a dict de manera segura."""
    if row is None:
        return {}
    if isinstance(row, dict):
        return row
    elif isinstance(row, (tuple, list)):
        return dict(zip(keys, row))
    else:
        return {}

# ==================== FUNCIONES DE GRUPOS Y CLIENTES ====================

def obtener_grupos():
    """Obtiene todos los grupos de clientes."""
    conn = conectar()
    if not conn:
        return []

    grupos = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_grupo, clave_grupo FROM grupo ORDER BY clave_grupo")
            resultados = cursor.fetchall()

            for row in resultados:
                grupo_dict = _dict_or_tuple(row, ['id_grupo', 'clave_grupo'])
                grupos.append(grupo_dict)
    except Exception as e:
        print(f"❌ Error al obtener grupos: {e}")
    finally:
        return_connection(conn)

    return grupos

def obtener_clientes_por_grupo(id_grupo):
    """Obtiene clientes de un grupo específico."""
    conn = conectar()
    if not conn:
        return []

    clientes = []
    try:
        with conn.cursor() as cursor:
            query = "SELECT id_cliente, nombre_cliente FROM cliente WHERE id_grupo = %s ORDER BY nombre_cliente"
            cursor.execute(query, (id_grupo,))
            resultados = cursor.fetchall()

            for row in resultados:
                cliente_dict = _dict_or_tuple(row, ['id_cliente', 'nombre_cliente'])
                cliente_dict['nombre_completo'] = cliente_dict.get('nombre_cliente', '')
                clientes.append(cliente_dict)
    except Exception as e:
        print(f"❌ Error al obtener clientes: {e}")
    finally:
        return_connection(conn)

    return clientes


def obtener_cliente_por_id(id_cliente):
    """Obtiene la información completa de un cliente por su ID."""
    conn = conectar()
    if not conn:
        return None

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT c.id_cliente, c.nombre_cliente, c.id_grupo, g.clave_grupo
                FROM cliente c
                LEFT JOIN grupo g ON c.id_grupo = g.id_grupo
                WHERE c.id_cliente = %s
            """
            cursor.execute(query, (id_cliente,))
            row = cursor.fetchone()

            if row:
                cliente_dict = _dict_or_tuple(row, ['id_cliente', 'nombre_cliente', 'id_grupo', 'clave_grupo'])
                cliente_dict['nombre_completo'] = cliente_dict.get('nombre_cliente', '')
                return cliente_dict
            return None
    except Exception as e:
        print(f"❌ Error al obtener cliente por ID: {e}")
        return None
    finally:
        return_connection(conn)

# ==================== FUNCIONES DE PRODUCTOS ====================

def obtener_productos_con_precios(id_grupo: int, solo_activos: bool = True) -> List[Dict[str, Any]]:
    """Obtiene productos con sus precios para un grupo específico."""
    conn = conectar()
    if not conn:
        return []
    
    productos = []
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    p.id_producto,
                    p.nombre_producto,
                    p.unidad_producto as unidad,
                    COALESCE(ppg.precio_base, 0) as precio,
                    p.stock
                FROM producto p
                LEFT JOIN precio_por_grupo ppg 
                    ON p.id_producto = ppg.id_producto 
                    AND ppg.id_grupo = %s
                WHERE 1=1
            """
            
            params = [id_grupo]
            
            if solo_activos:
                query += " AND p.stock > 0"
            
            query += " ORDER BY p.nombre_producto"
            
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            if not resultados:
                print(f"⚠️ No se encontraron productos para el grupo {id_grupo}")
                return []
            
            for row in resultados:
                prod_dict = _dict_or_tuple(row, 
                    ['id_producto', 'nombre_producto', 'unidad', 'precio', 'stock'])
                
                prod_dict['precio'] = float(prod_dict['precio']) if prod_dict['precio'] else 0.0
                prod_dict['stock'] = int(prod_dict['stock']) if prod_dict['stock'] else 0
                
                productos.append(prod_dict)
            
            print(f"✅ Se encontraron {len(productos)} productos para el grupo {id_grupo}")
    except Exception as e:
        print(f"❌ Error en obtener_productos_con_precios: {e}")
        import traceback
        traceback.print_exc()
    finally:
        return_connection(conn)

    return productos

def buscar_insumos(query, id_grupo):
    """Busca productos en la base de datos para un grupo específico."""
    conn = conectar()
    if not conn:
        return []
    
    resultados = []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    p.id_producto as id,
                    p.nombre_producto as nombre, 
                    COALESCE(ppg.precio_base, 0) as precio,
                    p.unidad_producto as unidad,
                    p.es_especial
                FROM producto p
                LEFT JOIN precio_por_grupo ppg 
                    ON p.id_producto = ppg.id_producto 
                    AND ppg.id_grupo = %s
                WHERE p.nombre_producto LIKE %s 
                AND p.stock > 0
                ORDER BY p.nombre_producto
            """
            cursor.execute(sql, (id_grupo, f"%{query}%"))
            rows = cursor.fetchall()
            
            for row in rows:
                prod_dict = _dict_or_tuple(row, ['id', 'nombre', 'precio', 'unidad', 'es_especial'])
                prod_dict['precio'] = float(prod_dict['precio']) if prod_dict['precio'] else 0.0
                resultados.append(prod_dict)
    except Exception as e:
        print(f"❌ Error al buscar insumos: {e}")
    finally:
        return_connection(conn)

    return resultados

def buscar_todos_insumos(id_grupo):
    """Obtiene todos los productos para un grupo específico."""
    conn = conectar()
    if not conn:
        return []
    
    resultados = []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    p.id_producto as id,
                    p.nombre_producto as nombre, 
                    COALESCE(ppg.precio_base, 0) as precio,
                    p.unidad_producto as unidad,
                    p.es_especial
                FROM producto p
                LEFT JOIN precio_por_grupo ppg 
                    ON p.id_producto = ppg.id_producto 
                    AND ppg.id_grupo = %s
                WHERE p.stock > 0
                ORDER BY p.nombre_producto
            """
            cursor.execute(sql, (id_grupo,))
            rows = cursor.fetchall()
            
            for row in rows:
                prod_dict = _dict_or_tuple(row, ['id', 'nombre', 'precio', 'unidad', 'es_especial'])
                prod_dict['precio'] = float(prod_dict['precio']) if prod_dict['precio'] else 0.0
                resultados.append(prod_dict)
    except Exception as e:
        print(f"❌ Error al buscar todos los insumos: {e}")
    finally:
        return_connection(conn)
    
    return resultados

# ==================== FUNCIONES DE FOLIOS ====================

def obtener_siguiente_folio():
    """Obtiene el siguiente número de folio disponible desde folio_sequence."""
    conn = conectar()
    if not conn:
        return None
    
    siguiente_folio = None
    try:
        conn.begin()
        
        with conn.cursor() as cursor:
            query = "SELECT next_val FROM folio_sequence WHERE id = 1 FOR UPDATE"
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                resultado_dict = _dict_or_tuple(resultado, ['next_val'])
                siguiente_folio = resultado_dict['next_val']
                
                update_query = "UPDATE folio_sequence SET next_val = next_val + 1 WHERE id = 1"
                cursor.execute(update_query)
            else:
                insert_query = "INSERT INTO folio_sequence (id, next_val) VALUES (1, 1)"
                cursor.execute(insert_query)
                siguiente_folio = 1
        
        conn.commit()
    except Exception as e:
        print(f"❌ Error al obtener siguiente folio: {e}")
        conn.rollback()
    finally:
        return_connection(conn)
    
    return siguiente_folio

def verificar_folio_disponible(folio):
    """Verifica si un folio está disponible para usar."""
    conn = conectar()
    if not conn:
        return False
    
    disponible = True
    try:
        with conn.cursor() as cursor:
            # Verificar en órdenes guardadas
            query_orden = "SELECT 1 FROM ordenes_guardadas WHERE folio_numero = %s AND activo = TRUE"
            cursor.execute(query_orden, (folio,))
            if cursor.fetchone():
                disponible = False
            
            # Verificar en facturas
            if disponible:
                query_factura = "SELECT 1 FROM factura WHERE folio_numero = %s"
                cursor.execute(query_factura, (folio,))
                if cursor.fetchone():
                    disponible = False
    except Exception as e:
        print(f"❌ Error al verificar folio: {e}")
        disponible = False
    finally:
        return_connection(conn)
    
    return disponible

# ==================== FUNCIONES DE FACTURACIÓN ====================

def crear_factura_completa(id_cliente: int, items_orden: List[Dict[str, Any]], 
                           fecha_venta: date, folio_numero: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Registra la factura y sus detalles en la BD de forma transaccional.
    
    Args:
        id_cliente: ID del cliente
        items_orden: Lista de items con formato dict:
            {
                'id_producto': int,
                'cantidad': float,
                'precio_unitario': float,
                'nombre_producto': str,
                'unidad': str,
                'seccion_id': str or None
            }
        fecha_venta: Fecha de la venta
        folio_numero: Folio específico (opcional, para órdenes guardadas)
        
    Returns:
        Dict con {'success': bool, 'id_factura': int, 'total': float, 'folio': int}
    """
    conn = conectar()
    if not conn:
        return None
    
    try:
        print("=" * 60)
        print("INICIANDO TRANSACCIÓN DE FACTURA")
        print(f"Cliente ID: {id_cliente}")
        print(f"Fecha: {fecha_venta}")
        print(f"Folio específico: {folio_numero}")
        print(f"Total items: {len(items_orden)}")
        print("=" * 60)
        
        conn.begin()
        
        with conn.cursor() as cursor:
            # 1. Obtener siguiente ID de factura
            query_seq = "SELECT next_val FROM factura_sequence WHERE id = 1 FOR UPDATE"
            cursor.execute(query_seq)
            resultado_seq = cursor.fetchone()
            
            if not resultado_seq:
                cursor.execute("INSERT INTO factura_sequence (id, next_val) VALUES (1, 1)")
                id_factura = 1
            else:
                resultado_dict = _dict_or_tuple(resultado_seq, ['next_val'])
                id_factura = resultado_dict['next_val']

            # 2. Calcular total y preparar items
            total_factura = 0.0
            items_procesados = []
            
            for item in items_orden:
                cantidad = float(item.get('cantidad', 0))
                precio_unitario = float(item.get('precio_unitario', 0))
                subtotal = cantidad * precio_unitario
                total_factura += subtotal
                
                items_procesados.append({
                    'id_producto': item['id_producto'],
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal,
                    'nombre_producto': item.get('nombre_producto', ''),
                    'unidad': item.get('unidad', 'unidad'),
                    'seccion_id': item.get('seccion_id')
                })
                
                print(f"  - {item.get('nombre_producto')}: {cantidad} x ${precio_unitario:.2f} = ${subtotal:.2f}")

            print(f"TOTAL CALCULADO: ${total_factura:.2f}")

            # 3. Determinar folio a usar
            if folio_numero is None:
                folio_numero = obtener_siguiente_folio()
                if folio_numero is None:
                    raise Exception("No se pudo obtener folio")
            
            print(f"FOLIO ASIGNADO: {folio_numero}")

            # 4. Insertar factura
            query_factura = """
                INSERT INTO factura (id_factura, fecha_factura, id_cliente, folio_numero)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_factura, (id_factura, fecha_venta, id_cliente, folio_numero))
            print(f"✅ Factura insertada: ID={id_factura}, Folio={folio_numero}")

            # 5. Insertar detalles de factura y actualizar stock
            query_detalle = """
                INSERT INTO detalle_factura 
                (id_factura, id_producto, cantidad_factura, precio_unitario_venta)
                VALUES (%s, %s, %s, %s)
            """
            
            query_stock = "UPDATE producto SET stock = stock - %s WHERE id_producto = %s"

            for item in items_procesados:
                cursor.execute(query_detalle, (
                    id_factura, 
                    item['id_producto'], 
                    item['cantidad'], 
                    item['precio_unitario']
                ))
                
                cursor.execute(query_stock, (item['cantidad'], item['id_producto']))
            
            print(f"✅ {len(items_procesados)} items procesados")

            # 6. Crear deuda automáticamente - UPDATED to use 'deudas' table
            # First get client and group names
            query_cliente_info = """
                SELECT c.nombre_cliente, g.clave_grupo
                FROM cliente c
                LEFT JOIN grupo g ON c.id_grupo = g.id_grupo
                WHERE c.id_cliente = %s
            """
            cursor.execute(query_cliente_info, (id_cliente,))
            cliente_info = cursor.fetchone()

            nombre_cliente = cliente_info['nombre_cliente'] if isinstance(cliente_info, dict) else cliente_info[0] if cliente_info else 'Cliente Desconocido'
            nombre_grupo = (cliente_info['clave_grupo'] if isinstance(cliente_info, dict) else cliente_info[1]) if cliente_info else 'Sin grupo'

            query_deuda = """
                INSERT INTO deudas
                (id_cliente, id_factura, nombre_cliente, nombre_grupo, monto_total, monto_pagado,
                 fecha_generada, pagado, descripcion, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, 0.00, %s, 0, %s, NOW(), NOW())
            """
            descripcion = f"Factura #{id_factura} - Folio {folio_numero}"
            cursor.execute(query_deuda, (
                id_cliente,
                str(id_factura),  # Convert to string for VARCHAR(50) column
                nombre_cliente,
                nombre_grupo,
                total_factura,
                fecha_venta,
                descripcion
            ))
            print(f"✅ Deuda creada: ${total_factura:.2f}")
                
            # 7. Actualizar secuencia de factura
            update_seq = "UPDATE factura_sequence SET next_val = next_val + 1 WHERE id = 1"
            cursor.execute(update_seq)
            
            # 8. Si hay folio de orden, marcar como completada
            # FIXED: Also update total_estimado to match actual invoice total
            if folio_numero:
                try:
                    query_orden = """
                        UPDATE ordenes_guardadas
                        SET estado = 'registrada',
                            total_estimado = %s,
                            fecha_modificacion = NOW()
                        WHERE folio_numero = %s AND estado = 'guardada'
                    """
                    cursor.execute(query_orden, (total_factura, folio_numero))
                    if cursor.rowcount > 0:
                        print(f"✅ Orden {folio_numero} marcada como registrada (Total: ${total_factura:.2f})")
                except Exception as e:
                    print(f"⚠️ Advertencia: No se pudo marcar orden como registrada: {e}")
        
        # 9. Confirmar transacción
        conn.commit()
        
        print("=" * 60)
        print(f"✅ FACTURA COMPLETADA EXITOSAMENTE")
        print(f"ID Factura: {id_factura}")
        print(f"Folio: {folio_numero}")
        print(f"Total: ${total_factura:.2f}")
        print("=" * 60)
        
        return {
            "success": True, 
            "id_factura": id_factura, 
            "total": total_factura, 
            "folio": folio_numero
        }

    except Exception as e:
        print(f"❌ Error en transacción al crear factura: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return None
    finally:
        return_connection(conn)

# ==================== FUNCIONES DE ÓRDENES GUARDADAS ====================

def guardar_orden(folio, id_cliente, usuario, datos_carrito, total_estimado):
    """Guarda una orden en la tabla ordenes_guardadas."""
    conn = conectar()
    if not conn:
        return False
    
    exito = False
    try:
        with conn.cursor() as cursor:
            if isinstance(datos_carrito, dict):
                datos_carrito_json = json.dumps(datos_carrito, ensure_ascii=False)
            else:
                datos_carrito_json = datos_carrito
                
            query = """
                INSERT INTO ordenes_guardadas 
                (folio_numero, id_cliente, usuario_creador, datos_carrito, total_estimado, estado)
                VALUES (%s, %s, %s, %s, %s, 'guardada')
            """
            cursor.execute(query, (folio, id_cliente, usuario, datos_carrito_json, total_estimado))
        
        conn.commit()
        exito = True
    except Exception as e:
        print(f"❌ Error al guardar orden: {e}")
        conn.rollback()
    finally:
        return_connection(conn)
    
    return exito

def cargar_orden(folio):
    """Carga una orden guardada desde la base de datos."""
    conn = conectar()
    if not conn:
        return None
    
    orden = None
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    og.folio_numero, 
                    og.id_cliente, 
                    c.nombre_cliente,
                    og.usuario_creador,
                    og.datos_carrito,
                    og.total_estimado,
                    og.estado,
                    og.fecha_creacion
                FROM ordenes_guardadas og
                JOIN cliente c ON og.id_cliente = c.id_cliente
                WHERE og.folio_numero = %s AND og.activo = TRUE
            """
            cursor.execute(query, (folio,))
            resultado = cursor.fetchone()
            
            if resultado:
                orden = _dict_or_tuple(resultado, [
                    'folio_numero', 'id_cliente', 'nombre_cliente', 
                    'usuario_creador', 'datos_carrito', 'total_estimado', 
                    'estado', 'fecha_creacion'
                ])
                
                try:
                    datos_carrito = json.loads(orden['datos_carrito'])
                    orden['datos_carrito_obj'] = datos_carrito
                except json.JSONDecodeError as e:
                    print(f"❌ Error al deserializar carrito del folio {folio}: {e}")
                    orden['datos_carrito_obj'] = None
    except Exception as e:
        print(f"❌ Error al cargar orden: {e}")
    finally:
        return_connection(conn)
    
    return orden

def actualizar_orden(folio, datos_carrito, total_estimado):
    """Actualiza una orden existente."""
    conn = conectar()
    if not conn:
        return False
    
    exito = False
    try:
        with conn.cursor() as cursor:
            if isinstance(datos_carrito, dict):
                datos_carrito_json = json.dumps(datos_carrito, ensure_ascii=False)
            else:
                datos_carrito_json = datos_carrito
                
            query = """
                UPDATE ordenes_guardadas 
                SET datos_carrito = %s, total_estimado = %s, fecha_modificacion = NOW()
                WHERE folio_numero = %s AND estado = 'guardada'
            """
            cursor.execute(query, (datos_carrito_json, total_estimado, folio))
            exito = cursor.rowcount > 0
        
        conn.commit()
    except Exception as e:
        print(f"❌ Error al actualizar orden: {e}")
        conn.rollback()
    finally:
        return_connection(conn)
    
    return exito

def marcar_orden_como_completada(folio, id_factura):
    """Marca una orden como completada y la relaciona con una factura."""
    conn = conectar()
    if not conn:
        return False
    
    exito = False
    try:
        with conn.cursor() as cursor:
            query = """
                UPDATE ordenes_guardadas 
                SET estado = 'registrada', fecha_modificacion = NOW()
                WHERE folio_numero = %s AND estado = 'guardada'
            """
            cursor.execute(query, (folio,))
            exito = cursor.rowcount > 0
        
        conn.commit()
    except Exception as e:
        print(f"❌ Error al marcar orden como completada: {e}")
        conn.rollback()
    finally:
        return_connection(conn)
    
    return exito

# ==================== BLOQUE DE PRUEBA ====================

if __name__ == '__main__':
    import sys
    import os
    
    # Agregar la raíz del proyecto al path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    print("--- Probando funciones del database.py ---")
    
    # Probar conexión
    conn = conectar()
    if conn:
        print("✅ Conexión exitosa a la base de datos")
        return_connection(conn)
    else:
        print("❌ Error de conexión")
    
    # Probar obtención de grupos
    print("\n📋 Obteniendo grupos:")
    grupos = obtener_grupos()
    if grupos:
        print(f"✅ Grupos encontrados: {grupos}")
        
        id_grupo_prueba = grupos[0]['id_grupo']
        
        print(f"\n👥 Obteniendo clientes del grupo ID {id_grupo_prueba}:")
        clientes = obtener_clientes_por_grupo(id_grupo_prueba)
        print(f"✅ Clientes encontrados: {len(clientes)}")

        print(f"\n�' Buscando productos para el grupo ID {id_grupo_prueba}:")
        productos = obtener_productos_con_precios(id_grupo_prueba, solo_activos=True)
        print(f"✅ Productos encontrados: {len(productos)}")
    else:
        print("⚠️ No se encontraron grupos. Asegúrate de tener datos en la BD.")