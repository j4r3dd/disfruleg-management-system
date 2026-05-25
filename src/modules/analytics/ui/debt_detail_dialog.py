# -*- coding: utf-8 -*-
"""
Debt Detail Dialog - Analytics Module
Ventana para mostrar clientes con deudas pendientes
"""
import customtkinter as ctk
from tkinter import messagebox
import logging
from typing import List

logger = logging.getLogger(__name__)


class DebtDetailDialog(ctk.CTkToplevel):
    """Dialog mostrando clientes con deudas pendientes"""

    def __init__(self, parent, analytics_service):
        super().__init__(parent)

        self.analytics_service = analytics_service

        # Configurar ventana
        self.title("Clientes con Deudas Pendientes")
        self.geometry("900x650")

        # Colores
        self.colors = {
            'bg_primary': '#0A0A0A',
            'bg_secondary': '#1A1A1A',
            'bg_card': '#242424',
            'bg_surface': '#2E2E2E',
            'accent': '#8B5CF6',
            'success': '#10B981',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'text_primary': '#F5F5F5',
            'text_secondary': '#A1A1A1',
            'text_muted': '#6B6B6B',
            'hover_surface': '#383838',
        }

        self.configure(fg_color=self.colors['bg_primary'])

        # Evitar errores de transparencia en macOS
        try:
            self.attributes('-alpha', 1.0)
        except:
            pass

        # Crear UI
        self.create_ui()

        # Cargar datos
        self.load_debt_data()

        # Centrar ventana
        self.center_window()

        # Focus
        self.lift()
        self.focus_force()

    def center_window(self):
        """Centrar ventana en pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_ui(self):
        """Crear interfaz del dialog"""
        # Header
        header = ctk.CTkFrame(
            self,
            fg_color=self.colors['bg_surface'],
            corner_radius=0,
            height=70
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)

        # Título
        ctk.CTkLabel(
            header_content,
            text="⚠️ Clientes con Deudas Pendientes",
            font=("Arial", 24, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")

        # Total label (se llenará después)
        self.total_label = ctk.CTkLabel(
            header_content,
            text="Total: $0.00",
            font=("Arial", 16, "bold"),
            text_color=self.colors['danger']
        )
        self.total_label.pack(side="right")

        # Container principal con scroll
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.colors['bg_primary']
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Footer con botón cerrar
        footer = ctk.CTkFrame(
            self,
            fg_color=self.colors['bg_surface'],
            corner_radius=0,
            height=60
        )
        footer.pack(fill="x")
        footer.pack_propagate(False)

        ctk.CTkButton(
            footer,
            text="Cerrar",
            font=("Arial", 14),
            fg_color=self.colors['accent'],
            hover_color="#7C3AED",
            height=38,
            width=120,
            command=self.destroy
        ).pack(side="right", padx=30, pady=11)

    def load_debt_data(self):
        """Cargar datos de clientes con deudas"""
        # Limpiar contenedor
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Mostrar indicador de carga
        loading = ctk.CTkLabel(
            self.scroll_frame,
            text="⟳ Cargando datos...",
            font=("Arial", 14),
            text_color=self.colors['text_secondary']
        )
        loading.pack(pady=40)

        # Actualizar UI
        self.update()

        try:
            # Obtener clientes con deudas del servicio
            clients_with_debts = self.analytics_service.get_clients_with_debts()

            # Limpiar loading
            loading.destroy()

            if not clients_with_debts:
                # No hay deudas
                ctk.CTkLabel(
                    self.scroll_frame,
                    text="✓ No hay clientes con deudas pendientes",
                    font=("Arial", 16),
                    text_color=self.colors['success']
                ).pack(pady=60)

                self.total_label.configure(text="Total: $0.00")
                return

            # Calcular total
            total_debt = sum(float(client.saldo_pendiente) for client in clients_with_debts)
            self.total_label.configure(text=f"Total: ${total_debt:,.2f}")

            # Mostrar header de tabla
            self.create_table_header()

            # Mostrar cada cliente
            for index, client in enumerate(clients_with_debts):
                self.create_client_row(client, index)

        except Exception as e:
            loading.destroy()
            logger.error(f"Error loading debt data: {e}")
            ctk.CTkLabel(
                self.scroll_frame,
                text=f"❌ Error cargando datos: {str(e)}",
                font=("Arial", 14),
                text_color=self.colors['danger']
            ).pack(pady=40)

    def create_table_header(self):
        """Crear header de tabla"""
        header = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.colors['bg_surface'],
            corner_radius=8,
            height=44
        )
        header.pack(fill="x", pady=(0, 12))
        header.pack_propagate(False)

        # Columnas
        columns = [
            ("Cliente", 0.30),
            ("Grupo", 0.20),
            ("# Deudas", 0.15),
            ("Total Pagado", 0.17),
            ("Saldo Pendiente", 0.18)
        ]

        for col_name, width_ratio in columns:
            label = ctk.CTkLabel(
                header,
                text=col_name,
                font=("Arial", 12, "bold"),
                text_color=self.colors['text_primary'],
                anchor="w"
            )
            label.place(relx=sum(c[1] for c in columns[:columns.index((col_name, width_ratio))]),
                       rely=0,
                       relwidth=width_ratio,
                       relheight=1)

    def create_client_row(self, client, index):
        """Crear fila de cliente - client es ClientDebtSummary (READ-ONLY)"""
        # Alternar color de fondo
        bg_color = self.colors['bg_card'] if index % 2 == 0 else self.colors['bg_secondary']

        row = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=bg_color,
            corner_radius=6,
            height=56
        )
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)

        # Columnas de datos (usando ClientDebtSummary fields)
        data_columns = [
            (client.nombre_cliente, 0.30, self.colors['text_primary'], "normal"),
            (client.clave_grupo, 0.20, self.colors['text_secondary'], "normal"),
            (f"{client.deudas_pendientes}", 0.15, self.colors['warning'], "normal"),
            (f"${float(client.total_deuda_pagada):,.2f}", 0.17, self.colors['success'], "normal"),
            (f"${float(client.saldo_pendiente):,.2f}", 0.18, self.colors['danger'], "bold")
        ]

        x_offset = 0
        for text, width_ratio, color, weight in data_columns:
            label = ctk.CTkLabel(
                row,
                text=text,
                font=("Arial", 13, weight),
                text_color=color,
                anchor="w"
            )
            label.place(relx=x_offset, rely=0, relwidth=width_ratio, relheight=1)
            x_offset += width_ratio
