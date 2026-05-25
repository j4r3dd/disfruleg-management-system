# -*- coding: utf-8 -*-
"""
Stats Panel Component
Displays user statistics in card format
"""

import customtkinter as ctk
from typing import Dict, Callable, Optional

from ...domain.models import UserStats


class StatsPanel(ctk.CTkFrame):
    """Panel displaying user statistics cards"""
    
    STATS_CONFIG = [
        {'key': 'total', 'label': 'Total Usuarios', 'icon': '👥', 'color': '#3b82f6'},
        {'key': 'active', 'label': 'Usuarios Activos', 'icon': '📈', 'color': '#10b981'},
        {'key': 'blocked', 'label': 'Bloqueados', 'icon': '🛡️', 'color': '#ef4444'},
        {'key': 'admins', 'label': 'Administradores', 'icon': '👨‍💼', 'color': '#a855f7'},
    ]
    
    def __init__(self, parent, **kwargs):
        """
        Initialize stats panel
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.stat_labels: Dict[str, ctk.CTkLabel] = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the stats cards UI"""
        for i, config in enumerate(self.STATS_CONFIG):
            card = self._create_stat_card(config)
            card.grid(row=0, column=i, padx=10, sticky="ew")
            self.grid_columnconfigure(i, weight=1)
    
    def _create_stat_card(self, config: dict) -> ctk.CTkFrame:
        """
        Create a single stat card
        
        Args:
            config: Card configuration dict
            
        Returns:
            Card frame widget
        """
        card = ctk.CTkFrame(self, fg_color=("#2a2a2a", "#2a2a2a"), corner_radius=15)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with label and icon
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text=config['label'],
            font=("Arial", 11),
            text_color="gray60",
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=config['icon'],
            font=("Arial", 18),
            text_color=config['color']
        ).pack(side="right")
        
        # Value label
        value_label = ctk.CTkLabel(
            content,
            text="0",
            font=("Arial", 32, "bold"),
            text_color="white",
            anchor="w"
        )
        value_label.pack(anchor="w", pady=(10, 0))
        
        # Store reference for updates
        self.stat_labels[config['key']] = value_label
        
        return card
    
    def update_stats(self, stats: UserStats):
        """
        Update all stat values
        
        Args:
            stats: UserStats object with current values
        """
        if 'total' in self.stat_labels:
            self.stat_labels['total'].configure(text=str(stats.total))
        if 'active' in self.stat_labels:
            self.stat_labels['active'].configure(text=str(stats.active))
        if 'blocked' in self.stat_labels:
            self.stat_labels['blocked'].configure(text=str(stats.blocked))
        if 'admins' in self.stat_labels:
            self.stat_labels['admins'].configure(text=str(stats.admins))
