"""
Módulo de Importación de Cotizaciones desde PDF
Sistema BodegaDisfruleg
Permite cargar cotizaciones en PDF y actualizar precios automáticamente

VERSIÓN MEJORADA - Octubre 2025
✅ NUEVAS CARACTERÍSTICAS:
- Integración con ModuleLogger y Event Bus
- Validador de integridad del sistema
- ProgressDialog para feedback visual
- Generación de reportes de importación
- Preview expandido con detalle de precios por grupo
- Soporte para letra Ü y caracteres especiales
- Manejo inteligente de productos sin precio
- Normalización extendida de unidades
- Búsqueda case-insensitive
- Aplicación de precios a TODOS los grupos con descuentos
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF para leer PDFs
import re
from decimal import Decimal
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import difflib
import traceback
from pathlib import Path

# ✅ IMPORTAR FUNCIONES DE NORMALIZACIÓN COMPARTIDAS
# ✅ IMPORTAR FUNCIONES DE NORMALIZACIÓN
try:
    from src.utils import (
        normalizar_unidad,
        normalizar_texto,
        normalizar_nombre,
        Normalizador
    )
    USAR_NORMALIZACION = True
except ImportError:
    print("⚠️ Módulo de normalización no disponible, usando funciones locales")
    USAR_NORMALIZACION = False
    
    # Fallback functions
    def normalizar_unidad(unidad):
        if not unidad:
            return "UNIDAD"
        return unidad.upper().strip()
    
    def normalizar_texto(texto):
        return texto.lower().strip() if texto else ""
    
    def normalizar_nombre(nombre):
        return nombre.strip() if nombre else ""

# ✅ IMPORTAR LOGGER Y EVENTBUS
try:
    from src.utils import (
        log_info,
        log_error,
        log_warning,
        ModuleLogger,
        publish,
        Events
    )
    USAR_LOGGER = True
    USAR_EVENTBUS = True
    
    # Crear logger para este módulo
    logger = ModuleLogger("CotizacionImporter")
    
except ImportError:
    print("⚠️ Módulos de logger/eventbus no disponibles")
    USAR_LOGGER = False
    USAR_EVENTBUS = False
    
    # Fallback logger
    class ModuleLogger:
        def __init__(self, name):
            self.name = name
        def info(self, msg): print(f"[INFO][{self.name}] {msg}")
        def error(self, msg): print(f"[ERROR][{self.name}] {msg}")
        def warning(self, msg): print(f"[WARNING][{self.name}] {msg}")
    
    logger = ModuleLogger("CotizacionImporter")
    
    def publish(event, data=None):
        pass

# Funciones auxiliares
def normalizar_nombre_producto(nombre):
    """Normaliza nombre de producto para comparación"""
    if not nombre:
        return ""
    if USAR_NORMALIZACION:
        return normalizar_texto(nombre)
    else:
        return nombre.lower().strip()

def comparar_productos_similar(nombre1, nombre2, umbral=0.8):
    """Compara dos nombres de productos"""
    import difflib
    n1 = normalizar_nombre_producto(nombre1)
    n2 = normalizar_nombre_producto(nombre2)
    ratio = difflib.SequenceMatcher(None, n1, n2).ratio()
    return ratio >= umbral


# ========================================
# ✅ NUEVA CLASE: PROGRESS DIALOG
# ========================================
class ProgressDialog(ctk.CTkToplevel):
    """
    ✅ NUEVA CLASE: Diálogo de progreso para operaciones largas
    """
    
    def __init__(self, parent, title="Procesando..."):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x150")
        self.transient(parent)
        self.grab_set()
        
        # Centrar en pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (150 // 2)
        self.geometry(f"400x150+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Label de estado
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Iniciando...",
            font=("Roboto", 14)
        )
        self.status_label.pack(pady=(0, 15))
        
        # Barra de progreso
        self.progress = ctk.CTkProgressBar(main_frame, width=340)
        self.progress.pack(pady=(0, 10))
        self.progress.set(0)
        
        # Label de detalles
        self.detail_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=("Roboto", 10),
            text_color="gray"
        )
        self.detail_label.pack()
    
    def update_progress(self, value, status="", detail=""):
        """Actualiza el progreso (value: 0.0 - 1.0)"""
        self.progress.set(value)
        if status:
            self.status_label.configure(text=status)
        if detail:
            self.detail_label.configure(text=detail)
        self.update()


# ========================================
# CLASE PRINCIPAL
# ========================================
class CotizacionImporter(ctk.CTkToplevel):
    """Ventana para importar cotizaciones desde PDF"""
    
    def __init__(self, parent, db_connection, user_info):
        """
        Inicializar importador de cotizaciones
        
        ✅ MEJORAS:
        - Integración con ModuleLogger
        - Integración con EventBus
        - Validaciones pre-vuelo
        """
        # ✅ VALIDACIÓN CRÍTICA
        if db_connection is None:
            raise Exception("db_connection es None")
        if not hasattr(db_connection, 'cursor'):
            raise Exception(f"db_connection inválido: {type(db_connection)}")
        if user_info is None:
            raise Exception("user_info es None")
        
        # ✅ CREAR VENTANA INDEPENDIENTE
        super().__init__(None)
        
        self.db = db_connection
        self.user_info = user_info
        self.productos_extraidos = []
        self.cambios_propuestos = []
        self.productos_sin_precio = []
        
        # ✅ NUEVO: Inicializar Logger
        if USAR_LOGGER:
            try:
                self.logger = logger  # Usar logger del módulo
            except:
                self.logger = None
                print("⚠️ No se pudo inicializar logger")
        else:
            self.logger = None
        
        # ✅ EventBus disponible globalmente mediante función publish()
        # No requiere inicialización de instancia
        
        # Configuración ventana
        self.title("Importar Cotización desde PDF")
        self.geometry("1200x700")
        
        # Hacer ventana independiente
        self.transient(None)
        self.lift()
        self.focus_force()
        
        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        
        # Build UI
        self.setup_ui()
        
        # ✅ NUEVO: Validar integridad del sistema
        self.after(500, self.validar_integridad_sistema)
    
    def validar_integridad_sistema(self):
        """
        ✅ NUEVA FUNCIÓN: Valida la integridad del sistema antes de permitir importar
        
        Verifica:
        - Todos los grupos tienen tipo de cliente asignado
        - Los descuentos están en rango válido (0-100%)
        - No hay conflictos en la BD
        """
        try:
            cursor = self.db.cursor()
            advertencias = []
            
            # 1. Verificar grupos sin tipo de cliente
            cursor.execute("""
                SELECT g.id_grupo, g.clave_grupo
                FROM grupo g
                WHERE g.id_tipo_cliente IS NULL
            """)
            grupos_sin_tipo = cursor.fetchall()
            
            if grupos_sin_tipo:
                nombres = ', '.join([g['clave_grupo'] if isinstance(g, dict) else g[1] for g in grupos_sin_tipo])
                advertencias.append(f"⚠️ Grupos sin tipo de cliente: {nombres}")
            
            # 2. Verificar descuentos fuera de rango
            cursor.execute("""
                SELECT nombre_tipo, descuento
                FROM tipo_cliente
                WHERE descuento < 0 OR descuento > 100
            """)
            descuentos_invalidos = cursor.fetchall()
            
            if descuentos_invalidos:
                nombres = ', '.join([f"{d['nombre_tipo'] if isinstance(d, dict) else d[0]} ({d['descuento'] if isinstance(d, dict) else d[1]}%)" for d in descuentos_invalidos])
                advertencias.append(f"⚠️ Descuentos inválidos: {nombres}")
            
            # 3. Si hay advertencias, mostrar diálogo
            if advertencias:
                mensaje = "Se encontraron las siguientes advertencias:\n\n"
                mensaje += "\n".join(advertencias)
                mensaje += "\n\n⚠️ Se recomienda corregir estos problemas antes de importar."
                mensaje += "\n\n¿Desea continuar de todos modos?"
                
                if not messagebox.askyesno("Advertencias del Sistema", mensaje, parent=self):
                    self.destroy()
                    return
            
            if self.logger:
                pass  # Logger deshabilitado temporalmente
                # self.logger.info(
                # 'Importación',
                # 'Validación de integridad',
                # f"Advertencias: {len(advertencias)}",
                # 'INFO' if not advertencias else 'WARNING'
                # )
                # TODO: Revisar y corregir esta llamada a logger.info()
                # El logger nuevo solo acepta un mensaje como string
                # logger.info("mensaje único")
        
        except Exception as e:
            print(f"Error en validación de integridad: {e}")
    
    def setup_ui(self):
        """Construir interfaz de usuario"""
        
        # ========== HEADER ==========
        header = ctk.CTkFrame(self, fg_color=("#2D9B6C", "#1a5d42"))
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="📄 Importar Cotización",
            font=("Roboto", 24, "bold"),
            text_color="white"
        ).pack(side="left", padx=20, pady=10)
        
        ctk.CTkLabel(
            header,
            text=f"Usuario: {self.user_info.get('username', 'N/A')}",
            font=("Roboto", 12),
            text_color="white"
        ).pack(side="right", padx=20)
        
        # ========== PANEL IZQUIERDO: CONTROLES ==========
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        left_panel.grid_rowconfigure(4, weight=1)
        
        # Sección 1: Selección de archivo
        ctk.CTkLabel(
            left_panel,
            text="1. Seleccionar Archivo PDF",
            font=("Roboto", 16, "bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        self.file_label = ctk.CTkLabel(
            left_panel,
            text="Ningún archivo seleccionado",
            font=("Roboto", 11),
            text_color="gray"
        )
        self.file_label.grid(row=1, column=0, sticky="w", padx=20, pady=5)
        
        ctk.CTkButton(
            left_panel,
            text="📁 Seleccionar PDF",
            command=self.seleccionar_pdf,
            height=40,
            font=("Roboto", 13, "bold")
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # Sección 2: Opciones de importación
        ctk.CTkLabel(
            left_panel,
            text="2. Opciones de Importación",
            font=("Roboto", 16, "bold")
        ).grid(row=3, column=0, sticky="w", padx=20, pady=(20, 10))
        
        options_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        options_frame.grid(row=4, column=0, sticky="new", padx=20, pady=5)
        
        self.actualizar_existentes = ctk.CTkCheckBox(
            options_frame,
            text="Actualizar productos existentes",
            font=("Roboto", 11)
        )
        self.actualizar_existentes.pack(anchor="w", pady=5)
        self.actualizar_existentes.select()
        
        self.agregar_nuevos = ctk.CTkCheckBox(
            options_frame,
            text="Agregar productos nuevos",
            font=("Roboto", 11)
        )
        self.agregar_nuevos.pack(anchor="w", pady=5)
        self.agregar_nuevos.select()
        
        self.mantener_stock = ctk.CTkCheckBox(
            options_frame,
            text="⚠️ NO modificar inventario/stock",
            font=("Roboto", 11, "bold"),
            text_color="#E74C3C"
        )
        self.mantener_stock.pack(anchor="w", pady=5)
        self.mantener_stock.select()
        self.mantener_stock.configure(state="disabled")
        
        # Sección 3: Acciones
        ctk.CTkLabel(
            left_panel,
            text="3. Procesar",
            font=("Roboto", 16, "bold")
        ).grid(row=5, column=0, sticky="w", padx=20, pady=(20, 10))
        
        self.btn_procesar = ctk.CTkButton(
            left_panel,
            text="🔍 Procesar PDF",
            command=self.procesar_pdf,
            height=45,
            font=("Roboto", 14, "bold"),
            fg_color="#3498DB",
            hover_color="#2980B9",
            state="disabled"
        )
        self.btn_procesar.grid(row=6, column=0, sticky="ew", padx=20, pady=5)
        
        self.btn_aplicar = ctk.CTkButton(
            left_panel,
            text="✅ Aplicar Cambios",
            command=self.aplicar_cambios,
            height=45,
            font=("Roboto", 14, "bold"),
            fg_color="#2ECC71",
            hover_color="#27AE60",
            state="disabled"
        )
        self.btn_aplicar.grid(row=7, column=0, sticky="ew", padx=20, pady=5)
        
        ctk.CTkButton(
            left_panel,
            text="Cancelar",
            command=self.destroy,
            height=35,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        ).grid(row=8, column=0, sticky="ew", padx=20, pady=(5, 20))
        
        # ========== PANEL DERECHO: PREVIEW ==========
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Header del preview
        preview_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        preview_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            preview_header,
            text="Vista Previa de Cambios",
            font=("Roboto", 18, "bold")
        ).pack(side="left")
        
        self.status_label = ctk.CTkLabel(
            preview_header,
            text="",
            font=("Roboto", 11),
            text_color="gray"
        )
        self.status_label.pack(side="right")
        
        # Tabla de cambios
        self.tabla_cambios = ctk.CTkScrollableFrame(right_panel)
        self.tabla_cambios.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.tabla_cambios.grid_columnconfigure(0, weight=1)
        
        self.mostrar_mensaje_inicial()
    
    def seleccionar_pdf(self):
        """Abrir diálogo para seleccionar archivo PDF"""
        filename = filedialog.askopenfilename(
            title="Seleccionar cotización PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            self.pdf_path = filename
            nombre_archivo = os.path.basename(filename)
            self.file_label.configure(
                text=f"✅ {nombre_archivo}",
                text_color="#2ECC71"
            )
            self.btn_procesar.configure(state="normal")
    
    def procesar_pdf(self):
        """
        Extraer datos del PDF y generar preview de cambios
        
        ✅ MEJORADO: Ahora con ProgressDialog para feedback visual
        """
        if not hasattr(self, 'pdf_path'):
            messagebox.showerror("Error", "Selecciona un archivo PDF primero")
            return
        
        # ✅ Crear diálogo de progreso
        progress = ProgressDialog(self, "Procesando PDF")
        
        try:
            # Paso 1: Extraer productos
            progress.update_progress(0.2, "Extrayendo productos del PDF...", "Analizando documento")
            self.update()
            
            self.productos_extraidos = self.extraer_productos_pdf(self.pdf_path)
            
            if not self.productos_extraidos:
                progress.destroy()
                mensaje = "No se pudieron extraer productos del PDF.\n"
                mensaje += "Verifica que el formato sea correcto."
                messagebox.showwarning("Sin datos", mensaje)
                self.status_label.configure(text="")
                return
            
            # Paso 2: Generar cambios
            progress.update_progress(0.5, "Analizando cambios...", f"{len(self.productos_extraidos)} productos encontrados")
            self.update()
            
            self.cambios_propuestos = self.generar_cambios_propuestos()
            
            # Paso 3: Mostrar preview
            progress.update_progress(0.8, "Generando vista previa...", "Preparando interfaz")
            self.update()
            
            self.mostrar_preview_cambios()
            
            # Paso 4: Finalizar
            progress.update_progress(1.0, "Completado", "Listo para aplicar cambios")
            self.update()
            
            # Cerrar diálogo después de un momento
            self.after(500, progress.destroy)
            
            # Actualizar estado
            total = len(self.cambios_propuestos)
            nuevos = sum(1 for c in self.cambios_propuestos if c['tipo'] == 'nuevo')
            actualizados = sum(1 for c in self.cambios_propuestos if c['tipo'] == 'actualizar')
            sin_precio = sum(1 for c in self.cambios_propuestos if not c.get('tiene_precio', True))
            
            status_text = f"✅ {total} cambios: {nuevos} nuevos, {actualizados} actualizaciones"
            if sin_precio > 0:
                status_text += f" | ⚠️ {sin_precio} sin precio"
            
            self.status_label.configure(text=status_text, text_color="#2ECC71")
            self.btn_aplicar.configure(state="normal")
            
            # ✅ Registrar en logger
            if self.logger:
                pass  # Logger deshabilitado temporalmente
                # self.logger.info(
                # 'Importación',
                # 'Procesar PDF',
                # f"Productos extraídos: {total} | Nuevos: {nuevos} | Actualizados: {actualizados} | Sin precio: {sin_precio}"
                # )
                # TODO: Revisar y corregir esta llamada a logger.info()
                # El logger nuevo solo acepta un mensaje como string
                # logger.info("mensaje único")
            
        except Exception as e:
            progress.destroy()
            messagebox.showerror("Error", f"Error procesando PDF:\n{str(e)}")
            self.status_label.configure(text="❌ Error al procesar", text_color="#E74C3C")
            print(f"Error completo: {e}")
            traceback.print_exc()
            
            # ✅ Registrar error
            if self.logger:
                self.logger.registrar_error('Importación', e, f"Archivo: {self.pdf_path}")
    
    def extraer_productos_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extrae productos del PDF de cotización
        Retorna lista de diccionarios con: nombre, unidad, precio, tiene_precio
        """
        productos = []
        self.productos_sin_precio = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                texto = page.get_text()
                
                patron = r"([A-ZAÉÍÓÚÜ'][A-ZAÉÍÓÚÜ'\s/]+?)\s+(KILO|KG|PIEZA|PZA|MANOJO|MJO|BURBUJA|GRANEL|LT|CUBETA|PQ|PAQ|MJ|HG)\s+\$?\s*([\d,]+\.?\d*|-)"
                
                matches = re.finditer(patron, texto, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    nombre = match.group(1).strip()
                    unidad = match.group(2).strip()
                    precio_str = match.group(3).strip()
                    
                    nombre = self.limpiar_nombre_producto(nombre)
                    unidad = self.normalizar_unidad(unidad)
                    
                    if precio_str == '-' or precio_str == '':
                        precio = Decimal('0.00')
                        tiene_precio = False
                    else:
                        try:
                            precio_str = precio_str.replace(',', '')
                            precio = Decimal(precio_str)
                            
                            if precio < 0:
                                print(f"⚠️ Precio negativo ignorado: {nombre}")
                                continue
                            
                            tiene_precio = precio > 0
                        except:
                            print(f"❌ Error procesando precio de '{nombre}'")
                            continue
                    
                    producto = {
                        'nombre': nombre,
                        'unidad': unidad,
                        'precio': precio,
                        'tiene_precio': tiene_precio
                    }
                    
                    productos.append(producto)
                    
                    if not tiene_precio:
                        self.productos_sin_precio.append(producto)
            
            doc.close()
            
            productos_unicos = self.eliminar_duplicados_inteligente(productos)
            
            return productos_unicos
            
        except Exception as e:
            print(f"Error extrayendo productos: {e}")
            raise
    def eliminar_duplicados_inteligente(self, productos: List[Dict]) -> List[Dict]:
        """Elimina duplicados respetando case-insensitive y priorizando productos con precio"""
        productos_map = {}
        
        for p in productos:
            key = f"{p['nombre'].lower()}_{p['unidad'].lower()}"
            
            if key not in productos_map:
                productos_map[key] = p
            else:
                # Si el producto actual tiene precio y el guardado no, reemplazar
                if p.get('tiene_precio', False) and not productos_map[key].get('tiene_precio', False):
                    productos_map[key] = p
                # Si ambos tienen precio, mantener el primero (o puedes decidir otra lógica)
                # Si ninguno tiene precio, mantener el primero
        
        return list(productos_map.values())
                     
    def normalizar_unidad(self, unidad: str) -> str:
        """Normaliza a formas CORTAS estándar"""
        unidad = unidad.upper().strip()
        
        normalizaciones = {
            'KILO': 'kg', 'KG': 'kg', 'KILOS': 'kg', 'K': 'kg',
            'PIEZA': 'pz', 'PZ': 'pz', 'PZA': 'pz', 'PIEZAS': 'pz', 'UNIDAD': 'pz',
            'LIBRA': 'lb', 'LB': 'lb', 'LIBRAS': 'lb',
            'MANOJO': 'mjo', 'MJO': 'mjo', 'MJ': 'mjo', 'MANOJOS': 'mjo',
            'PAQUETE': 'paq', 'PAQ': 'paq', 'PQ': 'paq', 'PAQUETES': 'paq',
            'LITRO': 'lt', 'LT': 'lt', 'LITROS': 'lt', 'L': 'lt',
            'HECTOGRAMO': 'hg', 'HG': 'hg', 'HECTOGRAMOS': 'hg',
            'GRAMO': 'g', 'G': 'g', 'GRAMOS': 'g', 'GR': 'g',
            'BURBUJA': 'burbuja', 'GRANEL': 'granel', 'CUBETA': 'cubeta',
            'CAJA': 'caja', 'COSTAL': 'costal', 'CHAROLA': 'charola',
            'BOLSA': 'bolsa',
        }
        
        return normalizaciones.get(unidad, unidad.lower())
        
    def limpiar_nombre_producto(self, nombre: str) -> str:
        """Limpia y normaliza el nombre del producto"""
        nombre = nombre.title()
        nombre = re.sub(r'\s+', ' ', nombre)
        nombre = nombre.strip('.,;:')
        return nombre
    
    def generar_cambios_propuestos(self) -> List[Dict]:
        """Compara productos extraídos con BD y genera lista de cambios"""
        cambios = []
        
        try:
            cursor = self.db.cursor()
            
            for prod_pdf in self.productos_extraidos:
                producto_bd = self.buscar_producto_similar(
                    prod_pdf['nombre'],
                    prod_pdf['unidad']
                )
                
                if producto_bd:
                    if self.actualizar_existentes.get():
                        cambios.append({
                            'tipo': 'actualizar',
                            'id_producto': producto_bd['id'],
                            'nombre': producto_bd['nombre'],
                            'unidad': producto_bd['unidad'],
                            'precio_nuevo': prod_pdf['precio'],
                            'tiene_precio': prod_pdf['tiene_precio'],
                            'stock': producto_bd['stock']
                        })
                else:
                    if self.agregar_nuevos.get():
                        cambios.append({
                            'tipo': 'nuevo',
                            'nombre': prod_pdf['nombre'],
                            'unidad': prod_pdf['unidad'],
                            'precio_nuevo': prod_pdf['precio'],
                            'tiene_precio': prod_pdf['tiene_precio'],
                            'stock': Decimal('0')
                        })
            
            return cambios
            
        except Exception as e:
            print(f"Error generando cambios: {e}")
            traceback.print_exc()
            raise
        
    def obtener_variantes_unidad(self, unidad: str) -> list:
        """Retorna TODAS las variantes posibles de una unidad"""
        variantes_map = {
            'kg': ['kg', 'kilo', 'kilos', 'k'],
            'pz': ['pz', 'pza', 'pieza', 'piezas', 'unidad'],
            'lb': ['lb', 'libra', 'libras'],
            'mjo': ['mjo', 'mj', 'manojo', 'manojos'],
            'paq': ['paq', 'pq', 'paquete', 'paquetes'],
            'lt': ['lt', 'l', 'litro', 'litros'],
            'hg': ['hg', 'hectogramo', 'hectogramos'],
            'g': ['g', 'gr', 'gramo', 'gramos'],
            'burbuja': ['burbuja'], 'granel': ['granel'],
            'cubeta': ['cubeta', 'cubetas'], 'caja': ['caja', 'cajas'],
            'costal': ['costal', 'costales'], 'charola': ['charola', 'charolas'],
            'bolsa': ['bolsa', 'bolsas'],
        }
        return variantes_map.get(unidad.lower(), [unidad.lower()])
    
    def buscar_producto_similar(self, nombre: str, unidad: str) -> Optional[Dict]:
        """Búsqueda con soporte para variantes - COMPATIBLE CON DICT Y TUPLE"""
        try:
            cursor = self.db.cursor()
            unidad_normalizada = self.normalizar_unidad(unidad)
            
            # BÚSQUEDA EXACTA
            cursor.execute("""
                SELECT id_producto, nombre_producto, unidad_producto, stock 
                FROM producto 
                WHERE LOWER(TRIM(nombre_producto)) = LOWER(TRIM(%s)) 
                AND LOWER(TRIM(unidad_producto)) = %s
            """, (nombre, unidad_normalizada))
            
            result = cursor.fetchone()
            if result:
                # ✅ MANEJAR DICT O TUPLE
                if isinstance(result, dict):
                    return {
                        'id': result['id_producto'],
                        'nombre': result['nombre_producto'],
                        'unidad': result['unidad_producto'],
                        'stock': Decimal(str(result['stock']))
                    }
                else:
                    return {
                        'id': result[0],
                        'nombre': result[1],
                        'unidad': result[2],
                        'stock': Decimal(str(result[3]))
                    }
            
            # FUZZY MATCHING
            cursor.execute("""
                SELECT id_producto, nombre_producto, unidad_producto, stock 
                FROM producto 
                WHERE LOWER(TRIM(unidad_producto)) = %s
            """, (unidad_normalizada,))
            
            productos_bd = cursor.fetchall()
            mejor_match = None
            mejor_ratio = 0.85
            
            for prod in productos_bd:
                # ✅ MANEJAR DICT O TUPLE
                nombre_bd = prod['nombre_producto'] if isinstance(prod, dict) else prod[1]
                
                ratio = difflib.SequenceMatcher(
                    None,
                    nombre.lower().strip(),
                    nombre_bd.lower().strip()
                ).ratio()
                
                if ratio > mejor_ratio:
                    mejor_ratio = ratio
                    if isinstance(prod, dict):
                        mejor_match = {
                            'id': prod['id_producto'],
                            'nombre': prod['nombre_producto'],
                            'unidad': prod['unidad_producto'],
                            'stock': Decimal(str(prod['stock']))
                        }
                    else:
                        mejor_match = {
                            'id': prod[0],
                            'nombre': prod[1],
                            'unidad': prod[2],
                            'stock': Decimal(str(prod[3]))
                        }
            
            return mejor_match
            
        except Exception as e:
            print(f"❌ Error en búsqueda de '{nombre}' ({unidad}): {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def mostrar_mensaje_inicial(self):
        """Muestra mensaje inicial en el área de preview"""
        for widget in self.tabla_cambios.winfo_children():
            widget.destroy()
        
        mensaje = ctk.CTkLabel(
            self.tabla_cambios,
            text="👆 Selecciona un archivo PDF para comenzar",
            font=("Roboto", 14),
            text_color="gray"
        )
        mensaje.pack(expand=True)
    
    def mostrar_preview_cambios(self):
        """Muestra tabla con preview de cambios propuestos"""
        for widget in self.tabla_cambios.winfo_children():
            widget.destroy()
        
        if not self.cambios_propuestos:
            ctk.CTkLabel(
                self.tabla_cambios,
                text="No se encontraron cambios para aplicar",
                font=("Roboto", 13),
                text_color="gray"
            ).pack(pady=20)
            return
        
        # Header de tabla
        header = ctk.CTkFrame(self.tabla_cambios, fg_color=("#e0e0e0", "#2b2b2b"))
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        headers = ["Tipo", "Producto", "Unidad", "Precio", "Acción"]
        for i, texto in enumerate(headers):
            ctk.CTkLabel(
                header,
                text=texto,
                font=("Roboto", 12, "bold")
            ).grid(row=0, column=i, padx=10, pady=8)
        
        # Filas de cambios
        for idx, cambio in enumerate(self.cambios_propuestos):
            fila = ctk.CTkFrame(
                self.tabla_cambios,
                fg_color=("#f8f9fa" if idx % 2 == 0 else "transparent")
            )
            fila.grid(row=idx+1, column=0, sticky="ew", pady=2)
            fila.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            # Tipo
            tipo_texto = "➕ NUEVO" if cambio['tipo'] == 'nuevo' else "🔄 ACTUALIZAR"
            tipo_color = "#2ECC71" if cambio['tipo'] == 'nuevo' else "#3498DB"
            
            ctk.CTkLabel(
                fila,
                text=tipo_texto,
                font=("Roboto", 11, "bold"),
                text_color=tipo_color
            ).grid(row=0, column=0, padx=10, pady=8)
            
            # Nombre
            ctk.CTkLabel(
                fila,
                text=cambio['nombre'],
                font=("Roboto", 11)
            ).grid(row=0, column=1, padx=10, pady=8, sticky="w")
            
            # Unidad
            ctk.CTkLabel(
                fila,
                text=cambio['unidad'],
                font=("Roboto", 11)
            ).grid(row=0, column=2, padx=10, pady=8)
            
            # Precio
            if cambio.get('tiene_precio', True):
                precio_texto = f"${cambio['precio_nuevo']:,.2f}"
                color = "#2ECC71"
            else:
                precio_texto = "⚠️ SIN PRECIO"
                color = "#E74C3C"
            
            ctk.CTkLabel(
                fila,
                text=precio_texto,
                font=("Roboto", 11, "bold"),
                text_color=color
            ).grid(row=0, column=3, padx=10, pady=8)
            
            # ✅ NUEVO: Botón Ver Detalle
            ctk.CTkButton(
                fila,
                text="🔍 Ver Detalle",
                command=lambda c=cambio: self.crear_preview_expandido(c),
                width=100,
                height=30,
                fg_color="#3498DB",
                hover_color="#2980B9",
                font=("Roboto", 10)
            ).grid(row=0, column=4, padx=10, pady=8)
    
    def crear_preview_expandido(self, cambio):
        """
        ✅ NUEVA FUNCIÓN: Muestra un diálogo con detalle completo de cómo quedarán los precios
        """
        try:
            # Crear ventana de detalle
            detalle = ctk.CTkToplevel(self)
            detalle.title(f"Detalle: {cambio['nombre']}")
            detalle.geometry("600x500")
            detalle.transient(self)
            detalle.grab_set()
            
            # Header
            header = ctk.CTkFrame(detalle, fg_color=("#2D9B6C", "#1a5d42"))
            header.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(
                header,
                text=f"📊 {cambio['nombre']}",
                font=("Roboto", 18, "bold"),
                text_color="white"
            ).pack(pady=15)
            
            # Info del producto
            info_frame = ctk.CTkFrame(detalle)
            info_frame.pack(fill="x", padx=20, pady=(0, 10))
            
            ctk.CTkLabel(
                info_frame,
                text=f"Unidad: {cambio['unidad']}",
                font=("Roboto", 12)
            ).pack(anchor="w", padx=15, pady=5)
            
            precio_str = f"${cambio['precio_nuevo']:.2f}" if cambio.get('tiene_precio', True) else "SIN PRECIO"
            ctk.CTkLabel(
                info_frame,
                text=f"Precio Base: {precio_str}",
                font=("Roboto", 12, "bold")
            ).pack(anchor="w", padx=15, pady=5)
            
            # Tabla de grupos
            ctk.CTkLabel(
                detalle,
                text="Precios por Grupo:",
                font=("Roboto", 14, "bold")
            ).pack(anchor="w", padx=20, pady=(10, 5))
            
            # Scroll frame para grupos
            scroll_frame = ctk.CTkScrollableFrame(detalle)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            
            # Obtener todos los grupos
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT g.id_grupo, g.clave_grupo, tc.nombre_tipo, tc.descuento
                FROM grupo g
                LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                ORDER BY g.clave_grupo
            """)
            todos_los_grupos = cursor.fetchall()
            
            precio_base = cambio['precio_nuevo']
            
            for grupo in todos_los_grupos:
                if isinstance(grupo, dict):
                    clave = grupo['clave_grupo']
                    nombre_tipo = grupo.get('nombre_tipo', 'Sin tipo')
                    descuento = grupo.get('descuento', 0) or 0
                else:
                    clave = grupo[1]
                    nombre_tipo = grupo[2] if grupo[2] else 'Sin tipo'
                    descuento = grupo[3] if grupo[3] else 0
                
                # Calcular precio final
                precio_final = precio_base * (Decimal('1') - Decimal(str(descuento)) / Decimal('100'))
                
                # Frame para cada grupo
                grupo_frame = ctk.CTkFrame(scroll_frame, fg_color=("gray90", "gray20"))
                grupo_frame.pack(fill="x", pady=3, padx=5)
                
                content = ctk.CTkFrame(grupo_frame, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=10)
                
                ctk.CTkLabel(
                    content,
                    text=f"{clave}",
                    font=("Roboto", 12, "bold")
                ).pack(side="left")
                
                ctk.CTkLabel(
                    content,
                    text=f"({nombre_tipo} - {descuento}%)",
                    font=("Roboto", 10),
                    text_color="gray"
                ).pack(side="left", padx=(10, 0))
                
                ctk.CTkLabel(
                    content,
                    text=f"${precio_final:.2f}",
                    font=("Roboto", 12, "bold"),
                    text_color="#2ECC71"
                ).pack(side="right")
            
            # Botón cerrar
            ctk.CTkButton(
                detalle,
                text="Cerrar",
                command=detalle.destroy,
                width=120,
                height=35
            ).pack(pady=15)
            
        except Exception as e:
            print(f"Error mostrando preview expandido: {e}")
            traceback.print_exc()
    
    def generar_reporte_importacion(self, cambios_exitosos, total_grupos, productos_sin_precio):
        """
        ✅ NUEVA FUNCIÓN: Genera un archivo de reporte detallado de la importación
        
        Returns:
            str: Ruta del archivo generado
        """
        try:
            # Crear carpeta de reportes si no existe
            reportes_dir = Path("reportes_importacion")
            reportes_dir.mkdir(exist_ok=True)
            
            # Nombre del archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = reportes_dir / f"importacion_{timestamp}.txt"
            
            # Generar contenido del reporte
            contenido = []
            contenido.append("=" * 70)
            contenido.append("REPORTE DE IMPORTACIÓN DE COTIZACIÓN")
            contenido.append("=" * 70)
            contenido.append(f"\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            contenido.append(f"Usuario: {self.user_info.get('nombre_completo', 'N/A')}")
            contenido.append(f"Archivo: {Path(self.pdf_path).name if hasattr(self, 'pdf_path') else 'N/A'}")
            contenido.append("\n" + "=" * 70)
            
            # Resumen
            contenido.append("\nRESUMEN DE CAMBIOS")
            contenido.append("-" * 70)
            contenido.append(f"Total de productos procesados: {cambios_exitosos}")
            
            nuevos = sum(1 for c in self.cambios_propuestos if c['tipo'] == 'nuevo')
            actualizados = sum(1 for c in self.cambios_propuestos if c['tipo'] == 'actualizar')
            
            contenido.append(f"  • Productos nuevos: {nuevos}")
            contenido.append(f"  • Productos actualizados: {actualizados}")
            contenido.append(f"  • Grupos afectados: {total_grupos}")
            if productos_sin_precio:
                contenido.append(f"  • Productos sin precio: {len(productos_sin_precio)}")
            
            # Detalle de productos nuevos
            if nuevos > 0:
                contenido.append("\n" + "=" * 70)
                contenido.append("PRODUCTOS NUEVOS")
                contenido.append("-" * 70)
                for c in self.cambios_propuestos:
                    if c['tipo'] == 'nuevo':
                        precio_str = f"${c['precio_nuevo']:.2f}" if c.get('tiene_precio', True) else "SIN PRECIO"
                        contenido.append(f"  • {c['nombre']} ({c['unidad']}) - {precio_str}")
            
            # Detalle de productos actualizados
            if actualizados > 0:
                contenido.append("\n" + "=" * 70)
                contenido.append("PRODUCTOS ACTUALIZADOS")
                contenido.append("-" * 70)
                for c in self.cambios_propuestos:
                    if c['tipo'] == 'actualizar':
                        precio_str = f"${c['precio_nuevo']:.2f}" if c.get('tiene_precio', True) else "SIN PRECIO"
                        contenido.append(f"  • {c['nombre']} ({c['unidad']}) - {precio_str}")
            
            # Productos sin precio
            if productos_sin_precio:
                contenido.append("\n" + "=" * 70)
                contenido.append("⚠️ PRODUCTOS QUE REQUIEREN ASIGNACIÓN DE PRECIO")
                contenido.append("-" * 70)
                for p in productos_sin_precio:
                    contenido.append(f"  • {p['nombre']} ({p['unidad']})")
            
            # Grupos afectados
            contenido.append("\n" + "=" * 70)
            contenido.append("GRUPOS AFECTADOS")
            contenido.append("-" * 70)
            
            try:
                cursor = self.db.cursor()
                cursor.execute("""
                    SELECT g.clave_grupo, tc.nombre_tipo, tc.descuento
                    FROM grupo g
                    LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                    ORDER BY g.clave_grupo
                """)
                grupos = cursor.fetchall()
                
                for grupo in grupos:
                    if isinstance(grupo, dict):
                        contenido.append(f"  • {grupo['clave_grupo']} - {grupo['nombre_tipo']} (Descuento: {grupo['descuento']}%)")
                    else:
                        contenido.append(f"  • {grupo[0]} - {grupo[1]} (Descuento: {grupo[2]}%)")
            except:
                contenido.append("  (No se pudo obtener información de grupos)")
            
            contenido.append("\n" + "=" * 70)
            contenido.append("FIN DEL REPORTE")
            contenido.append("=" * 70)
            
            # Escribir archivo
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(contenido))
            
            return str(filename)
            
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return None
    
    def aplicar_cambios(self):
        """
        ✅ VERSIÓN MEJORADA: Aplica precios a TODOS los grupos respetando descuentos
        Incluye logger, eventbus y generación de reporte
        """
        if not self.cambios_propuestos:
            messagebox.showinfo("Info", "No hay cambios para aplicar")
            return
        
        # ✅ VERIFICAR si hay productos sin precio
        productos_sin_precio = [c for c in self.cambios_propuestos if not c.get('tiene_precio', True)]
        
        if productos_sin_precio:
            respuesta = messagebox.askyesnocancel(
                "Productos sin precio detectados",
                f"⚠️ Se encontraron {len(productos_sin_precio)} productos sin precio.\n\n"
                f"¿Deseas continuar?\n\n"
                f"• SÍ: Aplicar cambios y abrir Price Editor para productos sin precio\n"
                f"• NO: Cancelar todo\n"
                f"• CANCELAR: Volver",
                parent=self
            )
            
            if respuesta is None:
                return
            elif not respuesta:
                return
            abrir_price_editor = True
        else:
            abrir_price_editor = False
        
        # Confirmar aplicación
        total = len(self.cambios_propuestos)
        nuevos = sum(1 for c in self.cambios_propuestos if c['tipo'] == 'nuevo')
        actualizados = sum(1 for c in self.cambios_propuestos if c['tipo'] == 'actualizar')
        sin_precio = len(productos_sin_precio)
        
        mensaje = f"📊 RESUMEN DE CAMBIOS\n\n"
        mensaje += f"• {nuevos} productos nuevos\n"
        mensaje += f"• {actualizados} productos actualizados\n"
        if sin_precio > 0:
            mensaje += f"• {sin_precio} productos sin precio\n"
        mensaje += f"\n⚠️ El stock NO será modificado\n\n"
        mensaje += f"✅ Los precios se aplicarán a TODOS los grupos\n"
        mensaje += f"   respetando el descuento de cada uno"
        
        if not messagebox.askyesno("Confirmar cambios", mensaje, parent=self):
            return
        
        try:
            cursor = self.db.cursor()
            
            # ✅ CARGAR TODOS LOS GRUPOS CON SUS DESCUENTOS
            cursor.execute("""
                SELECT g.id_grupo, g.clave_grupo, tc.descuento
                FROM grupo g
                LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
                ORDER BY g.clave_grupo
            """)
            todos_los_grupos = cursor.fetchall()
            
            cambios_exitosos = 0
            productos_creados = []
            
            for cambio in self.cambios_propuestos:
                precio_base = cambio['precio_nuevo']
                
                if cambio['tipo'] == 'nuevo':
                    # ✅ Insertar nuevo producto
                    cursor.execute("""
                        INSERT INTO producto (nombre_producto, unidad_producto, stock, es_especial)
                        VALUES (%s, %s, 0, 0)
                    """, (cambio['nombre'], cambio['unidad']))
                    
                    nuevo_id = cursor.lastrowid
                    productos_creados.append(nuevo_id)
                    
                    # ✅ APLICAR PRECIO A TODOS LOS GRUPOS
                    for grupo in todos_los_grupos:
                        if isinstance(grupo, dict):
                            id_grupo = grupo['id_grupo']
                            descuento = grupo.get('descuento', 0) or 0
                        else:
                            id_grupo = grupo[0]
                            descuento = grupo[2] if grupo[2] else 0
                        
                        precio_con_descuento = precio_base * (Decimal('1') - Decimal(str(descuento)) / Decimal('100'))
                        
                        cursor.execute("""
                            INSERT INTO precio_por_grupo (id_producto, id_grupo, precio_base)
                            VALUES (%s, %s, %s)
                        """, (nuevo_id, id_grupo, precio_con_descuento))
                    
                    cambios_exitosos += 1
                    
                elif cambio['tipo'] == 'actualizar':
                    # ✅ ACTUALIZAR PRECIO EN TODOS LOS GRUPOS
                    for grupo in todos_los_grupos:
                        if isinstance(grupo, dict):
                            id_grupo = grupo['id_grupo']
                            descuento = grupo.get('descuento', 0) or 0
                        else:
                            id_grupo = grupo[0]
                            descuento = grupo[2] if grupo[2] else 0
                        
                        precio_con_descuento = precio_base * (Decimal('1') - Decimal(str(descuento)) / Decimal('100'))
                        
                        # ✅ USAR INSERT ... ON DUPLICATE KEY UPDATE
                        cursor.execute("""
                            INSERT INTO precio_por_grupo (id_producto, id_grupo, precio_base)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE precio_base = %s
                        """, (cambio['id_producto'], id_grupo, precio_con_descuento, precio_con_descuento))
                    
                    cambios_exitosos += 1
            
            # ✅ Registrar en log
            detalle_log = f"Importación masiva: {cambios_exitosos} cambios aplicados a {len(todos_los_grupos)} grupos"
            if productos_sin_precio:
                detalle_log += f" | {len(productos_sin_precio)} productos requieren precio"
            
            try:
                cursor.execute("""
                    INSERT INTO logs_sistema (usuario, modulo, accion, detalles)
                    VALUES (%s, 'Importación', 'Importar cotización masiva', %s)
                """, (
                    self.user_info.get('username'),
                    detalle_log
                ))
            except:
                pass
            
            # ✅ Registrar con logger
            if self.logger:
                pass  # Logger deshabilitado temporalmente
                # self.logger.info(
                # 'Importación',
                # 'Aplicar cambios',
                # detalle_log,
                # 'SUCCESS'
                # )
                # TODO: Revisar y corregir esta llamada a logger.info()
                # El logger nuevo solo acepta un mensaje como string
                # logger.info("mensaje único")
            
            self.db.commit()
            
            # ✅ MENSAJE DE ÉXITO
            mensaje_exito = f"✅ IMPORTACIÓN EXITOSA\n\n"
            mensaje_exito += f"• {cambios_exitosos} productos procesados\n"
            mensaje_exito += f"• Precios aplicados a {len(todos_los_grupos)} grupos\n"
            
            if productos_sin_precio:
                mensaje_exito += f"\n⚠️ {len(productos_sin_precio)} productos sin precio\n"
                mensaje_exito += f"Se abrirá Price Editor para completarlos"
            
            # ✅ Generar reporte
            try:
                archivo_reporte = self.generar_reporte_importacion(
                    cambios_exitosos,
                    len(todos_los_grupos),
                    productos_sin_precio
                )
                
                if archivo_reporte:
                    mensaje_exito += f"\n\n📄 Reporte guardado en:\n{archivo_reporte}"
            except Exception as e:
                print(f"Error generando reporte: {e}")
            
            messagebox.showinfo("Éxito", mensaje_exito, parent=self)
            
            # ✅ PUBLICAR EVENTO
            if USAR_EVENTBUS:
                try:
                    publish(Events.IMPORTACION_COMPLETADA, {
                        'productos_nuevos': nuevos,
                        'productos_actualizados': actualizados,
                        'grupos_afectados': len(todos_los_grupos),
                        'productos_sin_precio': len(productos_sin_precio),
                        'usuario': self.user_info.get('username')
                    })
                except Exception as e:
                    print(f"Error publicando evento: {e}")
            
            # ✅ ABRIR PRICE EDITOR SI HAY PRODUCTOS SIN PRECIO
            if abrir_price_editor and productos_sin_precio:
                self.after(500, lambda: self.abrir_price_editor_filtrado(productos_creados))
            
            self.destroy()
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Error aplicando cambios:\n{str(e)}", parent=self)
            print(f"Error completo: {e}")
            traceback.print_exc()
            
            # ✅ Registrar error
            if self.logger:
                self.logger.registrar_error('Importación', e, 'Error al aplicar cambios')
    
    def abrir_price_editor_filtrado(self, productos_ids: List[int]):
        """
        ✅ NUEVA FUNCIÓN: Abre Price Editor mostrando solo productos sin precio
        """
        try:
            from price_editor import PriceEditorApp
            
            editor_window = ctk.CTkToplevel()
            editor_window.title("Price Editor - Productos Sin Precio")
            editor_window.geometry("1400x800")
            
            editor_app = PriceEditorApp(
                editor_window, 
                user_data=self.user_info,
                filtro_productos=productos_ids
            )
            
            messagebox.showinfo(
                "Productos sin precio",
                "Se abrió Price Editor con los productos que requieren precio.\n\n"
                "Por favor, asigna precios a estos productos y guarda los cambios.",
                parent=editor_window
            )
            
        except ImportError as e:
            print(f"Error importando Price Editor: {e}")
            messagebox.showwarning(
                "Aviso",
                "No se pudo abrir Price Editor automáticamente.\n"
                "Por favor, ábrelo manualmente desde el menú principal."
            )
        except Exception as e:
            print(f"Error abriendo Price Editor: {e}")
            traceback.print_exc()
            messagebox.showwarning(
                "Aviso",
                f"Ocurrió un error al abrir Price Editor:\n{str(e)}\n\n"
                "Por favor, ábrelo manualmente desde el menú principal."
            )


# ========== FUNCIÓN PARA AGREGAR AL DASHBOARD ==========
def abrir_importador_cotizaciones(parent, db, user_info):
    """
    Función para abrir el módulo desde el dashboard
    
    Uso en main_application.py:
    
    {
        'name': 'Importar Cotización',
        'icon': '📄',
        'color': '#9B59B6',
        'function': lambda: abrir_importador_cotizaciones(self, self.db, self.user_info),
        'admin_only': True
    }
    """
    importador = CotizacionImporter(parent, db, user_info)
    importador.focus()


if __name__ == "__main__":
    print("Módulo de Importación de Cotizaciones - BodegaDisfruleg")
    print("Versión Mejorada - Octubre 2025")
    print("Este archivo debe importarse desde main_application.py")