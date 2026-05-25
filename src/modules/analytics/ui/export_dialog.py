# -*- coding: utf-8 -*-
"""
DISFRULEG - Export Dialog (MISMO PATRÓN QUE FORMATO)
"""
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from typing import Callable
import threading
from datetime import datetime, timedelta


class ExportDialog(ctk.CTkToplevel):
    """Diálogo robusto de exportación"""
    
    def __init__(
        self,
        parent,
        export_callback: Callable,
        has_dashboard: bool = True,
        has_products: bool = True,
        has_clients: bool = True,
        has_groups: bool = True
    ):
        super().__init__(parent)

        self.title("Exportar")
        self.geometry("400x550")
        self.resizable(False, False)
        
        self.export_callback = export_callback
        self.result = None
        self._is_destroyed = False
        
        # Variables - MISMO PATRÓN QUE FORMATO
        self.format_var = ctk.StringVar(value="pdf")
        self.sections_var = ctk.StringVar(value="all")  # all, custom
        
        # Para secciones individuales
        self.dash_enabled = has_dashboard
        self.prod_enabled = has_products
        self.cli_enabled = has_clients
        self.grp_enabled = has_groups
        
        # Tracking de selección
        self.dash_selected = ctk.BooleanVar(value=has_dashboard)
        self.prod_selected = ctk.BooleanVar(value=has_products)
        self.cli_selected = ctk.BooleanVar(value=has_clients)
        self.grp_selected = ctk.BooleanVar(value=has_groups)
        
        self.chart_selected = ctk.BooleanVar(value=True)
        
        self._build_ui()
        
        # Override destroy
        original_destroy = self.destroy
        def safe_destroy():
            self._is_destroyed = True
            try:
                original_destroy()
            except:
                pass
        self.destroy = safe_destroy
        
        self.grab_set()
        self.focus()
    
    def _build_ui(self):
        """UI con mismo patrón que formato"""
        # Main
        main = ctk.CTkFrame(self, fg_color="#1a1a1a")
        main.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkFrame(main, fg_color="#0f0f0f", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="Exportar Reportes", font=("Arial", 14, "bold")).pack(pady=12)
        
        # Content
        content = ctk.CTkScrollableFrame(main, fg_color="#1a1a1a")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # ========== FORMATO (ORIGINAL - FUNCIONA) ==========
        ctk.CTkLabel(content, text="FORMATO", font=("Arial", 10, "bold"), text_color="#888").pack(anchor="w", pady=(0, 8))
        
        ctk.CTkRadioButton(
            content, text="PDF", variable=self.format_var, value="pdf",
            fg_color="#8B5CF6", text_color="#fff", font=("Arial", 11)
        ).pack(anchor="w", pady=2)
        
        ctk.CTkRadioButton(
            content, text="Excel", variable=self.format_var, value="excel",
            fg_color="#8B5CF6", text_color="#fff", font=("Arial", 11)
        ).pack(anchor="w", pady=2)
        
        ctk.CTkRadioButton(
            content, text="Ambos", variable=self.format_var, value="both",
            fg_color="#8B5CF6", text_color="#fff", font=("Arial", 11)
        ).pack(anchor="w", pady=2)
        
        ctk.CTkFrame(content, fg_color="#333", height=1).pack(fill="x", pady=12)

        # ========== RANGO DE FECHAS ==========
        ctk.CTkLabel(content, text="RANGO DE FECHAS", font=("Arial", 10, "bold"), text_color="#888").pack(anchor="w", pady=(0, 8))

        # Date range option
        date_range_frame = ctk.CTkFrame(content, fg_color="transparent")
        date_range_frame.pack(fill="x", pady=(0, 8))

        # Start date
        start_frame = ctk.CTkFrame(date_range_frame, fg_color="transparent")
        start_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(
            start_frame,
            text="Desde:",
            font=("Arial", 11),
            text_color="#fff",
            width=60
        ).pack(side="left")

        # Default: 30 days ago
        start_date = datetime.now() - timedelta(days=30)
        self.start_date_entry = DateEntry(
            start_frame,
            width=18,
            background='#8B5CF6',
            foreground='white',
            borderwidth=1,
            year=start_date.year,
            month=start_date.month,
            day=start_date.day,
            date_pattern='dd/mm/yyyy'
        )
        self.start_date_entry.pack(side="left", padx=(5, 0))

        # End date
        end_frame = ctk.CTkFrame(date_range_frame, fg_color="transparent")
        end_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(
            end_frame,
            text="Hasta:",
            font=("Arial", 11),
            text_color="#fff",
            width=60
        ).pack(side="left")

        # Default: today
        self.end_date_entry = DateEntry(
            end_frame,
            width=18,
            background='#8B5CF6',
            foreground='white',
            borderwidth=1,
            date_pattern='dd/mm/yyyy'
        )
        self.end_date_entry.pack(side="left", padx=(5, 0))

        ctk.CTkFrame(content, fg_color="#333", height=1).pack(fill="x", pady=12)

        # ========== SECCIONES - USANDO MISMO PATRÓN ==========
        ctk.CTkLabel(content, text="SECCIONES", font=("Arial", 10, "bold"), text_color="#888").pack(anchor="w", pady=(0, 8))
        
        # Dashboard
        dash_btn = ctk.CTkButton(
            content,
            text="✓ Dashboard" if self.dash_selected.get() else "☐ Dashboard",
            command=lambda: self._toggle_dash(),
            fg_color="#8B5CF6" if self.dash_selected.get() else "#333",
            hover_color="#7C3AED" if self.dash_selected.get() else "#444",
            text_color="#fff",
            font=("Arial", 11),
            height=28,
            state="normal" if self.dash_enabled else "disabled"
        )
        dash_btn.pack(anchor="w", pady=2, fill="x")
        self.dash_btn = dash_btn

        # Productos
        prod_btn = ctk.CTkButton(
            content,
            text="✓ Productos" if self.prod_selected.get() else "☐ Productos",
            command=lambda: self._toggle_prod(),
            fg_color="#8B5CF6" if self.prod_selected.get() else "#333",
            hover_color="#7C3AED" if self.prod_selected.get() else "#444",
            text_color="#fff",
            font=("Arial", 11),
            height=28,
            state="normal" if self.prod_enabled else "disabled"
        )
        prod_btn.pack(anchor="w", pady=2, fill="x")
        self.prod_btn = prod_btn

        # Clientes
        cli_btn = ctk.CTkButton(
            content,
            text="✓ Clientes" if self.cli_selected.get() else "☐ Clientes",
            command=lambda: self._toggle_cli(),
            fg_color="#8B5CF6" if self.cli_selected.get() else "#333",
            hover_color="#7C3AED" if self.cli_selected.get() else "#444",
            text_color="#fff",
            font=("Arial", 11),
            height=28,
            state="normal" if self.cli_enabled else "disabled"
        )
        cli_btn.pack(anchor="w", pady=2, fill="x")
        self.cli_btn = cli_btn

        # Grupos
        grp_btn = ctk.CTkButton(
            content,
            text="✓ Grupos" if self.grp_selected.get() else "☐ Grupos",
            command=lambda: self._toggle_grp(),
            fg_color="#8B5CF6" if self.grp_selected.get() else "#333",
            hover_color="#7C3AED" if self.grp_selected.get() else "#444",
            text_color="#fff",
            font=("Arial", 11),
            height=28,
            state="normal" if self.grp_enabled else "disabled"
        )
        grp_btn.pack(anchor="w", pady=2, fill="x")
        self.grp_btn = grp_btn
        
        ctk.CTkFrame(content, fg_color="#333", height=1).pack(fill="x", pady=12)
        
        # ========== OPCIONES ==========
        ctk.CTkLabel(content, text="OPCIONES", font=("Arial", 10, "bold"), text_color="#888").pack(anchor="w", pady=(0, 8))
        
        chart_btn = ctk.CTkButton(
            content,
            text="✓ Incluir gráficos" if self.chart_selected.get() else "☐ Incluir gráficos",
            command=lambda: self._toggle_chart(),
            fg_color="#8B5CF6" if self.chart_selected.get() else "#333",
            hover_color="#7C3AED" if self.chart_selected.get() else "#444",
            text_color="#fff",
            font=("Arial", 11),
            height=28
        )
        chart_btn.pack(anchor="w", pady=2, fill="x")
        self.chart_btn = chart_btn
        
        # BOTONES
        btn_frame = ctk.CTkFrame(main, fg_color="#1a1a1a")
        btn_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkButton(
            btn_frame, text="Exportar", command=self._export,
            fg_color="#10B981", hover_color="#059669", text_color="#fff",
            font=("Arial", 11, "bold"), height=38
        ).pack(side="left", expand=True, padx=(0, 5), fill="x")
        
        ctk.CTkButton(
            btn_frame, text="Cancelar", command=self.destroy,
            fg_color="#333", hover_color="#444", text_color="#fff",
            font=("Arial", 11), height=38
        ).pack(side="left", expand=True, padx=(5, 0), fill="x")
    
    def _toggle_dash(self):
        """Alternar Dashboard"""
        self.dash_selected.set(not self.dash_selected.get())
        self._update_btn(self.dash_btn, self.dash_selected.get(), "Dashboard")

    def _toggle_prod(self):
        """Alternar Productos"""
        self.prod_selected.set(not self.prod_selected.get())
        self._update_btn(self.prod_btn, self.prod_selected.get(), "Productos")

    def _toggle_cli(self):
        """Alternar Clientes"""
        self.cli_selected.set(not self.cli_selected.get())
        self._update_btn(self.cli_btn, self.cli_selected.get(), "Clientes")

    def _toggle_grp(self):
        """Alternar Grupos"""
        self.grp_selected.set(not self.grp_selected.get())
        self._update_btn(self.grp_btn, self.grp_selected.get(), "Grupos")

    def _toggle_chart(self):
        """Alternar Gráficos"""
        self.chart_selected.set(not self.chart_selected.get())
        self._update_btn(self.chart_btn, self.chart_selected.get(), "Incluir gráficos")

    def _update_btn(self, btn, is_selected, label_text):
        """Actualizar estilo y texto del botón"""
        if is_selected:
            btn.configure(
                text=f"✓ {label_text}",
                fg_color="#8B5CF6",
                hover_color="#7C3AED"
            )
        else:
            btn.configure(
                text=f"☐ {label_text}",
                fg_color="#333",
                hover_color="#444"
            )
    
    def _export(self):
        """Exportar"""
        # Validate date range
        try:
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()

            if start_date > end_date:
                messagebox.showerror("Error", "La fecha de inicio no puede ser posterior a la fecha final")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error en las fechas seleccionadas: {e}")
            return

        selected = {
            'dashboard': self.dash_selected.get() and self.dash_enabled,
            'products': self.prod_selected.get() and self.prod_enabled,
            'clients': self.cli_selected.get() and self.cli_enabled,
            'groups': self.grp_selected.get() and self.grp_enabled,
        }

        if not any(selected.values()):
            messagebox.showwarning("Validación", "Selecciona al menos una sección.")
            return

        thread = threading.Thread(target=self._do_export, args=(selected, start_date, end_date), daemon=True)
        thread.start()
    
    def _do_export(self, selected, start_date, end_date):
        """Exportar en background"""
        try:
            # Create filename with date range
            date_str = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"

            options = {
                'format': self.format_var.get(),
                'sections': selected,
                'include_charts': self.chart_selected.get(),
                'include_summary': True,
                'filename': f"Reporte_{date_str}",
                'start_date': start_date,
                'end_date': end_date,
            }

            success, message = self.export_callback(options)

            if success and not self._is_destroyed:
                self.result = message
                # Delay destroy to let pending events complete
                try:
                    self.after(100, self._safe_destroy)
                except:
                    pass
            elif not self._is_destroyed:
                try:
                    messagebox.showerror("Error", str(message))
                except:
                    pass

        except Exception as e:
            if not self._is_destroyed:
                try:
                    messagebox.showerror("Error", str(e))
                except:
                    pass

    def _safe_destroy(self):
        """Safely destroy dialog with cleanup"""
        try:
            if not self._is_destroyed:
                self._is_destroyed = True
                self.quit()
                self.destroy()
        except:
            pass


class ExportProgressDialog(ctk.CTkToplevel):
    """Diálogo de progreso"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Exportando")
        self.geometry("300x100")
        self.resizable(False, False)
        
        frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="Generando...", font=("Arial", 11, "bold")).pack(pady=(0, 10))
        
        ctk.CTkProgressBar(frame, fg_color="#333", progress_color="#8B5CF6", height=3).pack(fill="x")
        
        self.grab_set()
    
    def update_progress(self, value: float, status: str):
        self.progress_bar.set(value)
        self.status_label.configure(text=status)
        self.update_idletasks()