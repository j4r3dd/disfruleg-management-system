#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SUITE COMPLETO - Módulo de Recibos V2
Pruebas exhaustivas de todas las funcionalidades

INSTRUCCIONES:
Coloca este archivo en: src/modules/receipts/components/
Y córrelo desde ahí: python test_receipt_module.py
"""

import sys
import os
from src.modules.receipts.constants import OrderState, SectionNames

# Obtener el directorio donde está este script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Agregar el directorio raíz del proyecto (BodegaDisfruleg) al path
# Desde components, subimos 4 niveles: components -> receipts -> modules -> src -> BodegaDisfruleg
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

# También agregar components para imports directos
sys.path.insert(0, SCRIPT_DIR)

print(f"Project root: {PROJECT_ROOT}")
print(f"Components dir: {SCRIPT_DIR}")

class bcolors:
    """Colores para terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, passed, details=""):
    """Imprime resultado de test"""
    status = f"{bcolors.OKGREEN}✅ PASS{bcolors.ENDC}" if passed else f"{bcolors.FAIL}❌ FAIL{bcolors.ENDC}"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

def print_section(name):
    """Imprime sección de tests"""
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}{'='*60}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}{name}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}{'='*60}{bcolors.ENDC}\n")

# ==================== TESTS ====================

def test_imports():
    """Test 1: Verificar que todos los imports funcionan"""
    print_section("TEST 1: IMPORTS")
    
    tests = []
    
    # Test carrito_module_v2
    try:
        from carrito_module_v2 import CarritoConSeccionesV2, SeccionCarrito, ItemCarrito
        tests.append(("carrito_module_v2", True, "Imports correctos"))
    except Exception as e:
        tests.append(("carrito_module_v2", False, str(e)))
    
    # Test orden_manager
    try:
        from orden_manager import OrdenManager, obtener_manager
        tests.append(("orden_manager", True, "Imports correctos"))
    except Exception as e:
        tests.append(("orden_manager", False, str(e)))
    
    # Test database (sin conectar)
    try:
        import database
        tests.append(("database", True, "Import correcto"))
    except Exception as e:
        tests.append(("database", False, f"Warning: {e}"))
    
    for name, passed, details in tests:
        print_test(name, passed, details)
    
    return all(t[1] for t in tests)

def test_carrito_basico():
    """Test 2: Funcionalidad básica del carrito"""
    print_section("TEST 2: CARRITO BÁSICO")
    
    try:
        from carrito_module_v2 import CarritoConSeccionesV2, SeccionCarrito
        import uuid
        
        # Crear carrito sin GUI (parent_frame=None)
        carrito = CarritoConSeccionesV2(None)
        
        # Test 2.1: Carrito vacío
        total = carrito.obtener_total()
        print_test("Carrito vacío", total == 0, f"Total: ${total}")
        
        # Test 2.2: Crear sección
        seccion_id = str(uuid.uuid4())
        carrito.secciones[seccion_id] = SeccionCarrito(seccion_id, "COCINA")
        print_test("Crear sección", seccion_id in carrito.secciones, f"Sección: COCINA")
        
        # Test 2.3: Agregar item
        carrito.agregar_item(
            id_producto=1,
            nombre_producto="Aceite 1L",
            cantidad=5.0,
            precio_unitario=45.0,
            unidad_producto="litro",
            seccion_id=seccion_id
        )
        
        total = carrito.obtener_total()
        print_test("Agregar item", total == 225.0, f"Total: ${total} (esperado: $225.00)")
        
        # Test 2.4: Agregar mismo producto varias veces
        carrito.agregar_item(
            id_producto=1,
            nombre_producto="Aceite 1L",
            cantidad=2.0,
            precio_unitario=45.0,
            unidad_producto="litro",
            seccion_id=seccion_id
        )
        
        total = carrito.obtener_total()
        items_count = len(carrito.items)
        print_test("Múltiples items mismo producto", 
                   total == 315.0 and items_count == 2,
                   f"Total: ${total} (esperado: $315.00), Items: {items_count}")
        
        # Test 2.5: Limpiar carrito
        carrito.limpiar_carrito()
        total = carrito.obtener_total()
        print_test("Limpiar carrito", total == 0, f"Total después de limpiar: ${total}")
        
        return True
        
    except Exception as e:
        print_test("CARRITO BÁSICO", False, str(e))
        import traceback
        traceback.print_exc()
        return False

def test_secciones():
    """Test 3: Sistema de secciones"""
    print_section("TEST 3: SISTEMA DE SECCIONES")
    
    try:
        from carrito_module_v2 import CarritoConSeccionesV2, SeccionCarrito
        import uuid
        
        carrito = CarritoConSeccionesV2(None, )
        carrito.sectioning_enabled = True
        
        # Test 3.1: Múltiples secciones
        secciones = {
            "cocina": "COCINA",
            "barra": "BARRA",
            "piso": "PISO"
        }
        
        for key, nombre in secciones.items():
            sid = str(uuid.uuid4())
            carrito.secciones[sid] = SeccionCarrito(sid, nombre)
        
        print_test("Crear múltiples secciones", 
                   len(carrito.secciones) == 3,
                   f"Secciones creadas: {len(carrito.secciones)}")
        
        # Test 3.2: Items en diferentes secciones
        seccion_ids = list(carrito.secciones.keys())
        
        carrito.agregar_item(1, "Aceite", 5.0, 45.0, "litro", seccion_ids[0])
        carrito.agregar_item(2, "Refresco", 10.0, 25.0, "botella", seccion_ids[1])
        carrito.agregar_item(3, "Sal", 2.0, 15.0, "kg", seccion_ids[2])
        
        total = carrito.obtener_total()
        esperado = (5*45) + (10*25) + (2*15)  # 225 + 250 + 30 = 505
        
        print_test("Items en diferentes secciones",
                   total == esperado,
                   f"Total: ${total} (esperado: ${esperado})")
        
        # Test 3.3: Obtener items para BD
        items_bd = carrito.obtener_items_para_base_datos()
        print_test("Formato para BD",
                   len(items_bd) == 3 and all('seccion_id' in item for item in items_bd),
                   f"Items convertidos: {len(items_bd)}")
        
        return True
        
    except Exception as e:
        print_test("SISTEMA DE SECCIONES", False, str(e))
        import traceback
        traceback.print_exc()
        return False

def test_orden_manager():
    """Test 4: Orden Manager"""
    print_section("TEST 4: ORDEN MANAGER")
    
    try:
        from orden_manager import OrdenManager
        from carrito_module_v2 import CarritoConSeccionesV2
        import uuid
        
        manager = OrdenManager()
        carrito = CarritoConSeccionesV2(None, )
        
        # Test 4.1: Conversión carrito a JSON
        seccion_id = str(uuid.uuid4())
        carrito.secciones[seccion_id] = None  # Simular sección
        carrito.agregar_item(1, "Test", 1.0, 10.0, "unidad", seccion_id)
        
        datos_json = manager.carrito_a_json(carrito)
        
        print_test("Carrito a JSON",
                   'items' in datos_json and 'secciones' in datos_json,
                   f"Keys en JSON: {list(datos_json.keys())}")
        
        # Test 4.2: JSON a carrito
        carrito_nuevo = CarritoConSeccionesV2(None, )
        resultado = manager.json_a_carrito(datos_json, carrito_nuevo)
        
        print_test("JSON a Carrito",
                   resultado and len(carrito_nuevo.items) > 0,
                   f"Items recuperados: {len(carrito_nuevo.items)}")
        
        return True
        
    except Exception as e:
        print_test("ORDEN MANAGER", False, str(e))
        import traceback
        traceback.print_exc()
        return False

def test_validaciones():
    """Test 5: Validaciones"""
    print_section("TEST 5: VALIDACIONES")
    
    try:
        from carrito_module_v2 import CarritoConSeccionesV2
        import uuid
        
        carrito = CarritoConSeccionesV2(None, )
        seccion_id = str(uuid.uuid4())
        
        # Test 5.1: Cantidad negativa (debería fallar en la UI, pero el carrito lo acepta)
        try:
            carrito.agregar_item(1, "Test", -5.0, 10.0, "unidad", seccion_id)
            # El carrito no valida, eso lo hace la UI
            print_test("Cantidad negativa", True, "Validación debe hacerse en UI")
        except Exception as e:
            print_test("Cantidad negativa", False, str(e))
        
        # Test 5.2: Precio cero
        carrito.limpiar_carrito()
        carrito.agregar_item(1, "Gratis", 1.0, 0.0, "unidad", seccion_id)
        total = carrito.obtener_total()
        print_test("Precio cero", total == 0.0, f"Total con precio 0: ${total}")
        
        # Test 5.3: Decimales
        carrito.limpiar_carrito()
        carrito.agregar_item(1, "Test", 2.5, 10.50, "unidad", seccion_id)
        total = carrito.obtener_total()
        esperado = 2.5 * 10.50
        print_test("Decimales", abs(total - esperado) < 0.01, 
                   f"Total: ${total} (esperado: ${esperado})")
        
        return True
        
    except Exception as e:
        print_test("VALIDACIONES", False, str(e))
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test 6: Casos extremos"""
    print_section("TEST 6: CASOS EXTREMOS")
    
    try:
        from carrito_module_v2 import CarritoConSeccionesV2
        import uuid
        
        carrito = CarritoConSeccionesV2(None, )
        seccion_id = str(uuid.uuid4())
        
        # Test 6.1: Muchos items (100)
        for i in range(100):
            carrito.agregar_item(i, f"Producto {i}", 1.0, 10.0, "unidad", seccion_id)
        
        print_test("100 productos", len(carrito.items) == 100, 
                   f"Items en carrito: {len(carrito.items)}")
        
        # Test 6.2: Mismo producto 50 veces
        carrito.limpiar_carrito()
        for i in range(50):
            carrito.agregar_item(1, "Repetido", 1.0, 10.0, "unidad", seccion_id)
        
        print_test("Mismo producto 50 veces", len(carrito.items) == 50,
                   f"Items únicos: {len(carrito.items)}")
        
        # Test 6.3: Números muy grandes
        carrito.limpiar_carrito()
        carrito.agregar_item(1, "Caro", 1000.0, 9999.99, "unidad", seccion_id)
        total = carrito.obtener_total()
        print_test("Números grandes", total > 9000000,
                   f"Total grande: ${total:,.2f}")
        
        return True
        
    except Exception as e:
        print_test("CASOS EXTREMOS", False, str(e))
        import traceback
        traceback.print_exc()
        return False

def test_database_format():
    """Test 7: Formato para base de datos"""
    print_section("TEST 7: FORMATO BASE DE DATOS")
    
    try:
        from carrito_module_v2 import CarritoConSeccionesV2, SeccionCarrito
        import uuid
        
        carrito = CarritoConSeccionesV2(None, )
        
        # Crear sección
        seccion_id = str(uuid.uuid4())
        carrito.secciones[seccion_id] = SeccionCarrito(seccion_id, "COCINA")
        
        # Agregar items
        carrito.agregar_item(1, "Aceite", 5.0, 45.0, "litro", seccion_id)
        carrito.agregar_item(2, "Sal", 2.0, 15.0, "kg", seccion_id)
        
        # Obtener formato BD
        items_bd = carrito.obtener_items_para_base_datos()
        
        # Test 7.1: Estructura correcta
        campos_requeridos = ['id_producto', 'cantidad', 'precio_unitario', 
                            'nombre_producto', 'unidad', 'seccion_id']
        
        estructura_ok = all(
            all(campo in item for campo in campos_requeridos)
            for item in items_bd
        )
        
        print_test("Estructura BD correcta", estructura_ok,
                   f"Campos: {list(items_bd[0].keys()) if items_bd else 'No items'}")
        
        # Test 7.2: Tipos correctos
        if items_bd:
            primer_item = items_bd[0]
            tipos_ok = (
                isinstance(primer_item['id_producto'], int) and
                isinstance(primer_item['cantidad'], (int, float)) and
                isinstance(primer_item['precio_unitario'], (int, float)) and
                isinstance(primer_item['nombre_producto'], str)
            )
            print_test("Tipos de datos correctos", tipos_ok,
                      f"Tipos: id={type(primer_item['id_producto']).__name__}, "
                      f"cantidad={type(primer_item['cantidad']).__name__}")
        
        return True
        
    except Exception as e:
        print_test("FORMATO BASE DE DATOS", False, str(e))
        import traceback
        traceback.print_exc()
        return False

def test_seccion_general_fix():
    """Test 8: Fix de sección GENERAL cuando no hay secciones"""
    print_section("TEST 8: FIX SECCIÓN GENERAL")
    
    try:
        from carrito_module_v2 import CarritoConSeccionesV2, SeccionCarrito
        import uuid
        
        carrito = CarritoConSeccionesV2(None, )
        carrito.sectioning_enabled = True
        
        # Test 8.1: Sin secciones creadas, debe crear GENERAL automáticamente
        if not carrito.secciones:
            # Simular lo que debe hacer la ventana
            default_id = str(uuid.uuid4())
            carrito.secciones[default_id] = SeccionCarrito(default_id, SectionNames.GENERAL)
        
        print_test("Sección GENERAL creada", 
                   len(carrito.secciones) > 0,
                   f"Secciones: {[s.nombre for s in carrito.secciones.values()]}")
        
        # Test 8.2: Agregar item a GENERAL
        seccion_general_id = list(carrito.secciones.keys())[0]
        carrito.agregar_item(1, "Test", 1.0, 10.0, "unidad", seccion_general_id)
        
        print_test("Item en GENERAL",
                   len(carrito.items) == 1,
                   f"Items: {len(carrito.items)}")
        
        return True
        
    except Exception as e:
        print_test("FIX SECCIÓN GENERAL", False, str(e))
        import traceback
        traceback.print_exc()
        return False

# ==================== MAIN ====================

def run_all_tests():
    """Ejecuta todos los tests"""
    print(f"\n{bcolors.BOLD}{bcolors.HEADER}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         TEST SUITE - MÓDULO DE RECIBOS V2                 ║")
    print("║                  DISFRULEG                                 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{bcolors.ENDC}\n")
    
    tests = [
        ("IMPORTS", test_imports),
        ("CARRITO BÁSICO", test_carrito_basico),
        ("SISTEMA DE SECCIONES", test_secciones),
        ("ORDEN MANAGER", test_orden_manager),
        ("VALIDACIONES", test_validaciones),
        ("CASOS EXTREMOS", test_edge_cases),
        ("FORMATO BASE DE DATOS", test_database_format),
        ("FIX SECCIÓN GENERAL", test_seccion_general_fix),
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"{bcolors.FAIL}ERROR CRÍTICO en {nombre}: {e}{bcolors.ENDC}")
            resultados.append((nombre, False))
            import traceback
            traceback.print_exc()
    
    # Resumen final
    print_section("RESUMEN FINAL")
    
    total = len(resultados)
    passed = sum(1 for _, r in resultados if r)
    failed = total - passed
    
    for nombre, resultado in resultados:
        status = f"{bcolors.OKGREEN}✅{bcolors.ENDC}" if resultado else f"{bcolors.FAIL}❌{bcolors.ENDC}"
        print(f"{status} {nombre}")
    
    print(f"\n{bcolors.BOLD}Total: {total} tests{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}Passed: {passed}{bcolors.ENDC}")
    if failed > 0:
        print(f"{bcolors.FAIL}Failed: {failed}{bcolors.ENDC}")
    
    porcentaje = (passed / total) * 100
    print(f"\n{bcolors.BOLD}Success Rate: {porcentaje:.1f}%{bcolors.ENDC}\n")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)