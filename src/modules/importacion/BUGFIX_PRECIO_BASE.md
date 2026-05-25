# Bug Fix: Precio Base Calculation

## Issue

When importing prices from PDF, the module was incorrectly applying discounts to the `precio_base` column instead of keeping it constant across all groups.

### Example of the Bug:

**Aguacate @ $50**

**Before (WRONG):**
- Group A0 (0% discount): `precio_base = $50`, `precio_final = $50` ✓
- Group C50 (50% discount): `precio_base = $25`, `precio_final = $12.50` ❌

**After (CORRECT):**
- Group A0 (0% discount): `precio_base = $50`, `precio_final = $50` ✓
- Group C50 (50% discount): `precio_base = $50`, `precio_final = $25` ✓

## Root Cause

In `data/mysql_repositories.py`, the `set_price_all_groups()` method was calculating a discounted price and storing it in the `precio_base` column:

```python
# WRONG - Old code
precio_con_descuento = precio_base * (Decimal('1') - Decimal(str(descuento)) / Decimal('100'))
cursor.execute("""
    INSERT INTO precio_por_grupo (id_producto, id_grupo, precio_base)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE precio_base = %s
""", (product_id, id_grupo, precio_con_descuento, precio_con_descuento))
```

## Solution

The `precio_base` should be the same for all groups. The discount is applied at **query time** when calculating `precio_final`.

```python
# CORRECT - New code
cursor.execute("""
    INSERT INTO precio_por_grupo (id_producto, id_grupo, precio_base)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE precio_base = %s
""", (product_id, id_grupo, precio_base, precio_base))
```

## Database Schema

The correct schema is:

```
precio_por_grupo:
  - id_producto (FK)
  - id_grupo (FK)
  - precio_base (SAME for all groups)

grupo:
  - id_grupo (PK)
  - id_tipo_cliente (FK)

tipo_cliente:
  - id_tipo_cliente (PK)
  - descuento (percentage)

# When querying:
precio_final = precio_base * (1 - descuento / 100)
```

## Files Modified

1. `src/modules/importacion/data/mysql_repositories.py`
   - Fixed `MySQLPriceRepository.set_price_all_groups()` method
   - Removed discount calculation
   - Now sets same `precio_base` for all groups

2. `src/modules/importacion/ui/cotizacion_importer_app.py`
   - Added comment clarifying tuple format
   - Preview dialog correctly shows discount calculation

## Impact

- ✅ Prices now work correctly across all groups
- ✅ Compatible with pricing module behavior
- ✅ Discounts are applied correctly at display time
- ✅ No database migration needed (old incorrect data will be overwritten on next import)

## Testing

To verify the fix:

1. Import a PDF with products
2. Open the pricing module
3. Check a product's prices across different groups
4. Verify:
   - `precio_base` is the same for all groups
   - `precio_final` = `precio_base * (1 - discount/100)`

## Date

Fixed: November 10, 2024
