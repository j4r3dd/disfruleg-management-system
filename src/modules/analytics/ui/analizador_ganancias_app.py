# -*- coding: utf-8 -*-
"""
DISFRULEG - Análisis de Ganancias (Clean Architecture v3.0)
Professional Sidebar + Notion-Style Continuous Scroll
✅ REFACTORED: Using service layer with clean architecture
"""
import sys
import platform

# ✅ DPI Awareness Windows
if platform.system() == 'Windows':
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

import customtkinter as ctk
from tkinter import messagebox
# from tkcalendar import DateEntry  # Reemplazado por DarkDatePicker
import os
import subprocess
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging
from src.utils.responsive_manager import ResponsiveMixin

from src.database.conexion import conectar, return_connection
from src.theme import FONTS

# Import from business layer (Clean Architecture)
from ..business import AnalyticsService

# Import UI components
from .ui_components import (
    StatCard, MetricRow, LoadingIndicator, SearchBar,
    NoDataMessage, FilterBar, DarkDatePicker, ClickableCard, LoadingOverlay
)
from .components.chart_components import (
    LineChartComponent,
    BarChartComponent,
    ComparisonChartComponent
)
from .utils.formatters import (
    DateFormatter,
    CurrencyFormatter,
    NumberFormatter,
    PeriodConverter
)
from .utils.view_builders import (
    DashboardViewBuilder,
    RankingViewBuilder,
    FilterBarBuilder
)
from .debt_detail_dialog import DebtDetailDialog
from .export_manager import ExportManager, ChartExporter
from .export_dialog import ExportDialog, ExportProgressDialog

# 🎨 PALETA CUSTOM ANALYTICS - Dark Gray + Violet/Blue Accents
ANALYTICS_COLORS = {
    # Backgrounds
    'bg_primary': '#0A0A0A',
    'bg_secondary': '#1A1A1A',
    'bg_card': '#242424',
    'bg_surface': '#2E2E2E',
    
    # Accents vibrantes
    'accent_violet': '#8B5CF6',
    'accent_blue': '#3B82F6',
    'accent_cyan': '#06B6D4',
    
    # Status colors
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'info': '#3B82F6',
    
    # Text
    'text_primary': '#F5F5F5',
    'text_secondary': '#A1A1A1',
    'text_muted': '#6B6B6B',
    
    # Hovers
    'hover_violet': '#7C3AED',
    'hover_blue': '#2563EB',
    'hover_surface': '#383838',
}

COLORS = {
    'primary': ANALYTICS_COLORS['bg_primary'],
    'secondary': ANALYTICS_COLORS['bg_secondary'],
    'surface': ANALYTICS_COLORS['bg_surface'],
    'card_bg': ANALYTICS_COLORS['bg_card'],
    'accent': ANALYTICS_COLORS['accent_violet'],
    'success': ANALYTICS_COLORS['success'],
    'success_hover': '#059669',
    'warning': ANALYTICS_COLORS['warning'],
    'danger': ANALYTICS_COLORS['danger'],
    'info': ANALYTICS_COLORS['info'],
    'text_primary': ANALYTICS_COLORS['text_primary'],
    'text_secondary': ANALYTICS_COLORS['text_secondary'],
    'text_muted': ANALYTICS_COLORS['text_muted'],
    **ANALYTICS_COLORS
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalisisGananciasApp(ResponsiveMixin):
    """Aplicación de análisis - Clean Architecture Design"""

    def __init__(self, root, user_data, analytics_service: AnalyticsService):
        super().__init__()

        self.root = root
        self.root.title("Análisis de Ventas - Disfruleg")
        self.make_responsive_for_root('large')

        self.user_data = user_data if isinstance(user_data, dict) else {}
        self.es_admin = (self.user_data.get('rol', '') == 'admin')

        # Service layer (injected dependency)
        self.analytics_service = analytics_service

        # Initialize export manager
        from .export_manager import ExportManager
        self.export_manager = ExportManager(data_manager=None)  # data_manager not needed for our exports

        self.sidebar_collapsed = False
        self.current_view = 'dashboard'  # Track current active view
        self.selected_period = '7D'  # Default: últimos 7 días (for dashboard chart)

        self.create_interface()
        self.load_all_data()
    
    def make_responsive_for_root(self, preset='large'):
        """Hacer responsive la ventana root"""
        try:
            from src.utils.responsive_manager import ResponsiveConfig
            
            config = ResponsiveConfig.get_preset(preset)
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            width = int(screen_width * config['width_ratio'])
            height = int(screen_height * config['height_ratio'])
            
            width = min(width, config['max_width'])
            height = min(height, config['max_height'])
            width = max(width, config['min_width'])
            height = max(height, config['min_height'])
            
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            self.root.minsize(config['min_width'], config['min_height'])
            
            logger.info(f"✅ Analytics responsive: {width}x{height} (preset: {preset})")
            
        except Exception as e:
            logger.error(f"Error en make_responsive_for_root: {e}")
            self.root.geometry("1600x950")
    
    def create_interface(self):
        """Crear interfaz principal híbrida"""
        main_container = ctk.CTkFrame(self.root, fg_color=COLORS['primary'])
        main_container.pack(fill="both", expand=True)
        
        self.create_sidebar(main_container)
        
        self.content_area = ctk.CTkFrame(main_container, fg_color=COLORS['primary'])
        self.content_area.pack(side="right", fill="both", expand=True)
        
        self.create_top_bar()
        self.create_scrollable_content()
    
    def create_sidebar(self, parent):
        """Sidebar navigation profesional"""
        self.sidebar = ctk.CTkFrame(
            parent, 
            fg_color=COLORS['surface'],
            width=220,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        sidebar_header = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=60)
        sidebar_header.pack(fill="x", pady=(20, 30))
        sidebar_header.pack_propagate(False)
        
        ctk.CTkLabel(
            sidebar_header,
            text="📊",
            font=("Arial", 28)
        ).pack(pady=(0, 5))
        
        self.sidebar_title = ctk.CTkLabel(
            sidebar_header,
            text="Analytics",
            font=("Arial", 16, "bold"),
            text_color=COLORS['success']
        )
        self.sidebar_title.pack()
        
        nav_items = [
            ("📈", "Dashboard", "dashboard"),
            ("📦", "Productos", "productos"),
            ("👥", "Clientes", "clientes"),
            ("🏢", "Grupos", "grupos"),
        ]
        
        self.nav_buttons = {}
        for icon, label, section_id in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {label}",
                font=("Arial", 14),
                fg_color="transparent",
                hover_color=COLORS['accent'],
                anchor="w",
                height=44,
                command=lambda s=section_id: self.switch_to_view(s)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[section_id] = btn
        
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)
        
        separator = ctk.CTkFrame(self.sidebar, fg_color=COLORS['accent'], height=1)
        separator.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            self.sidebar,
            text="🔄  Actualizar",
            font=("Arial", 13),
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            height=38,
            command=self.refresh_all
        ).pack(fill="x", padx=12, pady=4)
        
        ctk.CTkButton(
            self.sidebar,
            text="📄  Exportar",
            font=("Arial", 13),
            fg_color="transparent",
            hover_color=COLORS['accent'],
            border_width=1,
            border_color=COLORS['accent'],
            height=38,
            command=self.export_to_pdf
        ).pack(fill="x", padx=12, pady=4)

        ctk.CTkButton(
            self.sidebar,
            text="📁  Cambiar carpeta",
            font=("Arial", 11),
            fg_color="transparent",
            hover_color=COLORS['hover_surface'],
            text_color=COLORS['text_secondary'],
            height=32,
            command=self.change_export_directory
        ).pack(fill="x", padx=12, pady=4)

        ctk.CTkButton(
            self.sidebar,
            text="⎋  Salir",
            font=("Arial", 13),
            fg_color=COLORS['danger'],
            hover_color="#DC2626",
            height=38,
            command=self.on_closing
        ).pack(side="bottom", fill="x", padx=12, pady=(4, 20))
    
    def create_top_bar(self):
        """Top bar minimalista con búsqueda global"""
        topbar = ctk.CTkFrame(self.content_area, fg_color=COLORS['surface'], height=60)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        
        left = ctk.CTkFrame(topbar, fg_color="transparent")
        left.pack(side="left", fill="y", padx=24, pady=15)
        
        ctk.CTkLabel(
            left,
            text="Inicio / Análisis de Ventas",
            font=("Arial", 13),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        search_container = ctk.CTkFrame(topbar, fg_color="transparent")
        search_container.pack(side="left", fill="both", expand=True, padx=20)
        
        self.global_search = ctk.CTkEntry(
            search_container,
            placeholder_text="Buscar en todo... (Ctrl+K)",
            font=("Arial", 13),
            height=36,
            border_width=1,
            border_color=COLORS['accent']
        )
        self.global_search.pack(fill="x", expand=True)
        self.global_search.bind('<KeyRelease>', self.on_global_search)
        
        right = ctk.CTkFrame(topbar, fg_color="transparent")
        right.pack(side="right", fill="y", padx=24, pady=15)
        
        user_name = self.user_data.get('nombre_completo', 'Usuario')
        ctk.CTkLabel(
            right,
            text=f"👤 {user_name}",
            font=("Arial", 13),
            text_color=COLORS['text_primary']
        ).pack(side="right")
    
    def create_scrollable_content(self):
        """Setup view-based navigation system"""
        # Container for all views
        self.views_container = ctk.CTkFrame(
            self.content_area,
            fg_color=COLORS['primary']
        )
        self.views_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Create all views
        self.create_dashboard_view()
        self.create_productos_view()
        self.create_clientes_view()
        self.create_grupos_view()

        # Show dashboard by default
        self.switch_to_view('dashboard')

    # ========== VIEW CREATION METHODS ==========

    def create_dashboard_view(self):
        """Create Dashboard view with KPIs and chart"""
        self.dashboard_view = ctk.CTkScrollableFrame(
            self.views_container,
            fg_color=COLORS['primary']
        )

        content = ctk.CTkFrame(self.dashboard_view, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)

        self.create_dashboard_section(content)
        self.create_chart_section(content)

    def create_productos_view(self):
        """Create Productos view with date picker filters"""
        self.productos_view = ctk.CTkScrollableFrame(
            self.views_container,
            fg_color=COLORS['primary']
        )

        content = ctk.CTkFrame(self.productos_view, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)

        # Header
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="📦 Top Productos por Ganancia",
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        self.products_count_label = ctk.CTkLabel(
            title_frame,
            text="(0)",
            font=("Arial", 16),
            text_color=COLORS['text_secondary']
        )
        self.products_count_label.pack(side="left", padx=(8, 0))

        # Date filters
        self.create_date_filters(header, 'productos')

        # Chart section
        chart_section = ctk.CTkFrame(
            content,
            fg_color=COLORS['card_bg'],
            corner_radius=12,
            height=300
        )
        chart_section.pack(fill="x", pady=(0, 20))
        chart_section.pack_propagate(False)

        self.productos_chart_container = ctk.CTkFrame(chart_section, fg_color="transparent")
        self.productos_chart_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Products list container
        self.products_container = ctk.CTkFrame(content, fg_color="transparent")
        self.products_container.pack(fill="both", expand=True)

    def create_clientes_view(self):
        """Create Clientes view with date picker filters"""
        self.clientes_view = ctk.CTkScrollableFrame(
            self.views_container,
            fg_color=COLORS['primary']
        )

        content = ctk.CTkFrame(self.clientes_view, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)

        # Header
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="👥 Top Clientes por Ventas",
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        self.clients_count_label = ctk.CTkLabel(
            title_frame,
            text="(0)",
            font=("Arial", 16),
            text_color=COLORS['text_secondary']
        )
        self.clients_count_label.pack(side="left", padx=(8, 0))

        # Date filters
        self.create_date_filters(header, 'clientes')

        # Chart section
        chart_section = ctk.CTkFrame(
            content,
            fg_color=COLORS['card_bg'],
            corner_radius=12,
            height=300
        )
        chart_section.pack(fill="x", pady=(0, 20))
        chart_section.pack_propagate(False)

        self.clientes_chart_container = ctk.CTkFrame(chart_section, fg_color="transparent")
        self.clientes_chart_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Clients list container
        self.clients_container = ctk.CTkFrame(content, fg_color="transparent")
        self.clients_container.pack(fill="both", expand=True)

    def create_grupos_view(self):
        """Create Grupos view with date picker filters"""
        self.grupos_view = ctk.CTkScrollableFrame(
            self.views_container,
            fg_color=COLORS['primary']
        )

        content = ctk.CTkFrame(self.grupos_view, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)

        # Header
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="🏢 Resumen por Grupos",
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        self.groups_count_label = ctk.CTkLabel(
            title_frame,
            text="(0)",
            font=("Arial", 16),
            text_color=COLORS['text_secondary']
        )
        self.groups_count_label.pack(side="left", padx=(8, 0))

        # Date filters
        self.create_date_filters(header, 'grupos')

        # Chart section
        chart_section = ctk.CTkFrame(
            content,
            fg_color=COLORS['card_bg'],
            corner_radius=12,
            height=300
        )
        chart_section.pack(fill="x", pady=(0, 20))
        chart_section.pack_propagate(False)

        self.grupos_chart_container = ctk.CTkFrame(chart_section, fg_color="transparent")
        self.grupos_chart_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Groups list container
        self.groups_container = ctk.CTkFrame(content, fg_color="transparent")
        self.groups_container.pack(fill="both", expand=True)

    # ========== SECTION COMPONENTS (used by views) ==========

    def create_date_filters(self, parent, section_name):
        """Create date range filter with dark-themed date pickers"""
        filters = ctk.CTkFrame(parent, fg_color="transparent")
        filters.pack(side="right")

        # Start date label
        ctk.CTkLabel(
            filters,
            text="Desde:",
            font=("Arial", 12),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 5))

        # Start date picker (default: 30 days ago) - Using DarkDatePicker
        start_date = datetime.now() - timedelta(days=30)
        start_date_picker = DarkDatePicker(
            filters,
            initial_date=start_date,
            width=130
        )
        start_date_picker.pack(side="left", padx=(0, 10))

        # End date label
        ctk.CTkLabel(
            filters,
            text="Hasta:",
            font=("Arial", 12),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 5))

        # End date picker (default: today) - Using DarkDatePicker
        end_date_picker = DarkDatePicker(
            filters,
            initial_date=datetime.now(),
            width=130
        )
        end_date_picker.pack(side="left", padx=(0, 10))

        # Apply button
        apply_btn = ctk.CTkButton(
            filters,
            text="Aplicar",
            width=80,
            height=32,
            font=("Arial", 12),
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            command=lambda: self.apply_date_filter(section_name, start_date_picker, end_date_picker)
        )
        apply_btn.pack(side="left")

        # Store references
        if section_name == 'productos':
            self.productos_start_date = start_date_picker
            self.productos_end_date = end_date_picker
        elif section_name == 'clientes':
            self.clientes_start_date = start_date_picker
            self.clientes_end_date = end_date_picker
        elif section_name == 'grupos':
            self.grupos_start_date = start_date_picker
            self.grupos_end_date = end_date_picker

    def apply_date_filter(self, section_name, start_date_picker, end_date_picker):
        """Apply date filter to reload data"""
        try:
            # Get selected dates from DarkDatePicker
            start_date = start_date_picker.get_date()
            end_date = end_date_picker.get_date()

            # Validate dates
            if start_date > end_date:
                messagebox.showerror("Error", "La fecha de inicio no puede ser posterior a la fecha final")
                return

            # Convert to DateRange
            from ..domain.models import DateRange
            date_range = DateRange(
                start_date=start_date,
                end_date=end_date,
                days=(end_date - start_date).days
            )

            # Reload data for the specific section
            if section_name == 'productos':
                # Reset loaded flags
                if hasattr(self, '_productos_chart_loaded'):
                    delattr(self, '_productos_chart_loaded')
                if hasattr(self, '_productos_data_loaded'):
                    delattr(self, '_productos_data_loaded')
                # Reload with date range
                self.load_products_data_by_date_range(date_range)
                self.load_productos_chart_by_date_range(date_range)

            elif section_name == 'clientes':
                # Reset loaded flags
                if hasattr(self, '_clientes_chart_loaded'):
                    delattr(self, '_clientes_chart_loaded')
                if hasattr(self, '_clientes_data_loaded'):
                    delattr(self, '_clientes_data_loaded')
                # Reload with date range
                self.load_clients_data_by_date_range(date_range)
                self.load_clientes_chart_by_date_range(date_range)

            elif section_name == 'grupos':
                # Reset loaded flags
                if hasattr(self, '_grupos_chart_loaded'):
                    delattr(self, '_grupos_chart_loaded')
                if hasattr(self, '_grupos_data_loaded'):
                    delattr(self, '_grupos_data_loaded')
                # Reload with date range
                self.load_groups_data_by_date_range(date_range)
                self.load_grupos_chart_by_date_range(date_range)

        except Exception as e:
            logger.error(f"Error applying date filter: {e}")
            messagebox.showerror("Error", f"Error al aplicar filtro: {e}")

    def create_dashboard_section(self, parent):
        """Sección Dashboard con KPIs - Built using DashboardViewBuilder"""
        builder = DashboardViewBuilder(parent, COLORS, "dashboard")
        builder.set_title("📊 Dashboard General")
        builder.set_timestamp_visible(True)

        # First row of KPIs
        builder.add_kpi_row([
            ("Total Vendido", "$0.00", "💰", COLORS['success']),
            ("Liquidez", "$0.00", "💧", COLORS['info']),
            ("Compras", "$0.00", "🛒", COLORS['warning']),
            ("Margen Promedio", "0%", "📊", COLORS['success'])
        ], row_name="row1")

        # Second row of KPIs
        builder.add_kpi_row([
            ("Clientes Activos", "0", "👥", COLORS['warning']),
            ("Notas Generadas", "0", "📄", COLORS['accent']),
            ("Pendiente de Pago", "$0.00", "⚠️", COLORS['danger'], self.show_debt_details)
        ], row_name="row2")

        # Build and store KPI widget references
        section = builder.build(StatCard)

        self.kpi_ventas = builder.get_kpi_widget("row1_0")
        self.kpi_liquidez = builder.get_kpi_widget("row1_1")
        self.kpi_comprado = builder.get_kpi_widget("row1_2")
        self.kpi_margen = builder.get_kpi_widget("row1_3")
        self.kpi_clientes = builder.get_kpi_widget("row2_0")
        self.kpi_facturas = builder.get_kpi_widget("row2_1")
        self.kpi_pendiente = builder.get_kpi_widget("row2_2")
    
    def create_chart_section(self, parent):
        """Sección de gráfico principal con filtros funcionales"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 40))
        
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(
            header,
            text="📈 Tendencia de Ventas",
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        filters = ctk.CTkFrame(header, fg_color="transparent")
        filters.pack(side="right")
        
        # ✅ INDENTACIÓN CORRECTA - dentro del método
        self.period_buttons = {}
        
        for period in ["1D", "7D", "30D", "90D"]:
            btn = ctk.CTkButton(
                filters,
                text=period,
                width=50,
                height=32,
                font=("Arial", 12),
                fg_color=COLORS['accent'] if period == '7D' else "transparent",  # 7D seleccionado por defecto
                hover_color=COLORS['accent'],
                border_width=1,
                border_color=COLORS['accent'],
                command=lambda p=period: self.change_chart_period(p)
            )
            btn.pack(side="left", padx=4)
            self.period_buttons[period] = btn
        
        chart_container = ctk.CTkFrame(
            section,
            fg_color=COLORS['card_bg'],
            corner_radius=12,
            height=350
        )
        chart_container.pack(fill="both")
        chart_container.pack_propagate(False)
        
        self.chart_canvas_container = ctk.CTkFrame(chart_container, fg_color="transparent")
        self.chart_canvas_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.load_chart()
    
    # ✅ INDENTACIÓN CORRECTA - métodos de clase con 4 espacios
    def change_chart_period(self, period):
        """Cambiar periodo del gráfico con feedback visual"""
        self.selected_period = period
        
        for p, btn in self.period_buttons.items():
            if p == period:
                btn.configure(fg_color=COLORS['accent'])
            else:
                btn.configure(fg_color="transparent")
        
        self.load_chart()
    
    def load_chart(self):
        """Cargar y mostrar gráfico de ventas según periodo seleccionado"""
        try:
            sales_data = self.analytics_service.get_sales_trend(self.selected_period)

            if not sales_data or len(sales_data) == 0:
                # Clear container
                for widget in self.chart_canvas_container.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(
                    self.chart_canvas_container,
                    text="📊 No hay datos de ventas para mostrar en este periodo",
                    font=("Arial", 14),
                    text_color=COLORS['text_secondary']
                ).pack(expand=True)
                return

            # Extract data for chart
            dates = [item.fecha for item in sales_data]
            ventas = [float(item.total_ventas) for item in sales_data]

            # Use chart component
            chart = LineChartComponent(COLORS)
            chart.create(
                dates=dates,
                values=ventas,
                parent=self.chart_canvas_container,
                title="",
                ylabel="Ventas ($)",
                xlabel="Fecha"
            )

        except Exception as e:
            logger.error(f"Error loading chart: {e}")
            # Clear container
            for widget in self.chart_canvas_container.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.chart_canvas_container,
                text=f"❌ Error cargando gráfico: {str(e)}",
                font=("Arial", 13),
                text_color=COLORS['danger']
            ).pack(expand=True)

    # ========== PRODUCTOS VIEW CHART METHODS ==========

    def load_productos_chart(self, period='30D'):
        """Load productos chart showing top products by profit"""
        try:
            # Get top products data with period filter
            products = self.analytics_service.get_top_products(limit=10, period=period)

            if not products or len(products) == 0:
                # Clear container
                for widget in self.productos_chart_container.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(
                    self.productos_chart_container,
                    text="📊 No hay datos de productos para mostrar",
                    font=("Arial", 14),
                    text_color=COLORS['text_secondary']
                ).pack(expand=True)
                return

            # Prepare data for chart
            product_names = [p.nombre_producto for p in products]
            profits = [float(p.ganancia_total) for p in products]

            # Use chart component
            chart = BarChartComponent(COLORS)
            chart.create(
                labels=product_names,
                values=profits,
                parent=self.productos_chart_container,
                title="Top 10 Productos por Ganancia",
                xlabel="Ganancia Total ($)"
            )

        except Exception as e:
            logger.error(f"Error loading productos chart: {e}")
            # Clear container
            for widget in self.productos_chart_container.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.productos_chart_container,
                text=f"❌ Error cargando gráfico: {str(e)}",
                font=("Arial", 13),
                text_color=COLORS['danger']
            ).pack(expand=True)

    # ========== CLIENTES VIEW CHART METHODS ==========

    def load_clientes_chart(self, period='30D'):
        """Load clientes chart showing top clients by sales"""
        try:
            # Get top clients data with period filter
            clients = self.analytics_service.get_top_clients(limit=10, period=period)

            if not clients or len(clients) == 0:
                # Clear container
                for widget in self.clientes_chart_container.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(
                    self.clientes_chart_container,
                    text="📊 No hay datos de clientes para mostrar",
                    font=("Arial", 14),
                    text_color=COLORS['text_secondary']
                ).pack(expand=True)
                return

            # Prepare data for chart
            client_names = [c.nombre_cliente for c in clients]
            sales = [float(c.total_ventas) for c in clients]

            # Use chart component
            chart = BarChartComponent(COLORS)
            chart.create(
                labels=client_names,
                values=sales,
                parent=self.clientes_chart_container,
                title="Top 10 Clientes por Ventas",
                xlabel="Total Ventas ($)"
            )

        except Exception as e:
            logger.error(f"Error loading clientes chart: {e}")
            # Clear container
            for widget in self.clientes_chart_container.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.clientes_chart_container,
                text=f"❌ Error cargando gráfico: {str(e)}",
                font=("Arial", 13),
                text_color=COLORS['danger']
            ).pack(expand=True)

    # ========== GRUPOS VIEW CHART METHODS ==========

    def load_grupos_chart(self, period='30D'):
        """Load grupos chart showing groups by sales"""
        try:
            # Get groups data with period filter
            groups = self.analytics_service.get_groups_summary(period=period)

            if not groups or len(groups) == 0:
                # Clear container
                for widget in self.grupos_chart_container.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(
                    self.grupos_chart_container,
                    text="📊 No hay datos de grupos para mostrar",
                    font=("Arial", 14),
                    text_color=COLORS['text_secondary']
                ).pack(expand=True)
                return

            # Sort by total_ventas descending and take top 10
            sorted_groups = sorted(groups, key=lambda g: float(g.total_ventas), reverse=True)[:10]

            # Prepare data for chart
            group_names = [g.clave_grupo for g in sorted_groups]
            sales = [float(g.total_ventas) for g in sorted_groups]

            # Use chart component
            chart = BarChartComponent(COLORS)
            chart.create(
                labels=group_names,
                values=sales,
                parent=self.grupos_chart_container,
                title="Top 10 Grupos por Ventas",
                xlabel="Total Ventas ($)"
            )

        except Exception as e:
            logger.error(f"Error loading grupos chart: {e}")
            # Clear container
            for widget in self.grupos_chart_container.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.grupos_chart_container,
                text=f"❌ Error cargando gráfico: {str(e)}",
                font=("Arial", 13),
                text_color=COLORS['danger']
            ).pack(expand=True)

    # ========== NEW DATE RANGE LOADING METHODS ==========

    def load_products_data_by_date_range(self, date_range):
        """Load products data filtered by date range"""
        self._clear_container(self.products_container)

        try:
            products = self.analytics_service.product_repo.get_top_products(limit=10, date_range=date_range)
            self.products_count_label.configure(text=f"({len(products)})")

            if not products:
                NoDataMessage(
                    self.products_container,
                    "No hay datos de productos para el rango de fechas seleccionado"
                ).pack(fill="both", expand=True, pady=20)
                return

            for i, p in enumerate(products):
                self.create_product_card(self.products_container, p, i)

        except Exception as e:
            self._show_error(self.products_container, str(e))

    def load_productos_chart_by_date_range(self, date_range):
        """Load productos chart for date range"""
        try:
            products = self.analytics_service.product_repo.get_top_products(limit=10, date_range=date_range)

            if not products or len(products) == 0:
                for widget in self.productos_chart_container.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(
                    self.productos_chart_container,
                    text="📊 No hay datos para el rango de fechas seleccionado",
                    font=("Arial", 14),
                    text_color=COLORS['text_secondary']
                ).pack(expand=True)
                return

            product_names = [p.nombre_producto for p in products]
            profits = [float(p.ganancia_total) for p in products]

            chart = BarChartComponent(COLORS)
            chart.create(
                labels=product_names,
                values=profits,
                parent=self.productos_chart_container,
                title="Top 10 Productos por Ganancia",
                xlabel="Ganancia Total ($)"
            )

        except Exception as e:
            logger.error(f"Error loading productos chart by date range: {e}")
            for widget in self.productos_chart_container.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.productos_chart_container,
                text=f"❌ Error: {str(e)}",
                font=("Arial", 13),
                text_color=COLORS['danger']
            ).pack(expand=True)

    def load_clients_data_by_date_range(self, date_range):
        """Load clients data filtered by date range"""
        self._clear_container(self.clients_container)

        try:
            clients = self.analytics_service.client_repo.get_top_clients(limit=10, date_range=date_range)
            self.clients_count_label.configure(text=f"({len(clients)})")

            if not clients:
                NoDataMessage(
                    self.clients_container,
                    "No hay datos de clientes para el rango de fechas seleccionado"
                ).pack(fill="both", expand=True, pady=20)
                return

            for i, c in enumerate(clients):
                self.create_client_card(self.clients_container, c, i)

        except Exception as e:
            self._show_error(self.clients_container, str(e))

    def load_clientes_chart_by_date_range(self, date_range):
        """Load clientes chart for date range"""
        try:
            clients = self.analytics_service.client_repo.get_top_clients(limit=10, date_range=date_range)

            if not clients or len(clients) == 0:
                for widget in self.clientes_chart_container.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(
                    self.clientes_chart_container,
                    text="📊 No hay datos para el rango de fechas seleccionado",
                    font=("Arial", 14),
                    text_color=COLORS['text_secondary']
                ).pack(expand=True)
                return

            client_names = [c.nombre_cliente for c in clients]
            sales = [float(c.total_ventas) for c in clients]

            chart = BarChartComponent(COLORS)
            chart.create(
                labels=client_names,
                values=sales,
                parent=self.clientes_chart_container,
                title="Top 10 Clientes por Ventas",
                xlabel="Total Ventas ($)"
            )

        except Exception as e:
            logger.error(f"Error loading clientes chart by date range: {e}")
            for widget in self.clientes_chart_container.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.clientes_chart_container,
                text=f"❌ Error: {str(e)}",
                font=("Arial", 13),
                text_color=COLORS['danger']
            ).pack(expand=True)

    def load_groups_data_by_date_range(self, date_range):
        """Load groups data filtered by date range"""
        self._clear_container(self.groups_container)

        try:
            groups = self.analytics_service.group_repo.get_groups_summary(date_range=date_range)
            self.groups_count_label.configure(text=f"({len(groups)})")

            if not groups:
                NoDataMessage(
                    self.groups_container,
                    "No hay datos de grupos para el rango de fechas seleccionado"
                ).pack(fill="both", expand=True, pady=20)
                return

            for i, g in enumerate(groups):
                self.create_group_card(self.groups_container, g, i)

        except Exception as e:
            self._show_error(self.groups_container, str(e))

    def load_grupos_chart_by_date_range(self, date_range):
        """Load grupos chart for date range"""
        try:
            groups = self.analytics_service.group_repo.get_groups_summary(date_range=date_range)

            if not groups or len(groups) == 0:
                for widget in self.grupos_chart_container.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(
                    self.grupos_chart_container,
                    text="📊 No hay datos para el rango de fechas seleccionado",
                    font=("Arial", 14),
                    text_color=COLORS['text_secondary']
                ).pack(expand=True)
                return

            sorted_groups = sorted(groups, key=lambda g: float(g.total_ventas), reverse=True)[:10]
            group_names = [g.clave_grupo for g in sorted_groups]
            sales = [float(g.total_ventas) for g in sorted_groups]

            chart = BarChartComponent(COLORS)
            chart.create(
                labels=group_names,
                values=sales,
                parent=self.grupos_chart_container,
                title="Top 10 Grupos por Ventas",
                xlabel="Total Ventas ($)"
            )

        except Exception as e:
            logger.error(f"Error loading grupos chart by date range: {e}")
            for widget in self.grupos_chart_container.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.grupos_chart_container,
                text=f"❌ Error: {str(e)}",
                font=("Arial", 13),
                text_color=COLORS['danger']
            ).pack(expand=True)

    # ========== DATA LOADING ==========
    
    def load_all_data(self):
        """Cargar todos los datos al inicio"""
        try:
            metrics = self.analytics_service.get_overall_metrics()
            self.update_kpis(metrics)

            self.load_products_data()
            self.load_clients_data()
            self.load_groups_data()

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            messagebox.showerror("Error", f"Error cargando datos: {e}")
    
    def update_kpis(self, metrics):
        """Actualizar KPIs del dashboard"""
        total_vendido = float(metrics.total_vendido)
        liquidez = float(metrics.liquidez)
        clientes = metrics.clientes_unicos
        facturas = metrics.total_facturas
        pendiente = float(metrics.total_pendiente)
        total_comprado = float(metrics.total_comprado)

        self.kpi_ventas.update_value(CurrencyFormatter.format(total_vendido))
        self.kpi_liquidez.update_value(CurrencyFormatter.format(liquidez))
        self.kpi_comprado.update_value(CurrencyFormatter.format(total_comprado))
        self.kpi_clientes.update_value(NumberFormatter.format_with_commas(clientes))
        self.kpi_facturas.update_value(NumberFormatter.format_with_commas(facturas))
        self.kpi_pendiente.update_value(CurrencyFormatter.format(pendiente))

        margen = float(metrics.calculate_margin_percentage())
        self.kpi_margen.update_value(NumberFormatter.format_percentage(margen))
    
    def load_products_data(self, period=None):
        """Cargar datos de productos

        Args:
            period: Optional period filter (1D, 7D, 30D, 90D)
        """
        self._clear_container(self.products_container)

        try:
            products = self.analytics_service.get_top_products(limit=10, period=period)
            self.products_count_label.configure(text=f"({len(products)})")

            if not products:
                NoDataMessage(
                    self.products_container,
                    "No hay datos de productos disponibles"
                ).pack(fill="both", expand=True, pady=20)
                return

            for i, p in enumerate(products):
                self.create_product_card(self.products_container, p, i)

        except Exception as e:
            self._show_error(self.products_container, str(e))
    
    def create_product_card(self, parent, product, index):
        """Crear card de producto clickeable"""
        ganancia = float(product.ganancia_total)
        cantidad = float(product.cantidad_vendida)
        unidad = product.unidad_producto
        margen = float(product.margen_ganancia_porcentaje)

        # Build metrics text
        metrics_parts = [f"Vendidas: {NumberFormatter.format_with_commas(cantidad)} {unidad}"]

        if product.precio_venta_promedio:
            precio_venta = float(product.precio_venta_promedio)
            metrics_parts.append(f"P.Venta: {CurrencyFormatter.format(precio_venta)}")

        if product.costo_unitario_promedio:
            costo_unit = float(product.costo_unitario_promedio)
            metrics_parts.append(f"Costo: {CurrencyFormatter.format(costo_unit)}")

        if product.ganancia_por_unidad:
            ganancia_unit = float(product.ganancia_por_unidad)
            metrics_parts.append(f"Gan/U: {CurrencyFormatter.format(ganancia_unit)}")

        metrics_parts.append(f"Margen: {NumberFormatter.format_percentage(margen)}")
        metrics_text = "  •  ".join(metrics_parts)

        # Use ClickableCard component
        card = ClickableCard(
            parent,
            rank=index + 1,
            title=product.nombre_producto,
            value=CurrencyFormatter.format(ganancia),
            value_color=COLORS['success'],
            subtitle=metrics_text,
            on_click=lambda p=product: self.show_product_detail(p)
        )
        card.pack(fill="x", pady=6)

    def show_product_detail(self, product):
        """Mostrar dialog con detalle del producto"""
        try:
            from .product_detail_dialog import ProductDetailDialog
            
            # Convertir producto a dict para el dialog
            product_data = {
                'id_producto': product.id_producto,
                'nombre_producto': product.nombre_producto,
                'unidad_producto': product.unidad_producto,
                'cantidad_vendida': float(product.cantidad_vendida),
                'ingresos_totales': float(product.ingresos_totales),
                'costos_totales': float(product.costos_totales),
                'ganancia_total': float(product.ganancia_total),
                'margen_ganancia_porcentaje': float(product.margen_ganancia_porcentaje),
                'stock': float(product.stock) if product.stock else 0,
            }
            
            ProductDetailDialog(self.root, product_data, self.analytics_service)
        except Exception as e:
            logger.error(f"Error showing product detail: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el detalle del producto:\n{e}")

    def show_debt_details(self):
        """Mostrar dialog con clientes que tienen deudas pendientes"""
        try:
            DebtDetailDialog(self.root, self.analytics_service)
        except Exception as e:
            logger.error(f"Error showing debt details: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el detalle de deudas:\n{e}")
    
    def load_clients_data(self, period=None):
        """Cargar datos de clientes

        Args:
            period: Optional period filter (1D, 7D, 30D, 90D)
        """
        self._clear_container(self.clients_container)

        try:
            clients = self.analytics_service.get_top_clients(limit=10, period=period)
            self.clients_count_label.configure(text=f"({len(clients)})")

            if not clients:
                NoDataMessage(
                    self.clients_container,
                    "No hay datos de clientes disponibles"
                ).pack(fill="both", expand=True, pady=20)
                return

            for i, c in enumerate(clients):
                self.create_client_card(self.clients_container, c, i)

        except Exception as e:
            self._show_error(self.clients_container, str(e))
    
    def create_client_card(self, parent, client, index):
        """Crear card de cliente clickeable"""
        ventas = float(client.total_ventas)
        facturas = client.cantidad_facturas
        pendiente = float(client.saldo_pendiente)
        metrics_text = f"{client.clave_grupo}  •  {client.tipo_cliente}  •  {NumberFormatter.format_with_commas(facturas)} notas  •  Pendiente: {CurrencyFormatter.format(pendiente)}"

        # Use ClickableCard component
        card = ClickableCard(
            parent,
            rank=index + 1,
            title=client.nombre_cliente,
            value=CurrencyFormatter.format(ventas),
            value_color=COLORS['info'],
            subtitle=metrics_text,
            on_click=lambda c=client: self.show_client_detail(c)
        )
        card.pack(fill="x", pady=6)

    def show_client_detail(self, client):
        """Mostrar dialog con detalle del cliente"""
        try:
            from .client_detail_dialog import ClientDetailDialog
            
            # Convertir cliente a dict para el dialog
            client_data = {
                'id_cliente': client.id_cliente,
                'nombre_cliente': client.nombre_cliente,
                'clave_grupo': client.clave_grupo,
                'tipo_cliente': client.tipo_cliente,
                'porcentaje_descuento': float(client.porcentaje_descuento),
                'total_ventas': float(client.total_ventas),
                'cantidad_facturas': client.cantidad_facturas,
                'ultima_compra': client.ultima_compra,
                'saldo_pendiente': float(client.saldo_pendiente),
            }
            
            ClientDetailDialog(self.root, client_data, self.analytics_service)
        except Exception as e:
            logger.error(f"Error showing client detail: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el detalle del cliente:\n{e}")
    
    def load_groups_data(self, period=None):
        """Cargar datos de grupos

        Args:
            period: Optional period filter (1D, 7D, 30D, 90D)
        """
        self._clear_container(self.groups_container)

        try:
            groups = self.analytics_service.get_groups_summary(period=period)
            self.groups_count_label.configure(text=f"({len(groups)})")

            if not groups:
                NoDataMessage(
                    self.groups_container,
                    "No hay datos de grupos disponibles"
                ).pack(fill="both", expand=True, pady=20)
                return

            for i, g in enumerate(groups):
                self.create_group_card(self.groups_container, g, i)

        except Exception as e:
            self._show_error(self.groups_container, str(e))
    
    def create_group_card(self, parent, group, index):
        """Crear card de grupo clickeable"""
        ventas = float(group.total_ventas)
        tipo_cliente = group.tipo_cliente or "N/A"
        clientes = group.cantidad_clientes
        facturas = group.cantidad_facturas
        descuento = float(group.descuento_aplicado)
        metrics_text = f"{tipo_cliente}  •  {NumberFormatter.format_with_commas(clientes)} clientes  •  {NumberFormatter.format_with_commas(facturas)} notas  •  Desc: {NumberFormatter.format_percentage(descuento)}"

        # Use ClickableCard component (sin callback por ahora - grupos no tienen detail dialog)
        card = ClickableCard(
            parent,
            rank=index + 1,
            title=group.clave_grupo,
            value=CurrencyFormatter.format(ventas),
            value_color=COLORS['warning'],
            subtitle=metrics_text,
            on_click=None  # Los grupos no tienen dialog de detalle por ahora
        )
        card.pack(fill="x", pady=6)
    
    # ========== INTERACTIONS ==========
    
    def toggle_sidebar(self):
        """Colapsar/expandir sidebar"""
        if self.sidebar_collapsed:
            self.sidebar.configure(width=220)
            self.sidebar_title.pack(pady=(0, 0))
            for btn in self.nav_buttons.values():
                current_text = btn.cget("text")
                if "  " not in current_text:
                    icon = current_text
                    labels = {
                        "📈": "Dashboard",
                        "📦": "Productos", 
                        "👥": "Clientes",
                        "🏢": "Grupos"
                    }
                    btn.configure(text=f"{icon}  {labels.get(icon, '')}")
        else:
            self.sidebar.configure(width=70)
            self.sidebar_title.pack_forget()
            for btn in self.nav_buttons.values():
                icon = btn.cget("text").split()[0]
                btn.configure(text=icon)
        
        self.sidebar_collapsed = not self.sidebar_collapsed
    
    def switch_to_view(self, view_name):
        """Switch between different views (Dashboard, Productos, Clientes, Grupos)"""
        # Hide all views
        self.dashboard_view.pack_forget()
        self.productos_view.pack_forget()
        self.clientes_view.pack_forget()
        self.grupos_view.pack_forget()

        # Show selected view and load/refresh data
        if view_name == 'dashboard':
            self.dashboard_view.pack(fill="both", expand=True)
        elif view_name == 'productos':
            self.productos_view.pack(fill="both", expand=True)
            # Always load data when switching to view
            self._load_productos_view_data()
        elif view_name == 'clientes':
            self.clientes_view.pack(fill="both", expand=True)
            # Always load data when switching to view
            self._load_clientes_view_data()
        elif view_name == 'grupos':
            self.grupos_view.pack(fill="both", expand=True)
            # Always load data when switching to view
            self._load_grupos_view_data()

        # Update current view and highlight nav button
        self.current_view = view_name
        self._highlight_nav_button(view_name)

    def _load_productos_view_data(self):
        """Load productos view with current date range"""
        from ..domain.models import DateRange
        
        # Get current date range from pickers if available
        if hasattr(self, 'productos_start_date') and hasattr(self, 'productos_end_date'):
            start = self.productos_start_date.get_date()
            end = self.productos_end_date.get_date()
            date_range = DateRange(start_date=start, end_date=end, days=(end-start).days)
        else:
            date_range = DateRange.from_days(30)
        
        self.load_productos_chart_by_date_range(date_range)
        self.load_products_data_by_date_range(date_range)

    def _load_clientes_view_data(self):
        """Load clientes view with current date range"""
        from ..domain.models import DateRange
        
        if hasattr(self, 'clientes_start_date') and hasattr(self, 'clientes_end_date'):
            start = self.clientes_start_date.get_date()
            end = self.clientes_end_date.get_date()
            date_range = DateRange(start_date=start, end_date=end, days=(end-start).days)
        else:
            date_range = DateRange.from_days(30)
        
        self.load_clientes_chart_by_date_range(date_range)
        self.load_clients_data_by_date_range(date_range)

    def _load_grupos_view_data(self):
        """Load grupos view with current date range"""
        from ..domain.models import DateRange
        
        if hasattr(self, 'grupos_start_date') and hasattr(self, 'grupos_end_date'):
            start = self.grupos_start_date.get_date()
            end = self.grupos_end_date.get_date()
            date_range = DateRange(start_date=start, end_date=end, days=(end-start).days)
        else:
            date_range = DateRange.from_days(30)
        
        self.load_grupos_chart_by_date_range(date_range)
        self.load_groups_data_by_date_range(date_range)

    def _highlight_nav_button(self, active_section):
        """Resaltar botón de navegación activo"""
        for section_id, btn in self.nav_buttons.items():
            if section_id == active_section:
                btn.configure(
                    fg_color=COLORS['accent'],
                    text_color=COLORS['text_primary']
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS['text_secondary']
                )

    def _smooth_scroll_to(self, widget):
        """Helper para scroll suave - DEPRECATED, keeping for compatibility"""
        try:
            widget_y = widget.winfo_y()
            canvas = self.scroll_frame._parent_canvas
            
            canvas_height = canvas.winfo_height()
            scrollregion = canvas.cget("scrollregion").split()
            total_height = int(scrollregion[3]) if len(scrollregion) > 3 else 1000
            
            scroll_pos = widget_y / total_height
            canvas.yview_moveto(scroll_pos)
        except:
            pass
    
    def on_global_search(self, event):
        """Búsqueda global en todas las secciones"""
        query = self.global_search.get().strip().lower()
        
        if not query or len(query) < 2:
            return
        
        # Buscar en la vista actual
        try:
            if self.current_view == 'productos':
                results = self.analytics_service.search_products(query, limit=20)
                self._display_search_results_products(results)
            elif self.current_view == 'clientes':
                results = self.analytics_service.search_clients(query, limit=20)
                self._display_search_results_clients(results)
        except Exception as e:
            logger.error(f"Error en búsqueda global: {e}")
    
    def _display_search_results_products(self, products):
        """Mostrar resultados de búsqueda de productos"""
        self._clear_container(self.products_container)
        self.products_count_label.configure(text=f"({len(products)})")
        
        if not products:
            NoDataMessage(
                self.products_container,
                "No se encontraron productos"
            ).pack(fill="both", expand=True, pady=20)
            return
        
        for i, p in enumerate(products):
            self.create_product_card(self.products_container, p, i)
    
    def _display_search_results_clients(self, clients):
        """Mostrar resultados de búsqueda de clientes"""
        self._clear_container(self.clients_container)
        self.clients_count_label.configure(text=f"({len(clients)})")
        
        if not clients:
            NoDataMessage(
                self.clients_container,
                "No se encontraron clientes"
            ).pack(fill="both", expand=True, pady=20)
            return
        
        for i, c in enumerate(clients):
            self.create_client_card(self.clients_container, c, i)
    
    def refresh_all(self):
        """Refrescar todos los datos"""
        try:
            self.analytics_service.refresh_cache()
            self.load_all_data()
            self.load_chart()

            now = datetime.now().strftime("%H:%M")
            messagebox.showinfo("Actualizado", f"Datos actualizados a las {now}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {e}")
    
    def change_export_directory(self):
        """Cambiar carpeta de exportación"""
        if self.export_manager.ask_and_set_output_directory(self.root):
            messagebox.showinfo(
                "Carpeta actualizada",
                f"Las exportaciones se guardarán en:\n{self.export_manager.get_output_directory()}"
            )

    def export_to_pdf(self):
        """Abrir diálogo de exportación"""
        # Check if this is the first export (no saved directory)
        import os
        config_file = os.path.join(os.path.expanduser("~"), ".disfruleg_export_config.json")

        if not os.path.exists(config_file):
            # First time export - ask for directory
            result = messagebox.askyesno(
                "Seleccionar carpeta de exportación",
                "¿Deseas elegir una carpeta para guardar las exportaciones?\n\n"
                "Si seleccionas 'No', se usará la carpeta de Descargas por defecto.",
                icon='question'
            )

            if result:
                # User wants to choose directory
                if not self.export_manager.ask_and_set_output_directory(self.root):
                    # User cancelled - use default
                    messagebox.showinfo(
                        "Carpeta por defecto",
                        f"Se usará la carpeta de Descargas:\n{self.export_manager.get_output_directory()}"
                    )
            else:
                # Save default directory to config
                self.export_manager._save_directory(self.export_manager.get_output_directory())

        # All sections are always available since we fetch data on-demand
        # Crear diálogo de exportación
        dialog = ExportDialog(
            self.root,
            export_callback=self._execute_export,
            has_dashboard=True,  # Always available
            has_products=True,   # Always available
            has_clients=True,    # Always available
            has_groups=True      # Always available
        )
        self.root.wait_window(dialog)
        
        if dialog.result:
            import subprocess
            import platform
            
            # Abrir archivo o carpeta
            try:
                filepath = dialog.result
                if platform.system() == 'Windows':
                    os.startfile(os.path.dirname(filepath))
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.Popen(['open', os.path.dirname(filepath)])
                else:  # Linux
                    subprocess.Popen(['xdg-open', os.path.dirname(filepath)])
            except:
                messagebox.showinfo(
                    "Exportación Completada",
                    f"Archivo guardado en:\n{filepath}"
                )
    
    def _execute_export(self, options: Dict) -> Tuple[bool, str]:
        """
        ✅ Ejecutar exportación según opciones seleccionadas
        Soporta PDF, Excel o ambos formatos con filtrado por fecha
        """
        try:
            format_type = options['format']
            sections = options['sections']
            include_charts = options['include_charts']
            filename = options['filename']
            start_date = options.get('start_date')
            end_date = options.get('end_date')

            # Convert dates to DateRange if provided
            date_range = None
            if start_date and end_date:
                from ..domain.models import DateRange
                date_range = DateRange(
                    start_date=datetime.combine(start_date, datetime.min.time()),
                    end_date=datetime.combine(end_date, datetime.max.time()),
                    days=(end_date - start_date).days
                )

            # Preparar datos con filtro de fecha
            dashboard_data = self._prepare_export_data(sections, include_charts, date_range)

            # Exportar según formato
            results = []

            if format_type in ['pdf', 'both']:
                if sections.get('dashboard'):
                    success, path = self.export_manager.export_dashboard_pdf(dashboard_data)
                    results.append((success, path))

                if sections.get('products') and dashboard_data.get('top_products'):
                    success, path = self.export_manager.export_products_report_pdf(
                        dashboard_data['top_products']
                    )
                    results.append((success, path))

                if sections.get('clients') and dashboard_data.get('top_clients'):
                    success, path = self.export_manager.export_clients_report_pdf(
                        dashboard_data['top_clients']
                    )
                    results.append((success, path))

            if format_type in ['excel', 'both']:
                success, path = self.export_manager.export_dashboard_excel(dashboard_data)
                results.append((success, path))

            # Verificar resultados
            successful = [r for r in results if r[0]]
            if successful:
                return True, successful[0][1]
            else:
                return False, "Error en la exportación"

        except Exception as e:
            logger.error(f"Error en exportación: {e}")
            return False, str(e)
    
    def _prepare_export_data(self, sections: Dict, include_charts: bool, date_range=None) -> Dict:
        """
        Preparar datos para exportación con filtro de fecha opcional

        Args:
            sections: Dict con las secciones a exportar
            include_charts: Si incluir gráficos
            date_range: DateRange opcional para filtrar datos
        """
        export_data = {}

        # Add date range info if available
        if date_range:
            start_str = date_range.start_date.strftime('%d/%m/%Y')
            end_str = date_range.end_date.strftime('%d/%m/%Y')
            export_data['date_range'] = f"{start_str} - {end_str}"

        # KPIs - Siempre usar datos actuales del dashboard
        if sections.get('dashboard'):
            try:
                metrics = self.analytics_service.get_overall_metrics()
                export_data['kpis'] = {
                    'total_ganancia': float(metrics.liquidez),
                    'total_ingresos': float(metrics.total_vendido),
                    'total_costos': float(metrics.total_comprado),
                    'margen_promedio': float(metrics.calculate_margin_percentage())
                }
            except Exception as e:
                logger.error(f"Error getting KPIs for export: {e}")

        # Productos - Usar date_range si está disponible
        if sections.get('products'):
            try:
                if date_range:
                    products = self.analytics_service.product_repo.get_top_products(limit=20, date_range=date_range)
                else:
                    products = self.analytics_service.get_top_products(limit=20)

                # Convert to dict format for export
                export_data['top_products'] = [
                    {
                        'nombre_producto': p.nombre_producto,
                        'cantidad_vendida': float(p.cantidad_vendida),
                        'ganancia_total': float(p.ganancia_total),
                        'margen_ganancia_porcentaje': float(p.margen_ganancia_porcentaje)
                    }
                    for p in products
                ]
            except Exception as e:
                logger.error(f"Error getting products for export: {e}")

        # Clientes - Usar date_range si está disponible
        if sections.get('clients'):
            try:
                if date_range:
                    clients = self.analytics_service.client_repo.get_top_clients(limit=20, date_range=date_range)
                else:
                    clients = self.analytics_service.get_top_clients(limit=20)

                # Convert to dict format for export
                export_data['top_clients'] = [
                    {
                        'nombre_cliente': c.nombre_cliente,
                        'numero_compras': c.cantidad_facturas,
                        'gasto_total': float(c.total_ventas),
                        'ticket_promedio': float(c.total_ventas) / c.cantidad_facturas if c.cantidad_facturas > 0 else 0
                    }
                    for c in clients
                ]
            except Exception as e:
                logger.error(f"Error getting clients for export: {e}")

        # Grupos - Usar date_range si está disponible
        if sections.get('groups'):
            try:
                if date_range:
                    groups = self.analytics_service.group_repo.get_groups_summary(date_range=date_range)
                else:
                    groups = self.analytics_service.get_groups_summary()

                # Convert to dict format for export
                export_data['group_summary'] = [
                    {
                        'nombre_grupo': g.clave_grupo,
                        'ingresos': float(g.total_ventas),
                        'ganancias': float(g.total_ventas)  # Adjust if you have actual profit data
                    }
                    for g in groups
                ]
            except Exception as e:
                logger.error(f"Error getting groups for export: {e}")

        # Gráfico (si está disponible y se solicita)
        if include_charts and hasattr(self, 'last_chart_image'):
            export_data['chart_image'] = self.last_chart_image

        return export_data
    
    # ========== UTILITIES ==========
    
    def _clear_container(self, container):
        """Limpiar contenedor"""
        for widget in container.winfo_children():
            widget.destroy()
    
    def _show_error(self, container, error):
        """Mostrar error en contenedor"""
        self._clear_container(container)
        ctk.CTkLabel(
            container,
            text=f"❌ Error: {error}",
            font=("Arial", 13),
            text_color=COLORS['danger']
        ).pack(expand=True, pady=20)
    
    def on_closing(self):
        """Cerrar aplicación con limpieza"""
        try:
            self._cleanup_responsive()
        except Exception as e:
            logger.error(f"Error en on_closing: {e}")
        finally:
            self.root.destroy()


# This function has been moved to analytics_launcher.py


def _bring_to_front(window, is_mac=False):
    """Helper para traer ventana al frente (optimizado Mac/Windows)"""
    try:
        if is_mac:
            window.withdraw()
            window.deiconify()
            window.lift()
            window.attributes('-topmost', True)
            window.update_idletasks()
            window.after(100, lambda: window.attributes('-topmost', False))
            window.focus_force()
            window.after(200, lambda: _mac_focus_retry(window))
        else:
            window.lift()
            window.attributes('-topmost', True)
            window.update()
            window.after(50, lambda: window.attributes('-topmost', False))
            window.focus_force()
            
    except Exception as e:
        logger.error(f"Error bringing window to front: {e}")


def _mac_focus_retry(window):
    """Reintento adicional para macOS"""
    try:
        window.lift()
        window.focus_force()
        
        current_geo = window.geometry()
        if 'x' in current_geo and 'y' in current_geo:
            parts = current_geo.split('+')
            if len(parts) == 3:
                x, y = int(parts[1]), int(parts[2])
                window.geometry(f"+{x}+{y-1}")
                window.after(10, lambda: window.geometry(f"+{x}+{y}"))
    except:
        pass


if __name__ == "__main__":
    """
    Standalone testing - Use analytics_launcher.py for production
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.title("Análisis de Ventas - Disfruleg")

    # Mock user data for testing
    user_data = {
        'nombre_completo': 'Usuario Prueba',
        'rol': 'admin'
    }

    try:
        from src.database.conexion import conectar
        from ..business import AnalyticsService
        from ..data import (
            MySQLAnalyticsRepository,
            MySQLProductAnalyticsRepository,
            MySQLClientAnalyticsRepository,
            MySQLGroupAnalyticsRepository,
            MySQLSalesTrendRepository,
            InMemoryCacheRepository
        )

        # Establish database connection
        conn = conectar()

        # Initialize repositories
        analytics_repo = MySQLAnalyticsRepository(conn)
        product_repo = MySQLProductAnalyticsRepository(conn)
        client_repo = MySQLClientAnalyticsRepository(conn)
        group_repo = MySQLGroupAnalyticsRepository(conn)
        sales_trend_repo = MySQLSalesTrendRepository(conn)
        cache_repo = InMemoryCacheRepository(default_ttl=300)

        # Initialize service with dependency injection
        analytics_service = AnalyticsService(
            analytics_repo=analytics_repo,
            product_repo=product_repo,
            client_repo=client_repo,
            group_repo=group_repo,
            sales_trend_repo=sales_trend_repo,
            cache_repo=cache_repo
        )

        # Initialize UI with service
        app = AnalisisGananciasApp(root, user_data, analytics_service)
        app.conn = conn

        root.mainloop()

    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n{e}")
        root.destroy()