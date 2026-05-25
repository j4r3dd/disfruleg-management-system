# -*- coding: utf-8 -*-
"""
Price Editor Application - Controller Layer
Coordinates UI with Business Services
NO direct database access - uses services only!
"""

import customtkinter as ctk
from tkinter import messagebox
from decimal import Decimal
from typing import Optional, List

from ..business.product_service import ProductService
from ..business.pricing_service import PricingService
from ..domain.models import Product, Group, ClientType
from ..domain.exceptions import (
    PricingDomainError,
    ProductNotFoundError,
    InvalidPriceError,
    DuplicateProductError,
    ProductLockError
)

# Import utils if available
try:
    from src.utils import normalizar_unidad, normalizar_texto
    USAR_NORMALIZACION = True
except ImportError:
    USAR_NORMALIZACION = False
    def normalizar_unidad(u): return u.upper().strip() if u else "UNIDAD"
    def normalizar_texto(t): return t.lower().strip() if t else ""

from src.theme import COLORS, FONTS
from src.auth.auth_manager import AuthManager


class PriceEditorApplication:
    """
    Price Editor Application Controller
    Coordinates view with business services
    """

    def __init__(
        self,
        root: ctk.CTk,
        user_data: dict,
        product_service: ProductService,
        pricing_service: PricingService,
        filtro_productos: Optional[List[int]] = None
    ):
        """
        Initialize application

        Args:
            root: Main window
            user_data: User information
            product_service: Product business service
            pricing_service: Pricing business service
            filtro_productos: Optional list of product IDs to filter
        """
        self.root = root
        self.user_data = user_data
        self.product_service = product_service
        self.pricing_service = pricing_service
        self.filtro_productos = filtro_productos

        # User info
        self.es_admin = (user_data.get('rol', '') == 'admin')
        self.auth_manager = AuthManager()

        # State
        self.current_group_id = 1
        self.groups: List[Group] = []
        self.client_types: List[ClientType] = []
        self.all_products: List[Product] = []
        self.search_var = ctk.StringVar()
        self.selected_product: Optional[Product] = None
        self.selected_product_price: Optional[object] = None  # Para ProductPrice

        # Pagination state
        self.page_size = 100  # Load 100 products at a time
        self.current_offset = 0
        self.total_count = 0
        self.is_loading = False

        # Search debouncing
        self.search_timer = None

        # UI Variables
        self.group_buttons = []
        self.product_rows = []

        # Window setup
        self._setup_window()

        # Create UI
        self._create_interface()

        # Load initial data
        self._load_initial_data()

    def _setup_window(self):
        """Configure main window"""
        self.root.title("Editor de Precios - Disfruleg")
        self.root.geometry("1400x900")

        # Force window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()

    def _create_interface(self):
        """Create the complete UI"""
        self._create_header()

        if self.filtro_productos:
            self._create_filter_banner()

        self._create_controls_section()
        self._create_main_content()
        self._create_status_bar()

    def _create_header(self):
        """Create application header"""
        header_frame = ctk.CTkFrame(
            self.root,
            fg_color=("#1a1a1a", "#1a1a1a"),
            height=80
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=0)

        # Left: Back button + Logo + Title
        left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        left_frame.pack(side="left", fill="y")

        # Back button
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
            command=self._on_closing
        )
        back_btn.pack(side="left", padx=(0, 15))

        # Logo
        ctk.CTkLabel(
            left_frame,
            text="💰",
            font=("Arial", 28)
        ).pack(side="left", padx=(0, 15))

        # Title
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="EDITOR DE PRECIOS",
            font=("Arial", 16, "bold"),
            text_color=COLORS['success'],
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

    def _create_filter_banner(self):
        """Show banner when filter is active"""
        self.banner_filtro = ctk.CTkFrame(
            self.root,
            fg_color="#FF6B6B",
            height=60
        )
        self.banner_filtro.pack(fill="x", pady=(0, 10))
        self.banner_filtro.pack_propagate(False)

        banner_content = ctk.CTkFrame(self.banner_filtro, fg_color="transparent")
        banner_content.pack(fill="both", expand=True, padx=20, pady=12)

        ctk.CTkLabel(
            banner_content,
            text="⚠️ MODO FILTRADO: Mostrando solo productos seleccionados",
            font=FONTS['body_bold'],
            text_color="white"
        ).pack(side="left")

        ctk.CTkLabel(
            banner_content,
            text=f"({len(self.filtro_productos)} productos)",
            font=FONTS['body'],
            text_color="white"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            banner_content,
            text="✖ Quitar Filtro y Ver Todos",
            command=self._remove_filter,
            fg_color="white",
            text_color="#FF6B6B",
            hover_color="#F0F0F0",
            width=180,
            height=35,
            font=FONTS['body_bold']
        ).pack(side="right")

    def _create_controls_section(self):
        """Create controls section (groups, search, actions)"""
        controls_container = ctk.CTkFrame(self.root, fg_color="transparent")
        controls_container.pack(fill="x", padx=30, pady=(15, 10))

        # 1. Group selection
        group_frame = ctk.CTkFrame(
            controls_container,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=15
        )
        group_frame.pack(fill="x", pady=(0, 10))

        group_header = ctk.CTkFrame(group_frame, fg_color="transparent")
        group_header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            group_header,
            text="1️⃣ Seleccionar Grupo:",
            font=FONTS['subheader'],
            text_color=COLORS['primary']
        ).pack(side="left")

        self.group_buttons_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
        self.group_buttons_frame.pack(fill="x", padx=20, pady=(0, 15))

        # 2. Client type info
        client_frame = ctk.CTkFrame(
            controls_container,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=15
        )
        client_frame.pack(fill="x", pady=(0, 10))

        client_header = ctk.CTkFrame(client_frame, fg_color="transparent")
        client_header.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            client_header,
            text="2️⃣ Información de Tipo de Cliente:",
            font=FONTS['subheader'],
            text_color=COLORS['primary']
        ).pack(side="left")

        self.client_type_info_label = ctk.CTkLabel(
            client_header,
            text="(Seleccione un grupo primero)",
            font=FONTS['body'],
            text_color="gray"
        )
        self.client_type_info_label.pack(side="left", padx=15)

        # 3. Search and actions
        action_frame = ctk.CTkFrame(controls_container, fg_color="transparent")
        action_frame.pack(fill="x")

        # Search
        search_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        search_container.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            search_container,
            text="3️⃣ 🔍 Buscar producto:",
            font=FONTS['subheader']
        ).pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_container,
            textvariable=self.search_var,
            placeholder_text="Buscar por nombre...",
            width=300,
            height=35,
            font=FONTS['body']
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_var.trace("w", lambda *args: self._debounced_search())

        ctk.CTkButton(
            search_container,
            text="✖ Limpiar",
            command=self._clear_search,
            width=80,
            height=35,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS['primary']
        ).pack(side="left")

        # Action buttons
        action_buttons = ctk.CTkFrame(action_frame, fg_color="transparent")
        action_buttons.pack(side="right")

        ctk.CTkButton(
            action_buttons,
            text="➕ Agregar Producto",
            command=self._show_add_product_dialog,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            width=160,
            height=35,
            font=FONTS['body_bold']
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_buttons,
            text="✏️ Editar Nombre",
            command=lambda: (
                self._show_edit_product_name_modal(self.selected_product_price)
                if self.selected_product_price
                else messagebox.showwarning("Advertencia", "Seleccione un producto")
            ),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary'],
            width=160,
            height=35,
            font=FONTS['body_bold']
        ).pack(side="left", padx=5)

        if self.es_admin:
            ctk.CTkButton(
                action_buttons,
                text="🗑️ Eliminar Producto",
                command=self._show_delete_product_modal,
                fg_color=COLORS['danger'],
                hover_color=COLORS['danger_hover'],
                width=160,
                height=35,
                font=FONTS['body_bold']
            ).pack(side="left", padx=5)

    def _create_main_content(self):
        """Create main content area with product table"""
        content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        # Scrollable products container
        self.products_scroll = ctk.CTkScrollableFrame(
            content_frame,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=15
        )
        self.products_scroll.pack(fill="both", expand=True)

        # Table header
        self._create_table_header()

    def _create_table_header(self):
        """Create table header"""
        header = ctk.CTkFrame(
            self.products_scroll,
            fg_color=COLORS['primary'],
            corner_radius=8,
            height=50
        )
        header.pack(fill="x", pady=(10, 5), padx=10)
        header.pack_propagate(False)

        # Configure grid
        header.grid_columnconfigure(0, weight=0, minsize=60)   # ID
        header.grid_columnconfigure(1, weight=3, minsize=320)  # Name
        header.grid_columnconfigure(2, weight=0, minsize=100)  # Unit
        header.grid_columnconfigure(3, weight=1, minsize=140)  # Base Price
        header.grid_columnconfigure(4, weight=1, minsize=150)  # Final Price
        header.grid_columnconfigure(5, weight=0, minsize=100)  # Stock
        header.grid_columnconfigure(6, weight=0, minsize=100)  # Actions

        headers = [
            ("ID", 0),
            ("PRODUCTO", 1),
            ("UNIDAD", 2),
            ("PRECIO BASE", 3),
            ("PRECIO FINAL", 4),
            ("STOCK", 5),
            ("ACCIONES", 6)
        ]

        for text, col in headers:
            ctk.CTkLabel(
                header,
                text=text,
                font=("Arial", 11, "bold"),
                text_color="white"
            ).grid(row=0, column=col, padx=10, pady=12, sticky="ew")

    def _create_status_bar(self):
        """Create status bar"""
        status_frame = ctk.CTkFrame(
            self.root,
            fg_color=("#2a2a2a", "#2a2a2a"),
            height=40
        )
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Listo",
            font=FONTS['body'],
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=20, pady=10)

    # ==================== DATA LOADING ====================

    def _load_initial_data(self):
        """Load initial data from services"""
        try:
            # Load groups
            self.groups = self.pricing_service.get_all_groups()
            self._create_group_buttons()

            # Load client types
            self.client_types = self.pricing_service.get_all_client_types()

            # Set initial group and load products
            if self.groups:
                self.current_group_id = self.groups[0].id_grupo
                self._update_client_type_info()
                self._load_products()

            self._update_status("Datos cargados correctamente")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al cargar datos iniciales:\n{str(e)}"
            )

    def _create_group_buttons(self):
        """Create group selection buttons"""
        # Clear existing buttons
        for widget in self.group_buttons_frame.winfo_children():
            widget.destroy()

        self.group_buttons = []

        for group in self.groups:
            btn = ctk.CTkButton(
                self.group_buttons_frame,
                text=group.clave_grupo,
                command=lambda g=group: self._on_group_change(g.id_grupo),
                width=120,
                height=35,
                corner_radius=8,
                fg_color=COLORS['primary'] if group.id_grupo == self.current_group_id else "transparent",
                border_width=2,
                border_color=COLORS['primary']
            )
            btn.pack(side="left", padx=5)
            self.group_buttons.append((btn, group.id_grupo))

    def _load_products(self, append=False):
        """
        Load products for current group with pagination

        Args:
            append: If True, append to existing products. If False, clear and reload.
        """
        if self.is_loading:
            return  # Prevent concurrent loads

        self.is_loading = True

        try:
            # If not appending, reset pagination and clear UI
            if not append:
                self.current_offset = 0
                self.all_products = []
                # Clear existing rows
                for widget in self.products_scroll.winfo_children()[1:]:
                    widget.destroy()

            # Get search query
            search_query = self.search_var.get().strip() if self.search_var.get().strip() else None

            # Show loading indicator
            self._update_status("Cargando productos...")

            # Get product prices from service with pagination
            product_prices, total_count = self.pricing_service.get_product_prices_for_group(
                self.current_group_id,
                self.filtro_productos,
                search_query=search_query,
                limit=self.page_size,
                offset=self.current_offset
            )

            self.total_count = total_count

            # Append to all_products
            if append:
                self.all_products.extend(product_prices)
            else:
                self.all_products = product_prices

            # Create product rows
            start_idx = len(self.all_products) - len(product_prices)
            for idx, product_price in enumerate(product_prices, start=start_idx):
                self._create_product_row(product_price, idx)

            # Update offset for next load
            self.current_offset += len(product_prices)

            # Update or create "Load More" button
            self._update_load_more_button()

            # Update status
            group_name = self._get_current_group_name()
            filtro_text = f" (FILTRADOS: {len(self.filtro_productos)})" if self.filtro_productos else ""
            search_text = f" | Búsqueda: '{search_query}'" if search_query else ""
            self._update_status(
                f"Mostrando {len(self.all_products)} de {self.total_count} productos para grupo: {group_name}{filtro_text}{search_text}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos:\n{str(e)}")
        finally:
            self.is_loading = False

    def _create_product_row(self, product_price, idx):
        """Create a product row"""
        precio_base = product_price.precio_base

        # Determine row color
        if product_price.es_especial:
            row_color = ("#FFE5B4", "#8B6914")
        elif precio_base == 0:
            row_color = ("#FFE5E5", "#8B3A3A")
        else:
            row_color = ("white", "gray20") if idx % 2 == 0 else ("gray95", "gray18")

        row_frame = ctk.CTkFrame(
            self.products_scroll,
            fg_color=row_color,
            corner_radius=8
        )
        row_frame.pack(fill="x", pady=1, padx=2)

        # Store data
        row_frame.product_data = product_price
        row_frame.original_color = row_color

        # Bind events
        row_frame.bind("<Button-1>", lambda e, p=product_price: self._select_product(p))
        row_frame.bind("<Double-Button-1>", lambda e, p=product_price: self._edit_product_price(p))
        row_frame.bind("<Enter>", lambda e, f=row_frame: f.configure(fg_color=COLORS['primary']))
        row_frame.bind("<Leave>", lambda e, f=row_frame: f.configure(fg_color=row_frame.original_color))
        row_frame.configure(cursor="hand2")

        # Configure grid
        row_frame.grid_columnconfigure(0, weight=0, minsize=60)
        row_frame.grid_columnconfigure(1, weight=3, minsize=320)
        row_frame.grid_columnconfigure(2, weight=0, minsize=100)
        row_frame.grid_columnconfigure(3, weight=1, minsize=140)
        row_frame.grid_columnconfigure(4, weight=1, minsize=150)
        row_frame.grid_columnconfigure(5, weight=0, minsize=100)
        row_frame.grid_columnconfigure(6, weight=0, minsize=100)

        # ID
        lbl = ctk.CTkLabel(row_frame, text=str(product_price.id_producto), font=FONTS['body'])
        lbl.grid(row=0, column=0, padx=10, pady=10)
        lbl.bind("<Button-1>", lambda e, p=product_price: self._select_product(p))
        lbl.bind("<Double-Button-1>", lambda e, p=product_price: self._edit_product_price(p))

        # Name
        lbl = ctk.CTkLabel(row_frame, text=product_price.nombre_producto, font=FONTS['body_bold'], anchor="w")
        lbl.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        lbl.bind("<Button-1>", lambda e, p=product_price: self._select_product(p))
        lbl.bind("<Double-Button-1>", lambda e, p=product_price: self._edit_product_price(p))

        # Unit
        lbl = ctk.CTkLabel(row_frame, text=product_price.unidad_producto, font=FONTS['body'])
        lbl.grid(row=0, column=2, padx=10, pady=10)
        lbl.bind("<Button-1>", lambda e, p=product_price: self._select_product(p))
        lbl.bind("<Double-Button-1>", lambda e, p=product_price: self._edit_product_price(p))

        # Base price
        precio_text = f"${precio_base:,.2f}" if precio_base > 0 else "Sin precio"
        lbl = ctk.CTkLabel(row_frame, text=precio_text, font=FONTS['body_bold'], text_color=COLORS['primary'])
        lbl.grid(row=0, column=3, padx=10, pady=10)
        lbl.bind("<Button-1>", lambda e, p=product_price: self._select_product(p))
        lbl.bind("<Double-Button-1>", lambda e, p=product_price: self._edit_product_price(p))

        # Final price
        precio_final_text = f"${product_price.precio_final:,.2f}"
        lbl = ctk.CTkLabel(row_frame, text=precio_final_text, font=FONTS['body_bold'], text_color=COLORS['success'])
        lbl.grid(row=0, column=4, padx=10, pady=10)
        lbl.bind("<Button-1>", lambda e, p=product_price: self._select_product(p))
        lbl.bind("<Double-Button-1>", lambda e, p=product_price: self._edit_product_price(p))

        # Stock
        lbl = ctk.CTkLabel(row_frame, text=f"{product_price.stock:.2f}", font=FONTS['body'])
        lbl.grid(row=0, column=5, padx=10, pady=10)
        lbl.bind("<Button-1>", lambda e, p=product_price: self._select_product(p))
        lbl.bind("<Double-Button-1>", lambda e, p=product_price: self._edit_product_price(p))

        # Edit button
        ctk.CTkButton(
            row_frame,
            text="✏️ Editar",
            command=lambda p=product_price: self._edit_product_price(p),
            width=80,
            height=30,
            fg_color=COLORS['accent'],
            font=("Arial", 10)
        ).grid(row=0, column=6, padx=10, pady=10)

    # ==================== EVENT HANDLERS ====================

    def _on_group_change(self, group_id: int):
        """Handle group selection change"""
        self.current_group_id = group_id

        # Update button colors
        for btn, btn_group_id in self.group_buttons:
            if btn_group_id == group_id:
                btn.configure(fg_color=COLORS['primary'])
            else:
                btn.configure(fg_color="transparent")

        # Update client type info
        self._update_client_type_info()

        # Reload products
        self._load_products()

    def _update_client_type_info(self):
        """Update client type information display"""
        try:
            client_type = self.pricing_service.get_client_type_for_group(
                self.current_group_id
            )

            client_count = self.pricing_service.get_group_client_count(
                self.current_group_id
            )

            info_text = (
                f"📊 Tipo: {client_type.nombre_tipo} | "
                f"Descuento: {client_type.descuento}% | "
                f"Clientes: {client_count}"
            )

            self.client_type_info_label.configure(
                text=info_text,
                text_color="white"
            )

        except Exception as e:
            self.client_type_info_label.configure(
                text="Error cargando información",
                text_color="red"
            )

    def _debounced_search(self):
        """Debounce search input - wait 300ms after user stops typing"""
        # Cancel previous timer if exists
        if self.search_timer:
            self.root.after_cancel(self.search_timer)

        # Set new timer
        self.search_timer = self.root.after(300, self._trigger_search)

    def _trigger_search(self):
        """Trigger actual search after debounce delay"""
        self._load_products(append=False)

    def _update_load_more_button(self):
        """Update or create 'Load More' button"""
        # Check if there are more products to load
        has_more = len(self.all_products) < self.total_count

        # Find existing load more button
        load_more_btn = None
        for widget in self.products_scroll.winfo_children():
            if hasattr(widget, 'is_load_more_btn'):
                load_more_btn = widget
                break

        if has_more:
            if not load_more_btn:
                # Create load more button
                load_more_btn = ctk.CTkButton(
                    self.products_scroll,
                    text=f"⬇ Cargar Más Productos ({len(self.all_products)}/{self.total_count})",
                    command=lambda: self._load_products(append=True),
                    fg_color=COLORS['accent'],
                    hover_color=COLORS['primary'],
                    height=50,
                    font=FONTS['body_bold']
                )
                load_more_btn.is_load_more_btn = True
                load_more_btn.pack(fill="x", pady=10, padx=10)
            else:
                # Update button text
                load_more_btn.configure(
                    text=f"⬇ Cargar Más Productos ({len(self.all_products)}/{self.total_count})"
                )
        else:
            # Remove load more button if exists
            if load_more_btn:
                load_more_btn.destroy()

    def _clear_search(self):
        """Clear search filter"""
        self.search_var.set("")
        # _load_products will be called automatically by the search var trace

    def _remove_filter(self):
        """Remove product filter"""
        self.filtro_productos = None

        if hasattr(self, 'banner_filtro'):
            self.banner_filtro.destroy()
            delattr(self, 'banner_filtro')

        self._load_products(append=False)
        self._update_status("✅ Filtro eliminado - Mostrando todos los productos")

    def _select_product(self, product_price):
        """Select a product"""
        self.selected_product_price = product_price
        # Crear un Product desde ProductPrice
        self.selected_product = Product(
            id_producto=product_price.id_producto,
            nombre_producto=product_price.nombre_producto,
            unidad_producto=product_price.unidad_producto,
            stock=product_price.stock,
            es_especial=product_price.es_especial
        )

    # ==================== DIALOG HANDLERS ====================

    def _show_add_product_dialog(self):
        """Show dialog to add new product"""
        try:
            # Use shared dialog from inventory
            # Import here to avoid circular dependencies if any
            from src.modules.inventory.ui.product_dialog import create_product_dialog
            
            success, product_data = create_product_dialog(self.root)
            
            if success:
                # Create product via service
                # Note: Inventory dialog returns 'nombre' and 'unidad'
                # Stock and is_special are not supported in the shared dialog yet, defaulting to 0 and False
                product_id = self.product_service.create_product(
                    nombre_producto=product_data['nombre'],
                    unidad_producto=product_data['unidad'],
                    stock=Decimal("0"),
                    es_especial=False
                )
                
                messagebox.showinfo("Éxito", f"Producto '{product_data['nombre']}' creado exitosamente (ID: {product_id})")
                
                # Reload products
                self._load_products(append=False)
                
        except DuplicateProductError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear producto:\n{str(e)}")

    def _edit_product_price(self, product_price):
        """Edit product price"""
        if not product_price:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return

        # Check if special product and user is not admin
        if product_price.es_especial and not self.es_admin:
            if not self._verify_admin_password(f"editar precio de {product_price.nombre_producto}"):
                return

        popup = ctk.CTkToplevel(self.root)
        popup.title(f"Editar Precio Base - {product_price.nombre_producto}")
        popup.geometry("650x550")
        popup.transient(self.root)
        popup.grab_set()

        # Header
        header_color = COLORS['accent'] if product_price.es_especial else COLORS['primary']
        header = ctk.CTkFrame(popup, fg_color=header_color)
        header.pack(fill="x")

        group_name = self._get_current_group_name()
        ctk.CTkLabel(
            header,
            text=f"EDITAR PRECIO BASE - GRUPO: {group_name}",
            font=FONTS['header'],
            text_color="white"
        ).pack(pady=20)

        if product_price.es_especial:
            ctk.CTkLabel(
                header,
                text="🔒 PRODUCTO ESPECIAL",
                font=FONTS['body_bold'],
                text_color="white"
            ).pack(pady=(0, 15))

        # Content
        content = ctk.CTkFrame(popup, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=15)

        # Product info
        info_card = ctk.CTkFrame(content, fg_color=("gray85", "gray25"), corner_radius=10)
        info_card.pack(fill="x", pady=(0, 15))

        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(info_content, text=f"Producto: {product_price.nombre_producto}", font=FONTS['body'], anchor="w").pack(fill="x")
        ctk.CTkLabel(info_content, text=f"Unidad: {product_price.unidad_producto}", font=FONTS['body'], anchor="w").pack(fill="x")
        ctk.CTkLabel(info_content, text=f"Stock actual: {product_price.stock:.2f}", font=FONTS['body'], anchor="w").pack(fill="x")

        precio_actual_text = f"${product_price.precio_base:.2f}" if product_price.precio_base > 0 else "Sin precio"
        ctk.CTkLabel(
            info_content,
            text=f"Precio base actual: {precio_actual_text}",
            font=FONTS['body_bold'],
            text_color=COLORS['primary'],
            anchor="w"
        ).pack(fill="x")

        # Price input
        form_frame = ctk.CTkFrame(content, fg_color="transparent")
        form_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(form_frame, text="Nuevo Precio Base:", font=FONTS['subheader'], anchor="w").pack(fill="x", pady=(0, 5))

        price_var = ctk.StringVar(value=str(product_price.precio_base))
        price_entry = ctk.CTkEntry(form_frame, textvariable=price_var, height=40, font=("Arial", 14))
        price_entry.pack(fill="x")
        price_entry.focus_set()

        # Preview
        preview_card = ctk.CTkFrame(content, fg_color=("gray85", "gray25"), corner_radius=10)
        preview_card.pack(fill="both", expand=True, pady=(0, 15))

        ctk.CTkLabel(
            preview_card,
            text="Vista Previa: Precio Final",
            font=FONTS['subheader'],
            text_color=COLORS['primary']
        ).pack(padx=15, pady=(12, 8), anchor="w")

        preview_label = ctk.CTkLabel(
            preview_card,
            text="",
            font=("Arial", 16, "bold"),
            text_color=COLORS['success']
        )
        preview_label.pack(padx=15, pady=(0, 15))

        def update_preview(*args):
            try:
                base_price = Decimal(price_var.get().strip()) if price_var.get().strip() else Decimal('0')
                final_price = base_price * (1 - product_price.descuento / 100)
                preview_label.configure(
                    text=f"Precio Final: ${final_price:,.2f} (Descuento: {product_price.descuento}%)"
                )
            except:
                preview_label.configure(text="Precio inválido")

        price_var.trace("w", update_preview)
        update_preview()

        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Precio (Todos los Grupos)",
            command=lambda: self._save_price_change(popup, product_price.id_producto, price_var.get()),
            fg_color=COLORS['success'],
            height=45,
            font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=popup.destroy,
            fg_color="gray",
            height=45,
            font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

    def _save_price_change(self, popup, product_id, new_price_str):
        """Save price change for ALL groups"""
        try:
            # Validate price
            try:
                new_price = Decimal(new_price_str.strip())
            except:
                messagebox.showerror("Error", "Precio inválido", parent=popup)
                return

            if new_price < 0:
                messagebox.showerror("Error", "El precio no puede ser negativo", parent=popup)
                return

            # Save via service - applies to current group only
            self.pricing_service.set_base_price(
                product_id,
                self.current_group_id,
                new_price
            )

            popup.destroy()
            group_name = self._get_current_group_name()
            messagebox.showinfo("Éxito", f"Precio base actualizado para el grupo '{group_name}' exitosamente")

            # Reload products
            self._load_products(append=False)

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar precio:\n{str(e)}", parent=popup)

    def _delete_product(self):
        """Delete selected product"""
        if not self.selected_product:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto para eliminar")
            return

        product_name = self.selected_product.nombre_producto

        # Confirm
        if not messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el producto '{product_name}'?\n\n"
            "ADVERTENCIA: Esto eliminará:\n"
            "- El producto\n"
            "- Todos sus precios en todos los grupos\n"
            "- Esta acción NO se puede deshacer"
        ):
            return

        # Admin verification
        if not self._verify_admin_password(f"eliminar {product_name}"):
            return

        try:
            # Delete via service
            username = self.user_data.get('nombre_completo', 'Usuario')
            self.product_service.delete_product(
                self.selected_product.id_producto,
                username
            )

            messagebox.showinfo("Éxito", f"Producto '{product_name}' eliminado exitosamente")

            # Reload products
            self.selected_product = None
            self._load_products(append=False)

        except ProductLockError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar producto:\n{str(e)}")

    def _verify_admin_password(self, action: str) -> bool:
        """Verify admin password"""
        popup = ctk.CTkToplevel(self.root)
        popup.title("Verificación de Administrador")
        popup.geometry("450x250")
        popup.transient(self.root)
        popup.grab_set()

        result = [False]

        header = ctk.CTkFrame(popup, fg_color=COLORS['danger'])
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="🔐 VERIFICACIÓN DE ADMINISTRADOR",
            font=FONTS['header'],
            text_color="white"
        ).pack(pady=20)

        content = ctk.CTkFrame(popup, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(
            content,
            text=f"Se requiere contraseña de administrador para: {action}",
            font=FONTS['body'],
            wraplength=380
        ).pack(pady=(0, 15))

        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            content,
            textvariable=password_var,
            placeholder_text="Contraseña de administrador",
            show="●",
            height=35,
            font=FONTS['body']
        )
        password_entry.pack(fill="x", pady=(0, 15))
        password_entry.focus_set()

        def verify():
            password = password_var.get()
            if self.auth_manager.verify_admin_password(password):
                result[0] = True
                popup.destroy()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta", parent=popup)
                password_var.set("")

        password_entry.bind("<Return>", lambda e: verify())

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="✅ Verificar",
            command=verify,
            fg_color=COLORS['success'],
            height=40,
            font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=popup.destroy,
            fg_color="gray",
            height=40,
            font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

        popup.wait_window()
        return result[0]

    # ==================== EDITAR NOMBRE Y FUSIÓN ====================

    def _show_edit_product_name_modal(self, product_price):
        """Modal para editar nombre del producto"""
        if not product_price:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        product_id = product_price.id_producto
        product_name = product_price.nombre_producto
        product_unit = product_price.unidad_producto
        product_stock = product_price.stock
        product_special = product_price.es_especial
        
        popup = ctk.CTkToplevel(self.root)
        popup.title(f"Editar: {product_name}")
        popup.geometry("500x320")
        popup.transient(self.root)
        popup.grab_set()
        popup.resizable(False, False)
        
        # Header
        header = ctk.CTkFrame(popup, fg_color=COLORS['primary'], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="✏️ EDITAR NOMBRE",
            font=FONTS['header'],
            text_color="white"
        ).pack(pady=12)
        
        # Content 
        content = ctk.CTkFrame(popup, fg_color="transparent")
        content.pack(fill="both", expand=False, padx=15, pady=10)
        
        # Nombre actual
        ctk.CTkLabel(
            content,
            text=f"Nombre actual: {product_name}",
            font=FONTS['body'],
            text_color="gray70"
        ).pack(anchor="w", pady=(0, 8))
        
        # Input label
        ctk.CTkLabel(content, text="Nuevo nombre:", font=FONTS['body']).pack(anchor="w", pady=(0, 4))
        
        name_var = ctk.StringVar(value=product_name)
        name_entry = ctk.CTkEntry(content, textvariable=name_var, height=32, font=("Arial", 12))
        name_entry.pack(fill="x", pady=(0, 8))
        name_entry.focus_set()
        
        # Status
        status_label = ctk.CTkLabel(content, text="", font=FONTS['body'], text_color="gray60")
        status_label.pack(fill="x", pady=(0, 10))
        
        def validate(*args):
            new_name = name_var.get().strip()
            if not new_name:
                status_label.configure(text="", text_color="gray60")
                return
            if new_name == product_name:
                status_label.configure(text="(Sin cambios)", text_color="gray60")
                return
            
            try:
                duplicates = self.product_service.search_products(new_name)
                for p in duplicates:
                    if p.id_producto != product_id and p.nombre_producto.lower() == new_name.lower():
                        status_label.configure(text=f"⚠️ Ya existe otro producto", text_color="orange")
                        return
                status_label.configure(text="✓ Disponible", text_color="green")
            except:
                status_label.configure(text="", text_color="gray60")
        
        name_var.trace("w", validate)
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        def save():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showwarning("Error", "El nombre no puede estar vacío")
                return
            if new_name == product_name:
                popup.destroy()
                return
            
            try:
                duplicates = self.product_service.search_products(new_name)
                duplicate = None
                for p in duplicates:
                    if p.id_producto != product_id and p.nombre_producto.lower() == new_name.lower():
                        duplicate = p
                        break
                
                if duplicate:
                    popup.destroy()
                    target = Product(
                        id_producto=duplicate.id_producto,
                        nombre_producto=duplicate.nombre_producto,
                        unidad_producto=duplicate.unidad_producto,
                        stock=duplicate.stock,
                        es_especial=duplicate.es_especial
                    )
                    source = Product(
                        id_producto=product_id,
                        nombre_producto=product_name,
                        unidad_producto=product_unit,
                        stock=product_stock,
                        es_especial=product_special
                    )
                    self._show_merge_options_modal(source, new_name, target)
                else:
                    self.product_service.update_product(
                        product_id, new_name, product_unit, product_stock, product_special
                    )
                    popup.destroy()
                    messagebox.showinfo("Éxito", f"Renombrado a '{new_name}'")
                    self._load_products(append=False)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ctk.CTkButton(
            btn_frame, text="💾 Guardar", command=save,
            fg_color=COLORS['success'], height=38, font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        ctk.CTkButton(
            btn_frame, text="❌ Cancelar", command=popup.destroy,
            fg_color="gray", height=38, font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True)

    def _show_merge_options_modal(self, source_product: Product, new_name: str, target_product: Product):
        """Modal cuando existe un producto con el mismo nombre"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("⚠️ Producto Duplicado")
        dialog.geometry("750x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="orange", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="⚠️ EXISTE UN PRODUCTO CON ESTE NOMBRE",
            font=FONTS['header'],
            text_color="white"
        ).pack(pady=15)
        
        # Content
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Info section
        info_frame = ctk.CTkFrame(content, fg_color=("gray90", "gray15"), corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 25))
        
        ctk.CTkLabel(
            info_frame,
            text="Información del conflicto:",
            font=FONTS['subheader'],
            text_color=COLORS['primary']
        ).pack(anchor="w", padx=15, pady=(12, 8))
        
        info_text = f"Intenta cambiar: '{source_product.nombre_producto}' → '{new_name}'\nPero ya existe: '{target_product.nombre_producto}' (ID: {target_product.id_producto})"
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=FONTS['body'],
            wraplength=650,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 12))
        
        # Options section
        ctk.CTkLabel(
            content,
            text="Elige qué hacer:",
            font=FONTS['subheader'],
            text_color=COLORS['primary']
        ).pack(anchor="w", pady=(0, 12))
        
        selected = [None]
        option_frames = []
        
        # Opción 1: Fusionar (recomendado)
        opt1 = ctk.CTkFrame(content, fg_color=("gray90", "gray20"), corner_radius=10, border_width=2, border_color="gray50")
        opt1.pack(fill="x", pady=(0, 12))
        option_frames.append((opt1, "merge"))
        
        def select1():
            for frame, _ in option_frames:
                frame.configure(border_color="gray50")
            opt1.configure(border_color="green")
            selected[0] = "merge"
        
        opt1_content = ctk.CTkFrame(opt1, fg_color="transparent")
        opt1_content.pack(fill="x", padx=15, pady=12)
        
        opt1_header = ctk.CTkFrame(opt1_content, fg_color="transparent")
        opt1_header.pack(fill="x", pady=(0, 8))
        
        ctk.CTkRadioButton(
            opt1_header,
            text="1. FUSIONAR (Recomendado)",
            command=select1,
            radiobutton_width=22,
            radiobutton_height=22,
            font=FONTS['body_bold'],
            text_color="green"
        ).pack(side="left")
        
        ctk.CTkLabel(
            opt1_header,
            text="✓ Mejor opción",
            font=FONTS['body'],
            text_color="green"
        ).pack(side="right")
        
        ctk.CTkLabel(
            opt1_content,
            text=f"Se eliminará '{source_product.nombre_producto}' y se consolidarán sus datos en '{target_product.nombre_producto}'.\nSolo habrá UN producto en el sistema.",
            font=FONTS['body'],
            text_color="gray70",
            wraplength=600,
            justify="left"
        ).pack(anchor="w", pady=(0, 0))
        
        # Opción 2: Cancelar
        opt2 = ctk.CTkFrame(content, fg_color=("gray90", "gray20"), corner_radius=10, border_width=2, border_color="gray50")
        opt2.pack(fill="x", pady=(0, 0))
        option_frames.append((opt2, "cancel"))
        
        def select2():
            for frame, _ in option_frames:
                frame.configure(border_color="gray50")
            opt2.configure(border_color="red")
            selected[0] = "cancel"
        
        opt2_content = ctk.CTkFrame(opt2, fg_color="transparent")
        opt2_content.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkRadioButton(
            opt2_content,
            text="2. Cancelar - No hacer nada",
            command=select2,
            radiobutton_width=22,
            radiobutton_height=22,
            font=FONTS['body_bold']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            opt2_content,
            text="Vuelve al editor sin aplicar cambios.",
            font=FONTS['body'],
            text_color="gray70",
            wraplength=600,
            justify="left"
        ).pack(anchor="w", pady=(4, 0))
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        def handle_choice():
            if selected[0] == "merge":
                dialog.destroy()
                self._show_merge_confirmation_modal(source_product, target_product)
            elif selected[0] == "cancel":
                dialog.destroy()
            else:
                messagebox.showwarning("Selección", "Por favor selecciona una opción")
        
        ctk.CTkButton(
            btn_frame,
            text="✓ Continuar",
            command=handle_choice,
            fg_color=COLORS['success'],
            height=40,
            font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Cerrar",
            command=dialog.destroy,
            fg_color="gray",
            height=40,
            font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True)

    def _show_merge_confirmation_modal(self, source_product: Product, target_product: Product):
        """Modal para confirmar fusión de productos"""
        popup = ctk.CTkToplevel(self.root)
        popup.title("Confirmar Fusión")
        popup.geometry("700x350")
        popup.transient(self.root)
        popup.grab_set()
        popup.resizable(False, False)
        
        # Header
        header = ctk.CTkFrame(popup, fg_color=COLORS['danger'], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="🔀 FUSIONAR PRODUCTOS", font=FONTS['header'], text_color="white").pack(pady=12)
        
        # Content
        content = ctk.CTkFrame(popup, fg_color="transparent")
        content.pack(fill="both", expand=False, padx=30, pady=20)
        
        # Info
        info = f"Se eliminará:\n'{source_product.nombre_producto}' (ID: {source_product.id_producto})\n\nSe mantiene:\n'{target_product.nombre_producto}' (ID: {target_product.id_producto})\n\nSe consolidarán todos los precios."
        ctk.CTkLabel(content, text=info, font=FONTS['body'], wraplength=600).pack(fill="x", pady=(0, 20))
        
        # Confirmation
        check_var = ctk.StringVar(value="no")
        ctk.CTkCheckBox(
            content,
            text="Confirmo que deseo fusionar estos productos",
            variable=check_var,
            onvalue="yes",
            offvalue="no",
            checkbox_width=20,
            checkbox_height=20,
            font=FONTS['body']
        ).pack(anchor="w", pady=(0, 15))
        
        # Buttons
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        def execute_merge():
            if check_var.get() != "yes":
                messagebox.showwarning("Confirmación", "Debe confirmar la operación")
                return
            
            try:
                username = self.user_data.get('nombre_completo', 'Usuario')
                self.product_service.delete_product(source_product.id_producto, username)
                
                popup.destroy()
                messagebox.showinfo("Éxito", f"'{source_product.nombre_producto}' se fusionó en '{target_product.nombre_producto}'")
                self._load_products(append=False)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en fusión: {str(e)}")
        
        ctk.CTkButton(
            btn_frame, text="✓ Confirmar Fusión", command=execute_merge, fg_color=COLORS['danger'], height=38, font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame, text="❌ Cancelar", command=popup.destroy, fg_color="gray", height=38, font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True)

    def _show_delete_product_modal(self):
        """Modal mejorado para eliminar producto"""
        if not self.selected_product:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        product = self.selected_product
        
        popup = ctk.CTkToplevel(self.root)
        popup.title("Eliminar Producto")
        popup.geometry("600x350")
        popup.transient(self.root)
        popup.grab_set()
        
        # Header
        header = ctk.CTkFrame(popup, fg_color=COLORS['danger'])
        header.pack(fill="x")
        ctk.CTkLabel(header, text="🗑️ ELIMINAR PRODUCTO", font=FONTS['header'], text_color="white").pack(pady=15)
        
        # Content
        content = ctk.CTkFrame(popup, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        warning_text = f"¿Está seguro de eliminar:\n\n'{product.nombre_producto}'\n(ID: {product.id_producto})\n\nSE ELIMINARÁ:\n• El producto\n• Todos sus precios en todos los grupos\n• NO SE PUEDE DESHACER"
        ctk.CTkLabel(content, text=warning_text, font=FONTS['body'], wraplength=500).pack(fill="x", pady=(0, 20))
        
        # Password
        ctk.CTkLabel(content, text="Contraseña de administrador:", font=FONTS['subheader']).pack(anchor="w", pady=(10, 5))
        
        pwd_var = ctk.StringVar()
        pwd_entry = ctk.CTkEntry(content, textvariable=pwd_var, show="●", height=35, font=("Arial", 12))
        pwd_entry.pack(fill="x", pady=(0, 20))
        pwd_entry.focus_set()
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        def delete_it():
            try:
                if not self.auth_manager.verify_admin_password(pwd_var.get()):
                    messagebox.showerror("Error", "Contraseña incorrecta")
                    pwd_var.set("")
                    return
                
                username = self.user_data.get('nombre_completo', 'Usuario')
                self.product_service.delete_product(product.id_producto, username)
                
                popup.destroy()
                messagebox.showinfo("Éxito", f"Producto '{product.nombre_producto}' eliminado")
                self.selected_product = None
                self._load_products(append=False)
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ctk.CTkButton(
            btn_frame, text="⚠️ Sí, Eliminar", command=delete_it, fg_color=COLORS['danger'], height=35, font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame, text="❌ Cancelar", command=popup.destroy, fg_color="gray", height=35, font=FONTS['body_bold']
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

    # ==================== HELPERS ====================

    def _get_current_group_name(self) -> str:
        """Get current group name"""
        for group in self.groups:
            if group.id_grupo == self.current_group_id:
                return group.clave_grupo
        return "Desconocido"

    def _update_status(self, text: str):
        """Update status bar"""
        self.status_label.configure(text=text)

    def _on_closing(self):
        """Handle window closing"""
        # Release all locks
        try:
            username = self.user_data.get('nombre_completo', 'Unknown')
            self.product_service.release_all_locks_for_user(username)
        except:
            pass

        self.root.destroy()