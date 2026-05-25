# -*- coding: utf-8 -*-
"""
window_lifecycle_manager.py - Gestiona el ciclo de vida de la ventana
Inicialización, configuración de UI y cierre ordenado
"""

import customtkinter as ctk
import logging
import os

from .window_ui_constants import (
    COLORS, FONTS, WINDOW_WIDTH, WINDOW_HEIGHT, INITIAL_STATUS, DEFAULT_TEXT_AREA
)
from .help_button import AnimatedHelpButton
from .help_center_window import HelpCenterWindow
from .custom_dialogs import show_info, show_success, show_warning, show_error, ask_confirm

logger = logging.getLogger(__name__)


class WindowLifecycleManager:
    """Maneja inicialización y cierre de la ventana"""

    def setup_window(self):
        """Configura la ventana principal"""
        self.title("Ubicuo AI · Procesamiento Inteligente")
        self.configure(fg_color=COLORS['bg_primary'])
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        ctk.set_appearance_mode("dark")
        logger.info("🔨 Ventana configurada")

    def create_ui(self):
        """Crea toda la interfaz de usuario - DISEÑO PROFESIONAL ORIGINAL"""
        try:
            # Main container
            self.main_container = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'])
            self.main_container.pack(fill="both", expand=True)
            
            logger.info("  📋 Panel superior...")
            self.create_top_panel()
            
            # Content
            content = ctk.CTkFrame(self.main_container, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=20, pady=10)
            
            logger.info("  📋 Panel izquierdo...")
            self.create_left_panel(content)
            
            logger.info("  📋 Panel derecho...")
            self.create_right_panel(content)
            
            logger.info("  📋 Barra inferior...")
            self.create_bottom_bar()
            
            logger.info("  🐕 Botón flotante de ayuda...")
            self.create_help_button()
            
            self.update()
            
        except Exception as e:
            logger.error(f"Error create_ui: {e}")
            raise

    def create_top_panel(self):
        """Create modern top panel with AI branding and back button"""
        top_panel = ctk.CTkFrame(
            self.main_container, 
            fg_color=COLORS['bg_secondary'], 
            height=90,
            corner_radius=0
        )
        top_panel.pack(fill="x", padx=0, pady=0)
        top_panel.pack_propagate(False)
        
        # Content container
        content = ctk.CTkFrame(top_panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=15)
        
        # Left side - Back button + Title
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left")
        
        # BACK BUTTON
        back_btn = ctk.CTkButton(
            left_frame,
            text="⎋",
            width=40,
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS['ai_red'],
            font=("Arial", 20),
            text_color=COLORS['text_primary'],
            border_width=0,
            command=self.on_closing
        )
        back_btn.pack(side="left", padx=(0, 15))
        
        # AI Badge (vertical line)
        badge_frame = ctk.CTkFrame(
            left_frame,
            fg_color=COLORS['ai_blue'],
            width=4,
            height=45,
            corner_radius=2
        )
        badge_frame.pack(side="left", padx=(0, 12))
        
        # Title section
        title_section = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_section.pack(side="left")
        
        title = ctk.CTkLabel(
            title_section,
            text="UBICUO AI",
            font=('Arial', 28, 'bold'),
            text_color=COLORS['text_primary']
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_section,
            text="Procesamiento Inteligente de Pedidos",
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        )
        subtitle.pack(anchor="w")
        
        # Right side - Stats in horizontal line
        stats_container = ctk.CTkFrame(content, fg_color="transparent")
        stats_container.pack(side="right")
        
        # Stats frame horizontal
        stats_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        stats_frame.pack()
        
        # Items stat
        items_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        items_frame.pack(side="left", padx=15)
        
        self.items_value = ctk.CTkLabel(
            items_frame,
            text="0",
            font=('Arial', 32, 'bold'),
            text_color=COLORS['ai_blue']
        )
        self.items_value.pack()
        
        ctk.CTkLabel(
            items_frame,
            text="Items",
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        ).pack()
        
        # Identificados stat
        matched_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        matched_frame.pack(side="left", padx=15)
        
        self.matched_value = ctk.CTkLabel(
            matched_frame,
            text="0",
            font=('Arial', 32, 'bold'),
            text_color=COLORS['ai_blue']
        )
        self.matched_value.pack()
        
        ctk.CTkLabel(
            matched_frame,
            text="Identificados",
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        ).pack()
        
        # Pendientes stat
        pending_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        pending_frame.pack(side="left", padx=15)
        
        self.pending_value = ctk.CTkLabel(
            pending_frame,
            text="0",
            font=('Arial', 32, 'bold'),
            text_color=COLORS['ai_orange']
        )
        self.pending_value.pack()
        
        ctk.CTkLabel(
            pending_frame,
            text="Pendientes",
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        ).pack()
        
        # Store references for updates
        self.stats_cards = {
            'items': type('obj', (object,), {'value_label': self.items_value})(),
            'matched': type('obj', (object,), {'value_label': self.matched_value})(),
            'pending': type('obj', (object,), {'value_label': self.pending_value})()
        }

    def create_left_panel(self, parent):
        """Create modern left input panel with complete logic"""
        left = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Header
        header = ctk.CTkFrame(left, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=20)
        
        # Section title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(anchor="w", pady=(0, 15))
        
        ctk.CTkLabel(
            title_frame,
            text="Entrada de Pedido",
            font=('Arial', 18, 'bold'),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # AI indicator
        ai_badge = ctk.CTkFrame(
            title_frame,
            fg_color=COLORS['ai_blue'],
            width=60,
            height=24,
            corner_radius=12
        )
        ai_badge.pack(side="left", padx=(10, 0))
        
        ctk.CTkLabel(
            ai_badge,
            text="AI",
            font=('Arial', 11, 'bold'),
            text_color=COLORS['bg_primary']
        ).pack(expand=True)
        
        # Client selection with two-step selection
        self._create_client_selector(header)
        
        # Text input area
        input_container = ctk.CTkFrame(left, fg_color=COLORS['bg_card'], corner_radius=8)
        input_container.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        
        # Input label
        input_label = ctk.CTkLabel(
            input_container,
            text="Texto del pedido",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        input_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.text_area = ctk.CTkTextbox(
            input_container,
            font=FONTS['mono'],
            wrap="word",
            border_width=2,
            border_color=COLORS['border'],
            fg_color=COLORS['bg_primary'],
            text_color=COLORS['text_primary'],
            corner_radius=6
        )
        self.text_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Placeholder
        placeholder = """📝 Pega tu pedido con producto, cantidad y unidad
   (copiado de Excel o WhatsApp)

📌 Las secciones van en MAYÚSCULAS
📌 Cada producto o sección en una sola línea

Ejemplo:
COCINA
3 kg jitomate
2 pz lechuga
BARRA
5 litros leche
────────────────────────────────
Presiona 'Procesar Pedido' cuando estés listo"""
        
        self.text_area.insert("1.0", placeholder)
        
        # Action buttons
        self._create_action_buttons(left)

    def _create_client_selector(self, parent):
        """Create modern client selector with two-step selection"""
        selector_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=8)
        selector_frame.pack(fill="x", pady=(0, 20))
        
        # Grid layout
        selector_frame.grid_columnconfigure(1, weight=1)
        selector_frame.grid_columnconfigure(3, weight=1)
        
        # Group selector
        ctk.CTkLabel(
            selector_frame,
            text="Grupo",
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Load all clients and extract unique groups
        self.all_clients = []
        self.groups_dict = {}
        self.clients_by_group = {}

        if self.controller and hasattr(self.controller, 'get_all_clients'):
            try:
                self.all_clients = self.controller.get_all_clients()
                for client in self.all_clients:
                    group_key = client['clave_grupo']
                    group_name = client['nombre_tipo']
                    group_label = f"{group_key} - {group_name}"
                    if group_label not in self.groups_dict:
                        self.groups_dict[group_label] = []
                    self.groups_dict[group_label].append(client)
                logger.info(f"    ✓ {len(self.all_clients)} clientes en {len(self.groups_dict)} grupos")
            except Exception as e:
                logger.error(f"Error cargando clientes: {e}")

        group_options = ["-- Seleccionar Grupo --"] + sorted(list(self.groups_dict.keys()))
        
        self.group_selector = ctk.CTkComboBox(
            selector_frame,
            values=group_options,
            command=self.on_group_selected,
            width=250,
            state="readonly",
            font=FONTS['body'],
            fg_color=COLORS['bg_primary'],
            border_color=COLORS['border'],
            button_color=COLORS['ai_blue'],
            button_hover_color=COLORS['ai_purple']
        )
        self.group_selector.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="ew")
        self.group_selector.set("-- Seleccionar Grupo --")
        
        # Client selector
        ctk.CTkLabel(
            selector_frame,
            text="Cliente",
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=2, padx=15, pady=15, sticky="w")
        
        self.client_selector = ctk.CTkComboBox(
            selector_frame,
            values=["-- Primero selecciona un grupo --"],
            command=self.on_client_selected,
            state="disabled",
            font=FONTS['body'],
            fg_color=COLORS['bg_primary'],
            border_color=COLORS['border'],
            button_color=COLORS['ai_blue'],
            button_hover_color=COLORS['ai_purple']
        )
        self.client_selector.grid(row=0, column=3, padx=(0, 15), pady=15, sticky="ew")
        
        # Client info
        self.client_info_label = ctk.CTkLabel(
            selector_frame,
            text="",
            font=FONTS['small'],
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        self.client_info_label.grid(row=1, column=0, columnspan=4, padx=15, pady=(0, 15), sticky="w")

    def _create_action_buttons(self, parent):
        """Create action buttons for input panel"""
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        # Process button
        process_btn = ctk.CTkButton(
            buttons_frame,
            text="⚙️ Procesar Pedido",
            font=('Arial', 15, 'bold'),
            fg_color=COLORS['ai_green'],
            hover_color="#059669",
            height=45,
            corner_radius=8,
            command=self.process_order
        )
        process_btn.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Clear button
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Limpiar",
            font=('Arial', 15, 'bold'),
            fg_color=COLORS['ai_purple'],
            hover_color="#7C3AED",
            height=45,
            corner_radius=8,
            command=self.clear_text
        )
        clear_btn.pack(side="left", fill="both", expand=True)

    def create_right_panel(self, parent):
        """Create right panel with results and controls"""
        right = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], corner_radius=12)
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Header
        header = ctk.CTkFrame(right, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=20)
        
        # Title
        ctk.CTkLabel(
            header,
            text="Procesamiento",
            font=('Arial', 18, 'bold'),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # Save button
        save_btn = ctk.CTkButton(
            header,
            text="💾 Guardar",
            font=('Arial', 12, 'bold'),
            fg_color=COLORS['ai_green'],
            hover_color="#059669",
            height=32,
            corner_radius=8,
            width=120,
            command=self.save_and_send_to_receipt_generator
        )
        save_btn.pack(side="right")
        
        # Results container
        self.results_frame = ctk.CTkScrollableFrame(
            right,
            fg_color=COLORS['bg_card'],
            corner_radius=8
        )
        self.results_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        
        # Placeholder
        self.show_placeholder()
        
        # Bottom controls
        controls_frame = ctk.CTkFrame(right, fg_color="transparent")
        controls_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        # Sections button
        self.sections_btn = ctk.CTkButton(
            controls_frame,
            text="📁 Secciones (0/0)",
            font=('Arial', 12, 'bold'),
            fg_color=COLORS['ai_purple'],
            hover_color="#7C3AED",
            height=36,
            corner_radius=8,
            state="disabled",
            command=self.show_section_management
        )
        self.sections_btn.pack(fill="x")

    def show_placeholder(self):
        """Show placeholder when no results"""
        # Clear existing
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Placeholder
        placeholder_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        placeholder_frame.pack(expand=True, fill="both")
        
        ctk.CTkLabel(
            placeholder_frame,
            text="📋\n\nProcesa un pedido para ver resultados",
            font=('Arial', 14),
            text_color=COLORS['text_secondary']
        ).pack(expand=True)

    def create_bottom_bar(self):
        """Create status bar at bottom"""
        bottom_bar = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS['bg_secondary'],
            height=50,
            corner_radius=0
        )
        bottom_bar.pack(fill="x", padx=0, pady=0)
        bottom_bar.pack_propagate(False)
        
        # Content
        content = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            content,
            text="💡 Pega el pedido de WhatsApp y presiona 'Procesar Pedido'",
            font=FONTS['small'],
            text_color=COLORS['ai_blue'],
            justify="left"
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        
        # Stats label
        self.stats_label = ctk.CTkLabel(
            content,
            text="",
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        )
        self.stats_label.pack(side="right")

    def _initialize_content(self):
        """Inicializa el contenido de la ventana después de crear UI"""
        try:
            if not self._is_destroyed and self.winfo_exists():
                logger.info("📊 Inicializando contenido...")
                self.update_stats(0, 0)
                self.update_status(INITIAL_STATUS)
                
                if hasattr(self, 'sections_btn'):
                    self.sections_btn.configure(state="disabled")
                
                logger.info("✨ Contenido cargado")
        except Exception as e:
            logger.error(f"❌ Error inicializando contenido: {e}")

    def clear_text(self):
        """Limpia el área de texto"""
        try:
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", DEFAULT_TEXT_AREA)
            logger.info("🔄 Texto limpiado")
        except Exception as e:
            logger.error(f"Error limpiando texto: {e}")

    def save_and_send_to_receipt_generator(self):
        """Guarda el pedido procesado y lo envía al generador de recibos"""
        try:
            if not hasattr(self, 'controller') or self.controller is None:
                show_error(self, "Error", "No hay controller disponible")
                logger.error("Controller no disponible para guardar")
                return
            
            # ✅ OBTENER RESULTADOS ACTUALES (como en versión original)
            # Esto incluye los overrides manuales si los hay
            if not hasattr(self.controller, 'get_current_results'):
                show_error(self, "Error", "Controller no tiene método get_current_results")
                logger.error("get_current_results no disponible")
                return
            
            parse_result, matches = self.controller.get_current_results()
            
            if not parse_result or not hasattr(parse_result, 'items'):
                show_warning(self, "Advertencia", "No hay resultados para guardar")
                logger.warning("No hay parse_result o items")
                return
            
            # ✅ CONSTRUIR RESULTADOS CON OVERRIDES MANUALES (como en versión original)
            results = []
            for item, match in zip(parse_result.items, matches):
                # Verificar si hay override manual
                line_num = getattr(item, 'line_number', None)
                if line_num and hasattr(self, 'manual_overrides') and line_num in self.manual_overrides:
                    # Usar el producto seleccionado manualmente
                    match = self.manual_overrides[line_num]
                    logger.debug(f"Usando override manual para línea {line_num}")
                
                results.append((item, match))
            
            logger.info(f"📦 Obtenidos {len(results)} resultados con overrides")
            
            # ✅ OBTENER QUANTITY OVERRIDES SI EXISTEN
            quantity_overrides = None
            if hasattr(self, 'quantity_overrides'):
                quantity_overrides = self.quantity_overrides
                if quantity_overrides:
                    logger.info(f"📝 Aplicando {len(quantity_overrides)} modificaciones de cantidad")
            
            # ✅ BUSCAR MÉTODO Y EJECUTAR
            if hasattr(self.controller, 'send_to_receipt_generator'):
                try:
                    result_tuple = self.controller.send_to_receipt_generator(results, quantity_overrides)
                    
                    # ✅ Manejar retorno correctamente
                    if isinstance(result_tuple, tuple):
                        success, folio = result_tuple
                    else:
                        success = result_tuple
                        folio = None
                    
                    if success:
                        # Formatear folio solo si es int
                        if folio and isinstance(folio, int):
                            folio_str = f"#{folio:06d}"
                            msg = f"✅ Pedido enviado al generador de recibos\n\nFolio asignado: {folio_str}"
                            logger.info(f"✅ Pedido guardado con folio {folio_str}")
                        else:
                            msg = "✅ Pedido enviado al generador de recibos"
                            logger.info("✅ Pedido guardado")
                        
                        show_success(self, "Éxito", msg)
                    else:
                        show_error(self, "Error", "No se pudo guardar el pedido")
                        logger.error("send_to_receipt_generator retornó False")
                
                except TypeError as te:
                    logger.error(f"TypeError: {te}")
                    show_error(self, "Error", f"Error de tipo: {str(te)}")
                
                except Exception as e:
                    show_error(self, "Error", f"Error al guardar: {str(e)}")
                    logger.error(f"Error en send_to_receipt_generator: {e}")
            else:
                show_error(self, "Error", "send_to_receipt_generator no disponible en controller")
                logger.error("send_to_receipt_generator no encontrado")
        
        except Exception as e:
            show_error(self, "Error", f"Error al guardar: {str(e)}")
            logger.error(f"Error en save_and_send_to_receipt_generator: {e}")

    def on_closing(self):
        """Cierra la ventana de forma ordenada"""
        try:
            logger.info("🔌 Cerrando ventana...")
            self._is_destroyed = True
            self.destroy()
        except Exception as e:
            logger.error(f"Error cerrando ventana: {e}")

    def create_help_button(self):
        """Crea el botón flotante de ayuda con Chumi y el Centro de Ayuda"""
        try:
            logger.info("🔧 Creando Centro de Ayuda y Botón...")
            
            image_path = os.path.join(
                os.path.dirname(__file__),
                'assets/chumi_feliz.png'
            )
            
            # Crear Centro de Ayuda
            logger.info("  📚 Inicializando HelpCenterWindow...")
            self.help_center = HelpCenterWindow(self, image_path=image_path)
            logger.info("  ✅ HelpCenterWindow creado")
            
            # Crear botón de ayuda
            logger.info("  🔘 Inicializando AnimatedHelpButton...")
            self.help_button = AnimatedHelpButton(
                self,
                image_path=image_path,
                bg_color='#FFA500',
                text_color='white'
            )
            logger.info("  ✅ AnimatedHelpButton creado")
            
            # Establecer callback
            logger.info("  📌 Configurando callback...")
            self.help_button.set_click_callback(self.on_help_clicked)
            logger.info("  ✅ Callback configurado")
            
            logger.info("✅ Botón de ayuda creado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error creando botón de ayuda: {e}")
            import traceback
            traceback.print_exc()

    def on_help_clicked(self):
        """Se ejecuta cuando el usuario hace click en el botón de ayuda"""
        try:
            logger.info("👤 Abriendo Centro de Ayuda...")
            if hasattr(self, 'help_center') and self.help_center:
                logger.info("✅ Centro de Ayuda existe, abriendo...")
                self.help_center.open()
                logger.info("✅ Centro de Ayuda abierto correctamente")
            else:
                logger.error("❌ Centro de Ayuda no inicializado")
        except Exception as e:
            logger.error(f"❌ Error abriendo Centro de Ayuda: {e}")
            import traceback
            traceback.print_exc()