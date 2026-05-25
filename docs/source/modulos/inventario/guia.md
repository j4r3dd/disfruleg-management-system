# 📦 Gestionar Inventario - Guía Completa

## 📍 Acceder al Módulo

### Paso 1: Abre BodegaDisfruleg
1. Inicia sesión con tu usuario
2. Visualizarás el panel principal

### Paso 2: Navega a Gestionar Inventario
1. En el menú principal, busca **"Gestionar Inventario"**, **"Compras"** o **"Registro de Compras"**
2. Haz clic en él
3. Se abrirá la ventana del módulo

---

## 🎯 Interfaz Principal

### Elementos Principales:

**1. Tabla de Productos**
- Nombre del producto
- Stock actual
- Stock mínimo
- Estado (verde/amarillo/rojo)

**2. Tabla de Compras**
- Historial de compras realizadas
- Fecha y cantidad
- Proveedor y costo

**3. Botones de Acción**
- + Registrar Compra
- Ajustar Stock
- Ver Historial

**4. Campo de Búsqueda**
- Busca productos
- Filtra rápidamente

---

## 📥 Registrar una Compra

### Paso 1: Haz clic en "+ Registrar Compra"

Se abre un formulario con:
- **Producto:** (selector de productos)
- **Cantidad:** (número de unidades)
- **Fecha de Compra:** (día de hoy o anterior)
- **Proveedor:** (quién la vendió)
- **Costo Unitario:** (precio pagado por unidad)
- **Notas:** (opcional, observaciones)

### Paso 2: Selecciona el Producto

1. Haz clic en el campo **"Producto"**
2. Se abre una lista de productos
3. Busca o desplázate
4. Selecciona el producto

**Nota:** Si el producto no existe, debes crearlo en el módulo de Productos primero.

### Paso 3: Ingresa la Cantidad

1. En el campo **"Cantidad"**, escribe el número
2. Ejemplo: 100 (para 100 kg de papa)

### Paso 4: Ingresa la Fecha

1. Haz clic en **"Fecha de Compra"**
2. Selecciona la fecha (normalmente hoy)
3. Si fue ayer, selecciona ayer

### Paso 5: Ingresa Proveedor y Costo

1. **Proveedor:** Nombre de quién compró (ej: "Distribuidora ABC")
2. **Costo Unitario:** Cuánto pagó por unidad
   - Papa: $10/kg
   - Chile: $20/kg
3. Sistema calcula el costo total automáticamente

### Paso 6: Guarda la Compra

Haz clic en **"Guardar"** o **"Registrar Compra"**

**Resultado automático:**
- ✅ Compra registrada en historial
- ✅ Stock del producto aumenta
- ✅ Movimiento registrado

---

## 📊 Ver Stock Actual

### Método 1: Tabla Principal

1. En la ventana principal, verás tabla de **"Productos"**
2. Columna **"Stock Actual"** muestra cantidad disponible
3. Columna **"Estado"** muestra:
   - 🟢 Verde: Stock saludable
   - 🟡 Amarillo: Cerca del mínimo
   - 🔴 Rojo: Debajo del mínimo (¡COMPRA YA!)

### Método 2: Buscar Producto Específico

1. Campo **"Buscar"** en la tabla
2. Escribe nombre del producto
3. Se filtra automáticamente
4. Ves stock actual

**Ejemplo:**
- Escribes "papa" → Aparecen "Papa Blanca", "Papa Cambray"
- Stock Papa Blanca: 50 kg
- Stock Papa Cambray: 30 kg

---

## 🔧 Ajustar Stock Manual

Cuando el sistema no registre automáticamente (ej: pérdida, daño):

### Paso 1: Haz clic en "Ajustar Stock"

Se abre formulario con:
- **Producto:** (selector)
- **Ajuste:** (cantidad a sumar o restar)
- **Motivo:** (por qué se ajusta)
- **Nota:** (observación adicional)

### Paso 2: Selecciona Producto y Cantidad

1. Selecciona el producto
2. Ingresa el ajuste:
   - Positivo (+): agregar stock (ej: +10)
   - Negativo (-): quitar stock (ej: -5)

### Paso 3: Ingresa Motivo

**Motivos comunes:**
- "Devolución de cliente"
- "Producto dañado"
- "Merma/evaporación"
- "Ajuste de conteo"
- "Error anterior"

### Paso 4: Guarda el Ajuste

Haz clic **"Aplicar Ajuste"**

**Resultado:**
- ✅ Stock actualizado
- ✅ Movimiento registrado con motivo
- ✅ Auditoría disponible

---

## 📈 Ver Historial de Movimientos

### Paso 1: Selecciona Producto

1. En tabla de productos, haz clic en un producto
2. O selecciona en el campo de búsqueda

### Paso 2: Ver Historial

1. Aparece sección **"Historial"** o **"Movimientos"**
2. Muestra todos los cambios:
   - Compras (entradas)
   - Ventas (salidas)
   - Ajustes (cambios manuales)

**Información por movimiento:**
- Fecha
- Tipo (Compra/Venta/Ajuste)
- Cantidad
- Stock resultante
- Usuario que registró

---

## ⚠️ Alertas de Stock

### Cómo Funcionan

El sistema alerta cuando:
- Stock actual < Stock Mínimo
- Stock llega a 0
- Stock sigue bajando

### Dónde Ver Alertas

**En la tabla principal:**
- Productos con stock bajo aparecen en ROJO

**En panel de alertas:**
- Lista de productos que necesitan compra
- Cantidad a comprar recomendada

### Qué Hacer

Cuando ves alerta roja:
1. **URGENTE:** Registrar compra inmediatamente
2. Ir a proveedor favorito
3. Hacer compra
4. Registrar en el sistema

---

## 🔍 Búsqueda y Filtrado

### Buscar por Nombre

1. Campo **"Buscar"**
2. Escribe nombre o parte de él
3. Se filtra automáticamente

### Filtrar por Estado

**Opción 1:** Ver solo productos con stock bajo
1. Botón **"Mostrar Bajos"** o **"Críticos"**
2. Se muestran solo en rojo/amarillo

**Opción 2:** Ver todos
1. Botón **"Mostrar Todos"**
2. Se muestran todos los productos

---

## 🚨 Solución de Problemas

### "No puedo registrar una compra"

**Problema:** Error al guardar

**Soluciones:**
1. Verifica que **seleccionaste un producto**
2. Verifica que **ingresaste una cantidad** válida
3. Verifica que **la cantidad sea > 0**
4. Si el producto no existe, créalo primero

---

### "El stock no coincide con mi conteo"

**Problema:** Sistema dice 50 kg, pero contaste 45 kg

**Solución:**
1. Haz un **ajuste manual**
2. Motivo: "Diferencia de conteo"
3. Ajuste: -5 (para restar 5 kg)
4. Guarda

El historial quedará registrado para auditoría.

---

### "¿Por qué aparece un producto que vendí?"

**Razón:** El sistema registra TODAS las transacciones

Cuando se vende un producto:
- Stock disminuye automáticamente
- Movimiento queda registrado
- Historial es completo

Es normal ver ventas en el historial.

---

## 💡 Tips y Mejores Prácticas

### 📋 Frecuencia de Actualización

```
✅ RECOMENDADO:
- Registrar compras: Cuando llegan los productos
- Registrar ventas: Diariamente o al cierre
- Contar físico: Mensualmente o trimestral

❌ EVITAR:
- Dejar compras sin registrar
- Actualizar solo cuando se acuerde
- No hacer conteo físico (asincronía)
```

### 🔒 Stock Mínimo Correcto

**Fórmula:**
```
Stock Mínimo = Consumo Diario × Días para Nueva Compra
```

**Ejemplo:**
- Papa Blanca:
  - Consumo diario: 10 kg
  - Días para nueva compra: 3 días
  - Stock Mínimo: 10 × 3 = 30 kg

### 📊 Conteo Físico

```
Recomendación: Mensualmente

Proceso:
1. Contar físicamente cada producto
2. Comparar con sistema
3. Si hay diferencia, hacer ajuste
4. Investigar grandes diferencias
5. Ajustar procedimientos si es necesario
```

---

## 🔗 Información Adicional

- **Panel de Control:** [Volver a Inventario →](index.md)
- **Preguntas Frecuentes:** [Ver FAQ →](faq.md)
- **Referencia Rápida:** [Ver Referencia →](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
