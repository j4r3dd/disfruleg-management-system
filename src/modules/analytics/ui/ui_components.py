# -*- coding: utf-8 -*-
"""
DISFRULEG - UI Components para Analytics
Componentes visuales reutilizables y consistentes - Versión Mejorada
"""
import customtkinter as ctk
from src.theme import COLORS, FONTS


class StatCard(ctk.CTkFrame):
    """Tarjeta de estadística con título, valor e ícono - Diseño mejorado"""

    def __init__(self, parent, title: str, value: str, icon: str = "", color: str = COLORS['success'], on_click=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.on_click = on_click
        self.default_bg = COLORS['card_bg']
        self.hover_bg = COLORS.get('hover_surface', '#383838')

        # Si es clickeable, agregar cursor
        if on_click:
            self.configure(
                fg_color=self.default_bg,
                corner_radius=12,
                border_width=0,
                cursor="hand2"
            )
            self.bind("<Button-1>", lambda e: self._handle_click())
        else:
            self.configure(
                fg_color=self.default_bg,
                corner_radius=12,
                border_width=0
            )

        # Contenedor principal con padding mejorado
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=24, pady=20)

        if on_click:
            self.content.bind("<Button-1>", lambda e: self._handle_click())

        # Header con ícono + título
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        if on_click:
            header.bind("<Button-1>", lambda e: self._handle_click())

        if icon:
            icon_label = ctk.CTkLabel(
                header,
                text=icon,
                font=("Arial", 20),
                text_color=COLORS['text_secondary']
            )
            icon_label.pack(side="left", padx=(0, 12))
            if on_click:
                icon_label.configure(cursor="hand2")
                icon_label.bind("<Button-1>", lambda e: self._handle_click())

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=("Arial", 13),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        title_label.pack(side="left", anchor="w")
        if on_click:
            title_label.configure(cursor="hand2")
            title_label.bind("<Button-1>", lambda e: self._handle_click())

        # Valor grande con mejor proporción
        self.value_label = ctk.CTkLabel(
            self.content,
            text=value,
            font=("Arial", 26, "normal"),  # Menos bold, más elegante
            text_color=color
        )
        self.value_label.pack(fill="x", anchor="w")

        if on_click:
            self.value_label.configure(cursor="hand2")
            self.value_label.bind("<Button-1>", lambda e: self._handle_click())

            # Efecto hover
            self.bind("<Enter>", lambda e: self.configure(fg_color=self.hover_bg))
            self.bind("<Leave>", lambda e: self.configure(fg_color=self.default_bg))

    def _handle_click(self):
        """Manejar click en la tarjeta"""
        if self.on_click:
            self.on_click()

    def update_value(self, new_value: str, color: str = None):
        """Actualizar valor mostrado"""
        self.value_label.configure(text=new_value)
        if color:
            self.value_label.configure(text_color=color)


class MetricRow(ctk.CTkFrame):
    """Fila con etiqueta y valor para listados - Diseño mejorado"""
    
    def __init__(self, parent, label: str, value: str = "", value_color: str = COLORS['text_primary'], **kwargs):
        super().__init__(parent, fg_color="transparent", height=40, **kwargs)
        self.pack_propagate(False)
        
        # Contenedor con padding
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=8)
        
        ctk.CTkLabel(
            content,
            text=label,
            font=("Arial", 14),
            text_color=COLORS['text_secondary'],
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
        
        self.value_label = ctk.CTkLabel(
            content,
            text=value,
            font=("Arial", 14, "normal"),
            text_color=value_color
        )
        self.value_label.pack(side="right", padx=(16, 0))
    
    def update_value(self, new_value: str, color: str = None):
        """Actualizar valor"""
        self.value_label.configure(text=new_value)
        if color:
            self.value_label.configure(text_color=color)


class LoadingIndicator(ctk.CTkFrame):
    """Indicador de carga minimalista"""
    
    def __init__(self, parent, text: str = "Cargando...", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        ctk.CTkLabel(
            self,
            text="⟳",
            font=("Arial", 32),
            text_color=COLORS['success']
        ).pack(pady=(40, 16))
        
        ctk.CTkLabel(
            self,
            text=text,
            font=("Arial", 14),
            text_color=COLORS['text_secondary']
        ).pack()


class DataTable(ctk.CTkFrame):
    """Tabla simple para mostrar datos - Diseño mejorado"""
    
    def __init__(self, parent, columns: list, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.columns = columns
        self.rows = []
        
        # Header más compacto y elegante
        header_frame = ctk.CTkFrame(
            self, 
            fg_color=COLORS['surface'], 
            height=44,
            corner_radius=8
        )
        header_frame.pack(fill="x", padx=0, pady=(0, 8))
        header_frame.pack_propagate(False)
        
        for col in columns:
            ctk.CTkLabel(
                header_frame,
                text=col,
                font=("Arial", 13, "normal"),
                text_color=COLORS['text_primary']
            ).pack(side="left", fill="both", expand=True, padx=16, pady=12)
        
        # Contenedor de filas con scroll
        self.rows_container = ctk.CTkFrame(self, fg_color="transparent")
        self.rows_container.pack(fill="both", expand=True)
        
        self.row_count = 0
    
    def add_row(self, values: list):
        """Agregar una fila a la tabla con zebra striping sutil"""
        # Alternar color de fondo muy sutilmente
        bg_color = COLORS['card_bg'] if self.row_count % 2 == 0 else COLORS['surface']
        
        row_frame = ctk.CTkFrame(
            self.rows_container,
            fg_color=bg_color,
            height=42,
            corner_radius=6
        )
        row_frame.pack(fill="x", padx=0, pady=2)
        row_frame.pack_propagate(False)
        
        # Efecto hover (si CustomTkinter lo soporta)
        row_frame.bind("<Enter>", lambda e: row_frame.configure(fg_color=COLORS['surface']))
        row_frame.bind("<Leave>", lambda e: row_frame.configure(fg_color=bg_color))
        
        for val in values:
            ctk.CTkLabel(
                row_frame,
                text=str(val),
                font=("Arial", 13),
                text_color=COLORS['text_primary']
            ).pack(side="left", fill="both", expand=True, padx=16, pady=10)
        
        self.rows.append(row_frame)
        self.row_count += 1
    
    def clear(self):
        """Limpiar todas las filas"""
        for row in self.rows:
            row.destroy()
        self.rows.clear()
        self.row_count = 0


class SearchBar(ctk.CTkFrame):
    """Barra de búsqueda minimalista"""
    
    def __init__(self, parent, on_search=None, placeholder: str = "Buscar...", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.search_var = ctk.StringVar()
        self.on_search = on_search
        
        # Contenedor con esquinas redondeadas
        search_container = ctk.CTkFrame(self, fg_color=COLORS['surface'], corner_radius=8)
        search_container.pack(fill="x", expand=True)
        
        # Input sin borde, más limpio
        self.entry = ctk.CTkEntry(
            search_container,
            textvariable=self.search_var,
            placeholder_text=placeholder,
            font=("Arial", 14),
            height=40,
            border_width=0,
            fg_color="transparent"
        )
        self.entry.pack(side="left", fill="both", expand=True, padx=16, pady=8)
        self.entry.bind('<KeyRelease>', self._on_key_release)
        
        # Botón buscar más discreto
        ctk.CTkButton(
            search_container,
            text="🔍",
            width=40,
            height=32,
            font=("Arial", 14),
            command=self._search,
            fg_color="transparent",
            hover_color=COLORS['surface'],
            text_color=COLORS['text_secondary']
        ).pack(side="right", padx=8)
    
    def _on_key_release(self, event):
        """Buscar en tiempo real"""
        if self.on_search:
            self.on_search(self.search_var.get())
    
    def _search(self):
        """Ejecutar búsqueda"""
        if self.on_search:
            self.on_search(self.search_var.get())
    
    def get_value(self):
        return self.search_var.get()
    
    def clear(self):
        self.search_var.set("")


class TabHeader(ctk.CTkFrame):
    """Header para pestañas minimalista"""
    
    def __init__(self, parent, title: str, icon: str = "", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        icon_text = f"{icon}  " if icon else ""
        
        ctk.CTkLabel(
            self,
            text=f"{icon_text}{title}",
            font=("Arial", 18, "normal"),
            text_color=COLORS['success']
        ).pack(side="left", anchor="w", pady=16)


class NoDataMessage(ctk.CTkFrame):
    """Mensaje cuando no hay datos - Diseño más sutil"""
    
    def __init__(self, parent, message: str = "No hay datos disponibles", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        ctk.CTkLabel(
            self,
            text="∅",
            font=("Arial", 40),
            text_color=COLORS['text_secondary']
        ).pack(pady=(50, 16))
        
        ctk.CTkLabel(
            self,
            text=message,
            font=("Arial", 14),
            text_color=COLORS['text_secondary']
        ).pack(pady=(0, 50))


class FilterBar(ctk.CTkFrame):
    """Barra de filtros múltiples - Diseño mejorado"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, 
            fg_color=COLORS['surface'], 
            corner_radius=10,
            **kwargs
        )
        
        self.filters = {}
        self.pack(fill="x", pady=(0, 16))
    
    def add_filter(self, label: str, values: list, on_change=None) -> ctk.CTkComboBox:
        """Agregar un filtro combo"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(side="left", padx=16, pady=12)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=("Arial", 12),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 12))
        
        combo = ctk.CTkComboBox(
            frame,
            values=values,
            width=140,
            height=32,
            font=("Arial", 13),
            command=on_change,
            border_width=0,
            corner_radius=6
        )
        combo.pack(side="left")
        
        self.filters[label] = combo
        return combo
    
    def get_filters(self) -> dict:
        """Obtener valores de todos los filtros"""
        return {label: combo.get() for label, combo in self.filters.items()}


# Componente bonus: Divider para separar secciones
class Divider(ctk.CTkFrame):
    """Separador visual sutil"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            height=1,
            fg_color=COLORS['surface'],
            **kwargs
        )
        self.pack(fill="x", pady=24)

# ==================== NUEVOS COMPONENTES OPTIMIZADOS v4.0 ====================

from datetime import datetime, timedelta
from typing import Optional, Callable, List, Tuple
import calendar


class DarkDatePicker(ctk.CTkFrame):
    """
    DatePicker personalizado con tema dark completo.
    Reemplaza tkcalendar.DateEntry que no respeta temas oscuros.
    """
    
    def __init__(
        self, 
        parent, 
        initial_date: datetime = None,
        on_date_change: Callable = None,
        width: int = 120,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.on_date_change = on_date_change
        self._date = initial_date or datetime.now()
        
        # Frame contenedor con estilo
        self.container = ctk.CTkFrame(
            self,
            fg_color=COLORS.get('card_bg', '#242424'),
            corner_radius=6,
            border_width=1,
            border_color=COLORS.get('accent', '#8B5CF6')
        )
        self.container.pack(fill="x")
        
        # Entry para mostrar fecha
        self.date_var = ctk.StringVar(value=self._format_date(self._date))
        self.entry = ctk.CTkEntry(
            self.container,
            textvariable=self.date_var,
            width=width - 35,
            height=32,
            font=("Arial", 12),
            fg_color="transparent",
            border_width=0,
            state="readonly"
        )
        self.entry.pack(side="left", padx=(8, 0), pady=4)
        
        # Botón calendario
        self.cal_btn = ctk.CTkButton(
            self.container,
            text="📅",
            width=28,
            height=28,
            font=("Arial", 12),
            fg_color="transparent",
            hover_color=COLORS.get('hover_surface', '#383838'),
            command=self._show_calendar
        )
        self.cal_btn.pack(side="right", padx=4, pady=4)
        
        self.calendar_popup = None
    
    def _format_date(self, date: datetime) -> str:
        return date.strftime('%d/%m/%Y')
    
    def _show_calendar(self):
        if self.calendar_popup and self.calendar_popup.winfo_exists():
            self.calendar_popup.destroy()
            return
        
        self.calendar_popup = ctk.CTkToplevel(self)
        self.calendar_popup.withdraw()
        self.calendar_popup.overrideredirect(True)
        self.calendar_popup.configure(fg_color=COLORS.get('bg_secondary', '#1A1A1A'))
        
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 5
        self.calendar_popup.geometry(f"280x320+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(self.calendar_popup, fg_color="transparent", height=50)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        ctk.CTkButton(
            header, text="◀", width=30, height=30,
            fg_color="transparent",
            hover_color=COLORS.get('accent', '#8B5CF6'),
            command=lambda: self._change_month(-1)
        ).pack(side="left")
        
        self.month_label = ctk.CTkLabel(
            header,
            text=self._get_month_year_text(),
            font=("Arial", 14, "bold"),
            text_color=COLORS.get('text_primary', '#F5F5F5')
        )
        self.month_label.pack(side="left", expand=True)
        
        ctk.CTkButton(
            header, text="▶", width=30, height=30,
            fg_color="transparent",
            hover_color=COLORS.get('accent', '#8B5CF6'),
            command=lambda: self._change_month(1)
        ).pack(side="right")
        
        # Días de la semana
        days_frame = ctk.CTkFrame(self.calendar_popup, fg_color="transparent")
        days_frame.pack(fill="x", padx=10)
        
        for day in ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]:
            ctk.CTkLabel(
                days_frame, text=day, width=35,
                font=("Arial", 11, "bold"),
                text_color=COLORS.get('text_secondary', '#A1A1A1')
            ).pack(side="left", padx=1)
        
        self.days_frame = ctk.CTkFrame(self.calendar_popup, fg_color="transparent")
        self.days_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self._populate_days()
        
        # Botones de acción
        actions = ctk.CTkFrame(self.calendar_popup, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkButton(
            actions, text="Hoy", width=60, height=28,
            fg_color=COLORS.get('accent', '#8B5CF6'),
            command=self._select_today
        ).pack(side="left")
        
        ctk.CTkButton(
            actions, text="Cerrar", width=60, height=28,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS.get('text_secondary', '#A1A1A1'),
            command=self._close_calendar
        ).pack(side="right")
        
        self.calendar_popup.deiconify()
    
    def _get_month_year_text(self) -> str:
        months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        return f"{months[self._date.month - 1]} {self._date.year}"
    
    def _change_month(self, delta: int):
        new_month = self._date.month + delta
        new_year = self._date.year
        
        if new_month > 12:
            new_month = 1
            new_year += 1
        elif new_month < 1:
            new_month = 12
            new_year -= 1
        
        try:
            self._date = self._date.replace(year=new_year, month=new_month, day=1)
        except ValueError:
            self._date = self._date.replace(year=new_year, month=new_month, day=28)
        
        self.month_label.configure(text=self._get_month_year_text())
        self._populate_days()
    
    def _populate_days(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        
        cal = calendar.Calendar(firstweekday=0)
        
        for week in cal.monthdayscalendar(self._date.year, self._date.month):
            week_frame = ctk.CTkFrame(self.days_frame, fg_color="transparent")
            week_frame.pack(fill="x", pady=1)
            
            for day in week:
                if day == 0:
                    ctk.CTkLabel(week_frame, text="", width=35).pack(side="left", padx=1)
                else:
                    is_selected = (day == self._date.day)
                    is_today = (
                        day == datetime.now().day and 
                        self._date.month == datetime.now().month and
                        self._date.year == datetime.now().year
                    )
                    
                    btn = ctk.CTkButton(
                        week_frame,
                        text=str(day),
                        width=35,
                        height=32,
                        font=("Arial", 12),
                        fg_color=COLORS.get('accent', '#8B5CF6') if is_selected else (
                            COLORS.get('success', '#10B981') if is_today else "transparent"
                        ),
                        hover_color=COLORS.get('hover_surface', '#383838'),
                        text_color=COLORS.get('text_primary', '#F5F5F5'),
                        command=lambda d=day: self._select_day(d)
                    )
                    btn.pack(side="left", padx=1)
    
    def _select_day(self, day: int):
        self._date = self._date.replace(day=day)
        self.date_var.set(self._format_date(self._date))
        self._close_calendar()
        if self.on_date_change:
            self.on_date_change(self._date)
    
    def _select_today(self):
        self._date = datetime.now()
        self.date_var.set(self._format_date(self._date))
        self._close_calendar()
        if self.on_date_change:
            self.on_date_change(self._date)
    
    def _close_calendar(self):
        if self.calendar_popup and self.calendar_popup.winfo_exists():
            self.calendar_popup.destroy()
            self.calendar_popup = None
    
    def get_date(self) -> datetime:
        return self._date
    
    def set_date(self, date: datetime):
        self._date = date
        self.date_var.set(self._format_date(self._date))


class ClickableCard(ctk.CTkFrame):
    """
    Card interactiva para mostrar items de ranking.
    Incluye hover effects y es clickeable para ver detalles.
    """
    
    def __init__(
        self,
        parent,
        rank: int,
        title: str,
        value: str,
        value_color: str,
        subtitle: str = "",
        on_click: Callable = None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=COLORS.get('card_bg', '#242424'),
            corner_radius=8,
            height=100,
            **kwargs
        )
        self.pack_propagate(False)
        
        self.on_click = on_click
        self.default_bg = COLORS.get('card_bg', '#242424')
        self.hover_bg = COLORS.get('hover_surface', '#383838')
        
        if on_click:
            self.configure(cursor="hand2")
            self.bind("<Button-1>", lambda e: self._handle_click())
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=16)
        
        if on_click:
            content.bind("<Button-1>", lambda e: self._handle_click())
        
        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")
        
        if on_click:
            top.bind("<Button-1>", lambda e: self._handle_click())
        
        title_label = ctk.CTkLabel(
            top,
            text=f"#{rank} {title}",
            font=("Arial", 15, "bold"),
            text_color=COLORS.get('text_primary', '#F5F5F5'),
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        if on_click:
            title_label.configure(cursor="hand2")
            title_label.bind("<Button-1>", lambda e: self._handle_click())
        
        value_label = ctk.CTkLabel(
            top,
            text=value,
            font=("Arial", 16, "bold"),
            text_color=value_color
        )
        value_label.pack(side="right")
        
        if on_click:
            value_label.configure(cursor="hand2")
            value_label.bind("<Button-1>", lambda e: self._handle_click())
        
        if subtitle:
            bottom = ctk.CTkFrame(content, fg_color="transparent")
            bottom.pack(fill="x", pady=(8, 0))
            
            if on_click:
                bottom.bind("<Button-1>", lambda e: self._handle_click())
            
            subtitle_label = ctk.CTkLabel(
                bottom,
                text=subtitle,
                font=("Arial", 12),
                text_color=COLORS.get('text_secondary', '#A1A1A1')
            )
            subtitle_label.pack(side="left")
            
            if on_click:
                subtitle_label.configure(cursor="hand2")
                subtitle_label.bind("<Button-1>", lambda e: self._handle_click())
        
        if on_click:
            arrow = ctk.CTkLabel(
                content,
                text="→",
                font=("Arial", 16),
                text_color=COLORS.get('text_muted', '#6B6B6B')
            )
            arrow.place(relx=0.98, rely=0.5, anchor="e")
    
    def _handle_click(self):
        if self.on_click:
            self.on_click()
    
    def _on_enter(self, event):
        self.configure(fg_color=self.hover_bg)
    
    def _on_leave(self, event):
        self.configure(fg_color=self.default_bg)


class LoadingOverlay(ctk.CTkFrame):
    """Overlay de carga animado"""
    
    def __init__(self, parent, message: str = "Cargando...", **kwargs):
        super().__init__(parent, fg_color=COLORS.get('bg_primary', '#0A0A0A'), **kwargs)
        
        self._animation_running = False
        self._animation_step = 0
        self._spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        self.spinner_label = ctk.CTkLabel(
            content,
            text=self._spinner_chars[0],
            font=("Arial", 32),
            text_color=COLORS.get('accent', '#8B5CF6')
        )
        self.spinner_label.pack(pady=(0, 16))
        
        self.message_label = ctk.CTkLabel(
            content,
            text=message,
            font=("Arial", 14),
            text_color=COLORS.get('text_secondary', '#A1A1A1')
        )
        self.message_label.pack()
    
    def show(self):
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self._animation_running = True
        self._animate()
    
    def hide(self):
        self._animation_running = False
        self.place_forget()
    
    def _animate(self):
        if not self._animation_running:
            return
        self._animation_step = (self._animation_step + 1) % len(self._spinner_chars)
        self.spinner_label.configure(text=self._spinner_chars[self._animation_step])
        self.after(80, self._animate)
    
    def update_message(self, message: str):
        self.message_label.configure(text=message)
