# -*- coding: utf-8 -*-
"""
UI Layer - Product Creation Dialog
Standalone dialog for creating new products - RESPONSIVE
"""

import customtkinter as ctk
from tkinter import messagebox
from src.theme import COLORS

# Import responsive system
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.responsive_manager import ResponsiveMixin


class ProductDialog(ResponsiveMixin, ctk.CTkToplevel):
    """Dialog responsive para crear productos"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.result = {'success': False, 'data': None}
        
        # Configure window
        self.title("Crear Producto Nuevo")
        
        # Apply responsive - DIALOG preset con force_visible
        self.make_responsive('dialog', force_visible=True)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Construir interfaz"""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Title
        ctk.CTkLabel(
            main_frame,
            text="Crear Producto Nuevo",
            font=("Arial", 20, "bold"),
            text_color=COLORS.get('primary', '#2196F3')
        ).pack(pady=(0, 20))

        # Variables
        self.nombre_var = ctk.StringVar()
        self.unidad_var = ctk.StringVar(value="PIEZA")

        # Product name
        ctk.CTkLabel(
            main_frame,
            text="Nombre del Producto: *",
            font=("Arial", 12, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        self.nombre_entry = ctk.CTkEntry(
            main_frame,
            textvariable=self.nombre_var,
            height=40,
            font=("Arial", 12),
            placeholder_text="Ej: Nutella 240g"
        )
        self.nombre_entry.pack(fill="x", pady=(0, 15))
        self.nombre_entry.focus_set()

        # Unit
        ctk.CTkLabel(
            main_frame,
            text="Unidad de Medida: *",
            font=("Arial", 12, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        unidades_comunes = [
            "PIEZA", "KG", "GRAMO", "LITRO", "ML",
            "CAJA", "PAQUETE", "BOLSA", "UNIDAD"
        ]

        self.unidad_combo = ctk.CTkComboBox(
            main_frame,
            variable=self.unidad_var,
            values=unidades_comunes,
            height=40,
            font=("Arial", 12)
        )
        self.unidad_combo.pack(fill="x", pady=(0, 20))

        # Info box
        info_frame = ctk.CTkFrame(main_frame, fg_color=("gray90", "gray20"), corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            info_frame,
            text="ℹ️ El producto se creará inmediatamente\ny estará disponible para esta compra",
            font=("Arial", 10),
            text_color="gray",
            justify="left"
        ).pack(padx=15, pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self._on_cancel,
            fg_color="gray",
            hover_color="darkgray",
            width=150,
            height=40,
            font=("Arial", 12)
        ).pack(side="left", expand=True, padx=(0, 5))

        ctk.CTkButton(
            button_frame,
            text="Crear Producto",
            command=self._on_save,
            fg_color=COLORS.get('success', '#4CAF50'),
            hover_color=COLORS.get('success_hover', '#45A049'),
            width=150,
            height=40,
            font=("Arial", 12, "bold")
        ).pack(side="left", expand=True, padx=(5, 0))
    
    def _on_save(self):
        """Handle save button"""
        try:
            nombre = self.nombre_entry.get().strip()
        except:
            nombre = self.nombre_var.get().strip()

        try:
            unidad = self.unidad_combo.get().strip()
        except:
            unidad = self.unidad_var.get().strip()

        # Validate
        if not nombre:
            messagebox.showerror(
                "Error",
                "El nombre del producto es obligatorio",
                parent=self
            )
            self.nombre_entry.focus_set()
            return

        if len(nombre) < 3:
            messagebox.showerror(
                "Error",
                "El nombre debe tener al menos 3 caracteres",
                parent=self
            )
            self.nombre_entry.focus_set()
            return

        if not unidad:
            messagebox.showerror(
                "Error",
                "Debe seleccionar una unidad",
                parent=self
            )
            return

        # Save result
        self.result['success'] = True
        self.result['data'] = {
            'nombre': nombre,
            'unidad': unidad
        }

        self.destroy()
    
    def _on_cancel(self):
        """Handle cancel button"""
        self.destroy()
    
    def get_result(self):
        """Obtener resultado después de wait_window()"""
        return self.result['success'], self.result['data']


def create_product_dialog(parent) -> tuple[bool, dict]:
    """
    Show dialog to create a new product - NUEVA VERSIÓN RESPONSIVE

    Args:
        parent: Parent window

    Returns:
        Tuple of (success, product_data)
    """
    dialog = ProductDialog(parent)
    dialog.wait_window()
    return dialog.get_result()