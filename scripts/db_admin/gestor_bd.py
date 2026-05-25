#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 GESTOR MAESTRO DE BASE DE DATOS
Menú interactivo para gestionar la BD sin necesidad de recordar comandos

Uso:
    python gestor_bd.py
"""

import os
import sys
import subprocess
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

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🎮 GESTOR MAESTRO DE BASE DE DATOS{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_menu():
    print(f"{Colors.OKBLUE}{Colors.BOLD}OPCIONES DISPONIBLES:{Colors.ENDC}\n")
    print(f"{Colors.OKCYAN}1.{Colors.ENDC} {Colors.BOLD}🔴 Desactivar Base de Datos{Colors.ENDC}")
    print(f"   Usa esto cuando tu factura de Google Cloud esté vencida\n")
    
    print(f"{Colors.OKCYAN}2.{Colors.ENDC} {Colors.BOLD}🟢 Activar Base de Datos{Colors.ENDC}")
    print(f"   Usa esto cuando hayas pagado tu factura\n")
    
    print(f"{Colors.OKCYAN}3.{Colors.ENDC} {Colors.BOLD}🔍 Verificar Estado{Colors.ENDC}")
    print(f"   Comprueba el estado actual de tu BD\n")
    
    print(f"{Colors.OKCYAN}4.{Colors.ENDC} {Colors.BOLD}📖 Ver Documentación{Colors.ENDC}")
    print(f"   Lee las instrucciones completas\n")
    
    print(f"{Colors.OKCYAN}5.{Colors.ENDC} {Colors.BOLD}❌ Salir{Colors.ENDC}\n")

def find_script(script_name):
    """Encuentra la ubicación del script"""
    script_dir = Path(__file__).parent  # Directorio donde está gestor_bd.py
    
    # Buscar en el mismo directorio
    if (script_dir / script_name).exists():
        return script_dir / script_name
    
    # Buscar en el directorio actual de ejecución
    current = Path.cwd()
    if (current / script_name).exists():
        return current / script_name
    
    return None

def run_script(script_name):
    """Ejecuta un script Python"""
    script_path = find_script(script_name)
    
    if not script_path:
        print(f"\n{Colors.FAIL}❌ Script no encontrado: {script_name}{Colors.ENDC}\n")
        input(f"{Colors.WARNING}Presiona ENTER para continuar...{Colors.ENDC}")
        return False
    
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Error ejecutando script: {e}{Colors.ENDC}\n")
        input(f"{Colors.WARNING}Presiona ENTER para continuar...{Colors.ENDC}")
        return False

def show_documentation():
    """Muestra documentación en terminal"""
    doc = """
{bold}{header}═══════════════════════════════════════════════════════════════════{endc}
{header}📖 DOCUMENTACIÓN DE GESTIÓN DE BASE DE DATOS{endc}
{header}═══════════════════════════════════════════════════════════════════{endc}

{bold}¿QUÉ HACEN ESTOS SCRIPTS?{endc}

Los scripts automatizan la activación/desactivación de tu conexión a Google Cloud SQL.
Esto es útil cuando tu factura está vencida y no puedes pagar de inmediato.

{bold}FLUJO NORMAL:{endc}

  1. Tu factura de Google Cloud vence
     ↓
  2. Ejecutas: python desactivar_bd.py
     ↓
  3. Tu app funciona SIN intentar conectar a Google Cloud (sin errores)
     ↓
  4. (Después de pagar la factura)
     ↓
  5. Ejecutas: python activar_bd.py
     ↓
  6. Tu app reconecta a Google Cloud normalmente

{bold}CAMBIOS QUE REALIZAN LOS SCRIPTS:{endc}

DESACTIVAR:
  • config.py: USE_DATABASE = False
  • conexion.py: Agrega guards para prevenir conexiones
  • Crea backups automáticos

ACTIVAR:
  • config.py: USE_DATABASE = True
  • conexion.py: Restaura desde backup
  • Remueve guards si no hay backup

{bold}ARCHIVOS PROTEGIDOS:{endc}

Los scripts NUNCA:
  ✓ Eliminan datos
  ✓ Eliminan archivos originales (crean backups)
  ✓ Modifican credenciales
  ✓ Cambian configuración de Google Cloud

{bold}SEGURIDAD:{endc}

Los backups se crean automáticamente como:
  • src/config.py.backup
  • src/database/conexion.py.backup

Puedes restaurarlos manualmente si es necesario:
  cp src/config.py.backup src/config.py

{bold}VERIFICACIÓN:{endc}

Usa "Verificar Estado" para comprobar en cualquier momento:
  • Estado actual (Activado/Desactivado)
  • Integridad de guards
  • Existencia de backups
  • Credenciales de Google Cloud

{bold}SOLUCIÓN DE PROBLEMAS:{endc}

Si algo sale mal, los backups te respaldan. Restaura así:
  
  1. cp src/config.py.backup src/config.py
  2. cp src/database/conexion.py.backup src/database/conexion.py
  3. python verificar_estado_bd.py (para verificar)

{bold}PRÓXIMOS PASOS:{endc}

1. Selecciona una opción del menú
2. Los scripts se ejecutarán automáticamente
3. Verifica el estado después de cada acción
4. Los mensajes te guiarán en cada paso

    """.format(
        bold=Colors.BOLD,
        header=Colors.HEADER,
        endc=Colors.ENDC
    )
    
    clear_screen()
    print(doc)
    input(f"{Colors.WARNING}Presiona ENTER para volver al menú...{Colors.ENDC}")

def main():
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        try:
            choice = input(f"{Colors.OKCYAN}{Colors.BOLD}Selecciona una opción (1-5):{Colors.ENDC} ").strip()
            
            if choice == '1':
                clear_screen()
                print_header()
                print(f"{Colors.BOLD}Desactivando Base de Datos...{Colors.ENDC}\n")
                run_script("desactivar_bd.py")
                input(f"\n{Colors.WARNING}Presiona ENTER para volver al menú...{Colors.ENDC}")
                
            elif choice == '2':
                clear_screen()
                print_header()
                print(f"{Colors.BOLD}Activando Base de Datos...{Colors.ENDC}\n")
                run_script("activar_bd.py")
                input(f"\n{Colors.WARNING}Presiona ENTER para volver al menú...{Colors.ENDC}")
                
            elif choice == '3':
                clear_screen()
                print_header()
                print(f"{Colors.BOLD}Verificando Estado...{Colors.ENDC}\n")
                run_script("verificar_estado_bd.py")
                input(f"\n{Colors.WARNING}Presiona ENTER para volver al menú...{Colors.ENDC}")
                
            elif choice == '4':
                show_documentation()
                
            elif choice == '5':
                clear_screen()
                print(f"\n{Colors.OKGREEN}¡Hasta luego!{Colors.ENDC}\n")
                sys.exit(0)
                
            else:
                print(f"\n{Colors.FAIL}❌ Opción inválida. Intenta de nuevo.{Colors.ENDC}")
                input(f"{Colors.WARNING}Presiona ENTER para continuar...{Colors.ENDC}")
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Interrupción del usuario{Colors.ENDC}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error: {e}{Colors.ENDC}\n")
            input(f"{Colors.WARNING}Presiona ENTER para continuar...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Programa terminado{Colors.ENDC}\n")
        sys.exit(0)
