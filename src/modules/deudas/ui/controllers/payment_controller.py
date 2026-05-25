# -*- coding: utf-8 -*-
"""
Payment Controller - UI Layer
Handles payment registration logic
Separates UI from business logic (MVC pattern)
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from decimal import Decimal, InvalidOperation
from datetime import date
from pathlib import Path
from PIL import Image

from src.config import debug_print
from src.theme import COLORS, FONTS

from ...business import PaymentService
from ...domain import Debt, PaymentMethod
from ...domain.exceptions import (
    PaymentExceedsSaldoError,
    InvalidPaymentAmountError,
    DebtAlreadyPaidError
)


class PaymentController:
    """
    Controller for payment registration
    Coordinates between payment form view and payment service
    """

    def __init__(
        self,
        parent,
        debt: Debt,
        payment_service: PaymentService,
        on_success: callable,
        user_data: dict = None
    ):
        """
        Initialize payment controller

        Args:
            parent: Parent window
            debt: Debt entity to register payment for
            payment_service: Payment business service
            on_success: Callback function to call after successful payment
            user_data: User information dictionary
        """
        self.parent = parent
        self.debt = debt
        self.payment_service = payment_service
        self.on_success_callback = on_success
        self.user_data = user_data or {"nombre": "sistema"}

        # State
        self.selected_image_path = None
        self.window = None

    def show(self):
        """Show payment registration window"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(f"Registrar Pago - {self.debt.nombre_cliente}")
        self.window.geometry("650x750")
        self.window.transient(self.parent)
        self.window.grab_set()

        self.create_ui()

    def create_ui(self):
        """Create payment form UI"""
        # Header
        self.create_header()

        # Content
        content = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent"
        )
        content.pack(fill="both", expand=True, padx=30, pady=20)

        # Debt info card
        self.create_debt_info_card(content)

        # Payment form
        self.create_payment_form(content)

        # Buttons
        self.create_buttons(content)

    def create_header(self):
        """Create header"""
        header = ctk.CTkFrame(self.window, fg_color=COLORS['primary'], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text=f"💵 Registrar Pago",
            font=("Arial", 23, "bold"),
            text_color="white"
        ).pack(pady=20)

    def create_debt_info_card(self, parent):
        """Create debt information card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['card_bg'], corner_radius=10)
        card.pack(fill="x", pady=(0, 20))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", padx=20, pady=15)

        ctk.CTkLabel(
            content,
            text="Información de la Deuda",
            font=("Arial", 15, "bold"),
            text_color=COLORS['primary']
        ).pack(anchor="w", pady=(0, 10))

        info_text = f"""
Cliente: {self.debt.nombre_cliente}
Grupo: {self.debt.nombre_grupo}
Folio: #{self.debt.id_factura}

Monto Total: ${self.debt.monto_total:,.2f}
Pagado Actualmente: ${self.debt.monto_pagado:,.2f}
Saldo Pendiente: ${self.debt.saldo_pendiente:,.2f}
        """.strip()

        ctk.CTkLabel(
            content,
            text=info_text,
            font=("Arial", 14),
            justify="left"
        ).pack(anchor="w")

    def create_payment_form(self, parent):
        """Create payment form"""
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)

        # Amount
        ctk.CTkLabel(
            form_frame,
            text="Monto del Pago: *",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(10, 5))

        self.amount_var = ctk.StringVar(value=str(self.debt.saldo_pendiente))
        self.amount_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.amount_var,
            placeholder_text="0.00",
            height=40,
            font=("Arial", 14)
        )
        self.amount_entry.pack(fill="x", pady=(0, 5))
        self.amount_entry.focus_set()

        # Payment method
        ctk.CTkLabel(
            form_frame,
            text="Método de Pago: *",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(15, 5))

        self.method_var = ctk.StringVar(value=PaymentMethod.CASH.value)
        methods = [
            ("💵 Efectivo", PaymentMethod.CASH.value),
            ("🏦 Transferencia", PaymentMethod.TRANSFER.value),
            ("💳 Tarjeta", PaymentMethod.CARD.value),
            ("📝 Cheque", PaymentMethod.CHECK.value)
        ]

        for label, value in methods:
            ctk.CTkRadioButton(
                form_frame,
                text=label,
                variable=self.method_var,
                value=value,
                font=("Arial", 14)
            ).pack(anchor="w", pady=2)

        # Reference
        ctk.CTkLabel(
            form_frame,
            text="Referencia (Opcional):",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(15, 5))

        self.reference_var = ctk.StringVar()
        self.reference_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.reference_var,
            placeholder_text="Número de transacción, cheque, etc.",
            height=35,
            font=("Arial", 14)
        )
        self.reference_entry.pack(fill="x")

        # Image
        ctk.CTkLabel(
            form_frame,
            text="Comprobante de Pago (Opcional):",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(15, 5))

        self.image_frame = ctk.CTkFrame(form_frame, fg_color=COLORS['surface'], height=120)
        self.image_frame.pack(fill="x")
        self.image_frame.pack_propagate(False)

        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="📎 Sin comprobante",
            font=("Arial", 14),
            text_color=COLORS['text_secondary']
        )
        self.image_label.pack(expand=True)

        ctk.CTkButton(
            form_frame,
            text="📁 Seleccionar Imagen",
            command=self.select_image,
            fg_color=COLORS['primary'],
            height=35,
            font=("Arial", 14, "bold")
        ).pack(fill="x", pady=(5, 0))

    def create_buttons(self, parent):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            button_frame,
            text="💾 Registrar Pago",
            command=self.process_payment,
            fg_color=COLORS['success'],
            hover_color="#28a745",
            height=45,
            font=("Arial", 14, "bold")
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            button_frame,
            text="❌ Cancelar",
            command=self.window.destroy,
            fg_color="gray",
            height=45,
            font=("Arial", 14, "bold")
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

    def select_image(self):
        """Select payment receipt image"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Comprobante",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )

        if file_path:
            self.selected_image_path = file_path
            filename = Path(file_path).name

            # Update label
            self.image_label.configure(
                text=f"✓ {filename}",
                text_color=COLORS['success']
            )

            # Try to show preview
            try:
                image = Image.open(file_path)
                image.thumbnail((100, 100))

                ctk_image = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=image.size
                )

                self.image_label.configure(image=ctk_image, text="")

            except Exception as e:
                debug_print(f"Error loading image preview: {e}")

    def process_payment(self):
        """Process payment registration"""
        try:
            # Validate amount
            amount_str = self.amount_var.get().strip()
            if not amount_str:
                messagebox.showerror(
                    "Error de Validación",
                    "Por favor ingrese el monto del pago",
                    parent=self.window
                )
                return

            try:
                amount = Decimal(amount_str)
            except InvalidOperation:
                messagebox.showerror(
                    "Error de Validación",
                    "Monto inválido. Ingrese un número válido.",
                    parent=self.window
                )
                return

            # Parse payment method
            try:
                method = PaymentMethod.from_string(self.method_var.get())
            except ValueError as e:
                messagebox.showerror(
                    "Error de Validación",
                    str(e),
                    parent=self.window
                )
                return

            # Get reference
            reference = self.reference_var.get().strip() or None

            # Load image bytes if selected
            image_bytes = None
            image_name = None

            if self.selected_image_path:
                try:
                    with open(self.selected_image_path, 'rb') as f:
                        image_bytes = f.read()
                    image_name = Path(self.selected_image_path).name

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error al leer imagen:\n{str(e)}",
                        parent=self.window
                    )
                    return

            # Get username from user_data
            username = self.user_data.get('nombre', 'sistema')

            # Register payment via service
            success = self.payment_service.register_payment(
                id_deuda=self.debt.id_deuda,
                monto=amount,
                metodo=method,
                referencia=reference,
                imagen_bytes=image_bytes,
                nombre_imagen=image_name,
                fecha=date.today(),
                usuario=username
            )

            if success:
                self.window.destroy()
                if self.on_success_callback:
                    self.on_success_callback()

        except InvalidPaymentAmountError as e:
            messagebox.showerror(
                "Monto Inválido",
                str(e),
                parent=self.window
            )

        except PaymentExceedsSaldoError as e:
            messagebox.showerror(
                "Monto Excede Saldo",
                str(e),
                parent=self.window
            )

        except DebtAlreadyPaidError as e:
            messagebox.showerror(
                "Deuda Pagada",
                str(e),
                parent=self.window
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al registrar pago:\n{str(e)}",
                parent=self.window
            )
            debug_print(f"Payment error: {e}")
