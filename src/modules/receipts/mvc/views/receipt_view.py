# -*- coding: utf-8 -*-
"""
Receipt View - UI Layer
Handles ALL user interface creation and updates
NO business logic or database access allowed here!
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List, Callable, Dict, Any

from src.modules.receipts.ui.cart_ui import CartUIComponent
from src.modules.receipts.mvc.views.confirm_sale_dialog import ConfirmSaleDialog
from src.theme import COLORS, FONTS
from src.config import debug_print


class ReciboView:
    """
    View layer for receipt UI

    Responsibilities:
    - Create UI components
    - Update UI elements
    - Display user feedback (errors, success messages)
    - NO business logic
    - NO database access
    """

    def __init__(self, parent=None):
        # Window setup
        self.is_launcher_context = parent is not None
        if parent:
            self.root = ctk.CTkToplevel(parent)
        else:
            self.root = ctk.CTk()

        self._configurar_ventana()

        # UI Components (will be created by _crear_interface)
        self.frame_controles = None
        self.frame_carrito = None
        self.combo_grupo = None
        self.combo_cliente = None
        self.entry_busqueda = None
        self.lbl_folio = None
        self.lbl_productos_count = None
        self.productos_scroll = None
        self.cart_ui: Optional[CartUIComponent] = None

        # Callbacks (set by controller)
        self.on_grupo_seleccionado: Optional[Callable] = None
        self.on_cliente_seleccionado: Optional[Callable] = None
        self.on_busqueda_changed: Optional[Callable] = None
        self.on_nueva_orden: Optional[Callable] = None
        self.on_guardar_orden: Optional[Callable] = None
        self.on_ver_ordenes: Optional[Callable] = None
        self.on_procesar_venta: Optional[Callable] = None
        self.on_generar_pdf: Optional[Callable] = None
        self.on_generar_excel: Optional[Callable] = None
        self.on_configurar_rutas: Optional[Callable] = None
        self.on_close: Optional[Callable] = None

    # ==================== WINDOW CONFIGURATION ====================

    def _configurar_ventana(self):
        """Configure main window"""
        self.root.title("DISFRULEG - Generador de Recibos v2.0 (MVC)")

        if not self.is_launcher_context:
            self.root.geometry("1400x900")
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
            y = (self.root.winfo_screenheight() // 2) - (900 // 2)
            self.root.geometry(f"1400x900+{x}+{y}")
        else:
            self.root.geometry("1400x900")

        self.root.minsize(1200, 800)

    def set_close_handler(self, handler: Callable):
        """Set window close handler"""
        self.on_close = handler
        self.root.protocol("WM_DELETE_WINDOW", handler)

    # ==================== UI CREATION ====================

    def crear_interface(self):
        """Create main UI structure"""
        # Grid setup
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)

        # Left frame (controls)
        self._crear_frame_controles()

        # Right frame (cart)
        self._crear_frame_carrito()

        debug_print("✅ UI Interface created")

    def _crear_frame_controles(self):
        """Create left control frame"""
        self.frame_controles_wrapper = ctk.CTkFrame(
            self.root,
            fg_color=("gray92", "gray18"),
            corner_radius=0
        )
        self.frame_controles_wrapper.grid(row=0, column=0, sticky="nsew")
        self.frame_controles_wrapper.grid_columnconfigure(0, weight=1)
        self.frame_controles_wrapper.grid_rowconfigure(0, weight=1)

        # Canvas for scrolling
        self.canvas_controles = ctk.CTkCanvas(
            self.frame_controles_wrapper,
            bg=("gray92" if ctk.get_appearance_mode() == "Light" else "#1a1a1a"),
            highlightthickness=0
        )
        self.scrollbar_controles = ctk.CTkScrollbar(
            self.frame_controles_wrapper,
            command=self.canvas_controles.yview
        )

        self.frame_controles = ctk.CTkFrame(self.canvas_controles, fg_color="transparent")

        self.scrollbar_controles.grid(row=0, column=1, sticky="ns")
        self.canvas_controles.grid(row=0, column=0, sticky="nsew")
        self.canvas_controles.configure(yscrollcommand=self.scrollbar_controles.set)

        self.canvas_window = self.canvas_controles.create_window(
            (0, 0),
            window=self.frame_controles,
            anchor="nw"
        )

        self.frame_controles.grid_columnconfigure(0, weight=1)

        # Bind for scroll region update
        self.frame_controles.bind(
            "<Configure>",
            lambda e: self.canvas_controles.configure(scrollregion=self.canvas_controles.bbox("all"))
        )
        self.canvas_controles.bind(
            "<Configure>",
            lambda e: self.canvas_controles.itemconfig(self.canvas_window, width=e.width)
        )

    def _crear_frame_carrito(self):
        """Create right cart frame"""
        self.frame_carrito = ctk.CTkFrame(
            self.root,
            fg_color=("gray95", "gray15"),
            corner_radius=0
        )
        self.frame_carrito.grid(row=0, column=1, sticky="nsew")
        self.frame_carrito.grid_columnconfigure(0, weight=1)
        self.frame_carrito.grid_rowconfigure(1, weight=1)

    def crear_header(self, nombre_usuario: str = "Usuario"):
        """Create header section"""
        header = ctk.CTkFrame(self.frame_controles, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            header,
            text="RECIBOS",
            font=FONTS.get('title', ('Arial', 24, 'bold')),
            text_color=COLORS.get('primary', '#2D9B6C')
        ).grid(row=0, column=0, sticky="w")

        # Settings button (top right)
        self.btn_configurar = ctk.CTkButton(
            header,
            text="⚙️",
            command=lambda: self.on_configurar_rutas() if self.on_configurar_rutas else None,
            width=40,
            height=32,
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            text_color=("gray20", "gray80"),
            corner_radius=6,
            font=FONTS.get('body', ('Arial', 16))
        )
        self.btn_configurar.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # User
        ctk.CTkLabel(
            header,
            text=f"👤 {nombre_usuario}",
            font=FONTS.get('body', ('Arial', 11)),
            text_color=("gray30", "gray70")
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Folio label
        self.lbl_folio = ctk.CTkLabel(
            header,
            text="FOLIO: --",
            font=FONTS.get('subheader', ('Arial', 12, 'bold')),
            text_color=COLORS.get('info', '#3498DB')
        )
        self.lbl_folio.grid(row=2, column=0, sticky="w", pady=(5, 0))

        # Separator
        ctk.CTkFrame(
            self.frame_controles,
            height=2,
            fg_color=("gray80", "gray30")
        ).grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))

        # Buttons
        self._crear_botones_orden()

    def _crear_botones_orden(self):
        """Create order buttons"""
        btn_frame = ctk.CTkFrame(self.frame_controles, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Nueva button
        self.btn_nueva = ctk.CTkButton(
            btn_frame,
            text="➕ Nueva",
            command=lambda: self.on_nueva_orden() if self.on_nueva_orden else None,
            fg_color=COLORS.get('info', '#3498DB'),
            hover_color=COLORS.get('info_hover', '#2980B9'),
            height=38,
            font=FONTS.get('body_bold', ('Arial', 11, 'bold')),
            corner_radius=8
        )
        self.btn_nueva.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Ver órdenes button
        self.btn_ver_ordenes = ctk.CTkButton(
            btn_frame,
            text="📂 Ver Órdenes",
            command=lambda: self.on_ver_ordenes() if self.on_ver_ordenes else None,
            fg_color=COLORS.get('success', '#2ECC71'),
            hover_color=COLORS.get('success_hover', '#27AE60'),
            height=38,
            font=FONTS.get('body_bold', ('Arial', 11, 'bold')),
            corner_radius=8
        )
        self.btn_ver_ordenes.grid(row=0, column=1, sticky="ew", padx=2.5)

        # Guardar button
        self.btn_guardar = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar",
            command=lambda: self.on_guardar_orden() if self.on_guardar_orden else None,
            fg_color=COLORS.get('warning', '#F39C12'),
            hover_color=COLORS.get('warning_hover', '#E67E22'),
            height=38,
            font=FONTS.get('body_bold', ('Arial', 11, 'bold')),
            corner_radius=8
        )
        self.btn_guardar.grid(row=0, column=2, sticky="ew", padx=2.5)

        # Procesar Venta button
        self.btn_procesar_venta = ctk.CTkButton(
            btn_frame,
            text="PROCESAR",
            command=lambda: self.on_procesar_venta() if self.on_procesar_venta else None,
            fg_color=COLORS.get('primary', '#E74C3C'),
            hover_color=COLORS.get('primary_hover', '#C0392B'),
            height=38,
            font=FONTS.get('body_bold', ('Arial', 11, 'bold')),
            corner_radius=8
        )
        self.btn_procesar_venta.grid(row=0, column=3, sticky="ew", padx=(5, 0))

        # Generar PDF button (second row, left half)
        self.btn_generar_pdf = ctk.CTkButton(
            btn_frame,
            text="📄 Generar PDF",
            command=lambda: self.on_generar_pdf() if self.on_generar_pdf else None,
            fg_color=COLORS.get('secondary', '#9B59B6'),
            hover_color=COLORS.get('secondary_hover', '#8E44AD'),
            height=38,
            font=FONTS.get('body_bold', ('Arial', 11, 'bold')),
            corner_radius=8
        )
        self.btn_generar_pdf.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 2.5), pady=(8, 0))

        # Generar Excel button (second row, right half)
        self.btn_generar_excel = ctk.CTkButton(
            btn_frame,
            text="📊 Generar Excel",
            command=lambda: self.on_generar_excel() if self.on_generar_excel else None,
            fg_color=COLORS.get('info', '#16A085'),
            hover_color=COLORS.get('info_hover', '#138D75'),
            height=38,
            font=FONTS.get('body_bold', ('Arial', 11, 'bold')),
            corner_radius=8
        )
        self.btn_generar_excel.grid(row=1, column=2, columnspan=2, sticky="ew", padx=(2.5, 0), pady=(8, 0))

    def crear_seccion_cliente(self, grupos: List[str]):
        """
        Create client selection section

        Args:
            grupos: List of group names
        """
        seccion = ctk.CTkFrame(
            self.frame_controles,
            fg_color=("white", "gray22"),
            corner_radius=12,
            border_width=1,
            border_color=("gray85", "gray28")
        )
        seccion.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        seccion.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            seccion,
            text="1️⃣ SELECCIONAR CLIENTE",
            font=FONTS.get('subheader', ('Arial', 13, 'bold')),
            text_color=COLORS.get('primary', '#2D9B6C')
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(15, 12))

        # Grupo combo
        ctk.CTkLabel(
            seccion,
            text="Grupo:",
            font=FONTS.get('body_bold', ('Arial', 11, 'bold')),
            text_color=("gray20", "gray80")
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 5))

        self.combo_grupo = ctk.CTkComboBox(
            seccion,
            values=grupos if grupos else ["No hay grupos"],
            command=lambda choice: self.on_grupo_seleccionado(choice) if self.on_grupo_seleccionado else None,
            font=FONTS.get('body', ('Arial', 11)),
            state="readonly",
            height=38,
            corner_radius=8,
            border_width=1,
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_hover']
        )
        self.combo_grupo.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))

        # Cliente combo
        ctk.CTkLabel(
            seccion,
            text="Cliente:",
            font=FONTS.get('body_bold', ('Arial', 11, 'bold')),
            text_color=("gray20", "gray80")
        ).grid(row=3, column=0, sticky="w", padx=18, pady=(0, 5))

        self.combo_cliente = ctk.CTkComboBox(
            seccion,
            values=["Seleccione grupo primero"],
            command=lambda choice: self.on_cliente_seleccionado(choice) if self.on_cliente_seleccionado else None,
            font=FONTS.get('body', ('Arial', 11)),
            state="readonly",
            height=38,
            corner_radius=8,
            border_width=1,
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_hover']
        )
        self.combo_cliente.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 15))

    def crear_seccion_busqueda(self):
        """Create product search section"""
        seccion = ctk.CTkFrame(
            self.frame_controles,
            fg_color=("white", "gray22"),
            corner_radius=12,
            border_width=1,
            border_color=("gray85", "gray28")
        )
        seccion.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))
        seccion.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            seccion,
            text="2️⃣ BUSCAR Y AGREGAR PRODUCTOS",
            font=FONTS.get('subheader', ('Arial', 13, 'bold')),
            text_color=COLORS.get('primary', '#2D9B6C')
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(15, 12))

        # Search entry
        search_frame = ctk.CTkFrame(seccion, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            search_frame,
            text="🔍 Buscar:",
            font=FONTS.get('body_bold', ('Arial', 11, 'bold')),
            text_color=("gray20", "gray80")
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.entry_busqueda = ctk.CTkEntry(
            search_frame,
            placeholder_text="Escribe el nombre del producto...",
            font=FONTS.get('body', ('Arial', 11)),
            height=40,
            corner_radius=10,
            border_width=2
        )
        self.entry_busqueda.grid(row=1, column=0, sticky="ew")
        self.entry_busqueda.bind(
            "<KeyRelease>",
            lambda e: self.on_busqueda_changed(e) if self.on_busqueda_changed else None
        )

        # Products count label
        self.lbl_productos_count = ctk.CTkLabel(
            search_frame,
            text="",
            font=("Arial", 9, "italic"),
            text_color=("gray50", "gray60")
        )
        self.lbl_productos_count.grid(row=2, column=0, sticky="w", pady=(5, 0))

        # Products container (scrollable)
        self._crear_productos_container(seccion)

    def _crear_productos_container(self, parent):
        """Create scrollable products container"""
        productos_container = ctk.CTkFrame(
            parent,
            fg_color=("gray97", "gray17"),
            corner_radius=8,
            border_width=1,
            border_color=("gray80", "gray30"),
            height=300
        )
        productos_container.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))
        productos_container.grid_propagate(False)
        productos_container.grid_columnconfigure(0, weight=1)
        productos_container.grid_rowconfigure(0, weight=1)

        # Canvas for products
        self.canvas_productos = ctk.CTkCanvas(
            productos_container,
            bg=("white" if ctk.get_appearance_mode() == "Light" else "#2b2b2b"),
            highlightthickness=0
        )
        self.scrollbar_productos = ctk.CTkScrollbar(
            productos_container,
            command=self.canvas_productos.yview
        )

        self.productos_scroll = ctk.CTkFrame(self.canvas_productos, fg_color="transparent")

        self.scrollbar_productos.grid(row=0, column=1, sticky="ns")
        self.canvas_productos.grid(row=0, column=0, sticky="nsew")
        self.canvas_productos.configure(yscrollcommand=self.scrollbar_productos.set)

        self.productos_window = self.canvas_productos.create_window(
            (0, 0),
            window=self.productos_scroll,
            anchor="nw"
        )

        self.productos_scroll.grid_columnconfigure(0, weight=1)

        self.productos_scroll.bind(
            "<Configure>",
            lambda e: self.canvas_productos.configure(scrollregion=self.canvas_productos.bbox("all"))
        )
        self.canvas_productos.bind(
            "<Configure>",
            lambda e: self.canvas_productos.itemconfig(self.productos_window, width=e.width)
        )

    def crear_seccion_carrito(self, cart_model, on_change_callback: Optional[Callable] = None):
        """
        Create cart section with CartModel

        Args:
            cart_model: CartModel instance (data model)
            on_change_callback: Callback when cart changes
        """
        # Cart header
        header = ctk.CTkFrame(self.frame_carrito, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="🛒 CARRITO DE COMPRAS",
            font=FONTS.get('title', ('Arial', 20, 'bold')),
            text_color=COLORS.get('primary', '#2D9B6C')
        ).pack(side="left")

        # Create cart UI component (uses CartModel for data)
        self.cart_ui = CartUIComponent(
            parent_frame=self.frame_carrito,
            cart_model=cart_model,
            on_change_callback=on_change_callback
        )

    # ==================== UI UPDATES ====================

    def actualizar_folio(self, folio: Optional[int]):
        """Update folio label"""
        if folio:
            self.lbl_folio.configure(text=f"FOLIO: {folio:06d}")
        else:
            self.lbl_folio.configure(text="FOLIO: --")

    def actualizar_clientes_combo(self, clientes: List[str]):
        """Update clients combobox"""
        self.combo_cliente.configure(values=clientes if clientes else ["Sin clientes"])
        if clientes:
            self.combo_cliente.set(clientes[0])

    def set_grupo_seleccionado(self, grupo_clave: str):
        """Set selected group in combobox"""
        if self.combo_grupo:
            self.combo_grupo.set(grupo_clave)

    def set_cliente_seleccionado(self, nombre_cliente: str):
        """Set selected client in combobox"""
        if self.combo_cliente:
            self.combo_cliente.set(nombre_cliente)

    def actualizar_productos_count(self, count: int = 0, texto: str = ""):
        """Update products count label"""
        if texto:
            # Use custom text
            self.lbl_productos_count.configure(text=texto)
        elif count > 0:
            self.lbl_productos_count.configure(
                text=f"✓ {count} productos encontrados - Doble clic para agregar"
            )
        else:
            self.lbl_productos_count.configure(text="")

    def limpiar_productos_lista(self):
        """Clear products list"""
        for widget in self.productos_scroll.winfo_children():
            widget.destroy()

    def limpiar_productos(self):
        """Clear products list (alias for compatibility)"""
        self.limpiar_productos_lista()

    def actualizar_productos(self, productos: List[Dict[str, Any]], on_producto_click: Callable):
        """
        Update products list with search results

        Args:
            productos: List of product dictionaries
            on_producto_click: Callback when product is clicked
        """
        # Clear current list
        self.limpiar_productos_lista()

        if not productos:
            # Show "no results" message
            no_results = ctk.CTkLabel(
                self.productos_scroll,
                text="😕 No se encontraron productos",
                font=("Arial", 11, "italic"),
                text_color=("gray40", "gray70")
            )
            no_results.grid(row=0, column=0, pady=30)
            self.actualizar_productos_count(count=0, texto="❌ Sin resultados")
            return

        # Show products
        for producto in productos:
            self.mostrar_producto_card(producto, on_producto_click)

        # Update count
        self.actualizar_productos_count(count=len(productos))

    def mostrar_producto_card(self, producto: Dict[str, Any], callback: Callable):
        """
        Display a product card

        Args:
            producto: Product dictionary
            callback: Function to call when product is clicked
        """
        card = ctk.CTkFrame(
            self.productos_scroll,
            fg_color=("white", "gray25"),
            corner_radius=8,
            border_width=1,
            border_color=("gray80", "gray35")
        )
        card.grid(sticky="ew", padx=5, pady=5)
        card.grid_columnconfigure(0, weight=1)

        # Bind double-click
        card.bind("<Double-Button-1>", lambda e: callback(producto))

        # Product name
        lbl_nombre = ctk.CTkLabel(
            card,
            text=producto['nombre_producto'],
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        lbl_nombre.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
        lbl_nombre.bind("<Double-Button-1>", lambda e: callback(producto))

        # Price info
        lbl_precio = ctk.CTkLabel(
            card,
            text=f"${producto['precio']:.2f} / {producto.get('unidad', 'unidad')}",
            font=("Arial", 10),
            text_color=COLORS['success'],
            anchor="w"
        )
        lbl_precio.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
        lbl_precio.bind("<Double-Button-1>", lambda e: callback(producto))

    # ==================== USER FEEDBACK ====================

    def mostrar_error(self, titulo: str, mensaje: str):
        """Display error message"""
        messagebox.showerror(titulo, mensaje, parent=self.root)

    def mostrar_advertencia(self, titulo: str, mensaje: str):
        """Display warning message"""
        messagebox.showwarning(titulo, mensaje, parent=self.root)

    def mostrar_exito(self, titulo: str, mensaje: str):
        """Display success message"""
        messagebox.showinfo(titulo, mensaje, parent=self.root)

    def mostrar_confirmacion(self, titulo: str, mensaje: str) -> bool:
        """Display confirmation dialog and return user's choice"""
        return messagebox.askyesno(titulo, mensaje, parent=self.root)

    def mostrar_info(self, titulo: str, mensaje: str):
        """Display info message (alias for mostrar_exito)"""
        messagebox.showinfo(titulo, mensaje, parent=self.root)

    def confirmar(self, titulo: str, mensaje: str) -> bool:
        """Show confirmation dialog"""
        return messagebox.askyesno(titulo, mensaje, parent=self.root)

    def confirmar_venta(self, total: float, items_count: int, client_name: str) -> bool:
        """
        Show custom sale confirmation dialog with 2-step verification

        Args:
            total: Total sale amount
            items_count: Number of items in cart
            client_name: Name of the client

        Returns:
            True if user confirmed, False otherwise
        """
        dialog = ConfirmSaleDialog(
            parent=self.root,
            total=total,
            items_count=items_count,
            client_name=client_name
        )
        self.root.wait_window(dialog)
        return dialog.get_result()

    # ==================== GETTERS ====================

    def get_grupo_seleccionado(self) -> str:
        """Get selected group"""
        return self.combo_grupo.get() if self.combo_grupo else ""

    def get_cliente_seleccionado(self) -> str:
        """Get selected client"""
        return self.combo_cliente.get() if self.combo_cliente else ""

    def get_texto_busqueda(self) -> str:
        """Get search text"""
        return self.entry_busqueda.get() if self.entry_busqueda else ""

    def run(self):
        """Start UI event loop"""
        self.root.mainloop()
