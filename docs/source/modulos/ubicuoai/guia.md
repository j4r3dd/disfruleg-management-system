# 🤖 UbicuoAI - Guía Completa

## 📍 Acceder al Módulo

### Paso 1: Abre BodegaDisfruleg
1. Inicia sesión con tu usuario
2. Visualizarás el panel principal

### Paso 2: Navega a UbicuoAI
1. En el menú principal, busca **"UbicuoAI"** o **"Procesador de Pedidos"**
2. Haz clic en él
3. Se abrirá la ventana de UbicuoAI

**Nota:** Debes estar autenticado para usar UbicuoAI. Si no puedes acceder, verifica tu usuario y contraseña.

---

## 🎯 Interfaz Principal

### Elementos Principales:

**1. Campo de Entrada (Área de Texto Grande)**
- Aquí pegas el texto con los productos
- Puede ser un listado de líneas
- No importa el formato exacto

**2. Botón "Procesar" o "Analizar"**
- Procesa el texto ingresado
- Busca productos en la base de datos
- Muestra resultados en tiempo real

**3. Tabla de Resultados**
- Muestra cada producto detectado
- Nombre del producto
- Cantidad y unidad
- % de confianza
- Botones para corregir

---

## ➕ Procesar Productos

### Paso 1: Prepara el Texto

Obtén un listado de productos. Ejemplos válidos:

**Formato 1: Simple**
```
Chile serrano 6 kg
Papa Cambray 12 kg
Limón 3 kg
```

**Formato 2: Con descripciones**
```
Chile serrano Oaxaca 6 kg
Papa Cambray premium 12 kg
Limón persa 3 kg
```

**Formato 3: Variado**
```
Chile serrano - 6 kg
Papa: 12 kg Cambray
3kg de Limón
```

### Paso 2: Copia y Pega el Texto

1. En la ventana de UbicuoAI, ve al campo de entrada (área grande de texto)
2. **Borra** cualquier texto anterior
3. **Pega** tu listado de productos

### Paso 3: Haz Clic en "Procesar"

1. Presiona el botón **"Procesar"**, **"Analizar"** o similar
2. UbicuoAI analiza el texto
3. Muestra los resultados en la tabla

---

## 📊 Interpretar Resultados

### Estados de Confianza:

**✅ Verde (95-100% Confianza)**
- Coincidencia exacta o aprendizaje
- Se puede usar directamente
- Enviar sin revisar

**⚠️ Amarillo (75-94% Confianza)**
- Fuzzy matching (búsqueda aproximada)
- Revisar antes de usar
- Puede necesitar corrección

**❌ Rojo (<75% Confianza)**
- No encontró coincidencia
- **DEBE corregirse manualmente**
- Es obligatorio editar antes de continuar

### Ejemplo de Resultados:

```
Producto              Cantidad  Unidad  Confianza  Acción
─────────────────────────────────────────────────────────
Chile Serrano         6         kg      100% ✅    [OK]
Papa Cambray          12        kg      100% ✅    [OK]
Limón                 3         kg      100% ✅    [OK]
Aguacate              6         kg      95%  ⚠️     [Revisar]
Cebolla Blanca        16        kg      87%  ⚠️     [Revisar]
Zanahoria [ERROR]     2         kg      45%  ❌     [Corregir]
```

---

## ✏️ Corregir Productos

### Cuando Necesitas Corregir:

Hay 2 situaciones:

**1. Confianza Baja (⚠️ Amarillo)**
- Verifica que el producto sea el correcto
- Si es incorrecto, corrige

**2. No Encontrado (❌ Rojo)**
- El sistema no pudo identificar el producto
- DEBES seleccionar el producto correcto

### Cómo Corregir:

**Opción 1: Haz Clic en la Fila**
1. Haz clic en el producto a corregir
2. Se abre un selector/dropdown
3. Selecciona el producto correcto
4. Se guarda automáticamente

**Opción 2: Usa el Botón "Editar"**
1. Haz clic en el botón **"Editar"** o **"..."** de la fila
2. Se abre un diálogo para cambiar el producto
3. Selecciona el correcto de la lista
4. Haz clic **"Guardar"**

**Opción 3: Escribe para Buscar**
1. Algunos sistemas permiten escribir directamente
2. Escribe el nombre del producto correcto
3. Selecciona de las opciones que aparecen

---

## 🧠 El Sistema de Aprendizaje

### ¿Qué es el Aprendizaje?

UbicuoAI **guarda** cada corrección que haces:

**Primera vez:**
```
Escribes: "aguacte"
Corriges a: "Aguacate"
Sistema aprende: "aguacte" = "Aguacate"
```

**Segunda vez:**
```
Escribes: "aguacte"
UbicuoAI ya lo sabe: "aguacte" → "Aguacate" ✅
(95% confianza automáticamente)
```

### Ventaja:

- No tienes que corregir lo mismo dos veces
- Con cada corrección, el sistema mejora
- A más uso, más preciso

---

## 🔍 Búsqueda de Productos

### Cómo Busca UbicuoAI:

**Nivel 1: Coincidencia Exacta**
```
Buscas: "Aguacate"
Encuentra: "Aguacate" ✅ 100%
```

**Nivel 2: Diccionario de Aprendizaje**
```
Buscas: "aguacte" (error ortográfico)
Ya lo conoce: "aguacte" → "Aguacate"
Encuentra: "Aguacate" ✅ 95%
```

**Nivel 3: Fuzzy Logic (Búsqueda Inteligente)**
```
Buscas: "agucate" (2 letras mal)
Calcula similitud: 85%
Encuentra: "Aguacate" ⚠️ 85%
```

### Unidades Soportadas:

El sistema reconoce automáticamente:
- **Peso:** kg, g, gr, gramos, kilogramo
- **Volumen:** L, ml, litro, mililitro
- **Cantidad:** pza, pieza, unidad, docena, caja, manojo, atado
- **Otros:** buche, lata, paquete, bolsa

---

## 📤 Enviar al Generador de Recibos

### Una Vez Procesados los Productos:

1. **Verifica todos los productos** (toda confianza ≥75%)
2. Haz clic en **"Enviar"** o **"Exportar"**
3. Se envían automáticamente al módulo de Recibos
4. Allí puedes crear el recibo final

### Requisitos para Enviar:

- ✅ Todos los productos deben tener al menos 75% de confianza
- ✅ No puede haber productos sin asignar
- ✅ Las cantidades deben ser válidas

---

## 🚨 Solución de Problemas

### "No puedo acceder a UbicuoAI"

**Problema:** Ventana no se abre o muestra error

**Soluciones:**
1. Verifica que estés **autenticado** (iniciaste sesión)
2. Cierra y reabre la aplicación
3. Verifica que tengas permisos en el módulo

---

### "Los productos no se encuentran"

**Problema:** La búsqueda no encuentra los productos

**Soluciones:**
1. Verifica que escribas el nombre **similar** al de la base de datos
2. Revisa la ortografía
3. Si es frecuente, **corrige** para que aprenda
4. Consulta con el administrador sobre nombres de productos

---

### "Producto con confianza muy baja"

**Problema:** Aparece con rojo (<75%)

**Soluciones:**
1. **Corrige manualmente** seleccionando el producto correcto
2. Aprenderá y la próxima vez será más rápido
3. Si el producto no existe, contacta al administrador

---

### "¿Por qué aparecen productos múltiples para lo mismo?"

**Problema:** "Papa Blanca", "papa blanca", "PAPA BLANCA" aparecen como diferentes

**Explicación:** La base de datos tiene productos con diferentes capitalizaciones

**Solución:** Elige uno consistentemente. Con cada corrección, UbicuoAI aprenderá tus preferencias

---

## 💡 Tips y Trucos

### 📋 Mejor Organización del Texto:
```
✅ RECOMENDADO (un producto por línea):
Chile serrano 6 kg
Papa Cambray 12 kg
Limón 3 kg

❌ EVITAR (todo en una línea):
Chile serrano 6 kg Papa Cambray 12 kg Limón 3 kg
```

### 📝 Cómo Escribir Correctamente:
```
✅ Correcto:
- "6 kg de Chile Serrano"
- "Chile Serrano 6kg"
- "Chile serrano 6 kg"

❌ Evitar:
- "6 chiles serranos" (sin cantidad clara)
- "varios chiles" (cantidad vaga)
```

### ⚡ Acelera tu Trabajo:
1. Copia listados directamente de emails
2. Pégalos sin editar
3. Deja que UbicuoAI procese
4. Revisa solo los con ⚠️ amarillo
5. Envía al generador de recibos

---

## 🎬 Flujo de Trabajo Típico

### Escenario: Procesar Pedido de 15 productos

**1. Obtener Listado (2 minutos)**
```
Recibe email o WhatsApp con productos
Copia el texto
```

**2. Procesar en UbicuoAI (30 segundos)**
```
Pega en UbicuoAI
Haz clic "Procesar"
```

**3. Revisar Resultados (2 minutos)**
```
Verifica productos con confianza baja
Corrige los necesarios
```

**4. Enviar (10 segundos)**
```
Haz clic "Enviar"
Listo para crear recibo
```

**Total: ~5 minutos** (vs 15-20 minutos seleccionando manualmente)

---

## 🔗 Información Adicional

- **Panel de Control:** [Volver a UbicuoAI →](index.md)
- **Preguntas Frecuentes:** [Ver FAQ →](faq.md)
- **Videos Tutorial:** [Ver Videos →](videos.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
