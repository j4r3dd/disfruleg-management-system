# 💳 Gestionar Deudas - Guía Completa

## 📍 Acceder al Módulo

### Paso 1: Abre BodegaDisfruleg
1. Inicia sesión con tu usuario
2. Visualizarás el panel principal

### Paso 2: Navega a Gestionar Deudas
1. En el menú principal, busca **"Gestionar Deudas"**, **"Cobranza"** o **"Cartera"**
2. Haz clic en él
3. Se abrirá la ventana del módulo

---

## 🎯 Interfaz Principal

### Elementos Principales:

**1. Dashboard de Cartera**
- Total adeudado
- Deudas vencidas
- Número de deudores
- Margen de morosidad

**2. Tabla de Deudas**
- Cliente
- Monto adeudado
- Fecha de vencimiento
- Estado (Pendiente/Vencida/Pagada)

**3. Filtros**
- Por estado (pendiente, vencida)
- Por cliente
- Por rango de fechas

**4. Botones de Acción**
- Registrar Deuda
- Registrar Pago
- Recordatorio

---

## ➕ Registrar una Deuda

### Paso 1: Haz clic en "+ Registrar Deuda"

Se abre un formulario con:
- **Cliente:** (selector)
- **Monto:** (cantidad adeudada)
- **Fecha de Vencimiento:** (cuándo debe pagar)
- **Descripción:** (opcional, referencia a factura)
- **Notas:** (opcional, observaciones)

### Paso 2: Selecciona el Cliente

1. Haz clic en **"Cliente"**
2. Se abre lista de clientes
3. Busca o desplázate
4. Selecciona el cliente

### Paso 3: Ingresa el Monto

1. Campo **"Monto"**
2. Escribe cantidad (ej: 10000)
3. Sistema valida que sea > 0

### Paso 4: Ingresa Fecha de Vencimiento

1. Haz clic en **"Fecha de Vencimiento"**
2. Se abre calendario
3. Selecciona fecha en que debe pagar
4. Haz clic OK

### Paso 5: Guarda la Deuda

Haz clic **"Guardar"** o **"Registrar Deuda"**

**Resultado:**
- ✅ Deuda registrada
- ✅ Aparece en tabla como "Pendiente"
- ✅ Recordatorio automático en fecha

---

## 💵 Registrar un Pago

### Paso 1: Haz clic en "Registrar Pago"

Se abre un formulario con:
- **Cliente:** (selector)
- **Deuda:** (selector de deudas pendientes)
- **Monto Pagado:** (cuánto pagó)
- **Fecha de Pago:** (cuándo pagó)
- **Método:** (efectivo, cheque, transferencia)

### Paso 2: Selecciona Cliente

1. Haz clic en **"Cliente"**
2. Selecciona el cliente que pagó

### Paso 3: Selecciona la Deuda

1. Se actualizan deudas pendientes de ese cliente
2. Selecciona la deuda que está pagando

### Paso 4: Ingresa Monto Pagado

1. Campo **"Monto Pagado"**
2. Escribe lo que pagó (ej: 5000 para pago parcial)

**⚠️ Importante:**
- Si paga todo → Ingresa monto total
- Si paga parcial → Ingresa monto parcial
- Sistema ajusta la deuda automáticamente

### Paso 5: Guarda el Pago

Haz clic **"Guardar Pago"**

**Resultado:**
- ✅ Pago registrado
- ✅ Deuda disminuye
- ✅ Si paga todo → Estado: PAGADA
- ✅ Si paga parcial → Sigue pendiente con monto reducido

---

## 📊 Ver Estado de Deudas

### Tabla Principal

Muestra todas las deudas con:

| Columna | Información |
|:---|:---|
| Cliente | Quién debe |
| Monto Adeudado | Cuánto falta pagar |
| Vencimiento | Cuándo debe pagar |
| Estado | Pendiente/Vencida/Pagada |
| Días Vencida | Si pasó la fecha |

### Colores por Estado:

- 🟢 **Verde:** Pendiente (no vencida)
- 🟡 **Amarillo:** Próxima a vencer (< 5 días)
- 🔴 **Rojo:** Vencida (pasó la fecha)
- ⚫ **Gris:** Pagada (completada)

---

## 🔍 Filtrado y Búsqueda

### Filtrar por Estado

1. Botón o checkbox: **"Mostrar Pendientes"**, **"Mostrar Vencidas"**
2. Se actualiza tabla
3. Se muestran solo deudas en ese estado

### Buscar por Cliente

1. Campo **"Buscar Cliente"**
2. Escribe nombre
3. Se filtra automáticamente

### Ver Deudas Vencidas

1. Pestaña: **"Deudas Vencidas"** o filtro
2. Se muestran solo las vencidas
3. Prioridad para cobranza

---

## ⏰ Recordatorios

### Automáticos

El sistema genera automáticamente:
- **3 días antes:** Recordatorio de próximo vencimiento
- **Fecha vencimiento:** Alerta de vencimiento
- **7 días después:** Recordatorio urgente
- **30 días después:** Alerta crítica

### Manuales

Para enviar recordatorio especial:

1. Selecciona la deuda
2. Haz clic **"Enviar Recordatorio"**
3. Se abre plantilla de mensaje
4. Ajusta si es necesario
5. Envía al cliente (email, SMS)

---

## 📈 Análisis de Cartera

### Dashboard Muestra:

**Total Adeudado**
- Suma de todas las deudas pendientes
- Ejemplo: $150,000

**Deudas Vencidas**
- Cuántas están vencidas
- Ejemplo: 15 deudas vencidas

**Porcentaje de Morosidad**
- % de lo adeudado que está vencido
- Ejemplo: 45% está vencido

**Días Promedio de Mora**
- Cuántos días en promedio están vencidas
- Ejemplo: 20 días de promedio

---

## 🚨 Solución de Problemas

### "No puedo registrar una deuda"

**Problema:** Error al guardar

**Soluciones:**
1. Verifica que **seleccionaste un cliente**
2. Verifica que **ingresaste un monto válido** (> 0)
3. Verifica que **seleccionaste una fecha**
4. Si cliente no existe, créalo primero

---

### "El cliente pagó pero sigue aparecer como deudor"

**Problema:** Deuda no actualiza

**Soluciones:**
1. Verifica que registraste el **pago correctamente**
2. Verifica que ingresaste el **monto correcto**
3. Actualiza la pantalla (F5)
4. Si sigue, contacta administrador

---

## 💡 Tips y Mejores Prácticas

### 📋 Política de Crédito

```
✅ RECOMENDADO:
- Crédito máximo: 30 días
- Mayoristas: Crédito más largo
- Minoristas: Crédito más corto
- Clientes nuevos: Contado primero
- Luego de 3 pagos puntuales: extender crédito
```

---

### ⏰ Seguimiento

```
Diario:
- Revisar deudas vencidas
- Preparar cobros del día

Semanal:
- Enviar recordatorios
- Registrar pagos
- Actualizar cartera

Mensual:
- Análisis de morosidad
- Reporte de deudores
- Decisiones de crédito
```

---

### 🎯 Gestión de Riesgo

```
Cliente con 60+ días vencido:
1. Llamada personal
2. Negociación de pago
3. Plan de pagos si es necesario
4. Si no paga: suspender crédito
```

---

## 🔗 Información Adicional

- **Panel de Control:** [Volver a Deudas →](index.md)
- **Preguntas Frecuentes:** [Ver FAQ →](faq.md)
- **Referencia Rápida:** [Ver Referencia →](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
