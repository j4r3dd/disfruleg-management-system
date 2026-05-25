# 👥 Gestionar Clientes

## Descripción

El módulo **Gestionar Clientes** es el sistema central para administrar toda la información de tus clientes. Desde aquí puedes crear nuevos clientes, organizarlos en grupos, asignar tipos de cliente, gestionar información fiscal y mantener un control completo de tu base de clientes.

### Funcionalidades Principales
- ✅ Crear, editar y eliminar clientes
- ✅ Organizar clientes en grupos
- ✅ Asignar tipos de cliente con descuentos
- ✅ Validar información fiscal (RFC, email)
- ✅ Activar/desactivar clientes
- ✅ Búsqueda y filtrado rápido
- ✅ Gestión de grupos y tipos de cliente
- ✅ Información de contacto y dirección

---

## 🎯 ¿Para Qué Sirve?

### Casos de Uso Comunes:

**📋 Necesitas una base de datos de clientes centralizada**
- Todos los datos en un lugar
- Acceso rápido a información
- Histórico de contactos

**🏢 Tienes diferentes tipos de clientes**
- Mayoristas vs Minoristas
- Descuentos por tipo
- Organización por grupo

**💼 Información fiscal importante**
- RFC para facturas
- Razón social
- Régimen fiscal
- Dirección fiscal

**📞 Gestión de contactos**
- Teléfono y email
- Notas personalizadas
- Historial de interacciones

---

## 📖 Contenido Disponible

| Sección | Descripción |
|:--------|:-----------|
| [**Guía Completa**](guia.md) | Paso a paso para gestionar clientes |
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

### 👤 Cliente
Un registro individual de una persona o empresa que compra tus productos.

**Información básica:**
- Nombre del cliente
- Grupo (categorización)
- Tipo de cliente (descuentos)
- Estado (activo/inactivo)

**Información adicional:**
- Teléfono y email
- RFC (para facturas)
- Razón social
- Dirección fiscal
- Notas personalizadas

### 📁 Grupo
Una categoría para organizar clientes. Ejemplo: "Mayoristas", "Minoristas", "Restaurantes".

**Características:**
- Clave única del grupo
- Descripción
- Tipo de cliente asignado (descuentos)

### 🏷️ Tipo de Cliente
Define descuentos especiales para categorías de clientes.

**Ejemplo:**
- Tipo: "Mayorista" → 15% descuento
- Tipo: "Minorista" → 5% descuento
- Tipo: "Empresa" → 10% descuento

---

## 💡 Ventajas de Organizar Bien

| Ventaja | Beneficio |
|:---|:---|
| ✅ **Grupos** | Encuentra clientes rápido por categoría |
| ✅ **Tipos** | Aplica descuentos automáticamente |
| ✅ **Información Fiscal** | Genera facturas correctas |
| ✅ **Contacto** | Mantén comunicación eficiente |
| ✅ **Activo/Inactivo** | Controla quién compra actualmente |

---

## 📊 Flujo Típico

```
1. Crear Tipos de Cliente (Mayorista, Minorista, etc.)
   ↓
2. Crear Grupos (categorización)
   ↓
3. Crear Clientes (asignar a grupo y tipo)
   ↓
4. Usar en Cotizaciones/Recibos (se aplican descuentos automáticamente)
```

---

## ❓ ¿Necesitas Ayuda?

- **Paso a paso:** Consulta la [**Guía →**](guia.md)
- **Dudas específicas:** Ve a [**FAQ →**](faq.md)
- **Video tutorial:** Mira los [**Videos →**](videos.md)

---

## 🎬 Ejemplo Práctico

### Escenario: Tienda de Frutas y Verduras

**1. Crear Tipos de Cliente:**
- "Mayorista" (15% descuento)
- "Minorista" (0% descuento)
- "Restaurante" (10% descuento)

**2. Crear Grupos:**
- "Zona Centro" → Tipo: Mayorista
- "Zona Periférica" → Tipo: Minorista
- "Clientes Especiales" → Tipo: Restaurante

**3. Crear Clientes:**
- "Mercado Los Mangos" → Zona Centro → Mayorista
- "Tienda Doña María" → Zona Periférica → Minorista
- "Restaurante El Ceviche" → Clientes Especiales → Restaurante

**4. Al hacer una cotización:**
- Si vendo a "Mercado Los Mangos" → Se aplica 15% descuento
- Si vendo a "Tienda Doña María" → Se aplica 0% descuento
- Si vendo a "Restaurante El Ceviche" → Se aplica 10% descuento

---

**Siguiente paso:** [📖 Ir a la Guía Completa →](guia.md)
