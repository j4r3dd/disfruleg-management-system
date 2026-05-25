# 👥 Gestionar Clientes - Guía Completa

## 📍 Acceder al Módulo

### Paso 1: Abre BodegaDisfruleg
1. Inicia sesión con tu usuario
2. Visualizarás el panel principal

### Paso 2: Navega a Gestionar Clientes
1. En el menú principal, busca **"Gestionar Clientes"** o **"Clientes"**
2. Haz clic en él
3. Se abrirá la ventana del módulo

**Nota:** Debes estar autenticado para usar el módulo.

---

## 🎯 Interfaz Principal

### Elementos Principales:

**1. Pestaña de Tipos de Cliente**
- Crear y gestionar tipos de cliente
- Asignar porcentajes de descuento

**2. Pestaña de Grupos**
- Crear y gestionar grupos
- Asignar tipos de cliente a grupos

**3. Pestaña de Clientes**
- Crear, editar y eliminar clientes
- Asignar clientes a grupos
- Información de contacto y fiscal

**4. Campo de Búsqueda**
- Busca clientes por nombre
- Filtra rápidamente

---

## 🏷️ Gestionar Tipos de Cliente

### ¿Por Qué Crear Tipos de Cliente?

Los tipos definen descuentos automáticos. Ejemplo:
- "Mayorista" = 15% descuento
- "Minorista" = 5% descuento
- "Empresa" = 10% descuento

### Paso 1: Accede a Tipos de Cliente

1. En la ventana principal, haz clic en la pestaña **"Tipos de Cliente"**

### Paso 2: Crear un Nuevo Tipo

1. Haz clic en **"+ Nuevo Tipo"** o **"Crear"**
2. Se abre un formulario con:
   - **Nombre del Tipo:** (ej: "Mayorista")
   - **Descuento (%):** (ej: 15)
3. Haz clic **"Guardar"**

### Paso 3: Editar un Tipo Existente

1. En la tabla, haz clic en el tipo a editar
2. Se abre el formulario con los datos
3. Modifica los valores
4. Haz clic **"Actualizar"**

### Paso 4: Eliminar un Tipo

1. Selecciona el tipo en la tabla
2. Haz clic en **"Eliminar"** o **"Borrar"**
3. Se pedirá confirmación
4. **IMPORTANTE:** No puedes eliminar tipos que están siendo usados

**⚠️ Restricción:** Si un tipo está asignado a un grupo, no se puede eliminar.

---

## 📁 Gestionar Grupos

### ¿Por Qué Crear Grupos?

Los grupos organizan clientes por categoría. Ejemplo:
- "Zona Centro"
- "Zona Periférica"
- "Clientes VIP"
- "Restaurantes"

### Paso 1: Accede a Grupos

1. En la ventana principal, haz clic en la pestaña **"Grupos"**

### Paso 2: Crear un Nuevo Grupo

1. Haz clic en **"+ Nuevo Grupo"** o **"Crear"**
2. Se abre un formulario con:
   - **Clave del Grupo:** (ej: "ZONA_CENTRO", único)
   - **Descripción:** (ej: "Clientes de la zona centro de la ciudad")
   - **Tipo de Cliente:** (selector desplegable)
3. Haz clic **"Guardar"**

**Nota:** La clave debe ser única (no puede repetirse).

### Paso 3: Editar un Grupo

1. En la tabla, haz clic en el grupo a editar
2. Se abre el formulario
3. Modifica los valores
4. Haz clic **"Actualizar"**

### Paso 4: Eliminar un Grupo

1. Selecciona el grupo en la tabla
2. Haz clic en **"Eliminar"** o **"Borrar"**
3. Se pedirá confirmación

**⚠️ Restricción:** Si hay clientes asignados al grupo, no se puede eliminar.

---

## 👤 Gestionar Clientes

### Paso 1: Accede a Clientes

1. En la ventana principal, haz clic en la pestaña **"Clientes"**

### Paso 2: Crear un Nuevo Cliente

1. Haz clic en **"+ Nuevo Cliente"** o **"Crear"**
2. Se abre un formulario con:

**Información Obligatoria:**
- **Nombre del Cliente:** (ej: "Mercado Los Mangos")
- **Grupo:** (selector de grupos existentes)

**Información Opcional:**
- **Teléfono:** (ej: "555-1234")
- **Email:** (ej: "contacto@mercado.com")
- **RFC:** (ej: "RFC123456ABC")
- **Razón Social:** (nombre legal para facturas)
- **Régimen Fiscal:** (ej: "PFF" o "Persona Moral")
- **Código Postal:** (ej: "28001")
- **Dirección Fiscal:** (dirección completa)
- **Notas:** (observaciones personalizadas)

3. Rellena los campos necesarios
4. Haz clic **"Guardar"**

**💡 Tip:** Los campos opcionales pueden dejarse en blanco si no los necesitas aún.

### Paso 3: Editar un Cliente

1. En la tabla, busca el cliente (usa el buscador si es necesario)
2. Haz clic en el cliente a editar
3. Se abre el formulario con los datos actuales
4. Modifica lo que necesites
5. Haz clic **"Actualizar"**

### Paso 4: Cambiar Estado (Activo/Inactivo)

1. En la tabla de clientes, verás una columna "Estado" o "Activo"
2. Haz clic en el cliente
3. Marca/desmarca la opción **"Activo"**
4. Haz clic **"Actualizar"**

**Uso:** Inactivo un cliente cuando ya no compra, pero sin borrarlo del historial.

### Paso 5: Eliminar un Cliente

1. Selecciona el cliente en la tabla
2. Haz clic en **"Eliminar"** o **"Borrar"**
3. Se pedirá confirmación

**⚠️ Restricción:** No puedes eliminar clientes que tienen facturas/recibos.

---

## 🔍 Buscar y Filtrar Clientes

### Búsqueda Rápida

1. En la tabla de clientes, verás un campo **"Buscar"** o **"Search"**
2. Escribe el nombre del cliente
3. La tabla se filtra automáticamente

**Ejemplo:**
- Escribe "mercado" → Aparecen todos los clientes con "mercado" en el nombre

### Filtro por Grupo

Algunos módulos permiten filtrar por grupo:

1. En el selector de filtros, elige un grupo
2. Se muestran solo clientes de ese grupo
3. Haz clic en "Limpiar" para ver todos

---

## 📊 Validaciones

El módulo valida automáticamente:

### Email
- Debe tener formato válido: `usuario@dominio.com`
- Si escribes un email inválido, mostrará error

### RFC
- Formato válido para facturas
- Si escribes RFC inválido, mostrará error

### Campos Obligatorios
- Nombre del Cliente: **OBLIGATORIO**
- Grupo: **OBLIGATORIO**
- Otros campos: opcionales

---

## 🎬 Flujo de Trabajo Completo

### Escenario: Dar de Alta un Nuevo Cliente Mayorista

**Paso 1: Verificar que existe el tipo**
1. Abre pestaña "Tipos de Cliente"
2. ¿Existe "Mayorista"? Si no, créalo con 15% descuento

**Paso 2: Verificar que existe el grupo**
1. Abre pestaña "Grupos"
2. ¿Existe "Zona Centro"? Si no, créalo y asigna tipo "Mayorista"

**Paso 3: Crear el cliente**
1. Abre pestaña "Clientes"
2. Haz clic "+ Nuevo Cliente"
3. Completa:
   - Nombre: "Mercado Los Mangos"
   - Grupo: "Zona Centro" (automáticamente hereda descuento 15%)
   - Teléfono: "555-1234"
   - Email: "contacto@mercado.com"
   - RFC: "RFC123456ABC"
4. Haz clic "Guardar"

**Paso 4: Verificar**
1. El cliente aparece en la tabla
2. Cuando lo uses en una cotización, se aplicará el descuento 15%

---

## 🚨 Solución de Problemas

### "No puedo crear un cliente"

**Problema:** Aparece error al guardar

**Soluciones:**
1. Verifica que el **nombre no esté vacío**
2. Verifica que **seleccionaste un grupo**
3. Si el email no es válido, déjalo vacío o corrige formato
4. Verifica que el grupo existe (si no, créalo primero)

---

### "No puedo eliminar un cliente"

**Problema:** No me deja eliminar

**Razón:** El cliente tiene facturas/recibos asociados

**Soluciones:**
1. En lugar de eliminar, **desactívalo** (marcar como inactivo)
2. Si REALMENTE necesitas eliminarlo, borra los recibos primero
3. Mejor opción: mantén un historial, solo desactiva

---

### "¿Por qué no puedo eliminar un grupo?"

**Problema:** El botón de eliminar no funciona

**Razón:** Hay clientes asignados a ese grupo

**Soluciones:**
1. Mueve los clientes a otro grupo primero
2. Luego elimina el grupo
3. O mejor: solo desactívalo en lugar de eliminarlo

---

### "No me deja guardar la información fiscal"

**Problema:** RFC o Email rechazados

**Soluciones:**
1. Verifica el formato del RFC (debe ser válido)
2. Email: debe tener @ y dominio válido
3. Si no sabes el RFC, déjalo en blanco por ahora
4. Puedes actualizar después

---

## 💡 Tips y Mejores Prácticas

### 📋 Organización de Grupos
```
✅ RECOMENDADO:
- "ZONA_NORTE"
- "ZONA_SUR"
- "MAYORISTAS"
- "MINORISTAS"

❌ EVITAR:
- "grupo1", "grupo2" (poco descriptivo)
- Nombres con espacios (usa guiones)
```

### 🏷️ Tipos de Cliente
```
✅ RECOMENDADO:
- "Mayorista" (15%)
- "Minorista" (5%)
- "Empresa" (10%)
- "VIP" (20%)

❌ EVITAR:
- Demasiados tipos
- Descuentos inconsistentes
```

### 👤 Información de Cliente
```
✅ COMPLETA:
- Nombre
- Grupo
- Teléfono
- Email
- RFC
- Dirección fiscal

❌ INCOMPLETA:
- Solo nombre
- Sin contacto
- Sin información fiscal
```

---

## 🔗 Información Adicional

- **Panel de Control:** [Volver a Clientes →](index.md)
- **Preguntas Frecuentes:** [Ver FAQ →](faq.md)
- **Referencia Rápida:** [Ver Referencia →](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
