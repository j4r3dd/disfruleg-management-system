# DISFRULEG - Guía de Compilación Multiplataforma

## 📋 Resumen

Este documento explica cómo preparar y compilar DISFRULEG para funcionar en **macOS** y **Windows** con los iconos correctos en cada plataforma.

## 🎯 Preparación Inicial (UNA SOLA VEZ)

### Paso 1: Instalar dependencias

```bash
pip install pillow pyinstaller
```

### Paso 2: Preparar el logo original

Coloca tu logo PNG en:
```
assets/logos/ubicuo_logo.png
```

**Requisitos del PNG:**
- Formato: PNG con transparencia (RGBA)
- Tamaño mínimo recomendado: 1024x1024 px
- Fondo transparente preferible

### Paso 3: Generar todos los iconos

```bash
python setup_icons.py
```

Este script creará automáticamente:
- `ubicuo_icon.ico` (Windows)
- `ubicuo_icon.icns` (macOS, solo si ejecutas en macOS)
- Verificará que `ubicuo_logo.png` exista (Linux)

**Nota:** Si estás en macOS, se crearán los 3 archivos. Si estás en Windows, solo se creará el `.ico` (el `.icns` se creará cuando compiles en macOS).

## 🖥️ Compilación según tu Sistema Operativo

### Para macOS

```bash
python build_macos.py
```

**Resultado:**
- Se crea `dist/DISFRULEG.app`
- Icono automático en el dock y barra de título
- Listo para distribuir o instalar en `/Applications/`

**Crear DMG para distribución:**
```bash
hdiutil create -volname DISFRULEG -srcfolder dist/DISFRULEG.app -ov -format UDZO DISFRULEG.dmg
```

### Para Windows

**Opción 1 - Script Python:**
```bash
python build_windows.py
```

**Opción 2 - Script Batch (doble clic):**
```
build_windows.bat
```

**Resultado:**
- Se crea `dist/DISFRULEG.exe`
- Icono automático en la ventana y barra de tareas
- Listo para distribuir

## 🔄 Cómo Funciona la Detección Automática

Tu `login_window.py` ya está configurado para detectar automáticamente el sistema operativo:

```python
def _setup_window_icon(self):
    """Configura el icono según el sistema operativo"""
    if platform.system() == "Windows":
        # Usa ubicuo_icon.ico
    elif platform.system() == "Darwin":  # macOS
        # Usa ubicuo_icon.icns o ubicuo_logo.png
    else:  # Linux
        # Usa ubicuo_logo.png
```

**Esto significa:**
- En macOS verás el icono correcto (.icns)
- En Windows verás el icono correcto (.ico)
- No necesitas cambiar código entre plataformas
- Los iconos se cargan automáticamente

## 📁 Estructura de Archivos Necesaria

```
BodegaDisfruleg/
├── assets/
│   └── logos/
│       ├── ubicuo_logo.png       # Original (necesario)
│       ├── ubicuo_icon.ico       # Windows (generado)
│       └── ubicuo_icon.icns      # macOS (generado)
├── src/
│   └── auth/
│       └── login_window.py       # Ya configurado
├── main.py                       # Punto de entrada
├── setup_icons.py                # Generador de iconos
├── build_macos.py                # Compilador macOS
├── build_windows.py              # Compilador Windows
└── build_windows.bat             # Compilador Windows (batch)
```

## 🚀 Flujo de Trabajo Recomendado

### Si desarrollas en macOS:

1. **Desarrollo y pruebas en macOS:**
   ```bash
   python main.py  # Desarrollo normal
   ```

2. **Preparar iconos (una vez):**
   ```bash
   python setup_icons.py
   ```

3. **Compilar para macOS:**
   ```bash
   python build_macos.py
   ```

4. **Compilar para Windows (desde macOS):**
   ```bash
   python build_windows.py
   ```
   
   Esto creará el `.exe` pero **debes probarlo en Windows**.

5. **Probar en Windows:**
   - Copia `dist/DISFRULEG.exe` a una máquina Windows
   - Ejecuta y verifica que el icono aparezca correctamente

### Si desarrollas en Windows:

1. **Preparar iconos (una vez):**
   ```bash
   python setup_icons.py
   ```
   Nota: El `.icns` no se creará, pero no es problema.

2. **Compilar para Windows:**
   ```bash
   python build_windows.py
   ```

3. **Para compilar para macOS:**
   - Necesitas ejecutar en una máquina macOS
   - Copia el proyecto completo a macOS
   - Ejecuta `python setup_icons.py` (creará el .icns)
   - Ejecuta `python build_macos.py`

## ⚠️ Solución de Problemas

### El icono no aparece en Windows

**Causa:** Falta el archivo `.ico`

**Solución:**
```bash
python setup_icons.py
```

### El icono no aparece en macOS

**Causa:** Falta el archivo `.icns`

**Solución:**
```bash
python setup_icons.py
```

### Error: "No se encuentra ubicuo_logo.png"

**Causa:** El archivo PNG original no está en la ruta correcta

**Solución:**
Coloca tu logo en `assets/logos/ubicuo_logo.png`

### El ejecutable es muy grande (>100 MB)

**Causa:** PyInstaller incluye Python completo y todas las librerías

**Solución:**
- Esto es normal
- Considera usar `--onedir` en lugar de `--onefile` si el tamaño es crítico
- Excluye librerías innecesarias (ya está configurado)

### Antivirus bloquea el .exe

**Causa:** PyInstaller a veces es detectado como sospechoso

**Solución:**
1. Agrega excepción en el antivirus
2. Firma digitalmente el ejecutable (requiere certificado)
3. Distribuye desde fuente confiable

## 📊 Comparación de Tamaños

| Plataforma | Archivo | Tamaño Aproximado |
|------------|---------|-------------------|
| macOS      | DISFRULEG.app | 60-80 MB |
| Windows    | DISFRULEG.exe | 50-70 MB |
| Linux      | DISFRULEG | 50-70 MB |

## 🔧 Personalización Avanzada

### Cambiar información de versión (Windows)

Edita `version_info.txt` y cambia:
- `FileVersion`
- `ProductVersion`
- `CompanyName`
- `LegalCopyright`

### Cambiar identificador del bundle (macOS)

En `build_macos.py`, modifica:
```python
'--osx-bundle-identifier=com.ubicuostudio.disfruleg',
```

### Agregar más archivos al ejecutable

En los scripts de compilación, agrega líneas como:
```python
'--add-data=ruta/origen:ruta/destino',
```

## ✅ Checklist de Distribución

### Antes de distribuir en Windows:
- [ ] Ejecutado `python setup_icons.py`
- [ ] Compilado con `python build_windows.py`
- [ ] Probado en Windows 10/11
- [ ] Verificado que aparece el icono
- [ ] Incluida carpeta `assets` si es necesaria

### Antes de distribuir en macOS:
- [ ] Ejecutado `python setup_icons.py` en macOS
- [ ] Compilado con `python build_macos.py`
- [ ] Probado en macOS (versión mínima recomendada: 10.15)
- [ ] Verificado que aparece el icono
- [ ] Opcional: Creado DMG para distribución

## 📞 Soporte

Si encuentras problemas:
1. Verifica que los archivos de iconos existen en `assets/logos/`
2. Revisa los mensajes de error de los scripts
3. Asegúrate de tener las dependencias instaladas
4. Verifica que `login_window.py` está actualizado

---

**© 2025 DISFRULEG - Ubicuo Studio**
