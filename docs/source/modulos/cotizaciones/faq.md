# 📦 Gestionar Compras - Preguntas Frecuentes

## 🚀 Primeros Pasos

### ¿Cuándo usar este módulo?

**Siempre que:**
- Compres productos a un proveedor
- Necesites registrar entrada de inventario
- Quieras historizar tus compras

---

### ¿Debo crear la orden ANTES o DESPUÉS de comprar?

**Lo ideal es ANTES:**

**Ventajas:**
- Documentas intención
- Tienes referencia clara
- Seguimiento más fácil
- Control de inventario

**Pero también puedes:**
- Crear después (si olvidaste)
- Importar desde factura

---

## 📦 Órdenes de Compra

### ¿Quién puede crear órdenes?

**Normalmente:** Administrador o comprador

Si no puedes crear, contacta al administrador para obtener permisos.

---

### ¿Puedo editar una orden?

**Depende del estado:**

| Estado | Puedo Editar |
|:---|:---:|
| Pendiente | ✅ Sí |
| Recibida | ⚠️ Parcialmente |
| Completada | ❌ No |

---

### ¿Qué hago si cometí error en la orden?

**Opciones:**

**1. Si aún es Pendiente:**
- Edita directamente
- Cambia cantidad o proveedor

**2. Si ya fue Recibida:**
- Contacta administrador
- Que revise y corrija

**3. Si quieres cancelar:**
- Elimina la orden (si sistema permite)
- O crea una nueva con datos correctos

---

## 📥 Recepción

### ¿Cuándo debo registrar recepción?

**Inmediatamente después de recibir los productos.**

Importante para:
- Actualizar inventario correctamente
- Registrar fecha real de llegada
- Validar cantidad

---

### ¿Qué pasa si recibí menos de lo esperado?

**Registro correctamente:**

1. Cantidad Esperada: 100 kg
2. Cantidad Recibida: 90 kg
3. Diferencia: -10 kg (falta)

Sistema registra discrepancia y alerta.

**Acción:**
- Contacta proveedor
- Reclama los 10 kg faltantes
- Documenta incidente

---

### ¿Qué pasa si la calidad no es buena?

**Registra en "Notas":**
- "Algunos productos dañados"
- "Llegó con golpes"
- "No cumple calidad estándar"

**Acción:**
- Devolución si es graves
- Descuento si es menor
- Cambiar proveedor si es frecuente

---

## 📁 Importación

### ¿Qué formatos acepta la importación?

**Recomendados:**
- Excel (.xlsx) ← Mejor opción
- CSV (.csv)
- PDF con tabla

---

### ¿Cuál es el formato correcto para Excel?

**Estructura necesaria:**

| Proveedor | Producto | Cantidad | Precio |
|:---|:---|---:|---:|
| XYZ | Papa Blanca | 100 | 10 |
| XYZ | Chile Serrano | 50 | 20 |
| ABC | Limón | 30 | 5 |

---

### ¿Puedo importar sin crear orden primero?

**Sí.** Importación crea todo automáticamente:
- Órdenes
- Líneas de productos
- Actualiza inventario

---

### ¿Qué pasa si hay errores en el archivo?

**Sistema muestra:**
- Errores encontrados
- Línea del problema
- Sugerencia de corrección

**Solución:**
1. Corrige en Excel
2. Guarda
3. Intenta importar de nuevo

---

## 💰 Costos

### ¿Cómo se calcula el costo total?

```
Costo Total = Cantidad × Precio Unitario

Ejemplo:
100 kg × $10/kg = $1,000
```

Sistema calcula automáticamente.

---

### ¿Puedo cambiar el precio después?

**No en la compra registrada.**

Pero puedes:
- Crear nueva orden con precio correcto
- Si es error grande, contactar administrador

---

## 🔍 Búsqueda

### ¿Cómo busco una compra específica?

**Tres formas:**

1. **Por Número:** Si recuerdas el #
2. **Por Proveedor:** Busca "XYZ"
3. **Por Producto:** Busca "Papa"

Sistema filtra automáticamente.

---

## 🚨 Problemas Comunes

### "No puedo crear orden porque no aparecen proveedores"

**Solución:**
1. ¿Existen proveedores en el sistema?
2. Si no, debes crearlos primero
3. Ve a módulo de Proveedores
4. Crea los necesarios
5. Vuelve a crear orden

---

### "El inventario se duplicó"

**Razón probable:** Registraste recepción dos veces

**Solución:**
1. Contacta administrador
2. Que verifique historial
3. Que corrija entrada duplicada

---

### "Importé datos incorrectos"

**Soluciones:**

**Si acabas de importar:**
- Contacta administrador
- Que revierta la importación

**Si fue hace tiempo:**
- Crea ajustes manuales
- Registra diferencias

---

## 💡 Tips Profesionales

### 📋 Flujo Eficiente

```
1. Crear Orden (documentar intención)
2. Enviar a Proveedor (confirmar)
3. Esperar Confirmación
4. Recibir Productos
5. Registrar Recepción (actualiza inventario)
6. Pagar (cuando corresponda)
7. Archivar (para referencia futura)
```

---

### 🏭 Gestión Inteligente

```
Proveedores:
- Tener múltiples
- Comparar precios
- Evaluar calidad
- Cambiar si es necesario

Historial:
- Revisar mensualmente
- Analizar tendencias
- Optimizar órdenes
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
