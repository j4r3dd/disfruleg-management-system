# -*- coding: utf-8 -*-
"""
DISFRULEG - Ventana de Órdenes (CustomTkinter) - OPTIMIZADA
Gestión de órdenes guardadas con FILTROS AVANZADOS
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from .orden_manager import obtener_manager
from src.theme import COLORS, FONTS


def formatear_fecha(fecha_str):
    """Convierte fecha de formato YYYY-MM-DD a DD/MM/AAAA"""
    if not fecha_str or fecha_str == 'N/A':
        return 'N/A'
    
    try:
        if ' ' in fecha_str:
            fecha_str = fecha_str.split(' ')[0]
        
        if '%' in fecha_str:
            return 'Sin fecha'
        
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
        return fecha_obj.strftime('%d/%m/%Y')
    except Exception as e:
        print(f"❌ Error formateando fecha '{fecha_str}': {e}")
        return 'Sin fecha'


class VentanaOrdenes:
    """Ventana principal para gestión de órdenes guardadas con FILTROS AVANZADOS"""
    
    def __init__(self, parent=None, user_data=None, on_nueva_orden=None, on_editar_orden=None):
        self.parent = parent
        self.user_data = user_data or {}
        self.on_nueva_orden = on_nueva_orden
        self.on_editar_orden = on_editar_orden
        
        self.username = self.user_data.get('username', 'usuario')
        self.es_admin = self.user_data.get('rol', '').lower() == 'admin'
        
        # Initialize root window FIRST to avoid "Too early to create variable" error
        self.root = ctk.CTkToplevel(parent) if parent else ctk.CTk()
        
        self.orden_manager = obtener_manager()
        
        # Variables de control
        self.auto_refresh_active = True
        self.filtro_busqueda = ctk.StringVar(master=self.root)
        self.filtro_busqueda.trace_add('write', self._on_filtro_changed)
        
        # ✨ NUEVAS VARIABLES PARA FILTROS AVANZADOS
        self.filtros_visible = ctk.BooleanVar(value=False, master=self.root)
        self.filtro_fecha_preset = ctk.StringVar(value="todos", master=self.root)
        self.filtro_fecha_desde = ctk.StringVar(master=self.root)
        self.filtro_fecha_hasta = ctk.StringVar(master=self.root)
        self.filtro_cliente = ctk.StringVar(master=self.root)
        self.filtro_usuario = ctk.StringVar(master=self.root)
        self.filtro_precio_min = ctk.StringVar(master=self.root)
        self.filtro_precio_max = ctk.StringVar(master=self.root)
        self.filtro_orden = ctk.StringVar(value="fecha_desc", master=self.root)
        
        # Datos originales para filtrado
        self.ordenes_activas_originales = []
        self.historial_original = []
        
        self.orden_columna = None
        self.orden_reverso = False
        self.headings_originales = {}
        
        self._configurar_ventana()
        self._crear_interfaz()
        self._cargar_datos_iniciales()
        self._iniciar_auto_refresh()
    
    def _configurar_ventana(self):
        """Configura las propiedades básicas de la ventana"""
        self.root.title("Gestión de Órdenes - Disfruleg")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.bind("<FocusIn>", self._on_focus_in)
        
        if self.parent:
            self.root.transient(self.parent)
            self.root.grab_set()
    
    def _crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self._crear_header()
        
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)
        
        self._crear_toolbar(main_container)
        self._crear_panel_filtros(main_container)  # ✨ NUEVO
        self._crear_notebook(main_container)
        self._crear_status_bar()
    
    def _crear_header(self):
        """Crea el header con información del usuario"""
        header_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray20"), corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        
        content = ctk.CTkFrame(header_frame, fg_color="transparent")
        content.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        content.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            content,
            text="📂 Gestión de Órdenes",
            font=FONTS['title'],
            text_color=COLORS['primary']
        ).grid(row=0, column=0, sticky="w")
        
        user_info = f"👤 {self.user_data.get('nombre_completo', self.username)}"
        if self.es_admin:
            user_info += " • ADMIN"
        
        ctk.CTkLabel(
            content,
            text=user_info,
            font=FONTS['body'],
            text_color=("gray30", "gray70")
        ).grid(row=0, column=1, sticky="e")
    
    def _crear_toolbar(self, parent):
        """Crea la barra de herramientas superior"""
        toolbar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar_frame.grid_columnconfigure(0, weight=1)
        
        # Frame izquierdo - Búsqueda
        search_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            search_frame,
            text="🔍 Búsqueda rápida:",
            font=FONTS['body_bold']
        ).pack(side="left", padx=(0, 10))
        
        self.entry_busqueda = ctk.CTkEntry(
            search_frame,
            textvariable=self.filtro_busqueda,
            width=200,
            height=38,
            corner_radius=8,
            placeholder_text="Folio, cliente, usuario...",
            font=FONTS['body']
        )
        self.entry_busqueda.pack(side="left", padx=(0, 10))
        
        # ✨ BOTÓN TOGGLE FILTROS AVANZADOS
        self.btn_toggle_filtros = ctk.CTkButton(
            search_frame,
            text="⚙️ Filtros Avanzados",
            command=self._toggle_filtros,
            width=150,
            height=38,
            fg_color=("gray70", "gray30"),
            hover_color=COLORS['info'],
            font=FONTS['body_bold'],
            corner_radius=8
        )
        self.btn_toggle_filtros.pack(side="left")
        
        # Frame derecho - Acciones
        actions_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=1, sticky="e")
        
        ctk.CTkButton(
            actions_frame,
            text="🔄 Actualizar",
            command=self._forzar_actualizacion_manual,
            width=120,
            height=38,
            fg_color=COLORS['secondary'],
            hover_color=COLORS['primary_hover'],
            font=FONTS['body_bold'],
            corner_radius=8
        ).pack(side="left", padx=(0, 10))
        
        self.btn_nueva_orden = ctk.CTkButton(
            actions_frame,
            text="➕ Nueva Orden",
            command=self._nueva_orden,
            width=150,
            height=38,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            font=FONTS['body_bold'],
            corner_radius=8
        )
        self.btn_nueva_orden.pack(side="left")
    
    def _crear_panel_filtros(self, parent):
        """✨ NUEVO: Crea el panel desplegable de filtros avanzados"""
        self.panel_filtros = ctk.CTkFrame(
            parent,
            fg_color=("gray95", "gray20"),
            corner_radius=10,
            border_width=2,
            border_color=COLORS['info']
        )
        
        # Inicialmente oculto
        self.panel_filtros.grid_remove()
        
        # Configurar grid interno
        self.panel_filtros.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Título del panel
        titulo_frame = ctk.CTkFrame(self.panel_filtros, fg_color="transparent")
        titulo_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            titulo_frame,
            text="🎯 Filtros Avanzados",
            font=("Arial", 16, "bold"),
            text_color=COLORS['info']
        ).pack(side="left")
        
        # Fila 1: Fecha y Orden
        # FECHA PRESET
        fecha_frame = ctk.CTkFrame(self.panel_filtros, fg_color="transparent")
        fecha_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(fecha_frame, text="📅 Período:", font=FONTS['body_bold']).pack(anchor="w")
        
        ctk.CTkOptionMenu(
            fecha_frame,
            variable=self.filtro_fecha_preset,
            values=["Todos", "Hoy", "Esta semana", "Este mes", "Personalizado"],
            command=self._on_fecha_preset_changed,
            width=150,
            height=32,
            corner_radius=8,
            font=FONTS['body']
        ).pack(fill="x", pady=(5, 0))
        
        # ORDENAMIENTO
        orden_frame = ctk.CTkFrame(self.panel_filtros, fg_color="transparent")
        orden_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(orden_frame, text="🔽 Ordenar por:", font=FONTS['body_bold']).pack(anchor="w")
        
        ctk.CTkOptionMenu(
            orden_frame,
            variable=self.filtro_orden,
            values=[
                "Fecha ↓ (Recientes primero)",
                "Fecha ↑ (Antiguos primero)",
                "Folio ↓ (Mayor a menor)",
                "Folio ↑ (Menor a mayor)",
                "Precio ↓ (Mayor a menor)",
                "Precio ↑ (Menor a menor)",
                "Cliente A-Z",
                "Cliente Z-A"
            ],
            command=lambda _: self._aplicar_filtros_avanzados(),
            width=200,
            height=32,
            corner_radius=8,
            font=FONTS['body']
        ).pack(fill="x", pady=(5, 0))
        
        # CLIENTE
        cliente_frame = ctk.CTkFrame(self.panel_filtros, fg_color="transparent")
        cliente_frame.grid(row=1, column=2, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(cliente_frame, text="👥 Cliente:", font=FONTS['body_bold']).pack(anchor="w")
        
        self.entry_cliente = ctk.CTkEntry(
            cliente_frame,
            textvariable=self.filtro_cliente,
            placeholder_text="Nombre del cliente",
            width=150,
            height=32,
            corner_radius=8,
            font=FONTS['body']
        )
        self.entry_cliente.pack(fill="x", pady=(5, 0))
        self.filtro_cliente.trace_add('write', lambda *args: self._aplicar_filtros_avanzados())
        
        # USUARIO
        usuario_frame = ctk.CTkFrame(self.panel_filtros, fg_color="transparent")
        usuario_frame.grid(row=1, column=3, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(usuario_frame, text="👤 Usuario:", font=FONTS['body_bold']).pack(anchor="w")
        
        self.entry_usuario = ctk.CTkEntry(
            usuario_frame,
            textvariable=self.filtro_usuario,
            placeholder_text="Usuario creador",
            width=150,
            height=32,
            corner_radius=8,
            font=FONTS['body']
        )
        self.entry_usuario.pack(fill="x", pady=(5, 0))
        self.filtro_usuario.trace_add('write', lambda *args: self._aplicar_filtros_avanzados())
        
        # Fila 2: Rango de fechas personalizado (inicialmente oculto)
        self.fecha_custom_frame = ctk.CTkFrame(self.panel_filtros, fg_color="transparent")
        self.fecha_custom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.fecha_custom_frame.grid_remove()
        
        desde_frame = ctk.CTkFrame(self.fecha_custom_frame, fg_color="transparent")
        desde_frame.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        ctk.CTkLabel(desde_frame, text="Desde:", font=FONTS['body']).pack(anchor="w")
        self.entry_fecha_desde = ctk.CTkEntry(
            desde_frame,
            textvariable=self.filtro_fecha_desde,
            placeholder_text="DD/MM/AAAA",
            width=120,
            height=32,
            corner_radius=8,
            font=FONTS['body']
        )
        self.entry_fecha_desde.pack(fill="x", pady=(5, 0))
        
        hasta_frame = ctk.CTkFrame(self.fecha_custom_frame, fg_color="transparent")
        hasta_frame.pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        ctk.CTkLabel(hasta_frame, text="Hasta:", font=FONTS['body']).pack(anchor="w")
        self.entry_fecha_hasta = ctk.CTkEntry(
            hasta_frame,
            textvariable=self.filtro_fecha_hasta,
            placeholder_text="DD/MM/AAAA",
            width=120,
            height=32,
            corner_radius=8,
            font=FONTS['body']
        )
        self.entry_fecha_hasta.pack(fill="x", pady=(5, 0))
        
        # RANGO DE PRECIOS
        precio_frame = ctk.CTkFrame(self.panel_filtros, fg_color="transparent")
        precio_frame.grid(row=2, column=2, columnspan=2, sticky="ew", padx=10, pady=5)
        
        min_frame = ctk.CTkFrame(precio_frame, fg_color="transparent")
        min_frame.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        ctk.CTkLabel(min_frame, text="💰 Precio mín:", font=FONTS['body_bold']).pack(anchor="w")
        self.entry_precio_min = ctk.CTkEntry(
            min_frame,
            textvariable=self.filtro_precio_min,
            placeholder_text="$0",
            width=100,
            height=32,
            corner_radius=8,
            font=FONTS['body']
        )
        self.entry_precio_min.pack(fill="x", pady=(5, 0))
        self.filtro_precio_min.trace_add('write', lambda *args: self._aplicar_filtros_avanzados())
        
        max_frame = ctk.CTkFrame(precio_frame, fg_color="transparent")
        max_frame.pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        ctk.CTkLabel(max_frame, text="💰 Precio máx:", font=FONTS['body_bold']).pack(anchor="w")
        self.entry_precio_max = ctk.CTkEntry(
            max_frame,
            textvariable=self.filtro_precio_max,
            placeholder_text="$999999",
            width=100,
            height=32,
            corner_radius=8,
            font=FONTS['body']
        )
        self.entry_precio_max.pack(fill="x", pady=(5, 0))
        self.filtro_precio_max.trace_add('write', lambda *args: self._aplicar_filtros_avanzados())
        
        # Fila 3: Botones de acción
        botones_frame = ctk.CTkFrame(self.panel_filtros, fg_color="transparent")
        botones_frame.grid(row=3, column=0, columnspan=4, pady=(10, 15))
        
        ctk.CTkButton(
            botones_frame,
            text="🗑️ Limpiar Filtros",
            command=self._limpiar_filtros,
            width=150,
            height=35,
            fg_color=("gray60", "gray40"),
            hover_color=COLORS['accent'],
            font=FONTS['body_bold'],
            corner_radius=8
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            botones_frame,
            text="✅ Aplicar Filtros",
            command=self._aplicar_filtros_avanzados,
            width=150,
            height=35,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover'],
            font=FONTS['body_bold'],
            corner_radius=8
        ).pack(side="left", padx=5)
    
    def _toggle_filtros(self):
        """✨ Muestra/oculta el panel de filtros"""
        if self.filtros_visible.get():
            self.panel_filtros.grid_remove()
            self.filtros_visible.set(False)
            self.btn_toggle_filtros.configure(fg_color=("gray70", "gray30"))
        else:
            self.panel_filtros.grid(row=1, column=0, sticky="ew", pady=(0, 10), padx=0)
            self.filtros_visible.set(True)
            self.btn_toggle_filtros.configure(fg_color=COLORS['info'])
    
    def _on_fecha_preset_changed(self, seleccion):
        """✨ Maneja cambios en el preset de fecha"""
        seleccion_lower = seleccion.lower()
        
        if seleccion_lower == "personalizado":
            self.fecha_custom_frame.grid()
        else:
            self.fecha_custom_frame.grid_remove()
            self.filtro_fecha_desde.set("")
            self.filtro_fecha_hasta.set("")
        
        self._aplicar_filtros_avanzados()
    
    def _limpiar_filtros(self):
        """✨ Limpia todos los filtros avanzados"""
        self.filtro_fecha_preset.set("Todos")
        self.filtro_fecha_desde.set("")
        self.filtro_fecha_hasta.set("")
        self.filtro_cliente.set("")
        self.filtro_usuario.set("")
        self.filtro_precio_min.set("")
        self.filtro_precio_max.set("")
        self.filtro_orden.set("Fecha ↓ (Recientes primero)")
        self.filtro_busqueda.set("")
        
        self._aplicar_filtros_avanzados()
    
    def _aplicar_filtros_avanzados(self):
        """✨ Aplica todos los filtros avanzados a las listas"""
        self._filtrar_ordenes_activas()
        self._filtrar_historial()
    
    def _filtrar_ordenes_activas(self):
        """✨ Filtra y ordena las órdenes activas"""
        ordenes = self.ordenes_activas_originales.copy()
        
        # Aplicar filtros
        ordenes = self._aplicar_filtro_fecha(ordenes)
        ordenes = self._aplicar_filtro_cliente(ordenes)
        ordenes = self._aplicar_filtro_usuario(ordenes)
        ordenes = self._aplicar_filtro_precio(ordenes)
        ordenes = self._aplicar_filtro_busqueda(ordenes)
        ordenes = self._aplicar_ordenamiento(ordenes)
        
        # Actualizar treeview
        self._poblar_tree_activas(ordenes)
        self.lbl_count_activas.configure(
            text=f"Órdenes activas: {len(ordenes)}" + 
            (f" de {len(self.ordenes_activas_originales)}" if len(ordenes) < len(self.ordenes_activas_originales) else "")
        )
    
    def _filtrar_historial(self):
        """✨ Filtra y ordena el historial"""
        ordenes = self.historial_original.copy()
        
        ordenes = self._aplicar_filtro_fecha(ordenes)
        ordenes = self._aplicar_filtro_cliente(ordenes)
        ordenes = self._aplicar_filtro_usuario(ordenes)
        ordenes = self._aplicar_filtro_precio(ordenes)
        ordenes = self._aplicar_filtro_busqueda(ordenes)
        ordenes = self._aplicar_ordenamiento(ordenes)
        
        self._poblar_tree_historial(ordenes)
        self.lbl_count_historial.configure(
            text=f"| Historial: {len(ordenes)}" + 
            (f" de {len(self.historial_original)}" if len(ordenes) < len(self.historial_original) else "")
        )
    
    def _aplicar_filtro_fecha(self, ordenes):
        """Filtra por rango de fechas"""
        preset = self.filtro_fecha_preset.get().lower()
        
        if preset == "todos":
            return ordenes
        
        hoy = datetime.now().date()
        
        if preset == "hoy":
            return [o for o in ordenes if self._fecha_en_rango(o, hoy, hoy)]
        elif preset == "esta semana":
            inicio = hoy - timedelta(days=hoy.weekday())
            return [o for o in ordenes if self._fecha_en_rango(o, inicio, hoy)]
        elif preset == "este mes":
            inicio = hoy.replace(day=1)
            return [o for o in ordenes if self._fecha_en_rango(o, inicio, hoy)]
        elif preset == "personalizado":
            desde_str = self.filtro_fecha_desde.get()
            hasta_str = self.filtro_fecha_hasta.get()
            
            if desde_str or hasta_str:
                try:
                    desde = datetime.strptime(desde_str, "%d/%m/%Y").date() if desde_str else datetime.min.date()
                    hasta = datetime.strptime(hasta_str, "%d/%m/%Y").date() if hasta_str else datetime.max.date()
                    return [o for o in ordenes if self._fecha_en_rango(o, desde, hasta)]
                except ValueError:
                    pass
        
        return ordenes
    
    def _fecha_en_rango(self, orden, desde, hasta):
        """Verifica si la fecha de la orden está en el rango"""
        fecha_orden = orden.get('fecha_modificacion') or orden.get('fecha_creacion')
        if not fecha_orden:
            return False
        
        if isinstance(fecha_orden, str):
            try:
                fecha_orden = datetime.strptime(fecha_orden.split()[0], '%Y-%m-%d').date()
            except:
                return False
        elif isinstance(fecha_orden, datetime):
            fecha_orden = fecha_orden.date()
        
        return desde <= fecha_orden <= hasta
    
    def _aplicar_filtro_cliente(self, ordenes):
        """Filtra por nombre de cliente"""
        filtro = self.filtro_cliente.get().strip().lower()
        if not filtro:
            return ordenes
        return [o for o in ordenes if filtro in o.get('nombre_cliente', '').lower()]
    
    def _aplicar_filtro_usuario(self, ordenes):
        """Filtra por usuario creador"""
        filtro = self.filtro_usuario.get().strip().lower()
        if not filtro:
            return ordenes
        return [o for o in ordenes if filtro in o.get('usuario_creador', '').lower()]
    
    def _aplicar_filtro_precio(self, ordenes):
        """Filtra por rango de precios"""
        min_str = self.filtro_precio_min.get().strip()
        max_str = self.filtro_precio_max.get().strip()
        
        if not min_str and not max_str:
            return ordenes
        
        try:
            precio_min = float(min_str.replace('$', '').replace(',', '')) if min_str else 0
            precio_max = float(max_str.replace('$', '').replace(',', '')) if max_str else float('inf')
            
            return [o for o in ordenes if precio_min <= o.get('total_estimado', 0) <= precio_max]
        except ValueError:
            return ordenes
    
    def _aplicar_filtro_busqueda(self, ordenes):
        """Aplica el filtro de búsqueda rápida"""
        filtro = self.filtro_busqueda.get().strip().lower()
        if not filtro:
            return ordenes
        
        resultado = []
        for orden in ordenes:
            texto_completo = f"{orden.get('folio_numero', '')} {orden.get('nombre_cliente', '')} {orden.get('usuario_creador', '')}".lower()
            if filtro in texto_completo:
                resultado.append(orden)
        
        return resultado
    
    def _aplicar_ordenamiento(self, ordenes):
        """Ordena las órdenes según el criterio seleccionado"""
        orden = self.filtro_orden.get()
        
        if "Fecha ↓" in orden:
            return sorted(ordenes, key=lambda x: x.get('fecha_modificacion') or x.get('fecha_creacion') or '', reverse=True)
        elif "Fecha ↑" in orden:
            return sorted(ordenes, key=lambda x: x.get('fecha_modificacion') or x.get('fecha_creacion') or '')
        elif "Folio ↓" in orden:
            return sorted(ordenes, key=lambda x: x.get('folio_numero', 0), reverse=True)
        elif "Folio ↑" in orden:
            return sorted(ordenes, key=lambda x: x.get('folio_numero', 0))
        elif "Precio ↓" in orden:
            return sorted(ordenes, key=lambda x: x.get('total_estimado', 0), reverse=True)
        elif "Precio ↑" in orden:
            return sorted(ordenes, key=lambda x: x.get('total_estimado', 0))
        elif "Cliente A-Z" in orden:
            return sorted(ordenes, key=lambda x: x.get('nombre_cliente', '').lower())
        elif "Cliente Z-A" in orden:
            return sorted(ordenes, key=lambda x: x.get('nombre_cliente', '').lower(), reverse=True)
        
        return ordenes
    
    def _crear_notebook(self, parent):
        """Crea el notebook con las pestañas de órdenes"""
        self.notebook = ctk.CTkTabview(parent, corner_radius=10)
        self.notebook.grid(row=2, column=0, sticky="nsew")
        
        self.notebook.add("📋 Órdenes Activas")
        self.notebook.add("📚 Historial")
        
        self.frame_activas = self.notebook.tab("📋 Órdenes Activas")
        self.frame_historial = self.notebook.tab("📚 Historial")
        
        self.frame_activas.grid_columnconfigure(0, weight=1)
        self.frame_activas.grid_rowconfigure(0, weight=1)
        self.frame_historial.grid_columnconfigure(0, weight=1)
        self.frame_historial.grid_rowconfigure(0, weight=1)
        
        self._crear_lista_ordenes(self.frame_activas, "activas")
        self._crear_lista_ordenes(self.frame_historial, "historial")
    
    def _crear_lista_ordenes(self, parent, tipo):
        """Crea la lista de órdenes para una pestaña específica"""
        list_container = ctk.CTkFrame(parent, fg_color="transparent")
        list_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)
        
        tree_frame = ctk.CTkFrame(
            list_container,
            fg_color=("gray95", "gray15"),
            corner_radius=10,
            border_width=1,
            border_color=("gray80", "gray30")
        )
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        if tipo == "activas":
            columnas = ("folio", "cliente", "total", "fecha_mod", "usuario", "acciones")
            headings = {
                "folio": "Folio",
                "cliente": "Cliente",
                "total": "Total",
                "fecha_mod": "Última Modificación",
                "usuario": "Usuario",
                "acciones": "Acciones"
            }
            tree_name = "tree_activas"
        else:
            columnas = ("folio", "cliente", "total", "fecha_reg", "usuario")
            headings = {
                "folio": "Folio",
                "cliente": "Cliente",
                "total": "Total",
                "fecha_reg": "Fecha Registro",
                "usuario": "Usuario"
            }
            tree_name = "tree_historial"
        
        style = ttk.Style()
        style.theme_use("clam")
        
        appearance_mode = ctk.get_appearance_mode()
        if appearance_mode == "Dark":
            bg_color = "#1a1a1a"
            fg_color = "#e0e0e0"
            field_bg = "#2b2b2b"
            heading_bg = "#2a2a2a"
        else:
            bg_color = "white"
            fg_color = "#2b2b2b"
            field_bg = "#f5f5f5"
            heading_bg = "#e8e8e8"
        
        tree_style_name = f"Ordenes.{tipo}.Treeview"
        
        style.configure(tree_style_name,
                       background=bg_color,
                       foreground=fg_color,
                       fieldbackground=field_bg,
                       borderwidth=0,
                       font=FONTS['body'],
                       rowheight=35)
        
        style.configure(f"{tree_style_name}.Heading",
                       background=heading_bg,
                       foreground=fg_color,
                       borderwidth=0,
                       relief="flat",
                       font=FONTS['body_bold'])
        
        style.map(tree_style_name,
                 background=[("selected", COLORS['primary'])],
                 foreground=[("selected", "white")])
        
        tree = ttk.Treeview(
            tree_frame,
            columns=columnas,
            show="headings",
            style=tree_style_name,
            height=20
        )
        
        for col in columnas:
            tree.heading(col, text=headings[col])
            
            if col == "folio":
                tree.column(col, width=80, anchor="center", minwidth=70)
            elif col == "cliente":
                tree.column(col, width=200, anchor="w", minwidth=150)
            elif col == "total":
                tree.column(col, width=120, anchor="e", minwidth=100)
            elif col in ["fecha_mod", "fecha_reg"]:
                tree.column(col, width=150, anchor="center", minwidth=130)
            elif col == "usuario":
                tree.column(col, width=120, anchor="center", minwidth=100)
            elif col == "acciones":
                tree.column(col, width=150, anchor="center", minwidth=130)
        
        scrollbar = ctk.CTkScrollbar(
            tree_frame,
            orientation="vertical",
            command=tree.yview,
            width=16,
            corner_radius=8
        )
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        
        setattr(self, tree_name, tree)
        
        tree_headings_key = f"{tipo}_headings"
        self.headings_originales[tree_headings_key] = headings
        
        if tipo == "activas":
            tree.bind("<Double-1>", self._on_doble_click_activas)
            tree.bind("<Button-1>", self._on_click_activas)
            # Bind right-click for context menu (Windows/Linux: Button-3, macOS: Button-2 or Button-3)
            tree.bind("<Button-3>", self._on_right_click_activas)
            tree.bind("<Button-2>", self._on_right_click_activas)
    
    def _crear_status_bar(self):
        """Crea la barra de estado"""
        status_frame = ctk.CTkFrame(
            self.root,
            fg_color=("gray85", "gray25"),
            corner_radius=0,
            height=40
        )
        status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        status_frame.grid_columnconfigure(1, weight=1)
        
        self.lbl_count_activas = ctk.CTkLabel(
            status_frame,
            text="Órdenes activas: 0",
            font=FONTS['body'],
            text_color=("gray30", "gray70")
        )
        self.lbl_count_activas.grid(row=0, column=0, sticky="w", padx=15)
        
        self.lbl_count_historial = ctk.CTkLabel(
            status_frame,
            text="| Historial: 0",
            font=FONTS['body'],
            text_color=("gray30", "gray70")
        )
        self.lbl_count_historial.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        self.lbl_ultima_actualizacion = ctk.CTkLabel(
            status_frame,
            text="",
            font=("Arial", 9, "italic"),
            text_color=("gray50", "gray60")
        )
        self.lbl_ultima_actualizacion.grid(row=0, column=2, sticky="e", padx=15)
    
    # ==================== EVENTOS Y CALLBACKS ====================
    
    def _nueva_orden(self):
        """Callback para crear una nueva orden"""
        if self.on_nueva_orden:
            try:
                self.on_nueva_orden()
                self.root.after(1000, self._actualizar_listas)
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear nueva orden: {str(e)}")
        else:
            messagebox.showinfo("No Implementado", "Callback de nueva orden no configurado")
    
    def _on_doble_click_activas(self, event):
        """Maneja doble clic en órdenes activas para editar"""
        item = self.tree_activas.selection()[0] if self.tree_activas.selection() else None
        if item:
            valores = self.tree_activas.item(item, "values")
            if valores:
                folio_str = str(valores[0]).strip().replace(',', '').lstrip('0') or '0'
                folio = int(folio_str)
                self._editar_orden(folio)
    
    def _on_click_activas(self, event):
        """Maneja clic simple en órdenes activas para acciones"""
        item = self.tree_activas.identify_row(event.y)
        if not item:
            return
        
        column = self.tree_activas.identify_column(event.x)
        if column == "#6":
            valores = self.tree_activas.item(item, "values")
            if valores:
                folio_str = str(valores[0]).strip().replace(',', '').lstrip('0') or '0'
                folio = int(folio_str)
                self._mostrar_menu_acciones(event, folio)

    def _on_right_click_activas(self, event):
        """Maneja clic derecho en órdenes activas para menú contextual"""
        item = self.tree_activas.identify_row(event.y)
        if not item:
            return
            
        # Seleccionar el item bajo el cursor
        self.tree_activas.selection_set(item)
        self.tree_activas.focus(item)
        
        valores = self.tree_activas.item(item, "values")
        if valores:
            folio_str = str(valores[0]).strip().replace(',', '').lstrip('0') or '0'
            folio = int(folio_str)
            self._mostrar_menu_acciones(event, folio)
    
    def _mostrar_menu_acciones(self, event, folio):
        """Muestra menú contextual con acciones para una orden"""
        menu = ctk.CTkToplevel(self.root)
        menu.withdraw()
        menu.overrideredirect(True)
        menu.configure(fg_color=("white", "gray20"))
        
        menu.geometry(f"+{event.x_root}+{event.y_root}")
        
        menu_frame = ctk.CTkFrame(menu, fg_color="transparent")
        menu_frame.pack(padx=5, pady=5)
        
        ctk.CTkButton(
            menu_frame,
            text="✏️ Editar",
            command=lambda: [self._editar_orden(folio), menu.destroy()],
            fg_color=COLORS['info'],
            hover_color=COLORS['info_hover'],
            height=35,
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=2)
        
        ctk.CTkButton(
            menu_frame,
            text="🗑️ Eliminar",
            command=lambda: [self._eliminar_orden(folio), menu.destroy()],
            fg_color=COLORS['accent'],
            hover_color=COLORS['error_red'],
            height=35,
            font=FONTS['body'],
            anchor="w"
        ).pack(fill="x", pady=2)
        
        menu.deiconify()
        menu.focus_set()
        menu.bind("<FocusOut>", lambda e: menu.destroy())
    
    def _editar_orden(self, folio):
        """Callback para editar una orden específica"""
        if self.on_editar_orden:
            try:
                self.on_editar_orden(folio)
                self.root.after(1000, self._actualizar_listas)
            except Exception as e:
                messagebox.showerror("Error", f"Error al editar orden {folio}: {str(e)}")
        else:
            messagebox.showinfo("No Implementado", f"Callback de edición no configurado para folio {folio}")
    
    def _eliminar_orden(self, folio):
        """Elimina una orden después de confirmación"""
        if messagebox.askyesno("Confirmar Eliminación",
                              f"¿Está seguro de que desea eliminar la orden con folio {folio:06d}?\n\n"
                              f"Esta acción liberará el folio y no se puede deshacer."):
            try:
                if self.orden_manager.liberar_folio(folio):
                    messagebox.showinfo("Éxito", f"Orden {folio:06d} eliminada exitosamente")
                    self._actualizar_listas()
                else:
                    messagebox.showerror("Error", f"No se pudo eliminar la orden {folio}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar orden: {str(e)}")
    
    def _on_filtro_changed(self, *args):
        """Maneja cambios en el filtro de búsqueda"""
        if hasattr(self, '_filter_job') and self._filter_job is not None:
            self.root.after_cancel(self._filter_job)
        self._filter_job = self.root.after(300, self._aplicar_filtros_avanzados)
    
    def _buscar_por_folio(self):
        """Busca una orden específica por folio"""
        texto_busqueda = self.entry_busqueda.get().strip()
        
        if not texto_busqueda:
            self.filtro_busqueda.set("")
            self._aplicar_filtros_avanzados()
            return
        
        try:
            if texto_busqueda.isdigit():
                folio_buscado = int(texto_busqueda)
                
                self._limpiar_highlights()
                
                encontrado = self._buscar_en_tree(self.tree_activas, folio_buscado, 0, "Órdenes Activas")
                
                if not encontrado:
                    encontrado = self._buscar_en_tree(self.tree_historial, folio_buscado, 1, "Historial")
                
                if not encontrado:
                    messagebox.showinfo("No Encontrado", f"No se encontró orden con folio {folio_buscado:06d}")
            else:
                self._aplicar_filtros_avanzados()
            
        except ValueError:
            messagebox.showwarning("Búsqueda Inválida", "Para buscar por folio, ingrese solo números")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la búsqueda: {str(e)}")
    
    def _buscar_en_tree(self, tree, folio_buscado, tab_index, tab_name):
        """Busca un folio específico en un treeview y lo selecciona"""
        try:
            for item in tree.get_children():
                valores = tree.item(item, "values")
                if valores and len(valores) > 0:
                    folio_str = str(valores[0]).strip().replace(',', '').lstrip('0') or '0'
                    folio_item = int(folio_str)
                    
                    if folio_item == folio_buscado:
                        if tab_index == 0:
                            self.notebook.set("📋 Órdenes Activas")
                        else:
                            self.notebook.set("📚 Historial")
                        
                        tree.selection_set(item)
                        tree.focus(item)
                        tree.see(item)
                        
                        tree.item(item, tags=("found",))
                        tree.tag_configure("found", background=COLORS['info'], foreground="white")
                        
                        self.root.after(5000, lambda: self._remover_highlight(tree, item))
                        
                        print(f"✅ Folio {folio_buscado:06d} encontrado en {tab_name}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error buscando en {tab_name}: {e}")
            return False
    
    def _limpiar_highlights(self):
        """Limpia todos los highlights previos"""
        try:
            for item in self.tree_activas.get_children():
                self.tree_activas.item(item, tags=())
            
            for item in self.tree_historial.get_children():
                self.tree_historial.item(item, tags=())
        except Exception as e:
            print(f"Error limpiando highlights: {e}")
    
    def _remover_highlight(self, tree, item):
        """Remueve el highlight de un item"""
        try:
            if tree.exists(item):
                tree.item(item, tags=())
        except Exception as e:
            print(f"Error removiendo highlight: {e}")
    
    # ==================== CARGA DE DATOS ====================
    
    def _cargar_datos_iniciales(self):
        """Carga los datos iniciales en ambas pestañas"""
        self._cargar_ordenes_activas()
        self._cargar_historial()
    
    def _cargar_ordenes_activas(self):
        """Carga las órdenes activas en el treeview"""
        try:
            ordenes = self.orden_manager.obtener_ordenes_activas(self.username, self.es_admin)
            self.ordenes_activas_originales = ordenes
            self._poblar_tree_activas(ordenes)
            self.lbl_count_activas.configure(text=f"Órdenes activas: {len(ordenes)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar órdenes activas: {str(e)}")
    
    def _poblar_tree_activas(self, ordenes):
        """Pobla el tree de órdenes activas"""
        for item in self.tree_activas.get_children():
            self.tree_activas.delete(item)
        
        for orden in ordenes:
            folio_str = f"{orden['folio_numero']:06d}"
            cliente = orden['nombre_cliente']
            total = f"${orden['total_estimado']:,.2f}"
            fecha_mod = formatear_fecha(orden.get('fecha_modificacion_str', 'N/A'))
            usuario = orden['usuario_creador']
            acciones = "⚙️ Acciones"
            
            self.tree_activas.insert("", "end", values=(
                folio_str, cliente, total, fecha_mod, usuario, acciones
            ))
    
    def _cargar_historial(self):
        """Carga el historial de órdenes en el treeview"""
        try:
            historial = self.orden_manager.obtener_historial(self.username, self.es_admin, limite=100)
            self.historial_original = historial
            self._poblar_tree_historial(historial)
            self.lbl_count_historial.configure(text=f"| Historial: {len(historial)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial: {str(e)}")
    
    def _poblar_tree_historial(self, ordenes):
        """Pobla el tree de historial"""
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)
        
        for orden in ordenes:
            folio_str = f"{orden['folio_numero']:06d}"
            cliente = orden['nombre_cliente']
            total = f"${orden['total_estimado']:,.2f}"
            fecha_reg = formatear_fecha(orden.get('fecha_creacion_str', 'N/A'))
            usuario = orden['usuario_creador']
            
            self.tree_historial.insert("", "end", values=(
                folio_str, cliente, total, fecha_reg, usuario
            ))
    
    def _actualizar_listas(self):
        """Actualiza ambas listas de órdenes"""
        self._cargar_ordenes_activas()
        self._cargar_historial()
        
        ahora = datetime.now().strftime("%H:%M:%S")
        self.lbl_ultima_actualizacion.configure(text=f"Actualizado: {ahora}")
    
    def _forzar_actualizacion_manual(self):
        """Fuerza actualización manual cuando se presiona el botón"""
        try:
            print("🔄 Actualizando listas manualmente...")
            
            self._cargar_ordenes_activas()
            self._cargar_historial()
            
            # Reaplicar filtros
            self._aplicar_filtros_avanzados()
            
            ahora = datetime.now().strftime("%H:%M:%S")
            self.lbl_ultima_actualizacion.configure(text=f"Actualizado: {ahora}")
            
            self.lbl_ultima_actualizacion.configure(text_color=COLORS['success'])
            self.root.after(2000, lambda: self.lbl_ultima_actualizacion.configure(
                text_color=("gray50", "gray60")
            ))
            
            print("✅ Actualización completada exitosamente")
            
        except Exception as e:
            print(f"❌ Error en actualización manual: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def forzar_actualizacion(self):
        """Fuerza la actualización de las listas desde el exterior"""
        try:
            self._actualizar_listas()
            self._aplicar_filtros_avanzados()
            print("🔄 Lista de órdenes actualizada desde ventana externa")
        except Exception as e:
            print(f"Error al forzar actualización: {e}")
    
    def _on_focus_in(self, event):
        """Se ejecuta cuando la ventana recibe el foco"""
        if event.widget == self.root:
            self.root.after(100, self.forzar_actualizacion)
    
    # ==================== AUTO-REFRESH ====================
    
    def _iniciar_auto_refresh(self):
        """Inicia el auto-refresh cada 30 segundos"""
        if self.auto_refresh_active:
            self._actualizar_listas()
            self._aplicar_filtros_avanzados()
            self.root.after(30000, self._iniciar_auto_refresh)
    
    def _detener_auto_refresh(self):
        """Detiene el auto-refresh"""
        self.auto_refresh_active = False
    
    # ==================== CLEANUP ====================
    
    def _on_closing(self):
        """Maneja el cierre de la ventana"""
        self._detener_auto_refresh()
        if self.parent:
            self.root.destroy()
        else:
            self.root.quit()
    
    def show(self):
        """Muestra la ventana"""
        self.root.mainloop()
    
    def destroy(self):
        """Destruye la ventana"""
        self._detener_auto_refresh()
        self.root.destroy()


# ==================== FUNCIÓN DE CONVENIENCIA ====================

def abrir_ventana_ordenes(parent=None, user_data=None, on_nueva_orden=None, on_editar_orden=None):
    """
    Función de conveniencia para abrir la ventana de gestión de órdenes.
    
    Args:
        parent: Ventana padre
        user_data: Datos del usuario autenticado
        on_nueva_orden: Callback para crear nueva orden
        on_editar_orden: Callback para editar orden (recibe folio)
        
    Returns:
        VentanaOrdenes: Instancia de la ventana creada
    """
    ventana = VentanaOrdenes(parent, user_data, on_nueva_orden, on_editar_orden)
    return ventana


# ==================== BLOQUE DE PRUEBA ====================

if __name__ == '__main__':
    """Bloque de pruebas para verificar la interfaz"""
    
    user_data_test = {
        'username': 'test_user',
        'nombre_completo': 'Usuario de Prueba',
        'rol': 'admin'
    }
    
    def callback_nueva_orden():
        print("Callback: Nueva orden solicitada")
        messagebox.showinfo("Prueba", "Callback de nueva orden ejecutado")
    
    def callback_editar_orden(folio):
        print(f"Callback: Editar orden {folio}")
        messagebox.showinfo("Prueba", f"Callback de edición ejecutado para folio {folio}")
    
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    
    ventana = abrir_ventana_ordenes(
        parent=None,
        user_data=user_data_test,
        on_nueva_orden=callback_nueva_orden,
        on_editar_orden=callback_editar_orden
    )
    
    ventana.show()