# -*- coding: utf-8 -*-
"""
Chart Components for Analytics Module
Reusable matplotlib chart components with consistent styling
"""
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BaseChartComponent:
    """Base class for all matplotlib charts with consistent dark theme styling"""

    def __init__(self, colors: dict):
        """
        Initialize base chart component

        Args:
            colors: Dictionary with theme colors (bg_card, text_primary, text_secondary, accent, etc.)
        """
        self.colors = colors

    def apply_dark_theme(self, ax, fig):
        """
        Apply consistent dark theme to chart axes and figure

        Args:
            ax: Matplotlib axes object
            fig: Matplotlib figure object
        """
        # Background colors
        ax.set_facecolor(self.colors.get('bg_card', '#242424'))
        fig.patch.set_facecolor(self.colors.get('bg_card', '#242424'))

        # Tick styling
        ax.tick_params(
            colors=self.colors.get('text_secondary', '#A1A1A1'),
            labelsize=9
        )

        # Spine styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.colors.get('text_secondary', '#A1A1A1'))
        ax.spines['bottom'].set_color(self.colors.get('text_secondary', '#A1A1A1'))

        # Grid
        ax.grid(
            True,
            alpha=0.15,
            color=self.colors.get('text_secondary', '#A1A1A1'),
            linestyle='--',
            linewidth=0.5
        )

    def create_canvas(self, fig, parent):
        """
        Create CustomTkinter canvas widget from matplotlib figure

        Args:
            fig: Matplotlib figure object
            parent: Parent CustomTkinter widget

        Returns:
            Canvas widget ready to be packed
        """
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        return canvas.get_tk_widget()

    def clear_parent(self, parent):
        """
        Clear all widgets from parent container and close matplotlib figures

        Args:
            parent: Parent CustomTkinter widget
        """
        for widget in parent.winfo_children():
            widget.destroy()
        # Close all figures to prevent memory leaks
        plt.close('all')


class LineChartComponent(BaseChartComponent):
    """Line chart component for time-series data with fill"""

    def create(
        self,
        dates: List,
        values: List[float],
        parent,
        title: str = "",
        ylabel: str = "",
        xlabel: str = "Fecha",
        figsize: Tuple[int, int] = (10, 4)
    ):
        """
        Create line chart with fill in parent container

        Args:
            dates: List of date labels (strings or datetime objects)
            values: List of numeric values
            parent: Parent CustomTkinter widget to insert chart
            title: Chart title (optional)
            ylabel: Y-axis label (optional)
            xlabel: X-axis label (default: "Fecha")
            figsize: Figure size tuple (width, height)
        """
        # Clear existing content
        self.clear_parent(parent)

        # Validate data
        if not dates or not values or len(dates) != len(values):
            logger.warning("Invalid data for LineChartComponent")
            return

        try:
            # Create figure
            fig = Figure(figsize=figsize, facecolor=self.colors.get('bg_card', '#242424'), dpi=100)
            ax = fig.add_subplot(111)

            # Plot line with fill
            ax.plot(
                range(len(dates)),
                values,
                color=self.colors.get('accent', '#8B5CF6'),
                linewidth=2.5,
                marker='o',
                markersize=5,
                markerfacecolor=self.colors.get('success', '#10B981'),
                markeredgecolor=self.colors.get('accent', '#8B5CF6'),
                markeredgewidth=1.5
            )

            # Fill area under line
            ax.fill_between(
                range(len(dates)),
                values,
                alpha=0.3,
                color=self.colors.get('accent', '#8B5CF6')
            )

            # Apply theme
            self.apply_dark_theme(ax, fig)

            # Labels and title
            if title:
                ax.set_title(
                    title,
                    fontsize=13,
                    color=self.colors.get('text_primary', '#F5F5F5'),
                    pad=15
                )

            ax.set_xlabel(
                xlabel,
                fontsize=11,
                color=self.colors.get('text_secondary', '#A1A1A1'),
                labelpad=10
            )

            if ylabel:
                ax.set_ylabel(
                    ylabel,
                    fontsize=11,
                    color=self.colors.get('text_secondary', '#A1A1A1'),
                    labelpad=10
                )

            # X-axis ticks
            if len(dates) > 10:
                # Show fewer labels for large datasets
                step = max(1, len(dates) // 8)
                ax.set_xticks(range(0, len(dates), step))
                ax.set_xticklabels(
                    [str(dates[i]) for i in range(0, len(dates), step)],
                    rotation=45,
                    ha='right'
                )
            else:
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels([str(d) for d in dates], rotation=45, ha='right')

            fig.tight_layout()

            # Insert into parent
            canvas_widget = self.create_canvas(fig, parent)
            canvas_widget.pack(fill="both", expand=True, padx=20, pady=20)

        except Exception as e:
            logger.error(f"Error creating line chart: {e}")
            raise


class BarChartComponent(BaseChartComponent):
    """Horizontal bar chart component for rankings with top-3 highlighting"""

    def create(
        self,
        labels: List[str],
        values: List[float],
        parent,
        title: str = "",
        xlabel: str = "",
        figsize: Tuple[int, int] = (10, 4),
        max_label_length: int = 20
    ):
        """
        Create horizontal bar chart in parent container

        Args:
            labels: List of labels (will be truncated if too long)
            values: List of numeric values
            parent: Parent CustomTkinter widget to insert chart
            title: Chart title (optional)
            xlabel: X-axis label (optional)
            figsize: Figure size tuple (width, height)
            max_label_length: Maximum characters for labels before truncation
        """
        # Clear existing content
        self.clear_parent(parent)

        # Validate data
        if not labels or not values or len(labels) != len(values):
            logger.warning("Invalid data for BarChartComponent")
            return

        try:
            # Create figure
            fig = Figure(figsize=figsize, facecolor=self.colors.get('bg_card', '#242424'), dpi=100)
            ax = fig.add_subplot(111)

            # Truncate long labels
            truncated_labels = [
                label[:max_label_length] + '...' if len(label) > max_label_length else label
                for label in labels
            ]

            # Create bars
            bars = ax.barh(
                range(len(labels)),
                values,
                color=self.colors.get('accent', '#8B5CF6'),
                alpha=0.8
            )

            # Highlight top 3 with different colors
            if len(bars) > 0:
                bars[0].set_color(self.colors.get('success', '#10B981'))  # 1st place
            if len(bars) > 1:
                bars[1].set_color(self.colors.get('info', '#3B82F6'))     # 2nd place
            if len(bars) > 2:
                bars[2].set_color(self.colors.get('warning', '#F59E0B'))  # 3rd place

            # Apply theme
            self.apply_dark_theme(ax, fig)

            # Labels and title
            if title:
                ax.set_title(
                    title,
                    fontsize=13,
                    color=self.colors.get('text_primary', '#F5F5F5'),
                    pad=15
                )

            if xlabel:
                ax.set_xlabel(
                    xlabel,
                    fontsize=11,
                    color=self.colors.get('text_secondary', '#A1A1A1'),
                    labelpad=10
                )

            # Y-axis labels
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(truncated_labels, fontsize=10)

            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, values)):
                width = bar.get_width()
                ax.text(
                    width,
                    bar.get_y() + bar.get_height() / 2,
                    f'${value:,.2f}' if value >= 1000 else f'{value:,.2f}',
                    ha='left',
                    va='center',
                    fontsize=9,
                    color=self.colors.get('text_primary', '#F5F5F5'),
                    bbox=dict(
                        boxstyle='round,pad=0.3',
                        facecolor=self.colors.get('card_bg', '#242424'),
                        alpha=0.8
                    )
                )

            # Invert y-axis so top item is at the top
            ax.invert_yaxis()

            fig.tight_layout()

            # Insert into parent
            canvas_widget = self.create_canvas(fig, parent)
            canvas_widget.pack(fill="both", expand=True, padx=20, pady=20)

        except Exception as e:
            logger.error(f"Error creating bar chart: {e}")
            raise


class ComparisonChartComponent(BaseChartComponent):
    """Line chart component for comparing current vs previous period"""

    def create(
        self,
        dates: List,
        current_values: List[float],
        previous_values: Optional[List[float]],
        parent,
        title: str = "",
        ylabel: str = "",
        xlabel: str = "Fecha",
        figsize: Tuple[int, int] = (10, 4)
    ):
        """
        Create comparison line chart in parent container

        Args:
            dates: List of date labels for current period
            current_values: List of numeric values for current period
            previous_values: List of numeric values for previous period (optional)
            parent: Parent CustomTkinter widget to insert chart
            title: Chart title (optional)
            ylabel: Y-axis label (optional)
            xlabel: X-axis label (default: "Fecha")
            figsize: Figure size tuple (width, height)
        """
        # Clear existing content
        self.clear_parent(parent)

        # Validate data
        if not dates or not current_values or len(dates) != len(current_values):
            logger.warning("Invalid data for ComparisonChartComponent")
            return

        try:
            # Create figure
            fig = Figure(figsize=figsize, facecolor=self.colors.get('bg_card', '#242424'), dpi=100)
            ax = fig.add_subplot(111)

            # Plot current period
            ax.plot(
                range(len(dates)),
                current_values,
                color=self.colors.get('accent', '#8B5CF6'),
                linewidth=2.5,
                marker='o',
                markersize=6,
                markerfacecolor=self.colors.get('success', '#10B981'),
                markeredgecolor=self.colors.get('accent', '#8B5CF6'),
                markeredgewidth=1.5,
                label='Periodo actual'
            )

            # Fill area under current period
            ax.fill_between(
                range(len(dates)),
                current_values,
                alpha=0.2,
                color=self.colors.get('accent', '#8B5CF6')
            )

            # Plot previous period if provided
            if previous_values and len(previous_values) > 0:
                min_len = min(len(current_values), len(previous_values))
                ax.plot(
                    range(min_len),
                    previous_values[:min_len],
                    color=self.colors.get('text_secondary', '#A1A1A1'),
                    linewidth=2,
                    linestyle='--',
                    marker='s',
                    markersize=4,
                    alpha=0.6,
                    label='Periodo anterior'
                )

            # Apply theme
            self.apply_dark_theme(ax, fig)

            # Labels and title
            if title:
                ax.set_title(
                    title,
                    fontsize=13,
                    color=self.colors.get('text_primary', '#F5F5F5'),
                    pad=15
                )

            ax.set_xlabel(
                xlabel,
                fontsize=11,
                color=self.colors.get('text_secondary', '#A1A1A1'),
                labelpad=10
            )

            if ylabel:
                ax.set_ylabel(
                    ylabel,
                    fontsize=11,
                    color=self.colors.get('text_secondary', '#A1A1A1'),
                    labelpad=10
                )

            # X-axis ticks
            if len(dates) > 15:
                step = max(1, len(dates) // 10)
                ax.set_xticks(range(0, len(dates), step))
                ax.set_xticklabels(
                    [str(dates[i]) for i in range(0, len(dates), step)],
                    rotation=45,
                    ha='right',
                    fontsize=9
                )
            else:
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels([str(d) for d in dates], rotation=45, ha='right', fontsize=9)

            # Legend
            if previous_values:
                ax.legend(
                    loc='upper left',
                    fontsize=10,
                    framealpha=0.9,
                    frameon=False,
                    labelcolor=self.colors.get('text_secondary', '#A1A1A1')
                )

            fig.tight_layout()

            # Insert into parent
            canvas_widget = self.create_canvas(fig, parent)
            canvas_widget.pack(fill="both", expand=True, padx=20, pady=20)

        except Exception as e:
            logger.error(f"Error creating comparison chart: {e}")
            raise
