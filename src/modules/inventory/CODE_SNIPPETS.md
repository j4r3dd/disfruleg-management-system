# 📋 Snippets de Código - Sistema Responsive

## Ejemplos listos para copiar y pegar

---

## 1️⃣ Ventana Responsive Básica

### Código Mínimo
```python
from utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk

class MiVentana(ResponsiveMixin, ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Mi Ventana")
        self.make_responsive('medium')
```

---

## 2️⃣ Diálogo Modal Responsive

### Diálogo de Confirmación
```python
from utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk
from tkinter import messagebox

class ConfirmDialog(ResponsiveMixin, ctk.CTkToplevel):
    """Diálogo de confirmación responsive"""
    
    def __init__(self, parent, title="Confirmar", message="¿Estás seguro?"):
        super().__init__(parent)
        self.title(title)
        self.make_responsive('dialog')
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Resultado
        self.result = False
        
        # UI
        self._build_ui(message)
    
    def _build_ui(self, message):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Mensaje
        ctk.CTkLabel(
            frame,
            text=message,
            font=("Arial", 14),
            wraplength=400
        ).pack(pady=20)
        
        # Botones
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self._on_cancel,
            fg_color="gray",
            width=150
        ).pack(side="left", padx=5, expand=True)
        
        ctk.CTkButton(
            btn_frame,
            text="Confirmar",
            command=self._on_confirm,
            width=150
        ).pack(side="right", padx=5, expand=True)
    
    def _on_confirm(self):
        self.result = True
        self.destroy()
    
    def _on_cancel(self):
        self.result = False
        self.destroy()
    
    @staticmethod
    def show(parent, title="Confirmar", message="¿Estás seguro?"):
        """Mostrar diálogo y retornar resultado"""
        dialog = ConfirmDialog(parent, title, message)
        dialog.wait_window()
        return dialog.result


# USO:
if ConfirmDialog.show(root, "Eliminar", "¿Eliminar este elemento?"):
    print("Usuario confirmó")
else:
    print("Usuario canceló")
```

---

## 3️⃣ Ventana de Formulario

### Formulario Responsive
```python
from utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk

class FormWindow(ResponsiveMixin, ctk.CTkToplevel):
    """Ventana de formulario responsive"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Formulario de Datos")
        self.make_responsive('medium')
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Variables
        self.nombre_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.telefono_var = ctk.StringVar()
        
        # UI
        self._build_ui()
    
    def _build_ui(self):
        # Contenedor principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="📝 Ingrese los Datos",
            font=("Arial", 24, "bold")
        ).pack(pady=(0, 30))
        
        # Campos
        self._create_field(main_frame, "Nombre:", self.nombre_var)
        self._create_field(main_frame, "Email:", self.email_var)
        self._create_field(main_frame, "Teléfono:", self.telefono_var)
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=30)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="gray",
            height=40
        ).pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self._on_save,
            height=40
        ).pack(side="right", expand=True, padx=5)
    
    def _create_field(self, parent, label, variable):
        """Crear campo de formulario"""
        ctk.CTkLabel(
            parent,
            text=label,
            font=("Arial", 12, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        ctk.CTkEntry(
            parent,
            textvariable=variable,
            height=40,
            font=("Arial", 12)
        ).pack(fill="x", pady=(0, 15))
    
    def _on_save(self):
        """Guardar datos"""
        nombre = self.nombre_var.get().strip()
        email = self.email_var.get().strip()
        telefono = self.telefono_var.get().strip()
        
        if not nombre or not email:
            from tkinter import messagebox
            messagebox.showerror("Error", "Nombre y email son obligatorios", parent=self)
            return
        
        print(f"Guardando: {nombre}, {email}, {telefono}")
        self.destroy()


# USO:
form = FormWindow(root)
```

---

## 4️⃣ Ventana de Búsqueda Avanzada

### Panel de Búsqueda Grande
```python
from utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk

class SearchWindow(ResponsiveMixin, ctk.CTkToplevel):
    """Ventana de búsqueda avanzada responsive"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🔍 Búsqueda Avanzada")
        self.make_responsive('large')  # Ventana grande
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Variables de búsqueda
        self.search_text = ctk.StringVar()
        self.date_from = ctk.StringVar()
        self.date_to = ctk.StringVar()
        
        # UI
        self._build_ui()
    
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="#1a1a1a", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="🔍 Búsqueda Avanzada",
            font=("Arial", 20, "bold")
        ).pack(side="left", padx=30, pady=20)
        
        ctk.CTkButton(
            header,
            text="✕ Cerrar",
            command=self.destroy,
            width=100,
            height=35
        ).pack(side="right", padx=30)
        
        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel: Filters
        left_panel = ctk.CTkFrame(content, width=350)
        left_panel.pack(side="left", fill="both", padx=(0, 10))
        
        self._create_filters(left_panel)
        
        # Right panel: Results
        right_panel = ctk.CTkFrame(content)
        right_panel.pack(side="right", fill="both", expand=True)
        
        self._create_results(right_panel)
    
    def _create_filters(self, parent):
        """Panel de filtros"""
        ctk.CTkLabel(
            parent,
            text="Filtros",
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        # Búsqueda de texto
        ctk.CTkLabel(parent, text="Buscar:", anchor="w").pack(fill="x", padx=20)
        ctk.CTkEntry(
            parent,
            textvariable=self.search_text,
            placeholder_text="Escribe aquí..."
        ).pack(fill="x", padx=20, pady=5)
        
        # Fechas
        ctk.CTkLabel(parent, text="Fecha desde:", anchor="w").pack(fill="x", padx=20, pady=(20, 0))
        ctk.CTkEntry(parent, textvariable=self.date_from).pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(parent, text="Fecha hasta:", anchor="w").pack(fill="x", padx=20, pady=(10, 0))
        ctk.CTkEntry(parent, textvariable=self.date_to).pack(fill="x", padx=20, pady=5)
        
        # Botón buscar
        ctk.CTkButton(
            parent,
            text="🔍 Buscar",
            command=self._on_search,
            height=40
        ).pack(fill="x", padx=20, pady=30)
    
    def _create_results(self, parent):
        """Panel de resultados"""
        ctk.CTkLabel(
            parent,
            text="Resultados",
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        # ScrollableFrame para resultados
        results_scroll = ctk.CTkScrollableFrame(parent)
        results_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Ejemplo de resultados
        for i in range(10):
            result_card = ctk.CTkFrame(results_scroll)
            result_card.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                result_card,
                text=f"Resultado #{i+1}",
                font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=15, pady=10)
    
    def _on_search(self):
        """Ejecutar búsqueda"""
        search = self.search_text.get()
        date_from = self.date_from.get()
        date_to = self.date_to.get()
        
        print(f"Buscando: {search}, desde {date_from} hasta {date_to}")


# USO:
search = SearchWindow(root)
```

---

## 5️⃣ Ventana de Configuración

### Configuración Pequeña
```python
from utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk

class SettingsWindow(ResponsiveMixin, ctk.CTkToplevel):
    """Ventana de configuración responsive"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("⚙️ Configuración")
        self.make_responsive('small')  # Ventana pequeña
        
        # Variables
        self.theme_var = ctk.StringVar(value="Oscuro")
        self.notifications_var = ctk.BooleanVar(value=True)
        self.auto_save_var = ctk.BooleanVar(value=True)
        
        # UI
        self._build_ui()
    
    def _build_ui(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Título
        ctk.CTkLabel(
            frame,
            text="⚙️ Configuración",
            font=("Arial", 20, "bold")
        ).pack(pady=(0, 30))
        
        # Tema
        ctk.CTkLabel(frame, text="Tema:", anchor="w").pack(fill="x")
        ctk.CTkOptionMenu(
            frame,
            variable=self.theme_var,
            values=["Claro", "Oscuro", "Sistema"]
        ).pack(fill="x", pady=(5, 20))
        
        # Notificaciones
        ctk.CTkCheckBox(
            frame,
            text="Activar notificaciones",
            variable=self.notifications_var
        ).pack(anchor="w", pady=10)
        
        # Auto-guardado
        ctk.CTkCheckBox(
            frame,
            text="Auto-guardar cambios",
            variable=self.auto_save_var
        ).pack(anchor="w", pady=10)
        
        # Botones
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=30)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="gray"
        ).pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self._on_save
        ).pack(side="right", expand=True, padx=5)
    
    def _on_save(self):
        """Guardar configuración"""
        print(f"Tema: {self.theme_var.get()}")
        print(f"Notificaciones: {self.notifications_var.get()}")
        print(f"Auto-guardar: {self.auto_save_var.get()}")
        self.destroy()


# USO:
settings = SettingsWindow(root)
```

---

## 6️⃣ Aplicar Responsive a Ventana Existente

### Sin Modificar la Clase
```python
from utils.responsive_manager import apply_responsive_to_window
import customtkinter as ctk

# Ventana existente (sin modificar su clase)
window = ctk.CTkToplevel(root)
window.title("Ventana Existente")

# Aplicar responsive sin tocar el código original
apply_responsive_to_window(window, preset='medium')

# Modal
window.transient(root)
window.grab_set()

# Resto del código...
```

---

## 7️⃣ ResponsiveWindow Directa

### Crear Ventana Rápidamente
```python
from utils.responsive_manager import ResponsiveWindow
import customtkinter as ctk

# Crear ventana responsive directamente
window = ResponsiveWindow(
    root,
    preset='large',
    title="Mi Ventana Rápida",
    modal=True  # Opcional
)

# Agregar contenido
frame = ctk.CTkFrame(window)
frame.pack(fill="both", expand=True, padx=20, pady=20)

ctk.CTkLabel(frame, text="¡Ventana lista!").pack(pady=50)
ctk.CTkButton(frame, text="Cerrar", command=window.destroy).pack()
```

---

## 8️⃣ Dimensiones Personalizadas

### Tamaño Custom con Responsive
```python
from utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk

class CustomWindow(ResponsiveMixin, ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ventana Custom")
        
        # Usar preset base pero sobrescribir dimensiones
        self.make_responsive(
            'medium',
            custom_width=1000,   # Ancho personalizado
            custom_height=700    # Alto personalizado
        )
```

---

## 9️⃣ Calcular Dimensiones sin Crear Ventana

### Para Pre-cálculos
```python
from utils.responsive_manager import get_responsive_dimensions

# Calcular dimensiones sin crear ventana
width, height, x, y = get_responsive_dimensions(
    preset='large',
    screen_width=1920,
    screen_height=1080
)

print(f"Ventana será: {width}x{height} en posición ({x}, {y})")

# Usar estas dimensiones como necesites
```

---

## 🔟 Template Completo para Nueva Ventana

### Plantilla Lista para Copiar
```python
"""
Módulo: mi_ventana.py
Descripción: [Tu descripción aquí]
"""

from utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk
from tkinter import messagebox


class MiVentana(ResponsiveMixin, ctk.CTkToplevel):
    """[Descripción de tu ventana]"""
    
    def __init__(self, parent, **kwargs):
        """
        Inicializar ventana
        
        Args:
            parent: Ventana padre
            **kwargs: Argumentos adicionales
        """
        super().__init__(parent)
        
        # Configuración básica
        self.title("[Título de tu ventana]")
        self.make_responsive('[preset]')  # fullscreen/large/medium/small/dialog
        
        # Modal (opcional)
        self.transient(parent)
        self.grab_set()
        
        # Variables de instancia
        self.data = kwargs.get('data', None)
        self.result = None
        
        # Construir interfaz
        self._build_ui()
        
        # Configuración adicional
        self._setup_bindings()
    
    def _build_ui(self):
        """Construir interfaz de usuario"""
        # Header
        self._create_header()
        
        # Main content
        self._create_content()
        
        # Footer/Buttons
        self._create_footer()
    
    def _create_header(self):
        """Crear encabezado"""
        header = ctk.CTkFrame(self, fg_color="#1a1a1a", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="[Título]",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=30, pady=20)
        
        ctk.CTkButton(
            header,
            text="✕",
            command=self.destroy,
            width=40,
            height=40
        ).pack(side="right", padx=30)
    
    def _create_content(self):
        """Crear contenido principal"""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tu contenido aquí
        ctk.CTkLabel(
            content,
            text="Contenido de tu ventana",
            font=("Arial", 14)
        ).pack(expand=True)
    
    def _create_footer(self):
        """Crear pie con botones"""
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            footer,
            text="Cancelar",
            command=self.destroy,
            fg_color="gray",
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            footer,
            text="Aceptar",
            command=self._on_accept,
            width=150
        ).pack(side="right", padx=5)
    
    def _setup_bindings(self):
        """Configurar atajos de teclado"""
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self._on_accept())
    
    def _on_accept(self):
        """Handle botón aceptar"""
        # Tu lógica aquí
        self.result = "accepted"
        self.destroy()
    
    def get_result(self):
        """Obtener resultado después de wait_window()"""
        return self.result


# Función auxiliar para mostrar la ventana
def show_mi_ventana(parent, **kwargs):
    """
    Mostrar ventana y retornar resultado
    
    Args:
        parent: Ventana padre
        **kwargs: Argumentos para la ventana
    
    Returns:
        Resultado de la ventana
    """
    window = MiVentana(parent, **kwargs)
    window.wait_window()
    return window.get_result()


# USO:
if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    
    resultado = show_mi_ventana(root, data={'ejemplo': 'datos'})
    print(f"Resultado: {resultado}")
```

---

## 🎨 Estilos y Temas

### Colores Consistentes
```python
# En tu ventana responsive
COLORS = {
    'primary': '#2196F3',
    'success': '#4CAF50',
    'danger': '#F44336',
    'warning': '#FF9800',
    'info': '#00BCD4',
    'dark_bg': '#1a1a1a',
    'card_bg': '#2a2a2a'
}

# Usar en componentes
ctk.CTkButton(
    parent,
    text="Botón",
    fg_color=COLORS['success'],
    hover_color='#45A049'
)
```

---

## ✅ Checklist de Implementación

Copia este checklist cuando implementes una nueva ventana:

```python
# [ ] 1. Importar ResponsiveMixin
# [ ] 2. Heredar de ResponsiveMixin (primero)
# [ ] 3. Llamar super().__init__(parent)
# [ ] 4. Aplicar self.make_responsive('[preset]')
# [ ] 5. Agregar self.transient(parent) si es modal
# [ ] 6. Agregar self.grab_set() si es modal
# [ ] 7. Construir UI
# [ ] 8. Probar en diferentes resoluciones
```

---

**¡Todos estos snippets están listos para copiar y usar!** 🚀

Simplemente copia el código que necesites y personalízalo para tu caso de uso.
