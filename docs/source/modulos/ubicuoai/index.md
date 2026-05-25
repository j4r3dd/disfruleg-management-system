# 🤖 UbicuoAI - Procesador Inteligente de Pedidos

## Descripción

**UbicuoAI** es un módulo inteligente que acelera el flujo de trabajo en el generador de recibos. En lugar de seleccionar cada producto individualmente, puedes pegar un texto con los productos y UbicuoAI los procesa automáticamente.

El sistema **aprende** de tus correcciones y mejora con el tiempo, reconociendo productos incluso con errores ortográficos.

### Funcionalidades Principales
- ✅ Procesar múltiples productos desde texto sin estructura
- ✅ Extrae automáticamente: nombre, cantidad y unidad de medida
- ✅ Busca productos en la base de datos con Fuzzy Logic
- ✅ Aprende de correcciones y mejora automáticamente
- ✅ Maneja errores ortográficos y variaciones de nombres
- ✅ Integración directa con la base de datos de productos

---

## 🎯 ¿Cuándo Usar UbicuoAI?

### Casos de Uso Perfectos:

**📋 Tienes un listado de productos:**
```
Chile serrano 6 kg
Papa Cambray 12 kg
Limón 3 kg
Cebolla blanca 16 kg
Aguacate 6 kg
```

**→ UbicuoAI:** Procesa todo en segundos en lugar de ir seleccionando uno por uno.

**❌ Errores ortográficos:**
- "aguacte" → Encuentra "Aguacate"
- "papa blanca" → Encuentra "Papa Blanca"
- "cebolla bca" → Encuentra "Cebolla Blanca"

**→ UbicuoAI:** Corrige automáticamente después de aprenderlo una vez.

---

## 📖 Contenido Disponible

| Sección | Descripción |
|:--------|:-----------|
| [**Guía Completa**](guia.md) | Paso a paso para usar UbicuoAI |
| [**Videos Tutoriales**](videos.md) | Videos de capacitación (próximamente) |
| [**Preguntas Frecuentes**](faq.md) | Respuestas a dudas comunes |

---

## 🚀 Comienza Aquí

Si es tu **primera vez** usando UbicuoAI:

1. **Lee la introducción** (esta página)
2. **Ve a la [Guía →](guia.md)** (10 minutos)
3. **Mira los [Videos →](videos.md)** (cuando estén disponibles)
4. **Consulta [FAQ →](faq.md)** si tienes dudas

---

## 💡 Conceptos Clave

### 🔍 Matching (Búsqueda de Productos)

UbicuoAI busca productos en **3 niveles**:

1. **Exacto (100%):** "Aguacate" coincide exactamente
2. **Aprendizaje (95%):** Correcciones anteriores ("aguacte" → "Aguacate")
3. **Fuzzy (75%+):** Búsqueda con tolerancia a errores ("aguacte" encuentra "Aguacate")

### 📚 Aprendizaje

Cada corrección que haces se guarda:
- Se aprende automáticamente
- La próxima vez se aplica sin intervención
- Mejora la precisión del sistema

### 📊 Confianza

Cada resultado tiene un **porcentaje de confianza**:
- ✅ **≥95%:** Muy seguro, se puede usar directamente
- ⚠️ **75-94%:** Revisar antes de usar
- ❌ **<75%:** Corregir manualmente

---

## 🔧 Requisitos

- ✅ Usuario autenticado en BodegaDisfruleg
- ✅ Base de datos de productos cargada
- ✅ Acceso a módulo de Recibos

---

## ❓ ¿Necesitas Ayuda?

- **Paso a paso:** Consulta la [**Guía →**](guia.md)
- **Dudas específicas:** Ve a [**FAQ →**](faq.md)
- **Video tutorial:** Mira los [**Videos →**](videos.md)

---

## 📊 Ventajas de Usar UbicuoAI

| Ventaja | Beneficio |
|:---|:---|
| ⚡ **Rápido** | Procesa 20+ productos en segundos |
| 🧠 **Inteligente** | Aprende de correcciones |
| 📝 **Flexible** | Acepta múltiples formatos de texto |
| 🎯 **Preciso** | Busca incluso con errores ortográficos |
| 💾 **Automático** | Guarda todas las correcciones |

---

## 🎬 Ejemplo Práctico

### Entrada (Texto):
```
Chile serrano 6 kg
Papa Cambray 12 kg
Limón 3 kg
aguacte 6 kg
cebolla bca 16 kg
```

### Salida (Productos Procesados):
```
✅ Chile Serrano          6 kg    (100% confianza)
✅ Papa Cambray          12 kg    (100% confianza)
✅ Limón                  3 kg    (100% confianza)
⚠️ Aguacate               6 kg    (95% confianza - aprendida)
⚠️ Cebolla Blanca        16 kg    (87% confianza - fuzzy)
```

### Resultado:
Listos para enviar al generador de recibos en **menos de 10 segundos**

---

**Siguiente paso:** [📖 Ir a la Guía Completa →](guia.md)
