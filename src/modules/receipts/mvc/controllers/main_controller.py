# -*- coding: utf-8 -*-
"""
Main Controller - Orchestrator
Coordinates all specialized controllers
"""

import traceback

from src.modules.receipts.mvc.models.receipt_model import ReciboModel
from src.modules.receipts.mvc.views.receipt_view import ReciboView
from src.modules.receipts.models.cart_model import CartModel
from src.modules.receipts.mvc.controllers.client_selection_controller import ClientSelectionController
from src.modules.receipts.mvc.controllers.product_search_controller import ProductSearchController
from src.modules.receipts.mvc.controllers.order_controller import OrderController
from src.modules.receipts.mvc.controllers.export_controller import ExportController
from src.modules.receipts.mvc.controllers.sales_controller import SalesController
from src.modules.receipts.mvc.controllers.settings_controller import SettingsController
from src.config import debug_print


class MainController:
    """
    Main Controller - Orchestrates all specialized controllers

    This controller follows the Coordinator pattern:
    - Initializes all sub-controllers
    - Binds events to appropriate controllers
    - Manages shared state (cart_model)
    - Coordinates inter-controller communication

    Architecture:
        MainController (Orchestrator)
        ├── ClientSelectionController (group/client selection)
        ├── ProductSearchController (product search/addition)
        ├── OrderController (order management)
        ├── ExportController (PDF/Excel generation)
        ├── SalesController (sales processing)
        └── SettingsController (configuration)
    """

    def __init__(
        self,
        view: ReciboView,
        model: ReciboModel,
        nombre_usuario: str = "Usuario",
        username: str = None
    ):
        """
        Initialize Main Controller and all sub-controllers

        Args:
            view: Main view component
            model: Data model
            nombre_usuario: Display name for user
            username: Username for database operations
        """
        self.view = view
        self.model = model
        self.nombre_usuario = nombre_usuario
        self.username = username if username else nombre_usuario

        # Shared cart data model
        self.cart_model = CartModel()

        # Initialize all sub-controllers
        self._initialize_controllers()

        # Bind events and initialize UI
        self._bind_events()
        self._initialize_ui()

        debug_print("✅ MainController initialized with specialized controllers")

    # ==================== INITIALIZATION ====================

    def _initialize_controllers(self):
        """Initialize all specialized controllers"""

        # Client selection controller
        self.client_ctrl = ClientSelectionController(
            self.view,
            self.model,
            self.cart_model
        )

        # Order controller (create FIRST - before export_ctrl)
        self.order_ctrl = OrderController(
            self.view,
            self.model,
            self.cart_model,
            self.client_ctrl,
            self.username,
            on_pdf_generate_callback=None  # Will be set after export_ctrl is created
        )

        # Export controller (NOW receives order_ctrl reference)
        self.export_ctrl = ExportController(
            self.view,
            self.model,
            self.cart_model,
            self.client_ctrl,
            self.order_ctrl  # ← ESTA ES LA NUEVA LÍNEA CRÍTICA
        )

        # NOW set the PDF callback after export_ctrl is created
        self.order_ctrl.on_pdf_generate_callback = self.export_ctrl.generate_pdf

        # Product search controller
        self.product_ctrl = ProductSearchController(
            self.view,
            self.model,
            self.cart_model,
            self.client_ctrl,
            on_cart_updated_callback=self._on_cart_updated
        )

        # Sales controller
        self.sales_ctrl = SalesController(
            self.view,
            self.model,
            self.cart_model,
            self.client_ctrl,
            self.order_ctrl,
            self.export_ctrl
        )

        # Settings controller
        self.settings_ctrl = SettingsController(
            self.view,
            self.model,
            self.cart_model
        )

        debug_print("✅ All specialized controllers initialized")

    def _bind_events(self):
        """Bind View callbacks to appropriate controller methods"""

        # Client selection events → ClientSelectionController
        self.view.on_grupo_seleccionado = self.client_ctrl.on_grupo_seleccionado
        self.view.on_cliente_seleccionado = self.client_ctrl.on_cliente_seleccionado

        # Product search events → ProductSearchController
        self.view.on_busqueda_changed = self.product_ctrl.on_busqueda_changed

        # Order management events → OrderController
        self.view.on_nueva_orden = self.order_ctrl.on_nueva_orden
        self.view.on_guardar_orden = self.order_ctrl.on_guardar_orden
        self.view.on_ver_ordenes = self.order_ctrl.on_ver_ordenes

        # Sales event → SalesController
        self.view.on_procesar_venta = self.sales_ctrl.on_procesar_venta

        # Export events → ExportController
        self.view.on_generar_pdf = self.export_ctrl.on_generar_pdf
        self.view.on_generar_excel = self.export_ctrl.on_generar_excel

        # Settings event → SettingsController
        self.view.on_configurar_rutas = self.settings_ctrl.on_configurar_rutas

        # Window close → MainController
        self.view.set_close_handler(self.on_close)

        debug_print("✅ View events bound to specialized controllers")

    def _initialize_ui(self):
        """Initialize UI with data from Model"""
        try:
            # Create UI structure
            self.view.crear_interface()

            # Create header
            self.view.crear_header(self.nombre_usuario)

            # Load groups and populate client section
            grupos = self.model.get_grupos()
            grupos_claves = list(grupos.keys())
            self.view.crear_seccion_cliente(grupos_claves)

            # Create product search section
            self.view.crear_seccion_busqueda()

            # Create cart section with cart_model
            self.view.crear_seccion_carrito(
                cart_model=self.cart_model,
                on_change_callback=self._on_cart_updated
            )

            debug_print("✅ UI initialized with CartModel")

        except Exception as e:
            debug_print(f"❌ Error initializing UI: {e}")
            traceback.print_exc()
            raise

    # ==================== CALLBACKS ====================

    def _on_cart_updated(self):
        """Callback when cart is updated"""
        total = self.cart_model.get_total()
        debug_print(f"💰 Total actualizado: ${total:.2f}")

    def on_close(self):
        """
        Handle window close

        Workflow:
        1. Check for unsaved changes
        2. Confirm with user if needed
        3. Close window
        """
        try:
            debug_print("🔄 Cerrando ventana")

            # Check for unsaved changes
            if not self.cart_model.is_empty() and not self.order_ctrl.get_current_folio():
                confirmar = self.view.mostrar_confirmacion(
                    "Cerrar Ventana",
                    "Hay cambios sin guardar.\n\n¿Desea cerrar de todos modos?"
                )

                if not confirmar:
                    return

            # Close window
            self.view.root.destroy()
            debug_print("✅ Ventana cerrada")

        except Exception as e:
            debug_print(f"❌ Error al cerrar: {e}")
            traceback.print_exc()

    # ==================== ACCESS METHODS ====================

    def get_cart_model(self) -> CartModel:
        """Get the shared cart model"""
        return self.cart_model

    def get_client_controller(self) -> ClientSelectionController:
        """Get client selection controller"""
        return self.client_ctrl

    def get_product_controller(self) -> ProductSearchController:
        """Get product search controller"""
        return self.product_ctrl

    def get_order_controller(self) -> OrderController:
        """Get order controller"""
        return self.order_ctrl

    def get_export_controller(self) -> ExportController:
        """Get export controller"""
        return self.export_ctrl

    def get_sales_controller(self) -> SalesController:
        """Get sales controller"""
        return self.sales_ctrl

    def get_settings_controller(self) -> SettingsController:
        """Get settings controller"""
        return self.settings_ctrl

    # ==================== DELEGATION METHODS ====================

    def cargar_orden_existente(self, folio: int):
        """
        Delegate to OrderController to load existing order

        Args:
            folio: Order folio to load
        """
        self.order_ctrl.cargar_orden_existente(folio)

    def on_nueva_orden(self):
        """Delegate to OrderController to create new order"""
        self.order_ctrl.on_nueva_orden()

    # ==================== RUN ====================

    def run(self):
        """Start the application"""
        try:
            debug_print("🚀 Starting application")
            self.view.root.mainloop()
        except Exception as e:
            debug_print(f"❌ Error running application: {e}")
            traceback.print_exc()
            raise
