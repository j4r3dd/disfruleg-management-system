"""
Ubicuo AI - Interfaz Gráfica Principal
Sistema completo de procesamiento de pedidos
"""

import customtkinter as ctk
from typing import List, Optional
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ..core.ubicuo_parser import UbicuoParser, ParsedItem
from core.ubicuo_matcher import UbicuoMatcher, MatchResult
from core.ubicuo_learning import UbicuoLearning


class UbicuoAI(ctk.CTk):
    """Ventana principal de Ubicuo AI"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de ventana
        self.title("Ubicuo AI - Sistema Inteligente de Pedidos")
        self.geometry("1400x900")
        
        # Tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Inicializar componentes
        self.parser = UbicuoParser()
        self.matcher = UbicuoMatcher()
        self.learning = UbicuoLearning()
        
        # Cargar diccionario de aprendizaje
        self.matcher.set_learning_dictionary(self.learning.get_all_corrections())
        
        # Variables
        self.parsed_items: List[ParsedItem] = []
        self.match_results: List[Optional[MatchResult]] = []
        self.current_session = "general"
        
        # Crear UI
        self.create_ui()
        
        # Simular carga de productos (en producción, conectar a BD)(queda pendiende la carga conexción con la base de datos)
        self.load_sample_products()
    
    def create_ui(self):
        """Crea la interfaz de usuario"""
        
        # === PANEL SUPERIOR ===
        top_panel = ctk.CTkFrame(self)
        top_panel.pack(fill="x", padx=10, pady=10)
        
        # Logo y título
        title_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(
            title_frame,
            text=" UBICUO AI",
            font=("Arial", 28, "bold"),
            text_color="#2D9B6C"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Sistema Inteligente de Procesamiento de Pedidos",
            font=("Arial", 12),
            text_color="gray"
        ).pack(anchor="w")
        
        # Estadísticas
        stats_frame = ctk.CTkFrame(top_panel)
        stats_frame.pack(side="right", padx=20)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="📊 Items: 0 | ✓ Matches: 0 | ⚠ Pendientes: 0",
            font=("Arial", 12)
        )
        self.stats_label.pack(padx=15, pady=10)
        
        # === CONTENEDOR PRINCIPAL ===
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- PANEL IZQUIERDO (Entrada de texto) ---
        left_panel = ctk.CTkFrame(main_container)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Header
        header_left = ctk.CTkFrame(left_panel, height=50)
        header_left.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_left,
            text="📋 Pegar Pedido de WhatsApp",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)
        
        # Selector de sesión
        session_frame = ctk.CTkFrame(header_left, fg_color="transparent")
        session_frame.pack(side="right", padx=10)
        
        ctk.CTkLabel(session_frame, text="Sesión:").pack(side="left", padx=5)
        
        self.session_selector = ctk.CTkComboBox(
            session_frame,
            values=["general", "cocina", "barra", "piso", "comida_personal", "limpieza"],
            width=150,
            command=self.on_session_change
        )
        self.session_selector.pack(side="left")
        self.session_selector.set("general")
        
        # Área de texto
        self.text_area = ctk.CTkTextbox(
            left_panel,
            font=("Courier", 12),
            wrap="word"
        )
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botones de acción
        button_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="🚀 Procesar Pedido",
            command=self.process_order,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#2D9B6C",
            hover_color="#27AE60"
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="🗑️ Limpiar",
            command=self.clear_text,
            height=40,
            font=("Arial", 14),
            fg_color="#E74C3C",
            hover_color="#C0392B"
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        # --- PANEL DERECHO (Resultados) ---
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Header
        header_right = ctk.CTkFrame(right_panel, height=50)
        header_right.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_right,
            text="✨ Resultados del Procesamiento",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)
        
        # Botones de exportación
        export_frame = ctk.CTkFrame(header_right, fg_color="transparent")
        export_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(
            export_frame,
            text="📥 Enviar a Receipt Generator",
            command=self.send_to_receipt_generator,
            width=200
        ).pack(side="left", padx=5)
        
        # Área de resultados (scrollable)
        self.results_frame = ctk.CTkScrollableFrame(right_panel)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === BARRA INFERIOR ===
        bottom_bar = ctk.CTkFrame(self, height=40)
        bottom_bar.pack(fill="x", side="bottom", padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(
            bottom_bar,
            text="💡 Pega el pedido de WhatsApp y presiona 'Procesar Pedido'",
            font=("Arial", 11),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=20)
        
        # Info del sistema de aprendizaje
        learning_stats = self.learning.get_statistics()
        self.learning_label = ctk.CTkLabel(
            bottom_bar,
            text=f"🧠 Aprendizaje: {learning_stats['total_entries']} correcciones guardadas",
            font=("Arial", 11),
            text_color="gray"
        )
        self.learning_label.pack(side="right", padx=20)
    
    def load_sample_products(self):
        """Carga productos de ejemplo (en producción, conectar a BD)"""
        sample_products = [
            {'id': 1, 'nombre': 'Chile Serrano', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 45.00},
            {'id': 2, 'nombre': 'Papa Cambray', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 32.00},
            {'id': 3, 'nombre': 'Papa Blanca', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 28.00},
            {'id': 4, 'nombre': 'Limón', 'categoria': 'Frutas', 'unidad': 'kg', 'precio': 25.00},
            {'id': 5, 'nombre': 'Cebolla Blanca', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 22.00},
            {'id': 6, 'nombre': 'Aguacate', 'categoria': 'Frutas', 'unidad': 'kg', 'precio': 85.00},
            {'id': 7, 'nombre': 'Jitomate Saladet', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 28.00},
            {'id': 8, 'nombre': 'Jitomate Bola', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 32.00},
            {'id': 9, 'nombre': 'Hoja de Plátano', 'categoria': 'Verduras', 'unidad': 'manojo', 'precio': 15.00},
            {'id': 10, 'nombre': 'Chile Morita', 'categoria': 'Chiles', 'unidad': 'gr', 'precio': 120.00},
            {'id': 11, 'nombre': 'Chile Guajillo', 'categoria': 'Chiles', 'unidad': 'kg', 'precio': 95.00},
            {'id': 12, 'nombre': 'Zanahoria', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 18.00},
            {'id': 13, 'nombre': 'Lechuga Sangría', 'categoria': 'Verduras', 'unidad': 'pz', 'precio': 25.00},
            {'id': 14, 'nombre': 'Lechuga Italiana', 'categoria': 'Verduras', 'unidad': 'pz', 'precio': 30.00},
            {'id': 15, 'nombre': 'Huevo', 'categoria': 'Abarrotes', 'unidad': 'kg', 'precio': 42.00},
            {'id': 16, 'nombre': 'Fresa', 'categoria': 'Frutas', 'unidad': 'caja', 'precio': 65.00},
            {'id': 17, 'nombre': 'Frambuesa', 'categoria': 'Frutas', 'unidad': 'caja', 'precio': 85.00},
            {'id': 18, 'nombre': 'Zarzamora', 'categoria': 'Frutas', 'unidad': 'caja', 'precio': 80.00},
            {'id': 19, 'nombre': 'Blueberry', 'categoria': 'Frutas', 'unidad': 'caja', 'precio': 95.00},
            {'id': 20, 'nombre': 'Espárragos', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 120.00},
            {'id': 21, 'nombre': 'Albahaca', 'categoria': 'Hierbas', 'unidad': 'manojo', 'precio': 20.00},
            {'id': 22, 'nombre': 'Higo', 'categoria': 'Frutas', 'unidad': 'gr', 'precio': 150.00},
            {'id': 23, 'nombre': 'Perejil Chino', 'categoria': 'Hierbas', 'unidad': 'manojo', 'precio': 15.00},
            {'id': 24, 'nombre': 'Perejil', 'categoria': 'Hierbas', 'unidad': 'manojo', 'precio': 12.00},
            {'id': 25, 'nombre': 'Betabel', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 24.00},
            {'id': 26, 'nombre': 'Pimiento Verde', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 38.00},
            {'id': 27, 'nombre': 'Pimiento Rojo', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 45.00},
            {'id': 28, 'nombre': 'Pimiento Amarillo', 'categoria': 'Verduras', 'unidad': 'kg', 'precio': 42.00},
        ]
        
        self.matcher.set_products_db(sample_products)
        self.update_status(f"✓ {len(sample_products)} productos cargados en memoria")
    
    def process_order(self):
        """Procesa el pedido pegado"""
        text = self.text_area.get("1.0", "end-1c").strip()
        
        if not text:
            self.update_status("⚠️ Por favor pega un pedido primero", "warning")
            return
        
        self.update_status("🔄 Procesando pedido...", "info")
        
        # Paso 1: Parsear el texto
        self.parsed_items = self.parser.parse_text(text)
        
        if not self.parsed_items:
            self.update_status("❌ No se pudieron extraer productos del texto", "error")
            return
        
        # Paso 2: Hacer matching con la BD
        self.match_results = []
        for item in self.parsed_items:
            match = self.matcher.match(item.product_name, item.unit)
            self.match_results.append(match)
        
        # Paso 3: Mostrar resultados
        self.display_results()
        
        # Actualizar estadísticas
        matched_count = sum(1 for m in self.match_results if m and m.confidence >= 0.75)
        self.update_stats(len(self.parsed_items), matched_count)
        
        self.update_status(f"✓ Procesamiento completo: {matched_count}/{len(self.parsed_items)} productos identificados", "success")
    
    def display_results(self):
        """Muestra los resultados en el panel derecho"""
        # Limpiar resultados anteriores
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        for i, (parsed, match) in enumerate(zip(self.parsed_items, self.match_results)):
            self.create_result_card(parsed, match, i)
    
    def create_result_card(self, parsed: ParsedItem, match: Optional[MatchResult], index: int):
        """Crea una tarjeta de resultado"""
        # Card container
        card = ctk.CTkFrame(self.results_frame, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Header con número de línea
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            header,
            text=f"#{parsed.line_number}",
            font=("Arial", 12, "bold"),
            width=40
        ).pack(side="left")
        
        # Estado
        if match and match.confidence >= 0.75:
            status_color = "#27AE60"
            status_icon = "✓"
            status_text = f"{match.confidence:.0%}"
        elif match:
            status_color = "#F39C12"
            status_icon = "⚠"
            status_text = f"{match.confidence:.0%}"
        else:
            status_color = "#E74C3C"
            status_icon = "✗"
            status_text = "Sin match"
        
        status_label = ctk.CTkLabel(
            header,
            text=f"{status_icon} {status_text}",
            font=("Arial", 11, "bold"),
            text_color=status_color
        )
        status_label.pack(side="right")
        
        # Contenido
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=5)
        
        # Original
        ctk.CTkLabel(
            content,
            text=f"Original: {parsed.raw_text}",
            font=("Arial", 10),
            text_color="gray",
            anchor="w"
        ).pack(fill="x")
        
        # Parseado
        ctk.CTkLabel(
            content,
            text=f"📦 {parsed.product_name} • {parsed.quantity} {parsed.unit}",
            font=("Arial", 12),
            anchor="w"
        ).pack(fill="x", pady=2)
        
        # Match
        if match:
            match_text = f"→ {match.matched_product}"
            
            # Check if product has valid price
            has_valid_price = (
                hasattr(match, 'has_price') and match.has_price and
                hasattr(match, 'price') and match.price and match.price > 0
            )
            
            if has_valid_price:
                match_text += f" • ${match.price:.2f}/{match.unit}"
            else:
                match_text += f" • ⚠️ SIN PRECIO"
                
            if match.category:
                match_text += f" • {match.category}"
            
            # Use warning color if no price
            text_color = "#F39C12" if not has_valid_price else "#3498DB"
            
            ctk.CTkLabel(
                content,
                text=match_text,
                font=("Arial", 11, "bold"),
                text_color=text_color,
                anchor="w"
            ).pack(fill="x")
        
        # Botones de acción si no hay match o es bajo
        if not match or match.confidence < 0.75:
            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkButton(
                actions,
                text="🔍 Ver Sugerencias",
                command=lambda p=parsed: self.show_suggestions(p),
                width=150,
                height=28
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                actions,
                text="✏️ Corregir Manualmente",
                command=lambda p=parsed, i=index: self.manual_correction(p, i),
                width=150,
                height=28
            ).pack(side="left", padx=2)
    
    def show_suggestions(self, parsed: ParsedItem):
        """Muestra sugerencias para un producto"""
        suggestions = self.matcher.get_suggestions(parsed.product_name, limit=5)
        
        # Crear ventana de sugerencias
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sugerencias")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text=f"Sugerencias para: {parsed.product_name}",
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        if suggestions:
            for sug in suggestions:
                btn = ctk.CTkButton(
                    dialog,
                    text=f"{sug.matched_product} ({sug.confidence:.0%})",
                    command=lambda s=sug: self.accept_suggestion(parsed, s, dialog),
                    height=40
                )
                btn.pack(fill="x", padx=20, pady=5)
        else:
            ctk.CTkLabel(dialog, text="No hay sugerencias disponibles").pack(pady=20)
    
    def accept_suggestion(self, parsed: ParsedItem, suggestion: MatchResult, dialog):
        """Acepta una sugerencia y la aprende"""
        self.learning.add_correction(parsed.product_name, suggestion.matched_product)
        self.matcher.set_learning_dictionary(self.learning.get_all_corrections())
        dialog.destroy()
        self.process_order()  # Reprocesar
        self.update_status(f"✓ Corrección aprendida: {parsed.product_name} → {suggestion.matched_product}", "success")
    
    def manual_correction(self, parsed: ParsedItem, index: int):
        """Permite corrección manual"""
        dialog = ctk.CTkInputDialog(
            text=f"Escribe el nombre correcto para:\n'{parsed.product_name}'",
            title="Corrección Manual"
        )
        correct_name = dialog.get_input()
        
        if correct_name:
            self.learning.add_correction(parsed.product_name, correct_name)
            self.matcher.set_learning_dictionary(self.learning.get_all_corrections())
            self.process_order()
            self.update_status(f"✓ Corrección aprendida: {parsed.product_name} → {correct_name}", "success")
    
    def send_to_receipt_generator(self):
        """Envía los resultados al Receipt Generator"""
        if not self.match_results:
            self.update_status("⚠️ No hay resultados para enviar", "warning")
            return
        
        # Aquí integrarías con tu receipt_generator
        # Por ahora solo mostramos un mensaje
        matched = [m for m in self.match_results if m and m.confidence >= 0.75]
        
        if not matched:
            self.update_status("⚠️ No hay productos con confianza suficiente", "warning")
            return
        
        self.update_status(f"📤 {len(matched)} productos listos para Receipt Generator", "success")
        # TODO: Llamar a receipt_generator aquí
    
    def update_status(self, message: str, status_type: str = "info"):
        """Actualiza la barra de estado"""
        colors = {
            "info": "gray",
            "success": "#27AE60",
            "warning": "#F39C12",
            "error": "#E74C3C"
        }
        self.status_label.configure(text=message, text_color=colors.get(status_type, "gray"))
    
    def update_stats(self, total: int, matched: int):
        """Actualiza las estadísticas"""
        pending = total - matched
        self.stats_label.configure(
            text=f"📊 Items: {total} | ✓ Matches: {matched} | ⚠ Pendientes: {pending}"
        )
    
    def clear_text(self):
        """Limpia el área de texto"""
        self.text_area.delete("1.0", "end")
        self.parsed_items = []
        self.match_results = []
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.update_stats(0, 0)
        self.update_status("💡 Área limpiada. Lista para nuevo pedido")
    
    def on_session_change(self, value):
        """Maneja el cambio de sesión"""
        self.current_session = value
        self.update_status(f"📁 Sesión cambiada a: {value}")


def main():
    """Función principal"""
    app = UbicuoAI()
    app.mainloop()


if __name__ == "__main__":
    main()