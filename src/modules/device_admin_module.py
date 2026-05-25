#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Administración de Dispositivos - GUI
DISFRULEG - Sistema de Seguridad
Versión moderna con CustomTkinter
"""

import customtkinter as ctk
from src.utils.responsive_manager import ResponsiveMixin
from tkinter import messagebox
from datetime import datetime
import sys
import os

# Imports del sistema
from src.database.db_manager import db_manager
from src.security.device_manager import device_manager
from src.config import debug_print
from src.theme import COLORS, FONTS


class DeviceAdminModule(ResponsiveMixin, ctk.CTkToplevel):
    """Módulo de Administración de Dispositivos - Interfaz Gráfica"""
    
    def __init__(self, parent, user_data=None):
        super().__init__(parent)
        
        self.user_data = user_data
        self.conn = db_manager.get_connection()
        self.current_filter = 'all'
        self.devices_data = []
        
        # Configuración de ventana
        self.title("Administración de Dispositivos - DISFRULEG")
        self.make_responsive('small')
        
        # Configuración de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar datos iniciales
        self.load_devices()
        
        # Mantener ventana al frente
        self.lift()
        self.focus_force()
    
    def create_interface(self):
        """Crear interfaz principal"""
        
        # HEADER
        self.create_header()
        
        # TOOLBAR con filtros
        self.create_toolbar()
        
        # MAIN CONTENT - Split view
        self.create_main_content()
        
        # STATUS BAR
        self.create_status_bar()
    
    def create_header(self):
        """Crear header del módulo"""
        header = ctk.CTkFrame(self, fg_color=("#1a1a1a", "#1a1a1a"), height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        content = ctk.CTkFrame(header, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=15)
        
        # Icono y título
        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="🔐",
            font=("Arial", 32)
        ).pack(side="left", padx=(0, 15))
        
        labels_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        labels_frame.pack(side="left")
        
        ctk.CTkLabel(
            labels_frame,
            text="Administración de Dispositivos",
            font=("Arial", 20, "bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            labels_frame,
            text="Control de acceso y autorización de dispositivos",
            font=("Arial", 11),
            text_color="gray60",
            anchor="w"
        ).pack(anchor="w")
        
        # Usuario actual
        if self.user_data:
            user_label = ctk.CTkLabel(
                content,
                text=f"👤 {self.user_data.get('nombre_completo', 'Usuario')}",
                font=("Arial", 12),
                text_color="gray70"
            )
            user_label.pack(side="right", padx=10)
    
    def create_toolbar(self):
        """Crear toolbar con filtros y acciones"""
        toolbar = ctk.CTkFrame(self, fg_color=("#2a2a2a", "#2a2a2a"), height=60)
        toolbar.pack(fill="x", padx=20, pady=(10, 0))
        toolbar.pack_propagate(False)
        
        content = ctk.CTkFrame(toolbar, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)
        
        # FILTROS
        filters_frame = ctk.CTkFrame(content, fg_color="transparent")
        filters_frame.pack(side="left")
        
        ctk.CTkLabel(
            filters_frame,
            text="Filtrar:",
            font=("Arial", 11, "bold"),
            text_color="gray70"
        ).pack(side="left", padx=(0, 10))
        
        filters = [
            ("all", "Todos", "#6b7280"),
            ("pending", "Pendientes", "#f59e0b"),
            ("authorized", "Autorizados", "#10b981"),
            ("blocked", "Bloqueados", "#ef4444")
        ]
        
        self.filter_buttons = {}
        for filter_key, label, color in filters:
            btn = ctk.CTkButton(
                filters_frame,
                text=label,
                width=100,
                height=30,
                corner_radius=6,
                fg_color=color if self.current_filter == filter_key else "transparent",
                border_width=1 if self.current_filter != filter_key else 0,
                border_color=color,
                hover_color=color,
                font=("Arial", 11),
                command=lambda k=filter_key: self.apply_filter(k)
            )
            btn.pack(side="left", padx=3)
            self.filter_buttons[filter_key] = (btn, color)
        
        # ACCIONES
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(side="right")
        
        ctk.CTkButton(
            actions_frame,
            text="🔄 Recargar",
            width=100,
            height=30,
            corner_radius=6,
            fg_color=COLORS['primary'],
            hover_color="#2563eb",
            font=("Arial", 11),
            command=self.load_devices
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            actions_frame,
            text="📋 Ver Logs",
            width=100,
            height=30,
            corner_radius=6,
            fg_color=COLORS['secondary'],
            hover_color="#4b5563",
            font=("Arial", 11),
            command=self.show_logs_window
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            actions_frame,
            text="🖥️ Este Dispositivo",
            width=130,
            height=30,
            corner_radius=6,
            fg_color="#6366f1",
            hover_color="#4f46e5",
            font=("Arial", 11),
            command=self.show_current_device
        ).pack(side="left", padx=3)
    
    def create_main_content(self):
        """Crear contenido principal con lista de dispositivos"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Lista de dispositivos (scrollable)
        self.devices_list = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=10
        )
        self.devices_list.pack(fill="both", expand=True)
    
    def create_status_bar(self):
        """Crear barra de estado"""
        status_bar = ctk.CTkFrame(self, fg_color=("#1a1a1a", "#1a1a1a"), height=35)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_bar,
            text="● Listo",
            font=("Arial", 10),
            text_color="gray60"
        )
        self.status_label.pack(side="left", padx=20)
        
        self.count_label = ctk.CTkLabel(
            status_bar,
            text="0 dispositivos",
            font=("Arial", 10),
            text_color="gray60"
        )
        self.count_label.pack(side="right", padx=20)
    
    def load_devices(self, filter_type=None):
        """Cargar dispositivos desde la base de datos"""
        if filter_type is None:
            filter_type = self.current_filter
        
        self.update_status("Cargando dispositivos...")
        
        try:
            cursor = self.conn.cursor()
            
            # Query según filtro
            if filter_type == 'pending':
                query = """
                    SELECT id_dispositivo, device_id, device_name, autorizado, activo, 
                           fecha_registro, fecha_autorizacion, ultimo_acceso
                    FROM dispositivos_autorizados
                    WHERE autorizado = FALSE
                    ORDER BY fecha_registro DESC
                """
            elif filter_type == 'authorized':
                query = """
                    SELECT id_dispositivo, device_id, device_name, autorizado, activo, 
                           fecha_registro, fecha_autorizacion, ultimo_acceso
                    FROM dispositivos_autorizados
                    WHERE autorizado = TRUE AND activo = TRUE
                    ORDER BY ultimo_acceso DESC
                """
            elif filter_type == 'blocked':
                query = """
                    SELECT id_dispositivo, device_id, device_name, autorizado, activo, 
                           fecha_registro, fecha_autorizacion, ultimo_acceso
                    FROM dispositivos_autorizados
                    WHERE activo = FALSE
                    ORDER BY fecha_registro DESC
                """
            else:  # all
                query = """
                    SELECT id_dispositivo, device_id, device_name, autorizado, activo, 
                           fecha_registro, fecha_autorizacion, ultimo_acceso
                    FROM dispositivos_autorizados
                    ORDER BY fecha_registro DESC
                """
            
            cursor.execute(query)
            self.devices_data = cursor.fetchall()
            
            # Actualizar UI
            self.render_devices()
            self.update_status("● Listo")
            self.count_label.configure(text=f"{len(self.devices_data)} dispositivos")
            
        except Exception as e:
            debug_print(f"Error loading devices: {e}")
            messagebox.showerror("Error", f"Error al cargar dispositivos:\n{str(e)}")
            self.update_status("● Error")
    
    def render_devices(self):
        """Renderizar lista de dispositivos"""
        # Limpiar lista actual
        for widget in self.devices_list.winfo_children():
            widget.destroy()
        
        if not self.devices_data:
            # Mensaje vacío
            empty_frame = ctk.CTkFrame(self.devices_list, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, pady=100)
            
            ctk.CTkLabel(
                empty_frame,
                text="📭",
                font=("Arial", 48)
            ).pack()
            
            ctk.CTkLabel(
                empty_frame,
                text="No hay dispositivos en esta categoría",
                font=("Arial", 14),
                text_color="gray60"
            ).pack(pady=10)
            
            return
        
        # Renderizar cada dispositivo
        for device in self.devices_data:
            self.create_device_card(device)
    
    def create_device_card(self, device):
        """Crear tarjeta de dispositivo"""
        # Extraer datos (soporte tupla/dict)
        if isinstance(device, dict):
            dev_id = device['id_dispositivo']
            device_hash = device['device_id']
            name = device['device_name']
            autorizado = device['autorizado']
            activo = device['activo']
            fecha_reg = device['fecha_registro']
            fecha_auth = device['fecha_autorizacion']
            ultimo_acc = device['ultimo_acceso']
        else:
            dev_id = device[0]
            device_hash = device[1]
            name = device[2]
            autorizado = device[3]
            activo = device[4]
            fecha_reg = device[5]
            fecha_auth = device[6]
            ultimo_acc = device[7]
        
        # Determinar color según estado
        if not autorizado:
            border_color = "#f59e0b"  # Amarillo - Pendiente
        elif not activo:
            border_color = "#ef4444"  # Rojo - Bloqueado
        else:
            border_color = "#10b981"  # Verde - Autorizado
        
        # Card principal
        card = ctk.CTkFrame(
            self.devices_list,
            fg_color=("#1a1a1a", "#1a1a1a"),
            border_color=border_color,
            border_width=2,
            corner_radius=10
        )
        card.pack(fill="x", padx=10, pady=5)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Header de la card
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Icono de estado
        if not autorizado:
            status_icon = "⏳"
            status_text = "PENDIENTE"
            status_color = "#f59e0b"
        elif not activo:
            status_icon = "🔴"
            status_text = "BLOQUEADO"
            status_color = "#ef4444"
        else:
            status_icon = "✅"
            status_text = "AUTORIZADO"
            status_color = "#10b981"
        
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.pack(side="left")
        
        ctk.CTkLabel(
            status_frame,
            text=status_icon,
            font=("Arial", 20)
        ).pack(side="left", padx=(0, 5))
        
        info_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        info_frame.pack(side="left")
        
        ctk.CTkLabel(
            info_frame,
            text=name,
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"ID: {dev_id} • {status_text}",
            font=("Arial", 10),
            text_color=status_color,
            anchor="w"
        ).pack(anchor="w")
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right")
        
        if not autorizado:
            # Botón AUTORIZAR
            ctk.CTkButton(
                actions_frame,
                text="✓ Autorizar",
                width=100,
                height=30,
                corner_radius=6,
                fg_color="#10b981",
                hover_color="#059669",
                font=("Arial", 11, "bold"),
                command=lambda: self.authorize_device(dev_id)
            ).pack(side="left", padx=3)
        
        if autorizado and activo:
            # Botón BLOQUEAR
            ctk.CTkButton(
                actions_frame,
                text="🚫 Bloquear",
                width=100,
                height=30,
                corner_radius=6,
                fg_color="#ef4444",
                hover_color="#dc2626",
                font=("Arial", 11),
                command=lambda: self.block_device(dev_id, name)
            ).pack(side="left", padx=3)
        
        if not activo:
            # Botón REACTIVAR
            ctk.CTkButton(
                actions_frame,
                text="🔄 Reactivar",
                width=100,
                height=30,
                corner_radius=6,
                fg_color="#10b981",
                hover_color="#059669",
                font=("Arial", 11),
                command=lambda: self.reactivate_device(dev_id)
            ).pack(side="left", padx=3)
        
        # Información detallada
        details_frame = ctk.CTkFrame(content, fg_color=("#0a0a0a", "#0a0a0a"), corner_radius=8)
        details_frame.pack(fill="x", pady=(5, 0))
        
        details_content = ctk.CTkFrame(details_frame, fg_color="transparent")
        details_content.pack(fill="x", padx=15, pady=10)
        
        # Grid de información
        info_items = [
            ("Device ID:", device_hash[:32] + "..." if len(device_hash) > 32 else device_hash),
            ("Registrado:", str(fecha_reg)),
        ]
        
        if fecha_auth:
            info_items.append(("Autorizado:", str(fecha_auth)))
        
        if ultimo_acc:
            info_items.append(("Último acceso:", str(ultimo_acc)))
        
        for i, (label, value) in enumerate(info_items):
            item_frame = ctk.CTkFrame(details_content, fg_color="transparent")
            item_frame.grid(row=i//2, column=(i%2)*2, sticky="w", padx=10, pady=3)
            
            ctk.CTkLabel(
                item_frame,
                text=label,
                font=("Arial", 10, "bold"),
                text_color="gray60"
            ).pack(side="left", padx=(0, 5))
            
            ctk.CTkLabel(
                item_frame,
                text=value,
                font=("Arial", 10),
                text_color="white"
            ).pack(side="left")
    
    def authorize_device(self, device_id):
        """Autorizar un dispositivo"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE dispositivos_autorizados
                SET autorizado = TRUE, fecha_autorizacion = NOW()
                WHERE id_dispositivo = %s
            """, (device_id,))
            
            if cursor.rowcount > 0:
                self.conn.commit()
                messagebox.showinfo(
                    "Éxito",
                    f"Dispositivo ID {device_id} autorizado correctamente"
                )
                self.load_devices()
            else:
                messagebox.showerror("Error", "No se encontró el dispositivo")
                
        except Exception as e:
            debug_print(f"Error authorizing device: {e}")
            messagebox.showerror("Error", f"Error al autorizar:\n{str(e)}")
    
    def block_device(self, device_id, device_name):
        """Bloquear un dispositivo"""
        if messagebox.askyesno(
            "Confirmar Bloqueo",
            f"¿Está seguro de bloquear el dispositivo?\n\n{device_name}\nID: {device_id}"
        ):
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    UPDATE dispositivos_autorizados
                    SET activo = FALSE
                    WHERE id_dispositivo = %s
                """, (device_id,))
                
                if cursor.rowcount > 0:
                    self.conn.commit()
                    messagebox.showinfo(
                        "Éxito",
                        f"Dispositivo ID {device_id} bloqueado"
                    )
                    self.load_devices()
                else:
                    messagebox.showerror("Error", "No se encontró el dispositivo")
                    
            except Exception as e:
                debug_print(f"Error blocking device: {e}")
                messagebox.showerror("Error", f"Error al bloquear:\n{str(e)}")
    
    def reactivate_device(self, device_id):
        """Reactivar un dispositivo"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE dispositivos_autorizados
                SET activo = TRUE
                WHERE id_dispositivo = %s
            """, (device_id,))
            
            if cursor.rowcount > 0:
                self.conn.commit()
                messagebox.showinfo(
                    "Éxito",
                    f"Dispositivo ID {device_id} reactivado"
                )
                self.load_devices()
            else:
                messagebox.showerror("Error", "No se encontró el dispositivo")
                
        except Exception as e:
            debug_print(f"Error reactivating device: {e}")
            messagebox.showerror("Error", f"Error al reactivar:\n{str(e)}")
    
    def apply_filter(self, filter_type):
        """Aplicar filtro"""
        self.current_filter = filter_type
        
        # Actualizar estilos de botones
        for key, (btn, color) in self.filter_buttons.items():
            if key == filter_type:
                btn.configure(fg_color=color, border_width=0)
            else:
                btn.configure(fg_color="transparent", border_width=1)
        
        self.load_devices(filter_type)
    
    def show_logs_window(self):
        """Mostrar ventana de logs"""
        LogsWindow(self, self.conn)
    
    def show_current_device(self):
        """Mostrar información del dispositivo actual"""
        CurrentDeviceWindow(self, self.conn)
    
    def update_status(self, text):
        """Actualizar barra de estado"""
        self.status_label.configure(text=text)
        self.update_idletasks()
    
    def on_closing(self):
        """Manejar cierre de ventana"""
        self.destroy()


class LogsWindow(ResponsiveMixin, ctk.CTkToplevel):
    """Ventana de logs de acceso"""
    
    def __init__(self, parent, conn):
        super().__init__(parent)
        
        self.conn = conn
        
        self.title("Registro de Accesos")
        self.make_responsive('dialog')
        
        self.create_interface()
        self.load_logs()
        
        self.lift()
        self.focus_force()
    
    def create_interface(self):
        """Crear interfaz"""
        # Header
        header = ctk.CTkFrame(self, fg_color=("#1a1a1a", "#1a1a1a"), height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📋 Registro de Accesos (Últimos 50)",
            font=("Arial", 16, "bold")
        ).pack(pady=20, padx=20)
        
        # Lista de logs
        self.logs_list = ctk.CTkScrollableFrame(
            self,
            fg_color=("#2a2a2a", "#2a2a2a")
        )
        self.logs_list.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Botón cerrar
        ctk.CTkButton(
            self,
            text="Cerrar",
            width=100,
            height=35,
            command=self.destroy
        ).pack(pady=10)
    
    def load_logs(self):
        """Cargar logs"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT l.username, l.modulo, l.accion, l.fecha_hora, l.exito,
                       d.device_name
                FROM log_accesos_dispositivos l
                LEFT JOIN dispositivos_autorizados d ON l.device_id = d.device_id
                ORDER BY l.fecha_hora DESC
                LIMIT 50
            """)
            
            logs = cursor.fetchall()
            
            if not logs:
                ctk.CTkLabel(
                    self.logs_list,
                    text="No hay logs registrados",
                    font=("Arial", 12),
                    text_color="gray60"
                ).pack(pady=50)
                return
            
            for log in logs:
                self.create_log_entry(log)
                
        except Exception as e:
            debug_print(f"Error loading logs: {e}")
            messagebox.showerror("Error", f"Error al cargar logs:\n{str(e)}")
    
    def create_log_entry(self, log):
        """Crear entrada de log"""
        if isinstance(log, dict):
            username = log['username']
            modulo = log['modulo']
            accion = log['accion']
            fecha = log['fecha_hora']
            exito = log['exito']
            device_name = log['device_name'] or "Dispositivo desconocido"
        else:
            username = log[0]
            modulo = log[1]
            accion = log[2]
            fecha = log[3]
            exito = log[4]
            device_name = log[5] or "Dispositivo desconocido"
        
        frame = ctk.CTkFrame(
            self.logs_list,
            fg_color=("#1a1a1a", "#1a1a1a"),
            corner_radius=8
        )
        frame.pack(fill="x", padx=5, pady=3)
        
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)
        
        # Icono de éxito
        icon = "✅" if exito else "❌"
        
        ctk.CTkLabel(
            content,
            text=f"{icon} {fecha}",
            font=("Arial", 11, "bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            content,
            text=f"👤 {username} • 📱 {device_name}",
            font=("Arial", 10),
            text_color="gray60",
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))
        
        ctk.CTkLabel(
            content,
            text=f"📦 {modulo} • {accion}",
            font=("Arial", 10),
            text_color="gray70",
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))


class CurrentDeviceWindow(ResponsiveMixin, ctk.CTkToplevel):
    """Ventana de información del dispositivo actual"""
    
    def __init__(self, parent, conn):
        super().__init__(parent)
        
        self.conn = conn
        
        self.title("Información del Dispositivo Actual")
        self.make_responsive('dialog')
        
        self.create_interface()
        self.load_device_info()
        
        self.lift()
        self.focus_force()
    
    def create_interface(self):
        """Crear interfaz"""
        # Header
        header = ctk.CTkFrame(self, fg_color=("#1a1a1a", "#1a1a1a"), height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="🖥️ Este Dispositivo",
            font=("Arial", 16, "bold")
        ).pack(pady=20, padx=20)
        
        # Contenido
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("#2a2a2a", "#2a2a2a")
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Botón cerrar
        ctk.CTkButton(
            self,
            text="Cerrar",
            width=100,
            height=35,
            command=self.destroy
        ).pack(pady=10)
    
    def load_device_info(self):
        """Cargar información del dispositivo"""
        try:
            current_id = device_manager.get_device_id()
            device_name = device_manager.get_device_name() if hasattr(device_manager, 'get_device_name') else "Desconocido"
            
            # Device ID
            self.create_info_section("Device ID", current_id)
            
            # Nombre
            self.create_info_section("Nombre", device_name)
            
            # Información técnica
            tech_frame = ctk.CTkFrame(self.content_frame, fg_color=("#1a1a1a", "#1a1a1a"), corner_radius=10)
            tech_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(
                tech_frame,
                text="📊 Información Técnica",
                font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=15, pady=(10, 5))
            
            for key, value in device_manager.device_info.items():
                info_line = ctk.CTkFrame(tech_frame, fg_color="transparent")
                info_line.pack(fill="x", padx=15, pady=2)
                
                ctk.CTkLabel(
                    info_line,
                    text=f"{key}:",
                    font=("Arial", 10, "bold"),
                    text_color="gray60"
                ).pack(side="left", padx=(0, 10))
                
                ctk.CTkLabel(
                    info_line,
                    text=str(value),
                    font=("Arial", 10),
                    text_color="white"
                ).pack(side="left")
            
            ctk.CTkLabel(tech_frame, text="").pack(pady=5)
            
            # Estado en BD
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT autorizado, activo, fecha_registro, ultimo_acceso
                FROM dispositivos_autorizados
                WHERE device_id = %s
            """, (current_id,))
            
            result = cursor.fetchone()
            
            status_frame = ctk.CTkFrame(self.content_frame, fg_color=("#1a1a1a", "#1a1a1a"), corner_radius=10)
            status_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(
                status_frame,
                text="📊 Estado en Base de Datos",
                font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=15, pady=(10, 5))
            
            if result:
                if isinstance(result, dict):
                    autorizado = result['autorizado']
                    activo = result['activo']
                    fecha_reg = result['fecha_registro']
                    ultimo_acc = result['ultimo_acceso']
                else:
                    autorizado = result[0]
                    activo = result[1]
                    fecha_reg = result[2]
                    ultimo_acc = result[3]
                
                self.create_status_item(status_frame, "Autorizado", "✅ Sí" if autorizado else "❌ No")
                self.create_status_item(status_frame, "Activo", "✅ Sí" if activo else "❌ No")
                self.create_status_item(status_frame, "Registrado", str(fecha_reg))
                if ultimo_acc:
                    self.create_status_item(status_frame, "Último acceso", str(ultimo_acc))
            else:
                ctk.CTkLabel(
                    status_frame,
                    text="⚠️ Este dispositivo NO está registrado en la base de datos",
                    font=("Arial", 11),
                    text_color="#f59e0b"
                ).pack(padx=15, pady=10)
            
            ctk.CTkLabel(status_frame, text="").pack(pady=5)
                
        except Exception as e:
            debug_print(f"Error loading device info: {e}")
            messagebox.showerror("Error", f"Error al cargar información:\n{str(e)}")
    
    def create_info_section(self, label, value):
        """Crear sección de información"""
        frame = ctk.CTkFrame(self.content_frame, fg_color=("#1a1a1a", "#1a1a1a"), corner_radius=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            content,
            text=label,
            font=("Arial", 10, "bold"),
            text_color="gray60",
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            content,
            text=value,
            font=("Arial", 11),
            text_color="white",
            anchor="w",
            wraplength=600
        ).pack(anchor="w", pady=(5, 0))
    
    def create_status_item(self, parent, label, value):
        """Crear item de estado"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", padx=15, pady=2)
        
        ctk.CTkLabel(
            item_frame,
            text=f"{label}:",
            font=("Arial", 10, "bold"),
            text_color="gray60"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            item_frame,
            text=value,
            font=("Arial", 10),
            text_color="white"
        ).pack(side="left")


# Función de lanzamiento para integración con el sistema
def launch_device_admin_module(parent=None, user_data=None):
    """
    Función para lanzar el módulo desde el sistema principal
    
    Args:
        parent: Ventana padre (opcional)
        user_data: Datos del usuario actual
    
    Returns:
        bool: True si se lanzó correctamente
    """
    try:
        debug_print("Launching Device Admin Module...")
        
        # Verificar permisos de usuario
        if user_data:
            user_role = user_data.get('rol', 'usuario')
            if user_role not in ['admin', 'superadmin']:
                messagebox.showwarning(
                    "Acceso Denegado",
                    "No tienes permisos para acceder a este módulo.\n\n"
                    "Este módulo requiere permisos de administrador."
                )
                return False
        
        # Crear ventana del módulo
        if parent:
            module = DeviceAdminModule(parent, user_data)
        else:
            # Si no hay parent, crear ventana raíz temporal
            root = ctk.CTk()
            root.withdraw()  # Ocultar ventana raíz
            module = DeviceAdminModule(root, user_data)
        
        debug_print("Device Admin Module launched successfully")
        return True
        
    except Exception as e:
        debug_print(f"Error launching Device Admin Module: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror(
            "Error",
            f"No se pudo abrir el módulo de administración de dispositivos:\n\n{str(e)}"
        )
        return False


# Para testing independiente
if __name__ == "__main__":
    # Simular usuario admin para testing
    test_user = {
        'nombre_completo': 'Admin Test',
        'rol': 'admin',
        'username': 'admin'
    }
    
    # Crear ventana de prueba
    root = ctk.CTk()
    root.title("Test - Device Admin")
    root.geometry("400x300")
    
    ctk.CTkLabel(
        root,
        text="Testing Device Admin Module",
        font=("Arial", 16, "bold")
    ).pack(pady=20)
    
    ctk.CTkButton(
        root,
        text="Abrir Administrador de Dispositivos",
        width=250,
        height=40,
        command=lambda: launch_device_admin_module(root, test_user)
    ).pack(pady=10)
    
    ctk.CTkButton(
        root,
        text="Salir",
        width=250,
        height=40,
        command=root.quit
    ).pack(pady=10)
    
    root.mainloop()