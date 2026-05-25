# -*- coding: utf-8 -*-
"""
Cotizacion Importer UI View with Back Button
Handles user interface and user interactions
Delegates ALL business logic to ImportController

✅ VERSIÓN REFACTORIZADA - Controller Layer Pattern
Fecha: 19 Nov 2025
Ubicuo Studio
"""

import os
import customtkinter as ctk
from src.utils.responsive_manager import ResponsiveMixin
from src.ui.loading_indicator import LoadingIndicator
from tkinter import filedialog, messagebox
from decimal import Decimal
from typing import List, Optional
import traceback
import threading

from ..business import PDFExtractorService, ImportService, ReportService
from ..data import MySQLProductRepository, MySQLPriceRepository, MySQLSystemRepository
from ..controllers import ImportController
from ..domain.models import ExtractedProduct, ProductChange
from ..domain.exceptions import (
    PDFExtractionError,
    PriceApplicationError,
    ReportGenerationError,
    SystemIntegrityError
)


# ============================================================================
# ✅ CLASE AGREGADA: ProgressDialog
# ============================================================================
class ProgressDialog(ctk.CTkToplevel):
    """
    Progress dialog window for showing operation progress
    """
    
    def __init__(self, parent, title="Procesando"):
        """
        Initialize progress dialog
        
        Args:
            parent: Parent window
            title: Dialog title
        """
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x200")
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Make responsive
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color=("#2D9B6C", "#1a5d42"))
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text=title,
            font=("Roboto", 16, "bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(content, width=300)
        self.progress_bar.pack(pady=(20, 10))
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            content,
            text="Iniciando...",
            font=("Roboto", 12)
        )
        self.status_label.pack(pady=5)
        
        # Detail label
        self.detail_label = ctk.CTkLabel(
            content,
            text="",
            font=("Roboto", 10),
            text_color="gray"
        )
        self.detail_label.pack(pady=5)
        
        # Center window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def update_progress(self, value: float, status: str = "", detail: str = ""):
        """
        Update progress bar and labels
        
        Args:
            value: Progress value (0.0 to 1.0)
            status: Status message
            detail: Detail message
        """
        self.progress_bar.set(value)
        
        if status:
            self.status_label.configure(text=status)
        
        if detail:
            self.detail_label.configure(text=detail)
        
        self.update()


# ============================================================================
# CLASE PRINCIPAL: CotizacionImporter
# ============================================================================
class CotizacionImporter(ResponsiveMixin, ctk.CTkToplevel):
    """
    Cotizacion Importer UI Controller with Back Button
    Handles user interface for importing quotations from PDF
    """

    def __init__(self, parent, db_connection, user_info):
        """Initialize importer window"""
        # Validate critical parameters
        if db_connection is None:
            raise ValueError("db_connection cannot be None")

        if not hasattr(db_connection, 'cursor'):
            raise ValueError(f"Invalid db_connection: {type(db_connection)}")

        if user_info is None:
            raise ValueError("user_info cannot be None")

        # Create independent window
        super().__init__(None)

        self.db = db_connection
        self.user_info = user_info

        # Initialize repositories (needed for some UI operations)
        product_repo = MySQLProductRepository(db_connection)
        price_repo = MySQLPriceRepository(db_connection)
        system_repo = MySQLSystemRepository(db_connection)

        # Initialize services
        pdf_extractor = PDFExtractorService()
        import_service = ImportService(
            product_repo,
            price_repo,
            system_repo
        )
        report_service = ReportService()

        # ✅ Initialize controller (business logic coordinator)
        self.controller = ImportController(
            import_service=import_service,
            pdf_extractor=pdf_extractor,
            report_service=report_service,
            price_repo=price_repo
        )

        # State
        self.productos_extraidos: List[ExtractedProduct] = []
        self.cambios_propuestos: List[ProductChange] = []
        self.productos_sin_precio: List[ExtractedProduct] = []
        self.pdf_path: Optional[str] = None
        self.grupos_disponibles: List[dict] = []
        self.selected_group_id: Optional[int] = None

        # Configure window
        self.title("Importar Cotización desde PDF")
        # ✅ FIX: Increase minimum height to show all content
        self.make_responsive('small', custom_config={
            'min_width': 650,
            'min_height': 650  # Increased from default 500 to show group selector
        })

        # Make window appear on top
        self.attributes('-topmost', True)
        self.lift()
        self.focus_force()

        # After a moment, disable topmost
        self.after(100, lambda: self.attributes('-topmost', False))

        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # Build UI
        self.setup_ui()

        # Load groups
        self.after(100, self.cargar_grupos)

        # Validate system integrity
        self.after(500, self.validar_integridad_sistema)

    def validar_integridad_sistema(self):
        """Validate system integrity before allowing import"""
        try:
            # ✅ Use controller for business logic
            is_valid, warning_message = self.controller.validate_system_integrity()

            if not is_valid and warning_message:
                if not messagebox.askyesno(
                    "Advertencias del Sistema",
                    warning_message,
                    parent=self
                ):
                    self.destroy()
                    return

        except SystemIntegrityError as e:
            print(f"Error en validación de integridad: {e}")
            messagebox.showerror(
                "Error",
                f"Error validando la integridad del sistema:\n{str(e)}",
                parent=self
            )

    def setup_ui(self):
        """Build user interface with back button"""

        # ========== HEADER WITH BACK BUTTON ==========
        header = ctk.CTkFrame(self, fg_color=("#2D9B6C", "#1a5d42"))
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Header content
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Back button + Title
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
            hover_color="#E74C3C",
            font=("Arial", 20),
            text_color="white",
            border_width=0,
            command=self.destroy
        )
        back_btn.pack(side="left", padx=(0, 15))

        # Title
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="📄 Importar Cotización",
            font=("Roboto", 24, "bold"),
            text_color="white"
        ).pack(side="left")

        # Right: User info
        ctk.CTkLabel(
            header_content,
            text=f"Usuario: {self.user_info.get('username', 'N/A')}",
            font=("Roboto", 12),
            text_color="white"
        ).pack(side="right", padx=20)

        # ========== LEFT PANEL: CONTROLS ==========
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        # ✅ FIX: Don't expand row 4, let content determine size
        # This prevents the group selector from being hidden

        # Section 1: File selection
        ctk.CTkLabel(
            left_panel,
            text="1. Seleccionar Archivo PDF",
            font=("Roboto", 16, "bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        self.file_label = ctk.CTkLabel(
            left_panel,
            text="Ningún archivo seleccionado",
            font=("Roboto", 11),
            text_color="gray"
        )
        self.file_label.grid(row=1, column=0, sticky="w", padx=20, pady=5)

        ctk.CTkButton(
            left_panel,
            text="📁 Seleccionar PDF",
            command=self.seleccionar_pdf,
            height=40,
            font=("Roboto", 13, "bold")
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        # Section 2: Group selection
        ctk.CTkLabel(
            left_panel,
            text="2. Seleccionar Grupo de Precios",
            font=("Roboto", 16, "bold")
        ).grid(row=3, column=0, sticky="w", padx=20, pady=(20, 10))

        # ✅ FIX: Use sticky="new" instead of "ew" to anchor to top
        group_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        group_frame.grid(row=4, column=0, sticky="new", padx=20, pady=5)

        ctk.CTkLabel(
            group_frame,
            text="Los precios se aplicarán solo a este grupo:",
            font=("Roboto", 11),
            text_color="gray"
        ).pack(anchor="w", pady=(0, 5))

        self.group_selector = ctk.CTkComboBox(
            group_frame,
            values=["Cargando grupos..."],
            state="readonly",
            font=("Roboto", 12),
            command=self.on_group_selected
        )
        self.group_selector.pack(fill="x", pady=5)

        # Section 3: Import options
        ctk.CTkLabel(
            left_panel,
            text="3. Opciones de Importación",
            font=("Roboto", 16, "bold")
        ).grid(row=5, column=0, sticky="w", padx=20, pady=(20, 10))

        options_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        options_frame.grid(row=6, column=0, sticky="new", padx=20, pady=5)

        self.actualizar_existentes = ctk.CTkCheckBox(
            options_frame,
            text="Actualizar productos existentes",
            font=("Roboto", 11)
        )
        self.actualizar_existentes.pack(anchor="w", pady=5)
        self.actualizar_existentes.select()

        self.agregar_nuevos = ctk.CTkCheckBox(
            options_frame,
            text="Agregar productos nuevos",
            font=("Roboto", 11)
        )
        self.agregar_nuevos.pack(anchor="w", pady=5)
        self.agregar_nuevos.select()

        self.mantener_stock = ctk.CTkCheckBox(
            options_frame,
            text="⚠️ NO modificar inventario/stock",
            font=("Roboto", 11, "bold"),
            text_color="#E74C3C"
        )
        self.mantener_stock.pack(anchor="w", pady=5)
        self.mantener_stock.select()
        self.mantener_stock.configure(state="disabled")

        # Section 4: Actions
        ctk.CTkLabel(
            left_panel,
            text="4. Procesar",
            font=("Roboto", 16, "bold")
        ).grid(row=7, column=0, sticky="w", padx=20, pady=(20, 10))

        self.btn_procesar = ctk.CTkButton(
            left_panel,
            text="🔍 Procesar PDF",
            command=self.procesar_pdf,
            height=45,
            font=("Roboto", 14, "bold"),
            fg_color="#3498DB",
            hover_color="#2980B9",
            state="disabled"
        )
        self.btn_procesar.grid(row=8, column=0, sticky="ew", padx=20, pady=5)

        self.btn_aplicar = ctk.CTkButton(
            left_panel,
            text="✅ Aplicar Cambios",
            command=self.aplicar_cambios,
            height=45,
            font=("Roboto", 14, "bold"),
            fg_color="#2ECC71",
            hover_color="#27AE60",
            state="disabled"
        )
        self.btn_aplicar.grid(row=9, column=0, sticky="ew", padx=20, pady=5)

        ctk.CTkButton(
            left_panel,
            text="Cancelar",
            command=self.destroy,
            height=35,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        ).grid(row=10, column=0, sticky="ew", padx=20, pady=(5, 20))

        # ========== RIGHT PANEL: PREVIEW ==========
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Preview header
        preview_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        preview_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            preview_header,
            text="Vista Previa de Cambios",
            font=("Roboto", 18, "bold")
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            preview_header,
            text="",
            font=("Roboto", 11),
            text_color="gray"
        )
        self.status_label.pack(side="right")

        # Changes table
        self.tabla_cambios = ctk.CTkScrollableFrame(right_panel)
        self.tabla_cambios.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.tabla_cambios.grid_columnconfigure(0, weight=1)

        self.mostrar_mensaje_inicial()

    def cargar_grupos(self):
        """Load available groups from database"""
        try:
            # ✅ Use controller for business logic
            self.grupos_disponibles = self.controller.load_groups()

            if not self.grupos_disponibles:
                messagebox.showwarning(
                    "Sin Grupos",
                    "No hay grupos de clientes configurados en el sistema.",
                    parent=self
                )
                self.group_selector.configure(values=["No hay grupos disponibles"])
                return

            # Create display values: "Clave - Descuento%"
            display_values = [
                f"{g['clave']} (Desc: {g['descuento']}%)"
                for g in self.grupos_disponibles
            ]

            self.group_selector.configure(values=display_values)
            self.group_selector.set(display_values[0])
            self.selected_group_id = self.grupos_disponibles[0]['id']

        except Exception as e:
            print(f"Error loading groups: {e}")
            traceback.print_exc()
            messagebox.showerror(
                "Error",
                f"Error al cargar grupos: {str(e)}",
                parent=self
            )

    def on_group_selected(self, choice: str):
        """Handle group selection change"""
        try:
            # Find selected group by matching display value
            for idx, grupo in enumerate(self.grupos_disponibles):
                display_value = f"{grupo['clave']} (Desc: {grupo['descuento']}%)"
                if display_value == choice:
                    self.selected_group_id = grupo['id']
                    print(f"Selected group: {grupo['clave']} (ID: {grupo['id']})")
                    break
        except Exception as e:
            print(f"Error in group selection: {e}")

    def seleccionar_pdf(self):
        """Open dialog to select PDF file"""
        # ✅ FIX: Add parent parameter to keep window on top
        filename = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar cotización PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        # ✅ FIX: Bring window back to front after dialog closes
        self.lift()
        self.focus_force()

        if filename:
            self.pdf_path = filename
            nombre_archivo = os.path.basename(filename)
            self.file_label.configure(
                text=f"✅ {nombre_archivo}",
                text_color="#2ECC71"
            )
            self.btn_procesar.configure(state="normal")

    def procesar_pdf(self):
        """Extract data from PDF and generate preview of changes"""
        if not self.pdf_path:
            messagebox.showerror("Error", "Selecciona un archivo PDF primero", parent=self)
            return

        progress = ProgressDialog(self, "Procesando PDF")

        try:
            # ✅ Use controller for business logic with progress callback
            def progress_callback(value, status, detail):
                progress.update_progress(value, status, detail)
                self.update()

            self.cambios_propuestos, self.productos_sin_precio, statistics = (
                self.controller.process_pdf(
                    pdf_path=self.pdf_path,
                    actualizar_existentes=self.actualizar_existentes.get(),
                    agregar_nuevos=self.agregar_nuevos.get(),
                    progress_callback=progress_callback
                )
            )

            # Show preview
            self.mostrar_preview()

            # Enable apply button
            self.btn_aplicar.configure(state="normal")

            # Close progress dialog
            progress.after(500, progress.destroy)

        except PDFExtractionError as e:
            progress.destroy()
            messagebox.showerror(
                "Error de Extracción",
                f"No se pudieron extraer los productos:\n{str(e)}",
                parent=self
            )
            print(f"Error completo: {e}")
            traceback.print_exc()

        except Exception as e:
            progress.destroy()
            messagebox.showerror(
                "Error",
                f"Error procesando PDF:\n{str(e)}",
                parent=self
            )
            print(f"Error completo: {e}")
            traceback.print_exc()

    # ... resto de los métodos continúan igual ...
    
    def mostrar_mensaje_inicial(self):
        """Show initial message in preview panel"""
        for widget in self.tabla_cambios.winfo_children():
            widget.destroy()

        mensaje = ctk.CTkFrame(self.tabla_cambios, fg_color="transparent")
        mensaje.pack(expand=True)

        ctk.CTkLabel(
            mensaje,
            text="👆",
            font=("Arial", 48)
        ).pack(pady=(50, 20))

        ctk.CTkLabel(
            mensaje,
            text="Selecciona un PDF y presiona",
            font=("Roboto", 14)
        ).pack()

        ctk.CTkLabel(
            mensaje,
            text="'Procesar PDF'",
            font=("Roboto", 14, "bold"),
            text_color="#3498DB"
        ).pack()

    def mostrar_preview(self):
        """Show preview of proposed changes"""
        # Clear previous content
        for widget in self.tabla_cambios.winfo_children():
            widget.destroy()

        if not self.cambios_propuestos:
            ctk.CTkLabel(
                self.tabla_cambios,
                text="No hay cambios para aplicar",
                font=("Roboto", 14),
                text_color="gray"
            ).pack(pady=50)
            return

        # ✅ Use controller for statistics
        total, nuevos, actualizados = self.controller.get_statistics(
            self.cambios_propuestos
        )
        self.status_label.configure(
            text=f"{total} cambios ({nuevos} nuevos, {actualizados} actualizados)"
        )

        # Show changes
        for idx, cambio in enumerate(self.cambios_propuestos):
            self.crear_card_cambio(cambio, idx)

    def crear_card_cambio(self, cambio: ProductChange, index: int):
        """Create a card for each proposed change"""
        # Card container
        card = ctk.CTkFrame(
            self.tabla_cambios,
            fg_color=("gray90", "gray20"),
            corner_radius=8
        )
        card.pack(fill="x", pady=5)

        # Content container
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # Left side: Product info
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        # Type badge
        tipo_color = "#3498DB" if cambio.tipo == 'nuevo' else "#E67E22"
        tipo_texto = "NUEVO" if cambio.tipo == 'nuevo' else "ACTUALIZAR"

        badge = ctk.CTkLabel(
            left,
            text=tipo_texto,
            font=("Roboto", 9, "bold"),
            text_color="white",
            fg_color=tipo_color,
            corner_radius=4,
            padx=8,
            pady=2
        )
        badge.pack(side="left", padx=(0, 10))

        # Product name
        ctk.CTkLabel(
            left,
            text=cambio.nombre,
            font=("Roboto", 12, "bold"),
            anchor="w"
        ).pack(side="left")

        # Right side: Price + Details button
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")

        # Price
        precio_str = (
            f"${cambio.precio_nuevo:.2f}"
            if cambio.tiene_precio
            else "SIN PRECIO"
        )
        precio_color = "#2ECC71" if cambio.tiene_precio else "#E74C3C"

        ctk.CTkLabel(
            right,
            text=precio_str,
            font=("Roboto", 13, "bold"),
            text_color=precio_color
        ).pack(side="left", padx=(0, 10))

        # Details button
        ctk.CTkButton(
            right,
            text="Ver detalles",
            command=lambda: self.mostrar_detalle_expandido(cambio),
            width=90,
            height=28,
            font=("Roboto", 10),
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        ).pack(side="left")

    def mostrar_detalle_expandido(self, cambio: ProductChange):
        """Show expanded detail for a product change"""
        try:
            # Create detail window
            detalle = ctk.CTkToplevel(self)
            detalle.title(f"Detalle: {cambio.nombre}")
            detalle.geometry("600x500")
            detalle.transient(self)
            detalle.grab_set()

            # Header
            header = ctk.CTkFrame(detalle, fg_color=("#2D9B6C", "#1a5d42"))
            header.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(
                header,
                text=f"📊 {cambio.nombre}",
                font=("Roboto", 18, "bold"),
                text_color="white"
            ).pack(pady=15)

            # Product info
            info_frame = ctk.CTkFrame(detalle)
            info_frame.pack(fill="x", padx=20, pady=(0, 10))

            ctk.CTkLabel(
                info_frame,
                text=f"Unidad: {cambio.unidad}",
                font=("Roboto", 12)
            ).pack(anchor="w", padx=15, pady=5)

            precio_str = (
                f"${cambio.precio_nuevo:.2f}"
                if cambio.tiene_precio
                else "SIN PRECIO"
            )
            ctk.CTkLabel(
                info_frame,
                text=f"Precio Base: {precio_str}",
                font=("Roboto", 12, "bold")
            ).pack(anchor="w", padx=15, pady=5)

            # Groups table
            ctk.CTkLabel(
                detalle,
                text="Precios por Grupo:",
                font=("Roboto", 14, "bold")
            ).pack(anchor="w", padx=20, pady=(10, 5))

            # Scroll frame for groups
            scroll_frame = ctk.CTkScrollableFrame(detalle)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

            # Get all groups
            grupos = self.price_repo.get_all_groups_with_discounts()
            precio_base = cambio.precio_nuevo

            for grupo in grupos:
                if isinstance(grupo, dict):
                    clave = grupo['clave_grupo']
                    nombre_tipo = grupo.get('nombre_tipo', 'Sin tipo')
                    descuento = grupo.get('descuento', 0) or 0
                else:
                    # Tuple format: (id_grupo, clave_grupo, descuento)
                    clave = grupo[1]
                    nombre_tipo = 'Sin tipo'  # Not available in tuple
                    descuento = grupo[2] if len(grupo) > 2 and grupo[2] else 0

                # Calculate final price (apply discount)
                precio_final = precio_base * (
                    Decimal('1') - Decimal(str(descuento)) / Decimal('100')
                )

                # Frame for each group
                grupo_frame = ctk.CTkFrame(scroll_frame, fg_color=("gray90", "gray20"))
                grupo_frame.pack(fill="x", pady=3, padx=5)

                content = ctk.CTkFrame(grupo_frame, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=10)

                ctk.CTkLabel(
                    content,
                    text=f"{clave}",
                    font=("Roboto", 12, "bold")
                ).pack(side="left")

                ctk.CTkLabel(
                    content,
                    text=f"({nombre_tipo} - {descuento}%)",
                    font=("Roboto", 10),
                    text_color="gray"
                ).pack(side="left", padx=(10, 0))

                ctk.CTkLabel(
                    content,
                    text=f"${precio_final:.2f}",
                    font=("Roboto", 12, "bold"),
                    text_color="#2ECC71"
                ).pack(side="right")

            # Close button
            ctk.CTkButton(
                detalle,
                text="Cerrar",
                command=detalle.destroy,
                width=120,
                height=35
            ).pack(pady=15)

        except Exception as e:
            print(f"Error mostrando preview expandido: {e}")
            traceback.print_exc()

    def aplicar_cambios(self):
        """Apply proposed changes to database"""
        # ✅ Step 1: Validate with controller
        is_valid, error_message, selected_group = self.controller.validate_apply_changes(
            cambios_propuestos=self.cambios_propuestos,
            productos_sin_precio=self.productos_sin_precio,
            selected_group_id=self.selected_group_id,
            grupos_disponibles=self.grupos_disponibles
        )

        if not is_valid:
            if error_message:
                messagebox.showerror("Error", error_message, parent=self)
            else:
                messagebox.showinfo("Info", "No hay cambios para aplicar", parent=self)
            return

        # ✅ Step 2: Check for products without price
        if self.productos_sin_precio:
            respuesta = messagebox.askyesnocancel(
                "Productos sin precio detectados",
                f"⚠️ Se encontraron {len(self.productos_sin_precio)} productos sin precio.\n\n"
                f"¿Deseas continuar?\n\n"
                f"• SÍ: Aplicar cambios\n"
                f"• NO: Cancelar todo\n"
                f"• CANCELAR: Volver",
                parent=self
            )

            if respuesta is None or not respuesta:
                return

        # ✅ Step 3: Get confirmation message from controller
        mensaje = self.controller.build_confirmation_message(
            cambios_propuestos=self.cambios_propuestos,
            productos_sin_precio=self.productos_sin_precio,
            selected_group=selected_group
        )

        if not messagebox.askyesno("Confirmar cambios", mensaje, parent=self):
            return

        # ✅ Step 4: Apply changes through controller with loading indicator
        def apply_task():
            """Task to run in background thread"""
            return self.controller.apply_changes(
                cambios_propuestos=self.cambios_propuestos,
                productos_sin_precio=self.productos_sin_precio,
                selected_group_id=self.selected_group_id,
                selected_group=selected_group,
                usuario=self.user_info.get('username'),
                nombre_completo=self.user_info.get('nombre_completo', 'N/A'),
                pdf_path=self.pdf_path,
                db_commit_callback=lambda: self.db.commit(),
                db_rollback_callback=lambda: self.db.rollback()
            )

        def on_complete(result):
            """Handle successful completion"""
            success, error_msg, success_msg = result
            if success:
                messagebox.showinfo("Éxito", success_msg, parent=self)
                self.destroy()
            else:
                messagebox.showerror("Error", error_msg, parent=self)

        def on_error(exception):
            """Handle error during processing"""
            messagebox.showerror(
                "Error",
                f"Error aplicando cambios:\n{str(exception)}",
                parent=self
            )
            traceback.print_exc()

        # Show loading indicator and run task in background
        LoadingIndicator.run_with_loading(
            parent=self,
            message="Aplicando cambios...",
            task=apply_task,
            on_complete=on_complete,
            on_error=on_error,
            timeout=60  # 60 seconds timeout for large imports
        )


def abrir_importador_cotizaciones(parent, db, user_info):
    """
    Function to open the importer from dashboard

    Usage in main_application.py:

    {
        'name': 'Importar Cotización',
        'icon': '📄',
        'color': '#9B59B6',
        'function': lambda: abrir_importador_cotizaciones(self, self.db, self.user_info),
        'admin_only': True
    }
    """
    importador = CotizacionImporter(parent, db, user_info)
    importador.focus()


# ============================================================================
# NOTAS TÉCNICAS - CAMBIOS REALIZADOS
# ============================================================================
"""
📝 PROBLEMA IDENTIFICADO:

La clase `ProgressDialog` se usaba en el método `procesar_pdf()` (línea 321)
pero NO estaba definida ni importada, causando un NameError cuando el usuario
intentaba procesar un PDF.

✅ SOLUCIÓN IMPLEMENTADA:

1. Agregada clase `ProgressDialog` completa (líneas 32-119)
   - Ventana de progreso modal con barra de progreso
   - Labels para status y detalles
   - Método `update_progress()` para actualizar el estado
   - Diseño consistente con el resto de la aplicación

2. La clase incluye:
   - Herencia de ctk.CTkToplevel para crear ventana independiente
   - Barra de progreso (CTkProgressBar)
   - Label de estado (status_label)
   - Label de detalles (detail_label)
   - Centrado automático sobre la ventana padre
   - Diseño responsive con grid

3. Uso en el método procesar_pdf():
   - Línea 321: progress = ProgressDialog(self, "Procesando PDF")
   - Actualización de progreso en cada paso
   - Cierre automático al completar

🎯 RESULTADO:

Ahora el botón "🔍 Procesar PDF" funciona correctamente y muestra
una ventana de progreso mientras procesa el archivo PDF.
"""