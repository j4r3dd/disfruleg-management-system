# -*- coding: utf-8 -*-
"""
Cart UI Component
Handles all cart UI rendering and user interactions
Completely separate from data model
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Callable

from src.theme import COLORS, FONTS
from src.modules.receipts.models.cart_model import CartModel, CartItem, CartSection
from src.modules.receipts.constants import SectionNames


class CartUIComponent:
    """
    Cart UI Component - Handles rendering and user interactions
    Uses CartModel for all data operations
    """

    def __init__(
        self,
        parent_frame,
        cart_model: CartModel,
        on_change_callback: Optional[Callable] = None
    ):
        """
        Initialize Cart UI Component

        Args:
            parent_frame: Parent CTk frame
            cart_model: CartModel instance to render
            on_change_callback: Callback when cart changes
        """
        self.parent = parent_frame
        self.cart_model = cart_model
        self.on_change_callback = on_change_callback
        self.parent_frame = None
        self.tree = None

        # UI state
        self.sectioning_var = None
        self.btn_gestionar = None
        self.btn_mover_seccion = None

        # Create interface
        self._create_interface()
        self._apply_treeview_styles()
        self.refresh()

    # ==================== UI CREATION ====================

    def _create_interface(self):
        """Create the cart UI structure"""
        # Main frame
        self.parent_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.parent_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.parent_frame.grid_rowconfigure(1, weight=1)
        self.parent_frame.grid_columnconfigure(0, weight=1)

        # Controls frame
        self._create_controls_frame()

        # Tree frame
        self._create_tree_frame()

    def _create_controls_frame(self):
        """Create controls section (sectioning toggle, manage button)"""
        frame_controles = ctk.CTkFrame(
            self.parent_frame,
            fg_color=("gray85", "gray20"),
            corner_radius=10
        )
        frame_controles.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        frame_controles.grid_columnconfigure(0, weight=1)

        controles_content = ctk.CTkFrame(frame_controles, fg_color="transparent")
        controles_content.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        controles_content.grid_columnconfigure(3, weight=1)

        # Sectioning checkbox
        self.sectioning_var = tk.BooleanVar(value=self.cart_model.sectioning_enabled)
        check_secciones = ctk.CTkCheckBox(
            controles_content,
            text="🗂️ Habilitar Secciones",
            variable=self.sectioning_var,
            command=self._on_toggle_sectioning,
            font=FONTS['body'],
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=6,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover']
        )
        check_secciones.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Manage sections button
        self.btn_gestionar = ctk.CTkButton(
            controles_content,
            text="⚙️ Gestionar",
            command=self._on_manage_sections,
            fg_color=COLORS['secondary'],
            hover_color=COLORS['primary_hover'],
            width=120,
            height=32,
            font=FONTS['body_bold'],
            corner_radius=8
        )
        self.btn_gestionar.grid(row=0, column=1, sticky="w", padx=(0, 10))

        # Move to section button
        self.btn_mover_seccion = ctk.CTkButton(
            controles_content,
            text="📋 Mover a Sección",
            command=self._on_move_to_section,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover'],
            width=150,
            height=32,
            font=FONTS['body_bold'],
            corner_radius=8
        )
        self.btn_mover_seccion.grid(row=0, column=2, sticky="w")

        # Info label
        ctk.CTkLabel(
            controles_content,
            text="💡 Ctrl+clic para selección múltiple | Doble clic para editar",
            font=("Arial", 10, "italic"),
            text_color=("gray50", "gray60")
        ).grid(row=0, column=3, sticky="e")

    def _create_tree_frame(self):
        """Create treeview frame and treeview"""
        tree_frame = ctk.CTkFrame(
            self.parent_frame,
            fg_color=("gray95", "gray15"),
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Inner padding frame
        inner_frame = ctk.CTkFrame(tree_frame, fg_color="transparent")
        inner_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        inner_frame.grid_rowconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(0, weight=1)

        # Container for tree and scrollbar
        tree_container = tk.Frame(inner_frame, bg=("white" if ctk.get_appearance_mode() == "Light" else "#2b2b2b"))
        tree_container.grid(row=0, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Define columns
        cols = ("cantidad", "unidad", "precio_unitario", "total", "del")
        self.tree = ttk.Treeview(
            tree_container,
            columns=cols,
            show="tree headings",
            style="Carrito.Treeview",
            height=15,
            selectmode="extended"  # Enable multi-selection
        )

        # Configure columns
        self.tree.heading("#0", text="📦 Producto / Sección")
        self.tree.column("#0", width=220, stretch=True, minwidth=150)

        self.tree.heading("cantidad", text="Cantidad")
        self.tree.column("cantidad", width=90, anchor="center", minwidth=70)

        self.tree.heading("unidad", text="Unidad")
        self.tree.column("unidad", width=80, anchor="center", minwidth=60)

        self.tree.heading("precio_unitario", text="Precio Unit.")
        self.tree.column("precio_unitario", width=110, anchor="e", minwidth=90)

        self.tree.heading("total", text="Subtotal")
        self.tree.column("total", width=110, anchor="e", minwidth=90)

        self.tree.heading("del", text="Eliminar")
        self.tree.column("del", width=70, anchor="center", minwidth=70)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind events
        self.tree.bind("<Double-Button-1>", self._on_double_click)
        self.tree.bind("<Button-1>", self._on_click)
        self.tree.bind("<Button-3>", self._on_right_click)  # Right-click for context menu
        self.tree.bind("<Button-2>", self._on_right_click)  # Middle-click for macOS

    def _apply_treeview_styles(self):
        """Apply custom styles to treeview"""
        style = ttk.Style()

        # Define Treeview style
        if ctk.get_appearance_mode() == "Light":
            bg_color = "white"
            fg_color = "black"
            selected_bg = COLORS['primary']
        else:
            bg_color = "#2b2b2b"
            fg_color = "white"
            selected_bg = COLORS['primary']

        style.theme_use("clam")
        style.configure(
            "Carrito.Treeview",
            background=bg_color,
            foreground=fg_color,
            fieldbackground=bg_color,
            borderwidth=0,
            font=FONTS['body']
        )
        style.map(
            "Carrito.Treeview",
            background=[("selected", selected_bg)],
            foreground=[("selected", "white")]
        )
        style.configure(
            "Carrito.Treeview.Heading",
            background=("gray75" if ctk.get_appearance_mode() == "Light" else "gray25"),
            foreground=fg_color,
            font=FONTS['body_bold']
        )

    # ==================== UI RENDERING ====================

    def refresh(self):
        """Refresh/redraw entire UI based on cart model state"""
        # Debug logging
        print(f"[DEBUG] CartUI.refresh() called:")
        print(f"  - sectioning_enabled: {self.cart_model.sectioning_enabled}")
        print(f"  - items count: {len(self.cart_model.items)}")
        print(f"  - sections count: {len(self.cart_model.sections)}")
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Update sectioning checkbox state
        self.sectioning_var.set(self.cart_model.sectioning_enabled)

        # Show/hide manage button based on sectioning state
        if self.cart_model.sectioning_enabled:
            self.btn_gestionar.grid(row=0, column=1, sticky="w", padx=(0, 10))
            self.btn_mover_seccion.grid(row=0, column=2, sticky="w")
        else:
            self.btn_gestionar.grid_forget()
            self.btn_mover_seccion.grid_forget()

        # Render items
        self._render_items()

    def _render_items(self):
        """Render all items in treeview based on sectioning state"""
        if self.cart_model.sectioning_enabled:
            self._render_sectioned_items()
        else:
            self._render_flat_items()

    def _render_flat_items(self):
        """Render items without sections (flat list)"""
        for item in self.cart_model.get_items():
            self._insert_item_node(item, parent="")

    def _render_sectioned_items(self):
        """Render items organized by sections"""
        items_by_section = self.cart_model.get_items_by_section()
        
        print(f"[DEBUG] _render_sectioned_items:")
        print(f"  - items_by_section keys: {list(items_by_section.keys())}")
        for section_name, items in items_by_section.items():
            print(f"    - {section_name}: {len(items)} items")

        # Sort sections by orden
        sorted_sections = sorted(
            self.cart_model.sections.values(),
            key=lambda s: s.orden
        )
        
        print(f"  - sorted_sections: {[s.nombre for s in sorted_sections]}")

        for section in sorted_sections:
            section_items = items_by_section.get(section.nombre, [])

            if not section_items:
                print(f"  - Skipping empty section: {section.nombre}")
                continue  # Skip empty sections

            # Calculate section subtotal
            subtotal = sum(item.subtotal for item in section_items)
            
            print(f"  - Rendering section: {section.nombre} with {len(section_items)} items, subtotal=${subtotal:.2f}")

            # Insert section header
            section_id = self.tree.insert(
                "",
                "end",
                text=f"📂 {section.nombre}",
                values=("", "", "", f"${subtotal:.2f}", ""),
                tags=("section",)
            )

            # Configure section header style
            self.tree.item(section_id, open=True)

            # Insert items under section
            for item in section_items:
                self._insert_item_node(item, parent=section_id)

    def _insert_item_node(self, item: CartItem, parent: str = ""):
        """Insert single item node into treeview"""
        item_id = self.tree.insert(
            parent,
            "end",
            text=f"  {item.nombre}" if parent else item.nombre,
            values=(
                f"{item.cantidad:.2f}",
                item.unidad,
                f"${item.precio_unitario:.2f}",
                f"${item.subtotal:.2f}",
                "🗑️"
            ),
            tags=(item.item_uuid,)
        )
        return item_id

    # ==================== EVENT HANDLERS ====================

    def _on_toggle_sectioning(self):
        """Handle sectioning checkbox toggle"""
        self.cart_model.sectioning_enabled = self.sectioning_var.get()
        self.refresh()
        self._notify_change()

    def _on_manage_sections(self):
        """Open section management dialog"""
        dialog = SectionManagementDialog(
            parent=self.parent_frame,
            cart_model=self.cart_model,
            on_update=lambda: (self.refresh(), self._notify_change())
        )

    def _on_click(self, event):
        """Handle single click on tree"""
        region = self.tree.identify_region(event.x, event.y)
        
        if region == "cell":
            # Get clicked item and column
            item_id = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)

            # Check if clicked on delete column
            if column == "#5":  # Delete column
                # Get item UUID from tags
                tags = self.tree.item(item_id, "tags")
                if tags and len(tags) > 0:
                    item_uuid = tags[0]
                    if item_uuid != "section":  # Not a section header
                        self._confirm_delete_item(item_uuid)

    def _on_double_click(self, event):
        """Handle double click for editing quantity"""
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        # Only handle cantidad column
        if column != "#1":  # cantidad is first column
            return

        # Get item UUID from tags
        tags = self.tree.item(item_id, "tags")
        if not tags or len(tags) == 0 or tags[0] == "section":
            return

        item_uuid = tags[0]
        self._edit_item_quantity(item_uuid)

    def _edit_item_quantity(self, item_uuid: str):
        """Show dialog to edit item quantity"""
        item = self.cart_model.get_item(item_uuid)
        if not item:
            return

        nueva_cantidad = simpledialog.askfloat(
            "Editar Cantidad",
            f"Nueva cantidad para {item.nombre}:",
            initialvalue=item.cantidad,
            minvalue=0.01,
            parent=self.parent_frame
        )

        if nueva_cantidad is not None and nueva_cantidad > 0:
            success = self.cart_model.update_item_quantity(item_uuid, nueva_cantidad)
            if success:
                self.refresh()
                self._notify_change()

    def _edit_item_price(self, item_uuid: str):
        """Show dialog to edit item unit price"""
        item = self.cart_model.get_item(item_uuid)
        if not item:
            return

        nuevo_precio = simpledialog.askfloat(
            "Editar Precio",
            f"Nuevo precio unitario para {item.nombre}:",
            initialvalue=item.precio_unitario,
            minvalue=0.0,
            parent=self.parent_frame
        )

        if nuevo_precio is not None and nuevo_precio >= 0:
            try:
                success = self.cart_model.update_item_price(item_uuid, nuevo_precio)
                if success:
                    self.refresh()
                    self._notify_change()
            except ValueError as e:
                messagebox.showerror(
                    "Error",
                    f"Precio inválido: {str(e)}",
                    parent=self.parent_frame
                )

    def _confirm_delete_item(self, item_uuid: str):
        """Confirm and delete item"""
        item = self.cart_model.get_item(item_uuid)
        if not item:
            return

        if messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar {item.nombre}?",
            parent=self.parent_frame
        ):
            success = self.cart_model.remove_item(item_uuid)
            if success:
                self.refresh()
                self._notify_change()

    # ==================== SECTION OPERATIONS ====================

    def _confirm_delete_section(self, section_id: str):
        """Confirm and delete section"""
        # Get section from model
        section = self.cart_model.sections.get(section_id)
        if not section:
            return

        # Check if it's the default section
        if section.nombre == SectionNames.GENERAL:
            messagebox.showwarning(
                "Sección por defecto",
                "No se puede eliminar la sección GENERAL.",
                parent=self.parent_frame
            )
            return

        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la sección '{section.nombre}'?\n"
            f"Todos sus ítems se moverán a GENERAL.",
            parent=self.parent_frame
        ):
            success = self.cart_model.remove_section(section_id)
            if success:
                self.refresh()
                self._notify_change()

    def _on_move_to_section(self):
        """Handle move selected items to section button click"""
        # Get selected items (only leaf nodes, not section headers)
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(
                "Sin Selección",
                "Por favor seleccione uno o más productos para mover.",
                parent=self.parent_frame
            )
            return

        # Filter only item nodes (not section headers)
        selected_items = []
        for tree_id in selection:
            # Check if it's a leaf node (has parent or has values)
            if self.tree.parent(tree_id) or self.tree.set(tree_id, "cantidad"):
                selected_items.append(tree_id)

        if not selected_items:
            messagebox.showinfo(
                "Sin Productos",
                "Por favor seleccione productos (no secciones) para mover.",
                parent=self.parent_frame
            )
            return

        # Show section selection dialog
        self._show_section_selection_dialog(selected_items)

    def _show_section_selection_dialog(self, tree_ids: list):
        """Show dialog to select target section for moving items"""
        dialog = SectionSelectionDialog(
            parent=self.parent_frame,
            cart_model=self.cart_model,
            on_section_selected=lambda section_name: self._move_items_to_section(tree_ids, section_name)
        )

    def _move_items_to_section(self, tree_ids: list, target_section: str):
        """Move items to target section"""
        moved_count = 0
        
        for tree_id in tree_ids:
            # Get item UUID from tree tags
            tags = self.tree.item(tree_id, "tags")
            if tags and len(tags) > 0:
                item_uuid = tags[0]
                
                # Update item section in model
                success = self.cart_model.update_item_section(item_uuid, target_section)
                if success:
                    moved_count += 1

        if moved_count > 0:
            self.refresh()
            self._notify_change()
            messagebox.showinfo(
                "Éxito",
                f"Se movieron {moved_count} producto(s) a '{target_section}'.",
                parent=self.parent_frame
            )

    def _on_right_click(self, event):
        """Handle right-click to show context menu"""
        # Identify clicked item
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        # Check if it's a product item (not section header)
        tags = self.tree.item(item_id, "tags")
        if not tags or len(tags) == 0:
            return  # It's a section header, don't show menu

        # Select the clicked item if not already selected
        if item_id not in self.tree.selection():
            self.tree.selection_set(item_id)

        # Create context menu
        menu = tk.Menu(self.tree, tearoff=0, font=FONTS['body'])

        # Get selected items count
        selected_items = [
            tid for tid in self.tree.selection()
            if self.tree.item(tid, "tags")  # Only items, not sections
        ]

        if len(selected_items) > 1:
            menu_label = f"Mover {len(selected_items)} productos a..."
        else:
            menu_label = "Mover a sección..."

        # Add "Move to section" submenu
        if self.cart_model.sectioning_enabled:
            move_menu = tk.Menu(menu, tearoff=0, font=FONTS['body'])
            
            # Sort sections by orden
            sorted_sections = sorted(
                self.cart_model.sections.values(),
                key=lambda s: s.orden
            )
            
            for section in sorted_sections:
                move_menu.add_command(
                    label=f"📁 {section.nombre}",
                    command=lambda s=section.nombre: self._move_items_to_section(selected_items, s)
                )
            
            menu.add_cascade(label=menu_label, menu=move_menu)
            menu.add_separator()

        # Add other options
        if len(selected_items) == 1:
            item_uuid = tags[0]
            item = self.cart_model.items.get(item_uuid)
            
            if item:
                menu.add_command(
                    label="✏️ Editar cantidad",
                    command=lambda: self._edit_item_quantity(item_uuid)
                )
                menu.add_command(
                    label="💰 Editar precio",
                    command=lambda: self._edit_item_price(item_uuid)
                )
                menu.add_separator()
                menu.add_command(
                    label="🗑️ Eliminar",
                    command=lambda: self._confirm_delete_item(item_uuid)
                )
        else:
            menu.add_command(
                label=f"🗑️ Eliminar {len(selected_items)} productos",
                command=lambda: self._delete_multiple_items(selected_items)
            )

        # Show menu at cursor position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _delete_multiple_items(self, tree_ids: list):
        """Delete multiple items"""
        if messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar {len(tree_ids)} producto(s) del carrito?",
            parent=self.parent_frame
        ):
            deleted_count = 0
            for tree_id in tree_ids:
                tags = self.tree.item(tree_id, "tags")
                if tags and len(tags) > 0:
                    item_uuid = tags[0]
                    if self.cart_model.remove_item(item_uuid):
                        deleted_count += 1
            
            if deleted_count > 0:
                self.refresh()
                self._notify_change()

    # ==================== UTILITY METHODS ====================

    def _notify_change(self):
        """Notify external callback of cart change"""
        if self.on_change_callback:
            self.on_change_callback()

    def get_cart_model(self) -> CartModel:
        """Get the underlying cart model"""
        return self.cart_model

    def set_cart_model(self, cart_model: CartModel):
        """Set a new cart model and refresh UI"""
        self.cart_model = cart_model
        self.refresh()


class SectionManagementDialog(ctk.CTkToplevel):
    """Dialog for managing cart sections"""

    def __init__(
        self,
        parent,
        cart_model: CartModel,
        on_update: Callable
    ):
        super().__init__(parent)
        self.cart_model = cart_model
        self.on_update = on_update

        # Window configuration
        self.title("Gestionar Secciones")
        self.geometry("500x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Create UI
        self._create_ui()
        self._load_sections()

    def _create_ui(self):
        """Create dialog UI"""
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            container,
            text="📂 Gestionar Secciones del Carrito",
            font=FONTS['title']
        ).pack(pady=(0, 15))

        # Listbox frame
        list_frame = ctk.CTkFrame(container, fg_color=("gray90", "gray20"))
        list_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Listbox
        self.listbox = tk.Listbox(
            list_frame,
            exportselection=False,
            font=FONTS['body'],
            bg=("white" if ctk.get_appearance_mode() == "Light" else "#2b2b2b"),
            fg=("black" if ctk.get_appearance_mode() == "Light" else "white"),
            selectbackground=COLORS['primary'],
            selectforeground="white",
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons panel
        btn_panel = ctk.CTkFrame(container, fg_color="transparent")
        btn_panel.pack(fill="x")

        ctk.CTkButton(
            btn_panel,
            text="➕ Agregar Sección",
            command=self._add_section,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_hover'],
            font=FONTS['body_bold']
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_panel,
            text="❌ Eliminar Seleccionada",
            command=self._remove_selected_section,
            fg_color=COLORS['secondary'],
            hover_color=COLORS['primary_hover'],
            font=FONTS['body_bold']
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_panel,
            text="✅ Cerrar",
            command=self._close,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            font=FONTS['body_bold']
        ).pack(side="right")

    def _load_sections(self):
        """Load sections into listbox"""
        self.listbox.delete(0, tk.END)

        # Sort sections by orden
        sorted_sections = sorted(
            self.cart_model.sections.values(),
            key=lambda s: s.orden
        )

        for section in sorted_sections:
            item_count = self.cart_model.get_item_count_by_section(section.nombre)
            display_text = f"{section.nombre} ({item_count} items)"

            # Mark default section
            if section.nombre == SectionNames.GENERAL:
                display_text += " [PREDETERMINADA]"

            self.listbox.insert(tk.END, display_text)
            # Store section_id as item data (using itemconfig)
            self.listbox.itemconfig(tk.END, fg="gray" if section.nombre == SectionNames.GENERAL else None)

    def _add_section(self):
        """Add new section"""
        nombre = simpledialog.askstring(
            "Nueva Sección",
            "Nombre de la nueva sección:",
            parent=self
        )

        if nombre and nombre.strip():
            nombre = nombre.strip().upper()

            # Check if section already exists
            if self.cart_model.get_section_by_name(nombre):
                messagebox.showwarning(
                    "Sección Duplicada",
                    f"Ya existe una sección llamada '{nombre}'.",
                    parent=self
                )
                return

            # Add section
            orden = len(self.cart_model.sections)
            self.cart_model.add_section(nombre, orden=orden)
            self._load_sections()
            self.on_update()

    def _remove_selected_section(self):
        """Remove selected section"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo(
                "Seleccionar Sección",
                "Por favor seleccione una sección para eliminar.",
                parent=self
            )
            return

        # Get selected section
        index = selection[0]
        sorted_sections = sorted(
            self.cart_model.sections.values(),
            key=lambda s: s.orden
        )

        if index >= len(sorted_sections):
            return

        section = sorted_sections[index]

        # Cannot delete default section
        if section.nombre == SectionNames.GENERAL:
            messagebox.showwarning(
                "Sección Predeterminada",
                "No se puede eliminar la sección GENERAL.",
                parent=self
            )
            return

        # Confirm deletion
        item_count = self.cart_model.get_item_count_by_section(section.nombre)
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar la sección '{section.nombre}'?\n"
            f"Sus {item_count} ítems se moverán a GENERAL.",
            parent=self
        ):
            success = self.cart_model.remove_section(section.section_id)
            if success:
                self._load_sections()
                self.on_update()

    def _close(self):
        """Close dialog"""
        self.destroy()


class SectionSelectionDialog(ctk.CTkToplevel):
    """Dialog for selecting a section to move items to"""

    def __init__(
        self,
        parent,
        cart_model: CartModel,
        on_section_selected: Callable
    ):
        super().__init__(parent)
        self.cart_model = cart_model
        self.on_section_selected = on_section_selected

        # Window configuration
        self.title("Seleccionar Sección")
        self.geometry("400x450")
        self.resizable(True, True)  # Permitir redimensionar
        self.minsize(350, 300)  # Tamaño mínimo
        self.transient(parent)
        self.grab_set()

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create dialog UI"""
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            container,
            text="📂 Seleccione la Sección Destino",
            font=FONTS['title']
        ).grid(row=0, column=0, pady=(0, 15), sticky="ew")

        # Scrollable frame for buttons
        buttons_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, sticky="nsew")

        # Sort sections by orden
        sorted_sections = sorted(
            self.cart_model.sections.values(),
            key=lambda s: s.orden
        )

        # Create button for each section
        for section in sorted_sections:
            item_count = self.cart_model.get_item_count_by_section(section.nombre)
            
            btn = ctk.CTkButton(
                buttons_frame,
                text=f"📁 {section.nombre} ({item_count} items)",
                command=lambda s=section.nombre: self._select_section(s),
                fg_color=COLORS['primary'],
                hover_color=COLORS['primary_hover'],
                height=40,
                font=FONTS['body_bold'],
                corner_radius=8
            )
            btn.pack(fill="x", pady=5)

        # Cancel button
        ctk.CTkButton(
            container,
            text="❌ Cancelar",
            command=self.destroy,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            height=35,
            font=FONTS['body_bold'],
            corner_radius=8
        ).grid(row=2, column=0, sticky="ew", pady=(15, 0))

    def _select_section(self, section_name: str):
        """Handle section selection"""
        self.on_section_selected(section_name)
        self.destroy()