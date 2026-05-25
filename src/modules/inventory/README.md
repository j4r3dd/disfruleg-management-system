# Inventory Module - Clean Architecture Implementation

## Overview

The Inventory module has been refactored following **Clean Architecture (Onion Architecture)** principles. This ensures maintainability, testability, and separation of concerns.

## Architecture

```
┌─────────────────────────────────────────────┐
│  UI Layer (Controllers/Views)               │
│  - purchase_controller.py                   │
│  - Orchestrates user interactions           │
└──────────────────┬──────────────────────────┘
                   │ depends on
┌──────────────────▼──────────────────────────┐
│  Business Layer (Services)                  │
│  - purchase_service.py                      │
│  - product_service.py                       │
│  - Contains ALL business logic              │
└──────────────────┬──────────────────────────┘
                   │ depends on
┌──────────────────▼──────────────────────────┐
│  Data Layer (Repositories)                  │
│  - repositories.py (interfaces)             │
│  - mysql_repositories.py (implementations)  │
│  - Data access ONLY                         │
└──────────────────┬──────────────────────────┘
                   │ depends on
┌──────────────────▼──────────────────────────┐
│  Domain Layer (Models/Entities)             │
│  - models.py                                │
│  - Pure data structures                     │
│  - No dependencies on other layers          │
└─────────────────────────────────────────────┘
```

## Directory Structure

```
inventory/
├── domain/                    # Domain Layer (innermost)
│   ├── __init__.py
│   └── models.py             # Entities: Product, Purchase, Exceptions
│
├── data/                      # Data Layer
│   ├── __init__.py
│   ├── repositories.py       # Repository Interfaces (Protocols)
│   └── mysql_repositories.py # MySQL Implementations
│
├── business/                  # Business Layer
│   ├── __init__.py
│   ├── purchase_service.py   # Purchase business logic
│   └── product_service.py    # Product business logic
│
├── ui/                        # UI Layer (outermost)
│   ├── __init__.py
│   └── purchase_controller.py # Orchestrates services for UI
│
├── __init__.py                # Module exports
├── purchase_manager.py        # Main entry point with DI
├── registro_compras_original.py # Original view (legacy)
└── README.md                  # This file
```

## Key Principles Applied

### 1. **Clean Architecture (Onion Architecture)**

**Rule:** Inner layers NEVER depend on outer layers.

- ✅ Domain has NO dependencies
- ✅ Data depends ONLY on Domain
- ✅ Business depends on Domain + Data interfaces
- ✅ UI depends on Business + Data interfaces

### 2. **Dependency Injection**

All dependencies are injected via constructors:

```python
# Good ✅
class PurchaseService:
    def __init__(self, purchase_repo: IPurchaseRepository, product_repo: IProductRepository):
        self.purchase_repo = purchase_repo
        self.product_repo = product_repo

# Bad ❌
class PurchaseService:
    def __init__(self):
        self.repo = MySQLPurchaseRepository(conectar())  # Hard-coded dependency
```

### 3. **Interface Segregation**

Repositories implement Protocol interfaces:

```python
# Interface (Protocol)
class IPurchaseRepository(Protocol):
    def get_by_id(self, purchase_id: int) -> Optional[Purchase]: ...
    def create(self, purchase: Purchase) -> int: ...

# Implementation
class MySQLPurchaseRepository:
    def get_by_id(self, purchase_id: int) -> Optional[Purchase]:
        # MySQL-specific implementation
        ...
```

### 4. **Single Responsibility**

Each layer has ONE responsibility:

- **Controllers:** Handle user input, orchestrate services
- **Services:** Business logic ONLY
- **Repositories:** Data access ONLY
- **Models:** Data structures ONLY

### 5. **Fail Fast**

Validate early to catch errors immediately:

```python
def create_purchase(self, id_producto: int, cantidad: Decimal, ...):
    # Fail fast: Validate product exists
    product = self.product_repo.get_by_id(id_producto)
    if product is None:
        raise ProductNotFoundError(f"Product with ID {id_producto} not found")

    # Fail fast: Validate quantities
    if cantidad <= 0:
        raise BusinessLogicError("Purchase quantity must be positive")

    # Proceed with business logic...
```

## Usage

### Basic Usage

```python
from src.modules.inventory import launch_purchase_manager

# Launch the purchase manager
user_data = {
    'nombre_completo': 'John Doe',
    'rol': 'admin'
}

launch_purchase_manager(user_data)
```

### Advanced Usage (Manual DI)

```python
from src.database.conexion import conectar
from src.modules.inventory.data.mysql_repositories import (
    MySQLProductRepository,
    MySQLPurchaseRepository
)
from src.modules.inventory.business import PurchaseService, ProductService
from src.modules.inventory.ui import PurchaseController

# Establish database connection
conn = conectar()

# Layer 1: Data Layer - Repository implementations
product_repo = MySQLProductRepository(conn)
purchase_repo = MySQLPurchaseRepository(conn)

# Layer 2: Business Layer - Services (depend on repositories)
product_service = ProductService(product_repo)
purchase_service = PurchaseService(purchase_repo, product_repo)

# Layer 3: UI Layer - Controller (depends on services)
controller = PurchaseController(purchase_service, product_service)

# Now use the controller
purchases = controller.get_all_purchases()
success, msg, id = controller.create_purchase(
    product_id=1,
    cantidad="10",
    precio="25.50",
    fecha_compra="2025-01-15",
    fecha_registro="2025-01-15",
    incluir_iva=True,
    folio="ABC123",
    proveedor="ACME Corp",
    rfc="ACM130101ABC"
)
```

## Testing

The architecture makes testing easy through dependency injection:

```python
# Mock repository for testing
class MockPurchaseRepository:
    def __init__(self):
        self.purchases = []

    def get_all(self):
        return self.purchases

    def create(self, purchase):
        purchase.id_compra = len(self.purchases) + 1
        self.purchases.append(purchase)
        return purchase.id_compra

# Test with mock
mock_purchase_repo = MockPurchaseRepository()
mock_product_repo = MockProductRepository()

purchase_service = PurchaseService(mock_purchase_repo, mock_product_repo)

# Test business logic without database
purchase_id = purchase_service.create_purchase(...)
assert purchase_id == 1
```

## Business Rules Implemented

### Purchase Validation

1. **Quantity Validation:** Must be positive
2. **Price Validation:** Must be positive
3. **Date Validation:** Cannot be in the future
4. **RFC Validation:** Must match SAT format (3-4 letters + 6 digits + 3 alphanumeric)
5. **Payment Method:** Must be PUE or PPD
6. **Stock Update:** Automatically updates product stock

### Tax Deductibility

1. **Fiscal Info Required:** Must have folio, supplier, and RFC
2. **Cash Limit:** Cash payments > $2,000 are NOT deductible per SAT regulations
3. **IVA Optional:** Can be included or excluded based on deductibility

### Stock Management

1. **Automatic Increment:** Stock increases on purchase creation
2. **Automatic Decrement:** Stock decreases on purchase deletion
3. **Adjustment:** Stock adjusts when purchase quantity is updated

## Migration from Legacy Code

The original `registro_compras.py` has been renamed to `registro_compras_original.py` and is currently still in use by `purchase_manager.py`.

### Next Steps for Complete Migration:

1. ✅ **Domain Layer** - Complete
2. ✅ **Data Layer** - Complete
3. ✅ **Business Layer** - Complete
4. ✅ **UI Controller** - Complete
5. ⏳ **UI View** - Refactor `ComprasApp` to use `PurchaseController`

### To Complete Migration:

Modify the view to use the controller instead of direct database access:

```python
# Instead of:
self.cursor.execute("SELECT * FROM compra...")

# Use:
purchases = self.controller.get_all_purchases()
```

## Benefits of This Architecture

### 1. **Testability**
- Easy to mock dependencies
- Unit test business logic without database
- Integration tests with real repositories

### 2. **Maintainability**
- Clear separation of concerns
- Changes in one layer don't affect others
- Easy to understand and navigate

### 3. **Flexibility**
- Easy to swap implementations (e.g., PostgreSQL instead of MySQL)
- Easy to add new features
- Easy to refactor without breaking existing code

### 4. **Reusability**
- Services can be used by different UIs (CLI, Web, Mobile)
- Repositories can be shared across modules
- Domain models are framework-agnostic

### 5. **Scalability**
- Can add caching layer without changing business logic
- Can add logging/monitoring without changing core code
- Can add authentication/authorization at controller level

## Common Patterns Used

### Repository Pattern
Abstracts data access behind interfaces

### Service Pattern
Encapsulates business logic in reusable services

### Dependency Injection
Injects dependencies via constructors for loose coupling

### Protocol Pattern (Python)
Uses Protocols for interface segregation

### Fail Fast Pattern
Validates early to catch errors immediately

## Contributing

When adding new features, follow these guidelines:

1. **Domain First:** Add entities/exceptions to `domain/models.py`
2. **Data Access:** Add repository methods to interfaces and implementations
3. **Business Logic:** Add to appropriate service in `business/`
4. **UI Orchestration:** Add to `ui/purchase_controller.py`
5. **Never Skip Layers:** Don't call repositories directly from UI

## Questions?

For questions or issues, refer to the clients module (`src/modules/clients`) which follows the same architecture pattern.
