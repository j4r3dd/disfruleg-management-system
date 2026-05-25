# 📦 Gestionar Inventario - Preguntas Frecuentes

## 🚀 Primeros Pasos

### ¿Cómo empiezo a usar el inventario?

1. Abre módulo **Gestionar Inventario**
2. Registra tu **primera compra:**
   - Producto: elige uno
   - Cantidad: ingresa cuánto compraste
   - Proveedor: quién la vendió
   - Costo: cuánto pagaste
3. Sistema **actualiza stock automáticamente**
4. ¡Listo! Ya tienes control

---

### ¿Qué pasa cuando vendo un producto?

**Automático:**
1. Cuando se registra una venta en Recibos/Cotizaciones
2. Sistema reduce el stock automáticamente
3. Movimiento queda registrado
4. No tienes que hacer nada manual

---

### ¿Necesito crear productos primero?

**Sí.** Los productos deben existir antes de registrar compras.

**Donde crear productos:**
- Módulo de **"Gestionar Productos"** o **"Catálogo"**
- Allí definas nombre, unidad, stock mínimo, etc.

Luego en Inventario solo registras movimientos.

---

## 📥 Registrar Compras

### ¿Qué datos son obligatorios en una compra?

**OBLIGATORIO:**
- ✅ Producto
- ✅ Cantidad
- ✅ Fecha

**OPCIONAL:**
- Proveedor
- Costo unitario
- Notas

Puedes dejar opcionales en blanco si no tienes la info.

---

### ¿Puedo registrar una compra de hace varios días?

**Sí.** En el campo **"Fecha de Compra"** selecciona la fecha real.

**Ejemplo:**
- Hoy es 13 de diciembre
- Pero la compra fue el 11
- Selecciona 11 en el calendario
- Registra la compra con fecha 11

---

### ¿Qué pasa si me equivoco en la cantidad?

**Soluciones:**

**Opción 1:** Registrar ajuste
- Cantidad registrada: 100 kg
- Cantidad real: 95 kg
- Hacer ajuste: -5 kg
- Motivo: "Error de cantidad"

**Opción 2:** Eliminar compra (si es muy reciente)
- Eliminar la compra incorrecta
- Registrar nueva con cantidad correcta

**Mejor opción:** Opción 1 (mantiene auditoría)

---

## 📊 Stock y Control

### ¿Cómo sé cuánto tengo en stock?

**Tabla de productos** (pantalla principal):
- Columna **"Stock Actual"** muestra cantidad disponible
- Stock en color:
  - 🟢 Verde: normal
  - 🟡 Amarillo: bajo
  - 🔴 Rojo: crítico

---

### ¿Qué es "Stock Mínimo"?

**Cantidad mínima recomendada** de un producto.

**Propósito:**
- Evitar desabastecimiento
- Alertar cuando comprar
- Calcular necesidad

**Ejemplo:**
- Papa Blanca:
  - Stock Mínimo: 30 kg
  - Stock Actual: 25 kg ← ¡ALERTA! Está bajo

---

### ¿Cómo calculo el Stock Mínimo correcto?

**Fórmula:**
```
Stock Mínimo = Consumo Diario × Días para Compra
```

**Pasos:**
1. Analiza cuánto consumes por día
2. ¿Cuántos días tarda llegar nueva compra?
3. Multiplica: Diario × Días = Mínimo

**Ejemplo:**
- Papa:
  - Consumo diario: 10 kg
  - Demora compra: 3 días
  - Stock Mínimo: 10 × 3 = **30 kg**

---

## 🔧 Ajustes Manuales

### ¿Cuándo debo hacer un ajuste manual?

**Cuando:**
- Hay diferencia entre sistema y conteo físico
- Producto se dañó o perdió
- Cliente devolvió producto
- Error anterior que necesita corregir

**No es para:**
- Registrar ventas (automático)
- Registrar compras (usa "Registrar Compra")

---

### ¿Cómo justifico un ajuste?

Siempre ingresa un **"Motivo"**:

**Ejemplos válidos:**
- "Devolución cliente"
- "Producto dañado en transporte"
- "Merma/evaporación"
- "Diferencia conteo físico"
- "Error de 15 kg anterior"

**Por qué es importante:**
- Auditoría y control
- Análisis de pérdidas
- Justificación ante gerencia

---

## 📈 Historial y Auditoría

### ¿Puedo ver todo lo que pasó con un producto?

**Sí.** Historial completo:
1. Selecciona un producto
2. Aparece pestaña **"Historial"** o **"Movimientos"**
3. Ves todas las transacciones:
   - Compras (quién, cuándo, cuánto)
   - Ventas (reducción de stock)
   - Ajustes (con motivo)

---

### ¿Puedo rastrear un producto específico?

**Depende del sistema:**

**Si tienes lotes:**
- Puedes ver de qué proveedor
- En qué fecha se compró
- Cuándo se vendió

**Si no tienes lotes:**
- Ves movimiento general
- No por lote individual
- Suficiente para mayoría de negocios

---

## ⚠️ Alertas

### ¿Cómo funcionan las alertas?

**Automático:**
1. Si Stock Actual < Stock Mínimo
2. Sistema marca en ROJO
3. Aparece en lista de alertas

**Qué hacer:**
1. Ver qué está en rojo
2. Registrar compra inmediatamente
3. Llenar el stock

---

### ¿Puedo recibir alertas por email/SMS?

**Depende de la configuración.**

Opciones:
- ✅ Alertas visuales en sistema (siempre)
- ✅ Notificaciones en dashboard
- ⏳ Email/SMS (si está configurado)

Consulta con tu administrador.

---

## 🚨 Problemas Comunes

### "El stock no coincide con mi conteo"

**Problema:** Sistema dice 100 kg, contaste 95 kg

**Razones posibles:**
1. Compra no registrada en sistema
2. Venta no registrada
3. Derrame/pérdida no anotada
4. Evaporación (productos frescos)

**Solución:**
1. Hacer ajuste manual: -5 kg
2. Motivo: "Diferencia conteo físico"
3. Investigar causa si es grande (>10%)

---

### "¿Por qué bajó el stock sin que hiciera nada?"

**Razones:**
1. **Venta registrada:** Alguien vendió producto
2. **Ajuste:** Alguien hizo ajuste manual
3. **Sistema automático:** Otro módulo lo restó

Consulta el **historial** para ver qué pasó.

---

### "Necesito aumentar stock, ¿cómo?"

**Opción 1:** Registrar compra
- Usa "Registrar Compra"
- Stock aumenta automáticamente

**Opción 2:** Ajuste manual
- Usa "Ajustar Stock"
- Ajuste: +50 (para agregar 50)
- Motivo: "Devolución de cliente" o similar

---

## 💡 Tips Profesionales

### 📊 Conteo Físico Mensual

```
Proceso Recomendado:

1. Establecer fecha (ej: último viernes mes)
2. Contar TODOS los productos
3. Anotar cantidades reales
4. Comparar con sistema
5. Hacer ajustes por diferencias
6. Investigar diferencias grandes
7. Documentar hallazgos

Beneficio: Auditoría, control, detección fraude
```

---

### 🔒 Prevención de Errores

```
✅ SIEMPRE:
- Registrar compras inmediatamente
- Verificar cantidades antes de guardar
- Justificar todos los ajustes
- Hacer conteo físico regular

❌ EVITAR:
- Dejar compras sin registrar
- Registrar aproximadamente
- Ajustes sin motivo
- Ignorar alertas de stock bajo
```

---

### 📈 Análisis Regular

```
Mensual:
- Revisar productos con más movimiento
- Analizar pérdidas/ajustes
- Validar stock mínimos

Trimestral:
- Análisis de rotación
- Productos lentos (considera eliminar)
- Productos rápidos (invertir más)
```

---

## 🔗 Enlaces Útiles

- [📖 Guía Completa](guia.md)
- [📺 Videos](videos.md)
- [⚡ Referencia Rápida](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
