# -*- coding: utf-8 -*-
"""
Database Module - Backwards Compatibility Wrapper
Uses new repository pattern internally while maintaining legacy function signatures

REFACTORED: Now uses ConnectionPool and Repository pattern
Original functions preserved for backwards compatibility
Legacy version backed up as database_legacy.py
"""

import json
from datetime import date
from typing import List, Dict, Any, Optional
from decimal import Decimal

# Import new repositories
from src.modules.receipts.database.repositories.orden_repository import OrdenRepository
from src.modules.receipts.database.repositories.product_repository import ProductRepository
from src.modules.receipts.database.repositories.client_repository import ClientRepository

# For functions not yet refactored, import from legacy
from src.database.conexion import conectar

# ==================== REPOSITORY SINGLETONS ====================

_orden_repo = None
_product_repo = None
_client_repo = None


def _get_orden_repo() -> OrdenRepository:
    """Get singleton OrdenRepository instance"""
    global _orden_repo
    if _orden_repo is None:
        _orden_repo = OrdenRepository()
    return _orden_repo


def _get_product_repo() -> ProductRepository:
    """Get singleton ProductRepository instance"""
    global _product_repo
    if _product_repo is None:
        _product_repo = ProductRepository()
    return _product_repo


def _get_client_repo() -> ClientRepository:
    """Get singleton ClientRepository instance"""
    global _client_repo
    if _client_repo is None:
        _client_repo = ClientRepository()
    return _client_repo


# ==================== HELPER FUNCTIONS ====================

def _dict_or_tuple(row, keys):
    """
    LEGACY: Convierte resultado de cursor a dict de manera segura.
    Kept for backwards compatibility with non-refactored code.
    """
    if row is None:
        return {}
    if isinstance(row, dict):
        return row
    elif isinstance(row, (tuple, list)):
        return dict(zip(keys, row))
    else:
        return {}


# ==================== GRUPOS Y CLIENTES (REFACTORED) ====================

def obtener_grupos():
    """
    Obtiene todos los grupos de clientes.
    REFACTORED: Now uses ClientRepository
    """
    try:
        repo = _get_client_repo()
        return repo.get_all_groups()
    except Exception as e:
        print(f"❌ Error al obtener grupos: {e}")
        return []


def obtener_clientes_por_grupo(id_grupo):
    """
    Obtiene clientes de un grupo específico.
    REFACTORED: Now uses ClientRepository
    """
    try:
        repo = _get_client_repo()
        clientes = repo.get_clients_by_group(id_grupo)

        # Add nombre_completo for backwards compatibility
        for cliente in clientes:
            if 'nombre_completo' not in cliente:
                cliente['nombre_completo'] = cliente.get('nombre_cliente', '')

        return clientes
    except Exception as e:
        print(f"❌ Error al obtener clientes: {e}")
        return []


def obtener_cliente_por_id(id_cliente):
    """
    Obtiene la información completa de un cliente por su ID.
    REFACTORED: Now uses ClientRepository
    """
    try:
        repo = _get_client_repo()
        cliente = repo.get_client_by_id(id_cliente)

        if cliente:
            # Add nombre_completo for backwards compatibility
            cliente['nombre_completo'] = cliente.get('nombre_cliente', '')

        return cliente
    except Exception as e:
        print(f"❌ Error al obtener cliente por ID: {e}")
        return None


# ==================== PRODUCTOS (REFACTORED) ====================

def obtener_productos_con_precios(id_grupo: int, solo_activos: bool = True) -> List[Dict[str, Any]]:
    """
    Obtiene productos con sus precios para un grupo específico.
    REFACTORED: Now uses ProductRepository
    """
    try:
        repo = _get_product_repo()
        productos = repo.get_products_with_prices(id_grupo, solo_activos)

        # Convert types for backwards compatibility
        for prod in productos:
            prod['precio'] = float(prod['precio']) if prod['precio'] else 0.0
            prod['stock'] = int(prod['stock']) if prod['stock'] else 0

        if not productos:
            print(f"⚠️ No se encontraron productos para el grupo {id_grupo}")
        else:
            print(f"✅ Se encontraron {len(productos)} productos para el grupo {id_grupo}")

        return productos
    except Exception as e:
        print(f"❌ Error en obtener_productos_con_precios: {e}")
        import traceback
        traceback.print_exc()
        return []


def buscar_insumos(query, id_grupo):
    """
    Busca productos en la base de datos para un grupo específico.
    REFACTORED: Now uses ProductRepository
    """
    try:
        repo = _get_product_repo()
        productos = repo.search_products(id_grupo, query)

        # Convert to legacy format
        resultados = []
        for prod in productos:
            prod_dict = {
                'id': prod.get('id_producto'),
                'nombre': prod.get('nombre_producto'),
                'precio': float(prod.get('precio', 0)),
                'unidad': prod.get('unidad'),
                'es_especial': prod.get('es_especial', False)
            }
            resultados.append(prod_dict)

        return resultados
    except Exception as e:
        print(f"❌ Error al buscar insumos: {e}")
        return []


def buscar_todos_insumos(id_grupo):
    """
    Obtiene todos los productos para un grupo específico.
    REFACTORED: Alias for obtener_productos_con_precios
    """
    return obtener_productos_con_precios(id_grupo, solo_activos=True)


# ==================== ÓRDENES (REFACTORED) ====================

def guardar_orden(folio, id_cliente, usuario, datos_carrito, total_estimado):
    """
    Guarda una orden en la tabla ordenes_guardadas.
    REFACTORED: Now uses OrdenRepository
    """
    try:
        repo = _get_orden_repo()
        success = repo.create_order(
            folio=folio,
            id_cliente=id_cliente,
            usuario=usuario,
            datos_carrito=datos_carrito,
            total=total_estimado
        )

        if success:
            print(f"✅ Orden {folio} guardada exitosamente")
        else:
            print(f"❌ No se pudo guardar la orden {folio}")

        return success
    except Exception as e:
        print(f"❌ Error al guardar orden: {e}")
        import traceback
        traceback.print_exc()
        return False


def cargar_orden(folio):
    """
    Carga una orden guardada desde la base de datos.
    REFACTORED: Now uses OrdenRepository
    """
    try:
        repo = _get_orden_repo()
        orden = repo.find_by_folio(folio)

        if orden:
            print(f"✅ Orden {folio} cargada exitosamente")
        else:
            print(f"⚠️ No se encontró orden con folio {folio}")

        return orden
    except Exception as e:
        print(f"❌ Error al cargar orden: {e}")
        import traceback
        traceback.print_exc()
        return None


def actualizar_orden(folio, datos_carrito, total_estimado):
    """
    Actualiza una orden existente en la base de datos.
    REFACTORED: Now uses OrdenRepository
    """
    try:
        repo = _get_orden_repo()
        success = repo.update_order(
            folio=folio,
            datos_carrito=datos_carrito,
            total=total_estimado
        )

        if success:
            print(f"✅ Orden {folio} actualizada exitosamente")
        else:
            print(f"❌ No se pudo actualizar la orden {folio}")

        return success
    except Exception as e:
        print(f"❌ Error al actualizar orden: {e}")
        import traceback
        traceback.print_exc()
        return False


def marcar_orden_como_completada(folio, id_factura=None):
    """
    Marca una orden como registrada cuando se completa la venta.
    REFACTORED: Now uses OrdenRepository

    Args:
        folio: Número de folio de la orden
        id_factura: ID de la factura asociada (opcional, no usado en nueva versión)
    """
    try:
        repo = _get_orden_repo()
        success = repo.mark_as_registered(folio)

        if success:
            print(f"✅ Orden {folio} marcada como completada")
        else:
            print(f"❌ No se pudo marcar orden {folio} como completada")

        return success
    except Exception as e:
        print(f"❌ Error al marcar orden como completada: {e}")
        return False


# ==================== FOLIOS (NOT REFACTORED YET) ====================

def obtener_siguiente_folio():
    """
    Obtiene el siguiente folio disponible.
    TODO: Refactor to use FolioRepository
    """
    conn = conectar()
    if not conn:
        print("❌ Error: No se pudo conectar a la base de datos")
        return None

    try:
        with conn.cursor() as cursor:
            # Usar tabla folio_sequence
            query = "SELECT next_val FROM folio_sequence WHERE id = 1 FOR UPDATE"
            cursor.execute(query)
            resultado = cursor.fetchone()

            if resultado:
                siguiente_folio = resultado['next_val'] if isinstance(resultado, dict) else resultado[0]

                # Actualizar el siguiente valor
                update_query = "UPDATE folio_sequence SET next_val = next_val + 1 WHERE id = 1"
                cursor.execute(update_query)
                conn.commit()

                print(f"✅ Siguiente folio disponible: {siguiente_folio}")
                return siguiente_folio
            else:
                # Inicializar la secuencia si no existe
                insert_query = "INSERT INTO folio_sequence (id, next_val) VALUES (1, 1)"
                cursor.execute(insert_query)
                conn.commit()
                siguiente_folio = 1
                print(f"✅ Inicializado folio_sequence, primer folio: {siguiente_folio}")
                return siguiente_folio
    except Exception as e:
        print(f"❌ Error al obtener siguiente folio: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def verificar_folio_disponible(folio):
    """
    Verifica si un folio específico está disponible.
    TODO: Refactor to use FolioRepository
    """
    conn = conectar()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            # Verificar en órdenes guardadas
            query_orden = "SELECT 1 FROM ordenes_guardadas WHERE folio_numero = %s AND activo = TRUE"
            cursor.execute(query_orden, (folio,))
            if cursor.fetchone():
                return False

            # Verificar en facturas
            query_factura = "SELECT 1 FROM factura WHERE folio_numero = %s"
            cursor.execute(query_factura, (folio,))
            if cursor.fetchone():
                return False

            return True
    except Exception as e:
        print(f"❌ Error al verificar folio: {e}")
        return False
    finally:
        conn.close()


# ==================== FACTURAS (NOT REFACTORED YET) ====================

def crear_factura_completa(id_cliente: int, items_orden: List[Dict[str, Any]],
                          fecha_compra: str, fecha_registro: str = None,
                          folio_numero: int = None) -> Optional[Dict[str, Any]]:
    """
    Crea una factura completa con sus detalles y actualiza el stock de productos.
    TODO: Refactor to use FacturaRepository

    Args:
        fecha_compra: Used as fecha_factura
        fecha_registro: Deprecated, kept for compatibility

    Returns:
        Dict with 'id_factura' and 'folio_numero' or None if error
    """
    conn = conectar()
    if not conn:
        print("❌ Error: No se pudo conectar a la base de datos")
        return None

    id_factura = None

    try:
        with conn.cursor() as cursor:
            # 1. Obtener siguiente folio si no se proporciona
            if folio_numero is None:
                cursor.execute("SELECT next_val FROM folio_sequence WHERE id = 1 FOR UPDATE")
                resultado = cursor.fetchone()
                if resultado:
                    folio_numero = resultado['next_val'] if isinstance(resultado, dict) else resultado[0]
                    cursor.execute("UPDATE folio_sequence SET next_val = next_val + 1 WHERE id = 1")
                else:
                    cursor.execute("INSERT INTO folio_sequence (id, next_val) VALUES (1, 2)")
                    folio_numero = 1

            # 2. Insertar factura (without total - not in schema)
            query_factura = """
                INSERT INTO factura
                (id_cliente, fecha_factura, folio_numero)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_factura, (id_cliente, fecha_compra, folio_numero))
            id_factura = cursor.lastrowid

            # 4. Insertar detalles y actualizar stock
            query_detalle = """
                INSERT INTO detalle_factura
                (id_factura, id_producto, cantidad_factura, precio_unitario_venta)
                VALUES (%s, %s, %s, %s)
            """

            total_factura = 0.0
            for item in items_orden:
                cantidad = float(item['cantidad'])
                precio_unitario = float(item['precio_unitario'])

                cursor.execute(query_detalle, (
                    id_factura,
                    item['id_producto'],
                    cantidad,
                    precio_unitario
                ))

                # Calcular total
                total_factura += cantidad * precio_unitario

                # Actualizar stock
                query_stock = """
                    UPDATE producto
                    SET stock = stock - %s
                    WHERE id_producto = %s
                """
                cursor.execute(query_stock, (cantidad, item['id_producto']))

            # 4.5. Crear registro de deuda - UPDATED to use 'deudas' table
            # First get client and group names for the deudas table
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
            descripcion_deuda = f"Deuda generada por factura #{folio_numero}"
            cursor.execute(query_deuda, (
                id_cliente,
                str(id_factura),  # Convert to string for VARCHAR(50) column
                nombre_cliente,
                nombre_grupo,
                total_factura,
                fecha_compra,
                descripcion_deuda
            ))
            print(f"✅ Deuda creada para factura {folio_numero}: ${total_factura:.2f}")

            # 5. Marcar orden como registrada si existe folio
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

            # Commit de la transacción
            conn.commit()
            print(f"✅ Factura creada exitosamente. ID: {id_factura}, Folio: {folio_numero}")

            return {
                'id_factura': id_factura,
                'folio_numero': folio_numero
            }

    except Exception as e:
        conn.rollback()
        print(f"❌ Error al crear factura: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        conn.close()


# ==================== EXPORTS ====================

__all__ = [
    # Client functions (REFACTORED)
    'obtener_grupos',
    'obtener_clientes_por_grupo',
    'obtener_cliente_por_id',

    # Product functions (REFACTORED)
    'obtener_productos_con_precios',
    'buscar_insumos',
    'buscar_todos_insumos',

    # Order functions (REFACTORED)
    'guardar_orden',
    'cargar_orden',
    'actualizar_orden',
    'marcar_orden_como_completada',

    # Folio functions (TODO: Refactor)
    'obtener_siguiente_folio',
    'verificar_folio_disponible',

    # Invoice functions (TODO: Refactor)
    'crear_factura_completa',
]
