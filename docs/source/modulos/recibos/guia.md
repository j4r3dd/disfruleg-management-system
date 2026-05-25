# 📝 Generar Recibos - Guía COMPLETA y DETALLADA

## 📍 Acceder al Módulo

### Paso 1: Abre BodegaDisfruleg
1. Inicia sesión con tu usuario
2. Visualizarás el panel principal

### Paso 2: Navega a Generar Recibos
1. En el menú principal, busca **"Generar Recibos"**, **"Crear Factura"** o **"Punto de Venta"**
2. Haz clic en él
3. Se abrirá la interfaz de recibos
4. **⏱️ Espera a que cargue** (puede tardar algunos segundos con muchos productos)

---

## 🎯 Interfaz Principal - EXPLICADA COMPLETAMENTE

### PANEL IZQUIERDO: Selección de Cliente (CRÍTICO)

```
┌─────────────────────────────────┐
│ GRUPO DE CLIENTE                │
│ [Seleccionar Grupo ▼]           │
│                                 │
│ CLIENTE                         │
│ [Seleccionar Cliente ▼]         │
│                                 │
│ ℹ️ Información del Cliente      │
│ • Crédito disponible: $XXX      │
│ • Descuentos: 15%               │
│ • Última compra: 05/12/2025     │
└─────────────────────────────────┘
```

**¿Qué ocurre aquí?**
1. **Selecciona GRUPO primero** (Mayorista, Minorista, VIP)
   - El grupo determina el listado de clientes
   - El grupo determina descuentos automáticos
   
2. **Luego selecciona CLIENTE específico**
   - Si es cliente nuevo: "Venta General" o registra primero
   - El cliente determina el precio de los productos
   - El cliente determina los descuentos personales

### PANEL CENTRAL: Búsqueda y Agregar Productos

```
┌─────────────────────────────────────────────────┐
│ BÚSQUEDA: [Escribe aquí]                        │
│                                                 │
│ 🔍 Resultados (mostrados dinámicamente)         │
│                                                 │
│ PAPA BLANCA (100 kg)  $15/kg  [+ Agregar]      │
│ CHILE SERRANO (50 kg) $20/kg  [+ Agregar]      │
│ LIMÓN (30 kg)         $8/kg   [+ Agregar]      │
└─────────────────────────────────────────────────┘
```

**¿Cómo buscar productos?**
1. Escribe en el campo "BÚSQUEDA"
2. Sistema FILTRA automáticamente mientras escribes
3. Haz clic **[+ Agregar]** en el producto

**⚠️ IMPORTANTE:**
- La búsqueda es EN TIEMPO REAL
- Muestra solo productos con stock disponible
- Muestra el precio EXACTO para ese cliente/grupo

### PANEL DERECHO: Carrito de Compra (LO QUE VA A PAGAR)

```
┌──────────────────────────────────────────┐
│ 🛒 CARRITO                               │
├──────────────────────────────────────────┤
│ PAPA BLANCA                              │
│ • Cantidad: [100] kg                     │
│ • Precio unit: $15                       │
│ • Subtotal: $1,500                       │
│ [Editar] [Eliminar]                      │
├──────────────────────────────────────────┤
│ CHILE SERRANO                            │
│ • Cantidad: [50] kg                      │
│ • Precio unit: $20                       │
│ • Subtotal: $1,000                       │
│ [Editar] [Eliminar]                      │
├──────────────────────────────────────────┤
│ SUBTOTAL:                    $2,500      │
│ DESCUENTO (15%):              -$375      │
│ TOTAL FINAL:                 $2,125      │
│                                          │
│ [PROCESAR PAGO]  [IMPRIMIR]              │
└──────────────────────────────────────────┘
```

---

## 📋 PASO A PASO COMPLETO: Crear Un Recibo

### FASE 1: PREPARACIÓN (30 segundos)

#### Paso 1.1: Selecciona el GRUPO del Cliente
```
Interfaz: [Seleccionar Grupo ▼]
```

**¿Qué significa cada grupo?**
| Grupo | Quién | Descuento | Plazo |
|:---|:---|:---:|:---:|
| **Mayorista** | Mercados, tiendas grandes | 15-20% | 30 días |
| **Minorista** | Pequeñas tiendas, restaurantes | 5-10% | 7-15 días |
| **VIP** | Clientes especiales, amigos | Variable | Variable |
| **Venta General** | Cliente anónimo | 0% | Contado |

**Acción:**
1. Haz clic en el dropdown
2. Selecciona el grupo
3. Sistema actualiza lista de clientes automáticamente

#### Paso 1.2: Selecciona el CLIENTE específico
```
Interfaz: [Seleccionar Cliente ▼]
```

**Después de seleccionar grupo:**
- Sistema muestra SOLO clientes de ese grupo
- Aparece información del cliente (crédito, descuentos)

**Si es cliente nuevo:**
- Selecciona "Venta General" (cliente anónimo)
- O registra al cliente primero en módulo Clientes

**Acción:**
1. Haz clic en dropdown
2. Selecciona cliente
3. **ESPERA 1-2 segundos** a que se actualice

### FASE 2: AGREGAR PRODUCTOS (1-5 minutos)

#### Paso 2.1: Busca el primer producto
```
Interfaz: BÚSQUEDA: [Escribe aquí]
```

**Ejemplo: Buscas Papa Blanca**

1. Haz clic en el campo de búsqueda
2. Escribe: "papa" (o "papa blanca" o "blanca")
3. Sistema filtra automáticamente
4. Ves: "PAPA BLANCA (100 kg) $15/kg"
   - El precio $15 es el de ESE cliente/grupo
   - El 100 kg es el STOCK disponible

#### Paso 2.2: Agrega el producto al carrito
```
Interfaz: PAPA BLANCA (100 kg) $15/kg [+ Agregar]
```

**Al hacer clic en [+ Agregar]:**
1. Abre un diálogo para ingresar cantidad
2. Pide: "¿Cuántos kg deseas agregar?"
3. Ingresas: 100 (cantidad deseada)
4. Haz clic [Agregar]

**Sistema calcula automáticamente:**
- Cantidad: 100 kg
- Precio: $15/kg
- Subtotal: $1,500
- Aparece en el carrito

**⚠️ IMPORTANTE:**
- La cantidad NO puede exceder el stock
- Sistema valida automáticamente
- Si tienes error: te dice cuál es el máximo

#### Paso 2.3: Agrega más productos (si necesita)

Repite proceso:
1. Busca siguiente producto
2. Ingresa cantidad
3. Agrega al carrito

**Puedes agregar ilimitados productos al mismo recibo**

### FASE 3: REVISAR CARRITO (1 minuto)

```
🛒 CARRITO - Verifica ANTES de pagar:

PAPA BLANCA
  Cantidad: 100 kg
  Precio: $15/kg
  Subtotal: $1,500
  [Editar] [Eliminar]
  
CHILE SERRANO
  Cantidad: 50 kg
  Precio: $20/kg
  Subtotal: $1,000
  [Editar] [Eliminar]

─────────────────────────
SUBTOTAL:       $2,500
DESCUENTO:        -$375  (15% mayorista)
IMPUESTOS:            $0  (si aplica)
─────────────────────────
TOTAL A PAGAR:  $2,125
```

**Checklist de revisión:**

```
✅ ¿Cliente es correcto?
   └─ Visible en interfaz
   
✅ ¿Productos son correctos?
   └─ Verifica nombre exacto
   
✅ ¿Cantidades son correctas?
   └─ No hay errores de dígitos
   
✅ ¿Precios son correctos?
   └─ Corresponden al grupo del cliente
   
✅ ¿Descuentos son correctos?
   └─ Sistema aplica automático
   
✅ ¿Total es razonable?
   └─ Haz cálculo mental: ¿tiene sentido?
```

**Si hay ERROR:**
- Haz clic [Editar] en el producto
- Cambia cantidad o elimínalo
- Vuelve a revisar

### FASE 4: EDITAR CARRITO (si es necesario)

#### Si necesitas cambiar CANTIDAD:
1. En carrito, haz clic [Editar]
2. Aparece diálogo: "Nueva cantidad:"
3. Ingresa cantidad correcta
4. Haz clic [OK]
5. Sistema recalcula subtotal automáticamente

#### Si necesitas ELIMINAR producto:
1. En carrito, haz clic [Eliminar]
2. Confirma: "¿Estás seguro?"
3. Haz clic [Sí]
4. Producto desaparece del carrito

#### Si necesitas APLICAR descuento manual:
```
⚠️ SOLO si está autorizado por supervisor
```

1. Botón: [Aplicar Descuento Manual]
2. Ingresa: "Porcentaje (ej: 10 para 10%)"
3. Motivo: "Cliente VIP especial" o similar
4. Haz clic [Aplicar]
5. Sistema recalcula total

### FASE 5: PROCESAR PAGO (2 minutos)

```
Interfaz: [PROCESAR PAGO]
```

**Al hacer clic, abre diálogo de pago:**

```
┌──────────────────────────────────┐
│ PROCESAR PAGO                    │
├──────────────────────────────────┤
│ Total a Pagar: $2,125            │
│                                  │
│ Método de Pago:                  │
│ ◉ Efectivo   ○ Cheque            │
│ ○ Crédito    ○ Transferencia     │
│                                  │
│ EFECTIVO:                        │
│ Monto recibido: [________]       │
│ Cambio: $0                       │
│                                  │
│ [CONFIRMAR PAGO]  [CANCELAR]     │
└──────────────────────────────────┘
```

#### Opción 1: PAGO EN EFECTIVO

1. Selecciona: ◉ Efectivo
2. Ingresa: "Monto recibido" (ej: 2,200)
3. Sistema calcula automáticamente:
   - Cambio: 2,200 - 2,125 = $75
4. Verifica que sea correcto
5. Haz clic [CONFIRMAR PAGO]

**Importante:**
- Si ingreso menos del total → Error
- Si ingreso más → Calcula cambio
- Si es exacto → Cambio = $0

#### Opción 2: PAGO CON CHEQUE

1. Selecciona: ◉ Cheque
2. Aparecen campos:
   - Número de cheque: [__________]
   - Banco: [__________]
   - Fecha de vencimiento: [__________]
3. Completa TODOS los datos
4. Haz clic [CONFIRMAR PAGO]

**Crítico:** Verifica datos antes de confirmar

#### Opción 3: PAGO A CRÉDITO

1. Selecciona: ◉ Crédito
2. Sistema muestra: "Crédito disponible: $XXX"
3. Verifica que la compra NO exceda crédito
4. Si está OK: [CONFIRMAR PAGO]
5. Sistema crea automáticamente DEUDA en módulo de Deudas

**⚠️ IMPORTANTE:**
- Acuerda plazo de pago con cliente
- Cliente DEBE tener crédito disponible
- Si no tiene → Rechaza automáticamente

#### Opción 4: PAGO TRANSFERENCIA BANCARIA

1. Selecciona: ◉ Transferencia
2. Aparece campo:
   - Referencia/Comprobante: [__________]
3. Cliente proporciona número de transferencia
4. Ingresas el número
5. Haz clic [CONFIRMAR PAGO]

**Para verificación posterior:** Banco

### FASE 6: GENERAR RECIBO (1 minuto)

```
Después de confirmar pago:
✅ Sistema guarda todo automáticamente
✅ Genera número de folio único
✅ Abre ventana de impresión
```

**Lo que ves:**
- Vista previa del recibo
- Botones: [IMPRIMIR] [ENVIAR EMAIL] [GUARDAR PDF]

**RECIBO IMPRESO contiene:**

```
═══════════════════════════════════
        BODEGA DISFRULEG
═══════════════════════════════════

Folio:        REC-2025-001234
Fecha:        13/12/2025  10:35 AM
Cliente:      Mercado Los Mangos
Dirección:    Calle Principal 123

───────────────────────────────────
DESCRIPCIÓN          QTY    PRECIO
───────────────────────────────────
Papa Blanca         100kg    $1,500
Chile Serrano        50kg    $1,000
Limón                30kg      $240
───────────────────────────────────

SUBTOTAL:                     $2,740
Descuento (15%):               -$410
TOTAL:                        $2,330

Método Pago:     EFECTIVO
Monto Recibido:  $2,400
Cambio:            $70

───────────────────────────────────
Gracias por su compra
Regrese pronto
═══════════════════════════════════
```

**Acciones disponibles:**

1. **[IMPRIMIR]** 
   - Imprime en la impresora predeterminada
   - Cliente recibe copia física

2. **[ENVIAR EMAIL]**
   - Envía recibo al email del cliente
   - Cliente recibe copia digital

3. **[GUARDAR PDF]**
   - Guarda en tu computadora
   - Para archivo/referencia futura

**⚠️ IMPORTANTE:** Siempre deja copia al cliente

### FASE 7: CONFIRMACIÓN FINAL (automática)

Después de procesar:

```
✅ Sistema actualiza automáticamente:

1. INVENTARIO
   └─ Papa: 350 - 100 = 250 kg
   └─ Chile: 170 - 50 = 120 kg
   └─ Limón: 100 - 30 = 70 kg

2. CLIENTES
   └─ Mercado Los Mangos:
      └─ Última compra: HOY
      └─ Monto: $2,125
      └─ Productos: 3

3. GANANCIAS
   └─ Vendido: $2,125
   └─ Ganancia estimada: $750 (35%)

4. SI ES CRÉDITO
   └─ Se crea automáticamente DEUDA
   └─ Plazo: 30 días (por defecto)
```

**Verificación:** Todo ocurre automático, sin hacer nada adicional

---

## 🔍 OPERACIONES ADICIONALES

### Cargar una Orden Anterior

```
Interfaz: [Cargar Orden] o [Historial]
```

**Situación:** Cliente dice "Quiero lo mismo que compré la semana pasada"

**Solución:**
1. Haz clic [Cargar Orden]
2. Busca orden anterior por fecha/cliente
3. Selecciona la orden
4. Aparece en carrito exactamente igual
5. Puedes editar si necesita cambios
6. Procesa el pago

**Ventaja:** Agiliza ventas repetitivas

### Ver Historial de Recibos

```
Interfaz: [Historial] o [Ver Anteriores]
```

**Información disponible:**
- Todos los recibos del día/período
- Cliente y total de cada uno
- Detalles completos si haces clic

**Usos:**
- Verificar si ya vendiste a ese cliente
- Consultar detalles de venta anterior
- Auditoría de lo vendido

### Editar Recibo No Confirmado

```
Interfaz: [Editar] (en recibos pendientes)
```

**Solo si:**
- Recibo aún no fue confirmado
- Error reciente que necesita corrección

**No es recomendable después de confir

mar**

---

## 🚨 ERRORES COMUNES Y SOLUCIONES

### Error 1: "No puedo agregar más cantidad de la disponible"

**Situación:** Intento agregar 120 kg de papa pero hay solo 100 kg

**Razón:** Sistema previene que vendas más de lo que tienes

**Solución:** Agregar máximo disponible (100 kg) o agregar otro proveedor

---

### Error 2: "Cliente seleccionado no tiene crédito suficiente"

**Situación:** Cliente quiere $5,000 a crédito pero tiene $3,000 de límite

**Razón:** Protección del sistema

**Soluciones:**
- Cliente paga en efectivo total
- Cliente paga parcial en efectivo, resto a crédito
- Supervisor autoriza aumento de límite

---

### Error 3: "El recibo no se guarda"

**Situación:** Hago todo pero recibo no se confirma

**Razones posibles:**
- No seleccionaste cliente
- No agregaste productos
- El pago no fue procesado

**Solución:** Verifica que completaste TODOS los pasos

---

## 💡 TIPS Y MEJORES PRÁCTICAS

### Velocidad

```
✅ RÁPIDO:
- Ten a mano los productos frecuentes
- Memoriza precios comunes
- Memoriza clientes principales
- Usa búsqueda eficientemente

❌ LENTO:
- Scroll por todo el listado
- No sabes dónde están los productos
- Revisar cada precio
- Procesar pagos sin agilidad
```

### Precisión

```
✅ CORRECTO:
- Verifica cliente 2x
- Verifica cantidad 2x
- Verifica total antes de pagar
- Entrena a nuevos vendedores

❌ ERROR:
- Apúrate sin verificar
- Confundas cliente
- Ingreses cantidad incorrecta
- Olvides confirmar pago
```

### Seguridad

```
✅ SEGURO:
- Siempre guarda recibo
- Guarda cambio en caja
- Cuenta caja al final del día
- Reporta discrepancias

❌ RIESGO:
- No guardo recibos
- Pongo dinero en bolsillos
- No verifico caja
- Oculto errores
```

---

## 🔗 Información Adicional

- **Panel de Control:** [Volver a Recibos →](index.md)
- **Preguntas Frecuentes:** [Ver FAQ →](faq.md)
- **Referencia Rápida:** [Ver Referencia →](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** COMPLETO Y MUY DETALLADO
