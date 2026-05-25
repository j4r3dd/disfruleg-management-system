"""
🎨 Section Dialogs - Diálogos para Gestión de Secciones (FINAL)
Interfaz idéntica al mockup con colores exactos del sistema UbicuoAI
"""

import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
import logging

from .custom_dialogs import show_info, show_warning

logger = logging.getLogger(__name__)

# Colores del sistema UbicuoAI
COLORS = {
    'ai_blue': '#00D4FF',
    'ai_purple': '#8B5CF6',
    'ai_green': '#10B981',
    'ai_orange': '#F59E0B',
    'ai_red': '#EF4444',
    'bg_primary': '#0A0E27',
    'bg_secondary': '#151933',
    'bg_card': '#1E2139',
    'text_primary': '#FFFFFF',
    'text_secondary': '#94A3B8',
    'border': '#2D3250',
}


class SectionManagementDialog(ctk.CTkToplevel):
    """
    Diálogo final para gestionar secciones - Exacto al mockup
    - Checkbox para confirmar/rechazar
    - Click en nombre para editar
    - Botón X para eliminar
    - Botones: Confirmar / Cerrar
    - Colores del sistema UbicuoAI
    """
    
    def __init__(
        self,
        parent,
        sections: List[Dict[str, Any]],
        on_confirm: Optional[Callable] = None,
        on_rename: Optional[Callable] = None,
        on_remove: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        on_apply_all: Optional[Callable] = None  # Nuevo: callback para aplicar todos los cambios
    ):
        super().__init__(parent)
        
        self.sections = sections
        self.on_confirm = on_confirm
        self.on_rename = on_rename  # Nuevo callback para renombrar
        self.on_remove = on_remove
        self.on_close = on_close
        self.on_apply_all = on_apply_all  # Callback que recibe todo el estado final
        
        # Estado de secciones
        self.sections_state = {}
        for section in sections:
            section_name = section.get('name', section.get('section_name', ''))
            self.sections_state[section_name] = {
                'confirmed': section.get('confirmed', False),
                'new_name': section_name,
                'deleted': False,
                'original_name': section_name
            }
        
        self.section_checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        self.section_widgets: Dict[str, Dict] = {}
        
        # Configuración de la ventana
        self.title("📁 Gestión de Secciones")
        self.geometry("550x700")
        self.resizable(True, True)  # Permitir redimensionar
        self.minsize(450, 400)  # Tamaño mínimo
        self.configure(fg_color=COLORS['bg_primary'])
        ctk.set_appearance_mode("dark")
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 550) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"550x700+{x}+{y}")
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        
        # Construir interfaz
        self._build_ui()
        
        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _build_ui(self):
        """Construye la interfaz del diálogo"""
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header
        self._build_header(main_frame)
        
        # Descripción
        self._build_description(main_frame)
        
        # Lista de secciones
        self._build_sections_list(main_frame)
        
        # Botones de acción
        self._build_action_buttons(main_frame)
    
    def _build_header(self, parent):
        """Construye el encabezado"""
        header = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], height=70, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        # Left: Icon + Title
        left = ctk.CTkFrame(header_content, fg_color="transparent")
        left.pack(side="left")
        
        ctk.CTkLabel(
            left,
            text="📁",
            font=("Arial", 24)
        ).pack(side="left", padx=(0, 12))
        
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Gestión de Secciones",
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text=f"{len(self.sections)} secciones encontradas",
            font=("Arial", 11),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        # Right: Close button
        close_btn = ctk.CTkButton(
            header_content,
            text="✕",
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['ai_red'],
            font=("Arial", 16),
            command=self._on_close
        )
        close_btn.pack(side="right")
    
    def _build_description(self, parent):
        """Construye el mensaje informativo"""
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=8,
            border_width=2,
            border_color=COLORS['ai_green']
        )
        info_frame.pack(fill="x", padx=20, pady=15)
        
        info_text = (
            "ℹ️  Las secciones confirmadas se usarán para organizar el pedido\n"
            "    en el Receipt Generator. Desmarca las que no desees usar."
        )
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Arial", 12),
            text_color=COLORS['ai_green'],
            justify="left",
            wraplength=500
        ).pack(padx=15, pady=12)
    
    def _build_sections_list(self, parent):
        """Construye la lista scrollable de secciones"""
        scrollable_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        for idx, section in enumerate(self.sections):
            self._add_section_item(scrollable_frame, section, idx)
    
    def _add_section_item(self, parent, section: Dict[str, Any], index: int):
        """
        Agrega un item de sección con:
        - Checkbox | Nombre (editable) | Botón X
        - Info: Línea + productos + Estado
        """
        section_name = section.get('name', section.get('section_name', ''))
        line_number = section.get('line', section.get('line_number', '?'))
        item_count = section.get('item_count', 0)
        confirmed = section.get('confirmed', False)
        
        # Frame principal con bordes verdes
        section_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=10,
            border_width=2,
            border_color=COLORS['ai_green']
        )
        section_frame.pack(fill="x", pady=8, padx=0)
        
        # === FILA 1: Checkbox | Nombre | X ===
        top_row = ctk.CTkFrame(section_frame, fg_color="transparent")
        top_row.pack(fill="x", padx=15, pady=(12, 8))
        
        # CHECKBOX (verde)
        checkbox_var = ctk.BooleanVar(value=confirmed)
        
        def on_checkbox_change(value=None, name=section_name):
            self.sections_state[name]['confirmed'] = checkbox_var.get()
            logger.debug(f"Checkbox {name}: {checkbox_var.get()}")
        
        checkbox = ctk.CTkCheckBox(
            top_row,
            text="",
            variable=checkbox_var,
            onvalue=True,
            offvalue=False,
            command=on_checkbox_change,
            checkbox_width=24,
            checkbox_height=24,
            border_width=2,
            border_color=COLORS['ai_green'],
            fg_color=COLORS['ai_green'],
            hover_color="#059669"
        )
        checkbox.pack(side="left", padx=(0, 12))
        
        self.section_checkboxes[section_name] = checkbox
        
        # NOMBRE (editable)
        name_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        name_frame.pack(side="left", fill="both", expand=True)
        
        name_label = ctk.CTkLabel(
            name_frame,
            text=section_name.upper(),
            font=("Arial", 14, "bold"),
            text_color=COLORS['text_primary'],
            justify="left"
        )
        name_label.pack(anchor="w")
        
        self.section_widgets[section_name] = {
            'checkbox': checkbox,
            'name_label': name_label,
            'frame': section_frame
        }
        
        # Hacer clickeable para editar
        def edit_name():
            self._edit_section_name_inline(section_name, name_label, name_frame)
        
        name_label.bind("<Button-1>", lambda e: edit_name())
        name_label.configure(cursor="hand2")
        
        # BOTÓN X (rojo, lado derecho)
        def delete_section():
            self._delete_section(section_name, section_frame)
        
        delete_btn = ctk.CTkButton(
            top_row,
            text="✕",
            width=32,
            height=32,
            corner_radius=6,
            fg_color=COLORS['ai_red'],
            hover_color="#DC2626",
            font=("Arial", 14, "bold"),
            text_color="white",
            command=delete_section
        )
        delete_btn.pack(side="right", padx=(10, 0))
        
        # === FILA 2: Info (Línea | Productos) + Estado ===
        info_row = ctk.CTkFrame(section_frame, fg_color="transparent")
        info_row.pack(fill="x", padx=50, pady=(0, 10))
        
        info_text = f"Línea {line_number} • {item_count} producto{'s' if item_count != 1 else ''}"
        info_label = ctk.CTkLabel(
            info_row,
            text=info_text,
            font=("Arial", 11),
            text_color=COLORS['text_secondary']
        )
        info_label.pack(anchor="w")
        
        # Estado (en color verde)
        status_label = ctk.CTkLabel(
            info_row,
            text="Estado: Pendiente",
            font=("Arial", 10, "italic"),
            text_color=COLORS['ai_green']
        )
        status_label.pack(anchor="w")
        
        self.section_widgets[section_name]['status_label'] = status_label
    
    def _edit_section_name_inline(self, section_name: str, label_widget, parent_frame):
        """Permite editar el nombre inline"""
        # Frame de edición
        edit_frame = ctk.CTkFrame(
            parent_frame,
            fg_color=COLORS['bg_primary'],
            corner_radius=6,
            border_width=2,
            border_color=COLORS['ai_blue']
        )
        edit_frame.pack(side="left", fill="both", expand=True, before=label_widget)
        
        # Campo entrada
        entry = ctk.CTkEntry(
            edit_frame,
            fg_color=COLORS['bg_card'],
            border_color=COLORS['ai_blue'],
            border_width=2,
            text_color=COLORS['text_primary'],
            placeholder_text="Nombre de sección"
        )
        entry.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        entry.insert(0, self.sections_state[section_name]['new_name'])
        entry.focus()
        entry.select_range(0, "end")
        
        # Guardar
        def save_name():
            new_name = entry.get().strip()
            if new_name:
                self.sections_state[section_name]['new_name'] = new_name
                label_widget.configure(text=new_name.upper())
                logger.info(f"Nombre actualizado: {section_name} → {new_name}")
            edit_frame.pack_forget()
            label_widget.pack()
        
        # Cancelar
        def cancel_edit():
            edit_frame.pack_forget()
            label_widget.pack()
        
        # Botones
        save_btn = ctk.CTkButton(
            edit_frame,
            text="✓",
            width=32,
            height=32,
            corner_radius=6,
            fg_color=COLORS['ai_green'],
            hover_color="#059669",
            font=("Arial", 12, "bold"),
            command=save_name
        )
        save_btn.pack(side="left", padx=4)
        
        cancel_btn = ctk.CTkButton(
            edit_frame,
            text="✕",
            width=32,
            height=32,
            corner_radius=6,
            fg_color=COLORS['ai_red'],
            hover_color="#DC2626",
            font=("Arial", 12, "bold"),
            command=cancel_edit
        )
        cancel_btn.pack(side="left", padx=2)
        
        # Atajos
        entry.bind("<Return>", lambda e: save_name())
        entry.bind("<Escape>", lambda e: cancel_edit())
    
    def _delete_section(self, section_name: str, section_frame):
        """Marca sección para eliminar"""
        self.sections_state[section_name]['deleted'] = True
        self.section_widgets[section_name]['checkbox'].configure(state="disabled")
        section_frame.configure(border_color=COLORS['ai_red'])
        logger.info(f"Sección marcada para eliminar: {section_name}")
    
    def _build_action_buttons(self, parent):
        """Construye los botones - Confirmar / Cerrar"""
        footer = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], height=80, corner_radius=0)
        footer.pack(fill="x", padx=0, pady=0)
        footer.pack_propagate(False)
        
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        button_frame = ctk.CTkFrame(footer_content, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Botón Confirmar (verde)
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="✓ Confirmar",
            font=("Arial", 13, "bold"),
            fg_color=COLORS['ai_green'],
            hover_color="#059669",
            height=40,
            corner_radius=8,
            command=self._apply_changes
        )
        confirm_btn.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Botón Cerrar (gris)
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cerrar",
            font=("Arial", 13),
            fg_color=COLORS['text_secondary'],
            hover_color="#64748B",
            height=40,
            corner_radius=8,
            command=self._on_close
        )
        cancel_btn.pack(side="left", fill="both", expand=True)
    
    def _apply_changes(self):
        """Aplica todos los cambios confirmados"""
        try:
            logger.info("💾 Confirmando cambios de secciones...")
            
            # Si hay callback para aplicar todo de una vez, usarlo
            if self.on_apply_all:
                # Construir lista de cambios
                changes = []
                for section_name, state in self.sections_state.items():
                    changes.append({
                        'original_name': state['original_name'],
                        'new_name': state['new_name'],
                        'confirmed': state['confirmed'],
                        'deleted': state['deleted']
                    })
                self.on_apply_all(changes)
            else:
                # Aplicar cambios uno por uno (modo legacy)
                for section_name, state in self.sections_state.items():
                    original_name = state['original_name']
                    new_name = state['new_name']
                    
                    if state['deleted']:
                        # Eliminar sección
                        if self.on_remove:
                            self.on_remove(original_name)
                        logger.info(f"  ✗ Eliminada: {original_name}")
                    else:
                        # Renombrar si cambió el nombre
                        if new_name != original_name and self.on_rename:
                            self.on_rename(original_name, new_name)
                            logger.info(f"  ✏️ Renombrada: {original_name} → {new_name}")
                        
                        # Confirmar o rechazar
                        if self.on_confirm:
                            self.on_confirm(new_name if new_name != original_name else original_name, state['confirmed'])
                        
                        if state['confirmed']:
                            logger.info(f"  ✓ Confirmada: {new_name}")
                        else:
                            logger.info(f"  ✗ No confirmada: {new_name}")
            
            self._on_close()
            
        except Exception as e:
            logger.error(f"Error aplicando cambios: {e}")
            messagebox.showerror("Error", f"Error: {str(e)}", parent=self)
    
    def _on_close(self):
        """Cierra el diálogo"""
        try:
            if self.on_close:
                self.on_close()
            
            self.grab_release()
            self.destroy()
        except Exception as e:
            logger.error(f"Error cerrando diálogo: {e}")


class RemovalDialog(ctk.CTkToplevel):
    """Diálogo para marcar items para eliminación"""
    
    def __init__(
        self,
        parent,
        items_to_review: List[Dict[str, Any]],
        on_mark_removal: Optional[Callable] = None,
        on_close: Optional[Callable] = None
    ):
        super().__init__(parent)
        
        self.items_to_review = items_to_review
        self.on_mark_removal = on_mark_removal
        self.on_close = on_close
        
        self.removal_checkboxes: Dict[int, ctk.CTkCheckBox] = {}
        
        # Configuración
        self.title("🗑️ Marcar para Eliminación")
        self.geometry("550x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_primary'])
        ctk.set_appearance_mode("dark")
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 550) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"550x600+{x}+{y}")
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Construir UI
        self._build_ui()
        
        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _build_ui(self):
        """Construye la interfaz"""
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_secondary'], height=70, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        left = ctk.CTkFrame(header_content, fg_color="transparent")
        left.pack(side="left")
        
        ctk.CTkLabel(left, text="🗑️", font=("Arial", 24)).pack(side="left", padx=(0, 12))
        
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Marcar para Eliminación",
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text=f"{len(self.items_to_review)} items a revisar",
            font=("Arial", 11),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        close_btn = ctk.CTkButton(
            header_content,
            text="✕",
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['ai_red'],
            font=("Arial", 16),
            command=self._on_close
        )
        close_btn.pack(side="right")
        
        # Items
        items_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        items_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        for item in self.items_to_review:
            self._add_removal_item(items_frame, item)
        
        # Footer
        footer = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_secondary'], height=80, corner_radius=0)
        footer.pack(fill="x", padx=0, pady=0)
        footer.pack_propagate(False)
        
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        buttons_frame = ctk.CTkFrame(footer_content, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        confirm_btn = ctk.CTkButton(
            buttons_frame,
            text="✓ Confirmar",
            font=("Arial", 13, "bold"),
            fg_color=COLORS['ai_green'],
            hover_color="#059669",
            height=40,
            corner_radius=8,
            command=self._apply_removals
        )
        confirm_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cerrar",
            font=("Arial", 13),
            fg_color=COLORS['text_secondary'],
            hover_color="#64748B",
            height=40,
            corner_radius=8,
            command=self._on_close
        )
        cancel_btn.pack(side="left", fill="x", expand=True)
    
    def _add_removal_item(self, parent, item: Dict[str, Any]):
        """Agrega un item a la lista"""
        line_number = item.get('line_number', 0)
        text = item.get('raw_text', 'Línea sin texto')
        
        frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=8,
            border_width=2,
            border_color=COLORS['border']
        )
        frame.pack(fill="x", pady=5, padx=0)
        
        checkbox = ctk.CTkCheckBox(
            frame,
            text=f"Línea {line_number}: {text[:50]}...",
            font=("Arial", 12),
            checkbox_width=20,
            checkbox_height=20,
            text_color=COLORS['text_primary'],
            border_color=COLORS['ai_orange'],
            fg_color=COLORS['ai_orange']
        )
        checkbox.pack(anchor="w", padx=15, pady=10)
        
        self.removal_checkboxes[line_number] = checkbox
    
    def _apply_removals(self):
        """Aplica marcas de eliminación"""
        marked = []
        
        for line_num, checkbox in self.removal_checkboxes.items():
            if checkbox.get():
                marked.append(line_num)
                if self.on_mark_removal:
                    self.on_mark_removal(line_num)
        
        if marked:
            show_info(
                self,
                "Eliminaciones Aplicadas",
                f"✓ {len(marked)} línea(s) marcada(s) para eliminación."
            )
            self._on_close()
        else:
            show_warning(
                self,
                "Sin Selección",
                "No se marcó ninguna línea para eliminar."
            )
    
    def _on_close(self):
        """Cierra el diálogo"""
        if self.on_close:
            self.on_close()
        
        self.grab_release()
        self.destroy()