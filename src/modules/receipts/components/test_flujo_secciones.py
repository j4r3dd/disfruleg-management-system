#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST ESPECÍFICO - Flujo de Agregar Secciones
Reproduce exactamente el flujo que describió el usuario
"""

import sys
import os

# Agregar paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SCRIPT_DIR)

print("=" * 60)
print("TEST FLUJO COMPLETO - AGREGAR SECCIONES")
print("=" * 60)

# Step 1: Crear carrito
print("\n1️⃣ Crear carrito vacío...")
from carrito_module_v2 import CarritoConSeccionesV2, SeccionCarrito
import uuid
from src.modules.receipts.constants import OrderState, SectionNames

carrito = CarritoConSeccionesV2(None)
print(f"   ✅ Carrito creado")
print(f"   Secciones actuales: {len(carrito.secciones)}")

# Step 2: Agregar primer producto sin secciones extras (va a GENERAL automático)
print("\n2️⃣ Agregar primer producto 'Aguacate' (debe ir a GENERAL)...")

# Simular que no hay secciones todavía, el sistema debe crear GENERAL
if not carrito.secciones:
    print("   No hay secciones, creando GENERAL...")
    seccion_general_id = str(uuid.uuid4())
    carrito.secciones[seccion_general_id] = SeccionCarrito(seccion_general_id, SectionNames.GENERAL)

seccion_id = list(carrito.secciones.keys())[0]
carrito.agregar_item(
    id_producto=1,
    nombre_producto="Aguacate",
    cantidad=1.0,
    precio_unitario=47.0,
    unidad_producto="kg",
    seccion_id=seccion_id
)

print(f"   ✅ Aguacate agregado a GENERAL")
print(f"   Total: ${carrito.obtener_total()}")
print(f"   Items en carrito: {len(carrito.items)}")

# Step 3: Usuario crea sección BARRA
print("\n3️⃣ Usuario crea sección 'BARRA'...")
seccion_barra_id = str(uuid.uuid4())
carrito.secciones[seccion_barra_id] = SeccionCarrito(seccion_barra_id, "BARRA")
print(f"   ✅ Sección BARRA creada")
print(f"   Secciones disponibles: {[s.nombre for s in carrito.secciones.values()]}")

# Step 4: Simular ventana de agregar producto con múltiples secciones
print("\n4️⃣ Agregar segundo producto con selector de sección...")
print("   Simulando VentanaEdicionProducto...")

# Este es el código que se ejecuta en la ventana
secciones = carrito.secciones
mostrar_selector = len(secciones) > 1 or carrito.sectioning_enabled

print(f"   ¿Mostrar selector de sección? {mostrar_selector}")
print(f"   Razón: len(secciones)={len(secciones)}, sectioning_enabled={carrito.sectioning_enabled}")

if mostrar_selector:
    secciones_nombres = [s.nombre for s in secciones.values()]
    print(f"   ✅ Selector de sección visible con opciones: {secciones_nombres}")
    
    # Usuario selecciona BARRA
    seccion_seleccionada = "BARRA"
    print(f"   Usuario selecciona: {seccion_seleccionada}")
    
    # Buscar ID de la sección
    seccion_id = next(
        (sid for sid, s in secciones.items() if s.nombre == seccion_seleccionada),
        None
    )
    
    if seccion_id:
        print(f"   ✅ Sección encontrada: {seccion_id}")
    else:
        print(f"   ❌ ERROR: No se encontró la sección {seccion_seleccionada}")
        sys.exit(1)
else:
    print(f"   ❌ ERROR: Selector de sección NO visible")
    sys.exit(1)

# Step 5: Agregar el producto a la sección seleccionada
print("\n5️⃣ Agregando 'Refresco' a sección BARRA...")
carrito.agregar_item(
    id_producto=2,
    nombre_producto="Refresco",
    cantidad=10.0,
    precio_unitario=25.0,
    unidad_producto="botella",
    seccion_id=seccion_id
)

print(f"   ✅ Refresco agregado a BARRA")
print(f"   Total: ${carrito.obtener_total()}")
print(f"   Items en carrito: {len(carrito.items)}")

# Step 6: Verificar que los items están en las secciones correctas
print("\n6️⃣ Verificando distribución de items por sección...")

items_por_seccion = {}
for item_key, item in carrito.items.items():
    seccion_nombre = next(
        (s.nombre for sid, s in carrito.secciones.items() if sid == item.seccion_id),
        "UNKNOWN"
    )
    if seccion_nombre not in items_por_seccion:
        items_por_seccion[seccion_nombre] = []
    items_por_seccion[seccion_nombre].append(item.nombre_producto)

for seccion, items in items_por_seccion.items():
    print(f"   {seccion}: {items}")

# Verificación final
print("\n" + "=" * 60)
print("RESULTADO FINAL")
print("=" * 60)

success = (
    len(carrito.secciones) == 2 and
    len(carrito.items) == 2 and
    SectionNames.GENERAL in items_por_seccion and
    "BARRA" in items_por_seccion and
    "Aguacate" in items_por_seccion[SectionNames.GENERAL] and
    "Refresco" in items_por_seccion["BARRA"]
)

if success:
    print("✅ ¡TEST EXITOSO!")
    print("   - Secciones: GENERAL y BARRA ✓")
    print("   - Aguacate en GENERAL ✓")
    print("   - Refresco en BARRA ✓")
    print("   - Selector de sección funcionando ✓")
else:
    print("❌ TEST FALLÓ")
    print(f"   Secciones: {list(items_por_seccion.keys())}")

print("\n" + "=" * 60)
sys.exit(0 if success else 1)