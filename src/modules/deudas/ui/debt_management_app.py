# -*- coding: utf-8 -*-
"""
Debt Management Application - UI Layer
Main application window coordinating all UI components
Follows MVC pattern - this is the main View/Controller coordinator
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from decimal import Decimal
import unicodedata
from PIL import Image
from io import BytesIO

from src.config import debug_print
from src.theme import COLORS, FONTS

from ..business import DebtService, PaymentService
from ..domain import PaymentMethod, DebtStatus
from ..domain.exceptions import (
    DebtNotFoundError,
    PaymentExceedsSaldoError,
    InvalidPaymentAmountError,
    DebtAlreadyPaidError
)


class DebtManagementApp:
    """
    Main debt management application
    Coordinates UI components and services
    """

    def __init__(
        self,
        root,
        user_data: dict,
        debt_service: DebtService,
        payment_service: PaymentService,
        invoice_access_service=None,
        auth_manager=None
    ):
        """
        Initialize application with injected services

        Args:
            root: Tkinter root window
            user_data: User information dictionary
            debt_service: Debt business service
            payment_service: Payment business service
            invoice_access_service: Optional invoice access service for PDF management
            auth_manager: Optional authentication manager for admin password verification
        """
        self.root = root
        self.user_data = user_data or {"nombre": "admin", "rol": "administrador"}

        # Injected services (NO direct database access!)
        self.debt_service = debt_service
        self.payment_service = payment_service
        self.invoice_access_service = invoice_access_service

        # Auth manager for admin password verification
        if auth_manager is None:
            from src.auth.auth_manager import AuthManager
            auth_manager = AuthManager()
        self.auth_manager = auth_manager

        # State variables
        self.search_var = ctk.StringVar()
        self.search_history_var = ctk.StringVar()
        self.clientes_deudas = []
        self.historial_pagos = []
        self.is_loading = False

        # Statistics variables
        self.stats_vars = {
            'total_clientes': ctk.StringVar(value="0"),
            'total_saldo_pendiente': ctk.StringVar(value="$0.00"),
            'total_deudas_pendientes': ctk.StringVar(value="0")
        }

        # Create interface
        self.create_interface()
        self.load_data()

        # Protocol for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ==================== UTILITY METHODS ====================

    def normalize_text(self, text):
        """Normalize text removing accents and converting to lowercase"""
        if not text:
            return ""
        text = unicodedata.normalize('NFKD', str(text))
        text = ''.join([c for c in text if not unicodedata.combining(c)])
        return text.lower()

    # ==================== UI CREATION ====================

    def create_interface(self):
        """Create the user interface"""
        self.create_header()
        self.create_statistics_section()
        self.create_tabview()
        self.create_status_bar()

    def create_header(self):
        """Create header with back button"""
        header_frame = ctk.CTkFrame(self.root, fg_color=COLORS['secondary'], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=0)

        # Left: Back button + Title
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
            command=self.on_closing
        )
        back_btn.pack(side="left", padx=(0, 15))

        # Title
        title_label = ctk.CTkLabel(
            left_frame,
            text="💰 Gestión de Deudas",
            font=("Arial", 27, "bold"),
            text_color="white"
        )
        title_label.pack(side="left")

        # Right: Refresh button
        right_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        right_frame.pack(side="right", fill="y")

        refresh_btn = ctk.CTkButton(
            right_frame,
            text="🔄 Actualizar",
            width=120,
            height=40,
            command=self.animate_refresh,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover'],
            font=("Arial", 14, "bold")
        )
        refresh_btn.pack(side="right")

    def create_statistics_section(self):
        """Create statistics cards"""
        stats_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=100)
        stats_frame.pack(fill="x", padx=30, pady=(20, 10))
        stats_frame.pack_propagate(False)

        # Statistics cards
        self.create_stat_card(
            stats_frame, "👥", "Clientes con Deuda",
            self.stats_vars['total_clientes'], 0
        )
        self.create_stat_card(
            stats_frame, "📋", "Deudas Pendientes",
            self.stats_vars['total_deudas_pendientes'], 1
        )
        self.create_stat_card(
            stats_frame, "💵", "Saldo Total Pendiente",
            self.stats_vars['total_saldo_pendiente'], 2, is_money=True
        )

    def create_stat_card(self, parent, icon, label, variable, column, is_money=False):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['card_bg'], corner_radius=12)
        card.grid(row=0, column=column, sticky="ew", padx=10)
        parent.grid_columnconfigure(column, weight=1)

        card_content = ctk.CTkFrame(card, fg_color="transparent")
        card_content.pack(fill="both", expand=True, padx=20, pady=15)

        # Icon and label
        header_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        header_frame.pack(fill="x")

        ctk.CTkLabel(
            header_frame, text=icon,
            font=("Arial", 27), text_color=COLORS['primary']
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            header_frame, text=label,
            font=("Arial", 14), text_color=COLORS['text_secondary']
        ).pack(side="left")

        # Value
        ctk.CTkLabel(
            card_content, textvariable=variable,
            font=("Arial", 23, "bold"), text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(5, 0))

    def create_tabview(self):
        """Create tab view for debts and history"""
        self.tabview = ctk.CTkTabview(self.root, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        # Add tabs
        self.tabview.add("📋 Deudas Pendientes")
        self.tabview.add("📊 Historial de Pagos")

        # Create tab contents
        self.create_pending_debts_tab()
        self.create_payment_history_tab()

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ctk.CTkFrame(self.root, fg_color=COLORS['surface'], height=30)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Listo",
            font=("Arial", 12),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(side="left", padx=10)

    # ==================== PENDING DEBTS TAB ====================

    def create_pending_debts_tab(self):
        """Create pending debts tab content"""
        tab = self.tabview.tab("📋 Deudas Pendientes")

        # Search frame
        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.pack(fill="x", pady=(10, 15))

        ctk.CTkLabel(
            search_frame, text="🔍 Buscar:",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=(0, 10))

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Buscar por nombre de cliente...",
            width=400,
            height=35,
            font=("Arial", 14)
        )
        search_entry.pack(side="left", padx=(0, 10))
        self.search_var.trace("w", lambda *args: self.filter_debts())


        # Table frame
        table_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color=COLORS['surface'],
            corner_radius=10
        )
        table_frame.pack(fill="both", expand=True)

        self.debts_table_frame = table_frame

        # Create table header
        columns = [
            ("Cliente", 200),
            ("Grupo", 120),
            ("Deudas", 80),
            ("Total Adeudado", 120),
            ("Saldo Pendiente", 130),
            ("Acciones", 200)
        ]
        self.create_table_header(table_frame, columns)

    def create_table_header(self, parent, columns):
        """Create table header row"""
        header_frame = ctk.CTkFrame(parent, fg_color=COLORS['primary'], height=40)
        header_frame.pack(fill="x", padx=2, pady=2)
        header_frame.pack_propagate(False)

        for col_name, col_width in columns:
            label = ctk.CTkLabel(
                header_frame,
                text=col_name,
                font=("Arial", 14, "bold"),
                text_color="white",
                width=col_width
            )
            label.pack(side="left", padx=5)

    def update_debts_table(self):
        """Update debts table with current data"""
        # Clear existing rows
        for widget in self.debts_table_frame.winfo_children()[1:]:
            widget.destroy()

        # Filter and display
        search_text = self.normalize_text(self.search_var.get())

        filtered_clients = [
            c for c in self.clientes_deudas
            if search_text in self.normalize_text(c.nombre_cliente)
        ] if search_text else self.clientes_deudas

        for idx, cliente in enumerate(filtered_clients):
            self.create_debt_row(cliente, idx)

    def create_debt_row(self, cliente, idx):
        """Create a debt row"""
        row_color = COLORS['card_bg'] if idx % 2 == 0 else COLORS['surface']

        row_frame = ctk.CTkFrame(
            self.debts_table_frame,
            fg_color=row_color,
            height=60
        )
        row_frame.pack(fill="x", padx=2, pady=1)
        row_frame.pack_propagate(False)

        # Cliente
        ctk.CTkLabel(
            row_frame, text=cliente.nombre_cliente,
            font=("Arial", 14), width=200, anchor="w"
        ).pack(side="left", padx=5)

        # Grupo
        ctk.CTkLabel(
            row_frame, text=cliente.nombre_grupo,
            font=("Arial", 14), width=120, anchor="w"
        ).pack(side="left", padx=5)

        # Deudas count
        ctk.CTkLabel(
            row_frame, text=str(cliente.deudas_pendientes),
            font=("Arial", 14), width=80, anchor="center"
        ).pack(side="left", padx=5)

        # Total adeudado
        ctk.CTkLabel(
            row_frame, text=f"${cliente.total_deudas:,.2f}",
            font=("Arial", 14), width=120, anchor="e"
        ).pack(side="left", padx=5)

        # Saldo pendiente
        ctk.CTkLabel(
            row_frame, text=f"${cliente.saldo_pendiente:,.2f}",
            font=("Arial", 14, "bold"), width=130, anchor="e",
            text_color=COLORS['accent']
        ).pack(side="left", padx=5)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=200)
        actions_frame.pack(side="left", padx=5)

        ctk.CTkButton(
            actions_frame, text="Ver Detalles",
            width=90, height=30,
            command=lambda: self.view_client_debts(cliente.id_cliente),
            fg_color=COLORS['primary'],
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions_frame, text="Pago Rápido",
            width=90, height=30,
            command=lambda: self.quick_payment(cliente.id_cliente),
            fg_color=COLORS['success'],
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=2)

    # ==================== PAYMENT HISTORY TAB ====================

    def create_payment_history_tab(self):
        """Create payment history tab content"""
        tab = self.tabview.tab("📊 Historial de Pagos")

        # Search and actions frame
        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.pack(fill="x", pady=(10, 15))

        # Left: Search
        ctk.CTkLabel(
            top_frame, text="🔍 Buscar:",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=(0, 10))

        search_entry = ctk.CTkEntry(
            top_frame,
            textvariable=self.search_history_var,
            placeholder_text="Buscar en historial...",
            width=400,
            height=35,
            font=("Arial", 14)
        )
        search_entry.pack(side="left", padx=(0, 10))
        self.search_history_var.trace("w", lambda *args: self.filter_payment_history())

        # Right: Invoice search button
        if self.invoice_access_service:
            ctk.CTkButton(
                top_frame,
                text="🔍 Búsqueda de Folios",
                command=self.open_invoice_search,
                fg_color=COLORS['primary'],
                height=35,
                font=("Arial", 14, "bold")
            ).pack(side="right")

        # Table frame
        table_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color=COLORS['surface'],
            corner_radius=10
        )
        table_frame.pack(fill="both", expand=True)

        self.history_table_frame = table_frame

        # Create table header
        columns = [
            ("Cliente", 180),
            ("Grupo", 100),
            ("Folio", 80),
            ("Total", 100),
            ("Pagado", 100),
            ("Fecha Pago", 110),
            ("Método", 100),
            ("Acciones", 180)
        ]
        self.create_table_header(table_frame, columns)

    def update_history_table(self):
        """Update payment history table"""
        # Clear existing rows
        for widget in self.history_table_frame.winfo_children()[1:]:
            widget.destroy()

        # Filter and display
        search_text = self.normalize_text(self.search_history_var.get())

        filtered_history = [
            p for p in self.historial_pagos
            if search_text in self.normalize_text(p.get('nombre_cliente', ''))
        ] if search_text else self.historial_pagos

        for idx, pago in enumerate(filtered_history):
            self.create_history_row(pago, idx)

    def create_history_row(self, pago, idx):
        """Create a payment history row"""
        row_color = COLORS['card_bg'] if idx % 2 == 0 else COLORS['surface']

        row_frame = ctk.CTkFrame(
            self.history_table_frame,
            fg_color=row_color,
            height=50
        )
        row_frame.pack(fill="x", padx=2, pady=1)
        row_frame.pack_propagate(False)

        # Cliente
        ctk.CTkLabel(
            row_frame, text=pago.get('nombre_cliente', ''),
            font=("Arial", 14), width=180, anchor="w"
        ).pack(side="left", padx=5)

        # Grupo
        ctk.CTkLabel(
            row_frame, text=pago.get('clave_grupo', ''),
            font=("Arial", 14), width=100, anchor="w"
        ).pack(side="left", padx=5)

        # Factura - Use folio_numero if available, otherwise id_factura
        folio_display = pago.get('folio_numero') or pago.get('id_factura', '')
        ctk.CTkLabel(
            row_frame, text=f"#{folio_display}",
            font=("Arial", 14), width=80, anchor="center"
        ).pack(side="left", padx=5)

        # Total
        monto_total = pago.get('monto_total', 0)
        ctk.CTkLabel(
            row_frame, text=f"${monto_total:,.2f}",
            font=("Arial", 14), width=100, anchor="e"
        ).pack(side="left", padx=5)

        # Pagado
        monto_pagado = pago.get('monto_pagado', 0)
        ctk.CTkLabel(
            row_frame, text=f"${monto_pagado:,.2f}",
            font=("Arial", 14, "bold"), width=100, anchor="e",
            text_color=COLORS['success']
        ).pack(side="left", padx=5)

        # Fecha pago (only show date, not time)
        fecha_pago = pago.get('fecha_pago', '')
        fecha_display = ''
        if fecha_pago:
            try:
                # If it's a datetime object, get just the date
                if hasattr(fecha_pago, 'date'):
                    fecha_display = str(fecha_pago.date())
                else:
                    # If it's already a string, try to parse and format
                    fecha_str = str(fecha_pago)
                    if ' ' in fecha_str:
                        fecha_display = fecha_str.split(' ')[0]
                    else:
                        fecha_display = fecha_str
            except:
                fecha_display = str(fecha_pago)

        ctk.CTkLabel(
            row_frame, text=fecha_display,
            font=("Arial", 14), width=110, anchor="center"
        ).pack(side="left", padx=5)

        # Método (convert PaymentMethod enum to display text)
        metodo = pago.get('metodo_pago', '')
        metodo_display = ''
        if metodo:
            try:
                # If it's a PaymentMethod enum, get its value
                if hasattr(metodo, 'value'):
                    metodo_display = metodo.value.capitalize()
                else:
                    # If it's a string, use it directly
                    metodo_str = str(metodo).lower()
                    # Remove "paymentmethod." prefix if present
                    if 'paymentmethod.' in metodo_str:
                        metodo_str = metodo_str.split('.')[-1]
                    metodo_display = metodo_str.capitalize()
            except:
                metodo_display = str(metodo).capitalize()

        ctk.CTkLabel(
            row_frame, text=metodo_display,
            font=("Arial", 14), width=100, anchor="center"
        ).pack(side="left", padx=5)

        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=180)
        actions_frame.pack(side="left", padx=5)

        ctk.CTkButton(
            actions_frame, text="Ver",
            width=80, height=30,
            command=lambda: self.view_payment_details(pago.get('id_deuda')),
            fg_color=COLORS['primary'],
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions_frame, text="Deshacer",
            width=80, height=30,
            command=lambda p=pago.get('id_pago'): self.undo_payment(p),
            fg_color=COLORS['danger'],
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=2)

    # ==================== ACTIONS ====================

    def view_client_debts(self, id_cliente):
        """View all debts for a client"""
        try:
            debts = self.debt_service.get_client_debts(id_cliente)

            # Filter out fully paid debts (status == PAID)
            pending_debts = [d for d in debts if not d.pagado]

            if not pending_debts:
                messagebox.showinfo(
                    "Sin Deudas",
                    "Este cliente no tiene deudas pendientes"
                )
                return

            # Create details window
            self.show_client_debts_window(pending_debts)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar deudas:\n{str(e)}")

    def show_client_debts_window(self, debts):
        """Show window with client's debts"""
        window = ctk.CTkToplevel(self.root)
        window.title(f"Deudas - {debts[0].nombre_cliente}")
        window.geometry("900x600")
        window.transient(self.root)
        window.grab_set()

        # Header
        header = ctk.CTkFrame(window, fg_color=COLORS['primary'], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text=f"Deudas de {debts[0].nombre_cliente}",
            font=("Arial", 23, "bold"),
            text_color="white"
        ).pack(pady=15)

        # Debts list
        list_frame = ctk.CTkScrollableFrame(window, fg_color=COLORS['surface'])
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)

        for debt in debts:
            self.create_debt_detail_card(list_frame, debt)

        # Close button
        ctk.CTkButton(
            window, text="Cerrar",
            command=window.destroy,
            fg_color="gray",
            width=100,
            font=("Arial", 14, "bold")
        ).pack(pady=10)

    def create_debt_detail_card(self, parent, debt):
        """Create a card showing debt details"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['card_bg'], corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=15)

        # Debt info - Use folio_numero if available, otherwise id_factura
        folio_display = debt.folio_numero if debt.folio_numero else debt.id_factura
        info_text = f"""
Folio #{folio_display} | {debt.fecha_generada}
Total: ${debt.monto_total:,.2f} | Pagado: ${debt.monto_pagado:,.2f} | Pendiente: ${debt.saldo_pendiente:,.2f}
Estado: {debt.status.display_name}
        """.strip()

        ctk.CTkLabel(
            content, text=info_text,
            font=("Arial", 14), justify="left"
        ).pack(side="left", fill="x", expand=True)

        # Pay button
        if not debt.pagado:
            ctk.CTkButton(
                content, text="Registrar Pago",
                width=120,
                command=lambda: self.open_payment_window(debt.id_deuda, debt),
                fg_color=COLORS['success'],
                font=("Arial", 14, "bold")
            ).pack(side="right")

    def quick_payment(self, id_cliente):
        """Quick payment for first pending debt"""
        try:
            debts = self.debt_service.get_client_debts(id_cliente)
            pending_debts = [d for d in debts if not d.pagado]

            if not pending_debts:
                messagebox.showinfo(
                    "Sin Deudas",
                    "Este cliente no tiene deudas pendientes"
                )
                return

            # Open payment window for first pending debt
            self.open_payment_window(pending_debts[0].id_deuda, pending_debts[0])

        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")

    def open_payment_window(self, id_deuda, deuda=None):
        """Open payment registration window"""
        # Import here to avoid circular dependency
        from .controllers.payment_controller import PaymentController

        try:
            # Get debt if not provided
            if deuda is None:
                deuda = self.debt_service.get_debt_by_id(id_deuda)

            # Create payment controller
            controller = PaymentController(
                parent=self.root,
                debt=deuda,
                payment_service=self.payment_service,
                on_success=self.on_payment_registered,
                user_data=self.user_data
            )
            controller.show()

        except DebtNotFoundError:
            messagebox.showerror("Error", "Deuda no encontrada")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de pago:\n{str(e)}")


    def open_invoice_search(self):
        """Open invoice search window"""
        from .controllers.invoice_search_controller import InvoiceSearchController

        try:
            controller = InvoiceSearchController(
                parent=self.root,
                debt_service=self.debt_service,
                invoice_access_service=self.invoice_access_service,
                user_data=self.user_data
            )
            controller.show()

        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo búsqueda:\n{str(e)}")

    def view_payment_details(self, id_deuda):
        """View payment details"""
        try:
            debt = self.debt_service.get_debt_by_id(id_deuda)
            # Retrieve payment history for this specific debt
            # Since get_payment_history filters by date/client, we might need a direct by_debt method 
            # OR we can filter the result. 
            # Or better, let's reuse get_payment_history but we need debt-specific filter.
            # Currently get_payment_history accepts id_cliente, start/end date.
            # We will use id_cliente to reduce scope and then filter in python for now, 
            # or add get_payments_by_debt in service.
            # BUT the user asked to FIX data visibility. 
            # Since I cannot easily add a new method to repo interface without touching interface definition (which I can't see but assume exists),
            # I will fetch history for client and filter.
            # Wait, I updated MySQLPaymentRepository.get_payment_history to select from pembayaran_registrado.
            # It returns ALL payments for a client. 
            
            # Let's trust that fetching all payments for the client isn't too heavy for now (paginated/limited usually)
            # Or better, fetch payments for this client and filter by id_deuda
            
            payments = self.payment_service.get_payment_history(id_cliente=debt.id_cliente)
            debt_payments = [p for p in payments if p.get('id_deuda') == id_deuda]
            
            self.show_payment_details_window(debt, debt_payments)

        except DebtNotFoundError:
            messagebox.showerror("Error", "Deuda no encontrada")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error:\n{str(e)}")

    def show_payment_details_window(self, debt, payments):
        """Show payment details window"""
        # Use folio_numero if available, otherwise id_factura
        folio_display = debt.folio_numero if debt.folio_numero else debt.id_factura
        
        window = ctk.CTkToplevel(self.root)
        window.title(f"Detalles de Pago - Folio #{folio_display}")
        window.geometry("700x800")
        window.transient(self.root)
        window.grab_set()

        # Header
        header = ctk.CTkFrame(window, fg_color=COLORS['primary'], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text=f"Folio #{folio_display}",
            font=("Arial", 23, "bold"),
            text_color="white"
        ).pack(pady=5)
        
        ctk.CTkLabel(
            header,
            text=f"{debt.nombre_cliente} - {debt.nombre_grupo}",
            font=("Arial", 14),
            text_color="white"
        ).pack(pady=0)

        # Content
        content_frame = ctk.CTkScrollableFrame(window, fg_color=COLORS['surface'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Debt Statistics Summary
        summary_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['card_bg'])
        summary_frame.pack(fill="x", pady=(0, 20))
        
        info_text = f"""
Monto Total: ${debt.monto_total:,.2f}
Monto Pagado: ${debt.monto_pagado:,.2f}
Saldo Pendiente: ${debt.saldo_pendiente:,.2f}
Estado Actual: {debt.status.display_name}
        """.strip()

        ctk.CTkLabel(
            summary_frame,
            text=info_text,
            font=("Arial", 16, "bold"),
            justify="left"
        ).pack(padx=20, pady=15, anchor="w")

        ctk.CTkLabel(
            content_frame,
            text=f"Historial de Pagos ({len(payments)})",
            font=("Arial", 18, "bold"),
            text_color=COLORS['primary']
        ).pack(anchor="w", pady=(0, 10))

        if not payments:
            ctk.CTkLabel(
                content_frame,
                text="No hay pagos registrados para esta deuda",
                font=("Arial", 14, "italic"),
                text_color="gray"
            ).pack(pady=20)
        
        # Sort payments by date desc (if not already)
        # payments.sort(key=lambda x: x.get('fecha_pago', ''), reverse=True)

        for payment in payments:
            self.create_single_payment_card(content_frame, payment)
            
        # Close button
        ctk.CTkButton(
            window, text="Cerrar",
            command=window.destroy,
            width=100,
            font=("Arial", 14, "bold")
        ).pack(pady=10)

    def create_single_payment_card(self, parent, payment):
        """Create a card for a single payment event"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['card_bg'], corner_radius=10)
        card.pack(fill="x", pady=10, padx=5)
        
        # Header: Date and Amount
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        fecha = payment.get('fecha_pago', 'N/A')
        monto = payment.get('monto_pagado', 0) # Mapped in repository query
        
        ctk.CTkLabel(
            header_frame,
            text=f"📅 {fecha}",
            font=("Arial", 14, "bold")
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_frame,
            text=f"💲 {monto:,.2f}",
            font=("Arial", 16, "bold"),
            text_color=COLORS['success']
        ).pack(side="right")
        
        # Details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.pack(fill="x", padx=15, pady=5)
        
        metodo = payment.get('metodo_pago', 'N/A')
        ref = payment.get('referencia_pago') or "Sin referencia"
        desc = payment.get('descripcion') or payment.get('notas') or "Sin notas"
        
        details_text = f"Método: {metodo}\nRef: {ref}\nNotas: {desc}"
        
        ctk.CTkLabel(
            details_frame,
            text=details_text,
            font=("Arial", 13),
            justify="left",
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        # Image
        img_bytes = payment.get('imagen_comprobante')
        if img_bytes:
            try:
                # Add separator
                ctk.CTkFrame(card, height=2, fg_color="gray").pack(fill="x", padx=15, pady=10)
                
                image = Image.open(BytesIO(img_bytes))
                # Resize for display
                image.thumbnail((400, 400))
                
                ctk_image = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=image.size
                )
                
                ctk.CTkLabel(
                    card,
                    image=ctk_image,
                    text=""
                ).pack(pady=(0, 15))
                
            except Exception as e:
                ctk.CTkLabel(
                    card,
                    text=f"Error cargando imagen: {e}",
                    text_color="red",
                    font=("Arial", 11)
                ).pack(pady=10)

    # ==================== DATA LOADING ====================

    def load_data(self):
        """Load all data"""
        self.load_statistics()
        self.load_clients_with_debts()
        self.load_payment_history()

    def load_statistics(self):
        """Load statistics"""
        try:
            stats = self.debt_service.get_debt_statistics()

            self.stats_vars['total_clientes'].set(str(stats.total_clientes_con_deudas))
            self.stats_vars['total_deudas_pendientes'].set(str(stats.total_deudas_pendientes))
            self.stats_vars['total_saldo_pendiente'].set(f"${stats.saldo_total_pendiente:,.2f}")

        except Exception as e:
            debug_print(f"Error loading statistics: {e}")

    def load_clients_with_debts(self):
        """Load clients with debts"""
        try:
            self.clientes_deudas = self.debt_service.get_clients_with_debts()
            self.update_debts_table()

        except Exception as e:
            debug_print(f"Error loading clients: {e}")
            messagebox.showerror("Error", f"Error al cargar clientes:\n{str(e)}")

    def load_payment_history(self):
        """Load payment history"""
        try:
            self.historial_pagos = self.payment_service.get_payment_history()
            self.update_history_table()

        except Exception as e:
            debug_print(f"Error loading history: {e}")

    # ==================== FILTERING ====================

    def filter_debts(self):
        """Filter debts table"""
        self.update_debts_table()

    def filter_payment_history(self):
        """Filter payment history"""
        self.update_history_table()

    # ==================== REFRESH ====================

    def animate_refresh(self):
        """Animate refresh"""
        self.load_data()
        self.status_label.configure(text="✓ Datos actualizados")
        self.root.after(2000, lambda: self.status_label.configure(text="Listo"))

    # ==================== CALLBACKS ====================

    def on_payment_registered(self):
        """Callback after payment is registered"""
        self.load_data()
        messagebox.showinfo("Éxito", "Pago registrado exitosamente")

    # ==================== UNDO PAYMENT ====================

    def _verify_admin_password(self, action: str) -> bool:
        """
        Show modal dialog to verify admin password

        Args:
            action: Description of action requiring verification

        Returns:
            True if password verified, False otherwise
        """
        popup = ctk.CTkToplevel(self.root)
        popup.title("Verificación de Administrador")
        popup.geometry("450x250")
        popup.transient(self.root)
        popup.grab_set()
        popup.focus_set()

        result = [False]

        # Header with danger color
        header = ctk.CTkFrame(popup, fg_color=COLORS['danger'], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🔐 VERIFICACIÓN DE ADMINISTRADOR",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(pady=15)

        # Content
        content = ctk.CTkFrame(popup, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(
            content,
            text=f"Se requiere contraseña de administrador para:\n{action}",
            font=("Arial", 14),
            wraplength=380
        ).pack(pady=(0, 15))

        # Password entry with masking
        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            content,
            textvariable=password_var,
            placeholder_text="Contraseña de administrador",
            show="●",
            height=35,
            font=("Arial", 14)
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
                password_entry.focus_set()

        password_entry.bind("<Return>", lambda e: verify())

        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="✅ Verificar",
            command=verify,
            fg_color=COLORS['success'],
            height=40,
            font=("Arial", 14, "bold")
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=popup.destroy,
            fg_color="gray",
            height=40,
            font=("Arial", 14, "bold")
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

        popup.wait_window()
        return result[0]

    def undo_payment(self, id_pago: int):
        """
        Handle undo payment with admin verification

        Args:
            id_pago: Payment record ID to undo
        """
        from ..domain.exceptions import PaymentNotFoundError

        # 1. Show confirmation dialog
        if not messagebox.askyesno(
            "⚠️ Confirmar Deshacer Pago",
            "¿Está seguro que desea deshacer este pago?\n\n"
            "Esto eliminará:\n"
            "• El registro de pago\n"
            "• La imagen del comprobante\n"
            "• El pago será devuelto a deudas pendientes\n\n"
            "Esta acción NO SE PUEDE DESHACER."
        ):
            return

        # 2. Verify admin password
        if not self._verify_admin_password("Deshacer Pago"):
            messagebox.showwarning("Cancelado", "Operación cancelada")
            return

        # 3. Execute undo via service
        try:
            success = self.payment_service.undo_payment(
                id_pago=id_pago,
                usuario=self.user_data.get('username', 'admin')
            )

            if success:
                messagebox.showinfo("Éxito", "Pago deshecho exitosamente")
                self.load_data()  # Refresh all data

        except PaymentNotFoundError:
            messagebox.showerror("Error", "Pago no encontrado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al deshacer pago:\n{str(e)}")

    def on_closing(self):
        """Handle window closing"""
        self.root.destroy()