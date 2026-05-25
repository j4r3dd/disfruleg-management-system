# -*- coding: utf-8 -*-
"""
Product Detail Dialog - Analytics Module (Refactored with Components)
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

class ProductDetailDialog(DetailDialogBase):
    """Dialog con detalle completo de producto - Refactored with components"""

    def __init__(self, parent, product_data, data_manager):
        # Initialize base dialog
        super().__init__(
            parent,
            title=f"Detalle: {product_data.get('nombre_producto', 'Producto')}",
            width=1000,
            height=750
        )

        self.product_data = product_data
        self.data_manager = data_manager

        # 🔍 DEBUG: Verificar datos recibidos
        print("\n🔍 DEBUG ProductDetailDialog:")
        print(f"   - product_data keys: {list(product_data.keys())}")
        print(f"   - id_producto: {product_data.get('id_producto')}")
        print(f"   - nombre_producto: {product_data.get('nombre_producto')}")

        # Estado de filtros
        self.selected_period = '30D'
        self.selected_metric = 'cantidad'
        self.compare_previous = False

        # Crear UI usando el content container de la base
        self.create_product_ui()

        # Cargar datos detallados
        self.load_detail_data()

    def create_product_ui(self):
        """Crear interfaz del producto usando componentes"""
        # ========== HEADER ==========
        self.create_header(self.content)

        # ========== KPIs usando KPIGrid ==========
        grid = KPIGrid(self.content, self.colors)
        grid.add_kpis([
            ("Cantidad Vendida", NumberFormatter.format_with_commas(self.product_data.get('cantidad_vendida', 0)), self.colors['accent']),
            ("Ingresos Totales", CurrencyFormatter.format(self.product_data.get('ingresos_totales', 0)), self.colors['success']),
            ("Stock Actual", NumberFormatter.format_with_commas(self.product_data.get('stock', 0)), self.colors['warning']),
            ("Ganancia", CurrencyFormatter.format(self.product_data.get('ganancia_total', 0)), self.colors['success']),
            ("Margen %", NumberFormatter.format_percentage(self.product_data.get('margen_ganancia_porcentaje', 0)), "#06B6D4"),
            ("Costos", CurrencyFormatter.format(self.product_data.get('costos_totales', 0)), "#EF4444"),
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
            [("cantidad", "Cantidad"), ("ventas", "Ventas"), ("ganancia", "Ganancia")],
            self.selected_metric,
            self.change_metric
        )
        panel.add_comparison_toggle(self.toggle_comparison)
        self.filter_panel, self.filter_refs = panel.build()

        # ========== GRÁFICO usando ChartSection ==========
        chart_section_builder = ChartSection(self.content, self.colors, height=350)
        self.chart_container = chart_section_builder.build()

        # ========== TOP CLIENTES ==========
        self.clients_section = ctk.CTkFrame(
            self.content,
            fg_color=self.colors['bg_card'],
            corner_radius=12
        )
        self.clients_section.pack(fill="x", pady=(0, 20))

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
            hover_color="#7C3AED",
            height=40,
            font=("Arial", 14)
        ).pack(side="right")
    
    def create_header(self, parent):
        """Crear header con nombre del producto"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        # Nombre
        ctk.CTkLabel(
            header,
            text=self.product_data.get('nombre_producto', 'Producto'),
            font=("Arial", 28, "bold"),
            text_color=self.colors['text_primary']
        ).pack(anchor="w")
        
        # Unidad
        ctk.CTkLabel(
            header,
            text=f"Unidad: {self.product_data.get('unidad_producto', 'N/A')}",
            font=("Arial", 14),
            text_color=self.colors['text_secondary']
        ).pack(anchor="w", pady=(5, 0))
    
    # ========== FILTER CALLBACKS ==========

    def change_period(self, period):
        """Callback para cambio de período"""
        self.selected_period = period
        # Update button states
        for p, btn in self.filter_refs['period_buttons'].items():
            if p == period:
                btn.configure(fg_color=self.colors['accent'])
            else:
                btn.configure(fg_color="transparent")
        print(f"🔄 Período cambiado a: {period}")
        self.load_detail_data()

    def change_metric(self, metric):
        """Callback para cambio de métrica"""
        self.selected_metric = metric
        # Update button states
        for m, btn in self.filter_refs['metric_buttons'].items():
            if m == metric:
                btn.configure(fg_color=self.colors['accent'])
            else:
                btn.configure(fg_color="transparent")
        print(f"🔄 Métrica cambiada a: {metric}")
        self.load_detail_data()

    def toggle_comparison(self):
        """Callback para toggle de comparación"""
        self.compare_previous = not self.compare_previous
        print(f"🔄 Comparación: {'activada' if self.compare_previous else 'desactivada'}")
        self.load_detail_data()
    
    # ========== CARGA DE DATOS (CON DEBUG MEJORADO) ==========
    
    def load_detail_data(self):
        """Cargar datos detallados del producto con logging completo"""
        try:
            id_producto = self.product_data.get('id_producto')
            
            if not id_producto:
                print("❌ ERROR: id_producto no está presente en product_data")
                print(f"   product_data keys: {list(self.product_data.keys())}")
                self.show_error_message("Error: ID de producto no encontrado")
                return
            
            print(f"\n📊 Cargando datos del producto:")
            print(f"   - ID: {id_producto}")
            print(f"   - Periodo: {self.selected_period}")
            print(f"   - Métrica: {self.selected_metric}")
            print(f"   - Comparar: {self.compare_previous}")
            
            # Verificar que el método existe
            if not hasattr(self.data_manager, 'get_product_detail'):
                print("❌ ERROR: data_manager no tiene método 'get_product_detail'")
                print(f"   Métodos disponibles: {[m for m in dir(self.data_manager) if not m.startswith('_')]}")
                self.show_error_message("Error: Método get_product_detail() no encontrado")
                return
            
            # Llamar al método con period en lugar de days
            detail = self.data_manager.get_product_detail(
                id_producto,
                period=self.selected_period,
                metric=self.selected_metric
            )
            
            print(f"\n📦 Respuesta del data_manager:")
            print(f"   - Tipo: {type(detail)}")
            
            if detail is None:
                print("❌ ERROR: get_product_detail() retornó None")
                self.show_error_message("No se pudieron cargar los datos")
                return
            
            if not isinstance(detail, dict):
                print(f"❌ ERROR: get_product_detail() retornó {type(detail)} en lugar de dict")
                self.show_error_message("Formato de datos incorrecto")
                return
            
            print(f"   - Claves: {list(detail.keys())}")
            
            # Verificar historial_ventas
            historial = detail.get('historial_ventas', [])
            print(f"   - historial_ventas: {len(historial)} registros")
            if historial and len(historial) > 0:
                print(f"     Ejemplo: {historial[0]}")
            
            # Verificar top_clientes
            clientes = detail.get('top_clientes', [])
            print(f"   - top_clientes: {len(clientes)} clientes")
            if clientes and len(clientes) > 0:
                print(f"     Ejemplo: {clientes[0]}")
            
            # Cargar datos actuales
            self.load_sales_chart(historial)
            self.load_top_clients(clientes)
            
            # TODO: Comparación con periodo anterior requiere implementación adicional en AnalyticsService
            if self.compare_previous:
                print(f"⚠️ Comparación con periodo anterior aún no implementada en AnalyticsService")
            
            print("✅ Datos cargados exitosamente\n")
            
        except Exception as e:
            print(f"❌ ERROR en load_detail_data: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Error al cargar datos: {str(e)}")
    
    def show_error_message(self, message):
        """Mostrar mensaje de error en el gráfico"""
        # Limpiar sección del gráfico
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        # Mostrar mensaje
        error_frame = ctk.CTkFrame(self.chart_container, fg_color="transparent")
        error_frame.pack(expand=True, pady=50)
        
        ctk.CTkLabel(
            error_frame,
            text="⚠️",
            font=("Arial", 48),
            text_color=self.colors['warning']
        ).pack()
        
        ctk.CTkLabel(
            error_frame,
            text=message,
            font=("Arial", 16),
            text_color=self.colors['text_secondary']
        ).pack(pady=(10, 0))
        
        ctk.CTkLabel(
            error_frame,
            text="Revisa la consola para más detalles",
            font=("Arial", 12),
            text_color=self.colors['text_secondary']
        ).pack(pady=(5, 0))
    
    def get_days_from_period(self, period):
        """Convertir periodo a días"""
        mapping = {
            '7D': 7,
            '15D': 15,
            '30D': 30,
            '60D': 60,
            '90D': 90,
            '180D': 180,
            '1Y': 365
        }
        return mapping.get(period, 30)
    
    def load_sales_chart(self, sales_data, previous_data=None):
        """Cargar gráfico de ventas"""
        # Limpiar
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        # Header
        header = ctk.CTkFrame(self.chart_container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        metric_names = {
            'cantidad': 'Cantidad Vendida',
            'ventas': 'Ventas ($)',
            'ganancia': 'Ganancia ($)'
        }
        
        title = f"📈 {metric_names.get(self.selected_metric, 'Ventas')} - {self.selected_period}"
        ctk.CTkLabel(
            header,
            text=title,
            font=("Arial", 18, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        if not sales_data or len(sales_data) == 0:
            ctk.CTkLabel(
                self.chart_container,
                text="No hay datos para el periodo seleccionado",
                font=("Arial", 14),
                text_color=self.colors['text_secondary']
            ).pack(pady=40)
            return
        
        # Crear figura
        fig = Figure(figsize=(10, 4), facecolor=self.colors['bg_card'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['bg_card'])
        
        # Extraer datos
        fechas = [item.get('fecha', '') for item in sales_data]
        valores = [float(item.get(self.selected_metric, 0)) for item in sales_data]
        
        # Plot principal
        ax.plot(fechas, valores, 
                color=self.colors['accent'],
                linewidth=2.5,
                marker='o',
                markersize=4,
                label='Actual')
        ax.fill_between(range(len(fechas)), valores, 
                        alpha=0.2, 
                        color=self.colors['accent'])
        
        # Plot comparación
        if previous_data and len(previous_data) > 0:
            prev_valores = [float(item.get(self.selected_metric, 0)) for item in previous_data]
            ax.plot(fechas, prev_valores[:len(fechas)],
                   color=self.colors['text_secondary'],
                   linewidth=1.5,
                   linestyle='--',
                   marker='s',
                   markersize=3,
                   label='Periodo Anterior',
                   alpha=0.6)
        
        # Estilo
        ax.set_xlabel('Fecha', fontsize=11, color=self.colors['text_secondary'])
        ax.set_ylabel(metric_names.get(self.selected_metric, 'Valor'), 
                     fontsize=11, 
                     color=self.colors['text_secondary'])
        
        ax.tick_params(colors=self.colors['text_secondary'], labelsize=9)
        ax.grid(True, alpha=0.1, color=self.colors['text_secondary'])
        
        # Rotar etiquetas del eje x
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Leyenda
        if previous_data:
            ax.legend(loc='upper left', 
                     frameon=False,
                     fontsize=10,
                     labelcolor=self.colors['text_secondary'])
        
        fig.tight_layout()
        
        # Incrustar
        canvas = FigureCanvasTkAgg(fig, self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def load_top_clients(self, clients_data):
        """Cargar top clientes"""
        # Limpiar
        for widget in self.clients_section.winfo_children():
            widget.destroy()
        
        # Header
        header = ctk.CTkFrame(self.clients_section, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="👥 Top Clientes",
            font=("Arial", 18, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        if not clients_data or len(clients_data) == 0:
            ctk.CTkLabel(
                self.clients_section,
                text="No hay datos de clientes",
                font=("Arial", 13),
                text_color=self.colors['text_secondary']
            ).pack(pady=20)
            return
        
        # Lista
        for i, client in enumerate(clients_data, 1):
            item = ctk.CTkFrame(
                self.clients_section,
                fg_color=self.colors['bg_secondary'],
                corner_radius=6,
                height=60
            )
            item.pack(fill="x", padx=20, pady=5)
            item.pack_propagate(False)
            
            content = ctk.CTkFrame(item, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=15, pady=10)
            
            # Número y nombre
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
                text=client.get('nombre_cliente', 'N/A'),
                font=("Arial", 14),
                text_color=self.colors['text_primary']
            ).pack(side="left", padx=(10, 0))
            
            # Stats
            right = ctk.CTkFrame(content, fg_color="transparent")
            right.pack(side="right")
            
            stats_text = f"Cantidad: {NumberFormatter.format_with_commas(client.get('cantidad_total', 0))}  •  Compras: {client.get('num_compras', 0)}"
            ctk.CTkLabel(
                right,
                text=stats_text,
                font=("Arial", 12),
                text_color=self.colors['text_secondary']
            ).pack(side="right")
    
    # ========== EXPORT ==========
    
    def export_excel(self):
        """Exportar datos a Excel"""
        try:
            from tkinter import filedialog
            import pandas as pd
            from datetime import datetime
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"detalle_{self.product_data.get('nombre_producto', 'producto')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )
            
            if not filename:
                return
            
            id_producto = self.product_data.get('id_producto')
            
            detail = self.data_manager.get_product_detail(
                id_producto,
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
                        'Producto',
                        'Unidad',
                        'Periodo',
                        'Cantidad Vendida',
                        'Ingresos Totales',
                        'Ganancia Total',
                        'Margen %',
                        'Stock Actual',
                        'Fecha Exportación'
                    ],
                    'Valor': [
                        self.product_data.get('nombre_producto', 'N/A'),
                        self.product_data.get('unidad_producto', 'N/A'),
                        self.selected_period,
                        NumberFormatter.format_with_commas(self.product_data.get('cantidad_vendida', 0), decimals=2),
                        CurrencyFormatter.format(self.product_data.get('ingresos_totales', 0)),
                        CurrencyFormatter.format(self.product_data.get('ganancia_total', 0)),
                        NumberFormatter.format_percentage(self.product_data.get('margen_ganancia_porcentaje', 0)),
                        NumberFormatter.format_with_commas(self.product_data.get('stock', 0), decimals=2),
                        DateFormatter.format_datetime(datetime.now())
                    ]
                }
                df_info = pd.DataFrame(info_data)
                df_info.to_excel(writer, sheet_name='Información', index=False)
                
                # Hoja 2: Historial de ventas
                sales_data = detail.get('historial_ventas', [])
                if sales_data:
                    df_sales = pd.DataFrame(sales_data)
                    df_sales.to_excel(writer, sheet_name='Historial Ventas', index=False)
                
                # Hoja 3: Top clientes
                clients_data = detail.get('top_clientes', [])
                if clients_data:
                    df_clients = pd.DataFrame(clients_data)
                    df_clients.to_excel(writer, sheet_name='Top Clientes', index=False)
            
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
    """Ejemplo de cómo usar el dialog con debug"""
    
    class MockDataManager:
        def get_product_detail(self, id_producto, days=30, metric='cantidad', offset_days=0):
            print(f"\n🔧 MockDataManager.get_product_detail() llamado:")
            print(f"   - id_producto: {id_producto}")
            print(f"   - days: {days}")
            print(f"   - metric: {metric}")
            print(f"   - offset_days: {offset_days}")
            
            from datetime import datetime, timedelta
            base_date = datetime.now() - timedelta(days=days + offset_days)
            
            historial = []
            for i in range(days):
                fecha = base_date + timedelta(days=i)
                historial.append({
                    'fecha': DateFormatter.format_short(fecha),
                    'cantidad': 10 + (i % 5) * 3,
                    'ventas': (10 + (i % 5) * 3) * 150,
                    'ganancia': (10 + (i % 5) * 3) * 50
                })
            
            result = {
                'historial_ventas': historial,
                'top_clientes': [
                    {'nombre_cliente': 'Cliente A', 'cantidad_total': 150, 'num_compras': 5},
                    {'nombre_cliente': 'Cliente B', 'cantidad_total': 120, 'num_compras': 4},
                    {'nombre_cliente': 'Cliente C', 'cantidad_total': 90, 'num_compras': 3},
                ]
            }
            
            print(f"   - Retornando: {len(historial)} registros de historial, {len(result['top_clientes'])} clientes")
            return result
    
    root = ctk.CTk()
    root.geometry("400x300")
    
    product_data = {
        'id_producto': 1,
        'nombre_producto': 'Producto de Prueba',
        'unidad_producto': 'KG',
        'cantidad_vendida': 1250.5,
        'ingresos_totales': 187575.0,
        'ganancia_total': 62525.0,
        'margen_ganancia_porcentaje': 33.33,
        'stock': 450.0,
        'costos_totales': 125050.0
    }
    
    def open_detail():
        data_manager = MockDataManager()
        dialog = ProductDetailDialog(root, product_data, data_manager)
    
    ctk.CTkButton(
        root,
        text="Abrir Detalle de Producto",
        command=open_detail,
        font=("Arial", 16),
        height=50
    ).pack(expand=True)
    
    root.mainloop()