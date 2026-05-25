# -*- coding: utf-8 -*-
"""
help_center_window.py - CENTRO DE AYUDA FUTURISTA NEÓN
Estilo ciberpunk con colores neón y efectos modernos
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import logging
import os

logger = logging.getLogger(__name__)

class HelpCenterWindow:
    """Centro de Ayuda futurista con estilo neón"""
    
    def __init__(self, parent, image_path=None):
        self.parent = parent
        self.window = None
        self.active_tab = 'guia'
        self.tab_frames = {}
        self.tab_buttons = {}
        self.photo = None
    
    def open(self):
        """Abre la ventana"""
        try:
            if self.window and self.window.winfo_exists():
                self.window.lift()
                return
            
            # Crear ventana
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title("Centro de Ayuda - AYUDA")
            self.window.geometry("1100x850")
            self.window.configure(fg_color='#0A0E27')
            
            # ========== HEADER FUTURISTA ==========
            header_content = ctk.CTkFrame(self.window, fg_color='#0A0E27')
            header_content.pack(fill='x', padx=25, pady=15)
            
            # Logo con borde neón
            logo_frame = ctk.CTkFrame(
                header_content,
                fg_color='#0A0E27',
                corner_radius=10,
                border_width=2,
                border_color='#00FF41',
                width=50,
                height=50
            )
            logo_frame.pack(side='left', padx=(0, 15))
            
            # Etiqueta de logo
            logo_label = ctk.CTkLabel(
                logo_frame,
                text='◆',
                text_color='#00FF41',
                font=('Helvetica', 28)
            )
            logo_label.pack(expand=True)
            
            title_frame = ctk.CTkFrame(header_content, fg_color='#0A0E27')
            title_frame.pack(side='left', fill='both', expand=True)
            
            ctk.CTkLabel(
                title_frame,
                text='CENTRO DE AYUDA',
                text_color='#00FF41',
                font=('Courier New', 24, 'bold')
            ).pack(anchor='w')
            
            ctk.CTkLabel(
                title_frame,
                text='> Sistema de Soporte Integrado',
                text_color='#00FFFF',
                font=('Courier New', 10)
            ).pack(anchor='w', pady=(2, 0))
            
            ctk.CTkLabel(
                title_frame,
                text='[Guía Completa de Pedidos]',
                text_color='#00FF41',
                font=('Courier New', 9)
            ).pack(anchor='w', pady=(2, 0))
            
            # Botón cerrar neón
            ctk.CTkButton(
                header_content,
                text='✕',
                width=40,
                height=40,
                fg_color='#0A0E27',
                text_color='#00FF41',
                border_width=2,
                border_color='#00FF41',
                font=('Courier New', 18),
                hover_color='#1a1f3a',
                command=self.window.destroy
            ).pack(side='right')
            
            # Separador neón
            ctk.CTkFrame(self.window, fg_color='#00FF41', height=2).pack(fill='x')
            
            # ========== TABS FUTURISTA ==========
            tabs_frame = ctk.CTkFrame(self.window, fg_color='#0A0E27')
            tabs_frame.pack(fill='x', padx=25, pady=15)
            
            tabs = [
                ('guia', '> GUÍA'),
                ('novedades', '> NOVEDADES'),
                ('ejemplos', '> EJEMPLOS'),
                ('unidades', '> UNIDADES'),
                ('faq', '> FAQ')
            ]
            
            for tab_id, tab_label in tabs:
                btn = ctk.CTkButton(
                    tabs_frame,
                    text=tab_label,
                    fg_color='#0A0E27',
                    text_color='#666666',
                    font=('Courier New', 11, 'bold'),
                    border_width=0,
                    hover_color='#1A1A2E',
                    command=lambda t=tab_id: self._switch_tab(t)
                )
                btn.pack(side='left', padx=8)
                self.tab_buttons[tab_id] = btn
            
            # Separador neón
            ctk.CTkFrame(self.window, fg_color='#00FF41', height=2).pack(fill='x', padx=25)
            
            # ========== CONTENIDO ==========
            content_container = ctk.CTkFrame(self.window, fg_color='#0A0E27')
            content_container.pack(fill='both', expand=True, padx=25, pady=20)
            
            # Crear tabs
            self._create_tab_guia(content_container)
            self._create_tab_novedades(content_container)
            self._create_tab_ejemplos(content_container)
            self._create_tab_unidades(content_container)
            self._create_tab_faq(content_container)
            
            # Mostrar primera tab
            self._switch_tab('guia')
            
            logger.info("[HelpCenter] ✅ Ventana futurista abierta exitosamente")
            
        except Exception as e:
            logger.error(f"[HelpCenter] Error: {e}")
            import traceback
            traceback.print_exc()
    
    def _switch_tab(self, tab_id):
        """Cambia la tab activa"""
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(
                    fg_color='#0A0E27',
                    text_color='#00FF41'
                )
            else:
                btn.configure(
                    fg_color='#0A0E27',
                    text_color='#666666'
                )
        
        for tid, frame in self.tab_frames.items():
            if tid == tab_id:
                frame.pack(fill='both', expand=True)
            else:
                frame.pack_forget()
        
        self.active_tab = tab_id
    
    def _create_tab_guia(self, parent):
        """Tab: Guía Rápida"""
        frame = ctk.CTkScrollableFrame(parent, fg_color='#0A0E27')
        self.tab_frames['guia'] = frame
        
        # Sección principal
        self._add_box(frame, '[ LO QUE DEBES HACER ]', '#00FF41', '#0A0E27', '#00FF41')
        self._add_text(frame, 'Para que el sistema entienda tu pedido, SIEMPRE debes escribir 3 cosas:')
        self._add_list_items(frame, [
            ('CANTIDAD', 'Un número (2, 1, 0.5, etc)'),
            ('UNIDAD', 'Cómo se mide (kg, g, lt, pz, docena, manojo, caja, bolsa, paquete, bote, lata, etc)'),
            ('PRODUCTO', 'Qué es lo que pides (cebolla, tomate, lechuga, etc)')
        ])
        
        # Cómo funciona internamente
        self._add_box(frame, '[ CÓMO FUNCIONA ]', '#00FFFF', '#0A0E27', '#00FFFF')
        self._add_text(frame, 'Cuando envías un pedido, el sistema automáticamente:')
        
        self._add_step(frame, '>>> PASO 1: Reorganiza', 'Si escribes: "cebolla 2 kg" → Sistema: "2 kg de cebolla"')
        self._add_step(frame, '>>> PASO 2: Lee', 'Extrae → Cantidad: 2, Unidad: kg, Producto: cebolla')
        self._add_step(frame, '>>> PASO 3: Busca', 'Busca en base de datos y retorna el producto más parecido')
        
        self._add_box(frame, '[ RESULTADO ]', '#00FF41', '#0A0E27', '#00FF41')
        self._add_text(frame, '✓ 2 kg de Cebolla Blanca (ID: 12)')
        self._add_text(frame, 'El sistema entiende exactamente qué quieres.')
        
        # Consejos
        self._add_box(frame, '[ CONSEJOS ]', '#00FFFF', '#0A0E27', '#00FFFF')
        self._add_list_items(frame, [
            ('Sé específico', 'Bueno: "cebolla blanca 2 kg" vs Menos: "cebolla 2 kg"'),
            ('Orden flexible', 'Funciona igual: "2 kg cebolla" o "cebolla 2 kg"'),
            ('Si no entiende', 'Verifica: cantidad + unidad + producto'),
            ('Fracciones OK', '"1/2 kg tomate" o "0.5 kg tomate" - Igual')
        ])
    
    def _create_tab_novedades(self, parent):
        """Tab: Novedades - Nuevas funcionalidades"""
        frame = ctk.CTkScrollableFrame(parent, fg_color='#0A0E27')
        self.tab_frames['novedades'] = frame
        
        # Header
        ctk.CTkLabel(
            frame,
            text='[ NUEVAS FUNCIONALIDADES ]',
            text_color='#00FF41',
            font=('Courier New', 14, 'bold')
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            frame,
            text='> Actualizaciones recientes del sistema',
            text_color='#00FFFF',
            font=('Courier New', 10)
        ).pack(pady=(0, 15))
        
        # === 1. PRECIOS POR CLIENTE ===
        self._add_box(frame, '[ 💰 PRECIOS POR CLIENTE ]', '#00FF41', '#0A0E27', '#00FF41')
        self._add_text(frame, 'Ahora los precios se cargan automáticamente según el cliente seleccionado:')
        self._add_list_items(frame, [
            ('Selecciona Grupo', 'Primero elige el grupo de clientes'),
            ('Selecciona Cliente', 'Luego elige el cliente específico'),
            ('Precios Automáticos', 'Los precios se actualizan al instante según el grupo del cliente'),
            ('Re-procesamiento', 'Si ya procesaste un pedido y cambias de cliente, los precios se actualizan solos')
        ])
        
        # === 2. EDICIÓN DE CANTIDADES ===
        self._add_box(frame, '[ ✏️ EDICIÓN DE CANTIDADES ]', '#00FFFF', '#0A0E27', '#00FFFF')
        self._add_text(frame, 'Puedes corregir cantidades directamente en cada tarjeta de producto:')
        self._add_list_items(frame, [
            ('Campo Cantidad', 'Edita el número directamente - se actualiza en vivo'),
            ('Selector de Unidad', 'Cambia entre kg, pz, caja, etc. con el menú desplegable'),
            ('Subtotal', 'Se calcula automáticamente: Cantidad × Precio'),
            ('Total Aproximado', 'Barra al final con la suma total del pedido')
        ])
        
        ctk.CTkLabel(
            frame,
            text='⚠️ Los precios son aproximaciones. Verifica siempre en Generador de Recibos.',
            text_color='#F59E0B',
            font=('Courier New', 9, 'italic')
        ).pack(anchor='w', padx=25, pady=(5, 15))
        
        # === 3. CONVERSIÓN GRAMOS A KILOS ===
        self._add_box(frame, '[ ⚖️ CONVERSIÓN AUTOMÁTICA DE GRAMOS ]', '#00FF41', '#0A0E27', '#00FF41')
        self._add_text(frame, 'Los gramos se convierten automáticamente a kilogramos:')
        
        conversions = [
            ('"500gr de chile"', '→ 0.50 kg de chile'),
            ('"250g de ajonjolí"', '→ 0.25 kg de ajonjolí'),
            ('"1000gr de frijol"', '→ 1.00 kg de frijol'),
        ]
        
        for before, after in conversions:
            row = ctk.CTkFrame(frame, fg_color='#0A0E27')
            row.pack(fill='x', padx=25, pady=2)
            
            ctk.CTkLabel(row, text=before, text_color='#666666', font=('Courier New', 10)).pack(side='left')
            ctk.CTkLabel(row, text=after, text_color='#00FF41', font=('Courier New', 10, 'bold')).pack(side='left', padx=(10, 0))
        
        self._add_text(frame, 'Esto es porque los precios están configurados por kilogramo.')
        
        # === 4. GESTIÓN DE SECCIONES ===
        self._add_box(frame, '[ 📁 GESTIÓN DE SECCIONES ]', '#00FFFF', '#0A0E27', '#00FFFF')
        self._add_text(frame, 'Organiza tu pedido en secciones para el Receipt Generator:')
        self._add_list_items(frame, [
            ('Detección Automática', 'El sistema detecta secciones como "COCINA:", "BODEGA:", etc.'),
            ('Renombrar', 'Haz clic en el nombre de la sección para editarlo'),
            ('Confirmar/Descartar', 'Usa las casillas para elegir qué secciones incluir'),
            ('Eliminar', 'Usa el botón X para quitar una sección completamente')
        ])
        
        # === 5. ENVÍO A RECEIPT GENERATOR ===
        self._add_box(frame, '[ 📤 ENVÍO MEJORADO ]', '#00FF41', '#0A0E27', '#00FF41')
        self._add_text(frame, 'Al enviar al Receipt Generator:')
        self._add_list_items(frame, [
            ('Cantidades Corregidas', 'Se envían las cantidades que editaste, no las originales'),
            ('Secciones Organizadas', 'Los productos van a sus secciones correspondientes'),
            ('Precios del Cliente', 'Se usan los precios específicos del cliente seleccionado'),
            ('Folio Asignado', 'Recibes confirmación con el número de folio')
        ])
        
        # === FLUJO RECOMENDADO ===
        self._add_box(frame, '[ 🚀 FLUJO RECOMENDADO ]', '#8B5CF6', '#0A0E27', '#8B5CF6')
        
        steps = [
            '1. Pega el pedido de WhatsApp',
            '2. Presiona "Procesar Pedido"',
            '3. Selecciona Grupo y Cliente',
            '4. Revisa cantidades y corrige si es necesario',
            '5. Verifica el total aproximado',
            '6. Gestiona las secciones (si aplica)',
            '7. Presiona "Guardar y Enviar"'
        ]
        
        for step in steps:
            ctk.CTkLabel(
                frame,
                text=f'  {step}',
                text_color='#00FFFF',
                font=('Courier New', 10)
            ).pack(anchor='w', padx=25, pady=2)

    def _create_tab_ejemplos(self, parent):
        """Tab: Ejemplos"""
        frame = ctk.CTkScrollableFrame(parent, fg_color='#0A0E27')
        self.tab_frames['ejemplos'] = frame
        
        # Ejemplos correctos
        self._add_box(frame, '[ ✓ CORRECTO ]', '#00FF41', '#0A0E27', '#00FF41')
        self._add_text(frame, 'Todas estas formas funcionan:')
        
        examples = [
            '2 kg de cebolla',
            'cebolla 2 kg',
            '3 piezas de lechuga',
            'lechuga 3 pz',
            '0.5 kg de tomate',
            'tomate 0.5 kg',
            '1 manojo de cilantro',
            '1 litro de leche',
            '2 cajas de huevo'
        ]
        
        for ex in examples:
            ctk.CTkLabel(
                frame,
                text=f'  > {ex}',
                text_color='#00FF41',
                font=('Courier New', 10)
            ).pack(anchor='w', padx=15, pady=2)
        
        # Nota
        ctk.CTkLabel(
            frame,
            text='> El sistema es flexible: no importa el orden, siempre que incluyas cantidad + unidad + producto',
            text_color='#00FFFF',
            font=('Courier New', 10),
            wraplength=1000,
            justify='left'
        ).pack(pady=15, padx=15)
        
        # Ejemplos incorrectos
        self._add_box(frame, '[ ✗ INCORRECTO ]', '#FF6B6B', '#0A0E27', '#FF6B6B')
        self._add_text(frame, 'Estas formas NO funcionan:')
        
        wrong = [
            ('dame cilantro', '→ falta cantidad y unidad'),
            ('2 de cebolla', '→ falta la unidad'),
            ('kg de tomate', '→ falta la cantidad'),
            ('cebolla', '→ falta cantidad y unidad')
        ]
        
        for w, reason in wrong:
            ctk.CTkLabel(
                frame,
                text=f'  x "{w}" {reason}',
                text_color='#FF9999',
                font=('Courier New', 10)
            ).pack(anchor='w', padx=15, pady=2)
        
        ctk.CTkLabel(
            frame,
            text='> Solución: Agrega la cantidad y unidad que falta',
            text_color='#FFB3B3',
            font=('Courier New', 10, 'italic')
        ).pack(pady=10, padx=15, anchor='w')
        
        # Múltiples productos
        self._add_box(frame, '[ MÚLTIPLES PRODUCTOS ]', '#00FFFF', '#0A0E27', '#00FFFF')
        self._add_text(frame, 'Puedes escribir varios productos, uno por línea:')
        
        code_text = '2 kg de cebolla\n1 manojo de cilantro\n0.5 kg de tomate'
        ctk.CTkLabel(
            frame,
            text=code_text,
            text_color='#00FF41',
            font=('Courier New', 10),
            justify='left'
        ).pack(anchor='w', padx=25, pady=10)
    
    def _create_tab_unidades(self, parent):
        """Tab: Unidades"""
        frame = ctk.CTkScrollableFrame(parent, fg_color='#0A0E27')
        self.tab_frames['unidades'] = frame
        
        ctk.CTkLabel(
            frame,
            text='[ UNIDADES RECONOCIDAS ]',
            text_color='#00FF41',
            font=('Courier New', 13, 'bold')
        ).pack(pady=(0, 15))
        
        ctk.CTkLabel(
            frame,
            text='> Puedes usar cualquiera de estos nombres y el sistema los entiende igual.',
            text_color='#00FFFF',
            font=('Courier New', 10)
        ).pack(pady=(0, 15))
        
        units = [
            # Weight units
            ('kg', 'KILOGRAMOS', ['kg', 'kilo', 'kilos'], '#00FF41'),
            ('g', 'GRAMOS → KG', ['g', 'gr', 'gramos', '(se convierte a kg)'], '#F59E0B'),

            # Volume units
            ('lt', 'LITROS', ['litro', 'litros', 'lt', 'l'], '#00FF41'),

            # Count units
            ('pz', 'PIEZAS', ['pz', 'pza', 'pieza', 'piezas'], '#00FF41'),
            ('docena', 'DOCENA', ['docena', 'docenas', 'dz'], '#00FFFF'),

            # Container units
            ('mjo', 'MANOJOS', ['mjo', 'manojo', 'manojos', 'ramo'], '#00FFFF'),
            ('caja', 'CAJAS', ['caja', 'cajas', 'charola'], '#00FFFF'),
            ('bolsa', 'BOLSAS', ['bolsa', 'bolsas'], '#00FF41'),
            ('paq', 'PAQUETES', ['paq', 'paquete', 'paquetes'], '#00FFFF'),
            ('bote', 'BOTES/FRASCOS', ['bote', 'botes', 'frasco'], '#00FF41'),
            ('botella', 'BOTELLAS', ['botella', 'botellas'], '#00FFFF'),
            ('lata', 'LATAS', ['lata', 'latas'], '#00FF41'),
            ('cubeta', 'CUBETAS', ['cubeta', 'cubetas'], '#00FFFF'),
            ('rollo', 'ROLLOS', ['rollo', 'rollos'], '#00FF41'),
            ('tableta', 'TABLETAS/BARRAS', ['tableta', 'tabletas', 'barra'], '#00FFFF'),
            ('burbuja', 'BURBUJAS', ['burbuja', 'burbujas'], '#00FF41'),

            # Special
            ('granel', 'A GRANEL', ['granel'], '#F59E0B')
        ]
        
        for abbr, name, examples, color in units:
            unit_frame = ctk.CTkFrame(
                frame,
                fg_color='#0A0E27',
                border_width=2,
                border_color=color,
                corner_radius=6
            )
            unit_frame.pack(fill='x', pady=8)
            
            title_f = ctk.CTkFrame(unit_frame, fg_color='#0A0E27')
            title_f.pack(fill='x', padx=12, pady=(10, 3))
            
            badge = ctk.CTkFrame(title_f, fg_color='#0A0E27', corner_radius=4, width=45, height=28, border_width=2, border_color=color)
            badge.pack(side='left', padx=(0, 10))
            
            ctk.CTkLabel(badge, text=abbr, text_color=color, font=('Courier New', 11, 'bold')).pack(expand=True)
            ctk.CTkLabel(title_f, text=name, text_color=color, font=('Courier New', 11, 'bold')).pack(side='left')
            
            ctk.CTkLabel(
                unit_frame,
                text=f'→ {", ".join(examples)}',
                text_color='#666666',
                font=('Courier New', 9)
            ).pack(padx=12, pady=(0, 10), anchor='w')
        
        # Nota sobre conversión
        note_frame = ctk.CTkFrame(frame, fg_color='#0A0E27', border_width=2, border_color='#F59E0B', corner_radius=6)
        note_frame.pack(fill='x', pady=15)
        
        ctk.CTkLabel(
            note_frame,
            text='⚠️ NOTA: Los gramos se convierten automáticamente a kilogramos',
            text_color='#F59E0B',
            font=('Courier New', 10, 'bold')
        ).pack(padx=12, pady=(10, 5), anchor='w')
        
        ctk.CTkLabel(
            note_frame,
            text='Ejemplo: "500gr de chile" → 0.50 kg de chile',
            text_color='#00FFFF',
            font=('Courier New', 9)
        ).pack(padx=12, pady=(0, 10), anchor='w')
    
    def _create_tab_faq(self, parent):
        """Tab: FAQ"""
        frame = ctk.CTkScrollableFrame(parent, fg_color='#0A0E27')
        self.tab_frames['faq'] = frame
        
        faqs = [
            ('¿Cómo funciona?', 'Escribe cantidad, unidad y producto. Ejemplo: "2 kg de cebolla"'),
            ('¿Importa el orden?', 'No. Puedes escribir "2 kg de cebolla" o "cebolla 2 kg". Igual.'),
            ('¿Si me equivoco?', 'El sistema te dirá. Verifica cantidad + unidad + producto.'),
            ('¿Necesito la unidad?', 'Sí. El sistema necesita saber kg, gramos, piezas, etc.'),
            ('¿Decimales?', 'Sí. "0.5 kg", "1.5 kg", "2.25 kg" funcionan.'),
            ('¿Fracciones?', 'Sí. "1/2 kg de tomate" o "0.5 kg de tomate" igual.'),
            ('¿Mal escrito?', 'Sí. "cevolla" → Sistema entiende "cebolla".'),
            ('¿Producto no existe?', 'Te lo dirá. Verifica el nombre.'),
            ('¿Similares?', 'Sí. El sistema busca automáticamente lo más parecido.'),
            ('¿100+ productos?', 'Sí, pero cada uno en una línea diferente.'),
            ('¿Aprende?', 'Sí. Si corriges algo, lo recuerda.'),
            ('¿Precisión?', 'Sé específico: "cebolla blanca" vs "cebolla".'),
        ]
        
        for question, answer in faqs:
            faq_box = ctk.CTkFrame(
                frame,
                fg_color='#0A0E27',
                border_width=2,
                border_color='#00FF41',
                corner_radius=6
            )
            faq_box.pack(fill='x', pady=8)
            
            # Pregunta
            q_frame = ctk.CTkFrame(faq_box, fg_color='#0A0E27')
            q_frame.pack(fill='x', padx=12, pady=(10, 5))
            
            ctk.CTkLabel(q_frame, text='>', font=('Courier New', 12, 'bold'), text_color='#00FF41').pack(side='left', padx=(0, 8))
            ctk.CTkLabel(
                q_frame,
                text=question,
                text_color='#00FF41',
                font=('Courier New', 10, 'bold'),
                wraplength=950,
                justify='left'
            ).pack(side='left', fill='x', expand=True)
            
            # Respuesta
            ctk.CTkLabel(
                faq_box,
                text=answer,
                text_color='#00FFFF',
                font=('Courier New', 9),
                wraplength=950,
                justify='left'
            ).pack(padx=40, pady=(0, 10), anchor='w')
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _add_box(self, parent, title, title_color, bg_color, border_color):
        """Agrega un título de sección con borde neón"""
        box = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=6,
            border_width=2,
            border_color=border_color
        )
        box.pack(fill='x', pady=(15, 5), padx=0)
        
        ctk.CTkLabel(
            box,
            text=title,
            text_color=title_color,
            font=('Courier New', 12, 'bold')
        ).pack(anchor='w', padx=12, pady=10)
    
    def _add_text(self, parent, text):
        """Agrega texto normal"""
        ctk.CTkLabel(
            parent,
            text=text,
            text_color='#00FFFF',
            font=('Courier New', 10),
            wraplength=1000,
            justify='left'
        ).pack(anchor='w', padx=15, pady=(5, 10))
    
    def _add_list_items(self, parent, items):
        """Agrega lista de items"""
        for label, desc in items:
            ctk.CTkLabel(
                parent,
                text=f'> {label}',
                text_color='#00FF41',
                font=('Courier New', 10, 'bold')
            ).pack(anchor='w', padx=25, pady=(5, 0))
            
            ctk.CTkLabel(
                parent,
                text=f'  {desc}',
                text_color='#666666',
                font=('Courier New', 9),
                wraplength=950,
                justify='left'
            ).pack(anchor='w', padx=25, pady=(0, 5))
    
    def _add_step(self, parent, title, description):
        """Agrega un paso"""
        ctk.CTkLabel(
            parent,
            text=title,
            text_color='#00FF41',
            font=('Courier New', 10, 'bold')
        ).pack(anchor='w', padx=25, pady=(8, 2))
        
        ctk.CTkLabel(
            parent,
            text=description,
            text_color='#00FFFF',
            font=('Courier New', 9),
            wraplength=950,
            justify='left'
        ).pack(anchor='w', padx=35, pady=(0, 5))