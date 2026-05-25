# 📦 Gestionar Inventario - Referencia Rápida

## ⚡ 4 Pasos Rápidos

### 1️⃣ COMPRA
```
+ Registrar Compra
→ Selecciona Producto
→ Cantidad: 100
→ Guardar
```

### 2️⃣ STOCK ACTUALIZA
```
Sistema actualiza automático
Stock aumenta en 100 unidades
```

### 3️⃣ VENTA
```
Al vender (en Recibos)
Stock disminuye automático
```

### 4️⃣ ALERTA
```
Si Stock < Mínimo
Aparece en ROJO
¡Compra urgente!
```

---

## 📥 Registrar Compra

1. Botón: **+ Registrar Compra**
2. Completa:
   - Producto: (selector)
   - Cantidad: 100
   - Fecha: (hoy o fecha real)
   - Proveedor: "Distribuidora ABC"
   - Costo: $10/unidad
3. Guardar

---

## 📊 Ver Stock

**Tabla Principal:**
- Columna "Stock Actual"
- 🟢 Verde: normal
- 🟡 Amarillo: bajo
- 🔴 Rojo: ¡COMPRA YA!

---

## 🔧 Ajustar Stock

1. Botón: **Ajustar Stock**
2. Completa:
   - Producto: (selector)
   - Ajuste: +50 o -10
   - Motivo: "Devolución cliente"
3. Guardar

---

## 📈 Ver Historial

1. Selecciona producto
2. Pestaña: **Historial**
3. Ve todos los movimientos

---

## 🔍 Buscar

1. Campo: **Buscar**
2. Escribe nombre
3. Se filtra automático

---

## ⚠️ Alertas

**Stock Bajo:**
```
Aparece ROJO en tabla
Significa: Stock < Stock Mínimo
Acción: Registra compra inmediatamente
```

---

## 📋 Stock Mínimo Correcto

**Fórmula:**
```
Stock Mínimo = Consumo Diario × Días para Compra

Ejemplo:
Papa = 10 kg/día × 3 días = 30 kg mínimo
```

---

## 🎯 Flujo Típico

```
1. Compra llega (100 kg papa)
   ↓
2. Registras en sistema (+100)
   ↓
3. Stock ahora: 100 kg
   ↓
4. Cliente compra 30 kg
   ↓
5. Stock ahora: 70 kg (automático)
   ↓
6. Cae bajo mínimo (30 kg)
   ↓
7. Aparece ROJO: ¡ALERTA!
   ↓
8. Registras nueva compra
```

---

## 🔗 Más Info

- [📖 Guía Completa](guia.md)
- [❓ FAQ](faq.md)
- [📺 Videos](videos.md)

---

**Imprime para referencia rápida.**
