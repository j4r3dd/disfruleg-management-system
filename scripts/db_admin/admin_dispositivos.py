#!/usr/bin/env python3
"""
Panel de Administración de Dispositivos
DISFRULEG - Sistema de Seguridad

Uso: python3 admin_dispositivos.py
"""

import sys
import os
from datetime import datetime
import pymysql.cursors

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import db_manager
from src.security.device_manager import device_manager

class DeviceAdminPanel:
    def __init__(self):
        self.conn = None
        self.current_user = None
        
    def clear_screen(self):
        """Limpiar la pantalla"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """Imprimir encabezado"""
        self.clear_screen()
        print("=" * 70)
        print("  🔒 PANEL DE ADMINISTRACIÓN DE DISPOSITIVOS - DISFRULEG")
        print("=" * 70)
        if self.current_user:
            print(f"  Usuario: {self.current_user}")
        print("=" * 70)
        print()
    
    def login(self):
        """Autenticación del administrador"""
        self.print_header()
        print("Por favor, inicia sesión para continuar\n")
        
        username = input("Usuario: ").strip()
        password = input("Contraseña: ").strip()
        
        print("\n🔄 Conectando...")
        result = db_manager.authenticate_and_connect(username, password)
        
        if result['success']:
            self.conn = db_manager.get_connection()
            self.current_user = username
            print("✅ Autenticación exitosa\n")
            input("Presiona ENTER para continuar...")
            return True
        else:
            print(f"❌ Error: {result['message']}\n")
            input("Presiona ENTER para salir...")
            return False
    
    def list_devices(self, filter_type='all'):
        """Listar dispositivos"""
        cursor = self.conn.cursor()
        
        if filter_type == 'pending':
            query = """
                SELECT id_dispositivo, device_id, device_name, autorizado, activo, 
                       fecha_registro, fecha_autorizacion, ultimo_acceso
                FROM dispositivos_autorizados
                WHERE autorizado = FALSE
                ORDER BY fecha_registro DESC
            """
            title = "⏳ DISPOSITIVOS PENDIENTES DE AUTORIZACIÓN"
        elif filter_type == 'authorized':
            query = """
                SELECT id_dispositivo, device_id, device_name, autorizado, activo, 
                       fecha_registro, fecha_autorizacion, ultimo_acceso
                FROM dispositivos_autorizados
                WHERE autorizado = TRUE AND activo = TRUE
                ORDER BY ultimo_acceso DESC
            """
            title = "✅ DISPOSITIVOS AUTORIZADOS"
        elif filter_type == 'blocked':
            query = """
                SELECT id_dispositivo, device_id, device_name, autorizado, activo, 
                       fecha_registro, fecha_autorizacion, ultimo_acceso
                FROM dispositivos_autorizados
                WHERE activo = FALSE
                ORDER BY fecha_registro DESC
            """
            title = "🔴 DISPOSITIVOS BLOQUEADOS"
        else:
            query = """
                SELECT id_dispositivo, device_id, device_name, autorizado, activo, 
                       fecha_registro, fecha_autorizacion, ultimo_acceso
                FROM dispositivos_autorizados
                ORDER BY fecha_registro DESC
            """
            title = "📱 TODOS LOS DISPOSITIVOS"
        
        cursor.execute(query)
        devices = cursor.fetchall()
        
        self.print_header()
        print(title)
        print("-" * 70)
        
        if not devices:
            print("\n  No hay dispositivos en esta categoría.\n")
            return []
        
        print()
        for dev in devices:
            # Soporte para tuplas y diccionarios
            if isinstance(dev, dict):
                dev_id = dev['id_dispositivo']
                device_hash = dev['device_id'][:16] + "..."
                name = dev['device_name']
                autorizado = dev['autorizado']
                activo = dev['activo']
                fecha_reg = dev['fecha_registro']
                fecha_auth = dev['fecha_autorizacion']
                ultimo_acc = dev['ultimo_acceso']
            else:
                dev_id = dev[0]
                device_hash = dev[1][:16] + "..."
                name = dev[2]
                autorizado = dev[3]
                activo = dev[4]
                fecha_reg = dev[5]
                fecha_auth = dev[6]
                ultimo_acc = dev[7]
            
            status = "✅" if autorizado else "⏳"
            active_status = "🟢" if activo else "🔴"
            
            print(f"  {status} {active_status} ID: {dev_id}")
            print(f"     Nombre: {name}")
            print(f"     Device ID: {device_hash}")
            print(f"     Registrado: {fecha_reg}")
            
            if fecha_auth:
                print(f"     Autorizado: {fecha_auth}")
            
            if ultimo_acc:
                print(f"     Último acceso: {ultimo_acc}")
            
            print()
        
        print("-" * 70)
        return devices
    
    def authorize_device(self):
        """Autorizar un dispositivo"""
        devices = self.list_devices('pending')
        
        if not devices:
            input("\nPresiona ENTER para volver...")
            return
        
        print("\n¿Qué dispositivo deseas autorizar?")
        device_id = input("Ingresa el ID del dispositivo (o 0 para cancelar): ").strip()
        
        if device_id == '0':
            return
        
        try:
            device_id = int(device_id)
            
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE dispositivos_autorizados
                SET autorizado = TRUE,
                    fecha_autorizacion = NOW(),
                    estado = 'AUTORIZADO',
                    activo = TRUE
                WHERE id_dispositivo = %s
            """, (device_id,))
            
            if cursor.rowcount > 0:
                self.conn.commit()
                print(f"\n✅ Dispositivo ID {device_id} AUTORIZADO exitosamente")
            else:
                print(f"\n❌ No se encontró el dispositivo con ID {device_id}")
                
        except ValueError:
            print("\n❌ ID inválido")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPresiona ENTER para continuar...")
    
    def block_device(self):
        """Bloquear/Desactivar un dispositivo"""
        devices = self.list_devices('authorized')
        
        if not devices:
            input("\nPresiona ENTER para volver...")
            return
        
        print("\n¿Qué dispositivo deseas BLOQUEAR?")
        device_id = input("Ingresa el ID del dispositivo (o 0 para cancelar): ").strip()
        
        if device_id == '0':
            return
        
        try:
            device_id = int(device_id)
            
            confirm = input(f"\n⚠️  ¿Estás seguro de bloquear el dispositivo {device_id}? (si/no): ").strip().lower()
            
            if confirm in ['si', 's', 'yes', 'y']:
                cursor = self.conn.cursor()
                cursor.execute("""
                    UPDATE dispositivos_autorizados
                    SET activo = FALSE,
                        estado = 'BLOQUEADO'
                    WHERE id_dispositivo = %s
                """, (device_id,))
                
                if cursor.rowcount > 0:
                    self.conn.commit()
                    print(f"\n🔴 Dispositivo ID {device_id} BLOQUEADO exitosamente")
                else:
                    print(f"\n❌ No se encontró el dispositivo con ID {device_id}")
            else:
                print("\n⚠️  Operación cancelada")
                
        except ValueError:
            print("\n❌ ID inválido")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPresiona ENTER para continuar...")
    
    def reactivate_device(self):
        """Reactivar un dispositivo bloqueado"""
        devices = self.list_devices('blocked')
        
        if not devices:
            input("\nPresiona ENTER para volver...")
            return
        
        print("\n¿Qué dispositivo deseas REACTIVAR?")
        device_id = input("Ingresa el ID del dispositivo (o 0 para cancelar): ").strip()
        
        if device_id == '0':
            return
        
        try:
            device_id = int(device_id)
            
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE dispositivos_autorizados
                SET activo = TRUE,
                    estado = 'AUTORIZADO'
                WHERE id_dispositivo = %s AND autorizado = TRUE
            """, (device_id,))
            
            if cursor.rowcount > 0:
                self.conn.commit()
                print(f"\n✅ Dispositivo ID {device_id} REACTIVADO exitosamente")
            else:
                print(f"\n❌ No se encontró el dispositivo con ID {device_id}")
                
        except ValueError:
            print("\n❌ ID inválido")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPresiona ENTER para continuar...")
    
    def delete_device(self):
        """Eliminar permanentemente un dispositivo"""
        devices = self.list_devices('all')
        
        if not devices:
            input("\nPresiona ENTER para volver...")
            return
        
        print("\n⚠️  ADVERTENCIA: Esta acción ELIMINARÁ PERMANENTEMENTE el dispositivo")
        print("También se eliminarán todos los logs asociados a este dispositivo")
        print()
        
        device_id = input("Ingresa el ID del dispositivo a ELIMINAR (o 0 para cancelar): ").strip()
        
        if device_id == '0':
            return
        
        try:
            device_id = int(device_id)
            
            # Obtener información del dispositivo antes de eliminarlo
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT device_id, device_name FROM dispositivos_autorizados
                WHERE id_dispositivo = %s
            """, (device_id,))
            
            device_info = cursor.fetchone()
            
            if not device_info:
                print(f"\n❌ No se encontró el dispositivo con ID {device_id}")
                input("\nPresiona ENTER para continuar...")
                return
            
            # Soporte para tuplas y diccionarios
            if isinstance(device_info, dict):
                device_hash = device_info['device_id']
                device_name = device_info['device_name']
            else:
                device_hash = device_info[0]
                device_name = device_info[1]
            
            # Verificar si es el dispositivo actual
            current_device_id = device_manager.get_device_id()
            if device_hash == current_device_id:
                print("\n⛔ ERROR: No puedes eliminar el dispositivo actual")
                input("\nPresiona ENTER para continuar...")
                return
            
            # Mostrar información y pedir confirmación
            print(f"\nDispositivo a eliminar:")
            print(f"  ID: {device_id}")
            print(f"  Nombre: {device_name}")
            print(f"  Hash: {device_hash[:16]}...")
            print()
            
            # Primera confirmación
            confirm1 = input("¿Estás seguro de eliminar este dispositivo? (si/no): ").strip().lower()
            
            if confirm1 not in ['si', 's', 'yes', 'y']:
                print("\n⚠️  Operación cancelada")
                input("\nPresiona ENTER para continuar...")
                return
            
            # Segunda confirmación (seguridad extra)
            confirm2 = input("\n⚠️  ÚLTIMA ADVERTENCIA: Esta acción es IRREVERSIBLE. Confirmar eliminación (ELIMINAR/cancelar): ").strip()
            
            if confirm2.upper() != 'ELIMINAR':
                print("\n⚠️  Operación cancelada")
                input("\nPresiona ENTER para continuar...")
                return
            
            # Proceder con la eliminación
            try:
                # Primero eliminar los logs asociados
                cursor.execute("""
                    DELETE FROM log_accesos_dispositivos
                    WHERE device_id = %s
                """, (device_hash,))
                
                logs_deleted = cursor.rowcount
                
                # Luego eliminar el dispositivo
                cursor.execute("""
                    DELETE FROM dispositivos_autorizados
                    WHERE id_dispositivo = %s
                """, (device_id,))
                
                if cursor.rowcount > 0:
                    self.conn.commit()
                    print(f"\n✅ Dispositivo ID {device_id} ELIMINADO exitosamente")
                    print(f"   - Logs eliminados: {logs_deleted}")
                else:
                    print(f"\n❌ Error al eliminar el dispositivo")
                    
            except Exception as e:
                self.conn.rollback()
                print(f"\n❌ Error durante la eliminación: {e}")
                
        except ValueError:
            print("\n❌ ID inválido")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPresiona ENTER para continuar...")
    
    def view_logs(self):
        """Ver logs de acceso"""
        self.print_header()
        print("📋 REGISTRO DE ACCESOS (Últimos 20)\n")
        print("-" * 70)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT l.username, l.modulo, l.accion, l.fecha_hora, l.exito,
                   d.device_name
            FROM log_accesos_dispositivos l
            LEFT JOIN dispositivos_autorizados d ON l.device_id = d.device_id
            ORDER BY l.fecha_hora DESC
            LIMIT 20
        """)
        
        logs = cursor.fetchall()
        
        if not logs:
            print("\n  No hay logs registrados.\n")
        else:
            for log in logs:
                # Soporte para tuplas y diccionarios
                if isinstance(log, dict):
                    username = log['username']
                    modulo = log['modulo']
                    accion = log['accion']
                    fecha = log['fecha_hora']
                    exito = log['exito']
                    device_name = log['device_name'] if log['device_name'] else "Dispositivo desconocido"
                else:
                    username = log[0]
                    modulo = log[1]
                    accion = log[2]
                    fecha = log[3]
                    exito = log[4]
                    device_name = log[5] if log[5] else "Dispositivo desconocido"
                
                status = "✅" if exito else "❌"
                
                print(f"\n  {status} {fecha}")
                print(f"     Usuario: {username}")
                print(f"     Dispositivo: {device_name}")
                print(f"     Módulo: {modulo}")
                print(f"     Acción: {accion}")
        
        print("\n" + "-" * 70)
        input("\nPresiona ENTER para volver...")
    
    def show_current_device(self):
        """Mostrar información del dispositivo actual"""
        self.print_header()
        print("🖥️  INFORMACIÓN DE ESTE DISPOSITIVO\n")
        print("-" * 70)
        
        current_id = device_manager.get_device_id()
        
        print(f"\nDevice ID: {current_id}")
        device_name = device_manager.get_device_name() if hasattr(device_manager, 'get_device_name') else "Desconocido"
        print(f"Nombre: {device_name}")
        print(f"\nInformación técnica:")
        for key, value in device_manager.device_info.items():
            print(f"  {key}: {value}")
        
        # Ver estado en la BD
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT autorizado, activo, fecha_registro, ultimo_acceso
            FROM dispositivos_autorizados
            WHERE device_id = %s
        """, (current_id,))
        
        result_rows = cursor.fetchall()
        
        if result_rows:
            dev = result_rows[0]
            
            # Soporte para tuplas y diccionarios
            if isinstance(dev, dict):
                autorizado = dev['autorizado']
                activo = dev['activo']
                fecha_reg = dev['fecha_registro']
                ultimo_acc = dev['ultimo_acceso']
            else:
                autorizado = dev[0]
                activo = dev[1]
                fecha_reg = dev[2]
                ultimo_acc = dev[3]
            
            print(f"\n📊 Estado en la base de datos:")
            print(f"  Autorizado: {'✅ SÍ' if autorizado else '❌ NO'}")
            print(f"  Activo: {'✅ SÍ' if activo else '❌ NO'}")
            print(f"  Registrado: {fecha_reg}")
            if ultimo_acc:
                print(f"  Último acceso: {ultimo_acc}")
        else:
            print("\n⚠️  Este dispositivo NO está registrado en la base de datos")
        
        print("\n" + "-" * 70)
        input("\nPresiona ENTER para volver...")
    
    def main_menu(self):
        """Menú principal"""
        while True:
            self.print_header()
            print("MENÚ PRINCIPAL\n")
            print("  1. Ver todos los dispositivos")
            print("  2. Ver dispositivos pendientes")
            print("  3. Ver dispositivos autorizados")
            print("  4. Ver dispositivos bloqueados")
            print("  5. Autorizar un dispositivo")
            print("  6. Bloquear un dispositivo")
            print("  7. Reactivar un dispositivo")
            print("  8. Eliminar un dispositivo (permanente)")
            print("  9. Ver logs de acceso")
            print(" 10. Ver información de este dispositivo")
            print("  0. Salir")
            print()
            
            choice = input("Selecciona una opción: ").strip()
            
            if choice == '1':
                self.list_devices('all')
                input("\nPresiona ENTER para volver...")
            elif choice == '2':
                self.list_devices('pending')
                input("\nPresiona ENTER para volver...")
            elif choice == '3':
                self.list_devices('authorized')
                input("\nPresiona ENTER para volver...")
            elif choice == '4':
                self.list_devices('blocked')
                input("\nPresiona ENTER para volver...")
            elif choice == '5':
                self.authorize_device()
            elif choice == '6':
                self.block_device()
            elif choice == '7':
                self.reactivate_device()
            elif choice == '8':
                self.delete_device()
            elif choice == '9':
                self.view_logs()
            elif choice == '10':
                self.show_current_device()
            elif choice == '0':
                self.print_header()
                print("¡Hasta luego!\n")
                break
            else:
                print("\n❌ Opción inválida")
                input("Presiona ENTER para continuar...")
    
    def run(self):
        """Ejecutar el panel"""
        if self.login():
            self.main_menu()

if __name__ == "__main__":
    panel = DeviceAdminPanel()
    panel.run()