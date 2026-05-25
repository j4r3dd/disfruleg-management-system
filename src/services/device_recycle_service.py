"""
Servicio de Limpieza y Reciclaje de Dispositivos
Ejecutar como tarea programada (cron job o celery task)
"""

import logging
from datetime import datetime, timedelta
from src.database.conexion import get_pooled_connection

logger = logging.getLogger(__name__)


class DeviceRecycleService:
    """Gestiona la limpieza y reciclaje automático de dispositivos"""
    
    # Configuración de tiempos (en días)
    DAYS_BEFORE_RECYCLE = 30  # Reciclar bloqueados después de 30 días
    DAYS_BEFORE_HARD_DELETE = 365  # Hard-delete después de 1 año
    
    @staticmethod
    def auto_recycle_blocked_devices(days: int = None) -> dict:
        """
        Recicla automáticamente dispositivos bloqueados hace más de N días
        
        Args:
            days: Días desde bloqueo para reciclar (default: DAYS_BEFORE_RECYCLE)
            
        Returns:
            dict: {'success': bool, 'recycled': int, 'message': str}
        """
        if days is None:
            days = DeviceRecycleService.DAYS_BEFORE_RECYCLE
        
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()
                
                # Encontrar dispositivos bloqueados antiguos
                date_threshold = datetime.now() - timedelta(days=days)
                
                cursor.execute("""
                    SELECT id_dispositivo, device_id, device_name, id_usuario, estado
                    FROM dispositivos_autorizados
                    WHERE estado = 'BLOQUEADO' 
                    AND fecha_registro < %s
                    AND fecha_eliminacion IS NULL
                """, (date_threshold,))
                
                devices = cursor.fetchall()
                recycled_count = 0
                
                for device in devices:
                    dev_id = device.get('id_dispositivo')
                    device_id_hash = device.get('device_id')
                    device_name = device.get('device_name')
                    user_id = device.get('id_usuario')
                    estado = device.get('estado')
                    
                    try:
                        # Insertar en tabla de reciclaje
                        cursor.execute("""
                            INSERT INTO dispositivos_reciclaje
                            (id_dispositivo, device_id, device_name, id_usuario, 
                             estado_anterior, fecha_bloqueo, puede_reasignar)
                            VALUES (%s, %s, %s, %s, %s, NOW(), TRUE)
                        """, (dev_id, device_id_hash, device_name, user_id, estado))
                        
                        # Soft-delete
                        cursor.execute("""
                            UPDATE dispositivos_autorizados
                            SET estado = 'ELIMINADO', fecha_eliminacion = NOW()
                            WHERE id_dispositivo = %s
                        """, (dev_id,))
                        
                        # Registrar evento
                        cursor.execute("""
                            INSERT INTO dispositivos_eventos
                            (id_dispositivo, device_id, estado_anterior, estado_nuevo, razon, usuario_admin)
                            VALUES (%s, %s, %s, 'ELIMINADO', 'Reciclaje automático', 'SYSTEM')
                        """, (dev_id, device_id_hash, estado))
                        
                        recycled_count += 1
                        logger.info(f"Dispositivo {device_id_hash[:16]}... reciclado automáticamente")
                        
                    except Exception as e:
                        logger.error(f"Error reciclando dispositivo {dev_id}: {str(e)}")
                        continue
                
                conn.commit()
                
                return {
                    'success': True,
                    'recycled': recycled_count,
                    'message': f'{recycled_count} dispositivos reciclados automáticamente'
                }
                
        except Exception as e:
            logger.error(f"Error en auto_recycle_blocked_devices: {str(e)}")
            return {
                'success': False,
                'recycled': 0,
                'message': f'Error: {str(e)}'
            }
    
    @staticmethod
    def hard_delete_old_records(days: int = None) -> dict:
        """
        Elimina permanentemente registros muy antiguos (después de soft-delete)
        
        Args:
            days: Días desde eliminación para hard-delete
            
        Returns:
            dict: {'success': bool, 'deleted': int, 'message': str}
        """
        if days is None:
            days = DeviceRecycleService.DAYS_BEFORE_HARD_DELETE
        
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()
                
                date_threshold = datetime.now() - timedelta(days=days)
                
                # Hard-delete de registros muy antiguos
                cursor.execute("""
                    DELETE FROM dispositivos_autorizados
                    WHERE estado = 'ELIMINADO' 
                    AND fecha_eliminacion < %s
                """, (date_threshold,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"{deleted_count} registros eliminados permanentemente")
                
                return {
                    'success': True,
                    'deleted': deleted_count,
                    'message': f'{deleted_count} registros eliminados permanentemente'
                }
                
        except Exception as e:
            logger.error(f"Error en hard_delete_old_records: {str(e)}")
            return {
                'success': False,
                'deleted': 0,
                'message': f'Error: {str(e)}'
            }
    
    @staticmethod
    def cleanup_expired_devices() -> dict:
        """
        Limpia dispositivos expirados (sin acceso en 180 días)
        
        Returns:
            dict: {'success': bool, 'expired': int, 'message': str}
        """
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()
                
                expiration_date = datetime.now() - timedelta(days=180)
                
                # Encontrar autorizados sin acceso
                cursor.execute("""
                    SELECT id_dispositivo, device_id, estado
                    FROM dispositivos_autorizados
                    WHERE estado = 'AUTORIZADO'
                    AND (ultimo_acceso < %s OR ultimo_acceso IS NULL)
                    AND fecha_registro < %s
                """, (expiration_date, expiration_date))
                
                devices = cursor.fetchall()
                expired_count = 0
                
                for device in devices:
                    dev_id = device.get('id_dispositivo')
                    device_id_hash = device.get('device_id')
                    estado = device.get('estado')
                    
                    try:
                        # Marcar como expirado
                        cursor.execute("""
                            UPDATE dispositivos_autorizados
                            SET estado = 'EXPIRADO', razon_bloqueo = 'Sin acceso por 180+ días'
                            WHERE id_dispositivo = %s
                        """, (dev_id,))
                        
                        # Registrar evento
                        cursor.execute("""
                            INSERT INTO dispositivos_eventos
                            (id_dispositivo, device_id, estado_anterior, estado_nuevo, razon, usuario_admin)
                            VALUES (%s, %s, %s, 'EXPIRADO', 'Expiración automática por inactividad', 'SYSTEM')
                        """, (dev_id, device_id_hash, estado))
                        
                        expired_count += 1
                        logger.info(f"Dispositivo {device_id_hash[:16]}... marcado como expirado")
                        
                    except Exception as e:
                        logger.error(f"Error expirando dispositivo {dev_id}: {str(e)}")
                        continue
                
                conn.commit()
                
                return {
                    'success': True,
                    'expired': expired_count,
                    'message': f'{expired_count} dispositivos marcados como expirados'
                }
                
        except Exception as e:
            logger.error(f"Error en cleanup_expired_devices: {str(e)}")
            return {
                'success': False,
                'expired': 0,
                'message': f'Error: {str(e)}'
            }
    
    @staticmethod
    def get_recycle_stats() -> dict:
        """
        Obtiene estadísticas de reciclaje
        
        Returns:
            dict: Estadísticas de dispositivos por estado
        """
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()
                
                # Contar por estado
                cursor.execute("""
                    SELECT estado, COUNT(*) as count
                    FROM dispositivos_autorizados
                    WHERE fecha_eliminacion IS NULL
                    GROUP BY estado
                """)
                
                active_stats = cursor.fetchall()
                
                # Contar reciclables
                cursor.execute("""
                    SELECT COUNT(*) as count FROM dispositivos_reciclaje
                    WHERE puede_reasignar = TRUE
                """)
                
                recyclable = cursor.fetchone()
                
                # Contar eliminados
                cursor.execute("""
                    SELECT COUNT(*) as count FROM dispositivos_autorizados
                    WHERE fecha_eliminacion IS NOT NULL
                """)
                
                eliminated = cursor.fetchone()
                
                stats = {
                    'activos': {},
                    'reciclables': recyclable.get('count', 0) if recyclable else 0,
                    'eliminados': eliminated.get('count', 0) if eliminated else 0,
                }
                
                for stat in active_stats:
                    stats['activos'][stat.get('estado')] = stat.get('count', 0)
                
                return {
                    'success': True,
                    'stats': stats
                }
                
        except Exception as e:
            logger.error(f"Error en get_recycle_stats: {str(e)}")
            return {
                'success': False,
                'stats': None,
                'message': f'Error: {str(e)}'
            }
    
    @staticmethod
    def run_full_cleanup() -> dict:
        """
        Ejecuta el ciclo completo de limpieza
        
        Returns:
            dict: Resumen de acciones realizadas
        """
        logger.info("=" * 60)
        logger.info("Iniciando ciclo completo de limpieza de dispositivos")
        logger.info("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'auto_recycle': DeviceRecycleService.auto_recycle_blocked_devices(),
            'cleanup_expired': DeviceRecycleService.cleanup_expired_devices(),
            'hard_delete': DeviceRecycleService.hard_delete_old_records(),
            'stats': DeviceRecycleService.get_recycle_stats()
        }
        
        logger.info("=" * 60)
        logger.info(f"Reciclados: {results['auto_recycle'].get('recycled', 0)}")
        logger.info(f"Expirados: {results['cleanup_expired'].get('expired', 0)}")
        logger.info(f"Hard-deleted: {results['hard_delete'].get('deleted', 0)}")
        logger.info("=" * 60)
        
        return results


# Script para ejecutar manualmente o con cron
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ejecutar limpieza completa
    result = DeviceRecycleService.run_full_cleanup()
    
    print("\n" + "=" * 60)
    print("RESULTADO DEL CICLO DE LIMPIEZA")
    print("=" * 60)
    print(f"Reciclados: {result['auto_recycle']['recycled']}")
    print(f"Expirados: {result['cleanup_expired']['expired']}")
    print(f"Hard-deleted: {result['hard_delete']['deleted']}")
    print("=" * 60)
