# -*- coding: utf-8 -*-
"""
Script para migrar automáticamente ventanas a responsive
Identifica patrones y sugiere cambios
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Mapeo de archivos a presets
WINDOW_PRESETS = {
    # Large windows
    'receipt_view.py': 'large',
    'purchase_view.py': 'large',
    'ubicuoai_window.py': 'large',
    'analizador_ganancias.py': 'large',
    
    # Medium windows
    'price_editor_app.py': 'medium',
    'client_view.py': 'medium',
    'debt_management_app.py': 'medium',
    'user_manager.py': 'medium',
    
    # Small windows
    'cotizacion_importer_app.py': 'small',
    'device_admin_module.py': 'small',
    'product_window.py': 'small',
    
    # Dialogs
    'dialogs.py': 'dialog',
    'product_dialog.py': 'dialog',
}


class WindowMigrator:
    """Migrador automático de ventanas"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / 'src'
    
    def find_window_classes(self, file_path: Path) -> List[Dict]:
        """Encontrar clases de ventana en un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patrón para encontrar clases que heredan de CTk ventanas
            pattern = r'class\s+(\w+)\s*\([^)]*(?:ctk\.CTkToplevel|ctk\.CTk|CTkToplevel|CTk)[^)]*\):'
            matches = re.finditer(pattern, content)
            
            classes = []
            for match in matches:
                class_name = match.group(1)
                
                # Buscar el __init__ de esta clase
                init_pattern = rf'class {class_name}.*?def __init__\(self[^)]*\):(.*?)(?=\n    def |\nclass |\Z)'
                init_match = re.search(init_pattern, content, re.DOTALL)
                
                if init_match:
                    init_content = init_match.group(1)
                    
                    # Verificar si ya tiene geometry o make_responsive
                    has_geometry = bool(re.search(r'\.geometry\(', init_content))
                    has_responsive = bool(re.search(r'make_responsive|ResponsiveWindow', init_content))
                    
                    classes.append({
                        'name': class_name,
                        'has_geometry': has_geometry,
                        'has_responsive': has_responsive,
                        'needs_migration': not has_responsive
                    })
            
            return classes
            
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {e}")
            return []
    
    def generate_migration_code(self, file_path: Path, class_name: str, preset: str) -> str:
        """Generar código de migración para una clase"""
        
        migration_options = f"""
# ============================================================================
# OPCIÓN 1: Heredar de ResponsiveWindow (Recomendado)
# ============================================================================
from src.utils.responsive_manager import ResponsiveWindow

class {class_name}(ResponsiveWindow):
    def __init__(self, parent):
        super().__init__(parent, preset='{preset}', title="Tu Título Aquí")
        
        # Tu código original aquí...


# ============================================================================
# OPCIÓN 2: Usar el Mixin
# ============================================================================
from src.utils.responsive_manager import ResponsiveMixin

class {class_name}(ResponsiveMixin, ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Tu Título Aquí")
        
        # Aplicar responsive ANTES de crear UI
        self.make_responsive('{preset}')
        
        # Tu código original aquí...


# ============================================================================
# OPCIÓN 3: Conversión sin modificar clase (En el código que la llama)
# ============================================================================
from src.utils.responsive_manager import convert_to_responsive

# Donde se crea la ventana:
window = {class_name}(parent)
convert_to_responsive(window, preset='{preset}')
"""
        return migration_options
    
    def scan_project(self) -> Dict[str, List[Dict]]:
        """Escanear todo el proyecto"""
        results = {}
        
        print("🔍 Escaneando proyecto...")
        
        for file_name, preset in WINDOW_PRESETS.items():
            # Buscar archivo en src/modules
            matches = list(self.src_dir.rglob(file_name))
            
            if not matches:
                print(f"⚠️  No encontrado: {file_name}")
                continue
            
            file_path = matches[0]
            print(f"\n📄 Analizando: {file_path.relative_to(self.project_root)}")
            
            classes = self.find_window_classes(file_path)
            
            if classes:
                results[str(file_path)] = {
                    'preset': preset,
                    'classes': classes
                }
                
                for cls in classes:
                    status = "✅" if cls['has_responsive'] else "❌"
                    print(f"  {status} {cls['name']}")
                    if cls['needs_migration']:
                        print(f"     → Preset sugerido: '{preset}'")
        
        return results
    
    def generate_migration_guide(self, results: Dict) -> str:
        """Generar guía de migración completa"""
        guide = """
# ============================================================================
# GUÍA DE MIGRACIÓN A RESPONSIVE
# ============================================================================

## 📊 RESUMEN

"""
        total_files = len(results)
        total_classes = sum(len(data['classes']) for data in results.values())
        needs_migration = sum(
            sum(1 for cls in data['classes'] if cls['needs_migration'])
            for data in results.values()
        )
        
        guide += f"""
- Total de archivos: {total_files}
- Total de clases: {total_classes}
- Necesitan migración: {needs_migration}
- Ya responsive: {total_classes - needs_migration}

"""
        
        # Agrupar por preset
        by_preset = {}
        for file_path, data in results.items():
            preset = data['preset']
            if preset not in by_preset:
                by_preset[preset] = []
            by_preset[preset].append((file_path, data))
        
        guide += "\n## 📋 PLAN DE MIGRACIÓN POR PRESET\n\n"
        
        for preset, files in sorted(by_preset.items()):
            guide += f"\n### Preset: '{preset}'\n\n"
            
            for file_path, data in files:
                file_name = Path(file_path).name
                guide += f"**{file_name}**\n\n"
                
                for cls in data['classes']:
                    if cls['needs_migration']:
                        guide += f"- [ ] `{cls['name']}` - Necesita migración\n"
                    else:
                        guide += f"- [x] `{cls['name']}` - Ya responsive\n"
                
                guide += "\n"
        
        return guide
    
    def create_migration_files(self, results: Dict, output_dir: str):
        """Crear archivos de migración individuales"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for file_path, data in results.items():
            file_name = Path(file_path).stem
            preset = data['preset']
            
            for cls in data['classes']:
                if cls['needs_migration']:
                    migration_file = output_path / f"{file_name}_{cls['name']}_migration.py"
                    
                    with open(migration_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Migración para {cls['name']} en {Path(file_path).name}\n")
                        f.write(self.generate_migration_code(Path(file_path), cls['name'], preset))
                    
                    print(f"📝 Creado: {migration_file.name}")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrar ventanas a responsive')
    parser.add_argument('project_root', help='Ruta raíz del proyecto')
    parser.add_argument('--generate-files', action='store_true', 
                       help='Generar archivos de migración individuales')
    parser.add_argument('--output-dir', default='./migrations',
                       help='Directorio para archivos de migración')
    
    args = parser.parse_args()
    
    migrator = WindowMigrator(args.project_root)
    results = migrator.scan_project()
    
    # Generar guía
    guide = migrator.generate_migration_guide(results)
    print("\n" + "="*80)
    print(guide)
    
    # Generar archivos si se solicita
    if args.generate_files:
        print("\n📁 Generando archivos de migración...")
        migrator.create_migration_files(results, args.output_dir)
        print(f"\n✅ Archivos generados en: {args.output_dir}")
    
    print("\n" + "="*80)
    print("\n💡 SIGUIENTE PASO:")
    print("   1. Copia responsive_manager.py a src/utils/")
    print("   2. Revisa la guía de migración arriba")
    print("   3. Empieza con los archivos marcados como 'large'")
    print("   4. Usa la OPCIÓN 1 (ResponsiveWindow) para código nuevo")
    print("   5. Usa la OPCIÓN 3 (convert_to_responsive) para pruebas rápidas")


if __name__ == "__main__":
    # Para prueba rápida sin argumentos
    import sys
    if len(sys.argv) == 1:
        # Asume que estás en la raíz del proyecto
        migrator = WindowMigrator('.')
        results = migrator.scan_project()
        guide = migrator.generate_migration_guide(results)
        print(guide)
    else:
        main()