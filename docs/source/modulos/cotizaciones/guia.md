# 📦 Gestionar Compras - Guía Completa

## 📍 Acceder al Módulo

### Paso 1: Abre BodegaDisfruleg
1. Inicia sesión con tu usuario
2. Visualizarás el panel principal

### Paso 2: Navega a Gestionar Compras
1. En el menú principal, busca **"Gestionar Compras"**, **"Importación"** o **"Órdenes de Compra"**
2. Haz clic en él
3. Se abrirá la ventana del módulo

---

## 🎯 Interfaz Principal

### Elementos Principales:

**1. Tabla de Órdenes/Compras**
- Número de orden
- Proveedor
- Fecha
- Estado (Pendiente/Recibida/Completada)
- Monto total

**2. Pestaña de Recepción**
- Registra entrada de productos
- Valida cantidades
- Actualiza inventario

**3. Importación de Datos**
- Cargar desde archivo (Excel, PDF)
- Procesar datos
- Validar e importar

**4. Historial**
- Todas las compras registradas
- Búsqueda y filtrado

---

## ➕ Crear una Orden de Compra

### Paso 1: Haz clic en "+ Nueva Orden"

Se abre un formulario con:
- **Proveedor:** (selector)
- **Fecha de Compra:** (fecha de hoy)
- **Fecha Esperada de Entrega:** (cuándo esperas recibir)
- **Referencia:** (número de factura o referencia)
- **Notas:** (observaciones)

### Paso 2: Selecciona el Proveedor

1. Haz clic en **"Proveedor"**
2. Se abre lista de proveedores
3. Busca o selecciona
4. Si no existe, puedes crear uno

### Paso 3: Agrega Productos

En la sección **"Productos":**

1. Haz clic **"+ Agregar Producto"**
2. Se abre formulario con:
   - Producto (selector)
   - Cantidad
   - Precio unitario
   - Subtotal (automático)
3. Completa y **"Agregar"**

### Paso 4: Revisa Total

Sistema calcula automáticamente:
- Subtotal por producto
- **Total de la orden** (suma de todos)
- **Cantidad de productos**

### Paso 5: Guarda la Orden

Haz clic **"Guardar Orden"**

**Resultado:**
- ✅ Orden creada
- ✅ Estado: PENDIENTE
- ✅ Aparece en tabla
- ✅ Esperando recepción

---

## 📥 Registrar Recepción

### Paso 1: Encuentra la Orden

1. En tabla de órdenes, busca la que llegó
2. O usa búsqueda por número/proveedor

### Paso 2: Haz clic en "Recibir"

Se abre formulario de recepción:
- Productos de la orden
- Cantidad esperada
- Campo para cantidad recibida

### Paso 3: Verifica Cantidades

Para cada producto:

1. **Cantidad Esperada:** (lo que ordenaste)
2. **Cantidad Recibida:** (lo que llegó realmente)
3. **Si hay diferencia:** Anota y guarda

**⚠️ Importante:**
- Si recibiste 190 kg pero ordenaste 200 kg → Registra 190
- Sistema alertará sobre diferencia
- Contacta proveedor si es grande

### Paso 4: Valida Calidad

1. **Campo "Notas":**
   - "Producto OK, calidad excelente"
   - "Algunos daños, 5 kg descartado"
   - "Llegó frío/cálido"

2. Si hay problemas:
   - Anota en "Notas"
   - Guarda evidencia (fotos)
   - Reporta a proveedor

### Paso 5: Guarda Recepción

Haz clic **"Confirmar Recepción"**

**Resultado automático:**
- ✅ Orden estado: RECIBIDA
- ✅ Inventario actualiza (cantidad correcta)
- ✅ Movimiento registrado
- ✅ Costo contabilizado

---

## 📁 Importar desde Archivo

### Paso 1: Prepara tu Archivo

Formato aceptado:
- **Excel (.xlsx):** Recomendado
- **CSV (.csv):** También soportado
- **PDF:** Si contiene tabla

**Estructura necesaria:**
```
Proveedor | Producto | Cantidad | Precio Unit.
XYZ       | Papa     | 100      | 10
ABC       | Chile    | 50       | 20
```

### Paso 2: Abre Importación

1. Botón **"Importar desde Archivo"**
2. Se abre diálogo de selección

### Paso 3: Selecciona el Archivo

1. Busca tu archivo en computadora
2. Selecciona (Excel, CSV o PDF)
3. Haz clic **"Abrir"**

### Paso 4: Valida Datos

Sistema muestra:
- Datos encontrados
- Previsualización
- Avisos de errores (si los hay)

**Si hay errores:**
- Verifica formato
- Corrige en Excel
- Intenta de nuevo

### Paso 5: Confirma Importación

1. Si todo está bien: **"Importar"**
2. Sistema procesa datos
3. Aparecen en tabla de compras

**Resultado:**
- ✅ Compras importadas
- ✅ Inventario actualizado
- ✅ Costos registrados

---

## 🔍 Búsqueda y Filtrado

### Buscar Orden

1. Campo **"Buscar"**
2. Por número, proveedor o producto
3. Se filtra automáticamente

### Filtrar por Estado

1. **Estado Pendiente:** Órdenes no recibidas
2. **Estado Recibida:** Órdenes completas
3. **Todas:** Mostrar todas

### Filtrar por Fecha

1. Campos **"Desde"** y **"Hasta"**
2. Selecciona rango
3. Se muestran compras de ese período

---

## 📊 Ver Historial y Reportes

### Historial de Compras

1. Pestaña **"Historial"** o **"Reporte"**
2. Muestra todas las compras completadas
3. Por proveedor
4. Por producto
5. Por período

### Análisis de Compras

**Información disponible:**
- Total gastado por proveedor
- Productos más comprados
- Costo promedio
- Frecuencia de compra

---

## 🚨 Solución de Problemas

### "No puedo crear una orden"

**Problema:** Error al guardar

**Soluciones:**
1. Verifica que **seleccionaste un proveedor**
2. Verifica que **agregaste productos**
3. Verifica que **cada producto tenga cantidad > 0**
4. Verifica que **las fechas sean válidas**

---

### "El inventario no actualiza"

**Problema:** Registro compra pero stock no cambia

**Soluciones:**
1. Verifica que **confirmastes la recepción** (no solo crear orden)
2. Verifica que el **estado sea "RECIBIDA"**
3. Actualiza la página
4. Si sigue, contacta soporte

---

## 💡 Tips y Mejores Prácticas

### 📋 Procedimiento Recomendado

```
1. Crear Orden ANTES de comprar
   - Documentas intención
   - Tienes referencia

2. Enviar Orden a proveedor
   - Por email
   - Con detalles claros

3. Esperar confirmación
   - Proveedor confirma
   - Acuerdan fecha entrega

4. Recibir productos
   - Verificar cantidad
   - Verificar calidad

5. Registrar en sistema
   - Recepción en módulo
   - Actualizar inventario
```

---

### 🏭 Gestión de Proveedores

```
✅ RECOMENDADO:
- Tener múltiples proveedores
- Negociar buenos precios
- Evaluar regularmente
- Cambiar si es necesario

❌ EVITAR:
- Depender de un solo proveedor
- Precios sin cuestionar
- Pedir órdenes inconsistentes
```

---

### 📊 Análisis de Compras

```
Mensual:
- Total gastado por proveedor
- Productos comprados
- Costo promedio

Trimestral:
- Proveedores más importantes
- Oportunidades de negociación
- Productos a descontinuar
```

---

## 🔗 Información Adicional

- **Panel de Control:** [Volver a Compras →](index.md)
- **Preguntas Frecuentes:** [Ver FAQ →](faq.md)
- **Referencia Rápida:** [Ver Referencia →](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
