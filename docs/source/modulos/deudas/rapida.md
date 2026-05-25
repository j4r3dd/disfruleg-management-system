# 💳 Gestionar Deudas - Referencia Rápida

## ⚡ 3 Pasos Rápidos

### 1️⃣ REGISTRAR DEUDA
```
+ Registrar Deuda
→ Cliente: (selector)
→ Monto: 10000
→ Vencimiento: (fecha)
→ Guardar
```

### 2️⃣ MONITOREAR
```
Ver Tabla:
- Estado (Pendiente/Vencida/Pagada)
- Colores: Verde=OK, Rojo=Vencida
```

### 3️⃣ COBRAR
```
Registrar Pago:
→ Cliente: (selector)
→ Monto: (lo que pagó)
→ Guardar
→ Deuda se reduce automático
```

---

## 💳 Registrar Deuda

1. Botón: **+ Registrar Deuda**
2. Completa:
   - Cliente: "Mercado Los Mangos"
   - Monto: 10000
   - Vencimiento: 30 días después
3. Guardar

---

## 💵 Registrar Pago

1. Botón: **Registrar Pago**
2. Completa:
   - Cliente: (selector)
   - Deuda: (selector)
   - Monto Pagado: (parcial o total)
3. Guardar

---

## 📊 Ver Estado

**Tabla Muestra:**
- Cliente
- Monto adeudado
- Vencimiento
- Estado (color)
- Días vencida (si aplica)

**Colores:**
- 🟢 Verde: Pendiente
- 🟡 Amarillo: Próxima vencer
- 🔴 Rojo: Vencida
- ⚫ Gris: Pagada

---

## 🔍 Filtrar

1. **Por Estado:**
   - Mostrar Pendientes
   - Mostrar Vencidas
   - Mostrar Pagadas

2. **Por Cliente:**
   - Campo Buscar
   - Escribe nombre
   - Se filtra automático

---

## ⏰ Vencimientos

**Ideal por cliente:**
- Mayorista: 30 días
- Minorista: 7-15 días
- Contado: 0 días (paga ahora)

---

## 📈 Morosidad

```
Fórmula:
Morosidad = Deudas Vencidas / Total Adeudado

Saludable: <20%
Problema: >30%
Crisis: >50%
```

---

## 🎯 Flujo Típico

```
1. Cliente compra $10,000 a crédito
   ↓
2. Registras deuda (vencimiento 30 días)
   ↓
3. Día 28: Cliente paga $3,000 parcial
   ↓
4. Registras pago
   ↓
5. Deuda ahora: $7,000
   ↓
6. Día 35: Deuda vencida (sin pagar)
   ↓
7. Envías recordatorio urgente
   ↓
8. Cliente paga $7,000
   ↓
9. Deuda: PAGADA
```

---

## 🔗 Más Info

- [📖 Guía Completa](guia.md)
- [❓ FAQ](faq.md)
- [📺 Videos](videos.md)

---

**Imprime para referencia rápida.**
