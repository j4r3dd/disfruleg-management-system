# -*- coding: utf-8 -*-
"""
Client Detail Dialog - Analytics Module (Refactored with Components)
Using DetailDialogBase, KPIGrid, FilterPanel, and ChartSection
"""
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from .utils.formatters import (
    DateFormatter,
    CurrencyFormatter,
    NumberFormatter,
    PeriodConverter
)
from .components.dialog_components import (
    DetailDialogBase,
    KPIGrid,
    FilterPanel,
    ChartSection
)

class ClientDetailDialog(DetailDialogBase):
    """Dialog con detalle completo de cliente - Refactored with components"""

    def __init__(self, parent, client_data, data_manager):
        # Initialize base dialog
        super().__init__(
            parent,
            title=f"Detalle: {client_data.get('nombre_cliente', 'Cliente')}",
            width=1100,
            height=800
        )

        self.client_data = client_data
        self.data_manager = data_manager

        # Estado de filtros
        self.selected_period = '30D'
        self.selected_metric = 'ventas'
        self.compare_previous = False

        # Crear UI usando el content container de la base
        self.create_client_ui()

        # Cargar datos detallados
        self.load_detail_data()

    def create_client_ui(self):
        """Crear interfaz del cliente usando componentes"""
        # ========== HEADER ==========
        self.create_header(self.content)

        # ========== KPIs usando KPIGrid ==========
        grid = KPIGrid(self.content, self.colors)
        grid.add_kpis([
            ("Total Compras", CurrencyFormatter.format(self.client_data.get('total_ventas', 0)), self.colors['accent']),
            ("Notas", NumberFormatter.format_with_commas(self.client_data.get('cantidad_facturas', 0)), self.colors['success']),
            ("Última Compra", DateFormatter.format_full(self.client_data.get('ultima_compra')), self.colors['warning']),
            ("Saldo Pendiente", CurrencyFormatter.format(self.client_data.get('saldo_pendiente', 0)), self.colors['danger']),
            ("Descuento", NumberFormatter.format_percentage(self.client_data.get('porcentaje_descuento', 0)), "#06B6D4"),
            ("Estado", "🟢 Activo" if self.client_data.get('activo', 1) else "🔴 Inactivo", "#10B981"),
        ], columns=3)
        grid.build()

        # ========== FILTROS usando FilterPanel ==========
        panel = FilterPanel(self.content, self.colors)
        panel.add_period_filter(
            ["1D", "7D", "15D", "30D", "90D"],
            self.selected_period,
            self.change_period
        )
        panel.add_metric_filter(
            [("ventas", "Ventas"), ("cantidad", "Cantidad"), ("facturas", "Notas")],
            self.selected_metric,
            self.change_metric
        )
        panel.add_comparison_toggle(self.toggle_comparison)
        self.filter_panel, self.filter_refs = panel.build()

        # ========== GRÁFICO usando ChartSection ==========
        chart_section_builder = ChartSection(self.content, self.colors, height=350)
        self.chart_container = chart_section_builder.build()

        # ========== TOP PRODUCTOS ==========
        self.products_section = ctk.CTkFrame(
            self.content,
            fg_color=self.colors['bg_card'],
            corner_radius=12
        )
        self.products_section.pack(fill="x", pady=(0, 20))
        
        # ========== ANÁLISIS DEUDAS ==========
        self.debts_section = ctk.CTkFrame(
            self.content,
            fg_color=self.colors['bg_card'],
            corner_radius=12
        )
        self.debts_section.pack(fill="x", pady=(0, 20))
        
        # ========== BOTONES ==========
        btn_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="📥 Exportar Excel",
            command=self.export_excel,
            fg_color="transparent",
            border_width=2,
            border_color=self.colors['accent'],
            hover_color=self.colors['accent'],
            height=40,
            font=("Arial", 13)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            command=self.destroy,
            fg_color=self.colors['accent'],
            hover_color="#2563EB",
            height=40,
            font=("Arial", 14)
        ).pack(side="right")
    
    def create_header(self, parent):
        """Crear header con info del cliente"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        # Nombre
        ctk.CTkLabel(
            header,
            text=self.client_data.get('nombre_cliente', 'Cliente'),
            font=("Arial", 28, "bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w")
        
        # Info adicional
        info_text = f"Grupo: {self.client_data.get('clave_grupo', 'N/A')} • {self.client_data.get('tipo_cliente', 'N/A')}"
        ctk.CTkLabel(
            header,
            text=info_text,
            font=("Arial", 14),
            text_color=self.colors['text_secondary']
        ).pack(anchor="w", pady=(5, 0))
    
    # ========== FILTER CALLBACKS ==========

    def change_period(self, period):
        """Callback para cambio de período"""
        self.selected_period = period
        for p, btn in self.filter_refs['period_buttons'].items():
            if p == period:
                btn.configure(fg_color=self.colors['accent'])
            else:
                btn.configure(fg_color="transparent")
        self.load_detail_data()

    def change_metric(self, metric):
        """Callback para cambio de métrica"""
        self.selected_metric = metric
        for m, btn in self.filter_refs['metric_buttons'].items():
            if m == metric:
                btn.configure(fg_color=self.colors['accent'])
            else:
                btn.configure(fg_color="transparent")
        self.load_detail_data()

    def toggle_comparison(self):
        """Callback para toggle de comparación"""
        self.compare_previous = not self.compare_previous
        self.load_detail_data()
    
    def load_detail_data(self):
        """Cargar datos detallados del cliente con filtros"""
        try:
            id_cliente = self.client_data.get('id_cliente')
            if not id_cliente:
                return
            
            # Obtener detalles con filtros usando period en lugar de days
            detail = self.data_manager.get_client_detail(
                id_cliente,
                period=self.selected_period,
                metric=self.selected_metric
            )
            
            if detail:
                # Actualizar gráfico
                purchases_data = detail.get('historial_compras', [])
                
                # TODO: Comparación con periodo anterior requiere implementación adicional
                if self.compare_previous:
                    print("⚠️ Comparación con periodo anterior aún no implementada en AnalyticsService")
                
                self.create_purchases_chart(purchases_data)
                
                # Actualizar top productos
                self.create_products_list(detail.get('top_productos', []))
                
                # Actualizar análisis de deudas
                self.create_debts_analysis(detail.get('deudas', []))
        
        except Exception as e:
            print(f"Error loading client detail data: {e}")
            messagebox.showerror("Error", f"Error cargando datos: {e}")
    
    def get_days_from_period(self, period):
        """Convertir periodo a días"""
        period_map = {
            "7D": 7,
            "30D": 30,
            "90D": 90,
            "6M": 180,
            "1Y": 365,
            "Todo": 9999
        }
        return period_map.get(period, 30)
    
    def create_purchases_chart(self, purchases_data):
        """Crear gráfico de tendencia de compras"""
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        if not purchases_data or len(purchases_data) == 0:
            ctk.CTkLabel(
                self.chart_container,
                text="📊 No hay historial de compras para este periodo",
                font=("Arial", 14),
                text_color=self.colors['text_secondary']
            ).pack(expand=True, pady=40)
            return
        
        fig = Figure(figsize=(9.5, 4), facecolor=self.colors['bg_card'], dpi=100)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['bg_card'])
        
        fechas = [item.get('fecha') for item in purchases_data]
        valores = self.extract_metric_values(purchases_data)
        fechas_str = self.format_dates(fechas)
        
        ax.plot(range(len(fechas)), valores, 
                color=self.colors['accent'], linewidth=2.5,
                marker='o', markersize=6, 
                markerfacecolor=self.colors['success'],
                markeredgecolor=self.colors['accent'], 
                markeredgewidth=1.5,
                label='Periodo actual')
        
        ax.fill_between(range(len(fechas)), valores, 
                        alpha=0.2, color=self.colors['accent'])
        
        metric_labels = {
            "ventas": "Ventas ($)",
            "cantidad": "Cantidad Comprada",
            "facturas": "Número de Notas"
        }
        
        ax.set_xlabel('Fecha', fontsize=11, color=self.colors['text_secondary'])
        ax.set_ylabel(metric_labels.get(self.selected_metric, 'Valor'), 
                     fontsize=11, color=self.colors['text_secondary'])
        ax.set_title(f'Tendencia de Compras - {metric_labels.get(self.selected_metric, "Ventas")} ({self.selected_period})', 
                    fontsize=13, color=self.colors['text_primary'], pad=15)
        
        if len(fechas) > 15:
            step = max(1, len(fechas) // 10)
            ax.set_xticks(range(0, len(fechas), step))
            ax.set_xticklabels([fechas_str[i] for i in range(0, len(fechas), step)], 
                              rotation=45, ha='right', fontsize=9)
        else:
            ax.set_xticks(range(len(fechas)))
            ax.set_xticklabels(fechas_str, rotation=45, ha='right', fontsize=9)
        
        ax.tick_params(colors=self.colors['text_secondary'])
        ax.spines['bottom'].set_color(self.colors['text_secondary'])
        ax.spines['left'].set_color(self.colors['text_secondary'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.1, color=self.colors['text_secondary'])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    def create_comparison_chart(self, current_data, previous_data):
        """Crear gráfico con comparación de periodos"""
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        if not current_data or len(current_data) == 0:
            self.create_purchases_chart(current_data)
            return
        
        fig = Figure(figsize=(9.5, 4), facecolor=self.colors['bg_card'], dpi=100)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['bg_card'])
        
        fechas_current = [item.get('fecha') for item in current_data]
        valores_current = self.extract_metric_values(current_data)
        fechas_str = self.format_dates(fechas_current)
        
        ax.plot(range(len(fechas_current)), valores_current, 
                color=self.colors['accent'], linewidth=2.5,
                marker='o', markersize=6, 
                markerfacecolor=self.colors['success'],
                markeredgecolor=self.colors['accent'], 
                markeredgewidth=1.5,
                label='Periodo actual')
        
        ax.fill_between(range(len(fechas_current)), valores_current, 
                        alpha=0.2, color=self.colors['accent'])
        
        if previous_data and len(previous_data) > 0:
            valores_previous = self.extract_metric_values(previous_data)
            min_len = min(len(valores_current), len(valores_previous))
            
            ax.plot(range(min_len), valores_previous[:min_len], 
                    color=self.colors['text_secondary'], linewidth=2,
                    linestyle='--', marker='s', markersize=4,
                    alpha=0.6,
                    label='Periodo anterior')
        
        metric_labels = {
            "ventas": "Ventas ($)",
            "cantidad": "Cantidad Comprada",
            "facturas": "Número de Notas"
        }
        
        ax.set_xlabel('Fecha', fontsize=11, color=self.colors['text_secondary'])
        ax.set_ylabel(metric_labels.get(self.selected_metric, 'Valor'), 
                     fontsize=11, color=self.colors['text_secondary'])
        ax.set_title(f'Comparación - {metric_labels.get(self.selected_metric, "Ventas")} ({self.selected_period})', 
                    fontsize=13, color=self.colors['text_primary'], pad=15)
        
        if len(fechas_current) > 15:
            step = max(1, len(fechas_current) // 10)
            ax.set_xticks(range(0, len(fechas_current), step))
            ax.set_xticklabels([fechas_str[i] for i in range(0, len(fechas_current), step)], 
                              rotation=45, ha='right', fontsize=9)
        else:
            ax.set_xticks(range(len(fechas_current)))
            ax.set_xticklabels(fechas_str, rotation=45, ha='right', fontsize=9)
        
        ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
        ax.tick_params(colors=self.colors['text_secondary'])
        ax.spines['bottom'].set_color(self.colors['text_secondary'])
        ax.spines['left'].set_color(self.colors['text_secondary'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.1, color=self.colors['text_secondary'])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
    
    def extract_metric_values(self, data):
        """Extraer valores según métrica seleccionada"""
        if self.selected_metric == 'ventas':
            return [float(item.get('total_ventas', 0)) for item in data]
        elif self.selected_metric == 'cantidad':
            return [float(item.get('cantidad_total', 0)) for item in data]
        elif self.selected_metric == 'facturas':
            return [int(item.get('num_facturas', 0)) for item in data]
        else:
            return [float(item.get('total_ventas', 0)) for item in data]
    
    def format_dates(self, dates):
        """Formatear fechas para etiquetas"""
        return [DateFormatter.format_short(fecha) for fecha in dates]

    def format_date(self, date):
        """Formatear una fecha individual"""
        return DateFormatter.format_full(date)
    
    def create_products_list(self, products_data):
        """Crear lista de top productos comprados"""
        for widget in self.products_section.winfo_children():
            widget.destroy()
        
        header = ctk.CTkFrame(self.products_section, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="📦 Top Productos Comprados",
            font=("Arial", 18, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        if not products_data or len(products_data) == 0:
            ctk.CTkLabel(
                self.products_section,
                text="No hay datos de productos",
                font=("Arial", 13),
                text_color=self.colors['text_secondary']
            ).pack(pady=20)
            return
        
        for i, product in enumerate(products_data, 1):
            item = ctk.CTkFrame(
                self.products_section,
                fg_color=self.colors['bg_secondary'],
                corner_radius=6,
                height=60
            )
            item.pack(fill="x", padx=20, pady=5)
            item.pack_propagate(False)
            
            content = ctk.CTkFrame(item, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=15, pady=10)
            
            left = ctk.CTkFrame(content, fg_color="transparent")
            left.pack(side="left", fill="y")
            
            ctk.CTkLabel(
                left,
                text=f"#{i}",
                font=("Arial", 14, "bold"),
                text_color=self.colors['accent'],
                width=30
            ).pack(side="left")
            
            ctk.CTkLabel(
                left,
                text=product.get('nombre_producto', 'N/A'),
                font=("Arial", 14),
                text_color=self.colors['text_primary']
            ).pack(side="left", padx=(10, 0))
            
            right = ctk.CTkFrame(content, fg_color="transparent")
            right.pack(side="right")
            
            stats_text = f"Cantidad: {NumberFormatter.format_with_commas(product.get('cantidad_total', 0))}  •  Total: {CurrencyFormatter.format(product.get('total_comprado', 0))}"
            ctk.CTkLabel(
                right,
                text=stats_text,
                font=("Arial", 12),
                text_color=self.colors['text_secondary']
            ).pack(side="right")
    
    def create_debts_analysis(self, debts_data):
        """Crear análisis de deudas"""
        for widget in self.debts_section.winfo_children():
            widget.destroy()
        
        header = ctk.CTkFrame(self.debts_section, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="💳 Análisis de Pagos y Deudas",
            font=("Arial", 18, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        if not debts_data:
            ctk.CTkLabel(
                self.debts_section,
                text="✅ Cliente sin deudas pendientes",
                font=("Arial", 13),
                text_color=self.colors['success']
            ).pack(pady=20)
            return
        
        # Resumen de deudas
        total_deuda = sum(float(d.get('monto', 0)) - float(d.get('monto_pagado', 0)) for d in debts_data if not d.get('pagado'))
        deudas_pendientes = sum(1 for d in debts_data if not d.get('pagado'))
        
        summary = ctk.CTkFrame(self.debts_section, fg_color=self.colors['bg_secondary'], corner_radius=8)
        summary.pack(fill="x", padx=20, pady=(0, 10))
        
        summary_content = ctk.CTkFrame(summary, fg_color="transparent")
        summary_content.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(
            summary_content,
            text=f"⚠️ {deudas_pendientes} deuda(s) pendiente(s)  •  Total: {CurrencyFormatter.format(total_deuda)}",
            font=("Arial", 14, "bold"),
            text_color=self.colors['danger']
        ).pack(side="left")
        
        # Lista de deudas
        for debt in debts_data[:5]:  # Mostrar máximo 5
            if not debt.get('pagado'):
                self.create_debt_item(debt)
    
    def create_debt_item(self, debt):
        """Crear item de deuda individual"""
        item = ctk.CTkFrame(
            self.debts_section,
            fg_color=self.colors['bg_secondary'],
            corner_radius=6,
            height=65
        )
        item.pack(fill="x", padx=20, pady=5)
        item.pack_propagate(False)
        
        content = ctk.CTkFrame(item, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Left: Info
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="y")
        
        fecha_gen = self.format_date(debt.get('fecha_generada'))
        ctk.CTkLabel(
            left,
            text=f"Nota #{debt.get('id_factura', 'N/A')} - {fecha_gen}",
            font=("Arial", 13),
            text_color=self.colors['text_primary']
        ).pack(anchor="w")
        
        descripcion = debt.get('descripcion', 'Sin descripción')
        ctk.CTkLabel(
            left,
            text=descripcion[:50] + "..." if len(descripcion) > 50 else descripcion,
            font=("Arial", 11),
            text_color=self.colors['text_secondary']
        ).pack(anchor="w", pady=(3, 0))
        
        # Right: Monto
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")
        
        monto = float(debt.get('monto', 0))
        pagado = float(debt.get('monto_pagado', 0))
        pendiente = monto - pagado
        
        ctk.CTkLabel(
            right,
            text=CurrencyFormatter.format(pendiente),
            font=("Arial", 16, "bold"),
            text_color=self.colors['danger']
        ).pack(side="right")

        if pagado > 0:
            ctk.CTkLabel(
                right,
                text=f"Pagado: {CurrencyFormatter.format(pagado)}  •  ",
                font=("Arial", 11),
                text_color=self.colors['text_secondary']
            ).pack(side="right", padx=(0, 5))
    
    def export_excel(self):
        """Exportar datos a Excel"""
        try:
            from tkinter import filedialog
            import pandas as pd
            from datetime import datetime
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"detalle_{self.client_data.get('nombre_cliente', 'cliente')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )
            
            if not filename:
                return
            
            id_cliente = self.client_data.get('id_cliente')
            
            detail = self.data_manager.get_client_detail(
                id_cliente,
                period=self.selected_period,
                metric=self.selected_metric
            )
            
            if not detail:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Hoja 1: Información general
                info_data = {
                    'Campo': [
                        'Cliente',
                        'Grupo',
                        'Tipo',
                        'Periodo',
                        'Total Compras',
                        'Notas Generadas',
                        'Saldo Pendiente',
                        'Descuento',
                        'Última Compra',
                        'Fecha Exportación'
                    ],
                    'Valor': [
                        self.client_data.get('nombre_cliente', 'N/A'),
                        self.client_data.get('clave_grupo', 'N/A'),
                        self.client_data.get('tipo_cliente', 'N/A'),
                        self.selected_period,
                        CurrencyFormatter.format(self.client_data.get('total_ventas', 0)),
                        NumberFormatter.format_with_commas(self.client_data.get('cantidad_facturas', 0)),
                        CurrencyFormatter.format(self.client_data.get('saldo_pendiente', 0)),
                        NumberFormatter.format_percentage(self.client_data.get('porcentaje_descuento', 0)),
                        DateFormatter.format_full(self.client_data.get('ultima_compra')),
                        DateFormatter.format_datetime(datetime.now())
                    ]
                }
                df_info = pd.DataFrame(info_data)
                df_info.to_excel(writer, sheet_name='Información', index=False)
                
                # Hoja 2: Historial de compras
                purchases_data = detail.get('historial_compras', [])
                if purchases_data:
                    df_purchases = pd.DataFrame(purchases_data)
                    df_purchases.to_excel(writer, sheet_name='Historial Compras', index=False)
                
                # Hoja 3: Top productos
                products_data = detail.get('top_productos', [])
                if products_data:
                    df_products = pd.DataFrame(products_data)
                    df_products.to_excel(writer, sheet_name='Top Productos', index=False)
                
                # Hoja 4: Deudas
                debts_data = detail.get('deudas', [])
                if debts_data:
                    df_debts = pd.DataFrame(debts_data)
                    df_debts.to_excel(writer, sheet_name='Deudas', index=False)
            
            messagebox.showinfo(
                "Exportación exitosa",
                f"Datos exportados correctamente a:\n{filename}"
            )
            
        except ImportError:
            messagebox.showerror(
                "Error",
                "Se requiere pandas y openpyxl para exportar a Excel.\n\n"
                "Instala con: pip install pandas openpyxl"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")


# ========== EJEMPLO DE USO ==========

if __name__ == "__main__":
    """
    Ejemplo de cómo usar el dialog de cliente
    """
    
    class MockDataManager:
        def get_client_detail(self, id_cliente, days=30, metric='ventas', offset_days=0):
            from datetime import datetime, timedelta
            
            base_date = datetime.now() - timedelta(days=days + offset_days)
            
            historial = []
            for i in range(days):
                fecha = base_date + timedelta(days=i)
                historial.append({
                    'fecha': DateFormatter.format_short(fecha),
                    'total_ventas': 1500 + (i % 7) * 300,
                    'cantidad_total': 25 + (i % 5) * 5,
                    'num_facturas': 2 + (i % 3)
                })
            
            return {
                'historial_compras': historial,
                'top_productos': [
                    {'nombre_producto': 'Producto A', 'cantidad_total': 150, 'total_comprado': 22500},
                    {'nombre_producto': 'Producto B', 'cantidad_total': 120, 'total_comprado': 18000},
                    {'nombre_producto': 'Producto C', 'cantidad_total': 90, 'total_comprado': 13500},
                ],
                'deudas': [
                    {
                        'id_factura': 1234,
                        'fecha_generada': datetime.now() - timedelta(days=15),
                        'monto': 5000,
                        'monto_pagado': 2000,
                        'pagado': False,
                        'descripcion': 'Factura de productos varios'
                    },
                    {
                        'id_factura': 1235,
                        'fecha_generada': datetime.now() - timedelta(days=30),
                        'monto': 3000,
                        'monto_pagado': 500,
                        'pagado': False,
                        'descripcion': 'Pedido especial'
                    }
                ]
            }
    
    root = ctk.CTk()
    root.geometry("400x300")
    
    client_data = {
        'id_cliente': 1,
        'nombre_cliente': 'Cliente de Prueba SA de CV',
        'clave_grupo': 'GRUPO-A',
        'tipo_cliente': 'Mayorista',
        'total_ventas': 125000.00,
        'cantidad_facturas': 45,
        'ultima_compra': datetime.now() - timedelta(days=5),
        'saldo_pendiente': 8000.00,
        'porcentaje_descuento': 15.0,
        'activo': 1
    }
    
    def open_detail():
        data_manager = MockDataManager()
        dialog = ClientDetailDialog(root, client_data, data_manager)
    
    ctk.CTkButton(
        root,
        text="Abrir Detalle de Cliente",
        command=open_detail,
        font=("Arial", 16),
        height=50
    ).pack(expand=True)
    
    root.mainloop()