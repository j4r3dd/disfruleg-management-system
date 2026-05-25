# -*- coding: utf-8 -*-
"""
MySQL Repositories para módulo de deudas
Versión FINAL - Retorna ClientDebtSummary correctamente
"""

from typing import List, Optional, Dict
from datetime import datetime

from ..domain.models import Debt, Payment, ClientDebtSummary
from ..domain.exceptions import DebtNotFoundError, PaymentExceedsSaldoError


class MySQLDebtRepository:
    """Repositorio de deudas en MySQL"""
    
    def __init__(self, connection):
        self.conn = connection
    
    def _row_to_dict(self, cursor, row):
        """Convertir tupla de fila a diccionario"""
        try:
            if not row:
                return {}
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            if not columns:
                return {}
            
            # Si row es None o no tiene elementos, retornar vacío
            if not row:
                return {}
            
            result = dict(zip(columns, row))
            return result
        except Exception as e:
            print(f"Error en _row_to_dict: {e}")
            return {}
    
    def _map_to_debt(self, row: Dict) -> Debt:
        """Mapear diccionario a objeto Debt"""
        try:
            from decimal import Decimal
            from datetime import date, datetime
            
            # Conversión segura de montos a Decimal
            monto_total = row.get('monto_total', 0)
            monto_pagado = row.get('monto_pagado', 0)
            
            if isinstance(monto_total, Decimal):
                pass
            elif monto_total:
                try:
                    monto_total = Decimal(str(monto_total))
                except:
                    monto_total = Decimal('0')
            else:
                monto_total = Decimal('0')
            
            if isinstance(monto_pagado, Decimal):
                pass
            elif monto_pagado:
                try:
                    monto_pagado = Decimal(str(monto_pagado))
                except:
                    monto_pagado = Decimal('0')
            else:
                monto_pagado = Decimal('0')
            
            # Convertir id_factura a int
            id_factura = row.get('id_factura', '')
            try:
                if isinstance(id_factura, int):
                    id_factura_int = id_factura
                else:
                    id_factura_int = int(''.join(filter(str.isdigit, str(id_factura))))
            except:
                id_factura_int = 0
            
            # Convertir fechas
            fecha_generada = row.get('fecha_generada')
            if isinstance(fecha_generada, datetime):
                fecha_generada = fecha_generada.date()
            
            fecha_pago = row.get('fecha_pago')
            if isinstance(fecha_pago, datetime):
                fecha_pago = fecha_pago.date()
            
            # Validación: si pagado=1 pero no hay fecha_pago, usar fecha_generada
            pagado = bool(row.get('pagado', False))
            if pagado and not fecha_pago:
                fecha_pago = fecha_generada
            
            # Manejar metodo_pago (convertir string a enum si es necesario)
            metodo_pago = row.get('metodo_pago')
            if metodo_pago and isinstance(metodo_pago, str):
                try:
                    from ..domain.value_objects import PaymentMethod
                    metodo_pago = PaymentMethod(metodo_pago)
                except:
                    metodo_pago = None
            
            return Debt(
                id_deuda=int(row.get('id_deuda', 0)),
                id_cliente=int(row.get('id_cliente', 0)),
                id_factura=id_factura_int,
                nombre_cliente=str(row.get('nombre_cliente', '')),
                nombre_grupo=str(row.get('nombre_grupo', '')),
                monto_total=monto_total,
                monto_pagado=monto_pagado,
                fecha_generada=fecha_generada,
                pagado=pagado,
                fecha_pago=fecha_pago,
                descripcion=row.get('descripcion') or '',
                metodo_pago=metodo_pago,
                referencia_pago=row.get('referencia_pago'),
                imagen_comprobante=row.get('imagen_comprobante'),
                nombre_imagen=row.get('nombre_imagen'),
                folio_numero=row.get('folio_numero')  # Get folio from joined query
            )
        except Exception as e:
            print(f"Error CRÍTICO en _map_to_debt: {e}")
            print(f"Row completo: {row}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_clients_with_debts(self) -> List[ClientDebtSummary]:
        """Obtener todos los clientes con deudas"""
        try:
            from decimal import Decimal
            
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    d.id_cliente, 
                    d.nombre_cliente,
                    COALESCE(d.nombre_grupo, '') as clave_grupo,
                    COALESCE(SUM(CASE WHEN d.pagado = 0 THEN (d.monto_total - d.monto_pagado) ELSE 0 END), 0) as saldo_pendiente,
                    COUNT(CASE WHEN d.pagado = 0 THEN 1 END) as deudas_pendientes,
                    COALESCE(SUM(CASE WHEN d.pagado = 0 THEN (d.monto_total - d.monto_pagado) ELSE 0 END), 0) as total_deuda_pendiente,
                    COALESCE(SUM(d.monto_pagado), 0) as total_deuda_pagada
                FROM deudas d
                WHERE d.pagado = 0
                GROUP BY d.id_cliente, d.nombre_cliente, d.nombre_grupo
                HAVING saldo_pendiente > 0
                ORDER BY saldo_pendiente DESC
            """)
            
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                if isinstance(row, dict):
                    id_cliente = row.get('id_cliente')
                    nombre_cliente = row.get('nombre_cliente', '')
                    clave_grupo = row.get('clave_grupo', '')
                    saldo_pendiente = row.get('saldo_pendiente', 0)
                    deudas_pendientes = row.get('deudas_pendientes', 0)
                    total_deuda_pendiente = row.get('total_deuda_pendiente', 0)
                    total_deuda_pagada = row.get('total_deuda_pagada', 0)
                else:
                    id_cliente = row[0]
                    nombre_cliente = row[1] or ''
                    clave_grupo = row[2] or ''
                    saldo_pendiente = row[3] or 0
                    deudas_pendientes = row[4] or 0
                    total_deuda_pendiente = row[5] or 0
                    total_deuda_pagada = row[6] or 0
                
                if id_cliente and saldo_pendiente > 0:
                    client_summary = ClientDebtSummary(
                        id_cliente=int(id_cliente),
                        nombre_cliente=str(nombre_cliente),
                        clave_grupo=str(clave_grupo),
                        saldo_pendiente=Decimal(str(saldo_pendiente or 0)),
                        deudas_pendientes=int(deudas_pendientes or 0),
                        total_deuda_pendiente=Decimal(str(total_deuda_pendiente or 0)),
                        total_deuda_pagada=Decimal(str(total_deuda_pagada or 0))
                    )
                    result.append(client_summary)
            
            cursor.close()
            return result
        except Exception as e:
            raise Exception(f"Error fetching clients with debts: {e}")
    
    def get_all(self) -> List[Debt]:
        """Obtener todas las deudas"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM deudas ORDER BY fecha_generada DESC")
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                row_dict = self._row_to_dict(cursor, row)
                if row_dict:
                    result.append(self._map_to_debt(row_dict))
            
            cursor.close()
            return result
        except Exception as e:
            raise Exception(f"Error fetching all debts: {e}")
    
    def get_by_id(self, id_deuda: int) -> Optional[Debt]:
        """Obtener deuda por ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM deudas WHERE id_deuda = %s", (id_deuda,))
            row = cursor.fetchone()
            
            if not row:
                cursor.close()
                return None
            
            # Obtener nombres de columnas ANTES de procesar
            columns = [desc[0] for desc in cursor.description]
            
            # Convertir a diccionario
            if isinstance(row, dict):
                row_dict = row
            else:
                row_dict = dict(zip(columns, row))
            
            cursor.close()
            
            if row_dict:
                return self._map_to_debt(row_dict)
            return None
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            raise Exception(f"Error fetching debt by ID: {e}")
    
    def get_by_client(self, id_cliente: int) -> List[Debt]:
        """Obtener deudas de un cliente"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM deudas WHERE id_cliente = %s ORDER BY fecha_generada DESC",
                (id_cliente,)
            )
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                row_dict = self._row_to_dict(cursor, row)
                if row_dict:
                    result.append(self._map_to_debt(row_dict))
            
            cursor.close()
            return result
        except Exception as e:
            raise Exception(f"Error fetching client debts: {e}")
    
    def get_debt_by_id(self, id_deuda: int) -> Optional[Debt]:
        """Obtener deuda por ID"""
        return self.get_by_id(id_deuda)
    
    def get_debt_by_id_for_update(self, id_deuda: int) -> Optional[Debt]:
        """Obtener deuda por ID con bloqueo para update (SELECT ... FOR UPDATE)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM deudas WHERE id_deuda = %s FOR UPDATE", (id_deuda,))
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                if isinstance(row, dict):
                    row_dict = row
                else:
                    columns = [desc[0] for desc in cursor.description]
                    row_dict = dict(zip(columns, row))
                
                if row_dict:
                    return self._map_to_debt(row_dict)
            return None
        except Exception as e:
            raise Exception(f"Error fetching debt by ID for update: {e}")
    
    def get_debts_by_client(self, id_cliente: int) -> List[Debt]:
        """Obtener deudas de un cliente con folio de factura"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """SELECT d.*, f.folio_numero 
                   FROM deudas d
                   LEFT JOIN factura f ON d.id_factura = f.id_factura
                   WHERE d.id_cliente = %s 
                   ORDER BY d.fecha_generada DESC""",
                (id_cliente,)
            )
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                # Si es tupla, convertir a diccionario
                if isinstance(row, dict):
                    row_dict = row
                else:
                    # Obtener nombres de columnas
                    columns = [desc[0] for desc in cursor.description]
                    row_dict = dict(zip(columns, row))
                
                if row_dict:
                    debt = self._map_to_debt(row_dict)
                    result.append(debt)
            
            cursor.close()
            return result
        except Exception as e:
            print(f"Error en get_debts_by_client: {e}")
            raise Exception(f"Error fetching client debts: {e}")
    
    def get_client_debts(self, id_cliente: int, only_pending: bool = True) -> List[Debt]:
        """
        Obtener deudas de un cliente con folio de factura
        
        Args:
            id_cliente: ID del cliente
            only_pending: Si True, solo retorna deudas no pagadas
        
        Returns:
            Lista de deudas del cliente
        """
        try:
            query = """SELECT d.*, f.folio_numero 
                       FROM deudas d
                       LEFT JOIN factura f ON d.id_factura = f.id_factura
                       WHERE d.id_cliente = %s"""
            params = [id_cliente]
            
            if only_pending:
                query += " AND d.pagado = 0"
            
            query += " ORDER BY d.fecha_generada DESC"
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                row_dict = self._row_to_dict(cursor, row)
                if row_dict:
                    result.append(self._map_to_debt(row_dict))
            
            cursor.close()
            return result
        except Exception as e:
            raise Exception(f"Error fetching client debts: {e}")
    
    def get_pending(self) -> List[Debt]:
        """Obtener deudas pendientes"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM deudas WHERE pagado = 0 ORDER BY fecha_generada DESC"
            )
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                row_dict = self._row_to_dict(cursor, row)
                if row_dict:
                    result.append(self._map_to_debt(row_dict))
            
            cursor.close()
            return result
        except Exception as e:
            raise Exception(f"Error fetching pending debts: {e}")
    
    def update_debt(self, id_deuda: int, monto_pagado: float, pagado: bool = False,
                   metodo_pago: str = None, referencia_pago: str = None) -> bool:
        """Actualizar deuda"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """UPDATE deudas 
                   SET monto_pagado = %s, pagado = %s, metodo_pago = %s, 
                       referencia_pago = %s, fecha_pago = NOW()
                   WHERE id_deuda = %s""",
                (monto_pagado, 1 if pagado else 0, metodo_pago, referencia_pago, id_deuda)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error updating debt: {e}")
    
    def update_debt_payment(self, id_deuda: int, monto_pagado, pagado: bool = False,
                           fecha_pago=None, metodo_pago: str = None,
                           referencia_pago: str = None, descripcion: str = None,
                           imagen_comprobante=None, nombre_imagen: str = None) -> bool:
        """Actualizar pago de deuda"""
        try:
            from decimal import Decimal
            from datetime import date, datetime

            # Convertir monto_pagado a float si es Decimal
            if isinstance(monto_pagado, Decimal):
                monto_pagado = float(monto_pagado)

            cursor = self.conn.cursor()
            cursor.execute(
                """UPDATE deudas
                   SET monto_pagado = %s, pagado = %s, fecha_pago = %s,
                       metodo_pago = %s, referencia_pago = %s, descripcion = %s,
                       imagen_comprobante = %s, nombre_imagen = %s
                   WHERE id_deuda = %s""",
                (monto_pagado, 1 if pagado else 0, fecha_pago, metodo_pago,
                 referencia_pago, descripcion, imagen_comprobante, nombre_imagen, id_deuda)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error updating debt payment: {e}")

    def revert_debt_payment(self, id_deuda: int, monto_to_subtract) -> bool:
        """
        Revert debt payment by subtracting payment amount

        Args:
            id_deuda: Debt ID
            monto_to_subtract: Amount to subtract from monto_pagado

        Returns:
            True if successful

        Note:
            This method must be called within an active transaction with row locking
        """
        try:
            from decimal import Decimal

            # Convert monto_to_subtract to float if Decimal
            if isinstance(monto_to_subtract, Decimal):
                monto_to_subtract = float(monto_to_subtract)

            cursor = self.conn.cursor()

            # Calculate new monto_pagado and determine if debt is still paid
            cursor.execute(
                """SELECT monto_total, monto_pagado
                   FROM deudas
                   WHERE id_deuda = %s""",
                (id_deuda,)
            )

            result = cursor.fetchone()

            if not result:
                cursor.close()
                raise Exception(f"Debt {id_deuda} not found")

            if isinstance(result, dict):
                monto_total = result['monto_total']
                monto_pagado_actual = result['monto_pagado']
            else:
                monto_total = result[0]
                monto_pagado_actual = result[1]

            # Convert to Decimal for safe arithmetic
            if not isinstance(monto_total, Decimal):
                monto_total = Decimal(str(monto_total))
            if not isinstance(monto_pagado_actual, Decimal):
                monto_pagado_actual = Decimal(str(monto_pagado_actual))

            # Calculate new monto_pagado
            nuevo_monto_pagado = monto_pagado_actual - Decimal(str(monto_to_subtract))

            # Ensure it doesn't go negative
            if nuevo_monto_pagado < 0:
                nuevo_monto_pagado = Decimal('0')

            # Determine if debt is still fully paid
            pagado = nuevo_monto_pagado >= monto_total

            # If no longer paid, clear payment fields
            if not pagado:
                cursor.execute(
                    """UPDATE deudas
                       SET monto_pagado = %s, pagado = 0, fecha_pago = NULL,
                           metodo_pago = NULL, referencia_pago = NULL,
                           imagen_comprobante = NULL, nombre_imagen = NULL
                       WHERE id_deuda = %s""",
                    (float(nuevo_monto_pagado), id_deuda)
                )
            else:
                # Still paid, just reduce monto_pagado
                cursor.execute(
                    """UPDATE deudas
                       SET monto_pagado = %s
                       WHERE id_deuda = %s""",
                    (float(nuevo_monto_pagado), id_deuda)
                )

            self.conn.commit()
            cursor.close()
            return True

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error reverting debt payment: {e}")
    
    def search_invoices(self, query: str, id_cliente: Optional[int] = None,
                       fecha_inicio = None, fecha_fin = None,
                       incluir_pagadas: bool = True) -> List[Dict]:
        """Buscar facturas"""
        try:
            where_clauses = []
            params = []
            
            where_clauses.append("(id_factura LIKE %s OR nombre_cliente LIKE %s)")
            search_term = f"%{query}%"
            params.extend([search_term, search_term])
            
            if id_cliente:
                where_clauses.append("id_cliente = %s")
                params.append(id_cliente)
            
            if fecha_inicio:
                where_clauses.append("fecha_generada >= %s")
                params.append(fecha_inicio)
            
            if fecha_fin:
                where_clauses.append("fecha_generada <= %s")
                params.append(fecha_fin)
            
            if not incluir_pagadas:
                where_clauses.append("pagado = 0")
            
            where_clause = " AND ".join(where_clauses)
            sql_query = f"""
                SELECT 
                    id_factura, id_deuda, id_cliente, nombre_cliente,
                    monto_total, monto_pagado, fecha_generada, pagado,
                    CASE 
                        WHEN pagado = 1 THEN 'pagada'
                        WHEN monto_pagado > 0 THEN 'parcial'
                        ELSE 'pendiente'
                    END as estado
                FROM deudas 
                WHERE {where_clause}
                ORDER BY fecha_generada DESC
                LIMIT 100
            """
            
            cursor = self.conn.cursor()
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                row_dict = self._row_to_dict(cursor, row)
                if row_dict:
                    result.append(row_dict)
            
            cursor.close()
            return result
        except Exception as e:
            raise Exception(f"Error searching invoices: {e}")
    
    def get_debts_by_ids_for_update(self, ids: List[int]) -> List[Debt]:
        """Obtener deudas con bloqueo FOR UPDATE"""
        if not ids:
            return []
        
        try:
            placeholders = ','.join(['%s'] * len(ids))
            query = f"""
                SELECT * FROM deudas
                WHERE id_deuda IN ({placeholders})
                FOR UPDATE
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query, ids)
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                row_dict = self._row_to_dict(cursor, row)
                if row_dict:
                    result.append(self._map_to_debt(row_dict))
            
            cursor.close()
            return result
        except Exception as e:
            raise Exception(f"Error fetching debts for update: {e}")


    def get_statistics(self):
        """
        Obtener estadísticas generales de deudas

        Returns:
            DebtStatistics: Objeto con estadísticas del sistema
        """
        try:
            from decimal import Decimal
            from ..domain.models import DebtStatistics

            cursor = self.conn.cursor()

            # Query para obtener todas las estadísticas en una sola consulta
            cursor.execute("""
                SELECT
                    COUNT(DISTINCT CASE WHEN pagado = 0 THEN id_cliente END) as total_clientes_con_deudas,
                    COUNT(CASE WHEN pagado = 0 THEN 1 END) as total_deudas_pendientes,
                    COALESCE(SUM(CASE WHEN pagado = 0 THEN (monto_total - monto_pagado) END), 0) as saldo_total_pendiente,
                    COALESCE(SUM(monto_total), 0) as total_deudas,
                    COALESCE(SUM(monto_pagado), 0) as total_pagado
                FROM deudas
            """)

            row = cursor.fetchone()
            cursor.close()

            if row:
                # Convertir tupla a diccionario si es necesario
                if isinstance(row, dict):
                    total_clientes_con_deudas = int(row.get('total_clientes_con_deudas', 0) or 0)
                    total_deudas_pendientes = int(row.get('total_deudas_pendientes', 0) or 0)
                    saldo_total_pendiente = Decimal(str(row.get('saldo_total_pendiente', 0) or 0))
                    total_deudas = Decimal(str(row.get('total_deudas', 0) or 0))
                    total_pagado = Decimal(str(row.get('total_pagado', 0) or 0))
                else:
                    total_clientes_con_deudas = int(row[0] or 0)
                    total_deudas_pendientes = int(row[1] or 0)
                    saldo_total_pendiente = Decimal(str(row[2] or 0))
                    total_deudas = Decimal(str(row[3] or 0))
                    total_pagado = Decimal(str(row[4] or 0))

                return DebtStatistics(
                    total_clientes_con_deudas=total_clientes_con_deudas,
                    total_deudas_pendientes=total_deudas_pendientes,
                    saldo_total_pendiente=saldo_total_pendiente,
                    total_deudas=total_deudas,
                    total_pagado=total_pagado
                )
            else:
                # Si no hay datos, retornar estadísticas en cero
                return DebtStatistics(
                    total_clientes_con_deudas=0,
                    total_deudas_pendientes=0,
                    saldo_total_pendiente=Decimal('0'),
                    total_deudas=Decimal('0'),
                    total_pagado=Decimal('0')
                )
        except Exception as e:
            raise Exception(f"Error fetching debt statistics: {e}")


class MySQLPaymentRepository:
    """Repositorio de pagos en MySQL"""

    def __init__(self, connection):
        self.conn = connection
    
    def get_payment_history(self, id_cliente: Optional[int] = None, 
                           fecha_inicio=None, fecha_fin=None) -> List[Dict]:
        """Obtener historial de pagos desde pago_registrado con folio de factura"""
        try:
            query = """
                SELECT 
                    p.id_pago,
                    p.id_deuda,
                    p.monto_pagado as monto_total, -- For UI compatibility
                    p.monto_pagado,
                    p.fecha_pago,
                    p.metodo_pago,
                    p.referencia_pago,
                    p.imagen_comprobante,
                    p.nombre_imagen,
                    p.notas as descripcion,
                    d.id_cliente,
                    d.nombre_cliente,
                    d.nombre_grupo as clave_grupo,
                    d.id_factura,
                    f.folio_numero
                FROM pago_registrado p
                INNER JOIN deudas d ON p.id_deuda = d.id_deuda
                LEFT JOIN factura f ON d.id_factura = f.id_factura
                WHERE 1=1
            """
            params = []
            
            if id_cliente:
                query += " AND d.id_cliente = %s"
                params.append(id_cliente)
            
            if fecha_inicio:
                query += " AND p.fecha_pago >= %s"
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += " AND p.fecha_pago <= %s"
                params.append(fecha_fin)
            
            query += " ORDER BY p.fecha_pago DESC, p.timestamp DESC"
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = []
            
            columns = [desc[0] for desc in cursor.description]
            for row in rows:
                if isinstance(row, dict):
                    result.append(row)
                else:
                    result.append(dict(zip(columns, row)))
            
            cursor.close()
            return result
        except Exception as e:
            raise Exception(f"Error fetching payment history: {e}")
    
    def record_payment(self, id_deuda: int, monto: float, metodo_pago: str = None,
                      referencia: str = None, imagen_bytes=None,
                      nombre_imagen: str = None, notas: str = None,
                      usuario: str = 'sistema') -> bool:
        """Registrar pago en pago_registrado"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO pago_registrado
                   (id_deuda, monto_pagado, metodo_pago, referencia_pago,
                    imagen_comprobante, nombre_imagen, notas, usuario_registro, fecha_pago, timestamp)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), NOW())""",
                (id_deuda, monto, metodo_pago, referencia,
                 imagen_bytes, nombre_imagen, notas, usuario)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error recording payment: {e}")

    def delete_payment_by_id(self, id_pago: int):
        """
        Delete payment record and return payment details for debt reversal

        Args:
            id_pago: Payment record ID

        Returns:
            Tuple of (id_deuda, monto_pagado) for reverting debt

        Raises:
            PaymentNotFoundError: If payment doesn't exist
        """
        try:
            from decimal import Decimal
            from ..domain.exceptions import PaymentNotFoundError

            cursor = self.conn.cursor()

            # First, get payment details before deletion
            cursor.execute(
                """SELECT id_deuda, monto_pagado
                   FROM pago_registrado
                   WHERE id_pago = %s""",
                (id_pago,)
            )

            result = cursor.fetchone()

            if not result:
                cursor.close()
                raise PaymentNotFoundError(f"Payment with ID {id_pago} not found")

            # Extract payment details
            if isinstance(result, dict):
                id_deuda = result['id_deuda']
                monto_pagado = result['monto_pagado']
            else:
                id_deuda = result[0]
                monto_pagado = result[1]

            # Convert to Decimal
            if not isinstance(monto_pagado, Decimal):
                monto_pagado = Decimal(str(monto_pagado))

            # Delete the payment record
            cursor.execute(
                "DELETE FROM pago_registrado WHERE id_pago = %s",
                (id_pago,)
            )

            self.conn.commit()
            cursor.close()

            return (int(id_deuda), monto_pagado)

        except PaymentNotFoundError:
            # Re-raise PaymentNotFoundError without wrapping
            raise
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error deleting payment: {e}")