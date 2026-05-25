# -*- coding: utf-8 -*-
"""
Confirm Sale Dialog - Two-Step Verification
Custom CTkToplevel dialog for sale confirmation with warning step
"""
import customtkinter as ctk
from typing import Optional
from src.theme import COLORS, FONTS


class ConfirmSaleDialog(ctk.CTkToplevel):
    """
    Two-step confirmation dialog for processing sales

    Step 1: Warning about processing the sale
    Step 2: Final confirmation with sale details
    """

    def __init__(
        self,
        parent,
        total: float,
        items_count: int,
        client_name: str
    ):
        """
        Initialize the confirmation dialog

        Args:
            parent: Parent window
            total: Total sale amount
            items_count: Number of items in cart
            client_name: Name of the client
        """
        super().__init__(parent)

        self.title("Confirmar Venta")
        self.geometry("600x700")
        self.resizable(False, False)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"600x700+{x}+{y}")

        # Store data
        self.total = total
        self.items_count = items_count
        self.client_name = client_name

        # Result
        self.result = False
        self.current_step = 1

        # Build UI
        self._build_ui()

        # Modal behavior
        self.grab_set()
        self.focus()

        # Bind escape key to cancel
        self.bind("<Escape>", lambda e: self._cancel())

    def _build_ui(self):
        """Build the dialog UI"""
        # Main container
        main = ctk.CTkFrame(self, fg_color=("gray95", "#1a1a1a"))
        main.pack(fill="both", expand=True)

        # Header
        self._create_header(main)

        # Content area (will change between steps)
        self.content_frame = ctk.CTkFrame(main, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Footer with buttons
        self._create_footer(main)

        # Show step 1
        self._show_step_1()

    def _create_header(self, parent):
        """Create dialog header"""
        header = ctk.CTkFrame(
            parent,
            fg_color=("gray85", "#0f0f0f"),
            height=70
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        # Warning icon and title
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=15)

        # Icon
        self.header_icon = ctk.CTkLabel(
            header_content,
            text="⚠️",
            font=("Arial", 32)
        )
        self.header_icon.pack(side="left", padx=(0, 15))

        # Title and subtitle
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)

        self.header_title = ctk.CTkLabel(
            title_frame,
            text="Confirmar Procesamiento de Venta",
            font=FONTS['subtitle'],
            text_color=COLORS['warning'],
            anchor="w"
        )
        self.header_title.pack(anchor="w")

        self.header_subtitle = ctk.CTkLabel(
            title_frame,
            text="Paso 1 de 2",
            font=FONTS['body'],
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        self.header_subtitle.pack(anchor="w", pady=(2, 0))

    def _create_footer(self, parent):
        """Create footer with action buttons"""
        footer = ctk.CTkFrame(
            parent,
            fg_color=("gray90", "#0f0f0f"),
            height=80
        )
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        btn_container = ctk.CTkFrame(footer, fg_color="transparent")
        btn_container.pack(fill="both", expand=True, padx=30, pady=15)

        # Cancel button (left)
        self.btn_cancel = ctk.CTkButton(
            btn_container,
            text="✕ Cancelar",
            command=self._cancel,
            fg_color=("gray70", "#333"),
            hover_color=("gray60", "#444"),
            text_color=("gray20", "#fff"),
            font=FONTS['body_bold'],
            height=45,
            width=150,
            corner_radius=8
        )
        self.btn_cancel.pack(side="left")

        # Next/Confirm button (right)
        self.btn_action = ctk.CTkButton(
            btn_container,
            text="Continuar →",
            command=self._next_step,
            fg_color=COLORS['warning'],
            hover_color=COLORS['warning_hover'],
            text_color="#fff",
            font=FONTS['body_bold'],
            height=45,
            width=150,
            corner_radius=8
        )
        self.btn_action.pack(side="right")

    def _show_step_1(self):
        """Show step 1: Warning"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Update header
        self.header_icon.configure(text="⚠️")
        self.header_title.configure(
            text="Confirmar Procesamiento de Venta",
            text_color=COLORS['warning']
        )
        self.header_subtitle.configure(text="Paso 1 de 2")

        # Warning message
        warning_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("white", "gray22"),
            corner_radius=12,
            border_width=2,
            border_color=COLORS['warning']
        )
        warning_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Warning icon and text
        ctk.CTkLabel(
            warning_frame,
            text="⚠️",
            font=("Arial", 48)
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            warning_frame,
            text="¡ATENCIÓN!",
            font=FONTS['title'],
            text_color=COLORS['warning']
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            warning_frame,
            text="Está a punto de procesar una venta",
            font=FONTS['subheader'],
            text_color=("gray20", "gray80")
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            warning_frame,
            text="Esta acción registrará la venta en el sistema",
            font=FONTS['body'],
            text_color=("gray40", "gray60")
        ).pack(pady=(0, 30))

        # Important notes
        notes_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray90", "gray17"),
            corner_radius=8
        )
        notes_frame.pack(fill="x")

        ctk.CTkLabel(
            notes_frame,
            text="📋 Antes de continuar, verifique:",
            font=FONTS['body_bold'],
            text_color=("gray20", "gray80"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(12, 8))

        checklist = [
            "✓ El cliente seleccionado es correcto",
            "✓ Los productos y cantidades son correctos",
            "✓ El monto total es el esperado"
        ]

        for item in checklist:
            ctk.CTkLabel(
                notes_frame,
                text=item,
                font=FONTS['body'],
                text_color=("gray30", "gray70"),
                anchor="w"
            ).pack(anchor="w", padx=25, pady=2)

        ctk.CTkLabel(
            notes_frame,
            text="",
            font=FONTS['body']
        ).pack(pady=5)

        # Update button
        self.btn_action.configure(
            text="Continuar →",
            fg_color=COLORS['warning'],
            hover_color=COLORS['warning_hover']
        )

    def _show_step_2(self):
        """Show step 2: Final confirmation with details"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Update header
        self.header_icon.configure(text="✓")
        self.header_title.configure(
            text="Confirmación Final",
            text_color=COLORS['success']
        )
        self.header_subtitle.configure(text="Paso 2 de 2")

        # Sale details
        details_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("white", "gray22"),
            corner_radius=12,
            border_width=2,
            border_color=COLORS['success']
        )
        details_frame.pack(fill="both", expand=True)

        # Title
        ctk.CTkLabel(
            details_frame,
            text="📋 Detalles de la Venta",
            font=FONTS['subtitle'],
            text_color=("gray20", "gray80")
        ).pack(pady=(20, 15))

        # Separator
        ctk.CTkFrame(
            details_frame,
            fg_color=("gray80", "gray30"),
            height=1
        ).pack(fill="x", padx=20, pady=(0, 15))

        # Client info
        info_row = ctk.CTkFrame(details_frame, fg_color="transparent")
        info_row.pack(fill="x", padx=30, pady=8)

        ctk.CTkLabel(
            info_row,
            text="Cliente:",
            font=FONTS['body_bold'],
            text_color=("gray30", "gray70"),
            anchor="w",
            width=120
        ).pack(side="left")

        ctk.CTkLabel(
            info_row,
            text=self.client_name,
            font=FONTS['body'],
            text_color=("gray20", "gray80"),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Items count
        info_row = ctk.CTkFrame(details_frame, fg_color="transparent")
        info_row.pack(fill="x", padx=30, pady=8)

        ctk.CTkLabel(
            info_row,
            text="Productos:",
            font=FONTS['body_bold'],
            text_color=("gray30", "gray70"),
            anchor="w",
            width=120
        ).pack(side="left")

        ctk.CTkLabel(
            info_row,
            text=f"{self.items_count} artículos",
            font=FONTS['body'],
            text_color=("gray20", "gray80"),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Separator
        ctk.CTkFrame(
            details_frame,
            fg_color=("gray80", "gray30"),
            height=1
        ).pack(fill="x", padx=20, pady=15)

        # Total amount (highlighted)
        total_frame = ctk.CTkFrame(
            details_frame,
            fg_color=("gray85", "gray17"),
            corner_radius=8
        )
        total_frame.pack(fill="x", padx=30, pady=(0, 20))

        total_container = ctk.CTkFrame(total_frame, fg_color="transparent")
        total_container.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            total_container,
            text="TOTAL:",
            font=FONTS['subtitle'],
            text_color=("gray30", "gray70"),
            anchor="w"
        ).pack(side="left")

        ctk.CTkLabel(
            total_container,
            text=f"${self.total:.2f}",
            font=("Arial", 28, "bold"),
            text_color=COLORS['success'],
            anchor="e"
        ).pack(side="right")

        # Confirmation question
        ctk.CTkLabel(
            details_frame,
            text="¿Desea procesar esta venta?",
            font=FONTS['subheader'],
            text_color=("gray20", "gray80")
        ).pack(pady=(5, 20))

        # Update button
        self.btn_action.configure(
            text="✓ Confirmar Venta",
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover']
        )

    def _next_step(self):
        """Handle next step or confirmation"""
        if self.current_step == 1:
            # Move to step 2
            self.current_step = 2
            self._show_step_2()
        else:
            # Confirm and close
            self.result = True
            self._close()

    def _cancel(self):
        """Cancel and close dialog"""
        self.result = False
        self._close()

    def _close(self):
        """Close the dialog"""
        self.grab_release()
        self.destroy()

    def get_result(self) -> bool:
        """
        Get the user's decision

        Returns:
            True if user confirmed, False otherwise
        """
        return self.result
