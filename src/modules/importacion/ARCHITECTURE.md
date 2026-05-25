# Importacion Module - Architecture Documentation

## Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI LAYER                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ cotizacion_importer_app.py                                 │ │
│  │                                                            │ │
│  │  - CotizacionImporter (Controller)                        │ │
│  │  - ProgressDialog (UI Component)                          │ │
│  │  - Handles user interactions                              │ │
│  │  - Delegates to services                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ depends on
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BUSINESS LAYER                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ PDFExtractor     │  │ ImportService    │  │ ReportService │ │
│  │ Service          │  │                  │  │               │ │
│  │                  │  │                  │  │               │ │
│  │ - extract_       │  │ - validate_      │  │ - generate_   │ │
│  │   products()     │  │   system_        │  │   report()    │ │
│  │                  │  │   integrity()    │  │               │ │
│  │ - normalize_     │  │ - generate_      │  │               │ │
│  │   unit()         │  │   changes()      │  │               │ │
│  │                  │  │ - apply_         │  │               │ │
│  │ - clean_name()   │  │   changes()      │  │               │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │ depends on
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ IProduct         │  │ IPrice           │  │ ISystem       │ │
│  │ Repository       │  │ Repository       │  │ Repository    │ │
│  │ (Protocol)       │  │ (Protocol)       │  │ (Protocol)    │ │
│  └────────┬─────────┘  └────────┬─────────┘  └───────┬───────┘ │
│           │                     │                     │         │
│           ↓                     ↓                     ↓         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ MySQLProduct     │  │ MySQLPrice       │  │ MySQLSystem   │ │
│  │ Repository       │  │ Repository       │  │ Repository    │ │
│  │                  │  │                  │  │               │ │
│  │ - search_        │  │ - get_all_       │  │ - check_      │ │
│  │   similar()      │  │   groups_with_   │  │   integrity() │ │
│  │ - create_        │  │   discounts()    │  │ - log_import_ │ │
│  │   product()      │  │ - set_price_     │  │   operation() │ │
│  │ - get_by_id()    │  │   all_groups()   │  │               │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │ depends on
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                       DOMAIN LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Models (Pure Business Entities)                          │   │
│  │                                                           │   │
│  │  - ExtractedProduct                                      │   │
│  │  - ProductChange                                         │   │
│  │  - ProductMatch                                          │   │
│  │  - ImportReport                                          │   │
│  │  - SystemIntegrityCheck                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Exceptions (Business Rule Violations)                    │   │
│  │                                                           │   │
│  │  - PDFExtractionError                                    │   │
│  │  - InvalidProductDataError                               │   │
│  │  - ProductMatchError                                     │   │
│  │  - PriceApplicationError                                 │   │
│  │  - ReportGenerationError                                 │   │
│  │  - SystemIntegrityError                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Import Workflow

```
User Action → Controller → Services → Repositories → Database
    ↓
[Select PDF]
    ↓
[Process PDF] → PDFExtractorService.extract_products()
                    ↓
                Returns: List[ExtractedProduct]
    ↓
[Generate Changes] → ImportService.generate_changes()
                        ↓
                    ProductRepository.search_similar()
                        ↓
                    Returns: List[ProductChange]
    ↓
[Show Preview] → Controller displays changes
    ↓
[Apply Changes] → ImportService.apply_changes()
                     ↓
                 ProductRepository.create_product()
                     ↓
                 PriceRepository.set_price_all_groups()
                     ↓
                 SystemRepository.log_import_operation()
    ↓
[Generate Report] → ReportService.generate_report()
    ↓
[Show Success] → Controller displays result
```

## Dependency Injection Flow

```
Controller Construction:
    ↓
CotizacionImporter.__init__(db_connection)
    ↓
    ├─→ product_repo = MySQLProductRepository(db_connection)
    ├─→ price_repo = MySQLPriceRepository(db_connection)
    └─→ system_repo = MySQLSystemRepository(db_connection)
    ↓
    ├─→ pdf_extractor = PDFExtractorService()
    ├─→ import_service = ImportService(product_repo, price_repo, system_repo)
    └─→ report_service = ReportService()
```

## Key Design Patterns

### 1. Repository Pattern
```
Interface (Protocol) → Implementation (MySQL)
    ↑
    │ depends on
    │
Services
```

### 2. Dependency Injection
```
Service receives dependencies through constructor:
    ↓
class ImportService:
    def __init__(self, product_repo, price_repo, system_repo):
        self.product_repo = product_repo
        self.price_repo = price_repo
        self.system_repo = system_repo
```

### 3. Single Responsibility
```
Each class has ONE reason to change:
- Controllers: UI changes
- Services: Business logic changes
- Repositories: Database schema changes
- Models: Business entity definition changes
```

### 4. Fail Fast
```
Validation at method entry:
    ↓
def create_product(self, nombre: str, ...):
    if not nombre or not nombre.strip():
        raise ValueError("Product name cannot be empty")
    # Continue with business logic
```

## Layer Responsibilities

### UI Layer
- **What**: User interface, event handling
- **How**: CustomTkinter widgets, dialogs
- **Depends on**: Business Layer (Services)
- **Used by**: End users

### Business Layer
- **What**: Business logic, workflows
- **How**: Pure Python, no UI or database code
- **Depends on**: Data Layer (Repositories), Domain Layer (Models)
- **Used by**: UI Layer

### Data Layer
- **What**: Database access, queries
- **How**: SQL queries, ORM
- **Depends on**: Domain Layer (Models)
- **Used by**: Business Layer

### Domain Layer
- **What**: Business entities, rules
- **How**: Dataclasses, validation
- **Depends on**: Nothing (pure entities)
- **Used by**: All layers

## Testing Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│ UI Tests (E2E)                                                   │
│ - User interactions                                              │
│ - Full workflow testing                                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│ Integration Tests                                                │
│ - Service + Repository                                           │
│ - Real database operations                                       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│ Unit Tests                                                        │
│ - Services with mock repositories                                │
│ - Domain model validation                                        │
│ - Business logic in isolation                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Benefits

### Testability
- Each layer can be tested independently
- Mock repositories for service testing
- No database needed for business logic tests

### Maintainability
- Clear separation of concerns
- Easy to locate and fix bugs
- Changes in one layer don't affect others

### Scalability
- Easy to add new features
- New services don't affect existing code
- New repository implementations (PostgreSQL, MongoDB, etc.)

### Flexibility
- Swap implementations without changing business logic
- Easy to add new data sources
- UI can be replaced (web, CLI, mobile)

## Comparison with Pricing Module

Both modules follow the same architecture:

```
pricing/                    importacion/
├── domain/                 ├── domain/
│   ├── models.py          │   ├── models.py
│   ├── exceptions.py      │   ├── exceptions.py
│   └── __init__.py        │   └── __init__.py
├── data/                  ├── data/
│   ├── repositories.py    │   ├── repositories.py
│   ├── mysql_repos.py     │   ├── mysql_repos.py
│   └── __init__.py        │   └── __init__.py
├── business/              ├── business/
│   ├── pricing_service.py │   ├── import_service.py
│   └── __init__.py        │   ├── pdf_extractor.py
└── ui/                    │   └── __init__.py
    ├── price_editor.py    └── ui/
    └── __init__.py            ├── importer_app.py
                               └── __init__.py
```

This consistency makes the codebase easier to understand and maintain.
