# -*- coding: utf-8 -*-
"""
UI Layer - Purchase History Dialog
Advanced search and filtering interface for purchases
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Callable

from src.theme import COLORS, FONTS

# Import responsive system
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.responsive_manager import ResponsiveMixin


class PurchaseHistoryDialog(ResponsiveMixin, ctk.CTkToplevel):
    """Advanced purchase history viewer with filters - RESPONSIVE"""

    def __init__(
        self,
        parent,
        on_search: Callable,
        on_delete: Optional[Callable] = None,
        on_edit: Optional[Callable] = None
    ):
        """
        Initialize dialog

        Args:
            parent: Parent window
            on_search: Callback for search (receives filter dict)
            on_delete: Callback for delete (receives purchase dict)
            on_edit: Callback for edit (receives purchase dict)
        """
        super().__init__(parent)

        self.on_search = on_search
        self.on_delete = on_delete
        self.on_edit = on_edit

        # Configure window
        self.title("Historial de Compras - Búsqueda Avanzada")
        
        # Apply responsive layout - LARGE preset con force_visible
        self.make_responsive('large', force_visible=True)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Filter variables
        self.search_text_var = ctk.StringVar()
        self.producto_var = ctk.StringVar(value="Todos")
        self.proveedor_var = ctk.StringVar(value="Todos")
        self.fecha_inicio_var = ctk.StringVar()
        self.fecha_fin_var = ctk.StringVar()
        self.cantidad_min_var = ctk.StringVar()
        self.cantidad_max_var = ctk.StringVar()
        self.precio_min_var = ctk.StringVar()
        self.precio_max_var = ctk.StringVar()
        self.solo_fiscales_var = ctk.BooleanVar(value=False)
        self.solo_informales_var = ctk.BooleanVar(value=False)

        # Data
        self.all_purchases = []
        self.filtered_purchases = []
        self.products_list = []
        self.suppliers_list = []

        # Build UI
        self.create_interface()

        # Trace filter changes
        self.setup_filter_traces()

    def create_interface(self):
        """Create main interface"""
        # HEADER
        self.create_header()

        # MAIN CONTENT
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # LEFT: Filters
        filters_panel = ctk.CTkFrame(
            main_container,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=15,
            width=350
        )
        filters_panel.pack(side="left", fill="both", padx=(0, 10))
        filters_panel.pack_propagate(False)

        self.create_filters_panel(filters_panel)

        # RIGHT: Results
        results_panel = ctk.CTkFrame(
            main_container,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=15
        )
        results_panel.pack(side="right", fill="both", expand=True)

        self.create_results_panel(results_panel)

    def create_header(self):
        """Create header"""
        header = ctk.CTkFrame(
            self,
            fg_color=("#1a1a1a", "#1a1a1a"),
            height=70
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        content = ctk.CTkFrame(header, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        # Title
        ctk.CTkLabel(
            content,
            text="📜 Historial de Compras",
            font=("Arial", 18, "bold"),
            text_color=COLORS['primary']
        ).pack(side="left")

        # Close button
        ctk.CTkButton(
            content,
            text="✕ Cerrar",
            command=self.destroy,
            width=100,
            height=35,
            fg_color=COLORS['accent'],
            hover_color=COLORS['danger_hover'],
            font=FONTS['body_bold']
        ).pack(side="right")

    def create_filters_panel(self, parent):
        """Create filters panel"""
        # Title
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            title_frame,
            text="🔍 Filtros de Búsqueda",
            font=FONTS['subtitle'],
            text_color=COLORS['primary']
        ).pack(anchor="w")

        # Scrollable filters
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 1. SEARCH TEXT
        self.create_filter_section(
            scroll,
            "Búsqueda General",
            self.create_search_text_filter
        )

        # 2. DATE FILTERS
        self.create_filter_section(
            scroll,
            "Fechas",
            self.create_date_filters
        )

        # 3. PRODUCT & SUPPLIER
        self.create_filter_section(
            scroll,
            "Producto y Proveedor",
            self.create_product_supplier_filters
        )

        # 4. QUANTITY & PRICE
        self.create_filter_section(
            scroll,
            "Cantidad y Precio",
            self.create_quantity_price_filters
        )

        # 5. FISCAL STATUS
        self.create_filter_section(
            scroll,
            "Estado Fiscal",
            self.create_fiscal_filters
        )

        # ACTION BUTTONS
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
            actions_frame,
            text="🔍 Buscar",
            command=self.apply_filters,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            height=40,
            font=FONTS['body_bold']
        ).pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            actions_frame,
            text="🗑️ Limpiar Filtros",
            command=self.clear_filters,
            fg_color="gray40",
            hover_color="gray30",
            height=35,
            font=FONTS['body']
        ).pack(fill="x")

    def create_filter_section(self, parent, title: str, content_builder: Callable):
        """Create a filter section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=("#1a1a1a", "#1a1a1a"),
            corner_radius=10
        )
        section.pack(fill="x", pady=(0, 15))

        # Title
        title_frame = ctk.CTkFrame(section, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(12, 8))

        ctk.CTkLabel(
            title_frame,
            text=title,
            font=FONTS['body_bold'],
            text_color=COLORS['primary'],
            anchor="w"
        ).pack(fill="x")

        # Content
        content_frame = ctk.CTkFrame(section, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(0, 12))

        content_builder(content_frame)

    def create_search_text_filter(self, parent):
        """Create search text filter"""
        ctk.CTkEntry(
            parent,
            textvariable=self.search_text_var,
            placeholder_text="Buscar en todos los campos...",
            height=35,
            font=FONTS['body']
        ).pack(fill="x")

    def create_date_filters(self, parent):
        """Create date filters"""
        # Quick date buttons
        quick_btns = ctk.CTkFrame(parent, fg_color="transparent")
        quick_btns.pack(fill="x", pady=(0, 10))

        btn_width = 70
        ctk.CTkButton(
            quick_btns,
            text="Hoy",
            command=lambda: self.set_date_range("today"),
            width=btn_width,
            height=28,
            font=("Arial", 9)
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            quick_btns,
            text="Semana",
            command=lambda: self.set_date_range("week"),
            width=btn_width,
            height=28,
            font=("Arial", 9)
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            quick_btns,
            text="Mes",
            command=lambda: self.set_date_range("month"),
            width=btn_width,
            height=28,
            font=("Arial", 9)
        ).pack(side="left")

        # Fecha inicio
        ctk.CTkLabel(
            parent,
            text="Fecha Inicio:",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            parent,
            textvariable=self.fecha_inicio_var,
            placeholder_text="YYYY-MM-DD",
            height=35,
            font=FONTS['body']
        ).pack(fill="x", pady=(0, 10))

        # Fecha fin
        ctk.CTkLabel(
            parent,
            text="Fecha Fin:",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkEntry(
            parent,
            textvariable=self.fecha_fin_var,
            placeholder_text="YYYY-MM-DD",
            height=35,
            font=FONTS['body']
        ).pack(fill="x")

    def create_product_supplier_filters(self, parent):
        """Create product and supplier filters"""
        # Product
        ctk.CTkLabel(
            parent,
            text="Producto:",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        self.producto_combo = ctk.CTkComboBox(
            parent,
            variable=self.producto_var,
            values=["Todos"],
            height=35,
            font=FONTS['body'],
            state="readonly"
        )
        self.producto_combo.pack(fill="x", pady=(0, 10))

        # Supplier
        ctk.CTkLabel(
            parent,
            text="Proveedor:",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        self.proveedor_combo = ctk.CTkComboBox(
            parent,
            variable=self.proveedor_var,
            values=["Todos"],
            height=35,
            font=FONTS['body'],
            state="readonly"
        )
        self.proveedor_combo.pack(fill="x")

    def create_quantity_price_filters(self, parent):
        """Create quantity and price filters"""
        # Quantity range
        ctk.CTkLabel(
            parent,
            text="Cantidad:",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        qty_row = ctk.CTkFrame(parent, fg_color="transparent")
        qty_row.pack(fill="x", pady=(0, 10))

        ctk.CTkEntry(
            qty_row,
            textvariable=self.cantidad_min_var,
            placeholder_text="Min",
            width=100,
            height=35,
            font=FONTS['body']
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkLabel(
            qty_row,
            text="-",
            font=FONTS['body']
        ).pack(side="left", padx=5)

        ctk.CTkEntry(
            qty_row,
            textvariable=self.cantidad_max_var,
            placeholder_text="Max",
            width=100,
            height=35,
            font=FONTS['body']
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))

        # Price range
        ctk.CTkLabel(
            parent,
            text="Precio Unitario:",
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        price_row = ctk.CTkFrame(parent, fg_color="transparent")
        price_row.pack(fill="x")

        ctk.CTkEntry(
            price_row,
            textvariable=self.precio_min_var,
            placeholder_text="Min $",
            width=100,
            height=35,
            font=FONTS['body']
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkLabel(
            price_row,
            text="-",
            font=FONTS['body']
        ).pack(side="left", padx=5)

        ctk.CTkEntry(
            price_row,
            textvariable=self.precio_max_var,
            placeholder_text="Max $",
            width=100,
            height=35,
            font=FONTS['body']
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def create_fiscal_filters(self, parent):
        """Create fiscal status filters"""
        ctk.CTkCheckBox(
            parent,
            text="Solo compras fiscales (con factura)",
            variable=self.solo_fiscales_var,
            font=FONTS['body'],
            checkbox_height=20,
            checkbox_width=20
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkCheckBox(
            parent,
            text="Solo compras informales (sin factura)",
            variable=self.solo_informales_var,
            font=FONTS['body'],
            checkbox_height=20,
            checkbox_width=20
        ).pack(anchor="w")

    def create_results_panel(self, parent):
        """Create results panel"""
        # Header with count
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        self.results_label = ctk.CTkLabel(
            header,
            text="📊 Resultados: 0 compras",
            font=FONTS['subtitle'],
            text_color=COLORS['primary'],
            anchor="w"
        )
        self.results_label.pack(side="left")

        # Export button
        ctk.CTkButton(
            header,
            text="📤 Exportar",
            command=self.export_results,
            width=100,
            height=32,
            fg_color=COLORS['info'],
            hover_color=COLORS['info_hover'],
            font=FONTS['body']
        ).pack(side="right")

        # Results list
        self.results_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color=("#1a1a1a", "#1a1a1a"),
            corner_radius=10
        )
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def setup_filter_traces(self):
        """Setup automatic filter application on change"""
        # Auto-apply on fiscal checkbox changes
        self.solo_fiscales_var.trace("w", lambda *args: self.apply_filters())
        self.solo_informales_var.trace("w", lambda *args: self.apply_filters())

    def set_date_range(self, range_type: str):
        """Set date range quickly"""
        today = date.today()

        if range_type == "today":
            self.fecha_inicio_var.set(str(today))
            self.fecha_fin_var.set(str(today))
        elif range_type == "week":
            start = today - timedelta(days=7)
            self.fecha_inicio_var.set(str(start))
            self.fecha_fin_var.set(str(today))
        elif range_type == "month":
            start = today - timedelta(days=30)
            self.fecha_inicio_var.set(str(start))
            self.fecha_fin_var.set(str(today))

        self.apply_filters()

    def apply_filters(self):
        """Apply all filters and update results"""
        # Build filter dict
        filters = {
            'search_text': self.search_text_var.get().strip(),
            'producto': self.producto_var.get() if self.producto_var.get() != "Todos" else None,
            'proveedor': self.proveedor_var.get() if self.proveedor_var.get() != "Todos" else None,
            'fecha_inicio': self.fecha_inicio_var.get().strip(),
            'fecha_fin': self.fecha_fin_var.get().strip(),
            'cantidad_min': self.cantidad_min_var.get().strip(),
            'cantidad_max': self.cantidad_max_var.get().strip(),
            'precio_min': self.precio_min_var.get().strip(),
            'precio_max': self.precio_max_var.get().strip(),
            'solo_fiscales': self.solo_fiscales_var.get(),
            'solo_informales': self.solo_informales_var.get()
        }

        # Call search callback
        if self.on_search:
            self.filtered_purchases = self.on_search(filters)
            self.display_results(self.filtered_purchases)

    def clear_filters(self):
        """Clear all filters"""
        self.search_text_var.set("")
        self.producto_var.set("Todos")
        self.proveedor_var.set("Todos")
        self.fecha_inicio_var.set("")
        self.fecha_fin_var.set("")
        self.cantidad_min_var.set("")
        self.cantidad_max_var.set("")
        self.precio_min_var.set("")
        self.precio_max_var.set("")
        self.solo_fiscales_var.set(False)
        self.solo_informales_var.set(False)

        self.apply_filters()

    def set_purchases_data(self, purchases: List[Dict], products: List[str], suppliers: List[str]):
        """Set initial data"""
        self.all_purchases = purchases
        self.products_list = products
        self.suppliers_list = suppliers

        # Update comboboxes
        self.producto_combo.configure(values=["Todos"] + products)
        self.proveedor_combo.configure(values=["Todos"] + suppliers)

        # Show all initially
        self.display_results(purchases)

    def display_results(self, purchases: List[Dict]):
        """Display filtered results"""
        # Clear existing
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Update count
        self.results_label.configure(
            text=f"📊 Resultados: {len(purchases)} compras"
        )

        if not purchases:
            empty = ctk.CTkLabel(
                self.results_frame,
                text="No se encontraron compras con los filtros aplicados",
                font=FONTS['body'],
                text_color="gray60"
            )
            empty.pack(pady=50)
            return

        # Display purchases
        for purchase in purchases:
            self.create_purchase_card(purchase)

    def create_purchase_card(self, purchase: Dict):
        """Create purchase card"""
        card = ctk.CTkFrame(
            self.results_frame,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=10
        )
        card.pack(fill="x", padx=5, pady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # TOP ROW: ID, Product, Date
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 8))

        # ID
        ctk.CTkLabel(
            top_row,
            text=f"#{purchase['id_compra']}",
            font=("Arial", 10, "bold"),
            text_color=COLORS['primary'],
            width=50,
            anchor="w"
        ).pack(side="left")

        # Product
        ctk.CTkLabel(
            top_row,
            text=purchase['nombre_producto'],
            font=("Arial", 11, "bold"),
            anchor="w"
        ).pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Date
        ctk.CTkLabel(
            top_row,
            text=str(purchase['fecha_compra']),
            font=("Arial", 9),
            text_color="gray60",
            anchor="e"
        ).pack(side="right")

        # MIDDLE ROW: Details
        middle_row = ctk.CTkFrame(content, fg_color="transparent")
        middle_row.pack(fill="x", pady=(0, 8))

        details_text = f"{float(purchase['cantidad_compra']):,.2f} {purchase['unidad_producto']} × ${float(purchase['precio_unitario_compra']):,.2f}"
        if purchase.get('proveedor'):
            details_text += f" | 🏢 {purchase['proveedor']}"
        if purchase.get('folio_factura'):
            details_text += f" | 📋 {purchase['folio_factura']}"

        ctk.CTkLabel(
            middle_row,
            text=details_text,
            font=("Arial", 10),
            text_color="gray70",
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # BOTTOM ROW: Total and Actions
        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.pack(fill="x")

        # Fiscal badge
        if purchase.get('folio_factura') and purchase.get('rfc_proveedor'):
            ctk.CTkLabel(
                bottom_row,
                text="✓ Fiscal",
                font=("Arial", 9, "bold"),
                text_color=COLORS['success'],
                fg_color=("#1a4d2e", "#1a4d2e"),
                corner_radius=5,
                width=60,
                height=22
            ).pack(side="left", padx=(0, 10))

        # Total
        ctk.CTkLabel(
            bottom_row,
            text=f"${float(purchase['total_con_impuestos']):,.2f}",
            font=("Arial", 14, "bold"),
            text_color=COLORS['success']
        ).pack(side="left")

        # Spacer
        ctk.CTkFrame(bottom_row, fg_color="transparent").pack(side="left", fill="x", expand=True)

        # Action buttons
        if self.on_delete:
            ctk.CTkButton(
                bottom_row,
                text="🗑️",
                command=lambda: self.handle_delete(purchase),
                width=35,
                height=35,
                fg_color=COLORS['accent'],
                hover_color=COLORS['danger_hover'],
                font=("Arial", 14)
            ).pack(side="right", padx=(5, 0))

    def handle_delete(self, purchase: Dict):
        """Handle delete button"""
        if self.on_delete:
            confirm = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Eliminar compra #{purchase['id_compra']}?\n\n"
                f"{purchase['nombre_producto']}\n"
                f"Total: ${float(purchase['total_con_impuestos']):,.2f}",
                parent=self
            )

            if confirm:
                self.on_delete(purchase)
                # Remove from current view
                self.filtered_purchases = [p for p in self.filtered_purchases if p['id_compra'] != purchase['id_compra']]
                self.display_results(self.filtered_purchases)

    def export_results(self):
        """Export results to CSV"""
        if not self.filtered_purchases:
            messagebox.showinfo(
                "Exportar",
                "No hay resultados para exportar",
                parent=self
            )
            return

        try:
            from tkinter import filedialog
            import csv

            filename = filedialog.asksaveasfilename(
                parent=self,
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"compras_{date.today()}.csv"
            )

            if not filename:
                return

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'ID', 'Fecha Compra', 'Fecha Registro', 'Producto', 'Cantidad',
                    'Unidad', 'Precio Unitario', 'Subtotal', 'IVA', 'Total',
                    'Proveedor', 'RFC', 'Folio', 'Usuario'
                ])
                writer.writeheader()

                for p in self.filtered_purchases:
                    writer.writerow({
                        'ID': p['id_compra'],
                        'Fecha Compra': p['fecha_compra'],
                        'Fecha Registro': p.get('fecha_registro', ''),
                        'Producto': p['nombre_producto'],
                        'Cantidad': float(p['cantidad_compra']),
                        'Unidad': p['unidad_producto'],
                        'Precio Unitario': float(p['precio_unitario_compra']),
                        'Subtotal': float(p.get('subtotal', 0)),
                        'IVA': float(p.get('iva', 0)),
                        'Total': float(p['total_con_impuestos']),
                        'Proveedor': p.get('proveedor', ''),
                        'RFC': p.get('rfc_proveedor', ''),
                        'Folio': p.get('folio_factura', ''),
                        'Usuario': p.get('usuario_registro', '')
                    })

            messagebox.showinfo(
                "Exportar",
                f"Resultados exportados exitosamente a:\n{filename}",
                parent=self
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al exportar: {str(e)}",
                parent=self
            )