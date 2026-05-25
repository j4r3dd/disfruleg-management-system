# -*- coding: utf-8 -*-
"""
UI Layer - Purchase View
Modern interface WITHOUT tabs - Single view with right panel
CORREGIDO: Eliminadas pestañas, panel derecho restaurado, stock negativo permitido, métodos de pago SAT
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from decimal import Decimal
from typing import Dict, List, Callable, Optional

from src.theme import COLORS, FONTS


class PurchaseView:
    """Purchase registration view with modern design"""

    def __init__(self, root, user_data: dict):
        """
        Initialize view

        Args:
            root: CTk root window
            user_data: User information
        """
        self.root = root
        self.user_data = user_data

        # Callbacks (set by controller)
        self.on_register_purchase: Optional[Callable] = None
        self.on_edit_purchase: Optional[Callable] = None
        self.on_delete_purchase: Optional[Callable] = None
        self.on_create_product: Optional[Callable] = None
        self.on_refresh: Optional[Callable] = None
        self.on_add_to_cart: Optional[Callable] = None
        self.on_remove_from_cart: Optional[Callable] = None
        self.on_batch_register: Optional[Callable] = None
        self.on_open_advanced_history: Optional[Callable] = None

        # Configure window
        self.root.title("Registro de Compras - DISFRULEG")
        self.root.geometry("1400x900")

        # Center window
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 1400) // 2
        y = (screen_height - 900) // 2
        self.root.geometry(f"1400x900+{x}+{y}")

        # Variables
        self.producto_var = ctk.StringVar()
        self.cantidad_var = ctk.StringVar()
        self.precio_var = ctk.StringVar()
        self.fecha_compra_var = ctk.StringVar(value=str(date.today()))
        self.fecha_registro_var = ctk.StringVar(value=str(date.today()))
        self.incluir_iva_var = ctk.BooleanVar(value=True)
        self.folio_var = ctk.StringVar()
        self.proveedor_var = ctk.StringVar()
        self.rfc_var = ctk.StringVar()
        self.ieps_var = ctk.StringVar()
        self.tasa_interes_var = ctk.StringVar()
        self.metodo_pago_var = ctk.StringVar(value="PUE - Pago en una exhibición")  # CORREGIDO
        self.forma_pago_var = ctk.StringVar(value="03 - Transferencia")  # CORREGIDO
        self.notas_var = ctk.StringVar()

        # Product search
        self.producto_search_var = ctk.StringVar()
        self.all_products = []
        self.filtered_products = []

        # Build UI
        self.create_interface()

    def create_interface(self):
        """Create main interface"""
        # HEADER with back button
        self.create_header()

        # MAIN CONTENT (NO tabs, direct layout)
        self.create_main_layout()

        # STATUS BAR
        self.create_status_bar()

    def create_header(self):
        """Create header with back button"""
        header_frame = ctk.CTkFrame(
            self.root,
            fg_color=("#1a1a1a", "#1a1a1a"),
            height=80
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=0)

        # LEFT: Back button + Logo + Title
        left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        left_frame.pack(side="left", fill="y")

        # BACK BUTTON
        back_btn = ctk.CTkButton(
            left_frame,
            text="⎋",
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['accent'],
            font=("Arial", 20),
            text_color="white",
            border_width=0,
            command=self.on_back_button
        )
        back_btn.pack(side="left", padx=(0, 15))

        # Logo
        logo_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        logo_frame.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(
            logo_frame,
            text="🛒",
            font=("Arial", 28)
        ).pack()

        # Title
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="REGISTRO DE COMPRAS",
            font=("Arial", 16, "bold"),
            text_color=COLORS['primary'],
            anchor="w"
        ).pack(anchor="w")

        user_info = f"Usuario: {self.user_data.get('nombre_completo', 'Usuario')} | Rol: {self.user_data.get('rol', 'usuario').upper()}"
        ctk.CTkLabel(
            title_frame,
            text=user_info,
            font=("Arial", 10),
            text_color="gray60",
            anchor="w"
        ).pack(anchor="w")

        # RIGHT: Action buttons
        button_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        button_frame.pack(side="right")

        ctk.CTkButton(
            button_frame,
            text="➕ Crear Producto",
            command=self._handle_create_product,
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            width=140,
            height=35,
            font=FONTS['body_bold']
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Actualizar",
            command=self._handle_refresh,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            width=120,
            height=35,
            font=FONTS['body_bold']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="📜 Historial",
            command=self._handle_open_history,
            fg_color=COLORS['info'],
            hover_color=COLORS['info_hover'],
            width=120,
            height=35,
            font=FONTS['body_bold']
        ).pack(side="left", padx=5)
    
    def _handle_open_history(self):
        """Handle open advanced history button"""
        if self.on_open_advanced_history:
            self.on_open_advanced_history()


    def on_back_button(self):
        """Handle back button click"""
        self.root.destroy()

    def create_main_layout(self):
        """Create main content layout WITHOUT tabs"""
        # MAIN CONTAINER
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        # LEFT PANEL - Form
        left_panel = ctk.CTkFrame(
            main_container,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=15
        )
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.create_form(left_panel)

        # RIGHT PANEL - Summary and History
        right_panel = ctk.CTkFrame(
            main_container,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=15,
            width=400
        )
        right_panel.pack(side="right", fill="both", expand=False)
        right_panel.pack_propagate(False)

        self.create_right_panel(right_panel)

    def create_form(self, parent):
        """Create purchase form"""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            header,
            text="Información de Compra",
            font=FONTS['subtitle'],
            text_color=COLORS['primary']
        ).pack(anchor="w")

        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # Product section
        self.create_product_section(scroll_frame)

        # Quantity and price
        self.create_quantity_price_section(scroll_frame)

        # Dates
        self.create_dates_section(scroll_frame)

        # Fiscal info
        self.create_fiscal_section(scroll_frame)

        # Payment info
        self.create_payment_section(scroll_frame)

        # Notes
        self.create_notes_section(scroll_frame)

    def create_product_section(self, parent):
        """Create product selection section - Con Canvas y Scrollbar como en receipts"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            section,
            text="Producto *",
            font=FONTS['body_bold'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        # Entry para escribir y buscar
        self.producto_search_entry = ctk.CTkEntry(
            section,
            textvariable=self.producto_search_var,
            placeholder_text="🔍 Escribe para buscar...",
            height=40,
            font=FONTS['body']
        )
        self.producto_search_entry.pack(fill="x", pady=(0, 8))
        self.producto_search_entry.bind('<KeyRelease>', self._on_product_search)

        # Container con Canvas y Scrollbar
        container = ctk.CTkFrame(
            section,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=8,
            height=200
        )
        container.pack(fill="x", pady=(0, 10))
        container.pack_propagate(False)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # Canvas
        self.canvas_productos = ctk.CTkCanvas(
            container,
            bg="#2a2a2a",
            highlightthickness=0,
            height=200
        )
        
        # Scrollbar
        self.scrollbar_productos = ctk.CTkScrollbar(
            container,
            command=self.canvas_productos.yview
        )

        # Frame dentro del canvas
        self.productos_scroll = ctk.CTkFrame(
            self.canvas_productos,
            fg_color="transparent"
        )

        self.scrollbar_productos.grid(row=0, column=1, sticky="ns")
        self.canvas_productos.grid(row=0, column=0, sticky="nsew")
        self.canvas_productos.configure(yscrollcommand=self.scrollbar_productos.set)

        self.productos_window = self.canvas_productos.create_window(
            (0, 0),
            window=self.productos_scroll,
            anchor="nw"
        )

        self.productos_scroll.grid_columnconfigure(0, weight=1)

        # Bind para actualizar scroll region
        self.productos_scroll.bind(
            "<Configure>",
            lambda e: self.canvas_productos.configure(scrollregion=self.canvas_productos.bbox("all"))
        )
        self.canvas_productos.bind(
            "<Configure>",
            lambda e: self.canvas_productos.itemconfig(self.productos_window, width=e.width)
        )
        
        # Cargar productos inicialmente
        self._update_product_list(self.all_products)

    def create_quantity_price_section(self, parent):
        """Create quantity and price section"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 15))

        # Cantidad
        cantidad_frame = ctk.CTkFrame(section, fg_color="transparent")
        cantidad_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            cantidad_frame,
            text="Cantidad *",
            font=FONTS['body_bold'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            cantidad_frame,
            textvariable=self.cantidad_var,
            placeholder_text="0.00",
            height=40,
            font=FONTS['body']
        ).pack(fill="x")

        # Precio
        precio_frame = ctk.CTkFrame(section, fg_color="transparent")
        precio_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            precio_frame,
            text="Precio Unitario *",
            font=FONTS['body_bold'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            precio_frame,
            textvariable=self.precio_var,
            placeholder_text="$0.00",
            height=40,
            font=FONTS['body']
        ).pack(fill="x")

        # IVA checkbox
        iva_frame = ctk.CTkFrame(parent, fg_color="transparent")
        iva_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkCheckBox(
            iva_frame,
            text="Incluir IVA (16%)",
            variable=self.incluir_iva_var,
            font=FONTS['body'],
            checkbox_height=20,
            checkbox_width=20
        ).pack(anchor="w")

    def create_dates_section(self, parent):
        """Create dates section"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 15))

        # Fecha de compra
        fecha_compra_frame = ctk.CTkFrame(section, fg_color="transparent")
        fecha_compra_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            fecha_compra_frame,
            text="Fecha de Compra *",
            font=FONTS['body_bold'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            fecha_compra_frame,
            textvariable=self.fecha_compra_var,
            height=40,
            font=FONTS['body']
        ).pack(fill="x")

        # Fecha de registro
        fecha_registro_frame = ctk.CTkFrame(section, fg_color="transparent")
        fecha_registro_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            fecha_registro_frame,
            text="Fecha de Registro *",
            font=FONTS['body_bold'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            fecha_registro_frame,
            textvariable=self.fecha_registro_var,
            height=40,
            font=FONTS['body']
        ).pack(fill="x")

    def create_fiscal_section(self, parent):
        """Create fiscal info section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=("#1a1a1a", "#1a1a1a"),
            corner_radius=10
        )
        section.pack(fill="x", pady=(0, 15))

        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            content,
            text="📋 Información Fiscal (Opcional)",
            font=FONTS['body_bold'],
            text_color=COLORS['info']
        ).pack(anchor="w", pady=(0, 10))

        # Folio
        ctk.CTkLabel(
            content,
            text="Folio de Factura",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            content,
            textvariable=self.folio_var,
            placeholder_text="A123",
            height=35,
            font=FONTS['body']
        ).pack(fill="x", pady=(0, 10))

        # Proveedor y RFC
        row = ctk.CTkFrame(content, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))

        # Proveedor
        prov_frame = ctk.CTkFrame(row, fg_color="transparent")
        prov_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            prov_frame,
            text="Proveedor",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            prov_frame,
            textvariable=self.proveedor_var,
            placeholder_text="Nombre del proveedor",
            height=35,
            font=FONTS['body']
        ).pack(fill="x")

        # RFC
        rfc_frame = ctk.CTkFrame(row, fg_color="transparent")
        rfc_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            rfc_frame,
            text="RFC",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            rfc_frame,
            textvariable=self.rfc_var,
            placeholder_text="ABC123456DEF",
            height=35,
            font=FONTS['body']
        ).pack(fill="x")

        # IEPS
        ctk.CTkLabel(
            content,
            text="IEPS",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            content,
            textvariable=self.ieps_var,
            placeholder_text="$0.00",
            height=35,
            font=FONTS['body']
        ).pack(fill="x")

    def create_payment_section(self, parent):
        """Create payment info section - CORREGIDO con códigos SAT"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            section,
            text="💳 Información de Pago (SAT)",
            font=FONTS['body_bold']
        ).pack(anchor="w", pady=(0, 10))

        row = ctk.CTkFrame(section, fg_color="transparent")
        row.pack(fill="x")

        # Método de pago (PUE/PPD)
        metodo_frame = ctk.CTkFrame(row, fg_color="transparent")
        metodo_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            metodo_frame,
            text="Método de Pago",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkComboBox(
            metodo_frame,
            variable=self.metodo_pago_var,
            values=[
                "PUE - Pago en una exhibición",
                "PPD - Pago en parcialidades"
            ],
            height=35,
            font=FONTS['body']
        ).pack(fill="x")

        # Forma de pago (Catálogo SAT)
        forma_frame = ctk.CTkFrame(row, fg_color="transparent")
        forma_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            forma_frame,
            text="Forma de Pago",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkComboBox(
            forma_frame,
            variable=self.forma_pago_var,
            values=[
                "01 - Efectivo",
                "02 - Cheque",
                "03 - Transferencia",
                "04 - Tarjeta de crédito",
                "28 - Tarjeta de débito",
                "99 - Por definir"
            ],
            height=35,
            font=FONTS['body']
        ).pack(fill="x")

    def create_notes_section(self, parent):
        """Create notes section"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            section,
            text="📝 Notas",
            font=FONTS['body_bold']
        ).pack(anchor="w", pady=(0, 5))

        self.notas_entry = ctk.CTkTextbox(
            section,
            height=80,
            font=FONTS['body']
        )
        self.notas_entry.pack(fill="x")

    def create_right_panel(self, parent):
        """Create right panel with summary and history"""
        # SECTION 1: TOTALS
        totals_section = ctk.CTkFrame(parent, fg_color="transparent")
        totals_section.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            totals_section,
            text="Resumen de Compra",
            font=FONTS['subtitle'],
            text_color=COLORS['primary']
        ).pack(anchor="w", pady=(0, 15))

        # Totals card
        totals_card = ctk.CTkFrame(
            totals_section,
            fg_color=("#1a1a1a", "#1a1a1a"),
            corner_radius=10
        )
        totals_card.pack(fill="x")

        totals_content = ctk.CTkFrame(totals_card, fg_color="transparent")
        totals_content.pack(fill="x", padx=15, pady=15)

        # Subtotal
        self.create_total_row(totals_content, "Subtotal:", "subtotal")

        # IVA
        self.create_total_row(totals_content, "IVA (16%):", "iva")

        # Separator
        ctk.CTkFrame(
            totals_content,
            fg_color="gray50",
            height=1
        ).pack(fill="x", pady=10)

        # Total
        total_frame = ctk.CTkFrame(totals_content, fg_color="transparent")
        total_frame.pack(fill="x")

        ctk.CTkLabel(
            total_frame,
            text="TOTAL:",
            font=("Arial", 14, "bold"),
            text_color=COLORS['primary']
        ).pack(side="left")

        self.total_label = ctk.CTkLabel(
            total_frame,
            text="$0.00",
            font=("Arial", 18, "bold"),
            text_color=COLORS['success']
        )
        self.total_label.pack(side="right")

        # SECTION 2: ACTION BUTTONS
        button_section = ctk.CTkFrame(parent, fg_color="transparent")
        button_section.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
            button_section,
            text="✓ Registrar Compra",
            command=self._handle_register,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            height=45,
            font=("Arial", 14, "bold")
        ).pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            button_section,
            text="🗑️ Limpiar Formulario",
            command=self.clear_form,
            fg_color="gray40",
            hover_color="gray30",
            height=35,
            font=FONTS['body']
        ).pack(fill="x")

        # SECTION 3: PURCHASE HISTORY
        history_section = ctk.CTkFrame(parent, fg_color="transparent")
        history_section.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Header
        history_header = ctk.CTkFrame(history_section, fg_color="transparent")
        history_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            history_header,
            text="📜 Historial Reciente",
            font=FONTS['body_bold'],
            text_color=COLORS['primary']
        ).pack(side="left")

        ctk.CTkButton(
            history_header,
            text="🔄",
            command=self._handle_refresh,
            fg_color="transparent",
            hover_color=COLORS['accent'],
            width=30,
            height=30,
            font=("Arial", 14)
        ).pack(side="right")

        # History list (scrollable)
        self.history_frame = ctk.CTkScrollableFrame(
            history_section,
            fg_color=("#1a1a1a", "#1a1a1a"),
            corner_radius=10
        )
        self.history_frame.pack(fill="both", expand=True)

    def create_total_row(self, parent, label: str, attr_name: str):
        """Create total row"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5)

        ctk.CTkLabel(
            row,
            text=label,
            font=FONTS['body'],
            text_color="gray70"
        ).pack(side="left")

        value_label = ctk.CTkLabel(
            row,
            text="$0.00",
            font=FONTS['body_bold']
        )
        value_label.pack(side="right")

        setattr(self, f"{attr_name}_label", value_label)

    def create_status_bar(self):
        """Create status bar"""
        status_frame = ctk.CTkFrame(
            self.root,
            fg_color=("#1a1a1a", "#1a1a1a"),
            height=30
        )
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Listo",
            font=FONTS['small'],
            text_color="gray60"
        )
        self.status_label.pack(side="left", padx=20)

    # ==================== DATA METHODS ====================

    def set_products(self, products: List[str]):
        """Set product list"""
        self.all_products = products
        self.filtered_products = products.copy()
        # Mostrar productos en el listbox
        self._update_product_list(products)

    def _update_product_list(self, products):
        """Actualizar lista de productos en el Canvas"""
        # Limpiar canvas
        for widget in self.productos_scroll.winfo_children():
            widget.destroy()
        
        # Mostrar máximo 20 productos para no saturar
        display_products = products[:20]
        
        if not display_products:
            # Mensaje si no hay resultados
            ctk.CTkLabel(
                self.productos_scroll,
                text="No hay productos que coincidan",
                text_color="gray60",
                font=FONTS['body']
            ).pack(pady=20)
            return
        
        # Crear botón para cada producto
        for product in display_products:
            btn = ctk.CTkButton(
                self.productos_scroll,
                text=product,
                anchor="w",
                fg_color=("#3a3a3a", "#3a3a3a"),
                hover_color=("#454545", "#454545"),
                text_color="gray80",
                font=FONTS['body'],
                height=35,
                command=lambda p=product: self._select_product(p)
            )
            btn.pack(fill="x", padx=5, pady=2)

    def _on_product_search(self, event=None):
        """Búsqueda EN VIVO mientras escribes"""
        search_text = self.producto_search_var.get().lower().strip()
        
        if not search_text:
            # Si está vacío, mostrar todos los productos
            self._update_product_list(self.all_products)
            return
        
        # Filtrar productos que contengan el texto
        filtered = [
            p for p in self.all_products
            if search_text in p.lower()
        ]
        
        # Mostrar resultados filtrados
        self._update_product_list(filtered)

    def _select_product(self, product):
        """Seleccionar un producto - Se asigna a producto_var y limpia búsqueda"""
        self.producto_var.set(product)
        self.producto_search_var.set("")
        # Mostrar todos los productos de nuevo
        self._update_product_list(self.all_products)

    def filter_products(self, search_text: str):
        """Filter products based on search - Actualiza el listbox"""
        if not search_text:
            self.filtered_products = self.all_products.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_products = [
                p for p in self.all_products
                if search_lower in p.lower()
            ]
        
        # Actualizar listbox con opciones filtradas
        self._update_product_list(self.filtered_products)

    def get_form_data(self) -> Dict:
        """Get form data - CORREGIDO: Extrae solo códigos SAT"""
        # Extraer solo el código de método de pago (PUE o PPD)
        metodo_pago_completo = self.metodo_pago_var.get()
        metodo_pago = metodo_pago_completo.split(" - ")[0] if " - " in metodo_pago_completo else metodo_pago_completo
        
        # Extraer solo el código de forma de pago (01, 02, 03, etc.)
        forma_pago_completo = self.forma_pago_var.get()
        forma_pago = forma_pago_completo.split(" - ")[0] if " - " in forma_pago_completo else forma_pago_completo
        
        return {
            'producto': self.producto_var.get(),
            'cantidad': self.cantidad_var.get(),
            'precio': self.precio_var.get(),
            'fecha_compra': self.fecha_compra_var.get(),
            'fecha_registro': self.fecha_registro_var.get(),
            'incluir_iva': self.incluir_iva_var.get(),
            'folio': self.folio_var.get(),
            'proveedor': self.proveedor_var.get(),
            'rfc': self.rfc_var.get(),
            'ieps': self.ieps_var.get(),
            'tasa_interes': self.tasa_interes_var.get(),
            'metodo_pago': metodo_pago,  # Solo "PUE" o "PPD"
            'forma_pago': forma_pago,    # Solo "01", "02", "03", etc.
            'notas': self.notas_entry.get("1.0", "end-1c")
        }

    def clear_form(self):
        """Clear form"""
        self.producto_var.set("")
        self.producto_search_var.set("")
        self.cantidad_var.set("")
        self.precio_var.set("")
        self.fecha_compra_var.set(str(date.today()))
        self.fecha_registro_var.set(str(date.today()))
        self.incluir_iva_var.set(True)
        self.folio_var.set("")
        self.proveedor_var.set("")
        self.rfc_var.set("")
        self.ieps_var.set("")
        self.tasa_interes_var.set("")
        self.metodo_pago_var.set("PUE - Pago en una exhibición")
        self.forma_pago_var.set("03 - Transferencia")
        self.notas_entry.delete("1.0", "end")

        self.update_totals(Decimal("0"), Decimal("0"), Decimal("0"))

    def update_totals(self, subtotal: Decimal, iva: Decimal, total: Decimal):
        """Update totals display"""
        self.subtotal_label.configure(text=f"${subtotal:,.2f}")
        self.iva_label.configure(text=f"${iva:,.2f}")
        self.total_label.configure(text=f"${total:,.2f}")

    def display_purchases(self, purchases: List[Dict]):
        """Display purchase history"""
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        if not purchases:
            empty = ctk.CTkLabel(
                self.history_frame,
                text="No hay compras registradas",
                font=FONTS['body'],
                text_color="gray60"
            )
            empty.pack(pady=30)
            return

        # Create purchase cards (only last 10)
        for purchase in purchases[:10]:
            self.create_purchase_card(purchase)

    def create_purchase_card(self, purchase: Dict):
        """Create purchase card"""
        card = ctk.CTkFrame(
            self.history_frame,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=8
        )
        card.pack(fill="x", padx=5, pady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=10)

        # Left: Product info
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            info_frame,
            text=f"#{purchase['id_compra']} - {purchase['nombre_producto']}",
            font=("Arial", 11, "bold"),
            anchor="w"
        ).pack(anchor="w")

        details = f"{float(purchase['cantidad_compra']):,.2f} {purchase['unidad_producto']} × ${float(purchase['precio_unitario_compra']):,.2f}"
        ctk.CTkLabel(
            info_frame,
            text=details,
            font=("Arial", 9),
            text_color="gray60",
            anchor="w"
        ).pack(anchor="w")

        # Right: Total and actions
        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right")

        ctk.CTkLabel(
            right_frame,
            text=f"${float(purchase['total_con_impuestos']):,.2f}",
            font=("Arial", 12, "bold"),
            text_color=COLORS['success']
        ).pack()

        # Delete button
        ctk.CTkButton(
            right_frame,
            text="🗑️",
            command=lambda: self._handle_delete(purchase),
            width=30,
            height=30,
            fg_color=COLORS['accent'],
            hover_color="#C0392B",
            font=("Arial", 12)
        ).pack(pady=(3, 0))

    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.configure(text=message)

    def show_message(self, title: str, message: str, icon: str = "info"):
        """Show message dialog"""
        if icon == "error":
            messagebox.showerror(title, message, parent=self.root)
        elif icon == "warning":
            messagebox.showwarning(title, message, parent=self.root)
        elif icon == "success":
            messagebox.showinfo(title, message, parent=self.root)
        else:
            messagebox.showinfo(title, message, parent=self.root)

    # ==================== CALLBACK HANDLERS ====================

    def _handle_register(self):
        """Handle register button"""
        if self.on_register_purchase:
            self.on_register_purchase()

    def _handle_create_product(self):
        """Handle create product button"""
        if self.on_create_product:
            self.on_create_product()

    def _handle_refresh(self):
        """Handle refresh button"""
        if self.on_refresh:
            self.on_refresh()

    def _handle_delete(self, purchase: Dict):
        """Handle delete purchase"""
        if self.on_delete_purchase:
            self.on_delete_purchase(purchase)

    # ==================== UNUSED LEGACY METHODS ====================
    # Estos métodos son para compatibilidad, no se usan en el diseño sin tabs

    def update_cart_display(self, items: List[Dict]):
        """Legacy method - cart not used in single view"""
        pass

    def _handle_add_to_cart(self):
        """Legacy method"""
        pass

    def _handle_remove_from_cart(self, cart_id: str):
        """Legacy method"""
        pass

    def _handle_batch_register(self):
        """Legacy method"""
        pass