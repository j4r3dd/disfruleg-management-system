# 👥 Administrar Usuarios - Guía Completa

## 📍 Acceder al Módulo

### Paso 1: Ingresar a BodegaDisfruleg
1. Abre tu navegador y ve a la plataforma
2. Inicia sesión con tu cuenta de administrador
3. Visualizarás el dashboard principal

### Paso 2: Navegar al módulo Usuarios
1. En el menú lateral izquierdo, busca **"Administración"**
2. Dentro de ese menú, selecciona **"Usuarios"**
3. Se abrirá la pantalla de gestión de usuarios

**Nota:** Solo administradores y gerentes pueden acceder a este módulo. Si no ves la opción, contacta a tu supervisor.

---

## ➕ Crear un Nuevo Usuario

### Paso 1: Haz clic en "Crear Usuario"
1. En la parte superior derecha, busca el botón **"+ Crear Usuario"** o **"Nuevo Usuario"**
2. Se abrirá un formulario en la pantalla

### Paso 2: Completa los Datos Básicos

**Campos requeridos:**
- **Nombre Completo:** Nombre y apellido del usuario (ej: "Juan García")
- **Email:** Correo corporativo único (ej: "juan.garcia@bodega.com")
- **Usuario:** Nombre de usuario para login (ej: "jgarcia")
- **Contraseña Temporal:** Crea una contraseña segura
  - Mínimo 8 caracteres
  - Incluir mayúsculas, minúsculas y números
  - El usuario deberá cambiarla en su primer acceso

**Campos opcionales:**
- **Teléfono:** Número de contacto
- **Puesto:** Cargo del usuario (Vendedor, Gerente, Bodeguero, etc.)
- **Departamento:** Área de trabajo (Ventas, Bodega, Finanzas, etc.)

### Paso 3: Asigna Roles y Permisos

**Opción A: Por Rol Predefinido**
1. En la sección **"Rol"**, selecciona uno de los roles disponibles:
   - **Vendedor:** Acceso a ventas, precios, clientes
   - **Bodeguero:** Gestión de inventario y compras
   - **Gerente:** Acceso a reportes y análisis
   - **Administrador:** Acceso total al sistema
   - **Soporte:** Solo lectura y asistencia

2. El rol asignará automáticamente los permisos correspondientes

**Opción B: Permisos Personalizados**
1. Activa la opción **"Permisos Personalizados"**
2. Verás una lista de módulos con checkboxes:
   - ☑️ **Ver:** Permiso de lectura
   - ☑️ **Crear:** Permiso para crear registros
   - ☑️ **Editar:** Permiso para modificar
   - ☑️ **Eliminar:** Permiso para borrar

3. Marca solo los permisos necesarios según el puesto

| Módulo | Ver | Crear | Editar | Eliminar |
|:-------|:---:|:-----:|:------:|:--------:|
| Ubicuo AI | ☑️ | ☑️ | ☑️ | ☐ |
| Recibos | ☑️ | ☑️ | ☑️ | ☐ |
| Precios | ☑️ | ☐ | ☑️ | ☐ |
| Compras | ☑️ | ☑️ | ☑️ | ☐ |
| Reportes | ☑️ | ☐ | ☐ | ☐ |

### Paso 4: Guarda el Usuario

1. Al final del formulario, haz clic en **"Guardar"** o **"Crear Usuario"**
2. Verás un mensaje de confirmación: ✅ "Usuario creado exitosamente"
3. El nuevo usuario aparecerá en la lista

---

## ✏️ Editar Información de un Usuario

### Para cambiar datos básicos:

1. En la **lista de usuarios**, busca el usuario a editar
2. Haz clic en el **icono de lápiz** o **"Editar"** en su fila
3. Modifica los campos que necesites:
   - Nombre, email, puesto, departamento
4. Haz clic en **"Guardar"** o **"Actualizar"**

### Datos que NO se pueden editar:
- Usuario (nombre de login) - Para cambiar, crear uno nuevo
- Fecha de creación - Se registra automáticamente
- Último acceso - Se actualiza automáticamente

---

## 🔐 Gestionar Contraseñas

### Resetear Contraseña

Si un usuario olvidó su contraseña:

1. En la lista, encuentra el usuario
2. Haz clic en **"Más opciones"** (⋮) o **"Acciones"**
3. Selecciona **"Resetear Contraseña"**
4. Se enviará un email al usuario con un link para crear nueva contraseña
5. El usuario tendrá 24 horas para cambiarla

### Cambiar Contraseña Forzadamente

1. En **"Más opciones"** (⋮), elige **"Forzar Cambio de Contraseña"**
2. En el próximo login, el sistema obligará al usuario a crear una nueva contraseña
3. Ideal cuando expira una contraseña o por razones de seguridad

---

## 👤 Asignar y Modificar Roles

### Cambiar Rol de un Usuario

1. Abre la lista de usuarios
2. Haz clic en el usuario a modificar
3. En la sección **"Rol"**, selecciona el nuevo rol:
   - Vendedor
   - Bodeguero
   - Gerente
   - Administrador
   - Soporte
4. **Guardar** los cambios

**Importante:** Cambiar el rol modifica automáticamente todos los permisos asociados.

### Ver Permisos Actuales

1. Selecciona un usuario de la lista
2. Busca la sección **"Permisos"** o **"Módulos Autorizados"**
3. Se mostrarán todos los módulos a los que tiene acceso
4. Verás si tiene acceso de Ver, Crear, Editar o Eliminar

---

## 🚫 Desactivar o Eliminar Usuarios

### Desactivar un Usuario (Recomendado)

Desactivar es mejor que eliminar porque mantiene el historial:

1. En la lista de usuarios, selecciona el usuario
2. Haz clic en **"Más opciones"** (⋮) → **"Desactivar"**
3. Se abrirá un modal de confirmación
4. Escribe la razón (opcional): "Empleado se fue" o similar
5. Haz clic en **"Confirmar Desactivación"**

**Resultado:**
- ✅ El usuario NO puede acceder más al sistema
- ✅ Su historial se mantiene para auditoría
- ✅ Puede reactivarse después si es necesario

### Reactivar un Usuario Desactivado

1. En la lista de usuarios, busca la pestaña **"Inactivos"**
2. Encuentra el usuario a reactivar
3. Haz clic en **"Reactivar"**
4. Confirma la acción
5. El usuario podrá acceder nuevamente

### Eliminar Permanentemente (Cuidado ⚠️)

**Advertencia:** Esto borra todos los datos del usuario. Usa solo si es absolutamente necesario.

1. En **"Más opciones"** (⋮), selecciona **"Eliminar Permanentemente"**
2. Se pedirá confirmación doble
3. Escribe "ELIMINAR" para confirmar
4. El usuario se borrará del sistema

---

## 📊 Visualizar Historial y Actividad

### Ver último acceso de un usuario

1. En la lista de usuarios, observa la columna **"Último Acceso"**
2. Muestra la fecha y hora de su último ingreso al sistema

### Ver historial de actividades

1. Selecciona un usuario específico
2. Busca la pestaña **"Historial"** o **"Actividad"**
3. Verás un registro de:
   - Creación de registros
   - Cambios importantes
   - Accesos al sistema
   - Modificaciones de permisos

### Buscar en el historial

1. Usa los filtros disponibles:
   - **Por tipo de acción:** Creación, edición, eliminación
   - **Por fecha:** Rango personalizado
   - **Por módulo:** Ubicuo AI, Recibos, etc.

---

## 🔍 Filtrar y Buscar Usuarios

### Búsqueda Rápida

1. En la parte superior, verás un campo de **"Buscar"**
2. Escribe el nombre, email o usuario
3. La lista se filtrará automáticamente

**Ejemplo:** Escribe "juan" para encontrar todos los usuarios con ese nombre.

### Filtros Avanzados

1. Haz clic en el botón **"Filtros"** o **"Opciones Avanzadas"**
2. Filtra por:
   - **Rol:** Vendedor, Bodeguero, Gerente, etc.
   - **Estado:** Activos, Inactivos, Suspendidos
   - **Departamento:** Ventas, Bodega, Finanzas, etc.
   - **Fecha de creación:** Usuarios nuevos, antiguos, etc.

3. Haz clic en **"Aplicar"** para ver resultados

---

## 🎬 Video Tutorial

Para una demostración visual de todos estos pasos:

👉 **[Ver Videos Tutoriales →](videos.md)**

Los videos te mostrarán:
- Overview del módulo
- Crear tu primer usuario
- Asignar permisos correctamente
- Resolver problemas comunes

---

## ❓ Preguntas Frecuentes

Si tienes dudas sobre:
- "¿Qué permisos debo dar a un vendedor?"
- "¿Cómo reseteo una contraseña?"
- "¿Qué diferencia hay entre desactivar y eliminar?"

👉 **[Consulta la FAQ Completa →](faq.md)**

---

## 🚨 Problemas Comunes

### "No puedo crear usuarios"
**Solución:** Verifica que tu cuenta tenga permisos de administrador. Contacta al administrador principal.

### "El usuario no puede acceder"
**Solución:** 
1. Verifica que el usuario esté ACTIVO (no desactivado)
2. Revisa que la contraseña sea correcta
3. Resetea la contraseña desde esta pantalla

### "El usuario ve módulos que no debería"
**Solución:** Edita el usuario y revisa los permisos asignados. Reduce los permisos según sea necesario.

---

## 📞 ¿Necesitas más ayuda?

- **Panel de Control:** [Volver a Usuarios →](index.md)
- **Preguntas:** [Ver FAQ →](faq.md)
- **Video Tutorial:** [Ver Videos →](videos.md)
- **Otro módulo:** [Volver al Inicio →](../../index.md)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0  
**Estado:** Completo
