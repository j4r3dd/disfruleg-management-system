#!/usr/bin/env python3
"""
Finish cleanup - Delete remaining clients
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.modules.receipts.database.connection_pool import get_pool

def main():
    print("\n🧹 Terminando limpieza de clientes...")

    pool = get_pool()

    with pool.get_connection() as conn:
        cursor = conn.cursor()

        # Count current clients
        cursor.execute("SELECT COUNT(*) as count FROM cliente")
        result = cursor.fetchone()
        count = result['count']

        if count == 0:
            print("✅ No hay clientes para eliminar")
            return

        print(f"📊 Clientes encontrados: {count}")
        print("🗑️  Eliminando clientes con FK checks deshabilitados...")

        # Delete with FK checks disabled
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DELETE FROM cliente")
        affected = cursor.rowcount
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

        print(f"✅ {affected} clientes eliminados")

        # Verify
        cursor.execute("SELECT COUNT(*) as count FROM cliente")
        result = cursor.fetchone()
        remaining = result['count']

        print(f"\n📊 Clientes restantes: {remaining}")

        if remaining == 0:
            print("\n✅ BASE DE DATOS COMPLETAMENTE LIMPIA!")
        else:
            print(f"\n⚠️  Aún quedan {remaining} clientes")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
