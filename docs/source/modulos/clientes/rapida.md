# 👥 Gestionar Clientes - Referencia Rápida

## ⚡ Orden de Creación

1. **Tipos de Cliente** (Mayorista, Minorista, etc.)
2. **Grupos** (Zona Centro, Minoristas, etc.)
3. **Clientes** (asignar a grupo)

---

## 📋 Crear Tipo de Cliente

1. Pestaña: **Tipos de Cliente**
2. Botón: **+ Nuevo Tipo**
3. Completa:
   - Nombre: "Mayorista"
   - Descuento: 15 (%)
4. Guardar

---

## 📁 Crear Grupo

1. Pestaña: **Grupos**
2. Botón: **+ Nuevo Grupo**
3. Completa:
   - Clave: "MAYORISTAS" (único)
   - Descripción: "Clientes mayoristas"
   - Tipo Cliente: "Mayorista"
4. Guardar

---

## 👤 Crear Cliente

1. Pestaña: **Clientes**
2. Botón: **+ Nuevo Cliente**
3. **Obligatorio:**
   - Nombre: "Mercado Los Mangos"
   - Grupo: "MAYORISTAS"
4. **Opcional:**
   - Teléfono: "555-1234"
   - Email: "contacto@mercado.com"
   - RFC: "RFC123456ABC"
   - Dirección fiscal
   - Notas
5. Guardar

---

## 🔍 Buscar Cliente

1. En tabla de clientes
2. Campo **"Buscar"**
3. Escribe nombre o parte de él
4. Se filtra automáticamente

---

## ✏️ Editar Cliente

1. En tabla, haz clic en cliente
2. Modifica campos
3. Botón: **Actualizar**

---

## 🚫 Desactivar Cliente

1. Abre cliente
2. Desmarca: **Activo**
3. Guardar

**Ventaja:** Mantiene historial sin eliminarlo

---

## ❌ Eliminar Cliente

1. Selecciona en tabla
2. Botón: **Eliminar**
3. Confirma

**⚠️ Restricción:** No puedes si tiene recibos

**Mejor opción:** Desactiva en lugar de eliminar

---

## 🏷️ Campos Obligatorios

| Campo | Obligatorio | Ejemplo |
|:---|:---:|:---|
| Nombre | ✅ | "Mercado Los Mangos" |
| Grupo | ✅ | "Mayoristas" |
| Teléfono | ❌ | "555-1234" |
| Email | ❌ | "contacto@mercado.com" |
| RFC | ❌ | "RFC123456ABC" |

---

## 💡 Validaciones

| Campo | Regla |
|:---|:---|
| **Nombre** | No vacío |
| **Grupo** | Debe existir |
| **Email** | Formato válido (usuario@dominio.com) |
| **RFC** | Formato válido (12 caracteres) |
| **Descuento Tipo** | 0-100% |

---

## 🎯 Flujo Típico

```
1. Crear "Tipo: Mayorista (15%)"
   ↓
2. Crear "Grupo: Zona Centro → Mayorista"
   ↓
3. Crear "Cliente: Mercado → Zona Centro"
   ↓
4. Al cotizar → Aplica 15% descuento automático
```

---

## 🔗 Más Información

- [📖 Guía Completa](guia.md)
- [❓ FAQ](faq.md)
- [📺 Videos](videos.md)

---

**Imprime para referencia rápida.**
