# -*- coding: utf-8 -*-
"""
Product Addition Window - View Component
Window for adding/editing products in the cart
"""

import uuid
import customtkinter as ctk
from src.utils.responsive_manager import ResponsiveMixin
from tkinter import messagebox
from typing import Optional, Dict, Callable, Any

from src.modules.receipts.models.cart_model import CartSection
from src.theme import COLORS, FONTS
from src.config import debug_print
from src.modules.receipts.constants import OrderState, SectionNames


# Constants
DEFAULT_SECTION_NAME = SectionNames.GENERAL
DEFAULT_QUANTITY = "1.0"
EDIT_PRODUCT_WINDOW_WIDTH = 550
EDIT_PRODUCT_WINDOW_HEIGHT_WITH_SECTIONS = 600  # ← Reducido de 700 a 600
EDIT_PRODUCT_WINDOW_HEIGHT_BASIC = 450          # ← Reducido de 500 a 450

class VentanaEdicionProducto(ResponsiveMixin, ctk.CTkToplevel):
    """
    Window for adding/editing products in the cart

    Allows user to:
    - Set quantity
    - Modify price
    - Choose section (if sectioning enabled or multiple sections exist)
    """

    def __init__(self, parent, producto, carrito, secciones=None, callback=None):
        """
        Initialize product addition window

        Args:
            parent: Parent window
            producto: Product dictionary (must have precio as float, not Decimal)
            carrito: Cart instance (CarritoConSeccionesV2)
            secciones: Available sections dictionary
            callback: Callback to execute after adding product
        """
        super().__init__(parent)

        self.producto = producto
        self.carrito = carrito
        self.secciones = secciones or {}
        self.callback = callback
        self.resultado = None

        # Window configuration
        self.title(f"Agregar: {producto['nombre_producto']}")
        self.make_responsive('medium')
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Handle window close (X button)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self._crear_interfaz()

        # Focus on quantity
        self.entry_cantidad.focus_set()
        self.entry_cantidad.select_range(0, 'end')

    def _crear_interfaz(self):
        """Create window interface"""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)

        # Header with product information
        header = ctk.CTkFrame(container, fg_color=("gray90", "gray20"), corner_radius=12)
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="📦 AGREGAR PRODUCTO AL CARRITO",
            font=FONTS['subheader'],
            text_color=COLORS['primary']
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            header,
            text=self.producto['nombre_producto'],
            font=FONTS['title'],
            text_color=("gray10", "gray90")
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            header,
            text=f"Precio: ${self.producto['precio']:.2f} / {self.producto.get('unidad', 'unidad')}",
            font=FONTS['body'],
            text_color=COLORS['success']
        ).pack(pady=(0, 15))

        # Fields frame
        campos_frame = ctk.CTkFrame(container, fg_color="transparent")
        campos_frame.pack(fill="x", pady=(0, 15))

        # Quantity
        ctk.CTkLabel(
            campos_frame,
            text="Cantidad:",
            font=FONTS['body_bold'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        self.entry_cantidad = ctk.CTkEntry(
            campos_frame,
            font=('Arial', 16),
            height=50,
            corner_radius=10,
            border_width=2,
            placeholder_text="Ej: 2.5"
        )
        self.entry_cantidad.pack(fill="x", pady=(0, 15))
        self.entry_cantidad.insert(0, DEFAULT_QUANTITY)
        self.entry_cantidad.bind("<Return>", lambda e: self.entry_precio.focus_set())

        # Unit Price
        ctk.CTkLabel(
            campos_frame,
            text="Precio Unitario:",
            font=FONTS['body_bold'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        self.entry_precio = ctk.CTkEntry(
            campos_frame,
            font=('Arial', 16),
            height=50,
            corner_radius=10,
            border_width=2,
            placeholder_text="Precio por unidad"
        )
        self.entry_precio.pack(fill="x", pady=(0, 15))
        self.entry_precio.insert(0, f"{self.producto['precio']:.2f}")
        self.entry_precio.bind("<Return>", lambda e: self._agregar() if not self.carrito.sectioning_enabled else None)

        # Section selector (show if more than 1 section OR sectioning enabled)
        self.combo_seccion = None
        mostrar_selector = len(self.secciones) > 1 or self.carrito.sectioning_enabled

        if mostrar_selector:
            ctk.CTkLabel(
                campos_frame,
                text="Sección:",
                font=FONTS['body_bold'],
                anchor="w"
            ).pack(fill="x", pady=(0, 5))

            # Get available section names
            secciones_nombres = []
            if self.secciones:
                secciones_nombres = [s.nombre for s in self.secciones.values()]

            # If no sections but sectioning is enabled, create GENERAL
            if not secciones_nombres:
                self._crear_seccion_general()
                self.secciones = self.carrito.secciones
                secciones_nombres = [DEFAULT_SECTION_NAME]

            # Create combobox with available sections
            self.combo_seccion = ctk.CTkComboBox(
                campos_frame,
                values=secciones_nombres,
                font=FONTS['body'],
                height=50,
                corner_radius=10,
                border_width=2,
                button_color=COLORS['primary'],
                button_hover_color=COLORS['primary_hover'],
                state="readonly"
            )
            self.combo_seccion.pack(fill="x", pady=(0, 15))

            # Select first section by default
            if secciones_nombres:
                self.combo_seccion.set(secciones_nombres[0])

        # Calculated subtotal in real-time
        self.lbl_subtotal = ctk.CTkLabel(
            campos_frame,
            text="Subtotal: $0.00",
            font=('Arial', 18, 'bold'),
            text_color=COLORS['success']
        )
        self.lbl_subtotal.pack(pady=(10, 0))

        # Bind to update subtotal in real-time
        self.entry_cantidad.bind("<KeyRelease>", self._actualizar_subtotal)
        self.entry_precio.bind("<KeyRelease>", self._actualizar_subtotal)

        # Action buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=self.destroy,
            fg_color=("gray60", "gray40"),
            hover_color=("gray50", "gray35"),
            height=50,
            font=FONTS['body_bold'],
            corner_radius=10
        ).grid(row=0, column=0, sticky="ew", padx=(0, 7))

        ctk.CTkButton(
            btn_frame,
            text="✅ AGREGAR AL CARRITO",
            command=self._agregar,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            height=50,
            font=FONTS['title'],
            corner_radius=10
        ).grid(row=0, column=1, sticky="ew", padx=(7, 0))

        # Update initial subtotal
        self._actualizar_subtotal()

    def _actualizar_subtotal(self, event=None):
        """Update displayed subtotal"""
        try:
            cantidad = float(self.entry_cantidad.get() or 0)
            precio = float(self.entry_precio.get() or 0)
            subtotal = cantidad * precio
            self.lbl_subtotal.configure(text=f"Subtotal: ${subtotal:,.2f}")
        except ValueError:
            self.lbl_subtotal.configure(text="Subtotal: $0.00")

    def _crear_seccion_general(self) -> str:
        """
        Create a GENERAL section in the cart

        Returns:
            str: UUID of the created section
        """
        seccion_id = str(uuid.uuid4())
        self.carrito.secciones[seccion_id] = CartSection(nombre=DEFAULT_SECTION_NAME, section_id=seccion_id)
        return seccion_id

    def _validar_y_obtener_cantidad(self) -> Optional[float]:
        """
        Validate and get quantity entered by user

        Returns:
            float: Valid quantity or None if error
        """
        try:
            cantidad = float(self.entry_cantidad.get())

            if cantidad <= 0:
                messagebox.showwarning(
                    "Cantidad Inválida",
                    "La cantidad debe ser mayor a 0.",
                    parent=self
                )
                self.entry_cantidad.focus_set()
                return None

            return cantidad

        except ValueError:
            messagebox.showerror(
                "Error de Formato",
                "Ingrese un valor numérico válido para la cantidad.",
                parent=self
            )
            self.entry_cantidad.focus_set()
            return None

    def _validar_y_obtener_precio(self) -> Optional[float]:
        """
        Validate and get price entered by user

        Returns:
            float: Valid price or None if error
        """
        try:
            precio = float(self.entry_precio.get())

            if precio < 0:
                messagebox.showwarning(
                    "Precio Inválido",
                    "El precio no puede ser negativo.",
                    parent=self
                )
                self.entry_precio.focus_set()
                return None

            return precio

        except ValueError:
            messagebox.showerror(
                "Error de Formato",
                "Ingrese un valor numérico válido para el precio.",
                parent=self
            )
            self.entry_precio.focus_set()
            return None

    def _buscar_seccion_por_nombre(self, nombre_seccion: str) -> Optional[str]:
        """
        Search for section by name

        Args:
            nombre_seccion: Section name to search for

        Returns:
            str: Section ID if found, None otherwise
        """
        return next(
            (sid for sid, s in self.secciones.items() if s.nombre == nombre_seccion),
            None
        )

    def _resolver_seccion_destino(self) -> str:
        """
        Resolve which section to use for adding the product

        Logic:
        1. If section combo exists, search for selected section
        2. If doesn't exist but is GENERAL, create it
        3. If no combo, use first available section
        4. If no sections, create GENERAL

        Returns:
            str: Section ID to use
        """
        if self.combo_seccion:
            # User selected a section from combo
            nombre_seccion = self.combo_seccion.get()
            seccion_id = self._buscar_seccion_por_nombre(nombre_seccion)

            # If not found but is GENERAL, create it
            if seccion_id is None and nombre_seccion == DEFAULT_SECTION_NAME:
                return self._crear_seccion_general()

            # If found, use it
            if seccion_id:
                return seccion_id

        # No combo or section not found
        # Use first available section or create GENERAL
        if self.secciones:
            return next(iter(self.secciones.keys()))

        return self._crear_seccion_general()

    def _agregar_producto_a_carrito(
        self,
        cantidad: float,
        precio: float,
        seccion_id: str
    ):
        """
        Add product to cart with specified data

        Args:
            cantidad: Product quantity
            precio: Unit price
            seccion_id: Section ID where to add
        """
        self.carrito.agregar_item(
            self.producto['id_producto'],
            self.producto['nombre_producto'],
            cantidad,
            precio,
            self.producto.get('unidad', 'unidad'),
            seccion_id
        )

    def _finalizar_agregado(
        self,
        cantidad: float,
        precio: float,
        seccion_id: str
    ):
        """
        Finalize addition process: save result, execute callback and close

        Args:
            cantidad: Added quantity
            precio: Used price
            seccion_id: Section where added
        """
        self.resultado = {
            'cantidad': cantidad,
            'precio': precio,
            'seccion_id': seccion_id
        }

        debug_print(
            f"✅ Producto '{self.producto['nombre_producto']}' agregado: "
            f"{cantidad} × ${precio:.2f} = ${cantidad * precio:.2f}"
        )

        # Execute callback if provided
        if self.callback:
            self.callback()

        # Close window
        self.destroy()

    def _agregar(self):
        """
        Main method to add product to cart

        Workflow:
        1. Validate quantity
        2. Validate price
        3. Resolve destination section
        4. Add product to cart
        5. Finalize (callback and close)
        """
        # Validate quantity
        cantidad = self._validar_y_obtener_cantidad()
        if cantidad is None:
            return

        # Validate price
        precio = self._validar_y_obtener_precio()
        if precio is None:
            return

        # Resolve section
        seccion_id = self._resolver_seccion_destino()

        # Add to cart
        self._agregar_producto_a_carrito(cantidad, precio, seccion_id)

        # Finalize
        self._finalizar_agregado(cantidad, precio, seccion_id)
