# -*- coding: utf-8 -*-
"""
DISFRULEG - Debt Manager Module

Gestor de deudas independiente que utiliza las vistas SQL existentes
para el control y seguimiento de cuentas por cobrar.
"""

from mysql.connector import Error
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional
from src.database.conexion import conectar
from src.config import debug_print

class DebtManager:
    """
    Gestor centralizado para el manejo de deudas y cuentas por cobrar.
    
    Utiliza las vistas SQL existentes:
    - vista_estado_cuenta_cliente: Para obtener resumen de deudas por cliente
    - vista_deudas_detalladas: Para detalles especificos de cada deuda
    - vista_historial_pagos: Para historial de pagos realizados
    """
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def _get_connection(self):
        """Obtiene conexion a la base de datos"""
        try:
            if not self.connection:
                self.connection = conectar()
                import pymysql.cursors
                self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            return self.connection
        except Error as e:
            debug_print(f"Error connecting to database: {e}")
            raise
    
    def _close_connection(self):
        """Cierra la conexion si esta activa"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        self.connection = None
        self.cursor = None
    
    def obtener_clientes_con_deudas(self) -> List[Dict]:
        """
        Obtiene todos los clientes que tienen deudas pendientes.
        
        Returns:
            List[Dict]: Lista de clientes con saldo pendiente > 0
        """
        try:
            self._get_connection()
            
            query = """
            SELECT 
                id_cliente,
                nombre_cliente,
                clave_grupo,
                tipo_cliente,
                saldo_pendiente,
                total_deuda_pendiente,
                total_deuda_pagada,
                deudas_pendientes,
                deudas_pagadas,
                ultima_deuda_generada,
                ultimo_pago,
                estado_cuenta
            FROM vista_estado_cuenta_cliente 
            WHERE saldo_pendiente > 0
            ORDER BY saldo_pendiente DESC
            """
            
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            
            debug_print(f"Clientes con deudas encontrados: {len(result)}")
            return result
            
        except Error as e:
            debug_print(f"Error obteniendo clientes con deudas: {e}")
            raise
        finally:
            self._close_connection()
    
    def obtener_deudas_cliente(self, id_cliente: int) -> List[Dict]:
        """
        Obtiene todas las deudas de un cliente especifico.
        
        Args:
            id_cliente (int): ID del cliente
            
        Returns:
            List[Dict]: Lista de deudas del cliente
        """
        try:
            self._get_connection()
            
            query = """
            SELECT 
                id_deuda,
                id_cliente,
                nombre_cliente,
                id_factura,
                fecha_factura,
                monto_total,
                monto_pagado,
                saldo_pendiente,
                fecha_generada,
                fecha_pago,
                estado_deuda,
                clave_grupo,
                tipo_cliente
            FROM vista_deudas_detalladas 
            WHERE id_cliente = %s
            ORDER BY fecha_generada DESC
            """
            
            self.cursor.execute(query, (id_cliente,))
            result = self.cursor.fetchall()
            
            debug_print(f"Deudas encontradas para cliente {id_cliente}: {len(result)}")
            return result
            
        except Error as e:
            debug_print(f"Error obteniendo deudas del cliente {id_cliente}: {e}")
            raise
        finally:
            self._close_connection()
    
    def obtener_deuda_por_id(self, id_deuda: int) -> Optional[Dict]:
        """
        Obtiene una deuda especifica por su ID.
        
        Args:
            id_deuda (int): ID de la deuda
            
        Returns:
            Optional[Dict]: Datos de la deuda o None si no existe
        """
        try:
            self._get_connection()
            
            query = """
            SELECT
                d.id_deuda,
                vdd.id_cliente,
                vdd.nombre_cliente,
                vdd.id_factura,
                vdd.fecha_factura,
                vdd.monto_total,
                vdd.monto_pagado,
                vdd.saldo_pendiente,
                vdd.fecha_generada,
                vdd.fecha_pago,
                vdd.estado_deuda,
                vdd.clave_grupo,
                vdd.tipo_cliente,
                d.imagen_comprobante,
                d.nombre_imagen,
                d.metodo_pago,
                d.referencia_pago
            FROM vista_deudas_detalladas vdd
            JOIN deuda d ON vdd.id_deuda = d.id_deuda
            WHERE vdd.id_deuda = %s
            """
            
            self.cursor.execute(query, (id_deuda,))
            result = self.cursor.fetchone()
            
            return result
            
        except Error as e:
            debug_print(f"Error obteniendo deuda {id_deuda}: {e}")
            raise
        finally:
            self._close_connection()
    
    def registrar_pago(self, id_deuda: int, monto_pago: Decimal, metodo_pago: str,
                      referencia_pago: str = None, usuario: str = None, imagen_comprobante: bytes = None, nombre_imagen: str = None) -> int:
        """
        Registra un pago para una deuda especifica.

        Args:
            id_deuda (int): ID de la deuda
            monto_pago (Decimal): Monto del pago
            metodo_pago (str): Metodo de pago (efectivo, transferencia, etc.)
            referencia_pago (str, optional): Referencia del pago
            usuario (str, optional): Usuario que registra el pago
            imagen_comprobante (bytes, optional): Imagen del comprobante en bytes
            nombre_imagen (str, optional): Nombre original del archivo de imagen

        Returns:
            int: ID de la deuda actualizada
        """
        try:
            self._get_connection()

            query_deuda = "SELECT * FROM vista_deudas_detalladas WHERE id_deuda = %s"
            self.cursor.execute(query_deuda, (id_deuda,))
            deuda_actual = self.cursor.fetchone()
            
            if not deuda_actual:
                raise ValueError(f"Deuda {id_deuda} no encontrada")
            
            # Validar que el monto no exceda el saldo pendiente
            saldo_pendiente = deuda_actual['saldo_pendiente']
            if monto_pago > saldo_pendiente:
                raise ValueError(f"El monto del pago ({monto_pago}) excede el saldo pendiente ({saldo_pendiente})")
            
            # Calcular nuevo monto pagado
            nuevo_monto_pagado = Decimal(str(deuda_actual['monto_pagado'])) + monto_pago
            nuevo_saldo = Decimal(str(deuda_actual['monto_total'])) - nuevo_monto_pagado
            
            # Determinar si la deuda queda completamente pagada
            pagado_completo = nuevo_saldo <= Decimal('0.01')
            
            # Limitar longitud de referencia
            if referencia_pago and len(referencia_pago) > 200:
                referencia_pago = referencia_pago[:200]
            
            # Crear descripción corta para este pago (máximo 200 caracteres)
            descripcion_pago = f"Pago {monto_pago} via {metodo_pago}"
            if referencia_pago:
                espacio_disponible = 200 - len(descripcion_pago) - 8
                if espacio_disponible > 0:
                    ref_truncada = referencia_pago[:espacio_disponible]
                    descripcion_pago += f" - Ref: {ref_truncada}"
            
            # Actualizar la deuda
            update_query = """
            UPDATE deuda
            SET
                monto_pagado = %s,
                pagado = %s,
                fecha_pago = %s,
                metodo_pago = %s,
                referencia_pago = %s,
                descripcion = %s,
                imagen_comprobante = %s,
                nombre_imagen = %s
            WHERE id_deuda = %s
            """

            fecha_pago = date.today() if pagado_completo else deuda_actual.get('fecha_pago')

            self.cursor.execute(update_query, (
                nuevo_monto_pagado,
                pagado_completo,
                fecha_pago,
                metodo_pago,
                referencia_pago,
                descripcion_pago,
                imagen_comprobante,
                nombre_imagen,
                id_deuda
            ))
            
            self.connection.commit()
            
            debug_print(f"Pago registrado para deuda {id_deuda}: {monto_pago}")
            debug_print(f"Nuevo estado: pagado={pagado_completo}, saldo={nuevo_saldo}")
            
            return id_deuda
            
        except (Error, ValueError) as e:
            if self.connection:
                self.connection.rollback()
            debug_print(f"Error registrando pago: {e}")
            raise
        finally:
            self._close_connection()
    
    def obtener_historial_pagos(self, id_cliente: int = None, 
                               fecha_inicio: date = None, fecha_fin: date = None) -> List[Dict]:
        """
        Obtiene el historial de pagos realizados.
        
        Args:
            id_cliente (int, optional): Filtrar por cliente especifico
            fecha_inicio (date, optional): Fecha de inicio del filtro
            fecha_fin (date, optional): Fecha de fin del filtro
            
        Returns:
            List[Dict]: Lista de pagos realizados
        """
        try:
            self._get_connection()
            
            query = """
            SELECT 
                id_deuda,
                id_cliente,
                nombre_cliente,
                id_factura,
                folio_numero,
                monto_total,
                monto_pagado,
                fecha_pago,
                metodo_pago,
                referencia_pago,
                registrado_por,
                descripcion,
                clave_grupo,
                tipo_cliente
            FROM vista_historial_pagos 
            WHERE 1=1
            """
            
            params = []
            
            if id_cliente:
                query += " AND id_cliente = %s"
                params.append(id_cliente)
            
            if fecha_inicio:
                query += " AND fecha_pago >= %s"
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += " AND fecha_pago <= %s"
                params.append(fecha_fin)
            
            query += " ORDER BY fecha_pago DESC"
            
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            
            debug_print(f"Historial de pagos encontrado: {len(result)} registros")
            return result
            
        except Error as e:
            debug_print(f"Error obteniendo historial de pagos: {e}")
            raise
        finally:
            self._close_connection()
    
    def obtener_estadisticas_deudas(self) -> Dict:
        """
        Obtiene estadisticas generales de las deudas.
        
        Returns:
            Dict: Estadisticas de deudas
        """
        try:
            self._get_connection()
            
            query = """
            SELECT 
                COUNT(DISTINCT CASE WHEN saldo_pendiente > 0 THEN id_cliente END) as clientes_con_deuda,
                COUNT(DISTINCT id_cliente) as total_clientes,
                COALESCE(SUM(saldo_pendiente), 0) as total_saldo_pendiente,
                COALESCE(SUM(total_deuda_pendiente), 0) as total_deuda_pendiente,
                COALESCE(SUM(total_deuda_pagada), 0) as total_deuda_pagada,
                COALESCE(SUM(deudas_pendientes), 0) as total_deudas_pendientes,
                COALESCE(SUM(deudas_pagadas), 0) as total_deudas_pagadas
            FROM vista_estado_cuenta_cliente
            """
            
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            
            debug_print("Estadisticas de deudas obtenidas")
            return result or {}
            
        except Error as e:
            debug_print(f"Error obteniendo estadisticas de deudas: {e}")
            raise
        finally:
            self._close_connection()


# Instancia global del gestor de deudas
_debt_manager_instance = None

def obtener_debt_manager() -> DebtManager:
    """
    Obtiene la instancia singleton del gestor de deudas.
    
    Returns:
        DebtManager: Instancia del gestor de deudas
    """
    global _debt_manager_instance
    if _debt_manager_instance is None:
        _debt_manager_instance = DebtManager()
    return _debt_manager_instance