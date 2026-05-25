# -*- coding: utf-8 -*-
"""
window_display_results.py - Renderizado de resultados con edición de cantidades
Muestra tarjetas con colores según confianza, edición inline de cantidades,
subtotales por producto y total en vivo del pedido.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, Any
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)

# Colores del sistema
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
    'warning': '#F59E0B',
}

FONTS = {
    'title': ('Arial', 32, 'bold'),
    'heading': ('Arial', 20, 'bold'),
    'subheading': ('Arial', 16, 'normal'),
    'body': ('Arial', 13),
    'mono': ('Courier', 12),
    'small': ('Arial', 11),
}


class WindowDisplayResults:
    """Maneja la visualización de resultados con correcciones manuales y totales en vivo"""

    def _init_quantity_tracking(self):
        """Inicializa el tracking de cantidades modificadas"""
        if not hasattr(self, 'quantity_overrides'):
            self.quantity_overrides: Dict[int, Dict[str, Any]] = {}
        if not hasattr(self, 'total_label'):
            self.total_label = None
        if not hasattr(self, 'total_frame'):
            self.total_frame = None

    def _is_section_item(self, product_name: str, item) -> bool:
        """
        Detecta si un item es una sección (no producto)
        """
        section_keywords = [
            'sección', 'section', 'pedido', 'order', 'comida', 'bebida', 
            'entrada', 'plato principal', 'postre', 'almacén', 'storage',
            'personal', 'cocina', 'bodega', 'valentina'
        ]
        
        product_name_lower = product_name.lower()
        
        for keyword in section_keywords:
            if keyword in product_name_lower:
                return True
        
        return False

    def _create_section_header(self, section_name: str):
        """Crea header de sección estilo mockup"""
        section_frame = ctk.CTkFrame(
            self.results_frame,
            fg_color=COLORS['bg_card'],
            border_width=2,
            border_color=COLORS['ai_purple'],
            corner_radius=12
        )
        section_frame.pack(fill="x", pady=8, padx=5)
        
        content = ctk.CTkFrame(section_frame, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)
        
        header_row = ctk.CTkFrame(content, fg_color="transparent")
        header_row.pack(fill="x")
        
        ctk.CTkLabel(
            header_row,
            text="📁",
            font=('Arial', 18)
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            header_row,
            text=section_name.upper() if len(section_name) > 0 else "SECCIÓN",
            font=('Arial', 14, 'bold'),
            text_color=COLORS['text_primary'],
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            content,
            text="Sección del pedido",
            font=('Arial', 11),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(4, 0))

    def _create_total_bar(self):
        """Crea la barra de total en la parte inferior del results_frame"""
        self._init_quantity_tracking()
        
        # Si ya existe, destruir
        if hasattr(self, 'total_frame') and self.total_frame:
            try:
                self.total_frame.destroy()
            except:
                pass
        
        # Crear frame del total (sticky en la parte inferior)
        self.total_frame = ctk.CTkFrame(
            self.results_frame,
            fg_color=COLORS['bg_secondary'],
            corner_radius=12,
            border_width=2,
            border_color=COLORS['ai_green']
        )
        self.total_frame.pack(fill="x", pady=(15, 5), padx=5)
        
        content = ctk.CTkFrame(self.total_frame, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)
        
        # Row 1: Total
        total_row = ctk.CTkFrame(content, fg_color="transparent")
        total_row.pack(fill="x")
        
        ctk.CTkLabel(
            total_row,
            text="💰 TOTAL APROXIMADO",
            font=('Arial', 14, 'bold'),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        self.total_label = ctk.CTkLabel(
            total_row,
            text="$0.00",
            font=('Arial', 22, 'bold'),
            text_color=COLORS['ai_green']
        )
        self.total_label.pack(side="right")
        
        # Row 2: Leyenda
        ctk.CTkLabel(
            content,
            text="⚠️ Los precios son aproximaciones sincronizadas con los precios de venta del cliente y grupo. Verifica en Generador de Recibos.",
            font=('Arial', 9),
            text_color=COLORS['text_secondary'],
            wraplength=400
        ).pack(fill="x", pady=(8, 0))

    def _calculate_and_update_total(self):
        """Calcula y actualiza el total basado en los items actuales"""
        self._init_quantity_tracking()
        
        if not self.total_label:
            return
        
        try:
            parse_result, matches = self.controller.get_current_results()
            
            if not parse_result or not matches:
                self.total_label.configure(text="$0.00")
                return
            
            total = Decimal('0')
            items_with_price = 0
            items_without_price = 0
            
            for item, match in zip(parse_result.items, matches):
                if not match:
                    continue
                
                line_num = getattr(item, 'line_number', 0)
                
                # Obtener cantidad (override o original)
                if line_num in self.quantity_overrides:
                    quantity = Decimal(str(self.quantity_overrides[line_num].get('quantity', item.quantity)))
                else:
                    quantity = Decimal(str(item.quantity))
                
                # Obtener precio
                price = getattr(match, 'price', None)
                has_price = getattr(match, 'has_price', False)
                
                if price and has_price and price > 0:
                    subtotal = quantity * Decimal(str(price))
                    total += subtotal
                    items_with_price += 1
                else:
                    items_without_price += 1
            
            # Actualizar label
            if items_without_price > 0:
                self.total_label.configure(
                    text=f"${total:,.2f}*",
                    text_color=COLORS['ai_orange']
                )
            else:
                self.total_label.configure(
                    text=f"${total:,.2f}",
                    text_color=COLORS['ai_green']
                )
                
        except Exception as e:
            logger.error(f"Error calculando total: {e}")
            self.total_label.configure(text="$-.--")

    def display_results(self):
        """Muestra los resultados del procesamiento"""
        try:
            if self._is_destroyed or not self.winfo_exists():
                return
            
            self._init_quantity_tracking()
            
            # Limpiar resultados previos
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            
            # Validar controller
            if not self.controller or not hasattr(self.controller, 'get_current_results'):
                logger.error("Controller no tiene get_current_results")
                self.show_placeholder()
                return
            
            # Obtener resultados
            parse_result, matches = self.controller.get_current_results()
            
            if not parse_result or not hasattr(parse_result, 'items'):
                logger.warning("No hay resultados para mostrar")
                self.show_placeholder()
                return
            
            logger.info(f"📊 Mostrando {len(parse_result.items)} resultados...")

            # Guardar resultados en el controller
            if hasattr(self.controller, 'last_results'):
                self.controller.last_results = parse_result.items
            
            if hasattr(self.controller, 'last_matches'):
                self.controller.last_matches = matches

            # Crear tarjetas para cada item
            for item, match in zip(parse_result.items, matches):
                line_num = getattr(item, 'line_number', None)
                
                # Verificar si hay override manual de producto
                if line_num and line_num in self.manual_overrides:
                    match = self.manual_overrides[line_num]

                self.create_result_card(item, match)
            
            # Crear barra de total
            self._create_total_bar()
            
            # Calcular total inicial
            self._calculate_and_update_total()
            
            # Actualizar estadísticas
            total = len(parse_result.items)
            matched = sum(1 for m in matches if m and hasattr(m, 'confidence') and m.confidence >= 0.75)
            self.update_stats(total, matched)
            
            logger.info(f"✅ {total} items mostrados ({matched} con match)")
            
        except Exception as e:
            logger.error(f"❌ Error en display_results: {e}")
            import traceback
            traceback.print_exc()
            self.show_placeholder()

    def create_result_card(self, item, match):
        """
        Crea tarjeta de resultado con:
        - Edición inline de cantidad
        - Subtotal por producto
        - Colores según confianza
        """
        try:
            # Verificar si es sección
            is_section = False
            product_name = getattr(item, 'product_name', 'N/A')
            
            if not match or (hasattr(match, 'confidence') and match.confidence == 0):
                is_section = self._is_section_item(product_name, item)
            
            if is_section:
                self._create_section_header(product_name)
                return
            
            # === DETERMINAR COLOR DE CONFIANZA ===
            confidence = getattr(match, 'confidence', 0) if match else 0
            is_high_confidence = confidence >= 0.75
            
            if confidence >= 0.9:
                border_color = COLORS['ai_green']
                status_color = COLORS['ai_green']
                status_text = "✓ Exacto"
            elif confidence >= 0.75:
                border_color = COLORS['ai_blue']
                status_color = COLORS['ai_blue']
                status_text = f"≈ {confidence:.0%}"
            elif confidence >= 0.5:
                border_color = COLORS['ai_orange']
                status_color = COLORS['ai_orange']
                status_text = f"? {confidence:.0%}"
            else:
                border_color = COLORS['ai_red']
                status_color = COLORS['ai_red']
                status_text = "✗ Sin match"
            
            # === CREAR TARJETA ===
            card = ctk.CTkFrame(
                self.results_frame,
                fg_color=COLORS['bg_card'],
                border_width=2,
                border_color=border_color,
                corner_radius=12
            )
            card.pack(fill="x", pady=6, padx=5)
            
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=12)
            
            line_num = getattr(item, 'line_number', 0)
            
            # === ROW 1: Header con línea, original y status ===
            header_row = ctk.CTkFrame(content_frame, fg_color="transparent")
            header_row.pack(fill="x", pady=(0, 8))
            
            # Badge de línea
            badge = ctk.CTkFrame(
                header_row,
                fg_color=status_color,
                width=32,
                height=32,
                corner_radius=16
            )
            badge.pack(side="left", padx=(0, 10))
            badge.pack_propagate(False)
            
            ctk.CTkLabel(
                badge,
                text=f"#{line_num}",
                font=('Arial', 11, 'bold'),
                text_color=COLORS['bg_primary']
            ).pack(expand=True)
            
            # Texto original
            raw_text = getattr(item, 'raw_text', str(item))
            ctk.CTkLabel(
                header_row,
                text=f"Original: {raw_text}",
                font=('Arial', 10),
                text_color=COLORS['text_secondary'],
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
            
            # Status badge
            status_badge = ctk.CTkFrame(
                header_row,
                fg_color=status_color,
                corner_radius=12,
                height=24
            )
            status_badge.pack(side="right")
            
            ctk.CTkLabel(
                status_badge,
                text=status_text,
                font=('Arial', 10, 'bold'),
                text_color=COLORS['bg_primary']
            ).pack(padx=10, pady=2)
            
            # === ROW 2: Nombre del producto (destacado) ===
            matched_name = getattr(match, 'matched_name', product_name) if match else product_name
            
            ctk.CTkLabel(
                content_frame,
                text=f"📦 {matched_name}",
                font=('Arial', 15, 'bold'),
                text_color=COLORS['text_primary'],
                anchor="w"
            ).pack(fill="x", pady=(0, 6))
            
            # === ROW 3: Cantidad y Unidad (primera fila) ===
            quantity_row = ctk.CTkFrame(content_frame, fg_color=COLORS['bg_secondary'], corner_radius=8)
            quantity_row.pack(fill="x", pady=(0, 8))
            
            # Fila superior: Cantidad + Unidad
            top_row = ctk.CTkFrame(quantity_row, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(10, 5))
            
            # Obtener valores actuales
            original_quantity = getattr(item, 'quantity', 1)
            original_unit = getattr(item, 'unit', 'kg')
            if hasattr(original_unit, 'value'):
                original_unit = original_unit.value
            
            # ✅ Prioridad de unidad:
            # 1. quantity_overrides (usuario editó o seleccionó producto)
            # 2. match.unit (unidad del producto de BD)
            # 3. original_unit del item parseado
            
            # Verificar si hay override de cantidad/unidad
            if line_num in self.quantity_overrides:
                current_qty = self.quantity_overrides[line_num].get('quantity', original_quantity)
                current_unit = self.quantity_overrides[line_num].get('unit', original_unit)
            else:
                current_qty = original_quantity
                # Usar unidad del producto de BD si existe
                match_unit = getattr(match, 'unit', None) if match else None
                current_unit = match_unit if match_unit else original_unit
            
            # === Cantidad (editable) ===
            qty_frame = ctk.CTkFrame(top_row, fg_color="transparent")
            qty_frame.pack(side="left", padx=(0, 20))
            
            ctk.CTkLabel(
                qty_frame,
                text="Cantidad:",
                font=('Arial', 11),
                text_color=COLORS['text_secondary']
            ).pack(side="left", padx=(0, 8))
            
            qty_entry = ctk.CTkEntry(
                qty_frame,
                width=80,
                height=32,
                font=('Arial', 14, 'bold'),
                fg_color=COLORS['bg_card'],
                border_color=COLORS['border'],
                text_color=COLORS['text_primary'],
                justify="center"
            )
            qty_entry.pack(side="left")
            qty_entry.insert(0, f"{float(current_qty):.2f}")
            
            # === Unidad (solo lectura - muestra unidad real del producto) ===
            unit_frame = ctk.CTkFrame(top_row, fg_color="transparent")
            unit_frame.pack(side="left")

            ctk.CTkLabel(
                unit_frame,
                text="Unidad:",
                font=('Arial', 11),
                text_color=COLORS['text_secondary']
            ).pack(side="left", padx=(0, 8))

            # Label en lugar de ComboBox - solo lectura
            unit_label = ctk.CTkLabel(
                unit_frame,
                text=current_unit if current_unit else 'kg',
                font=('Arial', 12, 'bold'),
                text_color=COLORS['ai_blue'],
                width=90,
                height=32,
                fg_color=COLORS['bg_card'],
                corner_radius=6
            )
            unit_label.pack(side="left")
            
            # Fila inferior: Precio + Subtotal
            bottom_row = ctk.CTkFrame(quantity_row, fg_color="transparent")
            bottom_row.pack(fill="x", padx=12, pady=(5, 10))
            
            # === Precio unitario ===
            price = getattr(match, 'price', None) if match else None
            has_price = getattr(match, 'has_price', False) if match else False
            
            price_frame = ctk.CTkFrame(bottom_row, fg_color="transparent")
            price_frame.pack(side="left", padx=(0, 30))
            
            ctk.CTkLabel(
                price_frame,
                text="Precio unitario:",
                font=('Arial', 11),
                text_color=COLORS['text_secondary']
            ).pack(side="left", padx=(0, 8))
            
            if price and has_price and price > 0:
                price_text = f"${float(price):.2f}"
                price_color = COLORS['ai_green']
            else:
                price_text = "⚠️ Sin precio"
                price_color = COLORS['ai_orange']
            
            price_label = ctk.CTkLabel(
                price_frame,
                text=price_text,
                font=('Arial', 13, 'bold'),
                text_color=price_color
            )
            price_label.pack(side="left")
            
            # === Subtotal ===
            subtotal_frame = ctk.CTkFrame(bottom_row, fg_color="transparent")
            subtotal_frame.pack(side="right")
            
            ctk.CTkLabel(
                subtotal_frame,
                text="Subtotal:",
                font=('Arial', 11),
                text_color=COLORS['text_secondary']
            ).pack(side="left", padx=(0, 8))
            
            if price and has_price and price > 0:
                subtotal = float(current_qty) * float(price)
                subtotal_text = f"${subtotal:,.2f}"
                subtotal_color = COLORS['ai_green']
            else:
                subtotal_text = "$-.--"
                subtotal_color = COLORS['text_secondary']
            
            subtotal_label = ctk.CTkLabel(
                subtotal_frame,
                text=subtotal_text,
                font=('Arial', 13, 'bold'),
                text_color=subtotal_color
            )
            subtotal_label.pack(side="left")
            
            # === Bind para actualización en vivo ===
            def on_quantity_change(event=None, ln=line_num, entry=qty_entry,
                                   product_unit=current_unit, sub_lbl=subtotal_label,
                                   item_price=price, has_p=has_price):
                try:
                    # Obtener nueva cantidad
                    qty_str = entry.get().strip()
                    try:
                        new_qty = float(qty_str)
                        if new_qty <= 0:
                            new_qty = 0.01
                    except ValueError:
                        return

                    # Guardar override - usar la unidad real del producto (no cambiar)
                    self.quantity_overrides[ln] = {
                        'quantity': new_qty,
                        'unit': product_unit  # Siempre usar la unidad del producto
                    }

                    # Actualizar subtotal local
                    if item_price and has_p and item_price > 0:
                        new_subtotal = new_qty * float(item_price)
                        sub_lbl.configure(
                            text=f"${new_subtotal:,.2f}",
                            text_color=COLORS['ai_green']
                        )

                    # Actualizar total general
                    self._calculate_and_update_total()

                except Exception as e:
                    logger.error(f"Error actualizando cantidad: {e}")

            qty_entry.bind("<KeyRelease>", on_quantity_change)
            qty_entry.bind("<FocusOut>", on_quantity_change)
            
            # === ROW 4: Botones según confianza ===
            if is_high_confidence:
                change_btn = ctk.CTkButton(
                    content_frame,
                    text="🔄 Cambiar Producto",
                    command=lambda i=item: self.show_suggestions(i, allow_same=True),
                    height=32,
                    fg_color=COLORS['bg_secondary'],
                    hover_color=COLORS['bg_primary'],
                    border_width=1,
                    border_color=COLORS['border'],
                    font=('Arial', 10),
                    anchor="center"
                )
                change_btn.pack(fill="x")
            else:
                btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                btn_frame.pack(fill="x")
                
                ctk.CTkButton(
                    btn_frame,
                    text="🔍 Ver Sugerencias",
                    command=lambda i=item: self.show_suggestions(i),
                    height=32,
                    fg_color=COLORS['ai_blue'],
                    hover_color=COLORS['ai_purple'],
                    font=('Arial', 10)
                ).pack(side="left", expand=True, fill="x", padx=(0, 5))

                ctk.CTkButton(
                    btn_frame,
                    text="✏️ Corregir",
                    command=lambda i=item: self.manual_correction(i),
                    height=32,
                    fg_color=COLORS['bg_secondary'],
                    hover_color=COLORS['ai_orange'],
                    border_width=1,
                    border_color=COLORS['border'],
                    font=('Arial', 10)
                ).pack(side="left", expand=True, fill="x", padx=(5, 0))
            
        except Exception as e:
            logger.error(f"Error creando tarjeta: {e}")
            import traceback
            traceback.print_exc()

    def get_modified_items(self):
        """
        Retorna los items con sus cantidades/unidades modificadas.
        Útil para enviar al Receipt Generator con las correcciones.
        """
        self._init_quantity_tracking()
        
        try:
            parse_result, matches = self.controller.get_current_results()
            
            if not parse_result:
                return []
            
            modified_items = []
            
            for item, match in zip(parse_result.items, matches):
                line_num = getattr(item, 'line_number', 0)
                
                # Aplicar override de cantidad si existe
                if line_num in self.quantity_overrides:
                    quantity = self.quantity_overrides[line_num].get('quantity', item.quantity)
                    unit = self.quantity_overrides[line_num].get('unit', getattr(item, 'unit', 'pz'))
                else:
                    quantity = item.quantity
                    unit = getattr(item, 'unit', 'pz')
                
                # Aplicar override de match si existe
                if line_num in self.manual_overrides:
                    match = self.manual_overrides[line_num]
                
                modified_items.append({
                    'item': item,
                    'match': match,
                    'quantity': quantity,
                    'unit': unit,
                    'line_number': line_num
                })
            
            return modified_items
            
        except Exception as e:
            logger.error(f"Error obteniendo items modificados: {e}")
            return []

    def show_suggestions(self, item, allow_same=False):
        """Muestra dialog de sugerencias de productos"""
        try:
            if not self.controller or not hasattr(self.controller, 'get_suggestions'):
                logger.error("Controller no tiene get_suggestions")
                return

            initial_suggestions = self.controller.get_suggestions(item.product_name, 5)

            dialog = ctk.CTkToplevel(self)
            dialog.title("🔍 Sugerencias de Productos")
            dialog.geometry("650x700")
            dialog.transient(self)
            dialog.grab_set()
            dialog.configure(fg_color=COLORS['bg_primary'])
            
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() - 650) // 2
            y = (dialog.winfo_screenheight() - 700) // 2
            dialog.geometry(f"650x700+{x}+{y}")
            
            # Header
            header = ctk.CTkFrame(dialog, fg_color=COLORS['bg_secondary'])
            header.pack(fill="x", padx=20, pady=20)
            
            ctk.CTkLabel(
                header,
                text=f"Sugerencias para: {item.product_name}",
                font=FONTS['heading'],
                text_color=COLORS['text_primary']
            ).pack(pady=15)

            # Sugerencias automáticas
            ctk.CTkLabel(
                dialog,
                text="🤖 Sugerencias automáticas:",
                font=('Arial', 13, 'bold'),
                text_color=COLORS['text_primary']
            ).pack(pady=(10, 10), padx=20, anchor="w")

            initial_frame = ctk.CTkScrollableFrame(
                dialog, 
                height=150,
                fg_color=COLORS['bg_secondary']
            )
            initial_frame.pack(fill="x", padx=20, pady=(0, 10))

            if initial_suggestions:
                for sug in initial_suggestions:
                    conf = getattr(sug, 'confidence', 0)
                    name = getattr(sug, 'matched_name', 'N/A')
                    price = getattr(sug, 'price', None)
                    
                    btn_text = f"{name} ({conf:.0%})"
                    if price and price > 0:
                        btn_text += f" - ${float(price):.2f}"
                    
                    btn = ctk.CTkButton(
                        initial_frame,
                        text=btn_text,
                        command=lambda s=sug: self.accept_suggestion(item, s, dialog, learn=(not allow_same)),
                        height=38,
                        fg_color=COLORS['bg_card'],
                        hover_color=COLORS['ai_blue'],
                        anchor="w",
                        font=('Arial', 12)
                    )
                    btn.pack(fill="x", pady=3)
            else:
                ctk.CTkLabel(
                    initial_frame,
                    text="No hay sugerencias disponibles",
                    font=('Arial', 12),
                    text_color=COLORS['text_secondary']
                ).pack(pady=20)

            # Búsqueda manual
            ctk.CTkLabel(
                dialog,
                text="🔎 Buscar producto:",
                font=('Arial', 13, 'bold'),
                text_color=COLORS['text_primary']
            ).pack(pady=(15, 10), padx=20, anchor="w")

            search_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            search_frame.pack(fill="x", padx=20)

            search_entry = ctk.CTkEntry(
                search_frame,
                placeholder_text="Escribe para buscar...",
                height=40,
                font=('Arial', 13),
                fg_color=COLORS['bg_secondary'],
                border_color=COLORS['border']
            )
            search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

            results_frame = ctk.CTkScrollableFrame(
                dialog,
                height=200,
                fg_color=COLORS['bg_secondary']
            )
            results_frame.pack(fill="x", padx=20, pady=10)

            def do_search(event=None):
                query = search_entry.get().strip()
                if len(query) < 2:
                    return
                
                for widget in results_frame.winfo_children():
                    widget.destroy()
                
                results = self.controller.get_suggestions(query, 10)
                
                if results:
                    for res in results:
                        conf = getattr(res, 'confidence', 0)
                        name = getattr(res, 'matched_name', 'N/A')
                        price = getattr(res, 'price', None)
                        
                        btn_text = f"{name} ({conf:.0%})"
                        if price and price > 0:
                            btn_text += f" - ${float(price):.2f}"
                        
                        btn = ctk.CTkButton(
                            results_frame,
                            text=btn_text,
                            command=lambda s=res: self.accept_suggestion(item, s, dialog, learn=True),
                            height=36,
                            fg_color=COLORS['bg_card'],
                            hover_color=COLORS['ai_green'],
                            anchor="w",
                            font=('Arial', 12)
                        )
                        btn.pack(fill="x", pady=2)
                else:
                    ctk.CTkLabel(
                        results_frame,
                        text="Sin resultados",
                        font=('Arial', 12),
                        text_color=COLORS['text_secondary']
                    ).pack(pady=20)

            search_entry.bind("<KeyRelease>", do_search)
            search_entry.focus()

            # Botón cerrar
            ctk.CTkButton(
                dialog,
                text="Cerrar",
                command=dialog.destroy,
                height=36,
                fg_color=COLORS['bg_secondary'],
                hover_color=COLORS['ai_purple'],
                font=('Arial', 11)
            ).pack(fill="x", padx=20, pady=(10, 20))

        except Exception as e:
            logger.error(f"Error mostrando sugerencias: {e}")
            import traceback
            traceback.print_exc()

    def accept_suggestion(self, item, suggestion, dialog, learn=True):
        """Acepta una sugerencia de producto y actualiza la unidad"""
        try:
            line_num = getattr(item, 'line_number', None)
            
            if not line_num:
                logger.warning("No se pudo obtener line_number del item")
                return
            
            # Guardar override de producto
            self.manual_overrides[line_num] = suggestion
            logger.info(f"✓ Override guardado para línea {line_num}: {getattr(suggestion, 'matched_name', 'N/A')}")
            
            # ✅ También actualizar la unidad con la del producto seleccionado
            product_unit = getattr(suggestion, 'unit', None)
            if product_unit:
                # Mantener la cantidad actual si existe, solo actualizar unidad
                current_qty = getattr(item, 'quantity', 1)
                if line_num in self.quantity_overrides:
                    current_qty = self.quantity_overrides[line_num].get('quantity', current_qty)
                
                self.quantity_overrides[line_num] = {
                    'quantity': current_qty,
                    'unit': product_unit
                }
                logger.info(f"✓ Unidad actualizada para línea {line_num}: {product_unit}")
            
            dialog.destroy()
            self.display_results()
            
            if learn and self.controller and hasattr(self.controller, 'learn_correction'):
                try:
                    self.controller.learn_correction(
                        item.product_name,
                        getattr(suggestion, 'matched_name', 'N/A')
                    )
                except Exception as e:
                    logger.warning(f"No se pudo guardar corrección aprendida: {e}")
            
        except Exception as e:
            logger.error(f"Error aceptando sugerencia: {e}")

    def manual_correction(self, item):
        """Corrección manual simple"""
        try:
            dialog = ctk.CTkInputDialog(
                text=f"Escribe el nombre correcto para:\n'{item.product_name}'",
                title="✏️ Corrección Manual"
            )
            
            correct_name = dialog.get_input()
            
            if correct_name and correct_name.strip() and self.controller:
                logger.info(f"Corrección manual: '{item.product_name}' → '{correct_name}'")
                
                if hasattr(self.controller, 'accept_suggestion'):
                    try:
                        self.controller.accept_suggestion(item.product_name, correct_name)
                    except Exception as e:
                        logger.warning(f"Error aceptando sugerencia en controller: {e}")
                
                self.process_order()
            
        except Exception as e:
            logger.error(f"Error en corrección manual: {e}")

    def show_placeholder(self):
        """Muestra mensaje cuando no hay resultados"""
        placeholder = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        placeholder.pack(fill="both", expand=True, pady=100)

        ctk.CTkLabel(
            placeholder,
            text="📭 Sin resultados",
            font=('Arial', 16, 'bold'),
            text_color=COLORS['text_secondary']
        ).pack()

        ctk.CTkLabel(
            placeholder,
            text="Procesa un pedido para ver resultados",
            font=('Arial', 12),
            text_color=COLORS['text_secondary']
        ).pack(pady=10)

    def update_stats(self, total: int, matched: int):
        """Actualiza estadísticas en el footer"""
        try:
            if hasattr(self, 'items_value'):
                self.items_value.configure(text=str(total))
            
            if hasattr(self, 'matched_value'):
                self.matched_value.configure(text=str(matched))
            
            pending = total - matched
            if hasattr(self, 'pending_value'):
                self.pending_value.configure(text=str(pending))
            
            logger.debug(f"Stats actualizadas: {total} items, {matched} matched, {pending} pending")
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")

    def update_status(self, message: str, status_type: str = "info"):
        """Actualiza el mensaje de estado"""
        try:
            if not hasattr(self, 'status_label'):
                return
            
            color_map = {
                'success': COLORS['ai_green'],
                'warning': COLORS['ai_orange'],
                'error': COLORS['ai_red'],
                'info': COLORS['ai_blue'],
            }
            
            text_color = color_map.get(status_type, COLORS['text_secondary'])
            
            self.status_label.configure(
                text=message,
                text_color=text_color
            )
            
            logger.debug(f"Status: {message}")
        except Exception as e:
            logger.error(f"Error actualizando status: {e}")
