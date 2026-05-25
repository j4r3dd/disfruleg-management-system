"""
Módulo de Administración de Dispositivos - v2.0 Mejorado
Con soporte de reciclaje de IDs, auditoría y máquina de estados
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
import json

from src.database.db_manager import db_manager
from src.security.device_manager import device_manager


class DeviceStateManager:
    """Gestiona la máquina de estados de dispositivos"""
    
    STATES = {
        'PENDING': {'label': '⏳ PENDIENTE', 'color': '#f59e0b', 'can_authorize': True, 'can_block': False},
        'AUTORIZADO': {'label': '✅ AUTORIZADO', 'color': '#10b981', 'can_authorize': False, 'can_block': True},
        'BLOQUEADO': {'label': '🔴 BLOQUEADO', 'color': '#ef4444', 'can_authorize': False, 'can_block': False},
        'EXPIRADO': {'label': '⏱️ EXPIRADO', 'color': '#8b5cf6', 'can_authorize': True, 'can_block': False},
        'ELIMINADO': {'label': '🗑️ ELIMINADO', 'color': '#6b7280', 'can_authorize': False, 'can_block': False},
    }
    
    @staticmethod
    def get_state_info(estado):
        """Obtiene información del estado"""
        return DeviceStateManager.STATES.get(estado, DeviceStateManager.STATES['PENDING'])


class DeviceAdminApp:
    """Aplicación de administración de dispositivos v2.0"""
    
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.current_filter = 'all'
        self.state_manager = DeviceStateManager()
        
        # Configurar ventana
        self.root.title("DISFRULEG - Administración de Dispositivos v2.0")
        self.root.geometry("1200x800")
        
        # Colores
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2a2a2a',
            'hover': '#333333',
            'primary': '#3b82f6',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'text': 'white',
            'text_secondary': 'gray60'
        }
        
        self.create_interface()
        self.load_devices()
    
    def create_interface(self):
        """Crear interfaz principal"""
        self.create_header()
        self.create_filter_tabs()
        self.create_devices_list()
        self.create_action_panel()
    
    def create_header(self):
        """Crear encabezado"""
        header = ctk.CTkFrame(self.root, fg_color=self.colors['bg'], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        content = ctk.CTkFrame(header, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Título
        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="🔐 Administración de Dispositivos v2.0",
            font=("Arial", 24, "bold"),
            text_color=self.colors['text']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Con auditoría y reciclaje de IDs",
            font=("Arial", 12),
            text_color=self.colors['text_secondary']
        ).pack(anchor="w")
        
        # Botón de actualizar
        ctk.CTkButton(
            content,
            text="🔄 Actualizar",
            font=("Arial", 12, "bold"),
            fg_color=self.colors['primary'],
            hover_color="#2563eb",
            corner_radius=10,
            command=self.load_devices
        ).pack(side="right")
    
    def create_filter_tabs(self):
        """Crear pestañas de filtros mejoradas"""
        tabs_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=60)
        tabs_frame.pack(fill="x", padx=30)
        tabs_frame.pack_propagate(False)
        
        self.tab_buttons = {}
        tabs = [
            ('all', 'Todos', None),
            ('PENDING', 'Pendientes', self.colors['warning']),
            ('AUTORIZADO', 'Autorizados', self.colors['success']),
            ('BLOQUEADO', 'Bloqueados', self.colors['danger']),
            ('reciclaje', 'Disponibles Reciclaje', self.colors['primary'])
        ]
        
        for tab_id, label, color in tabs:
            btn = ctk.CTkButton(
                tabs_frame,
                text=label,
                font=("Arial", 12, "bold"),
                fg_color=self.colors['primary'] if tab_id == 'all' else self.colors['card'],
                hover_color=color if color else self.colors['hover'],
                corner_radius=10,
                command=lambda t=tab_id: self.filter_devices(t)
            )
            btn.pack(side="left", padx=5)
            self.tab_buttons[tab_id] = btn
    
    def create_devices_list(self):
        """Crear lista scrollable de dispositivos"""
        self.list_frame = ctk.CTkScrollableFrame(
            self.root,
            fg_color="transparent"
        )
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    def create_action_panel(self):
        """Crear panel de acciones"""
        panel = ctk.CTkFrame(self.root, fg_color=self.colors['bg'], height=70)
        panel.pack(fill="x", side="bottom")
        panel.pack_propagate(False)
        
        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=15)
        
        # Info del dispositivo actual
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left")
        
        current_id = device_manager.get_device_id()[:16] + "..."
        
        ctk.CTkLabel(
            info_frame,
            text=f"🖥️ Este dispositivo: {current_id}",
            font=("Arial", 11),
            text_color=self.colors['text_secondary']
        ).pack(side="left", padx=(0, 20))
        
        # Estadísticas
        self.stats_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=("Arial", 11, "bold"),
            text_color=self.colors['text']
        )
        self.stats_label.pack(side="left")
    
    def load_devices(self):
        """Cargar dispositivos desde la BD"""
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            # Obtener dispositivos según filtro
            if self.current_filter == 'PENDING':
                query = """
                    SELECT id_dispositivo, device_id, device_name, estado, activo,
                           fecha_registro, fecha_autorizacion, ultimo_acceso, device_info,
                           razon_bloqueo
                    FROM dispositivos_activos
                    WHERE estado = 'PENDING'
                    ORDER BY fecha_registro DESC
                """
            elif self.current_filter == 'AUTORIZADO':
                query = """
                    SELECT id_dispositivo, device_id, device_name, estado, activo,
                           fecha_registro, fecha_autorizacion, ultimo_acceso, device_info,
                           razon_bloqueo
                    FROM dispositivos_activos
                    WHERE estado = 'AUTORIZADO'
                    ORDER BY ultimo_acceso DESC
                """
            elif self.current_filter == 'BLOQUEADO':
                query = """
                    SELECT id_dispositivo, device_id, device_name, estado, activo,
                           fecha_registro, fecha_autorizacion, ultimo_acceso, device_info,
                           razon_bloqueo
                    FROM dispositivos_activos
                    WHERE estado = 'BLOQUEADO'
                    ORDER BY fecha_registro DESC
                """
            elif self.current_filter == 'reciclaje':
                query = """
                    SELECT id_dispositivo, device_id, device_name, estado, activo,
                           fecha_registro, fecha_autorizacion, ultimo_acceso, device_info,
                           razon_bloqueo
                    FROM dispositivos_autorizados
                    WHERE fecha_eliminacion IS NOT NULL AND estado = 'BLOQUEADO'
                    ORDER BY fecha_eliminacion DESC
                    LIMIT 100
                """
            else:  # all
                query = """
                    SELECT id_dispositivo, device_id, device_name, estado, activo,
                           fecha_registro, fecha_autorizacion, ultimo_acceso, device_info,
                           razon_bloqueo
                    FROM dispositivos_activos
                    ORDER BY fecha_registro DESC
                    LIMIT 200
                """
            
            cursor.execute(query)
            devices = cursor.fetchall()
            
            # Limpiar lista
            for widget in self.list_frame.winfo_children():
                widget.destroy()
            
            if not devices:
                self.show_empty_state()
            else:
                for device in devices:
                    self.create_device_card(device)
            
            # Actualizar estadísticas
            self.update_stats(devices)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando dispositivos: {str(e)}")
    
    def show_empty_state(self):
        """Mostrar estado vacío"""
        empty_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True, pady=100)
        
        ctk.CTkLabel(
            empty_frame,
            text="📭",
            font=("Arial", 64)
        ).pack()
        
        ctk.CTkLabel(
            empty_frame,
            text="No hay dispositivos en esta categoría",
            font=("Arial", 16, "bold"),
            text_color=self.colors['text_secondary']
        ).pack(pady=10)
    
    def create_device_card(self, device):
        """Crear tarjeta de dispositivo"""
        # Extraer datos
        dev_id = device.get('id_dispositivo')
        device_hash = device.get('device_id')
        name = device.get('device_name')
        estado = device.get('estado', 'UNKNOWN')
        activo = device.get('activo')
        fecha_reg = device.get('fecha_registro')
        fecha_auth = device.get('fecha_autorizacion')
        ultimo_acc = device.get('ultimo_acceso')
        razon_bloqueo = device.get('razon_bloqueo')
        device_info_str = device.get('device_info')
        
        # Parsear device_info
        try:
            device_info = json.loads(device_info_str) if device_info_str else {}
        except:
            device_info = {}
        
        # Obtener info de estado
        state_info = self.state_manager.get_state_info(estado)
        status_color = state_info['color']
        status_text = state_info['label']
        
        # Card
        card = ctk.CTkFrame(
            self.list_frame,
            fg_color=self.colors['card'],
            corner_radius=15
        )
        card.pack(fill="x", pady=10)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Header del card
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")
        
        # Izquierda: Info
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        
        # Nombre y estado
        name_frame = ctk.CTkFrame(left, fg_color="transparent")
        name_frame.pack(anchor="w")
        
        ctk.CTkLabel(
            name_frame,
            text=name,
            font=("Arial", 16, "bold"),
            text_color=self.colors['text']
        ).pack(side="left", padx=(0, 15))
        
        status_badge = ctk.CTkLabel(
            name_frame,
            text=status_text,
            font=("Arial", 10, "bold"),
            text_color="white",
            fg_color=status_color,
            corner_radius=5
        )
        status_badge.pack(side="left")
        
        # Device ID
        ctk.CTkLabel(
            left,
            text=f"ID: {device_hash[:32]}...",
            font=("Arial", 10),
            text_color=self.colors['text_secondary']
        ).pack(anchor="w", pady=(5, 0))
        
        # Mostrar razón de bloqueo si existe
        if razon_bloqueo:
            ctk.CTkLabel(
                left,
                text=f"Razón: {razon_bloqueo}",
                font=("Arial", 9),
                text_color=self.colors['danger']
            ).pack(anchor="w", pady=(2, 0))
        
        # Derecha: Botones de acción
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        
        # Botones según estado
        if estado == 'PENDING':
            ctk.CTkButton(
                right,
                text="✓ Autorizar",
                font=("Arial", 11, "bold"),
                fg_color=self.colors['success'],
                hover_color="#059669",
                corner_radius=8,
                width=100,
                command=lambda: self.authorize_device(dev_id)
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                right,
                text="🔒 Bloquear",
                font=("Arial", 11, "bold"),
                fg_color=self.colors['danger'],
                hover_color="#dc2626",
                corner_radius=8,
                width=100,
                command=lambda: self.block_device(dev_id)
            ).pack(side="left", padx=5)
        
        elif estado == 'AUTORIZADO':
            ctk.CTkButton(
                right,
                text="🔒 Bloquear",
                font=("Arial", 11, "bold"),
                fg_color=self.colors['danger'],
                hover_color="#dc2626",
                corner_radius=8,
                width=100,
                command=lambda: self.block_device(dev_id)
            ).pack(side="left", padx=5)
        
        elif estado == 'BLOQUEADO':
            ctk.CTkButton(
                right,
                text="♻️ Reciclar",
                font=("Arial", 11, "bold"),
                fg_color=self.colors['primary'],
                hover_color="#2563eb",
                corner_radius=8,
                width=100,
                command=lambda: self.recycle_device(dev_id)
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                right,
                text="✓ Re-autorizar",
                font=("Arial", 11, "bold"),
                fg_color=self.colors['success'],
                hover_color="#059669",
                corner_radius=8,
                width=120,
                command=lambda: self.reauthorize_device(dev_id)
            ).pack(side="left", padx=5)
        
        # Detalles
        details = ctk.CTkFrame(content, fg_color="transparent")
        details.pack(fill="x", pady=(15, 0))
        
        # Información técnica en grid
        info_grid = ctk.CTkFrame(details, fg_color="transparent")
        info_grid.pack(fill="x")
        
        info_items = [
            ("Sistema", device_info.get('system', 'N/A')),
            ("Procesador", device_info.get('machine', 'N/A')),
            ("Registrado", self.format_date(fecha_reg)),
        ]
        
        if fecha_auth:
            info_items.append(("Autorizado", self.format_date(fecha_auth)))
        
        if ultimo_acc:
            info_items.append(("Último acceso", self.format_date(ultimo_acc)))
        
        col = 0
        for label, value in info_items:
            item = ctk.CTkFrame(info_grid, fg_color="transparent")
            item.grid(row=0, column=col, sticky="w", padx=(0, 30))
            
            ctk.CTkLabel(
                item,
                text=f"{label}:",
                font=("Arial", 10),
                text_color=self.colors['text_secondary']
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                item,
                text=value,
                font=("Arial", 11, "bold"),
                text_color=self.colors['text']
            ).pack(anchor="w")
            
            col += 1
    
    def format_date(self, date_obj):
        """Formatear fecha"""
        if not date_obj:
            return "N/A"
        
        try:
            if isinstance(date_obj, str):
                date_obj = datetime.fromisoformat(str(date_obj))
            return date_obj.strftime("%d/%m/%Y %H:%M")
        except:
            return str(date_obj)
    
    def filter_devices(self, filter_type):
        """Filtrar dispositivos"""
        self.current_filter = filter_type
        
        # Actualizar botones
        for tab_id, btn in self.tab_buttons.items():
            if tab_id == filter_type:
                btn.configure(fg_color=self.colors['primary'])
            else:
                btn.configure(fg_color=self.colors['card'])
        
        self.load_devices()
    
    def authorize_device(self, device_id):
        """Autorizar un dispositivo"""
        if messagebox.askyesno("Confirmar", 
                              "¿Autorizar este dispositivo para acceder al sistema?"):
            try:
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                
                # Actualizar dispositivo
                cursor.execute("""
                    UPDATE dispositivos_autorizados
                    SET estado = 'AUTORIZADO', autorizado = TRUE, fecha_autorizacion = NOW()
                    WHERE id_dispositivo = %s
                """, (device_id,))
                
                # Registrar evento
                cursor.execute("""
                    INSERT INTO dispositivos_eventos
                    (id_dispositivo, device_id, estado_anterior, estado_nuevo, razon, usuario_admin)
                    SELECT id_dispositivo, device_id, 'PENDING', 'AUTORIZADO', 
                           'Autorizado por administrador', %s
                    FROM dispositivos_autorizados WHERE id_dispositivo = %s
                """, (self.user_data.get('username'), device_id))
                
                conn.commit()
                
                messagebox.showinfo("Éxito", "Dispositivo autorizado correctamente")
                self.load_devices()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error autorizando dispositivo: {str(e)}")
    
    def block_device(self, device_id):
        """Bloquear un dispositivo con razón"""
        dialog = ctk.CTkTopLevel(self.root)
        dialog.title("Bloquear Dispositivo")
        dialog.geometry("400x200")
        dialog.attributes('-topmost', True)
        
        ctk.CTkLabel(
            dialog,
            text="Razón de bloqueo:",
            font=("Arial", 12, "bold")
        ).pack(padx=20, pady=10)
        
        razon_entry = ctk.CTkEntry(dialog, placeholder_text="Ej: Comportamiento malicioso detectado")
        razon_entry.pack(fill="x", padx=20, pady=10)
        
        def confirm_block():
            razon = razon_entry.get() or "Bloqueado por administrador"
            
            try:
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                
                # Actualizar dispositivo
                cursor.execute("""
                    UPDATE dispositivos_autorizados
                    SET estado = 'BLOQUEADO', activo = FALSE, razon_bloqueo = %s
                    WHERE id_dispositivo = %s
                """, (razon, device_id))
                
                # Registrar evento
                cursor.execute("""
                    INSERT INTO dispositivos_eventos
                    (id_dispositivo, device_id, estado_anterior, estado_nuevo, razon, usuario_admin)
                    SELECT id_dispositivo, device_id, 'AUTORIZADO', 'BLOQUEADO', %s, %s
                    FROM dispositivos_autorizados WHERE id_dispositivo = %s
                """, (razon, self.user_data.get('username'), device_id))
                
                conn.commit()
                
                messagebox.showinfo("Éxito", "Dispositivo bloqueado correctamente")
                dialog.destroy()
                self.load_devices()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error bloqueando dispositivo: {str(e)}")
        
        ctk.CTkButton(
            dialog,
            text="Bloquear",
            fg_color=self.colors['danger'],
            command=confirm_block
        ).pack(pady=10)
    
    def recycle_device(self, device_id):
        """Reciclar un dispositivo bloqueado"""
        if messagebox.askyesno("Confirmar Reciclaje",
                              "¿Reciclar este dispositivo para reasignar su ID?\n"
                              "Esto marcará el registro como disponible para reciclaje."):
            try:
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                
                # Obtener info del dispositivo
                cursor.execute("""
                    SELECT id_dispositivo, device_id, device_name, id_usuario, estado, fecha_bloqueo
                    FROM dispositivos_autorizados
                    WHERE id_dispositivo = %s
                """, (device_id,))
                
                device = cursor.fetchone()
                
                if device:
                    # Registrar en tabla de reciclaje
                    cursor.execute("""
                        INSERT INTO dispositivos_reciclaje
                        (id_dispositivo, device_id, device_name, id_usuario, estado_anterior, 
                         fecha_bloqueo, puede_reasignar)
                        VALUES (%s, %s, %s, %s, %s, NOW(), TRUE)
                    """, (device_id, device.get('device_id'), device.get('device_name'),
                          device.get('id_usuario'), device.get('estado')))
                    
                    # Soft-delete del dispositivo
                    cursor.execute("""
                        UPDATE dispositivos_autorizados
                        SET estado = 'ELIMINADO', fecha_eliminacion = NOW()
                        WHERE id_dispositivo = %s
                    """, (device_id,))
                    
                    # Registrar evento
                    cursor.execute("""
                        INSERT INTO dispositivos_eventos
                        (id_dispositivo, device_id, estado_anterior, estado_nuevo, razon, usuario_admin)
                        VALUES (%s, %s, 'BLOQUEADO', 'ELIMINADO', 'Reciclado para reasignación', %s)
                    """, (device_id, device.get('device_id'), self.user_data.get('username')))
                    
                    conn.commit()
                    
                    messagebox.showinfo("Éxito", "Dispositivo reciclado correctamente")
                    self.load_devices()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error reciclando dispositivo: {str(e)}")
    
    def reauthorize_device(self, device_id):
        """Re-autorizar un dispositivo bloqueado"""
        if messagebox.askyesno("Confirmar",
                              "¿Re-autorizar este dispositivo?\n"
                              "El dispositivo podrá acceder al sistema nuevamente."):
            try:
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                
                # Actualizar dispositivo
                cursor.execute("""
                    UPDATE dispositivos_autorizados
                    SET estado = 'AUTORIZADO', activo = TRUE, autorizado = TRUE,
                        razon_bloqueo = NULL, fecha_autorizacion = NOW()
                    WHERE id_dispositivo = %s
                """, (device_id,))
                
                # Registrar evento
                cursor.execute("""
                    INSERT INTO dispositivos_eventos
                    (id_dispositivo, device_id, estado_anterior, estado_nuevo, razon, usuario_admin)
                    SELECT id_dispositivo, device_id, 'BLOQUEADO', 'AUTORIZADO', 
                           'Re-autorizado por administrador', %s
                    FROM dispositivos_autorizados WHERE id_dispositivo = %s
                """, (self.user_data.get('username'), device_id))
                
                conn.commit()
                
                messagebox.showinfo("Éxito", "Dispositivo re-autorizado correctamente")
                self.load_devices()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error re-autorizando dispositivo: {str(e)}")
    
    def update_stats(self, devices):
        """Actualizar estadísticas"""
        total = len(devices)
        pending = sum(1 for d in devices if d.get('estado') == 'PENDING')
        authorized = sum(1 for d in devices if d.get('estado') == 'AUTORIZADO')
        blocked = sum(1 for d in devices if d.get('estado') == 'BLOQUEADO')
        
        stats_text = f"Total: {total} | ⏳ Pendientes: {pending} | ✅ Autorizados: {authorized} | 🔴 Bloqueados: {blocked}"
        self.stats_label.configure(text=stats_text)


def launch_device_admin(user_data):
    """Launch device admin window"""
    import tkinter as tk
    root = tk.Tk()
    app = DeviceAdminApp(root, user_data)
    root.mainloop()
