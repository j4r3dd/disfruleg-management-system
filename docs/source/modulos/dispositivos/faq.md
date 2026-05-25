# 📱 Administración de Dispositivos - Preguntas Frecuentes

## 🚀 Primeros Pasos

### ¿Quién puede acceder a este módulo?

**Solo administradores.**

Si eres administrador, verás la opción en menú.
Si no eres administrador, contacta a tu supervisor.

---

### ¿Qué es un dispositivo en este contexto?

**Una computadora, tablet o teléfono que accede a BodegaDisfruleg.**

Identificado por:
- IP (dirección de internet)
- Navegador (Chrome, Firefox, Safari)
- Sistema operativo (Windows, Mac, Linux)

---

## 📱 Autorizar Dispositivos

### ¿Por qué un dispositivo está "Pendiente"?

**Porque es la primera vez que intenta acceder.**

Sistema de seguridad:
1. Dispositivo nuevo intenta conectarse
2. Sistema lo marca como "Pendiente"
3. Administrador debe aprobar
4. Una vez aprobado, puede acceder siempre

---

### ¿Puedo autorizar múltiples dispositivos a un usuario?

**Sí, sin límite.**

Un empleado puede tener:
- Computadora de escritorio
- Laptop
- Tablet
- Teléfono

Todos pueden autorizarse.

---

### ¿Qué información veo antes de autorizar?

**Importante para verificar:**

1. **IP:** ¿Es de la oficina? ¿Domicilio del empleado?
2. **Navegador:** ¿Es estándar? (Chrome, Firefox, Edge)
3. **SO:** ¿Windows? ¿Mac? ¿Está desactualizado?
4. **Fecha:** ¿Cuándo intentó acceder?

Si algo parece extraño → NO autorices

---

## ❌ Desautorizar

### ¿Qué pasa cuando desautorizo un dispositivo?

**Inmediatamente:**
1. Dispositivo NO puede acceder más
2. Si estaba en línea, se desconecta
3. Necesitaría re-autorización (poco probable)

---

### ¿Puedo volver a autorizar un dispositivo?

**Sí, en general sí.**

Excepto si:
- Fue robado (mejor no re-autorizar)
- Fue comprometido (no re-autorizar)
- Usuario lo pide explícitamente

---

### ¿Cuándo debo desautorizar un dispositivo?

**Estas situaciones:**

| Situación | Acción |
|:---|:---|
| Empleado se va | Desautorizar inmediatamente |
| Cambió de computadora | Desautorizar la vieja |
| Dispositivo robado | Desautorizar inmediatamente |
| Acceso no autorizado | Investigar + desautorizar |
| Dispositivo fuera de servicio | Desautorizar y eliminar |

---

## 🔍 Búsqueda

### ¿Cómo busco un dispositivo específico?

**Tres formas:**

1. **Por nombre:** "Dell XPS de Juan"
2. **Por IP:** "192.168.1.100"
3. **Por usuario:** "juan@empresa.com"

Escribe cualquier dato en búsqueda y filtra.

---

### ¿Puedo ver todos los dispositivos de un usuario?

**Depende de la interfaz:**

**Opción 1:** Busca por nombre de usuario
**Opción 2:** Ordena tabla por usuario
**Opción 3:** Contacta a administrador si necesitas reporte

---

## 📊 Estados

### ¿Cuál es la diferencia entre estados?

| Estado | Significado | Acción |
|:---|:---|:---|
| **Pendiente** | Nuevo, esperando aprobación | Autorizar |
| **Autorizado** | Aprobado, puede acceder | Monitorear |
| **Desautorizado** | Bloqueado | Re-autorizar si es necesario |
| **Inactivo** | Autorizado pero no usa | Considerar desautorizar |

---

### ¿Por qué un dispositivo aparece "Inactivo"?

**Razones:**
1. Hace mucho tiempo que no se usa
2. Empleado cambió de computadora
3. Dispositivo se dañó
4. Simplemente no está en uso

**Acción:** Preguntar al usuario si sigue siendo necesario

---

## 🔐 Seguridad

### ¿Es seguro autorizar dispositivos?

**Sí, si verificas bien:**

✅ Verificar que sea dispositivo legítimo
✅ Verificar IP válida
✅ Verificar usuario conocido
✅ Desautorizar cuando no sea necesario

❌ NO autorices sin verificar
❌ NO dejes dispositivos robados autorizados

---

### ¿Qué pasa si autorizo un dispositivo comprometido?

**Riesgo:**
- Usuario no autorizado puede acceder
- Datos de la empresa en peligro
- Competencia obtiene información

**Prevención:**
- Verifica IP y navegador
- Si algo parece extraño, NO autorices
- Contacta al usuario para confirmar

---

### ¿Puedo ver el historial de accesos?

**Sí, en la información del dispositivo:**

- Última conexión
- Número de accesos
- Fechas de uso

Para auditoría más detallada, contacta a administrador.

---

## 🚨 Problemas Comunes

### "Autorizo un dispositivo pero sigue diciendo pendiente"

**Solución:**
1. Actualiza la página (F5)
2. Cierra y reabre el módulo
3. Si persiste, contacta soporte

---

### "Un usuario dice que autorizado su dispositivo pero no aparece"

**Verificar:**
1. ¿Está en pestaña "Autorizados"?
2. ¿Está en otra pestaña (Inactivos)?
3. Busca por nombre del usuario

Si no aparece en ningún lado → Vuelve a autorizar

---

### "¿Puedo eliminar un dispositivo permanentemente?"

**Depende del sistema:**

**Si:** Botón "Eliminar" o similar
- Elimina registro completamente
- Mejor para dispositivos viejos

**Si no:** Solo puedes desautorizar
- Queda en historial
- Pero bloqueado del acceso

---

## 💡 Tips Profesionales

### 📋 Mantener Lista Limpia

```
Mensual:
1. Revisar dispositivos "Inactivos"
2. Contactar usuarios para confirmar
3. Desautorizar los no necesarios
4. Mantener lista actualizada

Trimestral:
1. Auditoría completa
2. Revisar dispositivos sospechosos
3. Verificar cambios en IPs
```

---

### 🔐 Seguridad en Procedimientos

```
PROCEDIMIENTO DE ENTRADA:
1. Empleado nuevo llega
2. Intenta acceder (Pendiente)
3. Verifica información
4. Autoriza
5. Empleado puede trabajar

PROCEDIMIENTO DE SALIDA:
1. Antes de irse
2. Administrador revisa dispositivos
3. Desautoriza TODOS inmediatamente
4. Verifica no quedó acceso abierto
5. Cierra sesión
```

---

## 🔗 Enlaces Útiles

- [📖 Guía Completa](guia.md)
- [📺 Videos](videos.md)
- [⚡ Referencia Rápida](rapida.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
