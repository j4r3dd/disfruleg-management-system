# UbicuoAI Module

Sistema Inteligente de Procesamiento de Pedidos para Restaurantes

**Version:** 2.0.0
**Arquitectura:** Clean Architecture (Onion Architecture)

## Descripción

UbicuoAI es un módulo que acorta el flujo de trabajo en el generador de recibos. Reduce el tiempo que se gasta seleccionando cada producto individualmente. Además, este módulo aprende y guarda registros de correcciones.

### Características Principales

- **Parser Inteligente**: Extrae productos, cantidades y unidades de texto no estructurado
- **Matching con Fuzzy Logic**: Encuentra productos en la base de datos incluso con errores ortográficos
- **Sistema de Aprendizaje**: Aprende de las correcciones del usuario y mejora con el tiempo
- **Integración con Base de Datos**: Conectado directamente al sistema de productos existente

## Arquitectura

El módulo sigue Clean Architecture con 4 capas bien definidas:

```
ubicuoai/
├── domain/              # Capa de Dominio (Entidades y Reglas de Negocio)
│   ├── models.py        # Entidades: OrderItem, ProductMatch, LearningCorrection
│   ├── value_objects.py # Objetos de Valor: MatchMethod, Unit
│   └── exceptions.py    # Excepciones del Dominio
│
├── data/                # Capa de Datos (Repositorios)
│   ├── repositories.py  # Interfaces (Protocolos)
│   └── mysql_repositories.py  # Implementaciones MySQL
│
├── business/            # Capa de Negocio (Servicios)
│   ├── parser_service.py    # Servicio de Parsing
│   ├── matcher_service.py   # Servicio de Matching
│   ├── learning_service.py  # Servicio de Aprendizaje
│   └── ubicuoai_service.py  # Servicio Orquestador
│
├── ui/                  # Capa de Presentación (UI)
│   ├── controllers/
│   │   └── ubicuoai_controller.py  # Controlador MVC
│   └── ubicuoai_window.py   # Ventana Principal
│
└── ubicuoai_manager.py  # Punto de Entrada con DI
```

### Principios Aplicados

✅ **Dependency Injection**: Todos los servicios reciben sus dependencias por constructor
✅ **Interface Segregation**: Interfaces (Protocols) para repositorios
✅ **Fail Fast Validation**: Validación en `__post_init__` de todos los modelos
✅ **Single Responsibility**: Cada capa tiene UNA responsabilidad
✅ **No Cross-Layer Dependencies**: Las capas internas nunca dependen de las externas

## Uso

### 1. Desde el Menú Principal

```python
# En tu aplicación principal
from src.modules.ubicuoai import open_ubicuoai_window

# Abrir ventana de UbicuoAI
window = open_ubicuoai_window(parent_window)
```

### 2. Uso Programático

```python
from src.modules.ubicuoai import initialize_ubicuoai, get_ubicuoai_service

# Inicializar módulo
init_result = initialize_ubicuoai()
print(f"Productos cargados: {init_result['products_loaded']}")

# Obtener servicio
service = get_ubicuoai_service()

# Procesar pedido
text = """
Chile serrano 6 kg
Papa Cambray 12 kg
Limón 3 kg
"""

parse_result, matches = service.process_order(text)

# Ver resultados
for item, match in zip(parse_result.items, matches):
    if match:
        print(f"{item.product_name} -> {match.matched_name} ({match.confidence:.0%})")
```

### 3. Aprender Correcciones

```python
# Cuando el usuario corrige un producto
service.learn_correction(
    incorrect="aguacte",
    correct="Aguacate"
)

# La próxima vez que se vea "aguacte", se corregirá automáticamente
```

## Base de Datos

### Tabla de Aprendizaje

El módulo crea automáticamente una tabla para guardar las correcciones:

```sql
CREATE TABLE ubicuoai_learning (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incorrect VARCHAR(200) NOT NULL UNIQUE,
    correct VARCHAR(200) NOT NULL,
    times_used INT NOT NULL DEFAULT 1,
    first_added DATETIME NOT NULL,
    last_used DATETIME NOT NULL,
    confidence_boost DECIMAL(3, 2) NOT NULL DEFAULT 0.05,
    INDEX idx_incorrect (incorrect),
    INDEX idx_last_used (last_used)
);
```

### Conexión a Base de Datos

El módulo se integra automáticamente con el sistema de base de datos del proyecto:

- Requiere usuario autenticado (`db_manager.is_authenticated()`)
- Usa la conexión actual del usuario
- No requiere configuración adicional

## Dependencias

```bash
# Requeridas
pip install rapidfuzz  # o fuzzywuzzy

# Incluidas en el proyecto
- customtkinter
- mysql-connector-python
```

## Ejemplo de Texto de Pedido

```
Chile serrano 6 kg
papa Cambray 12 kg
limón 3 kg
Cebolla bca 16 kg
Aguacate 6 kg
Jitomate saladet 9 kg
hoja plátano 1 manojo
Chile morita 300 gr
Papa bca 2 kg
Zanahoria 2 kg
lechuga sangría 2 pieza(s)
lechuga italiana 2 pieza(s)
Huevo 6.5 kg
Fresa 2 cajas
Frambuesa 2 cajas
```

## Cómo Funciona

1. **Parsing**: El texto se analiza línea por línea, extrayendo:
   - Nombre del producto
   - Cantidad
   - Unidad de medida

2. **Matching**: Cada producto parseado se busca en la base de datos usando:
   - Coincidencia exacta (100% confianza)
   - Diccionario de aprendizaje (95% confianza)
   - Fuzzy matching (variable, mínimo 75%)

3. **Aprendizaje**: Cuando el usuario corrige un producto:
   - Se guarda la corrección en la base de datos
   - Se actualiza el diccionario en memoria
   - La próxima vez se aplicará automáticamente

4. **Exportación**: Los productos con alta confianza (≥75%) pueden enviarse al Receipt Generator

## Configuración

El módulo funciona con configuración por defecto. Para personalizar:

```python
# Ajustar threshold de confianza
from src.modules.ubicuoai.ubicuoai_manager import UbicuoAIManager

manager = UbicuoAIManager()
# El threshold se configura en MatcherService (default: 0.75)
```

## Solución de Problemas

### "No authenticated database connection"
**Solución**: El usuario debe iniciar sesión primero antes de abrir UbicuoAI.

### "Products not loaded"
**Solución**: Llamar a `initialize_ubicuoai()` antes de usar el servicio.

### Productos no se encuentran
**Solución**:
1. Verificar que los productos estén activos en la base de datos
2. Revisar que el nombre del producto sea similar al de la base de datos
3. Usar correcciones manuales para enseñar al sistema

## Mantenimiento

### Limpiar Correcciones Antiguas

```python
service = get_ubicuoai_service()
learning_service = service.learning

# Eliminar correcciones de más de 6 meses con menos de 2 usos
deleted = learning_service.cleanup_old_corrections(
    max_age_days=180,
    min_usage=2
)
print(f"Eliminadas {deleted} correcciones antiguas")
```

### Ver Estadísticas

```python
service = get_ubicuoai_service()
stats = service.get_system_statistics()

print(f"Productos en cache: {stats['matcher']['products_in_cache']}")
print(f"Correcciones: {stats['learning']['total_entries']}")
print(f"Usos totales: {stats['learning']['total_uses']}")
```

## Integración Futura

### Receipt Generator

Pendiente de integración. La función `send_to_receipt_generator()` está preparada para recibir la integración:

```python
def send_to_receipt_generator(self) -> bool:
    """Enviar productos al generador de recibos"""
    # TODO: Integrar con receipt_generator
    pass
```

## Migración desde Versión Antigua

Si tenías la versión anterior (standalone), los cambios principales son:

1. **No más configuración YAML**: El módulo se integra con el sistema de DB del proyecto
2. **No más sample products**: Se cargan productos reales de la base de datos
3. **Dependency Injection**: Los servicios se inyectan, no se instancian directamente
4. **Clean Architecture**: Separación clara de responsabilidades

## Contribuir

Al modificar este módulo, mantén la arquitectura limpia:

- ✅ Domain Layer: Solo entidades y reglas de negocio
- ✅ Data Layer: Solo acceso a datos
- ✅ Business Layer: Solo lógica de negocio
- ✅ UI Layer: Solo presentación

**NO hagas:**
- ❌ Acceso directo a BD desde servicios
- ❌ Lógica de negocio en controllers
- ❌ Dependencias de capas externas en capas internas

## Licencia

Parte del sistema Disfruleg - Uso interno
