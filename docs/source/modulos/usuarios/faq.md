# 👥 Administrar Usuarios - Preguntas Frecuentes (FAQ)

## 👤 Crear Usuarios

### ¿Cómo creo un nuevo usuario?

1. En el módulo **Administrar Usuarios**, haz clic en **"+ Crear Usuario"**
2. Completa los campos:
   - **Nombre Completo:** Nombre y apellido
   - **Email:** Correo corporativo único
   - **Usuario:** Nombre para login (sin espacios)
   - **Contraseña:** Temporal, mínimo 8 caracteres
3. Elige un **Rol** (Vendedor, Bodeguero, Gerente, etc.)
4. Haz clic en **"Guardar"**

✅ El usuario recibirá un email para confirmar su cuenta.

---

### ¿El usuario se tiene que cambiar la contraseña?

**Sí, es obligatorio.**

Cuando un usuario inicia sesión por primera vez con la contraseña temporal que estableciste, el sistema le pide que cree su propia contraseña segura.

**Requisitos de contraseña:**
- Mínimo 8 caracteres
- Una mayúscula
- Una minúscula
- Un número

---

### ¿Puedo crear un usuario sin email?

**No, el email es obligatorio.**

El email es importante porque:
- Es el identificador único del usuario
- Se usa para notificaciones
- Se usa para resetear contraseñas

Si el usuario no tiene email corporativo, contacta al administrador principal.

---

### ¿Cuántos usuarios puedo crear?

**Sin límite**, siempre que tu plan de suscripción lo permita. Si necesitas crear muchos usuarios, contacta al equipo comercial.

---

## 🔐 Contraseñas y Seguridad

### ¿Cómo reseteo una contraseña?

Si un usuario olvidó su contraseña:

1. Ve a **Administrar Usuarios**
2. Busca al usuario
3. Haz clic en **"Más opciones"** (⋮)
4. Selecciona **"Resetear Contraseña"**
5. Se enviará un email con un link para cambiarla

El usuario tendrá **24 horas** para establecer su nueva contraseña.

---

### ¿Puedo ver la contraseña de un usuario?

**No, por razones de seguridad.**

Las contraseñas están encriptadas y ni siquiera los administradores pueden verlas. Si alguien olvidó su contraseña, debes resetearla (opción anterior).

---

### ¿Qué pasa si un usuario olvida su contraseña?

**Opción 1:** (Como administrador)
- Entra a Administrar Usuarios
- Resetea la contraseña del usuario
- El usuario recibirá un email con instrucciones

**Opción 2:** (El usuario por sí mismo)
- En la pantalla de login, hace clic en **"¿Olvidaste tu contraseña?"**
- Ingresa su email
- Recibe instrucciones para crear una nueva

---

### ¿Con qué frecuencia debería cambiar mi contraseña?

**Recomendación:** Cada 90 días por seguridad.

Puedes habilitar una política de cambio obligatorio de contraseña en **Configuración del Sistema**.

---

## 👥 Roles y Permisos

### ¿Qué diferencia hay entre los roles?

| Rol | Acceso |
|:---|:---|
| **Vendedor** | Ventas, clientes, precios. Sin acceso a finanzas. |
| **Bodeguero** | Inventario, compras, recibos. Sin reportes avanzados. |
| **Gerente** | Reportes, análisis, todas las ventas del equipo. |
| **Administrador** | Acceso total al sistema incluyendo configuraciones. |
| **Soporte** | Solo lectura. Puede ver información pero no modificar. |

---

### ¿Cómo cambio el rol de un usuario?

1. Ve a **Administrar Usuarios**
2. Encuentra el usuario a editar
3. Haz clic en **"Editar"** (lápiz)
4. En la sección **"Rol"**, selecciona el nuevo rol
5. Haz clic en **"Guardar"**

✅ Los permisos se actualizarán automáticamente.

---

### ¿Puedo dar permisos personalizados?

**Sí, tienes dos opciones:**

**Opción A: Roles Predefinidos**
- Rápido y recomendado
- Asigna un rol automáticamente con permisos típicos

**Opción B: Permisos Personalizados**
1. Al crear/editar un usuario, activa **"Permisos Personalizados"**
2. Verás cada módulo con checkboxes de Ver, Crear, Editar, Eliminar
3. Marca solo lo que el usuario necesita

**Recomendación:** Usa permisos personalizados solo si es necesario.

---

### ¿Qué significa cada permiso?

| Permiso | Descripción |
|:---|:---|
| **Ver** | Puede abrir y visualizar la información |
| **Crear** | Puede crear nuevos registros |
| **Editar** | Puede modificar registros existentes |
| **Eliminar** | Puede borrar registros |

---

### ¿Un vendedor puede ver reportes financieros?

**No, a menos que se lo des explícitamente.**

Por defecto:
- ✅ Vendedor: Ve sus propias ventas
- ❌ Vendedor: No ve reportes de ganancias ni financieros

Si necesita verlos, edita el usuario y agrégale permiso a "Reportes" → Ver.

---

## 👤 Editar y Eliminar Usuarios

### ¿Cómo edito la información de un usuario?

1. En la lista de usuarios, haz clic en **"Editar"** (lápiz)
2. Modifica los campos que necesites
3. Haz clic en **"Guardar"**

**Puedes cambiar:**
- Nombre completo
- Email
- Puesto
- Departamento
- Rol y permisos

**NO puedes cambiar:**
- Usuario (nombre de login) - Debes eliminar y crear uno nuevo

---

### ¿Cuál es la diferencia entre desactivar y eliminar?

| Acción | Resultado |
|:---|:---|
| **Desactivar** | El usuario NO puede acceder. Su historial se guarda. Puede reactivarse. |
| **Eliminar** | El usuario se borra completamente del sistema. No hay vuelta atrás. |

**Recomendación:** **Siempre desactiva en lugar de eliminar.** El historial es importante para auditoría.

---

### ¿Cómo desactivo un usuario?

1. En la lista, selecciona el usuario
2. Haz clic en **"Más opciones"** (⋮)
3. Selecciona **"Desactivar"**
4. Opcionalmente, escribe la razón (ej: "Empleado se fue")
5. Confirma

✅ El usuario no podrá acceder más.

---

### ¿Cómo reactivo un usuario desactivado?

1. En la lista de usuarios, ve a la pestaña **"Inactivos"**
2. Busca al usuario
3. Haz clic en **"Reactivar"**
4. Confirma

✅ El usuario podrá acceder de nuevo.

---

### ¿Puedo eliminar un usuario permanentemente?

**Sí, pero úsalo solo en caso de extrema necesidad.**

1. En **"Más opciones"** (⋮), selecciona **"Eliminar Permanentemente"**
2. Se pedirá confirmación doble
3. Escribe **"ELIMINAR"** para confirmar
4. ⚠️ El usuario se borrará completamente sin vuelta atrás

---

## 🔍 Búsqueda y Filtros

### ¿Cómo busco un usuario específico?

**Búsqueda Rápida:**
1. En el campo de **"Buscar"** en la parte superior
2. Escribe el nombre, email o usuario
3. La lista se filtra automáticamente

**Búsqueda Avanzada:**
1. Haz clic en **"Filtros"**
2. Filtra por:
   - Rol (Vendedor, Bodeguero, etc.)
   - Estado (Activo, Inactivo)
   - Departamento
   - Fecha de creación

---

### ¿Puedo exportar la lista de usuarios?

Algunos sistemas permiten exportar a Excel o PDF. Busca un botón de **"Descargar"** o **"Exportar"** en la parte superior de la lista.

---

## 📊 Historial y Auditoría

### ¿Cómo veo el historial de un usuario?

1. Selecciona un usuario específico
2. Busca la pestaña **"Historial"** o **"Actividad"**
3. Verás:
   - Cuándo creó cada registro
   - Cuándo los editó
   - Último acceso al sistema

---

### ¿Puedo ver cuándo un usuario accedió al sistema?

**Sí, en la columna "Último Acceso"** de la lista principal, o en el historial detallado del usuario.

---

### ¿Cómo auditar las acciones de un usuario?

1. Abre el usuario
2. Ve a **"Historial"**
3. Verás un registro de:
   - Qué creó
   - Qué editó
   - Cuándo lo hizo
   - Qué valores cambió

Esto es útil para investigaciones o auditorías.

---

## 🚨 Problemas Comunes

### El usuario dice "No puedo acceder"

**Diagnóstico paso a paso:**

1. ¿El usuario está **activo**?
   - Busca en Administrar Usuarios
   - Si aparece en la lista, está activo
   - Si no, busca en **"Inactivos"** y reactívalo

2. ¿Introdujo la contraseña correcta?
   - Sugiere usar **"Olvidé mi contraseña"** en login
   - Tú puedes resetearla desde aquí

3. ¿Tiene **permisos para el módulo** que intenta acceder?
   - Abre el usuario
   - Revisa la sección "Permisos"
   - Si no tiene permiso "Ver", no puede acceder

4. ¿Hay problema técnico?
   - Intenta abrir sesión con otra cuenta
   - Si funciona, es problema del usuario

---

### "Creé un usuario pero no recibe el email"

**Soluciones:**

1. **Verifica el email es correcto** - Búscalo nuevamente en la lista
2. **Revisa carpeta de spam** - El email podría estar en spam/basura
3. **Reintentar envío:**
   - Edita el usuario
   - Busca **"Reenviar email de bienvenida"**
   - Haz clic para enviar de nuevo
4. **Contacta a soporte** si el email sigue sin llegar

---

### "Un usuario ve módulos que no debería"

**Solución:**

1. Abre el usuario en **Administrar Usuarios**
2. Ve a la sección **"Permisos"**
3. Revisa qué módulos tiene habilitados
4. Si ve algo que no debería, edita y quita ese permiso
5. Haz clic en **"Guardar"**

El cambio tomará efecto en el próximo login del usuario.

---

### "Cambié permisos pero el usuario sigue viendo lo mismo"

**Problema:** El usuario podría tener la sesión abierta.

**Solución:**
1. Fuerza el cierre de sesión del usuario (si hay esa opción)
2. Pídele al usuario que cierre sesión y vuelva a abrir
3. Los nuevos permisos entrarán en efecto

---

### "¿Cómo fuerzo a un usuario a cambiar contraseña?"

1. Abre el usuario en **Administrar Usuarios**
2. Haz clic en **"Más opciones"** (⋮)
3. Selecciona **"Forzar Cambio de Contraseña"**
4. En el próximo login, el sistema lo obligará a cambiarla

---

## 📞 ¿Aún tienes dudas?

### Consulta la Guía Completa
Para detalles más técnicos y paso a paso:
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
- [🏠 Inicio General](../../index.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
