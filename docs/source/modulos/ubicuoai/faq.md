# 🤖 UbicuoAI - Preguntas Frecuentes (FAQ)

## 🚀 Primeros Pasos

### ¿Cómo accedo a UbicuoAI?

1. Abre BodegaDisfruleg
2. Inicia sesión con tu usuario
3. En el menú principal, selecciona **"UbicuoAI"** o **"Procesador de Pedidos"**
4. Se abrirá la ventana del módulo

**Nota:** Debes estar autenticado. Si no aparece la opción, verifica tus permisos.

---

### ¿Necesito hacer algo especial para empezar?

**No.** El módulo funciona automáticamente:
- ✅ Carga los productos de la base de datos al abrir
- ✅ Carga el diccionario de aprendizaje
- ✅ Listo para usar

Solo tienes que pegar el texto con los productos.

---

### ¿Cuál es la interfaz exacta de UbicuoAI?

Tiene **3 partes principales:**

1. **Campo de Entrada (Arriba):** Área grande donde pegas el texto
2. **Botón Procesar (Centro):** Presiona para analizar
3. **Tabla de Resultados (Abajo):** Muestra los productos procesados

---

## 📝 Entrada de Datos

### ¿Qué formato debo usar para los productos?

**El más simple y recomendado:**
```
Producto Cantidad Unidad
Chile serrano 6 kg
Papa Cambray 12 kg
Limón 3 kg
```

**Pero también funciona:**
```
6 kg Chile serrano
12 kg Papa Cambray
3 kg Limón
```

```
Chile serrano - 6 kg
Papa Cambray (12 kg)
3 kg of Limón
```

El sistema es flexible y entiende variaciones.

---

### ¿Cuántos productos puedo procesar a la vez?

**Sin límite técnico.** Puedes procesar:
- 5 productos
- 50 productos
- 100+ productos

El tiempo depende de la cantidad, pero generalmente es **muy rápido** (segundos).

---

### ¿Puedo copiar y pegar directamente de emails/WhatsApp?

**Sí, absolutamente.** 

El sistema acepta:
- ✅ Listados de emails
- ✅ Mensajes de WhatsApp
- ✅ Documentos de Word
- ✅ PDFs (copia el texto)
- ✅ Hojas de cálculo

Solo copia y pega sin editar.

---

### ¿Qué pasa si hay errores ortográficos?

**El sistema maneja errores:**

| Error | Encuentra | Confianza |
|:---|:---|:---:|
| "aguacte" | "Aguacate" | 95% (aprendido) |
| "agucate" | "Aguacate" | 85% (fuzzy) |
| "cebolla bca" | "Cebolla Blanca" | 90% |
| "papa blanca" | "Papa Blanca" | 100% |

Si es error conocido (aprendido), lo corrige automáticamente.

---

### ¿Qué unidades reconoce?

El sistema reconoce automáticamente:

**Peso:**
- kg, kilogramo, k
- g, gr, gramo
- Ejemplos: "6 kg", "300 gr", "2.5 k"

**Volumen:**
- L, litro
- ml, mililitro
- Ejemplos: "1 L", "500 ml"

**Cantidad:**
- pza, pieza, unidad
- docena, caja, manojo
- bolsa, paquete, lata
- atado, buche
- Ejemplos: "2 pza", "1 docena", "3 cajas"

---

## 🔍 Búsqueda y Matching

### ¿Cómo decide si un producto existe?

El sistema usa **3 niveles de búsqueda:**

**1. Exacto (100%)**
```
Buscas: "Aguacate"
Base de datos: "Aguacate"
Resultado: ✅ 100% (coincidencia exacta)
```

**2. Aprendizaje (95%)**
```
Buscas: "aguacte" (error conocido)
Sistema sabe: "aguacte" = "Aguacate"
Resultado: ⚠️ 95% (aprendido)
```

**3. Fuzzy Logic (75%+)**
```
Buscas: "agucate" (error desconocido)
Similitud calculada: 85%
Resultado: ⚠️ 85% (búsqueda aproximada)
```

Si nada coincide ≥75%, aparece como ❌ rojo.

---

### ¿Por qué aparece con "baja confianza"?

**Razones comunes:**

1. **Ortografía muy diferente:** "agucte" vs "Aguacate" (2+ errores)
2. **Nombre abreviado:** "cebolla bca" vs "Cebolla Blanca" (abreviatura)
3. **Formato diferente:** "aguacate fresco" vs "Aguacate" (descripción extra)

**Solución:** Corrígelo manualmente. Con cada corrección, UbicuoAI aprende.

---

### ¿Qué significa cada porcentaje de confianza?

| Rango | Significado | Acción |
|:---|:---|:---|
| 95-100% | Muy seguro | Usar sin revisar |
| 85-94% | Bastante seguro | Revisar si tienes duda |
| 75-84% | Aceptable | Revisar antes de enviar |
| <75% | No seguro | Corregir obligatoriamente |

---

### ¿Puedo ver por qué un producto tiene baja confianza?

Depende de la interfaz. Algunas versiones muestran:
- ℹ️ Botón de información
- 💬 Tooltip al pasar el mouse
- 📊 Detalles en la fila

Si no ves el detalle, simplemente corrígelo manualmente.

---

## ✏️ Correcciones

### ¿Cómo corrijo un producto?

**Método 1: Haz clic en la fila**
1. Haz clic en el producto a corregir
2. Se abre un dropdown/selector
3. Selecciona el producto correcto de la lista
4. Se guarda automáticamente

**Método 2: Botón Editar**
1. Haz clic en el botón **"Editar"** (lápiz) o **"..."**
2. Se abre un diálogo
3. Busca y selecciona el correcto
4. Haz clic **"Guardar"**

**Método 3: Búsqueda Rápida**
1. Algunos sistemas permiten escribir
2. Empieza a escribir el nombre
3. Selecciona de las opciones que aparecen

---

### ¿Se guarda mi corrección?

**Sí, automáticamente.**

Cuando corriges:
1. Se guarda en el sistema de aprendizaje
2. La próxima vez se aplicará automáticamente
3. No tienes que corregir lo mismo dos veces

---

### ¿Puedo deshacer una corrección?

Depende de la interfaz:
- ✅ Si hay botón **"Deshacer"**, úsalo
- ❌ Si no hay, deberías corregir de nuevo al revés
- 📧 Si es crítico, contacta al administrador

---

## 🧠 Sistema de Aprendizaje

### ¿Qué aprende exactamente?

El sistema guarda:
- La forma **incorrecta** que escribiste
- El producto **correcto** que seleccionaste
- Fecha y número de veces usado

### Ejemplo:
```
Guardado:
- Incorrecto: "aguacte"
- Correcto: "Aguacate"
- Confianza: 95%
- Usos: 3 veces
- Última vez: 2025-12-12
```

---

### ¿Cuándo se aplica el aprendizaje?

**Automáticamente en la siguiente búsqueda:**

```
Sesión 1:
- Escribes: "aguacte"
- Resultado: 45% confianza (fuzzy)
- Corriges manualmente a: "Aguacate"
- Se guarda la corrección

Sesión 2:
- Escribes: "aguacte"
- Resultado: 95% confianza (aprendizaje)
- Se aplica automáticamente ✅
```

---

### ¿Puedo ver todas mis correcciones aprendidas?

Depende de la interfaz. Algunas opciones:
- ℹ️ Menú → "Historial de Aprendizaje"
- ⚙️ Configuración → "Diccionario"
- 📊 Estadísticas → "Correcciones"

Si no está visible, contacta al administrador.

---

### ¿Se comparten las correcciones con otros usuarios?

**Por defecto, SÍ** (si usa la base de datos compartida).

Cuando tú aprendes "aguacte = Aguacate", **todos los usuarios** se benefician.

Si quieres correcciones **privadas**, contacta al administrador.

---

## 📤 Envío a Recibos

### ¿Cómo envío los productos al generador de recibos?

1. **Completa el procesamiento** en UbicuoAI
2. **Verifica que todos tengan ≥75% confianza**
3. Haz clic en **"Enviar"** o **"Exportar"**
4. Los productos se envían al módulo de **Recibos**
5. Allí creas el recibo final

---

### ¿Qué pasa si envío sin revisar?

Depende de la configuración:

**Opción 1: Sistema permite**
- Se envía tal cual
- Recibos puede tener productos incorrectos
- ⚠️ No recomendado

**Opción 2: Sistema bloquea**
- No permite enviar si hay errores
- Debes corregir primero
- ✅ Más seguro

---

### ¿Puedo editar después en el generador de recibos?

**Sí.** Los productos se envían pero:
- El módulo de Recibos permite ediciones
- Puedes cambiar cantidad, precio, etc.
- Es el último lugar para correcciones

---

## 🚨 Problemas y Soluciones

### "No puedo abrir UbicuoAI"

**Problema:** La ventana no se abre o muestra error

**Soluciones (en orden):**
1. Verifica que estés **autenticado** (iniciaste sesión)
2. Cierra y reabre la aplicación principal
3. Reinicia la computadora
4. Contacta al administrador

---

### "Los productos no se encuentran"

**Problema:** La búsqueda devuelve 0% de confianza

**Causas posibles:**
1. Nombre muy diferente del que existe en BD
2. Producto no existe en la base de datos
3. Producto está inactivo

**Soluciones:**
1. Corrige manualmente seleccionando el nombre exacto
2. Si el producto no existe, contacta a administrador
3. Verifica que el producto esté "Activo" en el módulo de Productos

---

### "¿Por qué hay dos versiones del mismo producto?"

**Problema:** "Papa Blanca" y "papa blanca" se muestran diferentes

**Razón:** La base de datos tiene ambas versiones

**Soluciones:**
1. Elige consistentemente una (la mayúscula es más estándar)
2. Cada corrección enseña al sistema tu preferencia
3. A la larga, una opción será más probable

---

### "El sistema es muy lento"

**Problema:** Tarda mucho en procesar

**Causas posibles:**
1. Muchos productos (100+)
2. Base de datos lenta o lejos
3. Internet lenta

**Soluciones:**
1. Procesa en lotes más pequeños (30-40 productos)
2. Intenta en una hora diferente (menos carga)
3. Contacta a administrador si persiste

---

### "Aparecen productos extraños en las sugerencias"

**Problema:** El dropdown muestra productos irrelevantes

**Razón:** Búsqueda aproximada es demasiado amplia

**Solución:** Sigue escribiendo para afinar. Con más letras, más preciso.

---

## 💡 Tips y Mejores Prácticas

### 📋 Preparar Texto Antes

```
✅ RECOMENDADO:
- Un producto por línea
- Cantidad y unidad claros
- Nombres legibles

❌ EVITAR:
- Todo en una línea
- Cantidad vaga ("varios", "bastante")
- Siglas sin explicación
```

### ⚡ Acelerar Trabajo

1. **Procesa en lotes pequeños** (~30 productos)
2. **Revisa solo los amarillos** (verdes están bien)
3. **Aprende a escribir como la BD** (usa nombres estándar)
4. **Guarda listados frecuentes** como templates

### 🎯 Maximizar Confianza

| Acción | Efecto |
|:---|:---|
| Escribir correctamente | +confianza |
| Corregir errores | Sistema aprende |
| Usar nombres estándar | +exactitud |
| Procesar regularmente | Sistema mejora |

---

## 📞 ¿Aún tienes dudas?

### Consulta la Guía Completa
Para detalles técnicos y paso a paso:
👉 **[Ir a la Guía Completa →](guia.md)**

### Mira los Videos
Para aprender de forma visual:
👉 **[Ver Videos Tutoriales →](videos.md)**

### Contacta a Soporte
Si tu pregunta no está aquí:
📧 soporte@bodegadisfruleg.com
📞 [Tu número de soporte]

---

## 🔗 Enlaces Útiles

- [📖 Guía Completa](guia.md)
- [📺 Videos Tutoriales](videos.md)
- [👥 Volver al Índice](index.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
