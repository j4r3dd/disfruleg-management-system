# -*- coding: utf-8 -*-
"""
Script para ejecutar sistema_mejorado.sql en Cloud SQL
BodegaDisfruleg - Octubre 2025
"""
import sys
from pathlib import Path
# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.database.conexion import conectar, return_connection

def main():
    """Función principal"""
    print("=" * 70)
    print("INSTALACIÓN DE TABLAS DEL SISTEMA MEJORADO")
    print("BodegaDisfruleg - Octubre 2025")
    print("=" * 70)
    print()
    try:
        # Conectar
        print("📡 Conectando a Cloud SQL...")
        conn = conectar()
        
        if not conn:
            print("❌ Error: No se pudo conectar a la base de datos")
            return 1
        
        print("   ✅ Conexión establecida\n")
        
        cursor = conn.cursor()
        
        # Leer archivo SQL
        sql_file = Path("data/sql/sistema_mejorado.sql")
        
        if not sql_file.exists():
            print(f"❌ Error: No se encuentra el archivo {sql_file}")
            return 1
        
        print(f"📄 Leyendo {sql_file}...")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Separar por statement (punto y coma)
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        print(f"   ✅ {len(statements)} statements encontrados\n")
        
        # Ejecutar cada statement
        for i, statement in enumerate(statements, 1):
            if 'CREATE TABLE' in statement.upper():
                # Extraer nombre de tabla
                tabla = statement.split('CREATE TABLE')[1].split('(')[0].strip()
                if 'IF NOT EXISTS' in tabla:
                    tabla = tabla.replace('IF NOT EXISTS', '').strip()
                
                print(f"📋 [{i}/{len(statements)}] Creando tabla: {tabla}")
                
                try:
                    cursor.execute(statement)
                    print(f"   ✅ Tabla {tabla} creada correctamente")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f"   ℹ️  Tabla {tabla} ya existe (OK)")
                    else:
                        raise
        
        # Commit
        conn.commit()
        print("\n💾 Cambios guardados en la base de datos\n")
        
        # Verificar tablas
        print("🔍 Verificando instalación...")
        
        tablas = ['producto_locks', 'logs_sistema', 'eventos_sistema']
        
        for tabla in tablas:
            cursor.execute(f"""
                SELECT COUNT(*) as total 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = '{tabla}'
            """)
            
            resultado = cursor.fetchone()
            existe = resultado['total'] > 0 if isinstance(resultado, dict) else resultado[0] > 0
            
            if existe:
                cursor.execute(f"SELECT COUNT(*) as registros FROM {tabla}")
                count = cursor.fetchone()
                num_registros = count['registros'] if isinstance(count, dict) else count[0]
                print(f"   ✅ {tabla}: OK ({num_registros} registros)")
            else:
                print(f"   ❌ {tabla}: NO EXISTE")
                return 1
        
        print("\n" + "=" * 70)
        print("✅ INSTALACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print()
        print("📌 Las siguientes tablas están listas:")
        print("   • producto_locks - Para bloqueos de productos")
        print("   • logs_sistema - Para registro de actividades")
        print("   • eventos_sistema - Para sincronización de módulos")
        print()
        print("🚀 Ahora puedes usar:")
        print("   • Price Editor con bloqueos")
        print("   • Importador de Cotizaciones con logs")
        print("   • Todos los módulos con seguimiento de eventos")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if 'conn' in locals() and conn:
            return_connection(conn)
            print("🔌 Conexión devuelta al pool")

if __name__ == "__main__":
    sys.exit(main())