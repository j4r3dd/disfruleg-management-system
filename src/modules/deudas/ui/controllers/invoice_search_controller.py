# -*- coding: utf-8 -*-
"""
Invoice Search Controller - UI Layer
Handles invoice search and PDF download
NEW FILE: deudas/ui/controllers/invoice_search_controller.py
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import date
from pathlib import Path
import tempfile
import subprocess
import sys

from src.config import debug_print
from src.theme import COLORS, FONTS

from ...business import DebtService, InvoiceAccessService


class InvoiceSearchController:
    """Controller for invoice search and PDF access"""
    
    def __init__(
        self,
        parent,
        debt_service: DebtService,
        invoice_access_service: InvoiceAccessService,
        user_data: dict
    ):
        self.parent = parent
        self.debt_service = debt_service
        self.invoice_access_service = invoice_access_service
        self.user_data = user_data
        self.search_results = []
        self.window = None
    
    def show(self):
        """Show search window"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("🔍 Búsqueda de Folios")
        self.window.geometry("900x700")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Create search UI"""
        # Search bar
        search_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="Buscar:",
            font=FONTS['body_bold']
        ).pack(side="left", padx=(0, 10))
        
        self.search_var = ctk.StringVar()
        ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Número de folio o cliente...",
            height=40
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            search_frame,
            text="🔍 Buscar",
            command=self.perform_search,
            width=100
        ).pack(side="left")
        
        # Results
        self.results_frame = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def perform_search(self):
        """Execute search"""
        query = self.search_var.get().strip()
        
        if not query:
            messagebox.showwarning("Validación", "Ingrese un término de búsqueda")
            return
        
        try:
            self.search_results = self.debt_service.search_invoice_history(
                query=query,
                incluir_pagadas=True
            )
            
            self.render_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda:\n{str(e)}")
    
    def render_results(self):
        """Render search results"""
        # Clear previous
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not self.search_results:
            ctk.CTkLabel(
                self.results_frame,
                text="No se encontraron resultados",
                font=FONTS['body']
            ).pack(pady=20)
            return
        
        for invoice in self.search_results:
            self.create_invoice_result_card(invoice)
    
    def create_invoice_result_card(self, invoice: dict):
        """Create a result card for an invoice"""
        card = ctk.CTkFrame(self.results_frame, fg_color=COLORS['card_bg'], corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Left: Invoice info
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Folio #{invoice['id_factura']} | {invoice['fecha_generada']}",
            font=FONTS['body_bold']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"{invoice['nombre_cliente']} | ${invoice['monto_total']:,.2f} | {invoice['estado'].upper()}",
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(2, 0))
        
        # Right: Buttons
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(side="right")
        
        # Download button (only if PDF exists)
        if invoice.get('tiene_pdf', False):
            ctk.CTkButton(
                button_frame,
                text="📥 Descargar",
                command=lambda: self.download_pdf(invoice['id_factura']),
                width=90,
                height=30,
                font=FONTS['small']
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                button_frame,
                text="👁 Ver",
                command=lambda: self.view_pdf(invoice['id_factura']),
                width=60,
                height=30,
                font=FONTS['small']
            ).pack(side="left", padx=2)
        else:
            ctk.CTkLabel(
                button_frame,
                text="✗ PDF no disponible",
                font=FONTS['small'],
                text_color="gray"
            ).pack(padx=5)
    
    def download_pdf(self, id_factura: int):
        """Download PDF for invoice"""
        try:
            pdf_bytes = self.invoice_access_service.get_invoice_pdf(id_factura)
            
            if not pdf_bytes:
                messagebox.showerror("Error", "No se pudo obtener el PDF")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"folio_{id_factura}.pdf"
            )
            
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                # Log access
                self.invoice_access_service.log_pdf_access(
                    id_factura,
                    self.user_data.get('username', 'unknown'),
                    'descarga'
                )
                
                messagebox.showinfo("Éxito", f"PDF guardado en:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error descargando:\n{str(e)}")
    
    def view_pdf(self, id_factura: int):
        """Open PDF viewer"""
        try:
            pdf_bytes = self.invoice_access_service.get_invoice_pdf(id_factura)
            
            if not pdf_bytes:
                messagebox.showerror("Error", "No se pudo obtener el PDF")
                return
            
            # Create temp file and open
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name
            
            # Open with system PDF viewer
            if sys.platform == 'darwin':
                subprocess.Popen(['open', tmp_path])
            elif sys.platform == 'win32':
                subprocess.Popen(['start', tmp_path])
            else:
                subprocess.Popen(['xdg-open', tmp_path])
            
            # Log access
            self.invoice_access_service.log_pdf_access(
                id_factura,
                self.user_data.get('username', 'unknown'),
                'vista'
            )
        
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo:\n{str(e)}")
