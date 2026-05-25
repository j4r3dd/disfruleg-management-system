#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🟢 ACTIVADOR DE BASE DE DATOS v2
Activa BD y también re-habilita el módulo de dispositivos
"""

import sys
import shutil
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🟢 ACTIVADOR DE BASE DE DATOS v2{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")

def find_project_root():
    current = Path.cwd()
    if (current / "src" / "config.py").exists():
        return current
    for parent in current.parents:
        if (parent / "src" / "config.py").exists():
            return parent
    return None

def restore_from_backup(filepath):
    backup_path = f"{filepath}.backup"
    if not Path(backup_path).exists():
        print_warning(f"No hay backup: {filepath}")
        return False
    try:
        shutil.copy2(backup_path, filepath)
        print_success(f"Restaurado: {filepath}")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def modify_config_py(config_path):
    print_info("Modificando src/config.py...")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "USE_DATABASE = True" in content:
            print_warning("config.py ya tiene USE_DATABASE = True")
            return True
        
        if "USE_DATABASE = False" in content:
            content = content.replace("USE_DATABASE = False", "USE_DATABASE = True")
            print_success("USE_DATABASE = False → True")
        else:
            print_warning("USE_DATABASE no encontrado")
            return False
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success("config.py modificado")
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def restore_conexion_py(conexion_path):
    print_info("Restaurando src/database/conexion.py...")
    
    backup_path = f"{conexion_path}.backup"
    
    if Path(backup_path).exists():
        try:
            shutil.copy2(backup_path, conexion_path)
            print_success("Restaurado desde backup")
            return True
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    else:
        print_warning("No hay backup, removiendo guards manualmente...")
        try:
            with open(conexion_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remover imports
            content = content.replace(
                "\n# ✅ Importar config para desactivar BD\nfrom src.config import USE_DATABASE\n",
                ""
            )
            
            # Remover guards
            content = content.replace(
                """    if not USE_DATABASE:
        db_available = False
        logger.info("ℹ️ BD desactivada")
        return False
""",
                ""
            )
            
            content = content.replace(
                """    if not USE_DATABASE:
        return None
""",
                ""
            )
            
            with open(conexion_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print_success("Guards removidos")
            return True
            
        except Exception as e:
            print_error(f"Error: {e}")
            return False

def restore_module_launcher(launcher_path):
    """Restaura module_launcher.py"""
    print_info("Restaurando src/ui/module_launcher.py...")
    
    backup_path = f"{launcher_path}.backup"
    
    if Path(backup_path).exists():
        try:
            shutil.copy2(backup_path, launcher_path)
            print_success("Restaurado desde backup")
            return True
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    else:
        print_warning("No hay backup")
        return False

def main():
    print_header()
    
    project_root = find_project_root()
    if not project_root:
        print_error("Proyecto no encontrado")
        sys.exit(1)
    
    print_info(f"Proyecto: {project_root}\n")
    print_warning("VERIFICA QUE:")
    print_warning("  ✓ Factura de Google Cloud está pagada")
    print_warning("  ✓ Instancia Cloud SQL en estado RUNNABLE")
    print_warning("  ✓ Credenciales válidas\n")
    
    config_path = project_root / "src" / "config.py"
    conexion_path = project_root / "src" / "database" / "conexion.py"
    launcher_path = project_root / "src" / "ui" / "module_launcher.py"
    
    if not config_path.exists():
        print_error("config.py no encontrado")
        sys.exit(1)
    
    success = True
    success = modify_config_py(config_path) and success
    success = restore_conexion_py(conexion_path) and success
    
    if launcher_path.exists():
        success = restore_module_launcher(launcher_path) and success
    
    if success:
        print_header()
        print_success("✅ BASE DE DATOS ACTIVADA")
        print(f"\n{Colors.OKGREEN}Tu app intentará conectar a Google Cloud SQL.{Colors.ENDC}")
        print(f"{Colors.OKGREEN}El módulo 'Dispositivos' está re-habilitado.{Colors.ENDC}\n")
        
        if not Path(f"{conexion_path}.backup").exists():
            print_warning("Sin backup de conexion.py - algunos guards pueden quedar")
        
        print(f"{Colors.BOLD}Si hay errores, verifica:{Colors.ENDC}")
        print(f"  1. Factura pagada")
        print(f"  2. Instancia RUNNABLE")
        print(f"  3. Credenciales válidas\n")
        print(f"{Colors.BOLD}Para desactivar:{Colors.ENDC}")
        print(f"  python desactivar_bd_v2.py\n")
    else:
        print_error("Hubo errores")
        sys.exit(1)

if __name__ == "__main__":
    main()