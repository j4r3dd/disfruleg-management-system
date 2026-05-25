# 📦 Gestionar Inventario

## Descripción

El módulo **Gestionar Inventario** permite administrar el stock de tus productos en tiempo real. Registra compras, entradas y salidas de productos, mantén control de cantidades disponibles, realiza ajustes de inventario y genera reportes de existencias.

### Funcionalidades Principales
- ✅ Registrar compras de productos
- ✅ Actualizar stock automáticamente
- ✅ Realizar ajustes manuales de inventario
- ✅ Consultar existencias por producto
- ✅ Historial de movimientos
- ✅ Alertas de stock bajo
- ✅ Búsqueda y filtrado
- ✅ Reportes de inventario

---

## 🎯 ¿Para Qué Sirve?

### Casos de Uso Comunes:

**📦 Necesitas saber cuánto tienes en stock**
- ¿Cuánta papa blanca tengo?
- ¿Se acabó el chile serrano?
- ¿Cuándo compro más?

**📊 Quieres evitar desabastecimiento**
- Alertas de stock bajo
- Historial de consumo
- Predicción de necesidades

**💼 Necesitas registrar todas las compras**
- Origen del producto
- Fecha de compra
- Costo de adquisición

**🔍 Quieres trazabilidad completa**
- Historial de movimientos
- Auditoría de cambios
- Ajustes justificados

---

## 📖 Contenido Disponible

| Sección | Descripción |
|:--------|:-----------|
| [**Guía Completa**](guia.md) | Paso a paso para gestionar inventario |
| [**Videos Tutoriales**](videos.md) | Videos de capacitación (próximamente) |
| [**Preguntas Frecuentes**](faq.md) | Respuestas a dudas comunes |

---

## 🚀 Comienza Aquí

Si es tu **primera vez** en el módulo:

1. **Lee la introducción** (esta página)
2. **Ve a la [Guía →](guia.md)** (15 minutos)
3. **Mira los [Videos →](videos.md)** (cuando estén disponibles)
4. **Consulta [FAQ →](faq.md)** si tienes dudas

---

## 🔧 Conceptos Clave

### 📦 Producto
Un artículo de tu inventario con:
- Nombre y descripción
- Stock actual (cantidad disponible)
- Stock mínimo (para alertas)
- Unidad de medida (kg, pza, etc.)

### 📥 Compra
Registro de entrada de productos:
- Producto comprado
- Cantidad
- Fecha de compra
- Proveedor
- Costo unitario

### 📊 Stock
Cantidad disponible de un producto.

**Fórmula:**
```
Stock Actual = Stock Anterior + Compras - Ventas + Ajustes
```

### ⚠️ Alerta de Stock
Notificación cuando el stock está bajo:
- Stock Mínimo: cantidad mínima recomendada
- Stock Crítico: necesitas comprar YA
- Stock Óptimo: cantidad ideal

---

## 💡 Ventajas de Gestionar Bien el Inventario

| Ventaja | Beneficio |
|:---|:---|
| ✅ **Control Total** | Sabes qué tienes en todo momento |
| ✅ **Evita Desabastecimiento** | Alertas de stock bajo |
| ✅ **Optimiza Compras** | Compra lo necesario, no de más |
| ✅ **Reduce Pérdidas** | Productos frescos, menos expiración |
| ✅ **Trazabilidad** | Historial completo de movimientos |

---

## 📊 Flujo Típico

```
1. Registrar Compra (entrada de productos)
   ↓
2. Sistema actualiza Stock automáticamente
   ↓
3. Al vender producto, Stock disminuye
   ↓
4. Si Stock bajo, Sistema alerta
   ↓
5. Registrar nueva Compra
```

---

## ❓ ¿Necesitas Ayuda?

- **Paso a paso:** Consulta la [**Guía →**](guia.md)
- **Dudas específicas:** Ve a [**FAQ →**](faq.md)
- **Video tutorial:** Mira los [**Videos →**](videos.md)

---

## 🎬 Ejemplo Práctico

### Escenario: Control de Papa Blanca

**Día 1:**
- Stock inicial: 0 kg
- Compra: 100 kg
- Stock actual: 100 kg

**Día 2:**
- Venta: 30 kg
- Stock actual: 70 kg

**Día 3:**
- Venta: 20 kg
- Stock actual: 50 kg

**Día 4:**
- Stock Mínimo: 30 kg
- Stock actual: 50 kg ✅ (todo bien)

**Día 5:**
- Venta: 25 kg
- Stock actual: 25 kg ⚠️ (alerta: bajo mínimo)
- **Acción:** Registrar compra inmediatamente

**Día 6:**
- Compra: 80 kg
- Stock actual: 105 kg ✅ (repuesto)

---

**Siguiente paso:** [📖 Ir a la Guía Completa →](guia.md)
