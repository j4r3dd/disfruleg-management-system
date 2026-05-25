import uuid
import platform
import hashlib
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
from src.database.conexion import get_pooled_connection

class DeviceManager:
    """Gestor de dispositivos autorizados con soporte de reciclaje de IDs"""
    
    def __init__(self):
        self.device_id = self._generate_device_id()
        self.device_info = self._get_device_info()
    
    def _generate_device_id(self) -> str:
        """Genera un ID único para este dispositivo"""
        try:
            # Usar identificador estable según el sistema operativo
            system = platform.system()

            if system == "Windows":
                # En Windows, usar el Machine GUID del registro (permanente)
                import subprocess
                try:
                    result = subprocess.check_output(
                        'reg query "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid',
                        shell=True,
                        text=True
                    )
                    # Extraer el GUID de la salida
                    machine_guid = result.strip().split()[-1]
                    stable_id = machine_guid
                except:
                    # Fallback a hostname + username si falla el registro
                    import os
                    stable_id = f"{platform.node()}-{os.getenv('USERNAME', 'unknown')}"

            elif system == "Linux":
                # En Linux, usar machine-id
                try:
                    with open('/etc/machine-id', 'r') as f:
                        stable_id = f.read().strip()
                except:
                    # Fallback para WSL o sistemas sin machine-id
                    try:
                        with open('/var/lib/dbus/machine-id', 'r') as f:
                            stable_id = f.read().strip()
                    except:
                        import os
                        stable_id = f"{platform.node()}-{os.getenv('USER', 'unknown')}"

            elif system == "Darwin":  # macOS
                # En macOS, usar IOPlatformUUID
                import subprocess
                try:
                    result = subprocess.check_output(
                        ['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'],
                        text=True
                    )
                    for line in result.split('\n'):
                        if 'IOPlatformUUID' in line:
                            stable_id = line.split('"')[3]
                            break
                    else:
                        raise Exception("No UUID found")
                except:
                    import os
                    stable_id = f"{platform.node()}-{os.getenv('USER', 'unknown')}"

            else:
                # Otros sistemas: usar hostname + usuario
                import os
                stable_id = f"{platform.node()}-{os.getenv('USER', os.getenv('USERNAME', 'unknown'))}"

            # Información adicional del sistema
            hostname = platform.node()
            machine = platform.machine()

            # Crear hash único combinando stable_id con info del sistema
            device_string = f"{stable_id}-{system}-{machine}"
            device_hash = hashlib.sha256(device_string.encode()).hexdigest()

            return device_hash
        except Exception as e:
            print(f"Error generando device_id: {e}")
            import traceback
            traceback.print_exc()
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    def _get_device_name(self) -> str:
        """Obtiene nombre descriptivo del dispositivo"""
        hostname = platform.node()
        system = platform.system()
        return f"{hostname} - {system}"
    
    def get_device_id(self) -> str:
        """Obtener ID del dispositivo actual"""
        return self.device_id

    def get_device_name(self) -> str:
        """Obtener nombre descriptivo del dispositivo"""
        try:
            import socket
            return f"{socket.gethostname()} - {platform.system()}"
        except:
            return "Dispositivo desconocido"
    
    def _get_device_info(self) -> dict:
        """Obtiene información detallada del dispositivo"""
        return {
            'hostname': platform.node(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def verify_device_authorization(self) -> dict:
        """
        Verifica si el dispositivo está autorizado
        Busca solo entre dispositivos activos (no soft-deleted)
        
        Returns:
            dict: {'authorized': bool, 'needs_registration': bool, 'message': str}
        """
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()

                # Verificar si el dispositivo existe y está activo
                cursor.execute("""
                    SELECT autorizado, activo, estado, device_name, ultimo_acceso
                    FROM dispositivos_autorizados
                    WHERE device_id = %s AND fecha_eliminacion IS NULL
                """, (self.device_id,))

                result_rows = cursor.fetchall()

                if not result_rows:
                    # Dispositivo no registrado
                    return {
                        'authorized': False,
                        'needs_registration': True,
                        'message': 'Dispositivo no registrado. Se requiere autorización del administrador.'
                    }

                device = result_rows[0]

                # Acceder a campos del diccionario
                autorizado = device.get('autorizado')
                activo = device.get('activo')
                estado = device.get('estado', 'UNKNOWN')
                device_name = device.get('device_name')

                # Verificar estados
                if estado == 'BLOQUEADO' or not activo:
                    return {
                        'authorized': False,
                        'needs_registration': False,
                        'message': 'Este dispositivo ha sido bloqueado. Contacte al administrador.'
                    }

                if estado == 'PENDING' or not autorizado:
                    return {
                        'authorized': False,
                        'needs_registration': False,
                        'message': 'Dispositivo pendiente de autorización. Contacte al administrador.'
                    }

                if estado != 'AUTORIZADO':
                    return {
                        'authorized': False,
                        'needs_registration': False,
                        'message': f'Estado de dispositivo inválido: {estado}'
                    }

                # Dispositivo autorizado - actualizar último acceso
                cursor.execute("""
                    UPDATE dispositivos_autorizados
                    SET ultimo_acceso = NOW()
                    WHERE device_id = %s
                """, (self.device_id,))
                conn.commit()

                return {
                    'authorized': True,
                    'needs_registration': False,
                    'message': f'Dispositivo autorizado: {device_name}'
                }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'authorized': False,
                'needs_registration': False,
                'message': f'Error verificando autorización: {str(e)}'
            }
    
    def register_device(self, username: str) -> dict:
        """
        Registra un nuevo dispositivo
        Verifica si puede reciclar un ID existente
        
        Args:
            username: Usuario que solicita el registro

        Returns:
            dict: {'success': bool, 'message': str, 'recycled': bool}
        """
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()

                # Verificar si ya existe ACTIVO
                cursor.execute("""
                    SELECT id_dispositivo, estado FROM dispositivos_autorizados
                    WHERE device_id = %s AND fecha_eliminacion IS NULL
                """, (self.device_id,))

                existing = cursor.fetchall()
                if existing:
                    return {
                        'success': False,
                        'message': 'Este dispositivo ya está registrado.',
                        'recycled': False
                    }

                # Verificar si hay un registro eliminado que pueda reutilizarse
                cursor.execute("""
                    SELECT id_dispositivo FROM dispositivos_autorizados
                    WHERE device_id = %s AND fecha_eliminacion IS NOT NULL
                    LIMIT 1
                """, (self.device_id,))

                recyclable = cursor.fetchall()
                
                if recyclable:
                    # Reutilizar ID existente (reciclaje)
                    recycled_id = recyclable[0].get('id_dispositivo')
                    
                    cursor.execute("""
                        SELECT id_usuario FROM usuarios_sistema
                        WHERE username = %s
                    """, (username,))
                    
                    user_result = cursor.fetchall()
                    user_id = user_result[0].get('id_usuario') if user_result else None
                    
                    # Reactivar dispositivo reciclado
                    cursor.execute("""
                        UPDATE dispositivos_autorizados
                        SET 
                            device_name = %s,
                            device_info = %s,
                            id_usuario = %s,
                            autorizado = FALSE,
                            estado = 'PENDING',
                            activo = TRUE,
                            fecha_eliminacion = NULL,
                            razon_bloqueo = NULL,
                            fecha_registro = NOW(),
                            fecha_autorizacion = NULL,
                            ultimo_acceso = NULL
                        WHERE id_dispositivo = %s
                    """, (self.get_device_name(), json.dumps(self.device_info), user_id, recycled_id))
                    
                    # Registrar evento de reciclaje
                    self._log_event(conn, recycled_id, 'RECICLADO', 'PENDING', 
                                   f'Dispositivo reciclado por {username}')
                    
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': 'Dispositivo registrado (reciclado). Espere autorización del administrador.',
                        'recycled': True
                    }
                else:
                    # Nuevo registro
                    cursor.execute("""
                        SELECT id_usuario FROM usuarios_sistema
                        WHERE username = %s
                    """, (username,))

                    user_result = cursor.fetchall()
                    user_id = user_result[0].get('id_usuario') if user_result else None

                    # Registrar dispositivo nuevo
                    cursor.execute("""
                        INSERT INTO dispositivos_autorizados
                        (device_id, device_name, device_info, id_usuario, autorizado, estado, activo)
                        VALUES (%s, %s, %s, %s, FALSE, 'PENDING', TRUE)
                    """, (self.device_id, self.get_device_name(), json.dumps(self.device_info), user_id))
                    
                    device_id_new = cursor.lastrowid
                    
                    # Registrar evento de registro
                    self._log_event(conn, device_id_new, 'NUEVO', 'PENDING', 
                                   f'Dispositivo registrado por {username}')

                    conn.commit()

                    return {
                        'success': True,
                        'message': 'Dispositivo registrado. Espere autorización del administrador.',
                        'recycled': False
                    }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Error registrando dispositivo: {str(e)}',
                'recycled': False
            }
    
    def _log_event(self, conn, id_dispositivo: int, evento: str, nuevo_estado: str, razon: str = None):
        """
        Registra un evento en la tabla de auditoría
        
        Args:
            conn: Conexión activa
            id_dispositivo: ID del dispositivo
            evento: Tipo de evento (NUEVO, RECICLADO, etc)
            nuevo_estado: Nuevo estado del dispositivo
            razon: Razón del cambio
        """
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO dispositivos_eventos
                (id_dispositivo, device_id, estado_anterior, estado_nuevo, razon, usuario_admin)
                VALUES (%s, %s, NULL, %s, %s, 'SYSTEM')
            """, (id_dispositivo, self.device_id, nuevo_estado, razon))
            
        except Exception as e:
            print(f"Error logging event: {e}")
    
    def log_access(self, username: str, modulo: str, accion: str,
                   exito: bool = True, detalle: str = None):
        """
        Registra un acceso/acción del dispositivo
        
        Args:
            username: Usuario que realizó la acción
            modulo: Módulo de la aplicación
            accion: Acción realizada
            exito: Si la acción fue exitosa
            detalle: Información adicional
        """
        try:
            with get_pooled_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO log_accesos_dispositivos
                    (device_id, username, modulo, accion, exito, detalle)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (self.device_id, username, modulo, accion, exito, detalle))

                conn.commit()

        except Exception as e:
            print(f"Error logging access: {e}")


# Instancia global
device_manager = DeviceManager()
