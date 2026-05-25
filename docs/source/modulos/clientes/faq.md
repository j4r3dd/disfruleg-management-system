# 👥 Gestionar Clientes - Preguntas Frecuentes (FAQ)

## 🚀 Primeros Pasos

### ¿Cómo accedo al módulo de Clientes?

1. Abre BodegaDisfruleg
2. Inicia sesión
3. En el menú principal, busca **"Gestionar Clientes"** o **"Clientes"**
4. Se abrirá la ventana

---

### ¿En qué orden debo crear las cosas?

**El orden correcto es:**

1. **Primero: Tipos de Cliente** (ej: Mayorista, Minorista)
2. **Segundo: Grupos** (ej: Zona Centro, Zona Sur)
3. **Tercero: Clientes** (asigna a grupo y tipo)

**Por qué:** Un grupo necesita un tipo, y un cliente necesita un grupo.

---

### ¿Cuál es la diferencia entre Tipo y Grupo?

| Tipo de Cliente | Grupo |
|:---|:---|
| Define **descuentos** | Define **categoría/organización** |
| "Mayorista" = 15% dto | "Zona Centro" = ubicación |
| Se aplica automáticamente | Solo es una etiqueta |
| Ejemplo: Mayorista, Minorista | Ejemplo: Restaurantes, Tiendas |

---

## 📋 Tipos de Cliente

### ¿Cuántos tipos debo crear?

Depende de tu negocio. Ejemplos:

**Negocio Simple:**
- Solo 1 tipo: "Cliente Estándar"

**Negocio Mediano:**
- "Mayorista" (15%)
- "Minorista" (0%)

**Negocio Complejo:**
- "Mayorista" (15%)
- "Minorista" (5%)
- "Empresa" (10%)
- "VIP" (20%)

---

### ¿Puedo cambiar el descuento después?

**Sí.** Pero afectará a futuras cotizaciones/recibos, no a los pasados.

Pasos:
1. Abre el tipo
2. Edita el porcentaje
3. Guarda
4. Listo

---

### ¿Qué pasa si intento eliminar un tipo?

**Respuesta:** No puedes si está asignado a un grupo.

**Solución:**
1. Quita el tipo de todos los grupos
2. Luego elimina el tipo

---

## 📁 Grupos

### ¿Cuántos grupos debo crear?

Depende de cómo quieras organizar:

**Por zona geográfica:**
- Zona Norte
- Zona Sur
- Zona Centro

**Por tipo de cliente:**
- Mayoristas
- Minoristas
- Restaurantes

**Mixto:**
- Mayoristas Zona Centro
- Minoristas Zona Sur
- Restaurantes VIP

Crea los que necesites.

---

### ¿Puedo tener clientes sin grupo?

**No.** Cada cliente **DEBE** pertenecer a un grupo.

Si no tienes categoría, crea un grupo llamado "General" o "Sin Categoría".

---

### ¿Puedo mover un cliente de grupo?

**Sí.** 

Pasos:
1. Abre el cliente
2. Cambia el campo "Grupo"
3. Selecciona nuevo grupo
4. Guarda

El cliente se moverá al nuevo grupo y adoptará el tipo de cliente del nuevo grupo.

---

### ¿Qué pasa si elimino un grupo con clientes?

**Respuesta:** No puedes. Sistema bloqueará la eliminación.

**Solución:**
1. Mueve todos los clientes a otro grupo
2. Luego elimina el grupo vacío

---

## 👤 Clientes

### ¿Cuál es la información obligatoria?

**OBLIGATORIO:**
- ✅ Nombre del cliente
- ✅ Grupo

**OPCIONAL:**
- Teléfono
- Email
- RFC
- Razón social
- Dirección fiscal
- Notas
- Etc.

Puedes agregar información opcional después.

---

### ¿Cómo busco un cliente?

**Opción 1: Campo de búsqueda**
1. En la tabla de clientes
2. Escribe el nombre o parte de él
3. Se filtra automáticamente

**Ejemplo:** Escribe "Mercado" → Aparecen "Mercado Los Mangos", "Mercado Central"

---

### ¿Por qué un cliente aparece inactivo?

**Razón:** Fue marcado como inactivo manualmente.

**Solución:**
1. Abre el cliente
2. Marca la opción "Activo"
3. Guarda

---

### ¿Puedo desactivar un cliente?

**Sí.** Es la mejor opción si ya no compra.

Ventajas de desactivar vs. eliminar:
- ✅ Mantiene el historial
- ✅ No afecta recibos pasados
- ✅ Puedes reactivar después

Pasos:
1. Abre el cliente
2. Desmarca "Activo"
3. Guarda

---

### ¿Por qué no puedo eliminar un cliente?

**Razón:** Tiene recibos/facturas asociados.

**Por qué no se puede:** Afectaría el historial y auditoría contable.

**Soluciones:**
1. **Mejor opción:** Desactiva en lugar de eliminar
2. Si REALMENTE necesitas eliminar: borra primero sus recibos

---

### ¿Cómo agrego información fiscal?

**Pasos:**
1. Abre el cliente
2. En la sección "Información Fiscal":
   - RFC: número de identificación
   - Razón Social: nombre legal
   - Régimen Fiscal: PFF, PM, etc.
   - Código Postal: donde vive
   - Dirección Fiscal: domicilio completo
3. Guarda

Esta info es importante para **generar facturas correctas**.

---

### ¿Cuál es el formato correcto del RFC?

**RFC:**
- Formato: 12 caracteres
- Estructura: 6 letras + 6 números + 2 alfanuméricos
- Ejemplo: `RFC123456ABC`

Si no sabes el RFC, deja el campo vacío. Puedes agregarlo después.

---

### ¿Cuál es el formato correcto del Email?

**Email:**
- Estructura: usuario@dominio.com
- Ejemplos válidos:
  - contacto@empresa.com
  - info@tienda.com.mx
  - ventas@negocio.net

Si escribes formato inválido, el sistema rechazará.

---

## 📊 Descuentos y Tipos

### ¿Cómo se aplican los descuentos?

**Automáticamente:**

1. Cliente "Mercado Los Mangos" está en grupo "Mayoristas"
2. Grupo "Mayoristas" tiene tipo "Mayorista"
3. Tipo "Mayorista" tiene 15% descuento
4. **Resultado:** Al hacer una cotización al cliente, se aplica 15% automáticamente

---

### ¿Puedo dar descuentos individuales?

**Eso depende del módulo de Cotizaciones/Recibos.**

En Clientes solo defines descuentos por tipo.

Si necesitas descuentos especiales por cliente, probablemente sea en Cotizaciones.

---

### ¿Qué pasa si cambio el descuento de un tipo?

**Futuras cotizaciones:** Aplican nuevo descuento

**Cotizaciones pasadas:** No cambian (historial se mantiene)

---

## 🔍 Búsqueda y Filtrado

### ¿Puedo filtrar por estado (activo/inactivo)?

Depende de la interfaz. Algunas opciones:

- Checkbox "Mostrar inactivos"
- Botón filtro "Por estado"
- Columna "Estado" ordenable

Si no ves esta opción, contacta soporte.

---

### ¿Puedo filtrar por grupo?

Algunos módulos permiten:

1. Selector de grupo en la barra de filtros
2. Selecciona un grupo
3. Se muestran solo clientes de ese grupo

Si no está disponible, usa búsqueda por nombre.

---

## 🚨 Problemas Comunes

### "No puedo crear un cliente porque dice que el nombre está vacío"

**Solución:**
- El nombre **DEBE** tener al menos 1 carácter
- No puedes dejar en blanco
- Escribe: "Cliente Nuevo" o algo descriptivo

---

### "Dice que el grupo no existe"

**Problema:** Seleccionaste un grupo que fue eliminado

**Solución:**
1. Crea un nuevo grupo primero
2. Luego intenta crear el cliente
3. O edita cliente existente y cambia a otro grupo

---

### "El RFC/Email no se guarda"

**Problema:** Formato inválido

**Soluciones:**
1. **RFC:** Verifica formato (12 caracteres)
2. **Email:** Verifica que tenga @ y dominio válido
3. Si no sabes, déjalo vacío por ahora
4. Puedes actualizar después

---

### "¿Por qué se duplican clientes?"

**Razón común:** Creaste el mismo cliente dos veces sin darte cuenta

**Solución:**
1. Usa búsqueda antes de crear
2. Verifica que no exista
3. Si ya existe duplicado, elimina uno

---

## 💡 Tips Profesionales

### 📋 Estructura de Grupos Recomendada

```
✅ PARA TIENDA:
- Mayoristas
- Minoristas
- Consumidor Final

✅ PARA RESTAURANTE:
- Proveedores Locales
- Proveedores Regionales
- Distribuidoras Nacionales

✅ PARA DISTRIBUIDORA:
- Zona Centro (Mayorista)
- Zona Norte (Minorista)
- Zona Sur (Minorista)
- Clientes VIP
```

---

### 👤 Completar Información Gradualmente

No necesitas toda la información al crear un cliente:

**Mínimo (crear):**
- Nombre
- Grupo

**Después (actualizar):**
- Teléfono
- Email
- RFC
- Dirección

Puedes ir completando conforme obtengas la información.

---

### 🏷️ Mantén Descuentos Simples

**Recomendado:**
- Mayorista: 15%
- Minorista: 5%
- Empresa: 10%

**No recomendado:**
- 47 tipos diferentes
- Descuentos raros (7%, 11%)
- Complejidad innecesaria

---

## 🔗 Enlaces Útiles

- [📖 Guía Completa](guia.md)
- [📺 Videos](videos.md)
- [⚡ Referencia Rápida](rapida.md)
- [👥 Volver al Índice](index.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
