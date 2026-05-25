# 📝 Generar Recibos - Preguntas Frecuentes EXTENSAS

## 🚀 PRIMEROS PASOS

### ¿Quién usa este módulo?

**TODOS en el negocio:**
- ✅ Vendedores (usan diariamente)
- ✅ Cajero/Caja (procesa pagos)
- ✅ Dueño/Administrador (revisa resultados)
- ✅ Contador (auditoría de ventas)

**Si eres vendedor:** Este es tu herramienta principal

---

### ¿Necesito capacitación especial?

**No, pero sí es crítico que entiendas bien:**

- Cómo seleccionar cliente correcto
- Cómo buscar productos
- Cómo verificar cantidad y precio
- Cómo procesar pagos

**Recomendación:** Haz primeras 10 recibos con supervisor

---

## 👥 CLIENTES Y GRUPOS

### ¿Qué pasa si el cliente no está registrado?

**Dos opciones:**

**Opción 1: Registra rápidamente**
1. Ve al módulo Clientes
2. Crea nuevo cliente
3. Vuelve a Generar Recibos
4. Ya puedes seleccionarlo

**Opción 2: Venta General (anónima)**
1. Selecciona grupo
2. Cliente: "Venta General"
3. Completa venta normalmente
4. Después: registra cliente si quieres historial

**Recomendación:** Opción 1 es mejor (tienes historial)

---

### ¿Cómo sé qué grupo seleccionar?

**Haz estas preguntas:**

| Pregunta | Respuesta | Grupo |
|:---|:---|:---|
| ¿Cuánto compra? | Mucho (>50kg) | Mayorista |
| | Poco (<10kg) | Minorista |
| ¿Cuál es su negocio? | Tienda/Mercado | Mayorista |
| | Restaurante pequeño | Minorista |
| ¿Qué descuento acuerdan? | 15%+ | Mayorista |
| | <10% | Minorista |
| ¿Cuándo paga? | 30+ días | Mayorista |
| | Contado | Minorista |

---

### ¿Qué es "Venta General"?

**Es para clientes anónimos:**
- No tienes su nombre completo
- No volverá (probablemente)
- Paga contado

**Ejemplo:** Alguien que compra 5 kg de papa y no vuelve

**⚠️ No uses para clientes frecuentes** - pierdes historial

---

## 📦 PRODUCTOS

### ¿Cómo busco rápidamente un producto?

**Técnicas:**

1. **Primer intento:** Escribe primeras 3 letras
   - "pap" → Papa Blanca
   - "chi" → Chile Serrano

2. **Si no aparece:** Escribe cantidad
   - "papa 100" → Busca "papa" en cantidad 100

3. **Si sigue sin funcionar:** Scroll manualmente
   - Hazlo lentamente
   - Los productos están alfabéticamente

**Pro tip:** Memoriza dónde están los 5 productos más vendidos

---

### ¿Qué pasa si el producto no aparece?

**Razones posibles:**

1. **No hay stock:** Sistema no lo muestra si está en 0
   - Solución: Verifica inventario
   - ¿Necesitas cargar más?

2. **Está descontinuado:** No aparece más
   - Solución: Usa similar si existe

3. **Nombre diferente:** Quizás se llama diferente en el sistema
   - Solución: Pregunta a supervisor

---

### ¿Puedo vender menos del stock mínimo?

**Sí, pero con advertencia:**

Sistema muestra:
```
"Stock bajo - solo 5 kg disponibles"
```

Significa: Probablemente necesites comprar pronto

**Pero puedes vender los 5 kg**

---

## 💰 PRECIOS Y DESCUENTOS

### ¿De dónde salen los precios?

**Automático del sistema:**

```
Cliente: Mercado Los Mangos (Mayorista)
↓
Sistema consulta: ¿Cuál es precio de Papa para Mayorista?
↓
Respuesta: $15/kg (registrado en módulo Precios)
↓
Muestra en carrito: $15/kg
```

**⚠️ Nunca cambies manualmente a menos que supervisor autorice**

---

### ¿Por qué dos clientes del mismo grupo pagan diferente?

**Porque tienen descuentos personalizados:**

**Cliente A:** Mayorista + 5% descuento adicional (cliente VIP dentro de mayoristas)
**Cliente B:** Mayorista normal

Sistema aplica ambos automáticamente

---

### ¿Puedo aplicar un descuento no autorizado?

**Technically sí, pero:**

```
⚠️ CRÍTICO:
- Sistema puede registrar quién lo hizo
- Supervisor revisa después
- Cuenta de caja no cierra
- Puede afectar tu evaluación
```

**Respuesta corta:** NO, a menos que supervisor autorice Y esté presente

---

### ¿Qué pasa si hago mal un descuento?

**Opciones:**

1. **Si aún no confirmas:**
   - Edita el carrito
   - Elimina el descuento incorrecto
   - Aplica el correcto

2. **Si ya confirmaste:**
   - Contacta supervisor
   - Que cree nota de crédito
   - Vuelve a procesar

**Lesson:** Verifica 2x antes de confirmar

---

## 💵 PAGOS

### ¿Qué método de pago es "más seguro"?

**Por orden de seguridad:**

1. **Efectivo:** Inmediato, seguro, sin riesgos
2. **Transferencia:** Verificable después en banco
3. **Cheque:** Verificar banco antes de depositar
4. **Crédito:** Riesgoso si cliente no paga

**Recomendación:** Prefiere efectivo cuando sea posible

---

### ¿Qué pasa si el cliente paga con cheque?

**Proceso:**

1. Sistema abre campo de cheque
2. Ingresa: Número, Banco, Vencimiento
3. Toma el cheque físicamente
4. **IMPORTANTE:** Verifica que esté endosado correctamente
5. Deposita en banco a la fecha

**Riesgo:** Cheque puede rebotar (sin fondos)

---

### ¿Cómo registrar pago a crédito?

**Proceso:**

1. Cliente selecciona: "Crédito"
2. Sistema valida: ¿Tiene crédito disponible?
3. Si SÍ: Se confirma venta
4. Se crea automáticamente DEUDA en módulo Deudas
5. Vencimiento: 30 días (o lo que acuerdes)

**Recordar después:** El cliente debe pagar

---

### ¿Puedo usar crédito si el cliente NO lo tiene?

**No, sistema rechaza:**

```
Mensaje de error:
"Cliente no tiene crédito disponible"
"Límite: $0"
"Crédito usado: $0"
```

**Soluciones:**
- Cliente paga total en efectivo
- Cliente paga parcial, resto espera
- Supervisor aumenta límite

---

### ¿Qué pasa si doy cambio incorrecto?

**Ejemplo:**
- Total: $100
- Cliente paga: $150
- Cambio correcto: $50
- Yo doy: $60 (ERROR)

**Consecuencias:**

1. **Caja no cierra:** $10 falta
2. **Se revisa video:** Se ve el error
3. **Yo debo reponer:** Los $10 vienen de mi bolsillo
4. **Se reporta:** Afecta evaluación

**Prevención:** Haz cambio lentamente, verifica 2x

---

## 📋 OPERACIONES

### ¿Cómo cargo una orden anterior (venta repetida)?

**Proceso:**

1. Botón: [Cargar Orden]
2. Búsqueda: "Últimas órdenes de este cliente"
3. Selecciona la que quieres
4. Aparece en carrito idéntica
5. Puedes modificar si necesita

**Ventaja:** Rápido si cliente siempre compra lo mismo

---

### ¿Puedo editar un recibo ya confirmado?

**Depende del sistema y tiempo:**

**Si acabas de confirmar (< 5 min):**
- Sistema puede permitir edición
- O crear "nota de crédito" y nuevo recibo

**Si fue hace horas:**
- NO se puede editar
- Debes contactar supervisor
- Crear ajuste manual

**Mejor:** Verifica 2x ANTES de confirmar

---

### ¿Dónde veo el historial de mis recibos?

**Interfaz: [Historial] o [Ver Anteriores]**

**Información disponible:**
- Todos los recibos que creaste
- Fecha, cliente, total, método de pago
- Detalles completos si haces clic

**Uso importante:** Verificar si ya vendiste a ese cliente

---

## 🚨 ERRORES Y PROBLEMAS

### "El sistema dice 'Stock insuficiente'"

**Razón:** Intentaste agregar más de lo disponible

**Solución:**
1. Agregué máximo disponible
2. O avisa al supervisor para reabastecimiento
3. O cliente compra menos

**Ejemplo:**
```
Hay 50 kg de papa
Cliente quiere 100 kg
Sistema: Error
Tú: "Tengo solo 50 kg, ¿está bien?"
Cliente: "Sí, 50 kg está bien"
Agregas 50 kg
Funciona
```

---

### "¿Por qué me dice que el cliente no tiene crédito?"

**Razón:** Cliente agotó su límite

**Ejemplo:**
```
Límite de crédito: $5,000
Crédito usado: $5,000
Disponible: $0
Intenta comprar: $1,000
Sistema: Rechaza
```

**Soluciones:**
1. Cliente paga en efectivo
2. Cliente paga lo que debe, luego usa crédito nuevo
3. Supervisor sube el límite

---

### "Se va la luz, ¿se pierden los datos?"

**Depende de cuándo ocurra:**

**Antes de confirmar:**
- Se pierden productos en carrito
- Pero clientes y orden anterior están guardados
- Puedes recargar la orden

**Después de confirmar:**
- ✅ Recibo ya está guardado
- Banco confirmó el pago
- Inventario actualizado
- TODO está seguro

**Lección:** Confirma frecuentemente si es largo

---

## 🏪 VENDEDOR EN PUNTO DE VENTA

### ¿Cómo agilizo las ventas cuando hay cola?

**Técnicas:**

1. **Pre-selecciona cliente**
   - Mientras cliente se acerca, ya tienes grupo
   
2. **Productos frecuentes**
   - Memoriza los 10 más vendidos
   - Sabes exactamente dónde están

3. **Busca eficiente**
   - "pap" en lugar de "papa blanca"
   - Usa primeras 3 letras

4. **Confirma al final**
   - Una vez, no 3 veces
   - Verifica total una sola vez

5. **Pago rápido**
   - Ten cambio a mano
   - Calcula mentalmente

**Meta:** Recibo en menos de 3 minutos

---

### ¿Cómo tomo el pedido si el cliente no decide?

**Proceso:**

1. "¿Qué desea llevar?"
2. Cliente dice: "Papas, pero no sé cuánto"
3. Tú: "¿Para cuántas personas?" o "¿para su tienda?"
4. Cliente: "Para 10 personas"
5. Tú: "Recomiendo 5 kg"
6. Confirma y procede

**Tip:** Aconseja basado en experiencia

---

## 💡 BUENAS PRÁCTICAS

### Checklist Previo a Cada Venta

```
[ ] ¿Cliente correcto?
    └─ Verifico nombre en sistema
    
[ ] ¿Productos correctos?
    └─ Nombre exacto en carrito
    
[ ] ¿Cantidades correctas?
    └─ No hay error de dígitos
    
[ ] ¿Precios son correctos?
    └─ Corresponden al grupo
    
[ ] ¿Descuentos aplicados?
    └─ Son los pactados
    
[ ] ¿Total es razonable?
    └─ Hago cálculo mental: ¿tiene sentido?
    
[ ] ¿Método de pago claro?
    └─ Efectivo, cheque, crédito, transferencia
    
[ ] ¿Cantidad de pago correcta?
    └─ Si efectivo: tengo cambio
    └─ Si cheque: datos completos
    └─ Si crédito: cliente tiene límite
```

**Antes de confirmar: TODOS los checks deben estar ✅**

---

### Fin de Día: Procedimiento

```
1. Genera reporte de ventas del día
2. Suma total vendido (debe coincidir con caja)
3. Verifica: clientes, productos, pagos
4. Archiva recibos impresos
5. Reporta al supervisor:
   - Total vendido: $X,XXX
   - Número de transacciones: Y
   - Problemas ocurridos: Z (si hay)
5. Cierra caja
```

---

## 🔗 Enlaces Útiles

- [📖 Guía Completa](guia.md)
- [📺 Videos](videos.md)
- [⚡ Referencia Rápida](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** SUPER DETALLADO CON MUCHOS EJEMPLOS
