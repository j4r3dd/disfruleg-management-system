# Migration Guide - Importacion Module

## Overview

The importacion module has been refactored from a monolithic design to Clean Architecture.

**Old Structure**: Single file `cotizacion_importer.py` (1385 lines)
**New Structure**: Organized in 4 layers across 12 files

## What Changed?

### Old Code (cotizacion_importer.py)
- Mixed UI, business logic, and database access
- Hard to test
- Hard to maintain
- Tight coupling between components

### New Code (Clean Architecture)
- Separated into 4 distinct layers
- Easy to test each layer independently
- Easy to maintain and extend
- Loose coupling through dependency injection

## File Mapping

### Domain Layer (NEW)
These are new files containing business entities:

```
domain/
├── models.py           # Business entities (ExtractedProduct, ProductChange, etc.)
├── exceptions.py       # Domain exceptions
└── __init__.py
```

### Data Layer (NEW)
These replace direct database calls:

```
data/
├── repositories.py     # Repository interfaces
├── mysql_repositories.py  # MySQL implementations
└── __init__.py
```

**Before:**
```python
cursor.execute("SELECT * FROM producto WHERE ...")
```

**After:**
```python
product = self.product_repo.search_similar(nombre, unidad)
```

### Business Layer (NEW)
Business logic extracted from old code:

```
business/
├── pdf_extractor_service.py    # PDF extraction (lines 552-616 from old file)
├── import_service.py           # Import workflow (lines 662-796, 1122-1320)
├── report_service.py           # Report generation (lines 1017-1120)
└── __init__.py
```

### UI Layer (REFACTORED)
UI code cleaned up and focused:

```
ui/
├── cotizacion_importer_app.py  # UI controller (refactored from lines 172-1360)
└── __init__.py
```

## Code Changes Required

### Importing the Module

**Before:**
```python
from modules.importacion.cotizacion_importer import CotizacionImporter, abrir_importador_cotizaciones
```

**After:**
```python
from modules.importacion import CotizacionImporter, abrir_importador_cotizaciones
```

### Usage (UNCHANGED)

The public API remains the same:

```python
# This still works exactly the same way
abrir_importador_cotizaciones(parent, db, user_info)
```

## Breaking Changes

### None for External Users

If you were using the module through `abrir_importador_cotizaciones()`, **no changes needed**.

### For Internal Development

If you were directly accessing internal methods, you'll need to update:

**Before:**
```python
from modules.importacion.cotizacion_importer import CotizacionImporter

importer = CotizacionImporter(parent, db, user_info)
productos = importer.extraer_productos_pdf(pdf_path)
```

**After:**
```python
from modules.importacion import CotizacionImporter
from modules.importacion.business import PDFExtractorService

importer = CotizacionImporter(parent, db, user_info)
# OR for direct service access:
extractor = PDFExtractorService()
productos = extractor.extract_products(pdf_path)
```

## Benefits of New Architecture

### 1. Testability

**Before**: Hard to test because everything is mixed together
**After**: Each layer can be tested independently

```python
# Test services without database
def test_pdf_extraction():
    service = PDFExtractorService()
    products = service.extract_products("test.pdf")
    assert len(products) > 0

# Test with mock repositories
def test_import_service():
    mock_repo = MockProductRepository()
    service = ImportService(mock_repo, ...)
    changes = service.generate_changes(products, True, True)
    assert len(changes) > 0
```

### 2. Maintainability

**Before**: 1385 lines in one file
**After**: ~150-300 lines per file, clear responsibilities

### 3. Extensibility

**Before**: Hard to add new features without breaking existing code
**After**: Easy to add new services, repositories, or models

Example - Adding Excel import:
```python
# New service in business layer
class ExcelExtractorService:
    def extract_products(self, excel_path: str) -> List[ExtractedProduct]:
        # Implementation
        pass

# Use same ImportService, just inject new extractor
```

### 4. Flexibility

**Before**: Locked into MySQL
**After**: Easy to swap database implementations

```python
# Switch from MySQL to PostgreSQL
postgres_repo = PostgreSQLProductRepository(connection)
service = ImportService(postgres_repo, ...)
```

## Testing Strategy

### Unit Tests (NEW)
```python
# Test domain models
def test_extracted_product_validation():
    with pytest.raises(InvalidProductDataError):
        ExtractedProduct(nombre="", unidad="kg", precio=Decimal("10"), tiene_precio=True)

# Test services
def test_import_service_generate_changes():
    # Test with mock repositories
    pass
```

### Integration Tests (NEW)
```python
# Test with real database
def test_mysql_product_repository():
    repo = MySQLProductRepository(db_connection)
    product = repo.search_similar("Aguacate", "kg")
    assert product is not None
```

### UI Tests (UNCHANGED)
```python
# Test UI interactions
def test_cotizacion_importer_ui():
    app = CotizacionImporter(None, db, user_info)
    app.seleccionar_pdf()
    # ...
```

## Rollback Plan

The old `cotizacion_importer.py` file is still present in the module directory.

To rollback:

1. Rename new files:
   ```bash
   mv __init__.py __init__.py.new
   mv cotizacion_importer.py cotizacion_importer.py.old
   ```

2. Restore old imports in `__init__.py`:
   ```python
   from .cotizacion_importer import CotizacionImporter, abrir_importador_cotizaciones
   ```

## Verification Checklist

After migration, verify:

- [ ] Module imports correctly: `from modules.importacion import abrir_importador_cotizaciones`
- [ ] PDF selection works
- [ ] PDF processing extracts products correctly
- [ ] Changes preview displays correctly
- [ ] Price application works across all groups
- [ ] Report generation creates files
- [ ] Error handling works properly
- [ ] System integrity validation runs
- [ ] No regression in existing functionality

## Support

If you encounter issues:

1. Check the README.md for architecture details
2. Review the old cotizacion_importer.py for reference
3. Check error messages - they now include more context
4. Enable debug logging to see service interactions

## Timeline

- **Phase 1** (Complete): Refactor to Clean Architecture
- **Phase 2** (Next): Add comprehensive unit tests
- **Phase 3** (Future): Add integration tests
- **Phase 4** (Future): Remove old cotizacion_importer.py file

## Questions?

Refer to:
- README.md - Architecture documentation
- modules/pricing/ - Reference implementation
- Key principles document in project root
