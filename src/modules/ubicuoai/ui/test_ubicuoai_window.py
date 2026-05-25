#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for UbicuoAI Window
================================
Prueba la ventana de UbicuoAI de forma independiente
"""

import customtkinter as ctk
import sys
from pathlib import Path

# Add src to path if running from project root
project_root = Path(__file__).parent
if project_root not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the fixed window
# If you renamed it, adjust the import
try:
    from ubicuoai_window_FIXED import UbicuoAIWindow
    print("✅ Importado: ubicuoai_window_FIXED.py")
except ImportError:
    try:
        from ubicuoai_window import UbicuoAIWindow
        print("✅ Importado: ubicuoai_window.py")
    except ImportError as e:
        print(f"❌ Error al importar: {e}")
        print("\n💡 Asegúrate de que el archivo esté en la misma carpeta")
        sys.exit(1)


def main():
    """Main function"""
    print("=" * 60)
    print("🧪 TEST - UBICUO AI WINDOW")
    print("=" * 60)
    print()
    
    # Configure CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create root window (hidden)
    root = ctk.CTk()
    root.withdraw()  # Hide root window
    
    print("🚀 Abriendo ventana de UbicuoAI...")
    print()
    print("📝 INSTRUCCIONES:")
    print("  1. La ventana debe aparecer sin errores")
    print("  2. Debe verse el título '🤖 UBICUO AI'")
    print("  3. Debe haber dos paneles: izquierdo (input) y derecho (resultados)")
    print("  4. Debe haber botones de 'Procesar Pedido' y 'Limpiar'")
    print("  5. Debe haber un selector de clientes")
    print()
    print("⚠️  Si ves la ventana en blanco:")
    print("  • Revisa la consola por mensajes de error")
    print("  • Verifica que CustomTkinter esté instalado:")
    print("    pip install customtkinter")
    print()
    
    try:
        # Create and show UbicuoAI window
        window = UbicuoAIWindow(None)
        
        print("✅ Ventana creada exitosamente")
        print("👀 Verifica que la ventana se vea correctamente")
        print()
        print("💡 Para cerrar: Cierra la ventana o presiona Ctrl+C aquí")
        print("=" * 60)
        
        # Run main loop
        root.mainloop()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR AL CREAR LA VENTANA")
        print("=" * 60)
        print(f"\n{type(e).__name__}: {e}")
        print()
        print("🔍 DIAGNÓSTICO:")
        print()
        
        # Check dependencies
        try:
            import customtkinter
            print(f"✅ CustomTkinter instalado (v{customtkinter.__version__})")
        except ImportError:
            print("❌ CustomTkinter NO instalado")
            print("   Instalar con: pip install customtkinter")
        
        try:
            import tkinter
            print(f"✅ Tkinter disponible")
        except ImportError:
            print("❌ Tkinter NO disponible")
        
        print()
        print("📋 Stack trace completo:")
        import traceback
        traceback.print_exc()
        
        sys.exit(1)


if __name__ == "__main__":
    main()