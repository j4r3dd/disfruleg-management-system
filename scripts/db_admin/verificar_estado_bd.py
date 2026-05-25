#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VERIFICADOR DE ESTADO DE BASE DE DATOS
Script para diagnosticar el estado actual de tu BD

Uso:
    python verificar_estado_bd.py
"""

import os
import sys
from pathlib import Path

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🔍 DIAGNÓSTICO DE BASE DE DATOS{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'─'*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{'─'*70}{Colors.ENDC}\n")

# Encontrar raíz del proyecto
def find_project_root():
    """Busca el directorio raíz del proyecto"""
    current = Path.cwd()
    
    if (current / "src" / "config.py").exists():
        return current
    
    for parent in current.parents:
        if (parent / "src" / "config.py").exists():
            return parent
    
    return None

def check_files_exist(project_root):
    """Verifica que los archivos existan"""
    print_section("1. VERIFICACIÓN DE ARCHIVOS")
    
    files = {
        "src/config.py": project_root / "src" / "config.py",
        "src/database/conexion.py": project_root / "src" / "database" / "conexion.py",
        "src/database/cloud_config.py": project_root / "src" / "database" / "cloud_config.py",
    }
    
    all_exist = True
    for name, path in files.items():
        if path.exists():
            print_success(f"Encontrado: {name}")
        else:
            print_error(f"NO ENCONTRADO: {name}")
            all_exist = False
    
    return all_exist

def check_use_database_status(project_root):
    """Verifica el estado de USE_DATABASE"""
    print_section("2. ESTADO DE USE_DATABASE")
    
    config_path = project_root / "src" / "config.py"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "USE_DATABASE = True" in content:
            print_success("USE_DATABASE está ACTIVADO ✅")
            return "ACTIVADO"
        elif "USE_DATABASE = False" in content:
            print_warning("USE_DATABASE está DESACTIVADO 🔴")
            return "DESACTIVADO"
        else:
            print_error("USE_DATABASE no encontrado en config.py")
            return "NO_ENCONTRADO"
            
    except Exception as e:
        print_error(f"Error leyendo config.py: {e}")
        return "ERROR"

def check_guards_in_conexion(project_root):
    """Verifica si hay guards en conexion.py"""
    print_section("3. VERIFICACIÓN DE GUARDS EN conexion.py")
    
    conexion_path = project_root / "src" / "database" / "conexion.py"
    
    try:
        with open(conexion_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            "Import de USE_DATABASE": "from src.config import USE_DATABASE" in content,
            "Guard en verify_db_availability": "if not USE_DATABASE:" in content,
            "Guard en conectar": "if not USE_DATABASE:" in content,
        }
        
        has_guards = any(checks.values())
        
        for check_name, result in checks.items():
            if result:
                print_success(f"Guard presente: {check_name}")
            else:
                print_warning(f"Guard NO encontrado: {check_name}")
        
        return has_guards
        
    except Exception as e:
        print_error(f"Error leyendo conexion.py: {e}")
        return False

def check_backups(project_root):
    """Verifica si hay backups"""
    print_section("4. VERIFICACIÓN DE BACKUPS")
    
    backups = {
        "config.py.backup": project_root / "src" / "config.py.backup",
        "conexion.py.backup": project_root / "src" / "database" / "conexion.py.backup",
    }
    
    for name, path in backups.items():
        if path.exists():
            size = path.stat().st_size / 1024  # KB
            print_success(f"Backup encontrado: {name} ({size:.1f} KB)")
        else:
            print_warning(f"No hay backup: {name}")

def check_google_cloud_credentials(project_root):
    """Verifica credenciales de Google Cloud"""
    print_section("5. VERIFICACIÓN DE CREDENCIALES")
    
    # Buscar credentials.json en el proyecto
    cred_paths = [
        project_root / "credentials.json",
        project_root / "src" / "database" / "credentials.json",
        Path.home() / ".config" / "gcloud" / "credentials.json",
    ]
    
    cred_env = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'NOT SET')
    
    if cred_env != 'NOT SET':
        cred_path = Path(cred_env)
        if cred_path.exists():
            size = cred_path.stat().st_size
            print_success(f"Credenciales encontradas: {cred_env}")
            print_info(f"Tamaño: {size} bytes")
        else:
            print_error(f"Variable GOOGLE_APPLICATION_CREDENTIALS apunta a: {cred_env}")
            print_error(f"Pero el archivo NO EXISTE")
    else:
        print_warning("Variable GOOGLE_APPLICATION_CREDENTIALS no está configurada")
        print_info("Buscando credentials.json en ubicaciones comunes...")
        
        found = False
        for path in cred_paths:
            if path.exists():
                print_success(f"Encontrado: {path}")
                found = True
        
        if not found:
            print_error("No se encontraron credenciales en ubicaciones comunes")

def generate_recommendation(use_db_status, has_guards, project_root):
    """Genera recomendación basada en el diagnóstico"""
    print_section("📋 DIAGNÓSTICO Y RECOMENDACIÓN")
    
    if use_db_status == "DESACTIVADO" and has_guards:
        print_success("✅ ESTADO CORRECTO: BD está desactivada correctamente")
        print_info("Tu aplicación funcionará SIN intentar conectar a Google Cloud")
        print_info("Próximo paso: python activar_bd.py (cuando pagues la factura)")
        
    elif use_db_status == "ACTIVADO" and not has_guards:
        print_success("✅ ESTADO CORRECTO: BD está activada")
        print_info("Tu aplicación intentará conectar a Google Cloud")
        print_info("Si hay errores, verifica:")
        print_info("  1. Factura de Google Cloud pagada")
        print_info("  2. Instancia Cloud SQL en estado RUNNABLE")
        print_info("  3. Credenciales válidas")
        
    elif use_db_status == "DESACTIVADO" and not has_guards:
        print_warning("⚠️ ESTADO INCONSISTENTE: BD desactivada pero sin guards")
        print_info("Esto puede causar errores. Ejecuta:")
        print_info("  python desactivar_bd.py")
        
    elif use_db_status == "ACTIVADO" and has_guards:
        print_warning("⚠️ ESTADO INCONSISTENTE: BD activada pero con guards")
        print_info("Esto puede prevenir conexión a BD. Ejecuta:")
        print_info("  python activar_bd.py")
        
    else:
        print_error("❌ ESTADO DESCONOCIDO")
        print_info("Verifica manualmente los archivos")

def main():
    print_header()
    
    # Encontrar proyecto
    project_root = find_project_root()
    if not project_root:
        print_error("No se encontró el proyecto")
        print_info("Asegúrate de ejecutar desde el directorio raíz de tu proyecto")
        sys.exit(1)
    
    print_success(f"Proyecto encontrado en: {project_root}\n")
    
    # Ejecutar verificaciones
    files_ok = check_files_exist(project_root)
    
    if not files_ok:
        print_error("\n❌ Faltan archivos críticos. No se puede continuar.")
        sys.exit(1)
    
    use_db_status = check_use_database_status(project_root)
    has_guards = check_guards_in_conexion(project_root)
    check_backups(project_root)
    check_google_cloud_credentials(project_root)
    
    # Generar recomendación
    generate_recommendation(use_db_status, has_guards, project_root)
    
    print_header()

if __name__ == "__main__":
    main()
