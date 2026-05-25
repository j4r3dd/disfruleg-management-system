# -*- coding: utf-8 -*-
"""
Capa de UI - Vista del Gestor de Clientes
Código de UI puro - delega todas las acciones al controlador.
Implementa diseño responsive adaptable.
"""

import customtkinter as ctk
from tkinter import messagebox
from src.theme import COLORS, FONTS
from src.utils.responsive_manager import ResponsiveMixin
from ..domain.models import ClientSearchCriteria
from .client_controller import ClientController
from .dialogs import GroupManagerDialog, ClientTypeManagerDialog


class ClientManagerView(ResponsiveMixin, ctk.CTkToplevel):
    """Vista principal para gestión de clientes"""

    def __init__(self, root: ctk.CTk, controller: ClientController):
        """Inicializar vista con controlador"""
        super().__init__(root)
        self.withdraw()  # Ocultar ventana inicialmente
        
        # IMPORTANTE: Guardar referencia al controlador PRIMERO
        self.controller = controller

        # Configuración de ventana
        self.title("Gestor de Clientes - Disfruleg")
        
        # Aplicar diseño responsive
        self.make_responsive(
            preset='large',
            force_visible=True
        )

        # Estado inicial - TODOS los atributos antes de llamar métodos
        self.all_clients = []
        self.groups = []
        self.client_types = []
        self.selected_client = None
        self.edit_mode = False
        
        # Configurar responsividad de paneles
        self.current_layout = 'desktop'
        
        # Variables de búsqueda/filtro
        self.search_var = ctk.StringVar()
        self.filter_group_var = ctk.StringVar(value="Todos")
        self.filter_status_var = ctk.StringVar(value="Activos")
        self.filter_discount_var = ctk.StringVar(value="Todos")

        # Inicializar datos ANTES de crear la interfaz
        self.load_initial_data()
        
        # Crear interfaz (esto crea self.detail_panel)
        self.create_interface()
        
        # Cargar clientes DESPUÉS de que todo esté creado
        self.load_clients()
        
        # Configurar el protocolo de cierre de ventana
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # Bind resize event para layout adaptable
        self.bind("<Configure>", self._on_window_resize)
        
        # Mostrar ventana después de crear la interfaz
        self.after(100, self.deiconify)

    def _on_window_resize(self, event):
        """Manejar cambio de tamaño de ventana"""
        if event.widget == self:
            width = self.winfo_width()
            
            # Determinar layout según ancho
            if width < 900:
                new_layout = 'mobile'
            elif width < 1200:
                new_layout = 'tablet'
            else:
                new_layout = 'desktop'
            
            # Solo reconstruir si cambió el layout
            if new_layout != self.current_layout:
                self.current_layout = new_layout
                self._adapt_layout()

    def _adapt_layout(self):
        """Adaptar layout según tamaño de ventana"""
        pass

    def load_initial_data(self):
        """Cargar grupos y tipos de cliente"""
        self.groups = self.controller.get_all_groups()
        self.client_types = self.controller.get_all_client_types()

    def create_interface(self):
        """Crear la UI"""
        self.create_header()
        self.create_toolbar()
        self.create_main_content()
        self.create_status_bar()

    def create_header(self):
        """Crear encabezado con botón de regresar"""
        header_frame = ctk.CTkFrame(
            self,
            fg_color=("#1a1a1a", "#1a1a1a"),
            height=80
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=0)

        # Izquierda: Botón de regresar + Logo + Título
        left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        left_frame.pack(side="left", fill="y")

        # Botón de regresar
        ctk.CTkButton(
            left_frame,
            text="⎋",
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['accent'],
            font=("Arial", 20),
            text_color="white",
            border_width=0,
            command=self.close_window
        ).pack(side="left", padx=(0, 15))

        # Logo
        ctk.CTkLabel(
            left_frame,
            text="👥",
            font=("Arial", 28)
        ).pack(side="left", padx=(0, 15))

        # Título
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="GESTOR DE CLIENTES",
            font=("Arial", 16, "bold"),
            text_color=COLORS['success'],
            anchor="w"
        ).pack(anchor="w")

        self.client_counter_label = ctk.CTkLabel(
            title_frame,
            text="0 clientes",
            font=("Arial", 10),
            text_color="gray60",
            anchor="w"
        )
        self.client_counter_label.pack(anchor="w")

    def create_toolbar(self):
        """Crear barra de herramientas con búsqueda y filtros"""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=15, padx=20)

        # Fila 1: Búsqueda y botón Nuevo Cliente
        row1 = ctk.CTkFrame(toolbar, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))

        # Búsqueda
        search_frame = ctk.CTkFrame(row1, fg_color=("gray90", "gray20"), corner_radius=8)
        search_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Arial", 16)
        ).pack(side="left", padx=(15, 5))

        ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar por nombre, RFC, teléfono, email...",
            textvariable=self.search_var,
            fg_color="transparent",
            border_width=0,
            height=40,
            font=FONTS['body']
        ).pack(side="left", fill="x", expand=True, padx=(0, 15))

        self.search_var.trace("w", lambda *args: self.filter_clients())

        # Botón Nuevo Cliente
        ctk.CTkButton(
            row1,
            text="+ Nuevo Cliente",
            command=self.new_client,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            width=160,
            height=40,
            font=FONTS['body_bold']
        ).pack(side="right", padx=(15, 0))

        # Fila 2: Filtros
        row2 = ctk.CTkFrame(toolbar, fg_color="transparent")
        row2.pack(fill="x")

        ctk.CTkLabel(row2, text="Filtros:", font=FONTS['body_bold']).pack(side="left", padx=(0, 15))

        # Filtro de grupo
        ctk.CTkLabel(row2, text="Grupo:", font=FONTS['body']).pack(side="left", padx=(0, 5))
        group_names = ["Todos"] + [g.clave_grupo for g in self.groups]
        ctk.CTkComboBox(
            row2,
            variable=self.filter_group_var,
            values=group_names,
            width=150,
            height=32,
            command=lambda x: self.filter_clients()
        ).pack(side="left", padx=(0, 15))

        # Filtro de estado
        ctk.CTkLabel(row2, text="Estado:", font=FONTS['body']).pack(side="left", padx=(0, 5))
        ctk.CTkComboBox(
            row2,
            variable=self.filter_status_var,
            values=["Todos", "Activos", "Inactivos"],
            width=120,
            height=32,
            command=lambda x: self.filter_clients()
        ).pack(side="left", padx=(0, 15))

        # Filtro de descuento
        ctk.CTkLabel(row2, text="Descuento:", font=FONTS['body']).pack(side="left", padx=(0, 5))
        ctk.CTkComboBox(
            row2,
            variable=self.filter_discount_var,
            values=["Todos", "Sin descuento", "1-10%", "11-20%", "21-50%", "51%+"],
            width=140,
            height=32,
            command=lambda x: self.filter_clients()
        ).pack(side="left", padx=(0, 15))

        # Botón limpiar filtros
        ctk.CTkButton(
            row2,
            text="Limpiar Filtros",
            command=self.clear_filters,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            width=120,
            height=32,
            font=FONTS['small']
        ).pack(side="right")

    def create_main_content(self):
        """Crear vista híbrida: lista de clientes + panel de detalles"""
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Izquierda: Lista de Clientes
        list_container = ctk.CTkFrame(main_container, fg_color=("gray95", "gray15"))
        list_container.pack(side="left", fill="both", expand=False, padx=(0, 10))
        list_container.configure(width=550)

        list_header = ctk.CTkFrame(list_container, fg_color=("gray85", "gray25"), height=40)
        list_header.pack(fill="x")
        list_header.pack_propagate(False)

        ctk.CTkLabel(
            list_header,
            text="CLIENTES",
            font=FONTS['body_bold'],
            anchor="w"
        ).pack(side="left", padx=15, pady=10)

        self.clients_list_frame = ctk.CTkScrollableFrame(
            list_container,
            fg_color="transparent"
        )
        self.clients_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Derecha: Panel de Detalles - CREAR el frame
        self.detail_panel = ctk.CTkFrame(main_container, fg_color=("gray95", "gray15"))
        self.detail_panel.pack(side="right", fill="both", expand=True)

        # Crear contenido inicial del panel
        self.create_detail_panel()

    def create_detail_panel(self):
        """Crear o actualizar el panel de detalles"""
        # Verificar que detail_panel existe
        if not hasattr(self, 'detail_panel'):
            return
            
        # Limpiar widgets existentes
        for widget in self.detail_panel.winfo_children():
            widget.destroy()

        if self.selected_client is None:
            # Estado vacío
            empty_container = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
            empty_container.pack(expand=True)

            ctk.CTkLabel(empty_container, text="📋", font=("Arial", 64)).pack(pady=(0, 20))
            ctk.CTkLabel(
                empty_container,
                text="Selecciona un cliente",
                font=FONTS['header'],
                text_color="gray"
            ).pack()
            ctk.CTkLabel(
                empty_container,
                text="Selecciona un cliente de la lista para ver los detalles",
                font=FONTS['body'],
                text_color="gray60"
            ).pack(pady=(10, 0))
        else:
            self.create_client_details()

    def create_client_details(self):
        """Crear vista de detalles del cliente"""
        header = ctk.CTkFrame(self.detail_panel, fg_color=("gray85", "gray25"), height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Nombre del cliente
        name_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        name_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            name_frame,
            text=self.selected_client.nombre_cliente,
            font=FONTS['header'],
            anchor="w"
        ).pack(side="left")

        # Badge de estado
        status_color = COLORS['success'] if self.selected_client.activo else COLORS['accent']
        status_text = "ACTIVO" if self.selected_client.activo else "INACTIVO"

        ctk.CTkLabel(
            name_frame,
            text=status_text,
            font=FONTS['small'],
            text_color="white",
            fg_color=status_color,
            corner_radius=12,
            width=80,
            height=24
        ).pack(side="left", padx=10)

        # Botones de acción
        # Botones de acción
        btn_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        btn_frame.pack(side="right")

        if self.edit_mode:
            ctk.CTkButton(
                btn_frame,
                text="Guardar",
                command=self.save_client,
                fg_color=COLORS['success'],
                hover_color=COLORS['success_hover'],
                width=100,
                height=35
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                btn_frame,
                text="Cancelar",
                command=self.cancel_edit,
                fg_color=("gray70", "gray30"),
                width=100,
                height=35
            ).pack(side="left", padx=5)
        else:
            ctk.CTkButton(
                btn_frame,
                text="Editar",
                command=self.enable_edit_mode,
                fg_color=COLORS['primary'],
                hover_color=COLORS['primary_hover'],
                width=100,
                height=35
            ).pack(side="left", padx=5)

            # BOTÓN DESACTIVAR/ACTIVAR (nuevo)
            if self.selected_client.activo:
                ctk.CTkButton(
                    btn_frame,
                    text="Desactivar",
                    command=self.deactivate_selected_client,
                    fg_color="#FFA500",  # Naranja
                    hover_color="#FF8C00",
                    width=120,
                    height=35
                ).pack(side="left", padx=5)
            else:
                ctk.CTkButton(
                    btn_frame,
                    text="Activar",
                    command=self.activate_selected_client,
                    fg_color=COLORS['success'],
                    hover_color=COLORS['success_hover'],
                    width=120,
                    height=35
                ).pack(side="left", padx=5)

                # Mostrar botón Eliminar solo si está inactivo
                ctk.CTkButton(
                    btn_frame,
                    text="Eliminar",
                    command=self.delete_selected_client,
                    fg_color=COLORS['accent'],
                    hover_color="#c0392b",
                    width=100,
                    height=35
                ).pack(side="left", padx=5)

        # Contenido
        content = ctk.CTkScrollableFrame(self.detail_panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Crear campos del formulario
        self.create_client_form(content)

    def create_client_form(self, parent):
        """Crear campos del formulario del cliente"""
        # Sección 1: Información General
        section1 = ctk.CTkFrame(parent, fg_color=("white", "gray20"), corner_radius=10)
        section1.pack(fill="x", pady=(0, 15))

        section1_content = ctk.CTkFrame(section1, fg_color="transparent")
        section1_content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(section1_content, text="INFORMACIÓN GENERAL", font=FONTS['subheader']).pack(anchor="w", pady=(0, 10))

        # Campos de entrada para información general
        general_fields = [
            ("nombre_cliente", "Nombre del cliente", True),
            ("telefono", "Teléfono", False),
            ("correo", "Correo electrónico", False),
        ]

        for field_name, label, required in general_fields:
            field_frame = ctk.CTkFrame(section1_content, fg_color="transparent")
            field_frame.pack(fill="x", pady=8)

            label_text = f"{label} *" if required else label
            ctk.CTkLabel(
                field_frame,
                text=label_text,
                font=FONTS['body'],
                text_color=COLORS['accent'] if required else "gray60",
                width=180,
                anchor="w"
            ).pack(side="left", padx=(0, 10))

            value = getattr(self.selected_client, field_name, '')
            entry = ctk.CTkEntry(field_frame, width=400, height=35)
            entry.insert(0, str(value) if value else '')

            if not self.edit_mode:
                entry.configure(state="disabled")

            entry.pack(side="left", fill="x", expand=True)
            setattr(self, f"{field_name}_entry", entry)

        # Selector de grupo en sección general
        self.create_group_selector(section1_content)

        # Sección 2: Información Fiscal
        section2 = ctk.CTkFrame(parent, fg_color=("white", "gray20"), corner_radius=10)
        section2.pack(fill="x", pady=(0, 15))

        section2_content = ctk.CTkFrame(section2, fg_color="transparent")
        section2_content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(section2_content, text="INFORMACIÓN FISCAL (OPCIONAL)", font=FONTS['subheader']).pack(anchor="w", pady=(0, 10))

        fiscal_fields = [
            ("rfc", "RFC", False),
            ("razon_social", "Razón Social", False),
            ("regimen_fiscal", "Régimen Fiscal", False),
            ("codigo_postal", "Código Postal", False),
        ]

        for field_name, label, required in fiscal_fields:
            field_frame = ctk.CTkFrame(section2_content, fg_color="transparent")
            field_frame.pack(fill="x", pady=8)

            ctk.CTkLabel(
                field_frame,
                text=label,
                font=FONTS['body'],
                text_color="gray60",
                width=180,
                anchor="w"
            ).pack(side="left", padx=(0, 10))

            value = getattr(self.selected_client, field_name, '')
            entry = ctk.CTkEntry(field_frame, width=400, height=35)
            entry.insert(0, str(value) if value else '')

            if not self.edit_mode:
                entry.configure(state="disabled")

            entry.pack(side="left", fill="x", expand=True)
            setattr(self, f"{field_name}_entry", entry)

        # Dirección fiscal (área de texto)
        field_frame = ctk.CTkFrame(section2_content, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)

        ctk.CTkLabel(
            field_frame,
            text="Dirección Fiscal",
            font=FONTS['body'],
            text_color="gray60",
            width=180,
            anchor="w"
        ).pack(side="left", padx=(0, 10), anchor="n")

        value = getattr(self.selected_client, 'direccion_fiscal', '')
        text_widget = ctk.CTkTextbox(field_frame, width=400, height=60)
        text_widget.insert("1.0", str(value) if value else '')

        if not self.edit_mode:
            text_widget.configure(state="disabled")

        text_widget.pack(side="left", fill="x", expand=True)
        self.direccion_fiscal_text = text_widget

        # Sección 3: Notas
        section3 = ctk.CTkFrame(parent, fg_color=("white", "gray20"), corner_radius=10)
        section3.pack(fill="x", pady=(0, 15))

        section3_content = ctk.CTkFrame(section3, fg_color="transparent")
        section3_content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(section3_content, text="NOTAS ADICIONALES", font=FONTS['subheader']).pack(anchor="w", pady=(0, 10))

        field_frame = ctk.CTkFrame(section3_content, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)

        ctk.CTkLabel(
            field_frame,
            text="Notas",
            font=FONTS['body'],
            text_color="gray60",
            width=180,
            anchor="w"
        ).pack(side="left", padx=(0, 10), anchor="n")

        value = getattr(self.selected_client, 'notas', '')
        text_widget = ctk.CTkTextbox(field_frame, width=400, height=80)
        text_widget.insert("1.0", str(value) if value else '')

        if not self.edit_mode:
            text_widget.configure(state="disabled")

        text_widget.pack(side="left", fill="x", expand=True)
        self.notas_text = text_widget

    def create_group_selector(self, parent):
        """Crear selector de grupo"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)

        ctk.CTkLabel(
            field_frame,
            text="Grupo *",
            font=FONTS['body'],
            width=180,
            anchor="w"
        ).pack(side="left", padx=(0, 10))

        group_names = [g.clave_grupo for g in self.groups]
        self.grupo_combo = ctk.CTkComboBox(
            field_frame,
            values=group_names if group_names else ["No hay grupos"],
            width=400,
            height=35,
            state="normal" if self.edit_mode else "disabled"
        )

        if self.selected_client and self.selected_client.clave_grupo:
            self.grupo_combo.set(self.selected_client.clave_grupo)
        elif group_names:
            self.grupo_combo.set(group_names[0])

        self.grupo_combo.pack(side="left", fill="x", expand=True)

    def create_status_bar(self):
        """Crear barra de estado en la parte inferior"""
        self.status_frame = ctk.CTkFrame(
            self,
            fg_color=("gray85", "gray25"),
            height=35
        )
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)

        status_content = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        status_content.pack(fill="both", expand=True, padx=20, pady=0)

        self.status_label = ctk.CTkLabel(
            status_content,
            text="Listo",
            font=FONTS['small'],
            anchor="w"
        )
        self.status_label.pack(side="left", pady=8)

        # Botones de acceso rápido
        btn_frame = ctk.CTkFrame(status_content, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="Administrar Grupos",
            command=self.manage_groups,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            width=140,
            height=28,
            font=FONTS['small']
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Administrar Tipos",
            command=self.manage_client_types,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            width=140,
            height=28,
            font=FONTS['small']
        ).pack(side="left", padx=5)

    # Operaciones de datos
    def load_clients(self):
        """Cargar todos los clientes"""
        self.all_clients = self.controller.get_all_clients()
        self.filter_clients()

    def filter_clients(self):
        """Aplicar filtros y actualizar lista de clientes"""
        criteria = ClientSearchCriteria(
            search_text=self.search_var.get(),
            group_filter=self.filter_group_var.get(),
            status_filter=self.filter_status_var.get(),
            discount_filter=self.filter_discount_var.get()
        )

        filtered = self.controller.search_clients(criteria)
        self.display_client_list(filtered)
        self.update_client_counter(len(filtered), len(self.all_clients))

    def display_client_list(self, clients):
        """Mostrar clientes filtrados en la lista"""
        # Limpiar existentes
        for widget in self.clients_list_frame.winfo_children():
            widget.destroy()

        # Mostrar clientes
        for client in clients:
            self.create_client_card(client)

        # Estado vacío
        if not clients:
            empty = ctk.CTkFrame(self.clients_list_frame, fg_color="transparent")
            empty.pack(expand=True, pady=50)
            ctk.CTkLabel(
                empty,
                text="No se encontraron clientes",
                font=FONTS['body'],
                text_color="gray"
            ).pack()

    def create_client_card(self, client):
        """Crear una tarjeta de cliente en la lista"""
        is_selected = self.selected_client and self.selected_client.id_cliente == client.id_cliente

        card_color = COLORS['primary'] if is_selected else ("white", "gray20")
        text_color = "white" if is_selected else None

        card = ctk.CTkFrame(
            self.clients_list_frame,
            fg_color=card_color,
            corner_radius=8,
            cursor="hand2"
        )
        card.pack(fill="x", pady=3, padx=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # Nombre del cliente
        ctk.CTkLabel(
            content,
            text=client.nombre_cliente,
            font=FONTS['body_bold'],
            text_color=text_color,
            anchor="w"
        ).pack(anchor="w")

        # Información adicional
        info_parts = []
        if client.telefono:
            info_parts.append(client.telefono)
        if client.clave_grupo:
            info_parts.append(f"Grupo: {client.clave_grupo}")
        if client.descuento:
            info_parts.append(f"{client.descuento}% desc.")

        info_text = " • ".join(info_parts) if info_parts else "Sin información adicional"

        ctk.CTkLabel(
            content,
            text=info_text,
            font=FONTS['small'],
            text_color="gray80" if is_selected else "gray60",
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))

        # Evento de clic
        card.bind("<Button-1>", lambda e, c=client: self.select_client(c))
        content.bind("<Button-1>", lambda e, c=client: self.select_client(c))
        for widget in content.winfo_children():
            widget.bind("<Button-1>", lambda e, c=client: self.select_client(c))

    def select_client(self, client):
        """Seleccionar un cliente y mostrar detalles"""
        if self.edit_mode:
            if messagebox.askyesno(
                "Cambios sin guardar",
                "Tiene cambios sin guardar. ¿Desea descartarlos?"
            ):
                self.edit_mode = False
            else:
                return

        self.selected_client = client
        self.edit_mode = False
        self.create_detail_panel()
        self.filter_clients()

    def clear_filters(self):
        """Limpiar todos los filtros"""
        self.search_var.set("")
        self.filter_group_var.set("Todos")
        self.filter_status_var.set("Activos")
        self.filter_discount_var.set("Todos")
        self.filter_clients()

    def update_client_counter(self, shown, total):
        """Actualizar contador de clientes en el encabezado"""
        if shown == total:
            self.client_counter_label.configure(text=f"{total} clientes")
        else:
            self.client_counter_label.configure(text=f"{shown} de {total} clientes")

    def new_client(self):
        """Crear un nuevo cliente"""
        if self.edit_mode:
            if not messagebox.askyesno(
                "Cambios sin guardar",
                "Tiene cambios sin guardar. ¿Desea descartarlos?"
            ):
                return

        if not self.groups:
            messagebox.showerror("Error", "No hay grupos disponibles. Por favor cree un grupo primero.")
            return

        self.selected_client = type('obj', (object,), {
            'id_cliente': None,
            'nombre_cliente': '',
            'id_grupo': self.groups[0].id_grupo,
            'telefono': '',
            'correo': '',
            'rfc': '',
            'razon_social': '',
            'regimen_fiscal': '',
            'codigo_postal': '',
            'direccion_fiscal': '',
            'notas': '',
            'activo': True,
            'clave_grupo': self.groups[0].clave_grupo,
            'nombre_tipo': self.groups[0].nombre_tipo,
            'descuento': self.groups[0].descuento
        })()

        self.edit_mode = True
        self.create_detail_panel()

    def enable_edit_mode(self):
        """Habilitar modo de edición"""
        self.edit_mode = True
        self.create_detail_panel()

    def cancel_edit(self):
        """Cancelar modo de edición"""
        if self.selected_client.id_cliente is None:
            self.selected_client = None
        self.edit_mode = False
        self.load_clients()
        self.create_detail_panel()

    def save_client(self):
        """Guardar cambios del cliente"""
        try:
            # Obtener datos del formulario de todos los campos
            client_data = {
                'nombre_cliente': self.nombre_cliente_entry.get().strip(),
                'telefono': self.telefono_entry.get().strip() or None,
                'correo': self.correo_entry.get().strip() or None,
                'rfc': getattr(self, 'rfc_entry', None) and self.rfc_entry.get().strip() or None,
                'razon_social': getattr(self, 'razon_social_entry', None) and self.razon_social_entry.get().strip() or None,
                'regimen_fiscal': getattr(self, 'regimen_fiscal_entry', None) and self.regimen_fiscal_entry.get().strip() or None,
                'codigo_postal': getattr(self, 'codigo_postal_entry', None) and self.codigo_postal_entry.get().strip() or None,
                'direccion_fiscal': getattr(self, 'direccion_fiscal_text', None) and self.direccion_fiscal_text.get("1.0", "end-1c").strip() or None,
                'notas': getattr(self, 'notas_text', None) and self.notas_text.get("1.0", "end-1c").strip() or None,
            }

            # Obtener ID de grupo del grupo seleccionado
            selected_group_name = self.grupo_combo.get()
            group_id = next(
                (g.id_grupo for g in self.groups if g.clave_grupo == selected_group_name),
                None
            )

            if not group_id:
                messagebox.showerror("Error", "Por favor seleccione un grupo válido")
                return

            client_data['id_grupo'] = group_id

            # Crear o actualizar
            if self.selected_client.id_cliente is None:
                new_client = self.controller.create_client(client_data)
                if new_client:
                    self.selected_client = new_client
                    # Asegurar que la ventana regrese al frente después del messagebox
                    self.lift()
                    self.focus_force()
            else:
                updated_client = self.controller.update_client(
                    self.selected_client.id_cliente,
                    client_data
                )
                if updated_client:
                    self.selected_client = updated_client
                    # Asegurar que la ventana regrese al frente después del messagebox
                    self.lift()
                    self.focus_force()

            self.edit_mode = False
            self.load_clients()
            self.create_detail_panel()

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {str(e)}")

    def delete_selected_client(self):
        """Eliminar el cliente seleccionado actualmente"""
        if not self.selected_client or self.selected_client.id_cliente is None:
            return

        # Llamar al controlador para eliminar (maneja diálogos de confirmación)
        success = self.controller.delete_client(self.selected_client.id_cliente)

        if success:
            # Limpiar selección y refrescar
            self.selected_client = None
            self.edit_mode = False
            self.load_clients()
            self.create_detail_panel()

    def manage_groups(self):
        """Abrir diálogo de gestión de grupos"""
        dialog = GroupManagerDialog(self, self.controller)
        dialog.show()
        # Recargar grupos después de cerrar el diálogo
        self.load_initial_data()

    def manage_client_types(self):
        """Abrir diálogo de gestión de tipos de cliente"""
        dialog = ClientTypeManagerDialog(self, self.controller)
        dialog.show()
        # Recargar tipos después de cerrar el diálogo
        self.load_initial_data()

    def deactivate_selected_client(self):
        """Desactivar el cliente seleccionado"""
        if not self.selected_client or self.selected_client.id_cliente is None:
            return

        # Confirmación
        if messagebox.askyesno(
            "Desactivar Cliente",
            f"¿Desactivar a {self.selected_client.nombre_cliente}?\n\nLos datos se preservarán."
        ):
            try:
                self.controller.deactivate_client(self.selected_client.id_cliente)
                messagebox.showinfo("Éxito", "Cliente desactivado correctamente")
                self.load_clients()
                self.create_detail_panel()
            except Exception as e:
                messagebox.showerror("Error", f"Error al desactivar: {str(e)}")

    def activate_selected_client(self):
        """Activar el cliente seleccionado"""
        if not self.selected_client or self.selected_client.id_cliente is None:
            return

        try:
            self.controller.activate_client(self.selected_client.id_cliente)
            messagebox.showinfo("Éxito", "Cliente activado correctamente")
            self.load_clients()
            self.create_detail_panel()
        except Exception as e:
            messagebox.showerror("Error", f"Error al activar: {str(e)}")

    def close_window(self):
        """Cerrar ventana correctamente"""
        try:
            # Si hay cambios sin guardar, preguntar
            if self.edit_mode:
                if not messagebox.askyesno(
                    "Cambios sin guardar",
                    "Tiene cambios sin guardar. ¿Desea cerrar de todos modos?"
                ):
                    return
            
            # Limpiar recursos del ResponsiveMixin
            if hasattr(self, '_cleanup_responsive'):
                self._cleanup_responsive()
            
            # Unbind eventos para evitar referencias
            try:
                self.unbind("<Configure>")
            except:
                pass
            
            # Cancelar todos los callbacks 'after' pendientes
            self._cancel_all_callbacks(self)
            
            # Limpiar referencias
            self.all_clients = []
            self.groups = []
            self.client_types = []
            self.selected_client = None
            
            # Destruir widgets hijos primero
            for widget in self.winfo_children():
                try:
                    # Cancelar callbacks en widgets hijos
                    self._cancel_all_callbacks(widget)
                    widget.destroy()
                except:
                    pass
            
            # Forzar actualización antes de destruir
            try:
                self.update_idletasks()
            except:
                pass
            
            # Destruir la ventana
            self.destroy()
            
        except Exception as e:
            print(f"Error al cerrar ventana: {e}")
            # Forzar destrucción en caso de error
            try:
                self.destroy()
            except:
                pass
    
    def _cancel_all_callbacks(self, widget):
        """Cancelar todos los callbacks 'after' de un widget y sus hijos recursivamente"""
        try:
            # Cancelar callbacks conocidos del widget
            if hasattr(widget, '_responsive_after_ids'):
                for after_id in widget._responsive_after_ids:
                    try:
                        self.after_cancel(after_id)
                    except:
                        pass
            
            if hasattr(widget, '_after_ids'):
                for after_id in widget._after_ids:
                    try:
                        self.after_cancel(after_id)
                    except:
                        pass
            
            # Recursivamente cancelar en hijos
            try:
                for child in widget.winfo_children():
                    self._cancel_all_callbacks(child)
            except:
                pass
                
        except Exception as e:
            # Silenciosamente ignorar errores aquí
            pass