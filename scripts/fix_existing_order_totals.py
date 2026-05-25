"""
Fix existing orders that have incorrect total_estimado values
"""

from src.database.conexion import conectar

def fix_existing_orders():
    """
    Update total_estimado for processed orders to match actual invoice totals
    """
    conn = conectar()
    cursor = conn.cursor()

    print("=" * 70)
    print("FIXING EXISTING ORDERS WITH INCORRECT TOTALS")
    print("=" * 70)

    try:
        # Find all processed orders
        query_find = """
        SELECT
            og.folio_numero,
            og.id_cliente,
            og.estado,
            og.total_estimado as old_total,
            SUM(df.cantidad_factura * df.precio_unitario_venta) as actual_total
        FROM ordenes_guardadas og
        JOIN factura f ON og.folio_numero = f.folio_numero
        JOIN detalle_factura df ON f.id_factura = df.id_factura
        WHERE og.estado = 'registrada'
        GROUP BY og.folio_numero, og.id_cliente, og.estado, og.total_estimado
        HAVING ABS(og.total_estimado - SUM(df.cantidad_factura * df.precio_unitario_venta)) > 0.01
        """

        cursor.execute(query_find)
        incorrect_orders = cursor.fetchall()

        if not incorrect_orders:
            print("\n✅ All processed orders have correct totals!")
            return

        print(f"\n⚠️  Found {len(incorrect_orders)} orders with incorrect totals:\n")
        print(f"{'Folio':<10} {'Old Total':<15} {'Actual Total':<15} {'Difference':<15}")
        print("-" * 70)

        for order in incorrect_orders:
            folio = order['folio_numero']
            old_total = float(order['old_total'])
            actual_total = float(order['actual_total'])
            diff = actual_total - old_total

            print(f"{folio:<10} ${old_total:<14,.2f} ${actual_total:<14,.2f} ${diff:<14,.2f}")

        # Ask for confirmation
        print("\n" + "=" * 70)
        response = input("Do you want to fix these orders? (yes/no): ").strip().lower()

        if response != 'yes':
            print("Operation cancelled.")
            return

        # Fix each order
        print("\n" + "=" * 70)
        print("FIXING ORDERS...")
        print("=" * 70)

        fixed_count = 0
        for order in incorrect_orders:
            folio = order['folio_numero']
            actual_total = float(order['actual_total'])

            query_update = """
            UPDATE ordenes_guardadas
            SET total_estimado = %s,
                fecha_modificacion = NOW()
            WHERE folio_numero = %s AND estado = 'registrada'
            """

            cursor.execute(query_update, (actual_total, folio))

            if cursor.rowcount > 0:
                print(f"✅ Fixed Folio {folio}: Updated to ${actual_total:,.2f}")
                fixed_count += 1
            else:
                print(f"⚠️  Could not update Folio {folio}")

        conn.commit()

        print("\n" + "=" * 70)
        print(f"✅ FIXED {fixed_count} ORDERS!")
        print("=" * 70)

        # Verify the fix
        cursor.execute(query_find)
        remaining = cursor.fetchall()

        if not remaining:
            print("\n✅ All orders now have correct totals!")
        else:
            print(f"\n⚠️  Warning: {len(remaining)} orders still have incorrect totals")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_existing_orders()
