# -*- coding: utf-8 -*-
"""
Test Suite para UbicuoAI - Verificación de Fixes
Prueba todos los problemas que fueron corregidos
"""

import unittest
from decimal import Decimal

# Importar los servicios corregidos
from src.modules.ubicuoai.business.parser_service import ParserService
from src.modules.ubicuoai.domain.value_objects import Unit


class TestLetraLFix(unittest.TestCase):
    """Tests para verificar que la letra L ya no desaparece"""
    
    def setUp(self):
        self.parser = ParserService()
    
    def test_limon_basico(self):
        """Test: 'limón' debe mantenerse completo"""
        result = self.parser.parse_order_text("10 kg de limón")
        
        self.assertEqual(len(result.items), 1)
        item = result.items[0]
        
        self.assertIn("Limón", item.product_name, 
                     f"Expected 'Limón', got '{item.product_name}'")
        self.assertEqual(item.quantity, Decimal('10'))
        self.assertEqual(item.unit, Unit.KG)
    
    def test_limon_variaciones(self):
        """Test: Diferentes formas de escribir limón"""
        test_cases = [
            ("10 kg de limón", "Limón", 10),
            ("5 kg limón", "Limón", 5),
            ("2 kg limón eureka", "Limón Eureka", 2),
            ("3 pz limón", "Limón", 3),
        ]
        
        for input_text, expected_name, expected_qty in test_cases:
            with self.subTest(input_text=input_text):
                result = self.parser.parse_order_text(input_text)
                item = result.items[0]
                
                self.assertIn(expected_name.split()[0], item.product_name)
                self.assertEqual(item.quantity, Decimal(str(expected_qty)))
    
    def test_lima(self):
        """Test: 'lima' debe mantenerse completa"""
        result = self.parser.parse_order_text("2 kg lima")
        item = result.items[0]
        
        self.assertIn("Lima", item.product_name)
        self.assertEqual(item.quantity, Decimal('2'))
    
    def test_lechuga(self):
        """Test: 'lechuga' debe mantenerse completa"""
        result = self.parser.parse_order_text("3 pz lechuga")
        item = result.items[0]
        
        self.assertIn("Lechuga", item.product_name)
        self.assertEqual(item.quantity, Decimal('3'))
    
    def test_laurel(self):
        """Test: 'laurel' debe mantenerse completo"""
        result = self.parser.parse_order_text("1 manojo laurel")
        item = result.items[0]
        
        self.assertIn("Laurel", item.product_name)
        self.assertEqual(item.quantity, Decimal('1'))
    
    def test_leche(self):
        """Test: 'leche' con litros"""
        result = self.parser.parse_order_text("2 litros leche")
        item = result.items[0]
        
        self.assertIn("Leche", item.product_name)
        self.assertEqual(item.quantity, Decimal('2'))
        self.assertEqual(item.unit, Unit.LT)


class TestTypoCorrection(unittest.TestCase):
    """Tests para verificar auto-corrección de typos"""
    
    def setUp(self):
        self.parser = ParserService()
    
    def test_lg_a_kg(self):
        """Test: 'lg' debe auto-corregirse a 'kg'"""
        result = self.parser.parse_order_text("8 lg cebolla")
        item = result.items[0]
        
        self.assertEqual(item.unit, Unit.KG, 
                        f"Expected KG, got {item.unit}")
        self.assertEqual(item.quantity, Decimal('8'))
        self.assertIn("Cebolla", item.product_name)
    
    def test_lg_mayuscula(self):
        """Test: 'LG' también debe corregirse"""
        result = self.parser.parse_order_text("5 LG papa")
        item = result.items[0]
        
        self.assertEqual(item.unit, Unit.KG)
        self.assertEqual(item.quantity, Decimal('5'))
    
    def test_kl_a_kg(self):
        """Test: 'kl' debe corregirse a 'kg'"""
        result = self.parser.parse_order_text("3 kl tomate")
        item = result.items[0]
        
        self.assertEqual(item.unit, Unit.KG)


class TestSimbolosLimpieza(unittest.TestCase):
    """Tests para verificar limpieza de símbolos"""
    
    def setUp(self):
        self.parser = ParserService()
    
    def test_grado_simbolo(self):
        """Test: símbolo ° debe limpiarse"""
        result = self.parser.parse_order_text("°5kg papa")
        item = result.items[0]
        
        self.assertIn("Papa", item.product_name)
        self.assertEqual(item.quantity, Decimal('5'))
        self.assertEqual(item.unit, Unit.KG)
    
    def test_bullet_simbolo(self):
        """Test: símbolo • debe limpiarse"""
        result = self.parser.parse_order_text("• 3 kg cebolla")
        item = result.items[0]
        
        self.assertIn("Cebolla", item.product_name)
        self.assertEqual(item.quantity, Decimal('3'))
    
    def test_guion(self):
        """Test: guión - debe limpiarse"""
        result = self.parser.parse_order_text("- 2 kg jitomate")
        item = result.items[0]
        
        self.assertIn("Jitomate", item.product_name)
        self.assertEqual(item.quantity, Decimal('2'))
    
    def test_asterisco(self):
        """Test: asterisco * debe limpiarse"""
        result = self.parser.parse_order_text("* 4 kg aguacate")
        item = result.items[0]
        
        self.assertIn("Aguacate", item.product_name)
        self.assertEqual(item.quantity, Decimal('4'))


class TestSeccionDeteccion(unittest.TestCase):
    """Tests para verificar detección de secciones"""
    
    def setUp(self):
        self.parser = ParserService()
    
    def test_seccion_mayusculas(self):
        """Test: detectar sección en MAYÚSCULAS"""
        order_text = """
BALDEMAR
5 kg papa
"""
        sections = self.parser.parse_order_text_with_sections(order_text)
        
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]['section_name'], "Baldemar")
        self.assertEqual(len(sections[0]['items']), 1)
    
    def test_seccion_con_dos_puntos(self):
        """Test: detectar sección con dos puntos"""
        order_text = """
HABANERO:
3 kg cebolla
"""
        sections = self.parser.parse_order_text_with_sections(order_text)
        
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]['section_name'], "Habanero")
    
    def test_multiples_secciones(self):
        """Test: detectar múltiples secciones"""
        order_text = """
BALDEMAR
5 kg papa
2 kg cebolla

HABANERO
3 kg jitomate

COMIDA DE PERSONAL
1 kg chile
"""
        sections = self.parser.parse_order_text_with_sections(order_text)
        
        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0]['section_name'], "Baldemar")
        self.assertEqual(sections[1]['section_name'], "Habanero")
        self.assertEqual(sections[2]['section_name'], "Comida De Personal")
        
        # Verificar conteo de items por sección
        self.assertEqual(len(sections[0]['items']), 2)
        self.assertEqual(len(sections[1]['items']), 1)
        self.assertEqual(len(sections[2]['items']), 1)
    
    def test_seccion_sin_encabezado(self):
        """Test: items sin sección van a 'General'"""
        order_text = """
5 kg papa
3 kg cebolla
"""
        sections = self.parser.parse_order_text_with_sections(order_text)
        
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]['section_name'], "General")


class TestCasosReales(unittest.TestCase):
    """Tests con ejemplos reales de WhatsApp"""
    
    def setUp(self):
        self.parser = ParserService()
    
    def test_mensaje_baldemar_real(self):
        """Test: mensaje real de BALDEMAR"""
        order_text = """
BALDEMAR
1 caja zarzamora
3 cajas fresa
10 kg de limón
2 kg limón eureka
"""
        sections = self.parser.parse_order_text_with_sections(order_text)
        
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]['section_name'], "Baldemar")
        
        items = sections[0]['items']
        self.assertEqual(len(items), 4)
        
        # Verificar limones específicamente
        limon_items = [item for item in items if 'Limón' in item.product_name]
        self.assertEqual(len(limon_items), 2, 
                        "Debe haber 2 items de limón")
    
    def test_mensaje_con_simbolos_y_typos(self):
        """Test: mensaje con símbolos y typos combinados"""
        order_text = """
HABANERO
°5kg papa
8 lg cebolla blanca
• 3 kg de limón
"""
        sections = self.parser.parse_order_text_with_sections(order_text)
        
        self.assertEqual(len(sections), 1)
        items = sections[0]['items']
        
        # Verificar que todos se parsearon correctamente
        self.assertEqual(len(items), 3)
        
        # Verificar tipos
        papa = items[0]
        self.assertIn("Papa", papa.product_name)
        self.assertEqual(papa.unit, Unit.KG)
        
        cebolla = items[1]
        self.assertIn("Cebolla", cebolla.product_name)
        self.assertEqual(cebolla.unit, Unit.KG)  # lg → kg
        
        limon = items[2]
        self.assertIn("Limón", limon.product_name)
        self.assertEqual(limon.unit, Unit.KG)
    
    def test_orden_completa_cocina(self):
        """Test: orden completa para cocina"""
        order_text = """
Buenas noches; les dejo pedido para cocina

300 gr cilantro
1 kg pepino criollo
6 kg tomate verde
8 lg cebolla morada
500 gr jitomate cherry
"""
        result = self.parser.parse_order_text(order_text)
        
        # Debe parsear todos los items
        self.assertGreaterEqual(len(result.items), 4)
        
        # Verificar que lg se corrigió
        cebolla_items = [item for item in result.items 
                        if 'Cebolla' in item.product_name]
        if cebolla_items:
            self.assertEqual(cebolla_items[0].unit, Unit.KG)


class TestPreprocessing(unittest.TestCase):
    """Tests para verificar pre-procesamiento"""
    
    def setUp(self):
        self.parser = ParserService()
    
    def test_espacio_entre_numero_unidad(self):
        """Test: agregar espacio entre número y unidad"""
        # "5kg" debe convertirse a "5 kg"
        result = self.parser.parse_order_text("5kg papa")
        item = result.items[0]
        
        self.assertEqual(item.quantity, Decimal('5'))
        self.assertEqual(item.unit, Unit.KG)
    
    def test_limpieza_multiple(self):
        """Test: limpieza de múltiples problemas"""
        # Combina: símbolo, sin espacio, typo
        result = self.parser.parse_order_text("°5lg papa")
        item = result.items[0]
        
        self.assertEqual(item.quantity, Decimal('5'))
        self.assertEqual(item.unit, Unit.KG)
        self.assertIn("Papa", item.product_name)


def run_all_tests():
    """Ejecutar todos los tests y mostrar resumen"""
    
    # Crear test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todos los tests
    suite.addTests(loader.loadTestsFromTestCase(TestLetraLFix))
    suite.addTests(loader.loadTestsFromTestCase(TestTypoCorrection))
    suite.addTests(loader.loadTestsFromTestCase(TestSimbolosLimpieza))
    suite.addTests(loader.loadTestsFromTestCase(TestSeccionDeteccion))
    suite.addTests(loader.loadTestsFromTestCase(TestCasosReales))
    suite.addTests(loader.loadTestsFromTestCase(TestPreprocessing))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE TESTS")
    print("="*70)
    print(f"✅ Tests exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests fallidos: {len(result.failures)}")
    print(f"⚠️  Errores: {len(result.errors)}")
    print(f"📊 Total: {result.testsRun}")
    print("="*70)
    
    if result.wasSuccessful():
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ El sistema está funcionando correctamente")
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON")
        print("Por favor revisa los errores arriba")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)