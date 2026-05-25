# 💰 Gestionar Precios - Guía Completa

## 📍 Acceder al Módulo

### Paso 1: Abre BodegaDisfruleg
1. Inicia sesión con tu usuario
2. Visualizarás el panel principal

### Paso 2: Navega a Gestionar Precios
1. En el menú principal, busca **"Gestionar Precios"** o **"Precios"**
2. Haz clic en él
3. Se abrirá la ventana del módulo

---

## 🎯 Interfaz Principal

### Elementos Principales:

**1. Tabla de Productos**
- Lista de todos los productos
- Precio base y márgenes
- Costo del producto

**2. Pestaña de Precios por Grupo**
- Precios diferenciados por grupo de cliente
- Ajustes y descuentos
- Bloqueos

**3. Campo de Búsqueda**
- Busca productos por nombre
- Filtra rápidamente

**4. Botones de Acción**
- Editar precio
- Bloquear/desbloquear
- Aplicar ajuste

---

## 💲 Establecer Precios Base

### Paso 1: Encuentra el Producto

1. En la tabla de productos, busca el producto
2. O usa el campo **"Buscar"** para filtrarlo

### Paso 2: Edita el Precio

1. Haz clic en el producto o en el botón **"Editar"**
2. Se abre un formulario con:
   - **Nombre del Producto**
   - **Costo:** costo de adquisición
   - **Precio Base:** precio de venta por defecto
   - **Margen (%):** se calcula automáticamente

3. Modifica el precio
4. Haz clic **"Guardar"**

### Paso 3: Verifica Margen

El margen se calcula automáticamente:
```
Margen = (Precio - Costo) / Precio * 100%
```

**Ejemplo:**
- Costo: $10
- Precio: $25
- Margen: (25-10)/25 * 100 = 60%

---

## 📊 Precios por Grupo de Cliente

### ¿Por Qué Usar Precios por Grupo?

Diferentes clientes pagan diferentes precios:
- **Mayoristas:** Descuento 40%
- **Minoristas:** Descuento 10%
- **VIP:** Descuento 20%

### Paso 1: Accede a Precios por Grupo

1. Haz clic en la pestaña **"Precios por Grupo"**
2. O selecciona un producto en la tabla principal

### Paso 2: Crear Precio para Grupo

1. Haz clic en **"+ Nuevo Precio"** o **"Agregar Grupo"**
2. Se abre un formulario con:
   - **Producto:** (automático o selector)
   - **Grupo:** (selector de grupos)
   - **Precio para Grupo:** (ej: $15)
   - **Descuento (%):** (opcional)
   - **Notas:** (opcional)

3. Completa los campos
4. Haz clic **"Guardar"**

### Paso 3: Edita Precio de Grupo

1. En la tabla, haz clic en el precio a editar
2. Modifica los valores
3. Haz clic **"Actualizar"**

### Paso 4: Elimina Precio de Grupo

1. Selecciona en la tabla
2. Haz clic **"Eliminar"**
3. Confirma

---

## 🔒 Bloquear Precios

### ¿Cuándo Bloquear?

Bloquea un precio cuando:
- Es un precio negociado especialmente
- No debe cambiar sin aprobación
- Es crítico para tu negocio

### Paso 1: Bloquea un Precio

1. En la tabla, selecciona el precio
2. Haz clic en **"Bloquear"** o el icono de candado
3. **Se pedirá una razón/motivo:**
   - "Cliente especial, no modificar"
   - "Precio negociado, requiere aprobación"
   - Etc.

4. Haz clic **"Confirmar"**

### Paso 2: Intenta Cambiar Precio Bloqueado

1. Intenta editar el precio
2. Sistema mostrará advertencia:
   - **"Este precio está bloqueado"**
   - Motivo del bloqueo
   - Quién lo bloqueó

3. Para cambiar:
   - Primero debes **desbloquear**
   - Requiere aprobación (según configuración)

### Paso 3: Desbloquea un Precio

1. Selecciona el precio bloqueado
2. Haz clic en **"Desbloquear"**
3. Se pedirá razón:
   - "Aprobado cambio de precio"
   - "Cliente ya no es VIP"
   - Etc.

4. Haz clic **"Confirmar"**

---

## 📈 Ajustes y Cambios Masivos

### Aplicar Ajuste a Todos los Precios

Aumentar o disminuir todos los precios de una vez:

1. Haz clic en **"Ajuste Masivo"** o **"Aplicar Ajuste"**
2. Se abre un formulario con:
   - **Tipo de Ajuste:** Aumento o Reducción
   - **Porcentaje (%):** ej: 5 (para 5% de aumento)
   - **Productos Afectados:** Todos o seleccionados
   - **Grupos Afectados:** Todos o seleccionados

3. **IMPORTANTE:** Revisa qué se va a cambiar
4. Haz clic **"Aplicar"**

**⚠️ Advertencia:** Esto afecta múltiples precios. Verifica bien antes de aplicar.

---

## 🔍 Búsqueda y Filtrado

### Busca por Nombre

1. Campo **"Buscar"** en la tabla
2. Escribe el nombre del producto
3. Se filtra automáticamente

### Filtra por Margen

Algunos módulos permiten:

1. Filtro **"Por Margen"**
2. Selecciona rango: 0-20%, 20-50%, 50%+
3. Se muestran solo productos en ese rango

### Filtra por Grupo

1. Selector de grupo en filtros
2. Se muestran precios para ese grupo
3. "Mostrar todos" para ver todas las combinaciones

---

## 📊 Análisis de Márgenes

### Ver Márgenes

En la tabla principal, verás columna **"Margen %"**

**Interpretación:**
- ✅ **>50%:** Margen excelente
- ⚠️ **20-50%:** Margen aceptable
- ❌ **<20%:** Margen bajo, revisar

### Productos Rentables

Busca productos con:
- Margen >40%
- Volumen de ventas alto
- Costo bajo

**Acción:** Prioriza estos productos en promociones

### Productos No Rentables

Busca productos con:
- Margen <20%
- Volumen bajo
- Competencia fuerte

**Acción:** Considera eliminar o aumentar precio

---

## 🚨 Solución de Problemas

### "No puedo cambiar un precio"

**Problema:** El precio está bloqueado

**Solución:**
1. Verifica que no esté bloqueado
2. Si lo está, desbloquéalo primero
3. Luego puedes editar
4. Vuelve a bloquearlo si es necesario

---

### "El margen es muy bajo"

**Problema:** Margen <20%, no es rentable

**Soluciones:**
1. Aumenta el precio de venta
2. Negocia mejor costo con proveedor
3. Considera eliminar producto
4. O acepta bajo margen por volumen

---

### "Cambié un precio y afectó muchas ventas"

**Problema:** Cambio se aplicó retroactivamente

**Solución:**
- En BodegaDisfruleg, cambios de precio solo afectan **futuras** cotizaciones
- Las cotizaciones existentes mantienen su precio original
- Verifica antes de aplicar cambios masivos

---

## 💡 Tips y Mejores Prácticas

### 📋 Estructura de Precios Recomendada

```
✅ RECOMENDADO:
1. Precio Base Mayorista (márgenes bajos)
2. Precio Base Minorista (márgenes altos)
3. Precios Especiales VIP (negociados)

❌ EVITAR:
- Demasiadas variaciones por grupo
- Cambios frecuentes sin razón
- Márgenes inconsistentes
```

### 🔒 Bloqueo Estratégico

```
✅ BLOQUEA:
- Precios negociados especialmente
- Precios con márgenes críticos
- Precios de clientes VIP importantes

❌ NO BLOQUEES:
- Todos los precios (reduces flexibilidad)
- Precios de oferta (que cambían frecuentemente)
```

### 💹 Análisis Regular

```
✅ REVISA MENSUALMENTE:
- Márgenes por producto
- Productos con margen bajo
- Cambios de costo que requieren ajuste
- Comparativa con competencia

❌ EVITA:
- Cambios sin análisis
- Aumentos sin justificación
- Ignorar márgenes bajos
```

---

## 🔗 Información Adicional

- **Panel de Control:** [Volver a Precios →](index.md)
- **Preguntas Frecuentes:** [Ver FAQ →](faq.md)
- **Referencia Rápida:** [Ver Referencia →](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
