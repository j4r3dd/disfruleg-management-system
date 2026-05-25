# -*- coding: utf-8 -*-
"""
DISFRULEG - Debt Management Window (Modernized with CustomTkinter)
Ventana principal del módulo de gestión de deudas
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from src.modules.deudas.debt_manager import obtener_debt_manager
from src.config import debug_print
from src.theme import COLORS, FONTS
from decimal import Decimal
import decimal
import unicodedata
import os
from pathlib import Path
from PIL import Image
from io import BytesIO

class DebtManagementWindow:
    def __init__(self, root, user_data=None):
        self.root = root
        self.root.title("Gestión de Deudas - Disfruleg")
        self.root.geometry("1280x800")
        
        # ✅ FIX: Hacer que la ventana se abra ENCIMA de main_application
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()

        # Usuario del sistema
        self.user_data = user_data or {"nombre": "admin", "rol": "administrador"}

        self.debt_manager = obtener_debt_manager()

        # Variables
        self.search_var = ctk.StringVar()
        self.search_history_var = ctk.StringVar()
        self.clientes_deudas = []
        self.historial_pagos = []
        self.is_loading = False
        
        # Statistics variables
        self.stats_vars = {
            'total_clientes': ctk.StringVar(value="0"),
            'clientes_con_deuda': ctk.StringVar(value="0"),
            'total_saldo_pendiente': ctk.StringVar(value="$0.00"),
            'total_deudas_pendientes': ctk.StringVar(value="0")
        }
        
        self.create_interface()
        self.load_data()
        
        # Protocol for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def normalize_text(self, text):
        """Normaliza texto removiendo acentos y convirtiendo a minúsculas"""
        if not text:
            return ""
        text = unicodedata.normalize('NFKD', str(text))
        text = ''.join([c for c in text if not unicodedata.combining(c)])
        return text.lower()

    def create_interface(self):
        """Create the modern user interface"""
        self.create_header()
        self.create_statistics_section()
        self.create_tabview()
        self.create_status_bar()
    
    def create_header(self):
        """Create modern header with back button"""
        header_frame = ctk.CTkFrame(self.root, fg_color=COLORS['secondary'], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=0)
        
        # Left: Back button + Logo + Title
        left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        left_frame.pack(side="left", fill="y")
        
        # ✅ BACK BUTTON (similar al de user_manager)
        back_btn = ctk.CTkButton(
            left_frame,
            text="⎋",  # Símbolo de escape/salir
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['accent'],
            font=("Arial", 20),
            text_color="white",
            border_width=0,
            command=self.on_closing
        )
        back_btn.pack(side="left", padx=(0, 15))
        
        # Logo
        logo_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        logo_frame.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(
            logo_frame,
            text="💰",
            font=("Arial", 28)
        ).pack()
        
        # Title
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="GESTIÓN DE DEUDAS",
            font=("Arial", 16, "bold"),
            text_color=COLORS['success'],
            anchor="w"
        ).pack(anchor="w")
        
        user_info = f"Usuario: {self.user_data.get('nombre', self.user_data.get('nombre_completo', 'Admin'))} | Rol: {self.user_data.get('rol', 'ADMIN').upper()}"
        ctk.CTkLabel(
            title_frame,
            text=user_info,
            font=("Arial", 10),
            text_color="gray70",
            anchor="w"
        ).pack(anchor="w")
    
    
    def create_statistics_section(self):
        """Create modern statistics cards - COMPACTO"""
        stats_container = ctk.CTkFrame(self.root, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=10)  # Reducido de 15 a 10
        
        for i in range(4):
            stats_container.columnconfigure(i, weight=1)
        
        self.create_stat_card(stats_container, "👥", "Total Clientes", self.stats_vars['total_clientes'], 0)
        self.create_stat_card(stats_container, "⏱️", "Con Deuda", self.stats_vars['clientes_con_deuda'], 1)
        self.create_stat_card(stats_container, "💲", "Saldo Total", self.stats_vars['total_saldo_pendiente'], 2, is_money=True)
        self.create_stat_card(stats_container, "⏰", "Deudas Pendientes", self.stats_vars['total_deudas_pendientes'], 3)
    
    def create_stat_card(self, parent, icon, label, variable, column, is_money=False):
        """Create a single statistics card - COMPACTO"""
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=("gray85", "gray20"), border_width=0)
        card.grid(row=0, column=column, padx=8, sticky="ew")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=12)  # Reducido padding

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", anchor="w")

        ctk.CTkLabel(header, text=icon, font=("Arial", 18)).pack(side="left", padx=(0, 8))  # Icono más pequeño
        ctk.CTkLabel(header, text=label, font=("Arial", 10), text_color="gray").pack(side="left")  # Texto más pequeño

        # ✅ FIX: Add explicit text parameter with initial value to prevent "CTKLabel" showing in distributable
        value_label = ctk.CTkLabel(
            content,
            text=variable.get(),  # Set initial text value explicitly
            textvariable=variable,
            font=("Arial", 20, "bold"),  # Número más compacto
            text_color=COLORS['error_red'] if is_money else "white"
        )
        value_label.pack(anchor="w", pady=(8, 0))  # Menos espacio vertical
    
    def create_tabview(self):
        """Create tabview"""
        main_content = ctk.CTkFrame(self.root, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        self.tabview = ctk.CTkTabview(main_content, corner_radius=15)
        self.tabview.pack(fill="both", expand=True)
        
        self.tab_pending = self.tabview.add("Deudas Pendientes")
        self.tab_history = self.tabview.add("Historial de Pagos")
        
        self.create_pending_debts_tab()
        self.create_payment_history_tab()
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_frame = ctk.CTkFrame(self.root, fg_color=("gray85", "gray25"), height=30)
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Listo",
            font=FONTS['small'],
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
    
    def create_pending_debts_tab(self):
        """Create pending debts tab"""
        toolbar = ctk.CTkFrame(self.tab_pending, fg_color="transparent")
        toolbar.pack(fill="x", pady=(5, 10), padx=10)  # Reducido padding superior
        
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(search_frame, text="Buscar Cliente:", font=FONTS['subheader']).pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Escribe cualquier parte del nombre...",
            textvariable=self.search_var,
            width=300,
            height=35
        )
        self.search_entry.pack(side="left")
        self.search_var.trace("w", lambda *args: self.filter_debts())
        
        self.btn_actualizar = ctk.CTkButton(
            toolbar,
            text="Actualizar",
            command=self.animate_refresh,
            width=120,
            height=35,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover']
        )
        self.btn_actualizar.pack(side="right", padx=5)
        
        self.debts_scroll = ctk.CTkScrollableFrame(self.tab_pending, fg_color=("gray95", "gray15"))
        self.debts_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 5))  # Reducido padding inferior
        
        self.create_table_header(self.debts_scroll, [
            ("Cliente", 180),
            ("Grupo", 120),
            ("Tipo Cliente", 100),
            ("Saldo Pendiente", 130),
            ("Deudas Pendientes", 145),
            ("Última Deuda", 120),
            ("", 130)
        ])
    
    def create_table_header(self, parent, columns):
        """Create table header with fixed widths"""
        header_frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray25"))
        header_frame.pack(fill="x", pady=(0, 5))
        
        for i, (text, width) in enumerate(columns):
            header_frame.columnconfigure(i, minsize=width)
            
            ctk.CTkLabel(
                header_frame,
                text=text,
                font=FONTS['body_bold'],
                text_color="gray",
                width=width,
                anchor="w"
            ).grid(row=0, column=i, padx=5, pady=10, sticky="w")
    
    def update_debts_table(self):
        """Update debts table"""
        for widget in self.debts_scroll.winfo_children()[1:]:
            widget.destroy()
        
        search_term = self.normalize_text(self.search_var.get())
        filtered_data = [
            c for c in self.clientes_deudas 
            if not search_term or search_term in self.normalize_text(c.get('nombre_cliente', ''))
        ]
        
        for idx, cliente in enumerate(filtered_data):
            self.create_debt_row(cliente, idx)
    
    def create_debt_row(self, cliente, idx):
        """Create debt row with fixed column widths"""
        # Validar campos requeridos
        required = ['id_cliente', 'nombre_cliente', 'clave_grupo', 'tipo_cliente', 
                   'saldo_pendiente', 'deudas_pendientes']
        if not all(k in cliente for k in required):
            debug_print(f"Cliente con datos incompletos: {cliente}")
            return
        
        row_color = ("white", "gray20") if idx % 2 == 0 else ("gray95", "gray18")
        row_frame = ctk.CTkFrame(self.debts_scroll, fg_color=row_color)
        row_frame.pack(fill="x", pady=1, padx=2)

        widths = [180, 120, 100, 130, 145, 120, 130]
        for i, width in enumerate(widths):
            row_frame.columnconfigure(i, minsize=width)

        ctk.CTkLabel(
            row_frame,
            text=cliente['nombre_cliente'],
            font=FONTS['body_bold'],
            width=widths[0],
            anchor="w"
        ).grid(row=0, column=0, padx=5, pady=10, sticky="w")

        ctk.CTkLabel(row_frame, text=cliente['clave_grupo'], font=FONTS['body'], width=widths[1], anchor="w").grid(row=0, column=1, padx=5, pady=10, sticky="w")
        ctk.CTkLabel(row_frame, text=cliente['tipo_cliente'], font=FONTS['body'], width=widths[2], anchor="w").grid(row=0, column=2, padx=5, pady=10, sticky="w")

        ctk.CTkLabel(
            row_frame,
            text=f"${cliente['saldo_pendiente']:,.2f}",
            font=FONTS['body_bold'],
            text_color=COLORS['error_red'],
            width=widths[3],
            anchor="w"
        ).grid(row=0, column=3, padx=5, pady=10, sticky="w")

        ctk.CTkLabel(row_frame, text=str(cliente['deudas_pendientes']), font=FONTS['body'], width=widths[4], anchor="w").grid(row=0, column=4, padx=5, pady=10, sticky="w")
        ctk.CTkLabel(row_frame, text=cliente.get('ultima_deuda_generada', 'N/A'), font=FONTS['body'], width=widths[5], anchor="w").grid(row=0, column=5, padx=5, pady=10, sticky="w")

        ctk.CTkButton(
            row_frame,
            text="Ver Detalles",
            width=120,
            height=30,
            corner_radius=6,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            command=lambda id_cli=cliente['id_cliente']: self.view_client_details(id_cli)
        ).grid(row=0, column=6, padx=5, pady=8)
    
    def quick_payment(self, id_cliente):
        """Abrir ventana de selección rápida de deuda para pago"""
        select_window = ctk.CTkToplevel(self.root)
        select_window.title("Seleccionar Deuda para Pago")
        select_window.geometry("900x500")
        select_window.transient(self.root)
        select_window.grab_set()
        
        try:
            deudas = self.debt_manager.obtener_deudas_cliente(id_cliente)
            
            if not deudas:
                ctk.CTkLabel(select_window, text="No hay deudas pendientes", font=FONTS['subtitle']).pack(pady=50)
                return
            
            cliente_info = deudas[0]
            
            header = ctk.CTkFrame(select_window, fg_color=COLORS['secondary'])
            header.pack(fill="x")
            
            ctk.CTkLabel(
                header,
                text=f"SELECCIONAR DEUDA - {cliente_info.get('nombre_cliente', 'Cliente')}",
                font=FONTS['header'],
                text_color="white"
            ).pack(pady=15)
            
            scroll = ctk.CTkScrollableFrame(select_window, fg_color=("gray95", "gray15"))
            scroll.pack(fill="both", expand=True, padx=20, pady=20)
            
            header_row = ctk.CTkFrame(scroll, fg_color=("gray85", "gray25"))
            header_row.pack(fill="x", pady=(0, 5))
            
            headers = ["Factura", "Fecha", "Monto Total", "Saldo", "Estado", ""]
            widths = [100, 120, 120, 120, 120, 150]
            
            for i, (header_text, width) in enumerate(zip(headers, widths)):
                    ctk.CTkLabel(
                        header_row,
                        text=header_text,
                        font=FONTS['body_bold'],
                        text_color="gray",
                        width=width,
                        anchor="w"
                    ).grid(row=0, column=i, padx=5, pady=10, sticky="w")
            
            for idx, deuda in enumerate(deudas):
                if deuda.get('saldo_pendiente', 0) > 0:
                    row_color = ("white", "gray20") if idx % 2 == 0 else ("gray95", "gray18")
                    row = ctk.CTkFrame(scroll, fg_color=row_color)
                    row.pack(fill="x", pady=1)
                    
                    ctk.CTkLabel(row, text=str(deuda.get('id_factura', 'N/A')), font=FONTS['body'], width=widths[0], anchor="w").grid(row=0, column=0, padx=5, pady=10, sticky="w")
                    ctk.CTkLabel(row, text=deuda.get('fecha_factura', 'N/A'), font=FONTS['body'], width=widths[1], anchor="w").grid(row=0, column=1, padx=5, pady=10, sticky="w")
                    ctk.CTkLabel(row, text=f"${deuda.get('monto_total', 0):,.2f}", font=FONTS['body'], width=widths[2], anchor="w").grid(row=0, column=2, padx=5, pady=10, sticky="w")
                    ctk.CTkLabel(
                        row,
                        text=f"${deuda.get('saldo_pendiente', 0):,.2f}",
                        font=FONTS['body_bold'],
                        text_color=COLORS['error_red'],
                        width=widths[3],
                        anchor="w"
                    ).grid(row=0, column=3, padx=5, pady=10, sticky="w")
                    ctk.CTkLabel(row, text=deuda.get('estado_deuda', 'N/A'), font=FONTS['body'], width=widths[4], anchor="w").grid(row=0, column=4, padx=5, pady=10, sticky="w")
                    
                    ctk.CTkButton(
                        row,
                        text="Liquidar",
                        width=120,
                        height=30,
                        fg_color=COLORS['primary'],
                        hover_color=COLORS['primary_hover'],
                        command=lambda d=deuda: [select_window.destroy(), self.open_payment_window(d['id_deuda'], deuda=d)]
                    ).grid(row=0, column=5, padx=5, pady=8)
            
            ctk.CTkButton(
                select_window,
                text="Cancelar",
                command=select_window.destroy,
                fg_color=COLORS['accent'],
                height=35
            ).pack(pady=10)
            
        except Exception as e:
            debug_print(f"Error en quick_payment: {type(e).__name__} - {e}")
            messagebox.showerror("Error", f"Error al cargar deudas: {e}")
            select_window.destroy()
    
    def open_payment_window(self, id_deuda, deuda=None):
        """Abrir ventana de registro de pago"""
        payment_window = ctk.CTkToplevel(self.root)
        payment_window.title("Registrar Pago")
        payment_window.geometry("650x550")
        payment_window.transient(self.root)
        payment_window.grab_set()
        
        if not deuda:
            try:
                deuda = self.debt_manager.obtener_deuda_por_id(id_deuda)
            except Exception as e:
                debug_print(f"Error obteniendo deuda: {e}")
                deuda = None
            
            if not deuda:
                messagebox.showerror("Error", "Deuda no encontrada")
                payment_window.destroy()
                return
        
        header = ctk.CTkFrame(payment_window, fg_color=COLORS['secondary'])
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text="REGISTRAR PAGO",
            font=FONTS['header'],
            text_color="white"
        ).pack(pady=15)
        
        content = ctk.CTkScrollableFrame(payment_window, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Info de la deuda
        info_card = ctk.CTkFrame(content, fg_color=("gray90", "gray20"), corner_radius=10)
        info_card.pack(fill="x", pady=(0, 15))
        
        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(info_content, text="INFORMACIÓN DE LA DEUDA", font=FONTS['subtitle']).pack(anchor="w", pady=(0, 10))
        
        info_data = [
            ("Cliente:", deuda.get('nombre_cliente', 'N/A')),
            ("Factura No.:", str(deuda.get('id_factura', 'N/A'))),
            ("Fecha:", deuda.get('fecha_factura', 'N/A')),
            ("Monto Total:", f"${deuda.get('monto_total', 0):,.2f}"),
            ("Ya Pagado:", f"${deuda.get('monto_pagado', 0):,.2f}"),
        ]
        
        for label, value in info_data:
            row = ctk.CTkFrame(info_content, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, font=FONTS['body'], width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=FONTS['body_bold']).pack(side="left")
        
        saldo_frame = ctk.CTkFrame(info_content, fg_color=("#ffebee", "#8b0000"), corner_radius=8)
        saldo_frame.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(
            saldo_frame,
            text=f"SALDO PENDIENTE: ${deuda.get('saldo_pendiente', 0):,.2f}",
            font=FONTS['subtitle'],
            text_color=COLORS['error_red']
        ).pack(pady=10)
        
        # Formulario de pago
        form_card = ctk.CTkFrame(content, fg_color=("gray90", "gray20"), corner_radius=10)
        form_card.pack(fill="x", pady=(0, 15))
        
        form_content = ctk.CTkFrame(form_card, fg_color="transparent")
        form_content.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(form_content, text="DATOS DEL PAGO", font=FONTS['subtitle']).pack(anchor="w", pady=(0, 15))
        
        monto_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        monto_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(monto_frame, text="Monto a Pagar:*", font=FONTS['subheader'], width=150, anchor="w").pack(side="left")
        monto_var = ctk.StringVar()
        ctk.CTkEntry(monto_frame, textvariable=monto_var, width=200, height=35).pack(side="left", padx=10)
        
        metodo_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        metodo_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(metodo_frame, text="Método de Pago:*", font=FONTS['subheader'], width=150, anchor="w").pack(side="left")
        metodo_var = ctk.StringVar()
        metodo_combo = ctk.CTkComboBox(
            metodo_frame,
            variable=metodo_var,
            values=["Efectivo", "Transferencia Bancaria", "Tarjeta de Crédito", "Tarjeta de Débito", "Cheque", "Otro"],
            width=200,
            height=35
        )
        metodo_combo.pack(side="left", padx=10)
        
        ref_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        ref_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(ref_frame, text="Referencia:", font=FONTS['subheader'], width=150, anchor="w").pack(side="left")
        referencia_var = ctk.StringVar()
        ctk.CTkEntry(ref_frame, textvariable=referencia_var, width=300, height=35).pack(side="left", padx=10)

        # Campo de imagen de comprobante
        imagen_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        imagen_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(imagen_frame, text="Comprobante:", font=FONTS['subheader'], width=150, anchor="w").pack(side="left")

        imagen_path_var = ctk.StringVar(value="No se ha seleccionado imagen")
        imagen_label = ctk.CTkLabel(imagen_frame, textvariable=imagen_path_var, font=FONTS['body'], width=250, anchor="w")
        imagen_label.pack(side="left", padx=10)

        def seleccionar_imagen():
            file_path = filedialog.askopenfilename(
                title="Seleccionar comprobante de pago",
                filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos los archivos", "*.*")]
            )
            if file_path:
                imagen_path_var.set(os.path.basename(file_path))
                imagen_label.file_path = file_path

        ctk.CTkButton(
            imagen_frame,
            text="Seleccionar Imagen",
            command=seleccionar_imagen,
            width=140,
            height=35,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        ).pack(side="left", padx=5)

        # Botones de acción
        actions_frame = ctk.CTkFrame(payment_window, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=15)
        
        def procesar_pago():
            try:
                monto_str = monto_var.get().strip()
                if not monto_str:
                    messagebox.showerror("Error", "Ingrese el monto del pago")
                    return
                
                try:
                    monto = Decimal(monto_str)
                except (ValueError, decimal.InvalidOperation):
                    messagebox.showerror("Error", "Ingrese un monto válido (solo números)")
                    return
                
                if monto <= 0:
                    messagebox.showerror("Error", "El monto debe ser mayor a 0")
                    return
                
                saldo_pendiente = Decimal(str(deuda.get('saldo_pendiente', 0)))
                if monto > saldo_pendiente:
                    messagebox.showerror("Error", f"El monto no puede ser mayor al saldo pendiente (${saldo_pendiente:,.2f})")
                    return
                
                metodo = metodo_var.get().strip()
                if not metodo:
                    messagebox.showerror("Error", "Seleccione un método de pago")
                    return
                
                referencia = referencia_var.get().strip() if referencia_var.get().strip() else None
                usuario = self.user_data.get("nombre", "admin")

                # Procesar imagen si existe
                imagen_bytes = None
                nombre_imagen = None
                if hasattr(imagen_label, 'file_path') and imagen_label.file_path:
                    try:
                        # Leer imagen como bytes
                        with open(imagen_label.file_path, 'rb') as f:
                            imagen_bytes = f.read()
                        nombre_imagen = os.path.basename(imagen_label.file_path)
                        debug_print(f"Imagen cargada: {nombre_imagen}, tamaño: {len(imagen_bytes)} bytes")
                    except Exception as e:
                        debug_print(f"Error leyendo imagen: {e}")
                        messagebox.showwarning("Advertencia", f"No se pudo leer la imagen: {e}")

                # Registrar pago
                self.debt_manager.registrar_pago(id_deuda, monto, metodo, referencia, usuario, imagen_bytes, nombre_imagen)

                messagebox.showinfo("Éxito", f"Pago de ${monto:,.2f} registrado correctamente")
                payment_window.destroy()
                self.load_data()
                
            except Exception as e:
                debug_print(f"Error procesando pago: {type(e).__name__} - {e}")
                messagebox.showerror("Error", f"Error registrando pago: {e}")
        
        ctk.CTkButton(
            actions_frame,
            text="✓ Procesar Pago",
            command=procesar_pago,
            width=160,
            height=40,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            font=FONTS['button']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="Cancelar",
            command=payment_window.destroy,
            width=160,
            height=40,
            fg_color=COLORS['accent'],
            font=FONTS['button']
        ).pack(side="right", padx=5)
    
    def create_payment_history_tab(self):
        """Create history tab"""
        toolbar = ctk.CTkFrame(self.tab_history, fg_color="transparent")
        toolbar.pack(fill="x", pady=(5, 10), padx=10)  # Reducido padding
        
        # Search
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(search_frame, text="Buscar Cliente:", font=FONTS['subheader']).pack(side="left", padx=(0, 10))
        
        self.search_history_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar en historial...",
            textvariable=self.search_history_var,
            width=300,
            height=35
        )
        self.search_history_entry.pack(side="left")
        self.search_history_var.trace("w", lambda *args: self.filter_payment_history())
        
        ctk.CTkButton(
            toolbar,
            text="Actualizar Historial",
            command=self.load_payment_history,
            width=150,
            height=35,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover']
        ).pack(side="right")
        
        self.history_scroll = ctk.CTkScrollableFrame(
            self.tab_history,
            fg_color=("gray95", "gray15")
        )
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 5))  # Reducido padding inferior
        
        self.create_table_header(self.history_scroll, [
            ("Cliente", 160),
            ("Grupo", 70),
            ("Folio", 70),
            ("Monto Total", 100),
            ("Pagado", 100),
            ("Fecha", 90),
            ("Método", 110),
            ("Referencia", 110),
            ("", 100)
        ])
    
    def update_history_table(self):
        """Update history table"""
        for widget in self.history_scroll.winfo_children()[1:]:
            widget.destroy()
        
        search_term = self.normalize_text(self.search_history_var.get())
        filtered_data = [
            p for p in self.historial_pagos
            if not search_term or search_term in self.normalize_text(p.get('nombre_cliente', ''))
        ]
        
        for idx, pago in enumerate(filtered_data):
            self.create_history_row(pago, idx)
    
    def create_history_row(self, pago, idx):
        """Create history row"""
        if 'nombre_cliente' not in pago:
            debug_print(f"Pago con datos incompletos: {pago}")
            return
        
        row_color = ("white", "gray20") if idx % 2 == 0 else ("gray95", "gray18")
        row_frame = ctk.CTkFrame(self.history_scroll, fg_color=row_color)
        row_frame.pack(fill="x", pady=1, padx=2)
        
        widths = [160, 70, 70, 100, 100, 90, 110, 110, 100]
        for i, width in enumerate(widths):
            row_frame.columnconfigure(i, minsize=width)
        
        data = [
            (pago.get('nombre_cliente', 'N/A'), FONTS['body_bold']),
            (pago.get('clave_grupo', 'N/A'), FONTS['body']),
            (str(pago.get('folio_numero', 'N/A')), FONTS['body']),
            (f"${pago.get('monto_total', 0):,.2f}", FONTS['body']),
            (f"${pago.get('monto_pagado', 0):,.2f}", FONTS['body_bold']),
            (pago.get('fecha_pago', 'N/A'), FONTS['body']),
            (pago.get('metodo_pago', 'N/A'), FONTS['body']),
            (pago.get('referencia_pago', 'N/A'), FONTS['body'])
        ]
        
        for col, (text, font) in enumerate(data):
            color = COLORS['success_green'] if col == 4 else None
            ctk.CTkLabel(
                row_frame,
                text=text,
                font=font,
                text_color=color,
                width=widths[col],
                anchor="w"
            ).grid(row=0, column=col, padx=5, pady=10, sticky="w")
        
        ctk.CTkButton(
            row_frame,
            text="Ver Detalles",
            width=90,
            height=30,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=lambda id_d=pago.get('id_deuda'): self.view_payment_details(id_d) if id_d else None
        ).grid(row=0, column=8, padx=5, pady=8)
    
    def view_payment_details(self, id_deuda):
        """Ver detalles completos de un pago"""
        if not id_deuda:
            messagebox.showerror("Error", "ID de deuda no disponible")
            return
        
        details_window = ctk.CTkToplevel(self.root)
        details_window.title("Detalles del Pago")
        details_window.geometry("800x600")
        details_window.transient(self.root)
        details_window.grab_set()
        
        try:
            deuda = self.debt_manager.obtener_deuda_por_id(id_deuda)
            if not deuda:
                messagebox.showerror("Error", "No se encontró información del pago")
                details_window.destroy()
                return
            
            header = ctk.CTkFrame(details_window, fg_color=COLORS['secondary'])
            header.pack(fill="x")
            
            ctk.CTkLabel(
                header,
                text="DETALLES DEL PAGO",
                font=FONTS['header'],
                text_color="white"
            ).pack(pady=15)
            
            content = ctk.CTkScrollableFrame(details_window, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Información del Cliente
            client_card = ctk.CTkFrame(content, fg_color=("gray90", "gray20"), corner_radius=10)
            client_card.pack(fill="x", pady=(0, 15))
            
            client_content = ctk.CTkFrame(client_card, fg_color="transparent")
            client_content.pack(fill="x", padx=20, pady=15)
            
            ctk.CTkLabel(client_content, text="INFORMACIÓN DEL CLIENTE", font=FONTS['subtitle']).pack(anchor="w", pady=(0, 10))
            
            client_info = [
                ("Cliente:", deuda.get('nombre_cliente', 'N/A')),
                ("Grupo:", deuda.get('clave_grupo', 'N/A')),
                ("Tipo:", deuda.get('tipo_cliente', 'N/A'))
            ]
            
            for label, value in client_info:
                row = ctk.CTkFrame(client_content, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=label, font=FONTS['body'], width=120, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=value, font=FONTS['body_bold']).pack(side="left")
            
            # Información de la Deuda
            debt_card = ctk.CTkFrame(content, fg_color=("gray90", "gray20"), corner_radius=10)
            debt_card.pack(fill="x", pady=(0, 15))
            
            debt_content = ctk.CTkFrame(debt_card, fg_color="transparent")
            debt_content.pack(fill="x", padx=20, pady=15)
            
            ctk.CTkLabel(debt_content, text="INFORMACIÓN DE LA FACTURA", font=FONTS['subtitle']).pack(anchor="w", pady=(0, 10))
            
            debt_info = [
                ("Factura No.:", str(deuda.get('id_factura', 'N/A'))),
                ("Fecha Factura:", deuda.get('fecha_factura', 'N/A')),
                ("Fecha Deuda:", deuda.get('fecha_generada', 'N/A')),
                ("Estado:", deuda.get('estado_deuda', 'N/A'))
            ]
            
            for label, value in debt_info:
                row = ctk.CTkFrame(debt_content, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=label, font=FONTS['body'], width=120, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=value, font=FONTS['body_bold']).pack(side="left")
            
            # Información del Pago
            payment_card = ctk.CTkFrame(content, fg_color=("gray90", "gray20"), corner_radius=10)
            payment_card.pack(fill="x", pady=(0, 15))
            
            payment_content = ctk.CTkFrame(payment_card, fg_color="transparent")
            payment_content.pack(fill="x", padx=20, pady=15)
            
            ctk.CTkLabel(payment_content, text="DETALLES DEL PAGO", font=FONTS['subtitle']).pack(anchor="w", pady=(0, 10))
            
            payment_info = [
                ("Monto Total:", f"${deuda.get('monto_total', 0):,.2f}"),
                ("Monto Pagado:", f"${deuda.get('monto_pagado', 0):,.2f}"),
                ("Saldo Pendiente:", f"${deuda.get('saldo_pendiente', 0):,.2f}"),
                ("Método de Pago:", deuda.get('metodo_pago', 'N/A')),
                ("Referencia:", deuda.get('referencia_pago', 'N/A')),
                ("Fecha de Pago:", deuda.get('fecha_pago', 'N/A'))
            ]
            
            for label, value in payment_info:
                row = ctk.CTkFrame(payment_content, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=label, font=FONTS['body'], width=150, anchor="w").pack(side="left")
                
                color = None
                if "Saldo" in label and deuda.get('saldo_pendiente', 0) > 0:
                    color = COLORS['error_red']
                elif "Pagado" in label:
                    color = COLORS['success_green']
                
                ctk.CTkLabel(row, text=value, font=FONTS['body_bold'], text_color=color).pack(side="left")

            # Comprobante de pago (imagen)
            imagen_comprobante = deuda.get('imagen_comprobante')
            nombre_imagen = deuda.get('nombre_imagen', 'comprobante.jpg')

            if imagen_comprobante:
                imagen_card = ctk.CTkFrame(content, fg_color=("gray90", "gray20"), corner_radius=10)
                imagen_card.pack(fill="x", pady=(0, 15))

                imagen_content = ctk.CTkFrame(imagen_card, fg_color="transparent")
                imagen_content.pack(fill="x", padx=20, pady=15)

                ctk.CTkLabel(imagen_content, text="COMPROBANTE DE PAGO", font=FONTS['subtitle']).pack(anchor="w", pady=(0, 10))

                try:
                    # Convertir bytes a imagen
                    img = Image.open(BytesIO(imagen_comprobante))
                    img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                    ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)

                    img_label = ctk.CTkLabel(imagen_content, image=ctk_image, text="")
                    img_label.pack(pady=10)

                    # Mostrar nombre de archivo
                    ctk.CTkLabel(
                        imagen_content,
                        text=f"Archivo: {nombre_imagen}",
                        font=FONTS['body'],
                        text_color="gray"
                    ).pack(pady=5)

                    # Botón para descargar imagen
                    def descargar_imagen():
                        file_path = filedialog.asksaveasfilename(
                            defaultextension=os.path.splitext(nombre_imagen)[1],
                            initialfile=nombre_imagen,
                            filetypes=[("Todos los archivos", "*.*")]
                        )
                        if file_path:
                            try:
                                with open(file_path, 'wb') as f:
                                    f.write(imagen_comprobante)
                                messagebox.showinfo("Éxito", "Imagen descargada correctamente")
                            except Exception as e:
                                messagebox.showerror("Error", f"No se pudo descargar: {e}")

                    ctk.CTkButton(
                        imagen_content,
                        text="Descargar Imagen",
                        command=descargar_imagen,
                        width=150,
                        height=30,
                        fg_color=COLORS['primary'],
                        hover_color=COLORS['primary_hover']
                    ).pack(pady=5)

                except Exception as e:
                    debug_print(f"Error cargando imagen: {e}")
                    ctk.CTkLabel(
                        imagen_content,
                        text=f"No se pudo cargar la imagen\n{nombre_imagen}",
                        font=FONTS['body'],
                        text_color="gray"
                    ).pack(pady=10)

            ctk.CTkButton(
                details_window,
                text="Cerrar",
                command=details_window.destroy,
                fg_color=COLORS['accent'],
                height=40,
                width=150
            ).pack(pady=15)
            
        except Exception as e:
            debug_print(f"Error en view_payment_details: {type(e).__name__} - {e}")
            messagebox.showerror("Error", f"Error cargando detalles: {e}")
            details_window.destroy()
    
    def animate_refresh(self):
        """Animate refresh button"""
        if self.is_loading:
            return
        
        self.is_loading = True
        original_text = "Actualizar"
        
        self.btn_actualizar.configure(state="disabled", text="Cargando...")
        
        def do_load():
            try:
                self.load_data()
            except Exception as e:
                debug_print(f"Error en load_data: {e}")
            finally:
                self.root.after(0, lambda: self._finish_refresh(original_text))
        
        self.root.after(100, do_load)
    
    def _finish_refresh(self, original_text):
        """Finish refresh animation"""
        self.btn_actualizar.configure(state="normal", text="✓ Actualizado")
        self.root.after(1500, lambda: self.btn_actualizar.configure(text=original_text))
        self.is_loading = False
    
    def load_data(self):
        """Load all data"""
        try:
            self.status_label.configure(text="Cargando datos...")
            self.load_statistics()
            self.load_clients_with_debts()
            self.load_payment_history()
            
            count = len(self.clientes_deudas)
            payments = len(self.historial_pagos)
            self.status_label.configure(
                text=f"Datos cargados - {count} clientes con deuda, {payments} pagos registrados"
            )
        except Exception as e:
            debug_print(f"Error en load_data: {type(e).__name__} - {e}")
            self.status_label.configure(text="Error cargando datos")
            messagebox.showerror("Error", f"Error: {e}")
    
    def load_statistics(self):
        """Load statistics"""
        try:
            stats = self.debt_manager.obtener_estadisticas_deudas()
            self.stats_vars['total_clientes'].set(str(stats.get('total_clientes', 0)))
            self.stats_vars['clientes_con_deuda'].set(str(stats.get('clientes_con_deuda', 0)))
            self.stats_vars['total_saldo_pendiente'].set(f"${stats.get('total_saldo_pendiente', 0):,.2f}")
            self.stats_vars['total_deudas_pendientes'].set(str(stats.get('total_deudas_pendientes', 0)))
        except Exception as e:
            debug_print(f"Error cargando estadísticas: {type(e).__name__} - {e}")
    
    def load_clients_with_debts(self):
        """Load clients"""
        try:
            self.clientes_deudas = self.debt_manager.obtener_clientes_con_deudas()
            self.update_debts_table()
        except Exception as e:
            debug_print(f"Error cargando clientes: {type(e).__name__} - {e}")
    
    def load_payment_history(self):
        """Load history"""
        try:
            self.historial_pagos = self.debt_manager.obtener_historial_pagos()
            self.update_history_table()
        except Exception as e:
            debug_print(f"Error cargando historial: {type(e).__name__} - {e}")
    
    def filter_debts(self):
        """Filter debts"""
        self.update_debts_table()
    
    def filter_payment_history(self):
        """Filter history"""
        self.update_history_table()
    
    def view_client_details(self, id_cliente):
        """Open client details window"""
        details = ctk.CTkToplevel(self.root)
        details.title("Detalles del Cliente")
        details.geometry("1100x700")
        details.transient(self.root)
        details.grab_set()
        
        try:
            deudas = self.debt_manager.obtener_deudas_cliente(id_cliente)
            
            if not deudas:
                ctk.CTkLabel(details, text="No se encontraron deudas", 
                           font=FONTS['subtitle']).pack(pady=50)
                return
            
            cliente_info = deudas[0]
            
            header = ctk.CTkFrame(details, fg_color=COLORS['secondary'])
            header.pack(fill="x")
            
            ctk.CTkLabel(
                header,
                text=f"CLIENTE: {cliente_info.get('nombre_cliente', 'N/A')}",
                font=FONTS['header'],
                text_color="white"
            ).pack(pady=15)
            
            ctk.CTkLabel(
                header,
                text=f"Grupo: {cliente_info.get('clave_grupo', 'N/A')} - {cliente_info.get('tipo_cliente', 'N/A')}",
                font=FONTS['body'],
                text_color="lightgray"
            ).pack(pady=(0, 15))
            
            scroll = ctk.CTkScrollableFrame(details, fg_color=("gray95", "gray15"))
            scroll.pack(fill="both", expand=True, padx=20, pady=20)
            
            header_row = ctk.CTkFrame(scroll, fg_color=("gray85", "gray25"))
            header_row.pack(fill="x", pady=(0, 5))
            
            headers = ["Factura", "Fecha Fact.", "Fecha Deuda", "Monto Total", "Pagado", "Saldo", "Estado", ""]
            widths = [80, 100, 100, 110, 110, 110, 120, 130]
            
            for i, (header_text, width) in enumerate(zip(headers, widths)):
                ctk.CTkLabel(
                    header_row,
                    text=header_text,
                    font=FONTS['body_bold'],
                    text_color="gray",
                    width=width,
                    anchor="w"
                ).grid(row=0, column=i, padx=5, pady=10, sticky="w")
            
            # Filtrar solo deudas pendientes (con saldo > 0)
            deudas_pendientes = [d for d in deudas if d.get('saldo_pendiente', 0) > 0]

            for idx, deuda in enumerate(deudas_pendientes):
                row_color = ("white", "gray20") if idx % 2 == 0 else ("gray95", "gray18")
                row = ctk.CTkFrame(scroll, fg_color=row_color)
                row.pack(fill="x", pady=1)

                ctk.CTkLabel(row, text=str(deuda.get('id_factura', 'N/A')), font=FONTS['body'], width=widths[0], anchor="w").grid(row=0, column=0, padx=5, pady=10, sticky="w")
                ctk.CTkLabel(row, text=deuda.get('fecha_factura', 'N/A'), font=FONTS['body'], width=widths[1], anchor="w").grid(row=0, column=1, padx=5, pady=10, sticky="w")
                ctk.CTkLabel(row, text=deuda.get('fecha_generada', 'N/A'), font=FONTS['body'], width=widths[2], anchor="w").grid(row=0, column=2, padx=5, pady=10, sticky="w")
                ctk.CTkLabel(row, text=f"${deuda.get('monto_total', 0):,.2f}", font=FONTS['body'], width=widths[3], anchor="w").grid(row=0, column=3, padx=5, pady=10, sticky="w")
                ctk.CTkLabel(row, text=f"${deuda.get('monto_pagado', 0):,.2f}", font=FONTS['body'], width=widths[4], anchor="w").grid(row=0, column=4, padx=5, pady=10, sticky="w")

                saldo = deuda.get('saldo_pendiente', 0)
                ctk.CTkLabel(
                    row,
                    text=f"${saldo:,.2f}",
                    font=FONTS['body_bold'],
                    text_color=COLORS['error_red'],
                    width=widths[5],
                    anchor="w"
                ).grid(row=0, column=5, padx=5, pady=10, sticky="w")

                ctk.CTkLabel(row, text=deuda.get('estado_deuda', 'N/A'), font=FONTS['body'], width=widths[6], anchor="w").grid(row=0, column=6, padx=5, pady=10, sticky="w")

                ctk.CTkButton(
                    row,
                    text="Registrar Pago",
                    width=110,
                    height=30,
                    fg_color=COLORS['primary'],
                    hover_color=COLORS['primary_hover'],
                    command=lambda d=deuda: self.open_payment_window(d['id_deuda'], deuda=d)
                ).grid(row=0, column=7, padx=5, pady=8)
            
            button_frame = ctk.CTkFrame(details, fg_color="transparent")
            button_frame.pack(fill="x", padx=20, pady=15)
            
            ctk.CTkButton(
                button_frame,
                text="Actualizar",
                command=lambda: [details.destroy(), self.view_client_details(id_cliente)],
                fg_color=COLORS['primary'],
                height=35,
                width=150
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame,
                text="Cerrar",
                command=details.destroy,
                fg_color=COLORS['accent'],
                height=35,
                width=150
            ).pack(side="right", padx=5)
            
        except Exception as e:
            debug_print(f"Error en view_client_details: {type(e).__name__} - {e}")
            messagebox.showerror("Error", f"Error: {e}")
            details.destroy()

    
    def on_closing(self):
        """Handle window close event"""
        self.root.destroy()

def launch_debt_window(user_data=None):
    """Launch window"""
    try:
        root = ctk.CTk()
        app = DebtManagementWindow(root, user_data)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error inicializando ventana: {e}")

if __name__ == "__main__":
    launch_debt_window()