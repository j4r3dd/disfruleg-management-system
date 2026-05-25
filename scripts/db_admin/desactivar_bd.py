#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔴 DESACTIVADOR DE BASE DE DATOS v2
Desactiva BD y también deshabilita el módulo de dispositivos

Cambios desde v1:
- También parchea module_launcher.py para deshabilitar 'devices'
- Más consistente y automático
"""

import os
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
    print(f"{Colors.HEADER}{Colors.BOLD}🔴 DESACTIVADOR DE BASE DE DATOS v2{Colors.ENDC}")
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

def backup_file(filepath):
    backup_path = f"{filepath}.backup"
    if Path(filepath).exists() and not Path(backup_path).exists():
        shutil.copy2(filepath, backup_path)
        print_info(f"Backup creado: {backup_path}")
        return backup_path
    return None

def modify_config_py(config_path):
    print_info("Modificando src/config.py...")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "USE_DATABASE = False" in content:
            print_warning("config.py ya tiene USE_DATABASE = False")
            return True
        
        backup_file(config_path)
        
        if "USE_DATABASE = True" in content:
            content = content.replace("USE_DATABASE = True", "USE_DATABASE = False")
            print_success("USE_DATABASE = True → False")
        elif "USE_DATABASE" not in content:
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('"""') and i > 0:
                    insert_pos = i + 2
                    break
            new_line = "# ✅ DESACTIVA COMPLETAMENTE LA BASE DE DATOS\nUSE_DATABASE = False\n"
            lines.insert(insert_pos, new_line)
            content = '\n'.join(lines)
            print_success("USE_DATABASE = False agregado")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success("config.py modificado")
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def modify_conexion_py(conexion_path):
    print_info("Modificando src/database/conexion.py...")
    
    try:
        with open(conexion_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        content = ''.join(lines)
        if "USE_DATABASE" in content and "from src.config import USE_DATABASE" in content:
            print_warning("conexion.py ya tiene el guard")
            return True
        
        backup_file(conexion_path)
        
        # Agregar import
        for i, line in enumerate(lines):
            if line.strip().startswith("from contextlib import"):
                if "USE_DATABASE" not in ''.join(lines[i:i+3]):
                    lines.insert(i + 1, "\n# ✅ Importar config para desactivar BD\n")
                    lines.insert(i + 2, "from src.config import USE_DATABASE\n")
                    print_success("Import agregado")
                break
        
        # Agregar guard en verify_db_availability
        content = ''.join(lines)
        for i, line in enumerate(lines):
            if "def verify_db_availability():" in line:
                for j in range(i, min(i+5, len(lines))):
                    if "global db_available" in lines[j]:
                        guard = """    if not USE_DATABASE:
        db_available = False
        logger.info("ℹ️ BD desactivada")
        return False
"""
                        lines.insert(j + 1, guard)
                        print_success("Guard en verify_db_availability()")
                        break
                break
        
        # Agregar guard en conectar
        content = ''.join(lines)
        for i, line in enumerate(lines):
            if "def conectar():" in line:
                for j in range(i, min(i+15, len(lines))):
                    if "global last_connection_error" in lines[j]:
                        guard = """    if not USE_DATABASE:
        return None
"""
                        lines.insert(j + 1, guard)
                        print_success("Guard en conectar()")
                        break
                break
        
        with open(conexion_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print_success("conexion.py modificado")
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def patch_module_launcher(launcher_path):
    """Parchea module_launcher.py para deshabilitar devices"""
    print_info("Parchando src/ui/module_launcher.py...")
    
    try:
        with open(launcher_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parche 1: Importar USE_DATABASE
        if "from src.config import debug_print, USE_SESSION_MANAGER" in content:
            old_import = "from src.config import debug_print, USE_SESSION_MANAGER"
            new_import = "from src.config import debug_print, USE_SESSION_MANAGER, USE_DATABASE"
            if new_import not in content:
                content = content.replace(old_import, new_import)
                print_success("Import USE_DATABASE agregado")
        
        # Parche 2: Validación en launch_module
        validation_code = """    # ✅ Si módulo requiere BD y está desactivada
    if module_key == 'devices' and not USE_DATABASE:
        from tkinter import messagebox
        messagebox.showerror(
            "Módulo No Disponible",
            "El módulo de Dispositivos requiere una base de datos activa.\\n\\n"
            "Ejecuta: python activar_bd.py"
        )
        return False
"""
        
        if "if module_key == 'devices' and not USE_DATABASE:" not in content:
            if "def launch_module(self, module_key" in content:
                marker = 'def launch_module(self, module_key'
                idx = content.find(marker)
                if idx != -1:
                    end_idx = content.find('\n', idx)
                    next_line_idx = end_idx + 1
                    content = content[:next_line_idx] + validation_code + content[next_line_idx:]
                    print_success("Validación agregada en launch_module")
        
        # Parche 3: Filtro None
        old_filter = "return [m for m in modules if self._user_has_role(user_role, m.get('min_role', 'usuario'))]"
        new_filter = "return [m for m in modules if m is not None and self._user_has_role(user_role, m.get('min_role', 'usuario'))]"
        
        if new_filter not in content:
            content = content.replace(old_filter, new_filter)
            print_success("Filtro None agregado")
        
        backup_file(launcher_path)
        
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success("module_launcher.py parchado")
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    print_header()
    
    project_root = find_project_root()
    if not project_root:
        print_error("Proyecto no encontrado")
        sys.exit(1)
    
    print_info(f"Proyecto: {project_root}\n")
    
    config_path = project_root / "src" / "config.py"
    conexion_path = project_root / "src" / "database" / "conexion.py"
    launcher_path = project_root / "src" / "ui" / "module_launcher.py"
    
    if not config_path.exists() or not conexion_path.exists():
        print_error("Archivos no encontrados")
        sys.exit(1)
    
    print_warning("Se realizarán cambios en tu código\n")
    
    success = True
    success = modify_config_py(config_path) and success
    success = modify_conexion_py(conexion_path) and success
    
    if launcher_path.exists():
        success = patch_module_launcher(launcher_path) and success
    else:
        print_warning("module_launcher.py no encontrado (opcional)")
    
    if success:
        print_header()
        print_success("✅ BASE DE DATOS DESACTIVADA")
        print(f"\n{Colors.OKGREEN}Tu app funcionará sin intentar conectar a Google Cloud.{Colors.ENDC}")
        print(f"{Colors.OKGREEN}El módulo 'Dispositivos' también está deshabilitado.{Colors.ENDC}\n")
        print(f"{Colors.BOLD}Para reactivar:{Colors.ENDC}")
        print(f"  python activar_bd.py\n")
    else:
        print_error("Hubo errores")
        sys.exit(1)

if __name__ == "__main__":
    main()