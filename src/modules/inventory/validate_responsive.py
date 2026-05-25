#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Validación Estática del Sistema Responsive
Verifica estructura y código sin necesidad de ejecutar GUI
"""

import sys
import os
import ast
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_responsive_manager_exists():
    """Test 1: Verificar que responsive_manager.py existe"""
    logger.info("=" * 60)
    logger.info("TEST 1: Verificar archivos del sistema responsive")
    logger.info("=" * 60)
    
    required_files = [
        'utils/__init__.py',
        'utils/responsive_manager.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            logger.info(f"  ✅ {file_path}: EXISTE")
        else:
            logger.error(f"  ❌ {file_path}: NO EXISTE")
            all_exist = False
    
    return all_exist


def test_responsive_manager_structure():
    """Test 2: Verificar estructura de responsive_manager.py"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Estructura de responsive_manager.py")
    logger.info("=" * 60)
    
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'utils/responsive_manager.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Buscar clases y funciones
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        required_classes = ['ResponsiveMixin', 'ResponsiveWindow']
        required_functions = ['get_responsive_dimensions', 'apply_responsive_to_window']
        
        all_found = True
        
        # Verificar clases
        for cls in required_classes:
            if cls in classes:
                logger.info(f"  ✅ Clase {cls}: ENCONTRADA")
            else:
                logger.error(f"  ❌ Clase {cls}: NO ENCONTRADA")
                all_found = False
        
        # Verificar funciones
        for func in required_functions:
            if func in functions:
                logger.info(f"  ✅ Función {func}: ENCONTRADA")
            else:
                logger.error(f"  ❌ Función {func}: NO ENCONTRADA")
                all_found = False
        
        # Verificar WINDOW_PRESETS
        if 'WINDOW_PRESETS' in content:
            logger.info("  ✅ WINDOW_PRESETS: DEFINIDO")
            
            # Verificar presets individuales
            presets = ['fullscreen', 'large', 'medium', 'small', 'dialog']
            for preset in presets:
                if f"'{preset}'" in content:
                    logger.info(f"    ✅ Preset '{preset}': ENCONTRADO")
                else:
                    logger.error(f"    ❌ Preset '{preset}': NO ENCONTRADO")
                    all_found = False
        else:
            logger.error("  ❌ WINDOW_PRESETS: NO DEFINIDO")
            all_found = False
        
        return all_found
        
    except Exception as e:
        logger.error(f"❌ Error analizando archivo: {e}")
        return False


def test_purchase_history_dialog():
    """Test 3: Verificar modificaciones en purchase_history_dialog.py"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: purchase_history_dialog.py modificado")
    logger.info("=" * 60)
    
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'ui/purchase_history_dialog.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'import ResponsiveMixin': 'from utils.responsive_manager import ResponsiveMixin' in content,
            'herencia ResponsiveMixin': 'ResponsiveMixin, ctk.CTkToplevel' in content,
            'método make_responsive': 'self.make_responsive' in content,
            'preset large': "'large'" in content
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                logger.info(f"  ✅ {check_name}: OK")
            else:
                logger.error(f"  ❌ {check_name}: NO ENCONTRADO")
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        logger.error("  ❌ Archivo no encontrado")
        return False
    except Exception as e:
        logger.error(f"  ❌ Error: {e}")
        return False


def test_product_dialog():
    """Test 4: Verificar modificaciones en product_dialog.py"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: product_dialog.py modificado")
    logger.info("=" * 60)
    
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'ui/product_dialog.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'import ResponsiveMixin': 'from utils.responsive_manager import ResponsiveMixin' in content,
            'clase ProductDialog': 'class ProductDialog' in content,
            'herencia ResponsiveMixin': 'ResponsiveMixin, ctk.CTkToplevel' in content,
            'método make_responsive': 'self.make_responsive' in content,
            'preset dialog': "'dialog'" in content,
            'función create_product_dialog': 'def create_product_dialog' in content
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                logger.info(f"  ✅ {check_name}: OK")
            else:
                logger.error(f"  ❌ {check_name}: NO ENCONTRADO")
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        logger.error("  ❌ Archivo no encontrado")
        return False
    except Exception as e:
        logger.error(f"  ❌ Error: {e}")
        return False


def test_documentation():
    """Test 5: Verificar documentación"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Documentación del sistema")
    logger.info("=" * 60)
    
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'RESPONSIVE_SYSTEM.md')
        if os.path.exists(file_path):
            logger.info("  ✅ RESPONSIVE_SYSTEM.md: EXISTE")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar secciones importantes
            sections = [
                '## 🚀 Cómo Usar',
                '## 🎯 Presets Disponibles',
                '## 📝 Ejemplos de Implementación',
                '## 🧪 Ejecutar Tests',
                '## 🔧 Configuración Personalizada'
            ]
            
            all_found = True
            for section in sections:
                if section in content:
                    logger.info(f"  ✅ Sección '{section}': ENCONTRADA")
                else:
                    logger.error(f"  ❌ Sección '{section}': NO ENCONTRADA")
                    all_found = False
            
            return all_found
        else:
            logger.error("  ❌ RESPONSIVE_SYSTEM.md: NO EXISTE")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ Error: {e}")
        return False


def test_code_quality():
    """Test 6: Verificar calidad de código"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Calidad de código")
    logger.info("=" * 60)
    
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'utils/responsive_manager.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Intentar parsear el código
        try:
            ast.parse(content)
            logger.info("  ✅ Sintaxis Python: VÁLIDA")
            syntax_valid = True
        except SyntaxError as e:
            logger.error(f"  ❌ Error de sintaxis: {e}")
            syntax_valid = False
        
        # Verificar encoding UTF-8
        encoding_correct = '# -*- coding: utf-8 -*-' in content[:100]
        if encoding_correct:
            logger.info("  ✅ Encoding UTF-8: DECLARADO")
        else:
            logger.error("  ❌ Encoding UTF-8: NO DECLARADO")
        
        # Verificar docstrings
        tree = ast.parse(content)
        module_docstring = ast.get_docstring(tree)
        has_docstring = module_docstring is not None
        
        if has_docstring:
            logger.info("  ✅ Docstring del módulo: PRESENTE")
        else:
            logger.error("  ❌ Docstring del módulo: AUSENTE")
        
        return syntax_valid and encoding_correct and has_docstring
        
    except Exception as e:
        logger.error(f"  ❌ Error: {e}")
        return False


def test_imports():
    """Test 7: Verificar que los imports son correctos"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: Validación de imports")
    logger.info("=" * 60)
    
    files_to_check = {
        'utils/responsive_manager.py': [
            'from typing import',
        ],
        'ui/purchase_history_dialog.py': [
            'from utils.responsive_manager import ResponsiveMixin',
        ],
        'ui/product_dialog.py': [
            'from utils.responsive_manager import ResponsiveMixin',
        ]
    }
    
    all_valid = True
    
    for file_path, expected_imports in files_to_check.items():
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"\n  Archivo: {file_path}")
            for imp in expected_imports:
                if imp in content:
                    logger.info(f"    ✅ Import '{imp}': ENCONTRADO")
                else:
                    logger.error(f"    ❌ Import '{imp}': NO ENCONTRADO")
                    all_valid = False
                    
        except Exception as e:
            logger.error(f"    ❌ Error leyendo {file_path}: {e}")
            all_valid = False
    
    return all_valid


def run_all_tests():
    """Ejecutar todos los tests de validación"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTS DE VALIDACIÓN ESTÁTICA")
    logger.info("   SISTEMA RESPONSIVE - MÓDULO INVENTORY")
    logger.info("="*60 + "\n")
    
    results = {
        'test_1_files_exist': test_responsive_manager_exists(),
        'test_2_structure': test_responsive_manager_structure(),
        'test_3_purchase_history': test_purchase_history_dialog(),
        'test_4_product_dialog': test_product_dialog(),
        'test_5_documentation': test_documentation(),
        'test_6_code_quality': test_code_quality(),
        'test_7_imports': test_imports()
    }
    
    # Resumen final
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMEN DE VALIDACIÓN")
    logger.info("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    logger.info("\n" + "="*60)
    if total_passed == total_tests:
        logger.info(f"🎉 TODOS LOS TESTS PASARON ({total_passed}/{total_tests})")
        logger.info("✨ Sistema responsive implementado correctamente")
        logger.info("="*60)
        return True
    else:
        logger.error(f"⚠️ ALGUNOS TESTS FALLARON ({total_passed}/{total_tests})")
        logger.info("="*60)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
