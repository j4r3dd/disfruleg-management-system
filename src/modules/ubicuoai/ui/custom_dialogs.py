# -*- coding: utf-8 -*-
"""
custom_dialogs.py - Diálogos personalizados estéticos para UbicuoAI
Reemplaza los messagebox nativos de tkinter con diseños modernos
"""

import customtkinter as ctk
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

# Colores consistentes con el tema
DIALOG_COLORS = {
    'bg': '#0A0E27',
    'card': '#1E2139',
    'border': '#2D3250',
    'text': '#FFFFFF',
    'text_secondary': '#94A3B8',
    'success': '#10B981',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'info': '#00D4FF',
}


class CustomDialog(ctk.CTkToplevel):
    """Diálogo base personalizado con diseño moderno"""
    
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        dialog_type: str = "info",  # info, success, warning, error
        buttons: list = None,
        icon: str = None,
        width: int = 420,
        height: int = 200
    ):
        super().__init__(parent)
        
        self.result = None
        self.dialog_type = dialog_type
        
        # Configurar ventana
        self.title("")
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=DIALOG_COLORS['bg'])
        self.resizable(False, False)
        
        # Centrar en parent
        self.transient(parent)
        self.grab_set()
        
        # Centrar en pantalla
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
        
        # Construir UI
        self._build_ui(title, message, icon, buttons)
        
        # Bind escape
        self.bind("<Escape>", lambda e: self._on_cancel())
        
        # Focus
        self.focus_force()
    
    def _get_icon_and_color(self):
        """Retorna icono y color según tipo de diálogo"""
        icons = {
            'info': ('ℹ️', DIALOG_COLORS['info']),
            'success': ('✓', DIALOG_COLORS['success']),
            'warning': ('⚠', DIALOG_COLORS['warning']),
            'error': ('✕', DIALOG_COLORS['error']),
        }
        return icons.get(self.dialog_type, icons['info'])
    
    def _build_ui(self, title: str, message: str, icon: str, buttons: list):
        """Construye la interfaz del diálogo"""
        icon_char, accent_color = self._get_icon_and_color()
        if icon:
            icon_char = icon
        
        # Container principal con borde sutil
        main_frame = ctk.CTkFrame(
            self,
            fg_color=DIALOG_COLORS['card'],
            corner_radius=12,
            border_width=1,
            border_color=accent_color
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Header con icono
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        
        # Icono circular
        icon_frame = ctk.CTkFrame(
            header,
            width=48,
            height=48,
            corner_radius=24,
            fg_color=accent_color
        )
        icon_frame.pack(side="left")
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon_char,
            font=("Arial", 20, "bold"),
            text_color="#FFFFFF"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=("Arial", 18, "bold"),
            text_color=DIALOG_COLORS['text']
        )
        title_label.pack(side="left", padx=16)
        
        # Mensaje
        message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=("Arial", 13),
            text_color=DIALOG_COLORS['text_secondary'],
            wraplength=360,
            justify="left"
        )
        message_label.pack(fill="x", padx=24, pady=(0, 20))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 20))
        
        if buttons is None:
            buttons = [("Aceptar", "ok", True)]
        
        for btn_text, btn_value, is_primary in reversed(buttons):
            btn = ctk.CTkButton(
                btn_frame,
                text=btn_text,
                width=100,
                height=36,
                corner_radius=8,
                font=("Arial", 13, "bold"),
                fg_color=accent_color if is_primary else "transparent",
                hover_color=self._adjust_color(accent_color, 0.8) if is_primary else DIALOG_COLORS['border'],
                border_width=1 if not is_primary else 0,
                border_color=DIALOG_COLORS['border'],
                text_color="#FFFFFF" if is_primary else DIALOG_COLORS['text_secondary'],
                command=lambda v=btn_value: self._on_button(v)
            )
            btn.pack(side="right", padx=(8, 0))
    
    def _adjust_color(self, hex_color: str, factor: float) -> str:
        """Ajusta brillo de un color hex"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(min(255, int(c * factor)) for c in rgb)
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"
    
    def _on_button(self, value):
        """Maneja click en botón"""
        self.result = value
        self.grab_release()
        self.destroy()
    
    def _on_cancel(self):
        """Maneja cancelación (Escape)"""
        self.result = "cancel"
        self.grab_release()
        self.destroy()
    
    def get_result(self):
        """Espera y retorna el resultado"""
        self.wait_window()
        return self.result


# ============ Funciones de conveniencia ============

def show_info(parent, title: str, message: str, icon: str = None) -> str:
    """Muestra diálogo informativo"""
    dialog = CustomDialog(parent, title, message, "info", icon=icon)
    return dialog.get_result()


def show_success(parent, title: str, message: str, icon: str = "✓") -> str:
    """Muestra diálogo de éxito"""
    dialog = CustomDialog(parent, title, message, "success", icon=icon)
    return dialog.get_result()


def show_warning(parent, title: str, message: str, icon: str = "⚠") -> str:
    """Muestra diálogo de advertencia"""
    dialog = CustomDialog(parent, title, message, "warning", icon=icon)
    return dialog.get_result()


def show_error(parent, title: str, message: str, icon: str = "✕") -> str:
    """Muestra diálogo de error"""
    dialog = CustomDialog(parent, title, message, "error", icon=icon)
    return dialog.get_result()


def ask_confirm(parent, title: str, message: str, dialog_type: str = "warning") -> bool:
    """Muestra diálogo de confirmación. Retorna True si confirma."""
    buttons = [
        ("Cancelar", "cancel", False),
        ("Confirmar", "confirm", True),
    ]
    dialog = CustomDialog(parent, title, message, dialog_type, buttons=buttons)
    return dialog.get_result() == "confirm"


def ask_yes_no(parent, title: str, message: str, dialog_type: str = "info") -> Optional[bool]:
    """Muestra diálogo Sí/No. Retorna True, False o None si cancela."""
    buttons = [
        ("No", "no", False),
        ("Sí", "yes", True),
    ]
    dialog = CustomDialog(parent, title, message, dialog_type, buttons=buttons)
    result = dialog.get_result()
    if result == "yes":
        return True
    elif result == "no":
        return False
    return None


# ============ Toast Notification ============

class ToastNotification(ctk.CTkFrame):
    """Notificación tipo toast que aparece y desaparece"""
    
    def __init__(
        self,
        parent,
        message: str,
        toast_type: str = "info",
        duration: int = 3000,
        position: str = "bottom-right"
    ):
        # Colores según tipo
        colors = {
            'info': DIALOG_COLORS['info'],
            'success': DIALOG_COLORS['success'],
            'warning': DIALOG_COLORS['warning'],
            'error': DIALOG_COLORS['error'],
        }
        accent = colors.get(toast_type, colors['info'])
        
        icons = {
            'info': 'ℹ️',
            'success': '✓',
            'warning': '⚠',
            'error': '✕',
        }
        icon = icons.get(toast_type, 'ℹ️')
        
        super().__init__(
            parent,
            fg_color=DIALOG_COLORS['card'],
            corner_radius=10,
            border_width=1,
            border_color=accent
        )
        
        # Contenido
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", padx=16, pady=12)
        
        # Icono
        icon_label = ctk.CTkLabel(
            content,
            text=icon,
            font=("Arial", 16),
            text_color=accent,
            width=24
        )
        icon_label.pack(side="left")
        
        # Mensaje
        msg_label = ctk.CTkLabel(
            content,
            text=message,
            font=("Arial", 12),
            text_color=DIALOG_COLORS['text']
        )
        msg_label.pack(side="left", padx=(8, 0))
        
        # Posicionar
        self._position_toast(parent, position)
        
        # Auto-cerrar
        self.after(duration, self._fade_out)
    
    def _position_toast(self, parent, position: str):
        """Posiciona el toast en la ventana"""
        self.update_idletasks()
        
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        toast_width = self.winfo_reqwidth()
        toast_height = self.winfo_reqheight()
        
        margin = 20
        
        if "bottom" in position:
            y = parent_height - toast_height - margin
        else:
            y = margin
        
        if "right" in position:
            x = parent_width - toast_width - margin
        else:
            x = margin
        
        self.place(x=x, y=y)
    
    def _fade_out(self):
        """Desvanece y destruye el toast"""
        self.destroy()


def show_toast(parent, message: str, toast_type: str = "info", duration: int = 3000):
    """Muestra una notificación toast"""
    return ToastNotification(parent, message, toast_type, duration)
