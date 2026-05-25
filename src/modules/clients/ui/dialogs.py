# -*- coding: utf-8 -*-
"""
Capa de UI - Ventanas de diálogo para gestión de grupos y tipos de cliente
Implementación responsive y traducida al español
CORREGIDO: Manejo correcto del cierre de ventanas
"""

import customtkinter as ctk
from tkinter import messagebox
from src.theme import COLORS, FONTS
from src.utils.responsive_manager import ResponsiveMixin
from .client_controller import ClientController


class GroupManagerDialog(ResponsiveMixin, ctk.CTkToplevel):
    """Diálogo para gestión de grupos"""

    def __init__(self, parent, controller: ClientController):
        super().__init__(parent)
        self.controller = controller
        self._is_closing = False
        
        self.title("Administrar Grupos")
        self.transient(parent)
        self.grab_set()

        # Aplicar diseño responsive
        self.make_responsive(
            preset='medium',
            force_visible=True
        )

        self.create_ui()
        
        # Configurar protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)

    def create_ui(self):
        """Crear interfaz de usuario"""
        # Encabezado
        header = ctk.CTkFrame(self, fg_color=COLORS['secondary'], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="GRUPOS DE CLIENTES",
            font=FONTS['header'],
            text_color="white"
        ).pack(pady=15)

        # Lista scrollable
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=("gray95", "gray15"))
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.refresh_groups()

        # Botones inferiores
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", pady=15, padx=20)

        ctk.CTkButton(
            button_frame,
            text="+ Agregar Grupo",
            command=self.add_group,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            width=150,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cerrar",
            command=self.close_dialog,
            fg_color=("gray70", "gray30"),
            width=150,
            height=35
        ).pack(side="right", padx=5)

    def show(self):
        """Mostrar el diálogo"""
        self.wait_window()

    def close_dialog(self):
        """Cerrar el diálogo correctamente"""
        if self._is_closing:
            return
        self._is_closing = True
        
        try:
            # Liberar el grab
            self.grab_release()
            # Destruir la ventana
            self.destroy()
        except Exception as e:
            print(f"Error al cerrar GroupManagerDialog: {e}")

    def refresh_groups(self):
        """Refrescar lista de grupos"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        groups = self.controller.get_all_groups()

        if not groups:
            empty = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            empty.pack(expand=True, pady=50)
            ctk.CTkLabel(
                empty,
                text="No hay grupos disponibles",
                font=FONTS['body'],
                text_color="gray"
            ).pack()
            return

        for idx, group in enumerate(groups):
            row_color = ("white", "gray20") if idx % 2 == 0 else ("gray95", "gray18")
            row = ctk.CTkFrame(self.list_frame, fg_color=row_color, corner_radius=8)
            row.pack(fill="x", pady=3, padx=5)

            content = ctk.CTkFrame(row, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=12)

            tipo_info = f" - {group.nombre_tipo} ({group.descuento}%)" if group.nombre_tipo else " - Sin tipo asignado"

            info_frame = ctk.CTkFrame(content, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                info_frame,
                text=group.clave_grupo,
                font=FONTS['body_bold'],
                anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                info_frame,
                text=tipo_info,
                font=FONTS['small'],
                text_color="gray60",
                anchor="w"
            ).pack(anchor="w")

            if group.descripcion:
                ctk.CTkLabel(
                    info_frame,
                    text=f"📝 {group.descripcion}",
                    font=FONTS['small'],
                    text_color="gray50",
                    anchor="w"
                ).pack(anchor="w", pady=(2, 0))

            btn_frame = ctk.CTkFrame(content, fg_color="transparent")
            btn_frame.pack(side="right")

            ctk.CTkButton(
                btn_frame,
                text="Editar",
                width=70,
                height=30,
                fg_color=COLORS['primary'],
                hover_color=COLORS['primary_hover'],
                command=lambda g=group: self.edit_group(g)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                btn_frame,
                text="Eliminar",
                width=70,
                height=30,
                fg_color=COLORS['accent'],
                hover_color="#C0392B",
                command=lambda g=group: self.delete_group(g)
            ).pack(side="left", padx=3)

    def add_group(self):
        """Agregar nuevo grupo"""
        dialog = GroupFormDialog(self, self.controller, None)
        dialog.show()
        self.refresh_groups()

    def edit_group(self, group):
        """Editar grupo existente"""
        dialog = GroupFormDialog(self, self.controller, group)
        dialog.show()
        self.refresh_groups()

    def delete_group(self, group):
        """Eliminar grupo"""
        if self.controller.delete_group(group.id_grupo):
            self.refresh_groups()


class GroupFormDialog(ResponsiveMixin, ctk.CTkToplevel):
    """Formulario de diálogo para agregar/editar grupos"""

    def __init__(self, parent, controller: ClientController, group=None):
        super().__init__(parent)
        self.controller = controller
        self.group = group
        self._is_closing = False
        
        self.title("Nuevo Grupo" if group is None else "Editar Grupo")
        self.transient(parent)
        self.grab_set()

        # Aplicar diseño responsive
        self.make_responsive(
            preset='dialog',
            force_visible=True
        )

        self.create_ui()
        
        # Configurar protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)

    def create_ui(self):
        """Crear interfaz de usuario"""
        # Encabezado
        header = ctk.CTkFrame(self, fg_color=COLORS['primary'])
        header.pack(fill="x")
        title = "NUEVO GRUPO" if self.group is None else "EDITAR GRUPO"
        ctk.CTkLabel(header, text=title, font=FONTS['subtitle'], text_color="white").pack(pady=15)

        # Formulario
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(form, text="Clave del Grupo *", font=FONTS['body'], anchor="w").pack(fill="x", pady=(0, 5))
        self.group_name_var = ctk.StringVar(value=self.group.clave_grupo if self.group else "")
        ctk.CTkEntry(form, textvariable=self.group_name_var, height=35).pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(form, text="Descripción", font=FONTS['body'], anchor="w").pack(fill="x", pady=(0, 5))
        self.description_var = ctk.StringVar(value=self.group.descripcion if self.group and self.group.descripcion else "")
        ctk.CTkEntry(form, textvariable=self.description_var, height=35).pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(form, text="Tipo de Cliente *", font=FONTS['body'], anchor="w").pack(fill="x", pady=(0, 5))

        client_types = self.controller.get_all_client_types()
        if not client_types:
            ctk.CTkLabel(form, text="No hay tipos disponibles. Cree uno primero.", text_color=COLORS['accent']).pack()
            
            # Botón de cerrar si no hay tipos
            ctk.CTkButton(
                form,
                text="Cerrar",
                command=self.close_dialog,
                fg_color=("gray70", "gray30"),
                width=120,
                height=35
            ).pack(pady=15)
            return

        type_names = [f"{t.nombre_tipo} ({t.descuento}%)" for t in client_types]
        self.type_var = ctk.StringVar(value=type_names[0])

        # Establecer valor actual si se está editando
        if self.group:
            for i, t in enumerate(client_types):
                if t.id_tipo_cliente == self.group.id_tipo_cliente:
                    self.type_var.set(type_names[i])
                    break

        ctk.CTkComboBox(form, variable=self.type_var, values=type_names, state="readonly", height=35).pack(fill="x")

        # Botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self.save,
            fg_color=COLORS['success'],
            width=120,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.close_dialog,
            fg_color=COLORS['accent'],
            width=120,
            height=35
        ).pack(side="left", padx=5)

    def show(self):
        """Mostrar el diálogo"""
        self.wait_window()

    def close_dialog(self):
        """Cerrar el diálogo correctamente"""
        if self._is_closing:
            return
        self._is_closing = True
        
        try:
            # Liberar el grab
            self.grab_release()
            # Destruir la ventana
            self.destroy()
        except Exception as e:
            print(f"Error al cerrar GroupFormDialog: {e}")

    def save(self):
        """Guardar grupo"""
        group_name = self.group_name_var.get().strip()
        description = self.description_var.get().strip() or None

        if not group_name:
            messagebox.showerror("Error", "La clave del grupo es requerida")
            return

        client_types = self.controller.get_all_client_types()
        type_names = [f"{t.nombre_tipo} ({t.descuento}%)" for t in client_types]
        selected_index = type_names.index(self.type_var.get())
        selected_type_id = client_types[selected_index].id_tipo_cliente

        group_data = {
            'clave_grupo': group_name,
            'descripcion': description,
            'id_tipo_cliente': selected_type_id
        }

        if self.group is None:
            # Crear
            if self.controller.create_group(group_data):
                self.close_dialog()
        else:
            # Actualizar
            if self.controller.update_group(self.group.id_grupo, group_data):
                self.close_dialog()


class ClientTypeManagerDialog(ResponsiveMixin, ctk.CTkToplevel):
    """Diálogo para gestión de tipos de cliente"""

    def __init__(self, parent, controller: ClientController):
        super().__init__(parent)
        self.controller = controller
        self._is_closing = False
        
        self.title("Administrar Tipos de Cliente")
        self.transient(parent)
        self.grab_set()

        # Aplicar diseño responsive
        self.make_responsive(
            preset='medium',
            force_visible=True
        )

        self.create_ui()
        
        # Configurar protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)

    def create_ui(self):
        """Crear interfaz de usuario"""
        # Encabezado
        header = ctk.CTkFrame(self, fg_color=COLORS['secondary'], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="TIPOS DE CLIENTE",
            font=FONTS['header'],
            text_color="white"
        ).pack(pady=15)

        # Lista scrollable
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=("gray95", "gray15"))
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.refresh_types()

        # Botones inferiores
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", pady=15, padx=20)

        ctk.CTkButton(
            button_frame,
            text="+ Agregar Tipo",
            command=self.add_type,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            width=150,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cerrar",
            command=self.close_dialog,
            fg_color=("gray70", "gray30"),
            width=150,
            height=35
        ).pack(side="right", padx=5)

    def show(self):
        """Mostrar el diálogo"""
        self.wait_window()

    def close_dialog(self):
        """Cerrar el diálogo correctamente"""
        if self._is_closing:
            return
        self._is_closing = True
        
        try:
            # Liberar el grab
            self.grab_release()
            # Destruir la ventana
            self.destroy()
        except Exception as e:
            print(f"Error al cerrar ClientTypeManagerDialog: {e}")

    def refresh_types(self):
        """Refrescar lista de tipos"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        types = self.controller.get_all_client_types()

        if not types:
            empty = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            empty.pack(expand=True, pady=50)
            ctk.CTkLabel(
                empty,
                text="No hay tipos de cliente disponibles",
                font=FONTS['body'],
                text_color="gray"
            ).pack()
            return

        for idx, client_type in enumerate(types):
            row_color = ("white", "gray20") if idx % 2 == 0 else ("gray95", "gray18")
            row = ctk.CTkFrame(self.list_frame, fg_color=row_color, corner_radius=8)
            row.pack(fill="x", pady=3, padx=5)

            content = ctk.CTkFrame(row, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=12)

            info_frame = ctk.CTkFrame(content, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                info_frame,
                text=client_type.nombre_tipo,
                font=FONTS['body_bold'],
                anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                info_frame,
                text=f"Descuento: {client_type.descuento}%",
                font=FONTS['small'],
                text_color="gray60",
                anchor="w"
            ).pack(anchor="w")

            btn_frame = ctk.CTkFrame(content, fg_color="transparent")
            btn_frame.pack(side="right")

            ctk.CTkButton(
                btn_frame,
                text="Editar",
                width=70,
                height=30,
                fg_color=COLORS['primary'],
                hover_color=COLORS['primary_hover'],
                command=lambda t=client_type: self.edit_type(t)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                btn_frame,
                text="Eliminar",
                width=70,
                height=30,
                fg_color=COLORS['accent'],
                hover_color="#C0392B",
                command=lambda t=client_type: self.delete_type(t)
            ).pack(side="left", padx=3)

    def add_type(self):
        """Agregar nuevo tipo"""
        dialog = ClientTypeFormDialog(self, self.controller, None)
        dialog.show()
        self.refresh_types()

    def edit_type(self, client_type):
        """Editar tipo existente"""
        dialog = ClientTypeFormDialog(self, self.controller, client_type)
        dialog.show()
        self.refresh_types()

    def delete_type(self, client_type):
        """Eliminar tipo"""
        if self.controller.delete_client_type(client_type.id_tipo_cliente):
            self.refresh_types()


class ClientTypeFormDialog(ResponsiveMixin, ctk.CTkToplevel):
    """Formulario de diálogo para agregar/editar tipos de cliente"""

    def __init__(self, parent, controller: ClientController, client_type=None):
        super().__init__(parent)
        self.controller = controller
        self.client_type = client_type
        self._is_closing = False
        
        self.title("Nuevo Tipo de Cliente" if client_type is None else "Editar Tipo de Cliente")
        self.transient(parent)
        self.grab_set()

        # Aplicar diseño responsive
        self.make_responsive(
            preset='dialog',
            force_visible=True
        )

        self.create_ui()
        
        # Configurar protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)

    def create_ui(self):
        """Crear interfaz de usuario"""
        # Encabezado
        header = ctk.CTkFrame(self, fg_color=COLORS['primary'])
        header.pack(fill="x")
        title = "NUEVO TIPO DE CLIENTE" if self.client_type is None else "EDITAR TIPO DE CLIENTE"
        ctk.CTkLabel(header, text=title, font=FONTS['subtitle'], text_color="white").pack(pady=15)

        # Formulario
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(form, text="Nombre del Tipo *", font=FONTS['body'], anchor="w").pack(fill="x", pady=(0, 5))
        self.type_name_var = ctk.StringVar(value=self.client_type.nombre_tipo if self.client_type else "")
        ctk.CTkEntry(form, textvariable=self.type_name_var, height=35).pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(form, text="Descuento (%) *", font=FONTS['body'], anchor="w").pack(fill="x", pady=(0, 5))
        self.discount_var = ctk.StringVar(value=str(self.client_type.descuento) if self.client_type else "0")
        discount_entry = ctk.CTkEntry(form, textvariable=self.discount_var, height=35)
        discount_entry.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            form,
            text="Ingrese un valor entre 0 y 100",
            font=FONTS['small'],
            text_color="gray60"
        ).pack(fill="x", pady=(0, 15))

        # Botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self.save,
            fg_color=COLORS['success'],
            width=120,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.close_dialog,
            fg_color=COLORS['accent'],
            width=120,
            height=35
        ).pack(side="left", padx=5)

    def show(self):
        """Mostrar el diálogo"""
        self.wait_window()

    def close_dialog(self):
        """Cerrar el diálogo correctamente"""
        if self._is_closing:
            return
        self._is_closing = True
        
        try:
            # Liberar el grab
            self.grab_release()
            # Destruir la ventana
            self.destroy()
        except Exception as e:
            print(f"Error al cerrar ClientTypeFormDialog: {e}")

    def save(self):
        """Guardar tipo de cliente"""
        type_name = self.type_name_var.get().strip()
        discount_str = self.discount_var.get().strip()

        if not type_name:
            messagebox.showerror("Error", "El nombre del tipo es requerido")
            return

        try:
            discount = float(discount_str)
            if discount < 0 or discount > 100:
                messagebox.showerror("Error", "El descuento debe estar entre 0 y 100")
                return
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un descuento válido")
            return

        type_data = {
            'nombre_tipo': type_name,
            'descuento': discount
        }

        if self.client_type is None:
            # Crear
            if self.controller.create_client_type(type_data):
                self.close_dialog()
        else:
            # Actualizar
            if self.controller.update_client_type(self.client_type.id_tipo_cliente, type_data):
                self.close_dialog()