# 🧪 Pricing Module - Testing Guide

## Quick Start Testing

### 1. **Test Services Directly (Unit Testing)**

```python
from src.modules.pricing import ProductService, PricingService
from src.modules.pricing.data.mysql_repositories import *
from src.database.conexion import conectar
from decimal import Decimal

# Setup
conn = conectar()

# Initialize repositories
product_repo = MySQLProductRepository(conn)
lock_repo = MySQLLockRepository(conn)
price_repo = MySQLPriceRepository(conn)
group_repo = MySQLGroupRepository(conn)
client_type_repo = MySQLClientTypeRepository(conn)

# Initialize services
product_service = ProductService(product_repo, lock_repo)
pricing_service = PricingService(
    price_repo,
    group_repo,
    client_type_repo,
    product_repo
)

# Test 1: Create a product
print("Test 1: Creating product...")
try:
    product_id = product_service.create_product(
        nombre_producto="Test Product XYZ",
        unidad_producto="PIEZA",
        stock=Decimal("100.00"),
        es_especial=False
    )
    print(f"✅ Product created with ID: {product_id}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Get all products
print("\nTest 2: Getting all products...")
try:
    products = product_service.get_all_products()
    print(f"✅ Found {len(products)} products")
    if products:
        print(f"   First product: {products[0].nombre_producto}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Set price for a group
print("\nTest 3: Setting price for group 1...")
try:
    pricing_service.set_base_price(
        product_id=product_id,
        group_id=1,
        base_price=Decimal("25.50")
    )
    print(f"✅ Price set successfully")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Get product prices for group
print("\nTest 4: Getting prices for group 1...")
try:
    prices = pricing_service.get_product_prices_for_group(group_id=1)
    print(f"✅ Found {len(prices)} products with prices")
    for price in prices[:3]:  # Show first 3
        print(f"   {price.nombre_producto}: ${price.precio_base} → ${price.precio_final}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Calculate price preview
print("\nTest 5: Calculating price preview...")
try:
    final_price, client_type = pricing_service.calculate_final_price(
        base_price=Decimal("100.00"),
        group_id=1
    )
    print(f"✅ Base: $100.00 → Final: ${final_price} (Discount: {client_type.descuento}%)")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Search products
print("\nTest 6: Searching products...")
try:
    results = product_service.search_products(query="test")
    print(f"✅ Found {len(results)} products matching 'test'")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 7: Product locking
print("\nTest 7: Testing product locks...")
try:
    product_service.acquire_product_lock(
        product_id=product_id,
        usuario="TestUser",
        modulo="Testing"
    )
    print(f"✅ Lock acquired successfully")

    product_service.release_product_lock(product_id)
    print(f"✅ Lock released successfully")
except Exception as e:
    print(f"❌ Error: {e}")

# Cleanup
conn.close()
print("\n✅ All tests completed!")
```

---

### 2. **Test Full Application (Integration Testing)**

```python
from src.modules.pricing import launch_price_editor

# Test user data
test_user = {
    'nombre_completo': 'Test User',
    'username': 'testuser',
    'rol': 'admin'  # or 'usuario' for regular user
}

# Launch without filter (all products)
print("Launching price editor with all products...")
launch_price_editor(test_user)

# Launch with filter (specific products)
print("Launching price editor with filtered products...")
filtro_productos = [1, 2, 3, 4, 5]
launch_price_editor(test_user, filtro_productos)
```

---

## Manual Testing Checklist

### **Group Management** ✅

- [ ] Click different group buttons
- [ ] Verify products reload for each group
- [ ] Check client type info updates correctly
- [ ] Verify client count displays

### **Product Display** ✅

- [ ] Verify all products show correctly
- [ ] Check special products have special color
- [ ] Check products without price have red color
- [ ] Verify table headers align with columns
- [ ] Check alternating row colors

### **Search & Filter** ✅

- [ ] Type in search box - products filter in real-time
- [ ] Clear search - all products return
- [ ] Click "Quitar Filtro" if filter banner shows
- [ ] Verify search works case-insensitive

### **Add Product** ✅

- [ ] Click "➕ Agregar Producto"
- [ ] Enter product name (required)
- [ ] Enter unit (required)
- [ ] Enter stock (optional, defaults to 0)
- [ ] Check "Producto Especial" checkbox
- [ ] Click "Guardar"
- [ ] Verify product appears in list
- [ ] Try duplicate name - should show error

### **Edit Price** ✅

- [ ] Double-click a product row
- [ ] OR select product and click "✏️ Editar"
- [ ] Verify current price shows
- [ ] Enter new price
- [ ] Check price preview updates in real-time
- [ ] Click "Guardar Cambios"
- [ ] Verify product list updates with new price

### **Special Products** ✅

- [ ] Try to edit special product as regular user
- [ ] Verify admin password prompt appears
- [ ] Enter correct admin password
- [ ] Verify edit proceeds
- [ ] Try with wrong password
- [ ] Verify edit is blocked

### **Delete Product** (Admin Only) ✅

- [ ] Select a product
- [ ] Click "🗑️ Eliminar Producto"
- [ ] Verify confirmation dialog
- [ ] Verify admin password prompt
- [ ] Enter admin password
- [ ] Confirm deletion
- [ ] Verify product removed from list

### **Row Interactions** ✅

- [ ] Hover over row - changes color to blue
- [ ] Leave row - returns to original color
- [ ] Single click - selects product
- [ ] Double click - opens edit dialog

### **Window Behavior** ✅

- [ ] Window appears on top initially
- [ ] Click "⎋" back button - window closes
- [ ] Close window with X - locks are released
- [ ] Verify no crashes or errors

---

## Error Testing

### **Validation Errors** ✅

```python
# Test 1: Empty product name
product_service.create_product(
    nombre_producto="",  # Should fail
    unidad_producto="PIEZA"
)
# Expected: ValueError: Product name cannot be empty

# Test 2: Negative price
pricing_service.set_base_price(
    product_id=1,
    group_id=1,
    base_price=Decimal("-10.00")  # Should fail
)
# Expected: InvalidPriceError: Base price cannot be negative

# Test 3: Invalid product ID
product_service.get_product_by_id(-1)  # Should fail
# Expected: ValueError: Product ID must be positive

# Test 4: Non-existent product
pricing_service.set_base_price(
    product_id=999999,  # Doesn't exist
    group_id=1,
    base_price=Decimal("10.00")
)
# Expected: ProductNotFoundError: Product 999999 not found
```

### **Lock Errors** ✅

```python
# Test: Try to acquire lock on locked product
product_service.acquire_product_lock(1, "User1", "Module1")
product_service.acquire_product_lock(1, "User2", "Module2")  # Should fail
# Expected: ProductLockError: Product is locked by User1 in module Module1
```

---

## Performance Testing

```python
import time

# Test: Load large number of products
start = time.time()
products = product_service.get_all_products()
end = time.time()
print(f"Loaded {len(products)} products in {end - start:.2f} seconds")

# Test: Load prices for group
start = time.time()
prices = pricing_service.get_product_prices_for_group(group_id=1)
end = time.time()
print(f"Loaded {len(prices)} prices in {end - start:.2f} seconds")

# Expected: < 1 second for reasonable dataset (< 1000 products)
```

---

## Database State Verification

```python
from src.database.conexion import conectar

conn = conectar()
cursor = conn.cursor()

# Check products table
cursor.execute("SELECT COUNT(*) as count FROM producto")
print(f"Total products: {cursor.fetchone()['count']}")

# Check prices table
cursor.execute("SELECT COUNT(*) as count FROM precio_por_grupo")
print(f"Total prices: {cursor.fetchone()['count']}")

# Check groups
cursor.execute("SELECT id_grupo, nombre_grupo FROM grupo")
groups = cursor.fetchall()
print(f"Groups: {[g['nombre_grupo'] for g in groups]}")

# Check client types
cursor.execute("SELECT nombre_tipo, descuento FROM tipo_cliente")
types = cursor.fetchall()
for t in types:
    print(f"  {t['nombre_tipo']}: {t['descuento']}% discount")

# Check locks
cursor.execute("SELECT COUNT(*) as count FROM producto_locks")
print(f"Active locks: {cursor.fetchone()['count']}")

conn.close()
```

---

## Common Issues & Solutions

### **Issue 1: "No module named 'src.modules.pricing'"**
**Solution:**
```bash
# Make sure you're in the project root directory
cd /path/to/di_senos
python -c "from src.modules.pricing import launch_price_editor; print('OK')"
```

### **Issue 2: "Connection Error"**
**Solution:**
- Check MySQL is running
- Verify credentials in `src/database/conexion.py`
- Test connection: `python -c "from src.database.conexion import conectar; print(conectar())"`

### **Issue 3: "Table 'producto_locks' doesn't exist"**
**Solution:**
- The lock table is created automatically on first use
- If issue persists, manually create:
```sql
CREATE TABLE IF NOT EXISTS producto_locks (
    id_producto INT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    fecha_bloqueo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto) ON DELETE CASCADE
);
```

### **Issue 4: Prices not showing**
**Solution:**
- Verify product has price set: `SELECT * FROM precio_por_grupo WHERE id_producto = ?`
- Set price via service or SQL:
```python
pricing_service.set_base_price(product_id, group_id, Decimal("25.00"))
```

### **Issue 5: Search not working**
**Solution:**
- Check products exist: `product_service.get_all_products()`
- Verify search is case-insensitive
- Try exact product name first

---

## Expected Results

### **Successful Test Run Should Show:**

1. ✅ Window appears instantly on top
2. ✅ Group buttons display with first one selected
3. ✅ Client type info shows correctly
4. ✅ Products table populates within 1 second
5. ✅ All colors render correctly (special, no-price, alternating rows)
6. ✅ Search filters products instantly
7. ✅ Edit dialog opens quickly
8. ✅ Price preview updates in real-time
9. ✅ Changes save successfully
10. ✅ No console errors or warnings

### **Database After Tests:**

- New test products created
- Prices set for multiple groups
- No orphaned locks
- All foreign keys valid

---

## Cleanup After Testing

```python
from src.modules.pricing import ProductService
from src.modules.pricing.data.mysql_repositories import MySQLProductRepository, MySQLLockRepository
from src.database.conexion import conectar

conn = conectar()
product_repo = MySQLProductRepository(conn)
lock_repo = MySQLLockRepository(conn)
product_service = ProductService(product_repo, lock_repo)

# Delete test products
test_products = product_service.search_products("Test Product")
for product in test_products:
    print(f"Deleting: {product.nombre_producto}")
    product_service.delete_product(product.id_producto, "TestUser")

# Clear all locks
cursor = conn.cursor()
cursor.execute("DELETE FROM producto_locks")
conn.commit()

print("✅ Cleanup complete!")
conn.close()
```

---

## Continuous Testing

Create a test script at `src/modules/pricing/test_pricing.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automated test suite for pricing module
Run: python -m src.modules.pricing.test_pricing
"""

def test_all():
    """Run all tests"""
    print("🧪 Running Pricing Module Tests...\n")

    # Add all test functions here
    test_product_creation()
    test_price_management()
    test_group_operations()
    test_validation()
    test_locks()

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_all()
```

---

**Testing Status:** ✅ **Ready for Testing**
**Last Updated:** 2025-01-06
