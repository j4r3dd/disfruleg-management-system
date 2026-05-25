# Importacion Module - Clean Architecture

## Architecture Overview

This module follows Clean Architecture (Onion Architecture) principles:

```
UI Layer (Controllers/Views)
    ↓ depends on
Business Layer (Services)
    ↓ depends on
Data Layer (Repositories)
    ↓ depends on
Domain Layer (Models/Entities)
```

**Rule: Inner layers never depend on outer layers.**

## Directory Structure

```
importacion/
├── domain/              # Domain Layer (Core Business Entities)
│   ├── models.py        # Business entities
│   ├── exceptions.py    # Domain exceptions
│   └── __init__.py
│
├── data/                # Data Layer (Data Access)
│   ├── repositories.py  # Repository interfaces (Protocols)
│   ├── mysql_repositories.py  # MySQL implementations
│   └── __init__.py
│
├── business/            # Business Layer (Business Logic)
│   ├── pdf_extractor_service.py  # PDF extraction logic
│   ├── import_service.py         # Main import workflow
│   ├── report_service.py         # Report generation
│   └── __init__.py
│
├── ui/                  # UI Layer (User Interface)
│   ├── cotizacion_importer_app.py  # UI controller
│   └── __init__.py
│
├── __init__.py          # Module entry point
└── README.md            # This file
```

## Key Principles Applied

### 1. Clean Architecture (Onion Architecture)

Each layer has a specific responsibility:

- **Domain Layer**: Pure business entities, no dependencies
- **Data Layer**: Database access through repositories
- **Business Layer**: Business logic, uses repositories
- **UI Layer**: User interface, uses services

### 2. Dependency Injection

Services receive dependencies through constructor injection:

```python
# Good - Dependencies injected
class ImportService:
    def __init__(
        self,
        product_repo: IProductRepository,
        price_repo: IPriceRepository,
        system_repo: ISystemRepository
    ):
        self.product_repo = product_repo
        self.price_repo = price_repo
        self.system_repo = system_repo
```

### 3. Interface Segregation

Repositories are defined as protocols (interfaces):

```python
class IProductRepository(Protocol):
    def search_similar(self, nombre: str, unidad: str) -> Optional[ProductMatch]: ...
    def create_product(self, nombre: str, unidad: str) -> int: ...
```

Concrete implementations:

```python
class MySQLProductRepository:
    def __init__(self, connection):
        self.conn = connection

    def search_similar(self, nombre: str, unidad: str) -> Optional[ProductMatch]:
        # MySQL implementation
        ...
```

### 4. Single Responsibility Principle

Each class has one responsibility:

- **Controllers**: Handle user input, orchestrate services
- **Services**: Business logic ONLY
- **Repositories**: Data access ONLY
- **Models**: Data structures ONLY

### 5. Fail Fast

Validation happens early:

```python
def extract_products(self, pdf_path: str) -> List[ExtractedProduct]:
    # Fail fast: Validate input
    if not pdf_path:
        raise ValueError("PDF path cannot be empty")

    # Proceed with business logic
    ...
```

## Domain Layer

### Models

**ExtractedProduct**: Product data extracted from PDF
- nombre: str
- unidad: str
- precio: Decimal
- tiene_precio: bool

**ProductChange**: Proposed change to apply
- tipo: str ('nuevo' or 'actualizar')
- nombre: str
- unidad: str
- precio_nuevo: Decimal
- tiene_precio: bool
- stock: Decimal
- id_producto: Optional[int]

**ProductMatch**: Matched product from database
- id: int
- nombre: str
- unidad: str
- stock: Decimal

**ImportReport**: Import operation results
- fecha: datetime
- usuario: str
- archivo_pdf: str
- productos_procesados: int
- productos_nuevos: int
- productos_actualizados: int
- productos_sin_precio: int
- grupos_afectados: int

**SystemIntegrityCheck**: System validation results
- grupos_sin_tipo: list
- descuentos_invalidos: list
- tiene_advertencias: bool

### Exceptions

All exceptions inherit from `ImportacionDomainError`:
- PDFExtractionError
- InvalidProductDataError
- ProductMatchError
- PriceApplicationError
- ReportGenerationError
- SystemIntegrityError

## Data Layer

### Repository Interfaces

**IProductRepository**: Product data access
- search_similar()
- create_product()
- get_by_id()

**IPriceRepository**: Price data access
- get_all_groups_with_discounts()
- set_price_for_group()
- set_price_all_groups()

**ISystemRepository**: System operations
- check_integrity()
- log_import_operation()

### MySQL Implementations

- MySQLProductRepository
- MySQLPriceRepository
- MySQLSystemRepository

## Business Layer

### Services

**PDFExtractorService**: PDF extraction logic
- extract_products(): Extract products from PDF
- Pure business logic, no database access

**ImportService**: Main import workflow
- validate_system_integrity()
- generate_changes()
- apply_changes()
- get_statistics()

**ReportService**: Report generation
- generate_report(): Create detailed import report
- Pure business logic, file system access only

## UI Layer

### Controller

**CotizacionImporter**: UI controller
- Handles user interface
- Delegates to services
- No business logic

## Usage Example

```python
from modules.importacion import abrir_importador_cotizaciones

# Open from dashboard
abrir_importador_cotizaciones(parent_window, db_connection, user_info)
```

## Dependencies

### External
- customtkinter: UI framework
- PyMuPDF (fitz): PDF parsing
- pymysql: Database connection

### Internal
- src.utils: Normalization utilities (optional)

## Testing Strategy

### Unit Tests
- Domain models validation
- Service logic
- Repository queries

### Integration Tests
- End-to-end import workflow
- Database operations
- PDF extraction

### UI Tests
- User interactions
- Error handling
- Progress feedback

## Migration from Old Code

The old `cotizacion_importer.py` was a monolithic file mixing:
- UI code
- Business logic
- Database access
- PDF extraction

Now refactored into:
- **Domain**: Business entities
- **Data**: Database access through repositories
- **Business**: Business logic in services
- **UI**: User interface only

## Benefits

1. **Testability**: Each layer can be tested independently
2. **Maintainability**: Clear separation of concerns
3. **Flexibility**: Easy to swap implementations (e.g., different databases)
4. **Scalability**: Easy to add new features
5. **Readability**: Each file has a single, clear purpose

## Future Enhancements

- Add unit tests for all services
- Implement caching for repository queries
- Add support for multiple PDF formats
- Implement async/await for long operations
- Add event publishing for system integration
