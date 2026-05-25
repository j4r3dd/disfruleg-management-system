# 📝 Generar Recibos

## Descripción

El módulo **Generar Recibos** es el CORAZÓN de BodegaDisfruleg. Aquí es donde ocurren tus ventas. Creas facturas/recibos de venta, registras los productos que vende, aplicas descuentos, procesas pagos y genera documentos oficiales para tus clientes.

**Este es el módulo más crítico del sistema.** Todo lo demás existe para apoyar lo que ocurre aquí.

### Funcionalidades Principales
- ✅ **Crear recibos de venta** (Lo más importante)
- ✅ Seleccionar cliente y grupo de precios
- ✅ Buscar y agregar productos
- ✅ Ajustar cantidades y precios
- ✅ Aplicar descuentos (por cantidad, por cliente, etc.)
- ✅ Registrar pagos (efectivo, cheque, crédito)
- ✅ Generar documento imprimible
- ✅ Historial de recibos
- ✅ Cargar órdenes previas
- ✅ Editar recibos pendientes

---

## 🎯 ¿Para Qué Sirve?

### El Propósito PRINCIPAL:

**📌 REGISTRAR CADA VENTA que haces**

Sin Recibos: No sabes cuánto vendiste, a quién le vendiste, qué ganaste
Con Recibos: Control total de todo lo que ocurre en tu negocio

### Casos de Uso Concretos:

**💼 Llega un cliente mayorista a comprar**
1. Abres Generar Recibos
2. Seleccionas al cliente (ej: "Mercado Los Mangos")
3. Buscas productos (ej: "Papa Blanca")
4. Agregas cantidad (100 kg)
5. Sistema aplica automáticamente el precio mayorista
6. Cliente paga
7. Generas recibo/factura
8. LISTO - venta registrada

**🏪 Vendedor atiende minorista**
1. Abre Recibos en tablet/punto de venta
2. Selecciona cliente (puede ser "Venta General" si es anónimo)
3. Busca productos rápidamente
4. Agraga cantidades
5. Aplica descuento si es necesario
6. Procesa pago
7. Imprime/envía recibo
8. Venta completada

**📊 Fin de día: revisar lo que vendiste**
1. Ve historial de recibos del día
2. Cuánto vendiste: $5,000
3. A quiénes: 15 clientes
4. Productos más vendidos: Papa, Chile, Limón
5. Ganancias totales del día

---

## 📖 Contenido Disponible

| Sección | Descripción |
|:--------|:-----------|
| [**Guía Completa - LARGA**](guia.md) | Guía DETALLADA paso a paso (30+ minutos) |
| [**Videos Tutoriales**](videos.md) | Videos de capacitación (próximamente) |
| [**Preguntas Frecuentes - EXTENSO**](faq.md) | Respuestas MUY detalladas |
| [**Referencia Rápida**](rapida.md) | Para consultas rápidas |

---

## 🚀 Comienza Aquí

### Si tienes 5 minutos:
→ Lee esta página + [Referencia Rápida](rapida.md)

### Si tienes 30 minutos:
→ Lee [Guía Completa](guia.md) completa

### Si tienes dudas específicas:
→ Ve a [FAQ](faq.md)

### Si prefieres aprender con video:
→ Mira los [Videos](videos.md) (cuando estén disponibles)

---

## 🔧 Conceptos CRÍTICOS

### 🛒 Recibo (Factura)
**El documento de venta.**

Contiene:
- Cliente (quién compró)
- Productos (qué compró)
- Cantidades y precios
- Descuentos aplicados
- Total a pagar
- Forma de pago
- Fecha y folio
- Firma/autorización

**⚠️ CRÍTICO:** Sin recibo, no hay venta registrada.

### 👥 Cliente
**La persona o empresa que compra.**

**Tipos:**
- Cliente conocido (registrado en sistema)
- Venta general/anónima (sin cliente específico)

**Importancia:** Determina automáticamente:
- Grupo de precios aplicable
- Descuentos disponibles
- Crédito (si aplica)

### 📦 Producto
**Lo que vendes.**

Sistema calcula AUTOMÁTICAMENTE:
- Precio según grupo del cliente
- Costo unitario
- Margen de ganancia
- Disponibilidad en inventario

### 💰 Precio de Venta
**Cuánto cobra al cliente.**

**Regla AUTOMÁTICA:**
- Cliente mayorista → Precio mayorista
- Cliente minorista → Precio minorista
- Cliente VIP → Precio especial

**⚠️ NO cambies manualmente a menos que sea necesario**

### 🏷️ Descuento
**Reducción en el precio.**

**Tipos:**
- Por cantidad (ej: 10% si compra >50 kg)
- Por cliente (cliente VIP)
- Por promoción
- Manual (si autoriza)

**Impacto:** Reduce tu ganancia, úsalo estratégicamente

### 💵 Pago
**Cómo el cliente paga.**

**Métodos:**
- **Efectivo:** Pago inmediato, completo
- **Cheque:** A fecha, depósito bancario
- **Crédito:** Pago después (registra en Deudas)
- **Transferencia:** Número de referencia

**Crítico:** Debe coincidir con el total del recibo

---

## 💡 Por Qué Este Módulo Es El CORAZÓN

```
TODO lo demás depende de lo que registres aquí:

Inventario
  ↑
  └─ Se actualiza cuando vende aquí
  
Reportes/Analytics
  ↑
  └─ Datos vienen de recibos registrados aquí
  
Deudas
  ↑
  └─ Se crean si el cliente compra a crédito aquí
  
Dinero
  ↑
  └─ Ganancias vienen de lo que vende aquí
  
Clientes
  ↑
  └─ Se analizan basado en compras aquí
```

---

## 📊 Flujo de Venta COMPLETO

```
PASO 1: SELECCIONAR CLIENTE
└─ ¿Quién está comprando?
   - Cliente registrado: Accedo a sus datos
   - Cliente nuevo: Corro para registrarlo
   - Venta anónima: "Venta General"

PASO 2: AGREGAR PRODUCTOS
└─ ¿Qué quiere comprar?
   - Busco producto
   - Especifico cantidad
   - Sistema calcula precio automáticamente
   - Puedo agregar más productos

PASO 3: APLICAR DESCUENTOS
└─ ¿Tiene descuento?
   - Sistema aplica descuentos automáticos
   - Puedo agregar descuento manual si autorizado
   - Reviso que sea razonable

PASO 4: REVISAR TOTAL
└─ ¿Cuánto paga en total?
   - Veo subtotal
   - Veo descuentos aplicados
   - Veo TOTAL FINAL

PASO 5: PROCESAR PAGO
└─ ¿Cómo paga?
   - Efectivo: Ingreso cantidad recibida
   - Cheque: Ingreso datos del cheque
   - Crédito: Se registra como deuda
   - Transferencia: Ingreso referencia

PASO 6: GENERAR RECIBO
└─ Documento oficial
   - Imprimo o envío
   - Cliente tiene comprobante
   - Yo tengo registro

PASO 7: CONFIRMAR
└─ Sistema actualiza automáticamente:
   - Inventario disminuye
   - Cliente registra su historial
   - Ganancias se contabilizan
   - Si es crédito → Se crea deuda
```

---

## 🎯 Ejemplo Práctico REAL

### Escenario: Venta a Mayorista

**10:30 AM - Llega "Mercado Los Mangos"**

```
1. ABRO MÓDULO
   └─ Generar Recibos

2. SELECCIONO CLIENTE
   └─ "Mercado Los Mangos" (grupo: Mayorista)
   
3. AGREGO PRODUCTOS:
   Producto                Cantidad    Precio Unit.  Subtotal
   ─────────────────────────────────────────────────────────
   Papa Blanca             100 kg      $15           $1,500
   Chile Serrano           50 kg       $20           $1,000
   Limón                   30 kg       $8            $240
   ─────────────────────────────────────────────────────────
                                       SUBTOTAL      $2,740

4. SISTEMA APLICA DESCUENTOS:
   - Descuento mayorista (15%):  -$410
   - Descuento por volumen (5%): -$117
   ─────────────────────────────────────────
   TOTAL DESCUENTOS:                    -$527

5. TOTAL FINAL: $2,213

6. CLIENTE PAGA:
   - Efectivo: $2,213 ✅
   
7. IMPRIMO RECIBO:
   - Folio: REC-2025-001234
   - Fecha: 13/12/2025
   - Cliente: Mercado Los Mangos
   - Total: $2,213
   - Firmado y sellado
   
8. RESULTADO:
   ✅ Venta registrada
   ✅ Inventario actualizado:
      - Papa: 250 - 100 = 150 kg
      - Chile: 120 - 50 = 70 kg
      - Limón: 100 - 30 = 70 kg
   ✅ Ganancias contabilizadas
   ✅ Cliente tiene comprobante
   ✅ TODO queda registrado para auditoría
```

---

## ⚠️ Cosas CRÍTICAS a Recordar

```
✅ SIEMPRE:
1. Verifica que el cliente sea correcto
2. Verifica que los productos sean correctos
3. Verifica que las cantidades sean correctas
4. Verifica el total final
5. Asegúrate de procesar el pago correctamente
6. Guarda/imprime el recibo

❌ NUNCA:
1. Olvides registrar una venta
2. Ingrese cantidad incorrecta
3. Apliques descuento que no está autorizado
4. Registres pago incorrecto
5. Dejes recibos sin confirmar
6. Modifiques un recibo después sin autorización
```

---

**Siguiente paso:** [📖 Ir a la Guía Completa DETALLADA →](guia.md)
