# -*- coding: utf-8 -*-
"""
Dialog Components for Analytics Module
Reusable components for detail dialogs (Product, Client, etc.)
"""
import customtkinter as ctk
from typing import Dict, List, Optional, Callable, Tuple
import logging

logger = logging.getLogger(__name__)


class DetailDialogBase(ctk.CTkToplevel):
    """
    Base class for detail dialogs with common functionality

    Provides:
    - Window setup and configuration
    - Centering functionality
    - Common color scheme
    - Scrollable main container
    - Standard layout structure

    Usage:
        class MyDetailDialog(DetailDialogBase):
            def __init__(self, parent, data):
                super().__init__(parent, title="My Dialog", width=1000, height=750)
                self.data = data
                self.create_content()
    """

    def __init__(
        self,
        parent,
        title: str = "Detail",
        width: int = 1000,
        height: int = 750,
        colors: Optional[Dict] = None
    ):
        """
        Initialize base dialog

        Args:
            parent: Parent window
            title: Dialog title
            width: Window width
            height: Window height
            colors: Custom color scheme (optional)
        """
        super().__init__(parent)

        self.title(title)
        self.geometry(f"{width}x{height}")

        # Default color scheme (can be overridden)
        self.colors = colors or {
            'bg_primary': '#0A0A0A',
            'bg_secondary': '#1A1A1A',
            'bg_card': '#242424',
            'bg_surface': '#2E2E2E',
            'accent': '#8B5CF6',
            'accent_secondary': '#3B82F6',
            'success': '#10B981',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'info': '#3B82F6',
            'text_primary': '#F5F5F5',
            'text_secondary': '#A1A1A1',
            'text_muted': '#6B6B6B',
        }

        self.configure(fg_color=self.colors['bg_primary'])

        # Fix transparency issues on macOS
        try:
            self.attributes('-alpha', 1.0)
        except:
            pass

        # Create main scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.colors['bg_primary']
        )
        self.scroll_frame.pack(fill="both", expand=True)

        self.content = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=30, pady=30)

        # Center window and bring to front
        self.after(100, self._finalize_setup)

    def _finalize_setup(self):
        """Finalize window setup after initial render"""
        self.center_window()
        self.lift()
        self.focus_force()

    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')


class KPIGrid:
    """
    Component for creating KPI grids in dialogs

    Creates a grid of KPI cards with consistent styling:
    - Configurable rows and columns
    - Responsive layout
    - Custom colors per KPI
    - Professional card design

    Usage:
        grid = KPIGrid(parent, colors)
        grid.add_kpis([
            ("Label", "Value", color),
            ("Label2", "Value2", color2)
        ], columns=3)
        grid.build()
    """

    def __init__(self, parent, colors: Dict):
        """
        Initialize KPI grid

        Args:
            parent: Parent container
            colors: Color scheme dictionary
        """
        self.parent = parent
        self.colors = colors
        self.kpis = []
        self.columns = 3

    def add_kpis(self, kpis: List[Tuple[str, str, str]], columns: int = 3):
        """
        Add KPIs to the grid

        Args:
            kpis: List of (label, value, color) tuples
            columns: Number of columns per row
        """
        self.kpis = kpis
        self.columns = columns
        return self

    def build(self) -> ctk.CTkFrame:
        """
        Build and return the KPI grid

        Returns:
            CTkFrame containing the KPI grid
        """
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="x", pady=(0, 20))

        # Calculate number of rows needed
        num_rows = (len(self.kpis) + self.columns - 1) // self.columns

        # Create rows
        for row_idx in range(num_rows):
            row = ctk.CTkFrame(container, fg_color="transparent")

            # Add padding between rows except last
            if row_idx < num_rows - 1:
                row.pack(fill="x", pady=(0, 12))
            else:
                row.pack(fill="x")

            # Add KPIs to this row
            start_idx = row_idx * self.columns
            end_idx = min(start_idx + self.columns, len(self.kpis))

            for col_idx, kpi_idx in enumerate(range(start_idx, end_idx)):
                label, value, color = self.kpis[kpi_idx]

                card = self._create_kpi_card(row, label, value, color)

                # Add padding except for last item in row
                is_last_in_row = (col_idx == (end_idx - start_idx - 1))
                card.pack(
                    side="left",
                    fill="both",
                    expand=True,
                    padx=(0, 0 if is_last_in_row else 12)
                )

        return container

    def _create_kpi_card(
        self,
        parent,
        label: str,
        value: str,
        color: str
    ) -> ctk.CTkFrame:
        """
        Create individual KPI card

        Args:
            parent: Parent container
            label: KPI label
            value: KPI value
            color: Value text color

        Returns:
            Configured KPI card frame
        """
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_card'],
            corner_radius=8,
            height=90
        )
        card.pack_propagate(False)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(expand=True, padx=15, pady=10)

        ctk.CTkLabel(
            content,
            text=label,
            font=("Arial", 12),
            text_color=self.colors['text_secondary']
        ).pack(anchor="w")

        ctk.CTkLabel(
            content,
            text=value,
            font=("Arial", 20, "bold"),
            text_color=color
        ).pack(anchor="w", pady=(8, 0))

        return card


class FilterPanel:
    """
    Component for creating filter panels in dialogs

    Creates a styled filter panel with:
    - Period selection buttons
    - Metric selection buttons
    - Comparison toggles
    - Custom callbacks

    Usage:
        panel = FilterPanel(parent, colors)
        panel.add_period_filter(["1D", "7D", "30D"], "30D", callback)
        panel.add_metric_filter(["cantidad", "ventas"], "cantidad", callback)
        panel_frame, refs = panel.build()
    """

    def __init__(self, parent, colors: Dict):
        """
        Initialize filter panel

        Args:
            parent: Parent container
            colors: Color scheme dictionary
        """
        self.parent = parent
        self.colors = colors

        # Filter configurations
        self.periods = []
        self.default_period = None
        self.period_callback = None

        self.metrics = []
        self.default_metric = None
        self.metric_callback = None

        self.has_comparison = False
        self.comparison_callback = None

    def add_period_filter(
        self,
        periods: List[str],
        default: str,
        callback: Callable
    ):
        """Add period filter"""
        self.periods = periods
        self.default_period = default
        self.period_callback = callback
        return self

    def add_metric_filter(
        self,
        metrics: List[Tuple[str, str]],  # (value, label)
        default: str,
        callback: Callable
    ):
        """Add metric filter"""
        self.metrics = metrics
        self.default_metric = default
        self.metric_callback = callback
        return self

    def add_comparison_toggle(self, callback: Callable):
        """Add comparison toggle"""
        self.has_comparison = True
        self.comparison_callback = callback
        return self

    def build(self) -> Tuple[ctk.CTkFrame, Dict]:
        """
        Build and return the filter panel

        Returns:
            Tuple of (panel_frame, widget_references)
        """
        # Main filter panel
        panel = ctk.CTkFrame(
            self.parent,
            fg_color=self.colors['bg_surface'],
            corner_radius=12
        )
        panel.pack(fill="x", pady=(0, 20))

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)

        refs = {}

        # Period filter
        if self.periods:
            period_section = self._create_period_section(content)
            refs['period_buttons'] = period_section

        # Metric filter
        if self.metrics:
            metric_section = self._create_metric_section(content)
            refs['metric_buttons'] = metric_section

        # Comparison toggle
        if self.has_comparison:
            toggle = self._create_comparison_toggle(content)
            refs['comparison_toggle'] = toggle

        return panel, refs

    def _create_period_section(self, parent) -> Dict:
        """Create period filter section"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(
            section,
            text="📅 Período:",
            font=("Arial", 13, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left", padx=(0, 10))

        buttons = {}
        for period in self.periods:
            btn = ctk.CTkButton(
                section,
                text=period,
                width=50,
                height=32,
                font=("Arial", 12),
                fg_color=self.colors['accent'] if period == self.default_period else "transparent",
                hover_color=self.colors['accent'],
                border_width=1,
                border_color=self.colors['accent'],
                command=lambda p=period: self.period_callback(p) if self.period_callback else None
            )
            btn.pack(side="left", padx=3)
            buttons[period] = btn

        return buttons

    def _create_metric_section(self, parent) -> Dict:
        """Create metric filter section"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(
            section,
            text="📊 Métrica:",
            font=("Arial", 13, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left", padx=(0, 10))

        buttons = {}
        for metric_value, metric_label in self.metrics:
            btn = ctk.CTkButton(
                section,
                text=metric_label,
                width=80,
                height=32,
                font=("Arial", 12),
                fg_color=self.colors['accent'] if metric_value == self.default_metric else "transparent",
                hover_color=self.colors['accent'],
                border_width=1,
                border_color=self.colors['accent'],
                command=lambda m=metric_value: self.metric_callback(m) if self.metric_callback else None
            )
            btn.pack(side="left", padx=3)
            buttons[metric_value] = btn

        return buttons

    def _create_comparison_toggle(self, parent) -> ctk.CTkCheckBox:
        """Create comparison toggle"""
        toggle = ctk.CTkCheckBox(
            parent,
            text="Comparar con período anterior",
            font=("Arial", 12),
            text_color=self.colors['text_primary'],
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent'],
            command=lambda: self.comparison_callback() if self.comparison_callback else None
        )
        toggle.pack(side="left")
        return toggle


class ChartSection:
    """
    Component for creating chart sections in dialogs

    Creates a styled container for charts with:
    - Consistent card styling
    - Fixed or flexible height
    - Loading state support
    - Error state support

    Usage:
        section = ChartSection(parent, colors, height=400)
        container = section.build()
        # Add chart to container
    """

    def __init__(self, parent, colors: Dict, height: Optional[int] = 350):
        """
        Initialize chart section

        Args:
            parent: Parent container
            colors: Color scheme dictionary
            height: Fixed height (None for flexible)
        """
        self.parent = parent
        self.colors = colors
        self.height = height
        self.title = None

    def set_title(self, title: str):
        """Set chart section title"""
        self.title = title
        return self

    def build(self) -> ctk.CTkFrame:
        """
        Build and return the chart section

        Returns:
            CTkFrame that can contain a chart
        """
        # Outer frame with card styling
        section = ctk.CTkFrame(
            self.parent,
            fg_color=self.colors['bg_card'],
            corner_radius=12
        )

        if self.height:
            section.configure(height=self.height)
            section.pack(fill="both", pady=(0, 20))
            section.pack_propagate(False)
        else:
            section.pack(fill="both", expand=True, pady=(0, 20))

        # Title (if provided)
        if self.title:
            title_frame = ctk.CTkFrame(section, fg_color="transparent")
            title_frame.pack(fill="x", padx=20, pady=(15, 5))

            ctk.CTkLabel(
                title_frame,
                text=self.title,
                font=("Arial", 16, "bold"),
                text_color=self.colors['text_primary']
            ).pack(side="left")

        # Chart container
        container = ctk.CTkFrame(section, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        return container
