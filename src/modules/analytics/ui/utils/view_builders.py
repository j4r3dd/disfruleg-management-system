# -*- coding: utf-8 -*-
"""
View Builders for Analytics Module
Reusable builders for creating common UI sections using the Builder Pattern
"""
import customtkinter as ctk
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DashboardViewBuilder:
    """
    Builder for creating Dashboard KPI sections

    Follows the Builder Pattern to construct complex KPI grids with:
    - Section header with title and timestamp
    - Multiple rows of KPI cards
    - Flexible layout configuration

    Usage:
        builder = DashboardViewBuilder(parent, colors)
        builder.set_title("📊 Dashboard General")
        builder.add_kpi_row([
            ("Total Vendido", "$0.00", "💰", colors['success']),
            ("Liquidez", "$0.00", "💧", colors['info'])
        ])
        section = builder.build()
    """

    def __init__(self, parent, colors: Dict, section_id: str = "dashboard"):
        """
        Initialize dashboard builder

        Args:
            parent: Parent CTkFrame
            colors: Color scheme dictionary
            section_id: Unique identifier for the section
        """
        self.parent = parent
        self.colors = colors
        self.section_id = section_id

        # Builder state
        self.title = "📊 Dashboard"
        self.show_timestamp = True
        self.kpi_rows = []
        self.kpi_widgets = {}  # Store references to KPI widgets

    def set_title(self, title: str) -> 'DashboardViewBuilder':
        """Set section title"""
        self.title = title
        return self

    def set_timestamp_visible(self, visible: bool) -> 'DashboardViewBuilder':
        """Set whether to show timestamp"""
        self.show_timestamp = visible
        return self

    def add_kpi_row(
        self,
        kpis: List[tuple],
        row_name: Optional[str] = None
    ) -> 'DashboardViewBuilder':
        """
        Add a row of KPI cards

        Args:
            kpis: List of KPI tuples (label, default_value, icon, color, on_click)
                  on_click is optional
            row_name: Optional name for this row (for widget references)

        Returns:
            Self for method chaining
        """
        self.kpi_rows.append((kpis, row_name))
        return self

    def build(self, StatCard) -> ctk.CTkFrame:
        """
        Build the dashboard section

        Args:
            StatCard: StatCard component class to use for KPIs

        Returns:
            Configured CTkFrame containing the dashboard
        """
        from .formatters import DateFormatter

        # Main section container
        section = ctk.CTkFrame(self.parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 40))
        section._section_id = self.section_id

        # Header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text=self.title,
            font=("Arial", 24, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")

        if self.show_timestamp:
            now = datetime.now().strftime("%H:%M")
            ctk.CTkLabel(
                header,
                text=f"Actualizado: {now}",
                font=("Arial", 12),
                text_color=self.colors['text_secondary']
            ).pack(side="right")

        # KPI Grid
        kpi_grid = ctk.CTkFrame(section, fg_color="transparent")
        kpi_grid.pack(fill="x")

        # Build each row
        for row_idx, (kpis, row_name) in enumerate(self.kpi_rows):
            row = ctk.CTkFrame(kpi_grid, fg_color="transparent")

            # Add padding between rows except for the last one
            if row_idx < len(self.kpi_rows) - 1:
                row.pack(fill="x", pady=(0, 12))
            else:
                row.pack(fill="x")

            # Build each KPI in the row
            for kpi_idx, kpi_data in enumerate(kpis):
                # Unpack KPI data (handle optional on_click)
                if len(kpi_data) == 4:
                    label, default_value, icon, color = kpi_data
                    on_click = None
                elif len(kpi_data) == 5:
                    label, default_value, icon, color, on_click = kpi_data
                else:
                    logger.warning(f"Invalid KPI data: {kpi_data}")
                    continue

                # Create KPI card
                kpi = StatCard(
                    row, label, default_value, icon,
                    color=color,
                    on_click=on_click
                )

                # Add padding except for last item
                if kpi_idx < len(kpis) - 1:
                    kpi.pack(side="left", fill="both", expand=True, padx=(0, 12))
                else:
                    kpi.pack(side="left", fill="both", expand=True)

                # Store widget reference
                widget_key = f"{row_name}_{kpi_idx}" if row_name else f"kpi_{row_idx}_{kpi_idx}"
                self.kpi_widgets[widget_key] = kpi

        # Store widget references on section for external access
        section._kpi_widgets = self.kpi_widgets

        return section

    def get_kpi_widget(self, key: str):
        """Get a KPI widget by its key"""
        return self.kpi_widgets.get(key)


class RankingViewBuilder:
    """
    Builder for creating Ranking/Listing views

    Creates views with:
    - Header with title and count
    - Filter bar with period buttons
    - Chart section
    - Item list container

    Usage:
        builder = RankingViewBuilder(parent, colors)
        builder.set_title("📦 Top Productos", "products_count")
        builder.set_filters(["1D", "7D", "30D", "90D"], "30D", change_callback)
        builder.set_chart_height(300)
        view, refs = builder.build()
    """

    def __init__(self, parent, colors: Dict):
        """
        Initialize ranking view builder

        Args:
            parent: Parent container
            colors: Color scheme dictionary
        """
        self.parent = parent
        self.colors = colors

        # Builder state
        self.title = "📊 Ranking"
        self.count_label_key = None
        self.filter_periods = []
        self.default_period = "30D"
        self.filter_callback = None
        self.chart_height = 300
        self.show_chart = True

    def set_title(self, title: str, count_label_key: Optional[str] = None) -> 'RankingViewBuilder':
        """
        Set view title

        Args:
            title: Title text (e.g., "📦 Top Productos")
            count_label_key: Key for storing count label reference

        Returns:
            Self for method chaining
        """
        self.title = title
        self.count_label_key = count_label_key
        return self

    def set_filters(
        self,
        periods: List[str],
        default_period: str,
        callback: Callable
    ) -> 'RankingViewBuilder':
        """
        Configure filter bar

        Args:
            periods: List of period strings (e.g., ["1D", "7D", "30D"])
            default_period: Default selected period
            callback: Function to call when period changes

        Returns:
            Self for method chaining
        """
        self.filter_periods = periods
        self.default_period = default_period
        self.filter_callback = callback
        return self

    def set_chart_height(self, height: int) -> 'RankingViewBuilder':
        """Set chart section height"""
        self.chart_height = height
        return self

    def set_chart_visible(self, visible: bool) -> 'RankingViewBuilder':
        """Set whether chart section is visible"""
        self.show_chart = visible
        return self

    def build(self) -> tuple[ctk.CTkScrollableFrame, Dict]:
        """
        Build the ranking view

        Returns:
            Tuple of (view_frame, widget_references)
            widget_references contains:
                - count_label: Label for item count
                - period_buttons: Dict of period filter buttons
                - chart_container: Container for chart
                - items_container: Container for item cards
        """
        # Main scrollable view
        view = ctk.CTkScrollableFrame(
            self.parent,
            fg_color=self.colors['primary']
        )

        content = ctk.CTkFrame(view, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)

        # Header with title and count
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text=self.title,
            font=("Arial", 28, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")

        count_label = None
        if self.count_label_key:
            count_label = ctk.CTkLabel(
                header,
                text="(0)",
                font=("Arial", 18),
                text_color=self.colors['text_secondary']
            )
            count_label.pack(side="left", padx=(10, 0))

        # Filter bar (if configured)
        period_buttons = {}
        if self.filter_periods:
            filters_frame = ctk.CTkFrame(
                content,
                fg_color=self.colors['surface'],
                corner_radius=12
            )
            filters_frame.pack(fill="x", pady=(0, 20))

            filter_content = ctk.CTkFrame(filters_frame, fg_color="transparent")
            filter_content.pack(fill="x", padx=20, pady=15)

            ctk.CTkLabel(
                filter_content,
                text="📅 Filtrar por período:",
                font=("Arial", 14, "bold"),
                text_color=self.colors['text_primary']
            ).pack(side="left", padx=(0, 15))

            for period in self.filter_periods:
                btn = ctk.CTkButton(
                    filter_content,
                    text=period,
                    width=60,
                    height=36,
                    font=("Arial", 13),
                    fg_color=self.colors['accent'] if period == self.default_period else "transparent",
                    hover_color=self.colors['accent'],
                    border_width=1,
                    border_color=self.colors['accent'],
                    command=lambda p=period: self.filter_callback(p) if self.filter_callback else None
                )
                btn.pack(side="left", padx=4)
                period_buttons[period] = btn

        # Chart section (if enabled)
        chart_container = None
        if self.show_chart:
            chart_section = ctk.CTkFrame(
                content,
                fg_color=self.colors['card_bg'],
                corner_radius=12,
                height=self.chart_height
            )
            chart_section.pack(fill="both", pady=(0, 20))
            chart_section.pack_propagate(False)

            chart_container = ctk.CTkFrame(chart_section, fg_color="transparent")
            chart_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Items container
        items_container = ctk.CTkFrame(content, fg_color="transparent")
        items_container.pack(fill="x", pady=(0, 0))

        # Return view and widget references
        refs = {
            'count_label': count_label,
            'period_buttons': period_buttons,
            'chart_container': chart_container,
            'items_container': items_container
        }

        return view, refs


class FilterBarBuilder:
    """
    Builder for creating filter bars with period selection

    Creates a styled filter bar with:
    - Label text
    - Period buttons
    - Active state management

    Usage:
        builder = FilterBarBuilder(parent, colors)
        builder.set_label("📅 Periodo:")
        builder.add_periods(["1D", "7D", "30D"], "7D", callback)
        filter_bar, buttons = builder.build()
    """

    def __init__(self, parent, colors: Dict):
        """
        Initialize filter bar builder

        Args:
            parent: Parent container
            colors: Color scheme dictionary
        """
        self.parent = parent
        self.colors = colors

        # Builder state
        self.label_text = "📅 Filtrar:"
        self.periods = []
        self.default_period = None
        self.callback = None

    def set_label(self, text: str) -> 'FilterBarBuilder':
        """Set filter label text"""
        self.label_text = text
        return self

    def add_periods(
        self,
        periods: List[str],
        default: str,
        callback: Callable
    ) -> 'FilterBarBuilder':
        """
        Add period filter buttons

        Args:
            periods: List of period strings
            default: Default selected period
            callback: Function to call on period change

        Returns:
            Self for method chaining
        """
        self.periods = periods
        self.default_period = default
        self.callback = callback
        return self

    def build(self) -> tuple[ctk.CTkFrame, Dict]:
        """
        Build the filter bar

        Returns:
            Tuple of (filter_frame, period_buttons_dict)
        """
        # Main filter frame
        filters_frame = ctk.CTkFrame(
            self.parent,
            fg_color=self.colors['surface'],
            corner_radius=12
        )

        filter_content = ctk.CTkFrame(filters_frame, fg_color="transparent")
        filter_content.pack(fill="x", padx=20, pady=15)

        # Label
        ctk.CTkLabel(
            filter_content,
            text=self.label_text,
            font=("Arial", 14, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left", padx=(0, 15))

        # Period buttons
        period_buttons = {}
        for period in self.periods:
            btn = ctk.CTkButton(
                filter_content,
                text=period,
                width=60,
                height=36,
                font=("Arial", 13),
                fg_color=self.colors['accent'] if period == self.default_period else "transparent",
                hover_color=self.colors['accent'],
                border_width=1,
                border_color=self.colors['accent'],
                command=lambda p=period: self.callback(p) if self.callback else None
            )
            btn.pack(side="left", padx=4)
            period_buttons[period] = btn

        return filters_frame, period_buttons
