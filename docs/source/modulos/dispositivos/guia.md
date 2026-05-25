# 📱 Administración de Dispositivos - Guía Completa

## 📍 Acceder al Módulo

### Paso 1: Abre BodegaDisfruleg
1. Inicia sesión con tu usuario (administrador)
2. Visualizarás el panel principal

### Paso 2: Navega a Administración de Dispositivos
1. En el menú principal, busca **"Dispositivos"**, **"Administración"** o **"Seguridad"**
2. Haz clic en él
3. Se abrirá la ventana de administración

**⚠️ Nota:** Solo administradores pueden acceder a este módulo.

---

## 🎯 Interfaz Principal

### Elementos Principales:

**1. Pestañas de Filtro**
- Todos (todos los dispositivos)
- Autorizados (con permiso)
- Pendientes (esperando aprobación)
- Desautorizados (bloqueados)
- Inactivos (sin usar)

**2. Tabla de Dispositivos**
- Nombre/Descripción
- IP (dirección)
- Navegador y SO
- Estado
- Última actividad

**3. Botones de Acción**
- Autorizar
- Desautorizar
- Eliminar
- Ver Detalles

---

## ✅ Autorizar un Dispositivo

### Paso 1: Accede a Dispositivos Pendientes

1. Abre módulo Administración de Dispositivos
2. Haz clic en pestaña **"Pendientes"**
3. Se muestran dispositivos nuevos esperando aprobación

### Paso 2: Revisa la Información

Se muestra:
- **Nombre:** Descripción del dispositivo (ej: "Dell XPS de Juan")
- **IP:** Dirección de internet
- **Navegador:** Chrome, Firefox, Safari
- **Sistema Operativo:** Windows, Mac, Linux
- **Fecha:** Cuándo intentó acceder
- **Nota:** Si el usuario dejó un mensaje

### Paso 3: Verifica que sea Legítimo

Preguntas a hacer:
1. ¿Conozco este dispositivo?
2. ¿Es de la oficina o empleado conocido?
3. ¿IP es válida?
4. ¿Navegador es estándar?

**⚠️ Si algo parece raro:**
- ❌ NO autorices
- Contacta al empleado primero
- Verifica antes de autorizar

### Paso 4: Autoriza el Dispositivo

1. Selecciona el dispositivo
2. Haz clic **"Autorizar"**
3. Se pide confirmación:
   - "¿Deseas autorizar este dispositivo?"
4. Haz clic **"Sí, Autorizar"**

**Resultado:**
- ✅ Dispositivo autorizado
- ✅ Pasa a "Autorizados"
- ✅ Usuario puede acceder desde ahora

---

## ❌ Desautorizar un Dispositivo

### Cuándo Desautorizar:

**Situaciones:**
- Empleado se va de la empresa
- Dispositivo fue robado
- Acceso no autorizado detectado
- Empleado cambia de computadora
- Dispositivo comprometido

### Paso 1: Busca el Dispositivo

1. En pestaña **"Autorizados"**
2. Busca el dispositivo a bloquear
3. O usa búsqueda para encontrarlo

### Paso 2: Desautoriza

1. Selecciona el dispositivo
2. Haz clic **"Desautorizar"** o botón de bloqueo
3. Se pide confirmación
4. Haz clic **"Sí, Desautorizar"**

**Resultado:**
- ✅ Dispositivo bloqueado inmediatamente
- ✅ Usuario NO puede acceder
- ✅ Aparece en "Desautorizados"
- ✅ Sesión activa se cierra

---

## 📊 Ver Estados de Dispositivos

### Pestaña: Autorizados

Dispositivos con permiso para acceder.

**Información:**
- ✅ Todos activos y en uso
- 🟢 Verde: En línea ahora
- ⚪ Gris: Offline

### Pestaña: Pendientes

Nuevos dispositivos esperando aprobación.

**Acción:** Autorizar o rechazar

### Pestaña: Desautorizados

Dispositivos bloqueados.

**Ejemplo:**
- Empleado anterior
- Dispositivo robado
- Computadora fuera de servicio

### Pestaña: Inactivos

Autorizados pero sin usar hace tiempo.

**Acción:** Considerar desautorizar si no se usa

---

## 🔍 Búsqueda y Filtrado

### Buscar Dispositivo

1. Campo **"Buscar"** en la tabla
2. Escribe nombre, IP o usuario
3. Se filtra automáticamente

**Ejemplos:**
- Escribe "Dell" → Aparecen todos Dell
- Escribe "192.168" → Aparecen de esa red
- Escribe "Juan" → Dispositivos de Juan

### Filtrar por Estado

1. **Pestaña Autorizados:** Todos los activos
2. **Pestaña Pendientes:** Esperan aprobación
3. **Pestaña Desautorizados:** Bloqueados
4. **Pestaña Inactivos:** No usados

---

## 👁️ Ver Detalles del Dispositivo

### Información Disponible:

1. **Identificación:**
   - Nombre/descripción
   - Usuario propietario
   - Fecha de registro

2. **Técnica:**
   - IP (dirección de internet)
   - Navegador (Chrome, Firefox)
   - Sistema operativo (Windows, Mac)
   - Versión de navegador/SO

3. **Actividad:**
   - Última conexión
   - Fecha de autorización
   - Número de accesos

### Cómo Acceder:

1. Selecciona dispositivo
2. Haz clic **"Ver Detalles"** o botón "ℹ️"
3. Se abre ventana con toda la información
4. Puedes cerrar o copiar información

---

## 🚨 Solución de Problemas

### "Un usuario dice que no puede acceder"

**Checklist:**

1. ¿Su dispositivo está autorizado?
   - Ve a "Autorizados"
   - Busca su dispositivo
   - Si no está: autorízalo

2. ¿Está en "Pendientes"?
   - Significa que no fue aprobado
   - Debes autorizar

3. ¿Está en "Desautorizados"?
   - Fue bloqueado deliberadamente
   - Contacta con tu supervisor

### "Un dispositivo aparece como inactivo"

**Razones:**
- No se ha usado en mucho tiempo
- Usuario cambió de computadora
- Dispositivo se dañó

**Acciones:**
- Si no se necesita: desautoriza
- Si se necesita: verifica con usuario

---

## 💡 Tips y Mejores Prácticas

### 🔐 Seguridad

```
✅ SIEMPRE:
- Verifica dispositivo nuevo antes de autorizar
- Bloquea inmediatamente si empleado se va
- Revisa "Inactivos" mensualmente
- Mantén lista limpia

❌ NUNCA:
- Autorices sin verificar
- Dejes dispositivos robados autorizados
- Olvides bloquear acceso de empleados antiguos
```

---

### 📋 Procedimiento de Bienvenida

```
Cuando llega empleado nuevo:
1. Proporcionarle credenciales
2. Que intente acceder (generará "Pendiente")
3. Verificar dispositivo
4. Autorizar
5. Empleado ya puede trabajar
6. Registrar en lista de control
```

---

### 👋 Procedimiento de Salida

```
Cuando se va un empleado:
1. Recuperar sus dispositivos
2. Venir a administrador ANTES de irse
3. Desautorizar TODOS sus dispositivos
4. Cambiar contraseña compartidas
5. Verificar historial de accesos
6. Archivar información
```

---

## 🔗 Información Adicional

- **Panel de Control:** [Volver a Dispositivos →](index.md)
- **Preguntas Frecuentes:** [Ver FAQ →](faq.md)
- **Referencia Rápida:** [Ver Referencia →](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
