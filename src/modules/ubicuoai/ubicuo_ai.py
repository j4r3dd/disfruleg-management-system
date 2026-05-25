#!/usr/bin/env python3
"""
Ubicuo AI - Punto de entrada principal
Sistema Inteligente de Procesamiento de Pedidos para Restaurantes
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.ubicuo_ai_interface import main

if __name__ == "__main__":
    print("=" * 60)
    print("UBICUO AI v1.0.0")
    print("Sistema Inteligente de Procesamiento de Pedidos")
    print("=" * 60)
    print("\n✓ Inicializando...")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Ubicuo AI cerrado correctamente")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()