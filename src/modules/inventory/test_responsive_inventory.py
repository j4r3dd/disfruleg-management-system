#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del sistema responsive del módulo inventory
Verifica que todas las ventanas se adapten correctamente a diferentes tamaños de pantalla
"""

import sys
import os

# Agregar src e inventory al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'inventory'))

import customtkinter as ctk
from inventory.utils.responsive_manager import (
    ResponsiveWindow, 
    ResponsiveMixin, 
    WINDOW_PRESETS,
    get_responsive_dimensions,
    apply_responsive_to_window
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_responsive_window():
    """Test 1: ResponsiveWindow directa"""
    logger.info("=" * 60)
    logger.info("TEST 1: ResponsiveWindow directa")
    logger.info("=" * 60)
    
    root = ctk.CTk()
    root.withdraw()
    
    try:
        window = ResponsiveWindow(
            root, 
            preset='large',
            title="Test Inventory Responsive - Large"
        )
        
        # Agregar contenido de prueba
        frame = ctk.CTkFrame(window, fg_color="#2a2a2a")
        frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        ctk.CTkLabel(
            frame,
            text="✅ Test 1: ResponsiveWindow\nMódulo Inventory\nFunciona Correctamente",
            font=("Arial", 24, "bold"),
            text_color="white"
        ).pack(expand=True)
        
        ctk.CTkButton(
            frame,
            text="Cerrar",
            command=window.destroy,
            height=50,
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        logger.info("✅ Test 1 PASADO: ResponsiveWindow creada correctamente")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 1 FALLIDO: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass


def test_responsive_mixin():
    """Test 2: ResponsiveMixin con clase custom"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: ResponsiveMixin con clase custom")
    logger.info("=" * 60)
    
    root = ctk.CTk()
    root.withdraw()
    
    try:
        class TestWindow(ResponsiveMixin, ctk.CTkToplevel):
            def __init__(self, parent):
                super().__init__(parent)
                self.title("Test Inventory Mixin - Medium")
                
                # Aplicar responsive
                self.make_responsive('medium')
                
                # UI de prueba
                frame = ctk.CTkFrame(self, fg_color="#2a2a2a")
                frame.pack(fill="both", expand=True, padx=40, pady=40)
                
                ctk.CTkLabel(
                    frame,
                    text="✅ Test 2: ResponsiveMixin\nMódulo Inventory\nFunciona Correctamente",
                    font=("Arial", 24, "bold"),
                    text_color="white"
                ).pack(expand=True)
                
                ctk.CTkButton(
                    frame,
                    text="Cerrar",
                    command=self.destroy,
                    height=50,
                    font=("Arial", 16, "bold")
                ).pack(pady=20)
        
        window = TestWindow(root)
        
        logger.info("✅ Test 2 PASADO: ResponsiveMixin funciona correctamente")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test 2 FALLIDO: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass


def test_all_presets():
    """Test 3: Todos los presets"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Todos los presets")
    logger.info("=" * 60)
    
    presets = ['fullscreen', 'large', 'medium', 'small', 'dialog']
    results = {}
    
    for preset in presets:
        root = ctk.CTk()
        root.withdraw()
        
        try:
            window = ResponsiveWindow(
                root,
                preset=preset,
                title=f"Test Inventory {preset}"
            )
            
            # Verificar geometría
            geometry = window.geometry()
            width, height = geometry.split('+')[0].split('x')
            
            results[preset] = {
                'success': True,
                'width': int(width),
                'height': int(height)
            }
            
            logger.info(f"  ✅ {preset:12s}: {width}x{height}")
            
            window.destroy()
            
        except Exception as e:
            results[preset] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"  ❌ {preset:12s}: {e}")
            
        finally:
            try:
                root.destroy()
            except:
                pass
    
    # Resumen
    passed = sum(1 for r in results.values() if r['success'])
    total = len(presets)
    
    logger.info(f"\n✅ Test 3: {passed}/{total} presets funcionan correctamente")
    
    return passed == total


def test_purchase_history_dialog():
    """Test 4: Importar y verificar PurchaseHistoryDialog"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: PurchaseHistoryDialog responsive")
    logger.info("=" * 60)
    
    try:
        from inventory.ui.purchase_history_dialog import PurchaseHistoryDialog
        logger.info("✅ PurchaseHistoryDialog importado correctamente")
        
        # Verificar que tiene el mixin
        if hasattr(PurchaseHistoryDialog, 'make_responsive'):
            logger.info("✅ PurchaseHistoryDialog tiene método make_responsive")
            
            # Verificar herencia
            if ResponsiveMixin in PurchaseHistoryDialog.__mro__:
                logger.info("✅ PurchaseHistoryDialog hereda de ResponsiveMixin")
                return True
            else:
                logger.error("❌ PurchaseHistoryDialog NO hereda de ResponsiveMixin")
                return False
        else:
            logger.error("❌ PurchaseHistoryDialog NO tiene método make_responsive")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error importando PurchaseHistoryDialog: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_product_dialog():
    """Test 5: Importar y verificar ProductDialog"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: ProductDialog responsive")
    logger.info("=" * 60)
    
    try:
        from inventory.ui.product_dialog import ProductDialog
        logger.info("✅ ProductDialog importado correctamente")
        
        # Verificar que tiene el mixin
        if hasattr(ProductDialog, 'make_responsive'):
            logger.info("✅ ProductDialog tiene método make_responsive")
            
            # Verificar herencia
            if ResponsiveMixin in ProductDialog.__mro__:
                logger.info("✅ ProductDialog hereda de ResponsiveMixin")
                return True
            else:
                logger.error("❌ ProductDialog NO hereda de ResponsiveMixin")
                return False
        else:
            logger.error("❌ ProductDialog NO tiene método make_responsive")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error importando ProductDialog: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_responsive_dimensions():
    """Test 6: Función auxiliar get_responsive_dimensions"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: get_responsive_dimensions")
    logger.info("=" * 60)
    
    try:
        # Test con diferentes presets
        test_cases = [
            ('fullscreen', 1920, 1080),
            ('large', 1920, 1080),
            ('medium', 1920, 1080),
            ('small', 1920, 1080),
            ('dialog', 1920, 1080)
        ]
        
        all_passed = True
        
        for preset, screen_w, screen_h in test_cases:
            try:
                width, height, x, y = get_responsive_dimensions(
                    preset, 
                    screen_w, 
                    screen_h
                )
                
                logger.info(f"  ✅ {preset:12s}: {width}x{height} en posición ({x}, {y})")
                
                # Verificar que las dimensiones tienen sentido
                if width <= 0 or height <= 0:
                    logger.error(f"  ❌ {preset}: Dimensiones inválidas")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"  ❌ {preset}: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_window_presets():
    """Test 7: Verificar que todos los presets están definidos"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: Verificación de WINDOW_PRESETS")
    logger.info("=" * 60)
    
    try:
        required_presets = ['fullscreen', 'large', 'medium', 'small', 'dialog']
        
        all_present = True
        for preset in required_presets:
            if preset in WINDOW_PRESETS:
                config = WINDOW_PRESETS[preset]
                logger.info(f"  ✅ {preset:12s}: {config}")
            else:
                logger.error(f"  ❌ {preset:12s}: NO ENCONTRADO")
                all_present = False
        
        return all_present
        
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests(interactive=False):
    """Ejecutar todos los tests"""
    logger.info("\n" + "="*60)
    logger.info("🧪 EJECUTANDO TESTS DEL SISTEMA RESPONSIVE")
    logger.info("   MÓDULO: INVENTORY")
    logger.info("="*60 + "\n")
    
    results = {
        'test_1_window': test_responsive_window(),
        'test_2_mixin': test_responsive_mixin(),
        'test_3_presets': test_all_presets(),
        'test_4_purchase_history': test_purchase_history_dialog(),
        'test_5_product_dialog': test_product_dialog(),
        'test_6_dimensions': test_get_responsive_dimensions(),
        'test_7_window_presets': test_window_presets()
    }
    
    # Resumen final
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMEN DE TESTS")
    logger.info("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    logger.info("\n" + "="*60)
    if total_passed == total_tests:
        logger.info(f"🎉 TODOS LOS TESTS PASARON ({total_passed}/{total_tests})")
        logger.info("="*60)
        return True
    else:
        logger.error(f"⚠️ ALGUNOS TESTS FALLARON ({total_passed}/{total_tests})")
        logger.info("="*60)
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test del sistema responsive del módulo inventory')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Modo interactivo (mostrar ventanas)')
    
    args = parser.parse_args()
    
    success = run_all_tests(interactive=args.interactive)
    
    sys.exit(0 if success else 1)
