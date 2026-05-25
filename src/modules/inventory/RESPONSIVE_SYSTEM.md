# 📐 Sistema Responsive para Módulo Inventory

## 📋 Resumen de Cambios

Se ha implementado un sistema completo de ventanas responsive para el módulo `inventory` que permite que todas las ventanas se adapten automáticamente a diferentes tamaños de pantalla.

### ✅ Archivos Creados

1. **`inventory/utils/__init__.py`**
   - Inicializa el paquete utils

2. **`inventory/utils/responsive_manager.py`**
   - Sistema completo de gestión responsive
   - Incluye `ResponsiveMixin`, `ResponsiveWindow` y utilidades

3. **`inventory/test_responsive_inventory.py`**
   - Suite completa de tests para verificar el sistema

### ✅ Archivos Modificados

1. **`inventory/ui/purchase_history_dialog.py`**
   - Ahora hereda de `ResponsiveMixin`
   - Usa preset `'large'` (85% de pantalla)
   - Centrado automático y responsive

2. **`inventory/ui/product_dialog.py`**
   - Convertido a clase `ProductDialog` con `ResponsiveMixin`
   - Usa preset `'dialog'` (tamaño fijo más pequeño)
   - Mantiene compatibilidad con función `create_product_dialog()`

---

## 🎯 Presets Disponibles

El sistema incluye 5 presets predefinidos:

| Preset | Tamaño | Uso Recomendado |
|--------|---------|-----------------|
| `fullscreen` | 100% pantalla | Aplicaciones principales |
| `large` | 85% pantalla (1400x900) | Ventanas de historial, búsqueda avanzada |
| `medium` | 75% pantalla (1200x800) | Ventanas de formularios complejos |
| `small` | 55% pantalla (800x600) | Ventanas de configuración |
| `dialog` | Fijo 500x400 | Diálogos simples, confirmaciones |

---

## 🚀 Cómo Usar

### Método 1: ResponsiveMixin (Recomendado)

Usa herencia múltiple para agregar capacidades responsive a cualquier ventana:

```python
from inventory.utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk

class MyWindow(ResponsiveMixin, ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Mi Ventana")
        
        # Aplicar responsive con preset
        self.make_responsive('medium')
        
        # Resto de tu código...
```

### Método 2: ResponsiveWindow (Uso Directo)

Usa la clase ResponsiveWindow directamente:

```python
from inventory.utils.responsive_manager import ResponsiveWindow

window = ResponsiveWindow(
    parent,
    preset='large',
    title="Mi Ventana",
    modal=True  # Opcional
)

# Agregar contenido a window...
```

### Método 3: Aplicar a Ventana Existente

Aplica responsive a una ventana ya creada:

```python
from inventory.utils.responsive_manager import apply_responsive_to_window

# Ventana existente
window = ctk.CTkToplevel(parent)
window.title("Mi Ventana")

# Aplicar responsive
apply_responsive_to_window(window, preset='medium')
```

---

## 📝 Ejemplos de Implementación

### Ejemplo 1: Diálogo Simple

```python
from inventory.utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk

class ConfirmDialog(ResponsiveMixin, ctk.CTkToplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.title("Confirmar")
        
        # Diálogo pequeño y centrado
        self.make_responsive('dialog')
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        
        # UI
        ctk.CTkLabel(self, text=message).pack(pady=20)
        ctk.CTkButton(self, text="OK", command=self.destroy).pack(pady=10)
```

### Ejemplo 2: Ventana de Búsqueda Avanzada

```python
from inventory.utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk

class AdvancedSearchWindow(ResponsiveMixin, ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Búsqueda Avanzada")
        
        # Ventana grande para muchos filtros
        self.make_responsive('large')
        
        # UI compleja con filtros...
```

### Ejemplo 3: Configuración Media

```python
from inventory.utils.responsive_manager import ResponsiveMixin
import customtkinter as ctk

class SettingsWindow(ResponsiveMixin, ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuración")
        
        # Tamaño medio para formularios
        self.make_responsive('medium')
        
        # Formularios de configuración...
```

---

## 🔧 Configuración Personalizada

### Dimensiones Personalizadas

```python
# Sobrescribir dimensiones del preset
self.make_responsive('medium', custom_width=1000, custom_height=700)
```

### Calcular Dimensiones sin Crear Ventana

```python
from inventory.utils.responsive_manager import get_responsive_dimensions

# Obtener dimensiones calculadas
width, height, x, y = get_responsive_dimensions(
    preset='large',
    screen_width=1920,
    screen_height=1080
)

print(f"Ventana será: {width}x{height} en posición ({x}, {y})")
```

### Crear Preset Personalizado

Puedes modificar o agregar presets en `responsive_manager.py`:

```python
WINDOW_PRESETS['custom'] = {
    'width': 1100,
    'height': 750,
    'width_ratio': None,  # Usar width fijo
    'height_ratio': None,  # Usar height fijo
    'min_width': 900,
    'min_height': 600,
    'resizable': True,
    'center': True
}
```

---

## 🧪 Ejecutar Tests

```bash
# Tests automáticos (sin mostrar ventanas)
cd inventory
python test_responsive_inventory.py

# Tests interactivos (muestra ventanas)
python test_responsive_inventory.py --interactive
```

### Tests Incluidos

1. ✅ **test_1_window**: ResponsiveWindow directa
2. ✅ **test_2_mixin**: ResponsiveMixin con herencia múltiple
3. ✅ **test_3_presets**: Todos los presets (fullscreen, large, medium, small, dialog)
4. ✅ **test_4_purchase_history**: PurchaseHistoryDialog responsive
5. ✅ **test_5_product_dialog**: ProductDialog responsive
6. ✅ **test_6_dimensions**: Función get_responsive_dimensions
7. ✅ **test_7_window_presets**: Verificación de WINDOW_PRESETS

---

## 📊 Ventanas Actualizadas

### ✅ PurchaseHistoryDialog
- **Preset**: `large` (85% pantalla)
- **Características**:
  - Centrado automático
  - Redimensionable
  - Tamaño mínimo: 1200x800

### ✅ ProductDialog
- **Preset**: `dialog` (500x400 fijo)
- **Características**:
  - Centrado automático
  - Tamaño fijo (no redimensionable)
  - Perfecto para diálogos simples

---

## 🎨 Ventanas Pendientes

Si deseas actualizar más ventanas, aquí está la guía:

### PurchaseView (Ventana Principal)

La `PurchaseView` trabaja con el root window directamente. Para hacerla responsive:

```python
# En tu código principal donde inicializas
from inventory.utils.responsive_manager import apply_responsive_to_window

root = ctk.CTk()

# Aplicar responsive al root
apply_responsive_to_window(root, preset='large')

# Crear la vista
view = PurchaseView(root, user_data)
```

### Otras Ventanas Personalizadas

Para cualquier otra ventana en tu proyecto:

```python
from inventory.utils.responsive_manager import ResponsiveMixin

class MiVentana(ResponsiveMixin, ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.make_responsive('medium')  # Elige el preset adecuado
```

---

## 📐 Configuración por Tipo de Ventana

| Tipo de Ventana | Preset Recomendado | Ejemplo |
|-----------------|-------------------|---------|
| Ventana principal | `fullscreen` o `large` | App principal |
| Búsqueda/Historial | `large` | PurchaseHistoryDialog |
| Formularios complejos | `medium` | Registro de compras |
| Configuración | `small` | Preferencias |
| Diálogos simples | `dialog` | ProductDialog, Confirmación |

---

## 🔥 Características Principales

### ✅ Centrado Automático
Todas las ventanas se centran automáticamente en la pantalla.

### ✅ Adaptación a Resolución
Las ventanas se adaptan al tamaño de la pantalla del usuario.

### ✅ Tamaños Mínimos
Se garantiza que las ventanas no sean demasiado pequeñas.

### ✅ Compatibilidad
Funciona con cualquier ventana CustomTkinter (CTk, CTkToplevel).

### ✅ Fácil de Usar
Solo necesitas una línea de código: `self.make_responsive('preset')`

---

## 🐛 Solución de Problemas

### Error: "No module named 'inventory.utils'"

Asegúrate de que:
1. El archivo `inventory/utils/__init__.py` existe
2. Estás ejecutando desde el directorio correcto

### Error: "ResponsiveMixin not found"

Verifica la ruta de importación:
```python
# Correcto
from inventory.utils.responsive_manager import ResponsiveMixin

# O si estás dentro del módulo inventory
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.responsive_manager import ResponsiveMixin
```

### La ventana no se centra

Asegúrate de llamar a `make_responsive()` ANTES de mostrar la ventana:
```python
def __init__(self, parent):
    super().__init__(parent)
    self.make_responsive('medium')  # Antes de mostrar
    # Resto del código...
```

---

## 📚 Referencias

- **responsive_manager.py**: Sistema completo con todas las funciones
- **test_responsive_inventory.py**: Ejemplos de uso y tests
- **purchase_history_dialog.py**: Ejemplo de implementación con ResponsiveMixin
- **product_dialog.py**: Ejemplo de diálogo responsive

---

## 🎓 Mejores Prácticas

1. **Usar Presets**: Prefiere los presets predefinidos antes de personalizar
2. **Consistencia**: Usa el mismo preset para ventanas similares
3. **Testing**: Prueba en diferentes resoluciones de pantalla
4. **Herencia Múltiple**: Siempre pon `ResponsiveMixin` primero en la herencia
5. **Centrado**: Deja el centrado automático activado para mejor UX

---

## 📞 Soporte

Para más información sobre el sistema responsive o problemas de implementación, consulta:

- `inventory/utils/responsive_manager.py` - Código fuente completo
- `inventory/test_responsive_inventory.py` - Ejemplos y tests
- Esta documentación

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0.0  
**Módulo**: Inventory - BodegaDisfruleg
