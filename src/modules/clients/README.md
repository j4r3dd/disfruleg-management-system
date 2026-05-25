# Clients Module - Clean Architecture Implementation

## Overview
This module implements client management following Clean Architecture (Onion Architecture) principles with full dependency injection and SOLID principles.

## Architecture Layers

```
┌─────────────────────────────────────┐
│   UI Layer (ui/)                    │
│   - Controllers                     │
│   - Views                           │
│   - Dialogs                         │
└──────────────┬──────────────────────┘
               │ depends on
┌──────────────▼──────────────────────┐
│   Business Layer (business/)        │
│   - ClientService                   │
│   - GroupService                    │
│   - ClientTypeService               │
└──────────────┬──────────────────────┘
               │ depends on
┌──────────────▼──────────────────────┐
│   Data Layer (data/)                │
│   - IClientRepository (Protocol)    │
│   - IGroupRepository (Protocol)     │
│   - IClientTypeRepository (Protocol)│
│   - MySQL Implementations           │
└──────────────┬──────────────────────┘
               │ depends on
┌──────────────▼──────────────────────┐
│   Domain Layer (domain/)            │
│   - Client (Entity)                 │
│   - Group (Entity)                  │
│   - ClientType (Entity)             │
│   - Business Exceptions             │
└─────────────────────────────────────┘
```

## Key Principles Applied

### 1. Clean Architecture (Onion Architecture)
- **Inner layers never depend on outer layers**
- Domain layer has ZERO dependencies
- Data layer depends only on Domain
- Business layer depends on Domain + Data interfaces
- UI layer depends on Business + Domain

### 2. Dependency Injection
All dependencies are injected through constructors:

```python
# Bad (tight coupling)
class ClientService:
    def __init__(self):
        self.repo = MySQLClientRepository()  # ❌ Direct dependency

# Good (loose coupling)
class ClientService:
    def __init__(self, client_repo: IClientRepository):  # ✅ Injected dependency
        self.repo = client_repo
```

### 3. Interface Segregation
Repositories implement Protocol interfaces:

```python
class IClientRepository(Protocol):
    def get_by_id(self, client_id: int) -> Optional[Client]: ...
    def create(self, client: Client) -> int: ...
    # ... other methods

class MySQLClientRepository:  # Implements IClientRepository
    def get_by_id(self, client_id: int) -> Optional[Client]:
        # MySQL-specific implementation
```

### 4. Single Responsibility
Each class has ONE responsibility:

- **Controllers**: Handle user input, orchestrate services
- **Services**: Business logic ONLY
- **Repositories**: Data access ONLY
- **Models**: Data structures ONLY

### 5. Fail Fast
All methods validate inputs immediately:

```python
def create_client(self, nombre_cliente: str, id_grupo: int):
    # Validate early
    if not nombre_cliente or not nombre_cliente.strip():
        raise ValueError("Client name cannot be empty")

    if id_grupo is None or id_grupo <= 0:
        raise ValueError("Group ID must be a positive integer")

    # Proceed with business logic
    ...
```

## Module Structure

```
src/modules/clients/
├── domain/                     # Domain Layer (Pure Business Entities)
│   ├── __init__.py
│   └── models.py              # Client, Group, ClientType entities + Exceptions
│
├── data/                       # Data Layer (Repository Pattern)
│   ├── __init__.py
│   ├── repositories.py        # Repository interfaces (Protocols)
│   └── mysql_repositories.py  # MySQL implementations
│
├── business/                   # Business Layer (Services)
│   ├── __init__.py
│   ├── client_service.py      # Client business logic
│   ├── group_service.py       # Group business logic
│   └── client_type_service.py # Client type business logic
│
├── ui/                         # UI Layer (Controllers & Views)
│   ├── __init__.py
│   ├── client_controller.py   # Orchestrates user actions
│   ├── client_view.py         # UI components
│   └── dialogs.py             # Dialog windows
│
├── __init__.py                 # Module exports
├── client_manager_refactored.py # Main entry point (Composition Root)
├── client_manager.py           # [DEPRECATED] Old implementation
└── README.md                   # This file
```

## Usage

### Basic Usage

```python
from src.modules.clients import launch_client_manager

# Launch the client manager
launch_client_manager()
```

### Dependency Injection (Composition Root)

The `client_manager_refactored.py` file is the **Composition Root** where all dependencies are wired:

```python
def launch_client_manager():
    conn = conectar()  # Get DB connection

    # Layer 1: Create repositories
    client_repo = MySQLClientRepository(conn)
    group_repo = MySQLGroupRepository(conn)
    client_type_repo = MySQLClientTypeRepository(conn)

    # Layer 2: Create services (inject repositories)
    client_service = ClientService(client_repo, group_repo)
    group_service = GroupService(group_repo, client_type_repo)
    client_type_service = ClientTypeService(client_type_repo)

    # Layer 3: Create controller (inject services)
    controller = ClientController(
        client_service,
        group_service,
        client_type_service
    )

    # Layer 4: Create view (inject controller)
    root = ctk.CTk()
    view = ClientManagerView(root, controller)
    root.mainloop()
```

## Features

### Client Management
- ✅ Create, read, update, delete clients
- ✅ Toggle client active/inactive status
- ✅ Search and filter clients
- ✅ Validate email and RFC formats
- ✅ Fiscal information management
- ✅ Check for invoices before deletion

### Group Management
- ✅ Create, read, update, delete groups
- ✅ Assign client types to groups
- ✅ Prevent deletion if group is in use
- ✅ Group-based client organization

### Client Type Management
- ✅ Create, read, update, delete client types
- ✅ Define discount percentages (0-100%)
- ✅ Prevent deletion if type is in use

## Domain Entities

### Client
```python
@dataclass
class Client:
    id_cliente: Optional[int]
    nombre_cliente: str       # Required
    id_grupo: int            # Required
    activo: bool = True
    telefono: Optional[str] = None
    correo: Optional[str] = None
    rfc: Optional[str] = None
    razon_social: Optional[str] = None
    regimen_fiscal: Optional[str] = None
    codigo_postal: Optional[str] = None
    direccion_fiscal: Optional[str] = None
    notas: Optional[str] = None
```

### Group
```python
@dataclass
class Group:
    id_grupo: Optional[int]
    clave_grupo: str          # Required
    descripcion: Optional[str]
    id_tipo_cliente: int      # Required
```

### ClientType
```python
@dataclass
class ClientType:
    id_tipo_cliente: Optional[int]
    nombre_tipo: str          # Required
    descuento: Decimal        # Required (0-100)
```

## Business Exceptions

All business exceptions inherit from `BusinessLogicError`:

- `ClientNotFoundError` - Client doesn't exist
- `GroupNotFoundError` - Group doesn't exist
- `ClientTypeNotFoundError` - Client type doesn't exist
- `ClientHasInvoicesError` - Cannot delete client with invoices
- `GroupInUseError` - Cannot delete group in use
- `ClientTypeInUseError` - Cannot delete type in use

## Testing

The architecture makes testing easy through dependency injection:

```python
# Mock repository for testing
class MockClientRepository:
    def __init__(self):
        self.clients = {}

    def get_by_id(self, client_id):
        return self.clients.get(client_id)

    def create(self, client):
        client_id = len(self.clients) + 1
        self.clients[client_id] = client
        return client_id

# Test service with mock
def test_create_client():
    mock_repo = MockClientRepository()
    mock_group_repo = MockGroupRepository()
    service = ClientService(mock_repo, mock_group_repo)

    client = service.create_client("Test Client", 1)
    assert client.nombre_cliente == "Test Client"
```

## Migration from Old Code

The old `client_manager.py` (1780 lines) has been refactored into clean architecture with proper separation of concerns:

**Before:**
- ❌ 1780 lines in single file
- ❌ Direct database calls in UI code
- ❌ Business logic mixed with UI
- ❌ Hard to test
- ❌ Tight coupling

**After:**
- ✅ Modular architecture (4 layers, 12 files)
- ✅ Clear separation of concerns
- ✅ Business logic isolated in services
- ✅ Easy to test with dependency injection
- ✅ Loose coupling through interfaces

## Benefits

1. **Maintainability**: Each layer has a single responsibility
2. **Testability**: Easy to mock dependencies
3. **Flexibility**: Can swap implementations (e.g., MySQL → PostgreSQL)
4. **Scalability**: Easy to add new features
5. **Type Safety**: Full type hints throughout
6. **Error Handling**: Fail-fast validation with clear exceptions

## Future Improvements

1. Add unit tests for all services
2. Add integration tests for repositories
3. Implement caching layer
4. Add audit logging
5. Implement undo/redo functionality
6. Add data export/import features
