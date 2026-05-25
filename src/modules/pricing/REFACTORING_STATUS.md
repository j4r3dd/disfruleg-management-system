# 🚧 Pricing Module Refactoring - STATUS

## Summary

Successfully refactored the monolithic `price_editor.py` (1,733 lines) into **Clean Architecture** layers.

---

## ✅ COMPLETED

### **Architecture Created**

```
pricing/
├── domain/                    ✅ COMPLETE (3 files, ~200 lines)
│   ├── __init__.py           - Exports
│   ├── models.py             - Entities (Product, Group, ClientType, PriceByGroup, ProductPrice, ProductLock)
│   └── exceptions.py         - Business exceptions (6 types)
│
├── data/                      ✅ COMPLETE (3 files, ~800 lines)
│   ├── __init__.py           - Exports
│   ├── repositories.py       - Interfaces (5 protocols)
│   └── mysql_repositories.py - MySQL implementations
│
├── business/                  ✅ COMPLETE (3 files, ~400 lines)
│   ├── __init__.py           - Exports
│   ├── product_service.py    - Product business logic
│   └── pricing_service.py    - Pricing business logic
│
├── ui/                        ⚠️ NEEDS MIGRATION (1,100 lines to migrate)
│   ├── __init__.py           - Exports
│   └── price_editor_app.py   - TO BE CREATED (migrate UI from old_price_editor.py)
│
├── price_manager.py           ✅ COMPLETE (~100 lines)
│   - Entry point with full Dependency Injection
│
└── old_price_editor.py        ✅ BACKED UP (original monolith)
    - DO NOT USE - kept for reference only
```

---

## 🎯 Key Principles Applied

### 1. **Clean Architecture (Onion)**
```
UI → Business → Data → Domain
(Outer layers depend on inner, NEVER the reverse)
```

### 2. **Dependency Injection**
```python
# All dependencies injected via constructor
product_service = ProductService(product_repo, lock_repo)
pricing_service = PricingService(price_repo, group_repo, client_type_repo, product_repo)
```

### 3. **Interface Segregation**
```python
class IProductRepository(Protocol):  # Interface
    def get_all(...): ...

class MySQLProductRepository:  # Implementation
    def get_all(...): ...
```

### 4. **Single Responsibility**
- **Domain**: Pure entities and exceptions
- **Data**: Database access ONLY
- **Business**: Business logic ONLY
- **UI**: User interface and coordination

### 5. **Fail Fast**
```python
# Validate immediately in domain models __post_init__
if self.precio_base < 0:
    raise InvalidPriceError("Base price cannot be negative")
```

---

## 📋 TODO: Complete UI Migration

### **What Needs to Be Done**

The `old_price_editor.py` contains ~1,100 lines of UI code that needs to be migrated to `ui/price_editor_app.py`:

#### **1. Extract Pure UI Components**
From `old_price_editor.py`, extract these sections into `ui/price_editor_view.py`:
- `create_interface()` - Main UI layout
- `create_header()` - Header with user info
- `create_controls_section()` - Search and controls
- `create_group_buttons()` - Group selector
- `create_main_content()` - Product table
- `create_table_header_improved()` - Table headers
- `create_product_row_improved()` - Product rows
- `create_status_bar()` - Status bar
- Dialog methods: `add_product_dialog()`, `edit_product_price()`, `verify_admin_password()`

#### **2. Create Application Controller**
In `ui/price_editor_app.py`, create `PriceEditorApplication` class:

```python
class PriceEditorApplication:
    def __init__(
        self,
        root,
        user_data: dict,
        product_service: ProductService,
        pricing_service: PricingService,
        filtro_productos=None
    ):
        self.product_service = product_service
        self.pricing_service = pricing_service
        self.filtro_productos = filtro_productos

        # Create view
        self.view = PriceEditorView(root, user_data)

        # Connect callbacks
        self._connect_callbacks()

        # Load initial data
        self._load_initial_data()
```

#### **3. Migrate Event Handlers**
Move these methods from `old_price_editor.py` to the application controller:
- `on_group_change()` - When group selector changes
- `load_products()` - Load products for selected group
- `filter_products()` - Search/filter products
- `handle_add_product()` - Create new product
- `handle_edit_price()` - Edit product price
- `handle_delete_product()` - Delete product
- `handle_save_price()` - Save price changes

#### **4. Connect Services to Handlers**
Replace direct database calls with service calls:

**Before (Monolithic)**:
```python
self.cursor.execute("""
    SELECT * FROM producto WHERE id_producto = %s
""", (product_id,))
```

**After (Clean Architecture)**:
```python
product = self.product_service.get_product_by_id(product_id)
```

---

## 🔄 Migration Pattern

### **Example: Edit Price Flow**

#### **Old Monolithic Code**:
```python
def edit_product_price(self, event, product=None):
    # UI code mixed with business logic and database access
    product_id = product['id_producto']

    # Direct database access
    self.cursor.execute("""
        SELECT precio_base FROM precio_por_grupo
        WHERE id_producto = %s AND id_grupo = %s
    """, (product_id, group_id))
    result = self.cursor.fetchone()

    # Show dialog
    popup = ctk.CTkToplevel(...)
    # ...more UI code...

    # Save changes - direct database access
    self.cursor.execute("""
        UPDATE precio_por_grupo SET precio_base = %s
        WHERE id_producto = %s AND id_grupo = %s
    """, (new_price, product_id, group_id))
    self.conn.commit()
```

#### **New Clean Architecture**:

**View (`price_editor_view.py`)**:
```python
def show_edit_price_dialog(self, product, current_price, client_type):
    """Pure UI - Show dialog for editing price"""
    popup = ctk.CTkToplevel(...)
    # ...UI code only...

    # When user clicks save:
    if self.on_save_price:
        self.on_save_price(product_id, new_price)
```

**Application Controller (`price_editor_app.py`)**:
```python
def handle_edit_price(self, product):
    """Coordinate view with services"""
    try:
        # Get data from services
        product_id = product.id_producto
        group_id = self.current_group_id

        current_price = self.pricing_service.get_base_price(
            product_id,
            group_id
        )

        client_type = self.pricing_service.get_client_type_for_group(group_id)

        # Show view
        self.view.show_edit_price_dialog(product, current_price, client_type)

    except Exception as e:
        self.view.show_error(f"Error: {str(e)}")

def handle_save_price(self, product_id, new_price):
    """Save price using service"""
    try:
        self.pricing_service.set_base_price(
            product_id,
            self.current_group_id,
            new_price
        )

        self.view.show_success("Price updated successfully")
        self.handle_refresh()

    except Exception as e:
        self.view.show_error(f"Error saving price: {str(e)}")
```

**Service (Already Created)**:
```python
def set_base_price(self, product_id, group_id, base_price):
    """Business logic ONLY"""
    # Fail fast validations
    product = self.product_repo.get_by_id(product_id)
    if not product:
        raise ProductNotFoundError(...)

    if base_price < 0:
        raise InvalidPriceError(...)

    # Save using repository
    return self.price_repo.set_base_price(product_id, group_id, base_price)
```

---

## 🎯 Entry Point Usage

```python
# In main.py or wherever price editor is launched:
from src.modules.pricing.price_manager import launch_price_editor

user_data = {
    'nombre_completo': 'John Doe',
    'username': 'jdoe',
    'rol': 'admin'
}

# Optional: filter specific products
filtro_productos = [1, 2, 3, 45, 67]  # or None for all products

launch_price_editor(user_data, filtro_productos)
```

---

## 📊 Progress

- ✅ Domain Layer: **100% Complete**
- ✅ Data Layer: **100% Complete**
- ✅ Business Layer: **100% Complete**
- ⚠️ UI Layer: **0% Complete** (needs migration)
- ✅ Entry Point: **100% Complete**

**Total Progress**: **75% Complete**

---

## 🚀 Next Steps

1. **Create `ui/price_editor_view.py`**:
   - Extract all UI methods from `old_price_editor.py`
   - Remove all business logic and database calls
   - Add callbacks for user actions

2. **Create `ui/price_editor_app.py`**:
   - Create `PriceEditorApplication` class
   - Implement event handlers
   - Connect services to handlers
   - Connect view callbacks

3. **Test the Application**:
   - Run via `price_manager.py`
   - Verify all features work
   - Test with different user roles
   - Test with product filters

4. **Delete Old File** (after testing):
   - Once fully migrated and tested
   - Remove `old_price_editor.py`

---

## 📚 Benefits Achieved So Far

| Benefit | Status |
|---------|--------|
| **Clean separation of concerns** | ✅ Done |
| **Testability** | ✅ Services are testable |
| **Maintainability** | ✅ Clear structure |
| **Reusability** | ✅ Services can be reused |
| **Flexibility** | ✅ Can swap repositories |
| **Scalability** | ✅ Easy to add features |

---

**Status**: ✅ **Architecture Complete - UI Migration Pending**
**Created By**: Claude (Anthropic)
**Date**: 2025-01-06
