#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Database Cleanup Script
Removes soft-deleted orders blocking folio reuse
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.conexion import get_pooled_connection
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def view_soft_deleted_orders():
    """View all soft-deleted draft orders"""
    logger.info("=" * 70)
    logger.info("STEP 1: Viewing soft-deleted orders that will be removed")
    logger.info("=" * 70)

    with get_pooled_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                folio_numero,
                id_cliente,
                usuario_creador,
                estado,
                activo,
                total_estimado,
                fecha_creacion,
                fecha_modificacion
            FROM ordenes_guardadas
            WHERE activo = FALSE AND estado = 'guardada'
            ORDER BY folio_numero
        """)

        orders = cursor.fetchall()

        if not orders:
            logger.info("✅ No soft-deleted orders found (nothing to clean up)")
            return []

        logger.info(f"\nFound {len(orders)} soft-deleted order(s) to remove:\n")
        for order in orders:
            logger.info(f"  Folio: {order['folio_numero']:06d} | "
                       f"Cliente: {order['id_cliente']} | "
                       f"Usuario: {order['usuario_creador']} | "
                       f"Total: ${order['total_estimado']:.2f} | "
                       f"Estado: {order['estado']} | "
                       f"Activo: {order['activo']} | "
                       f"Modificado: {order['fecha_modificacion']}")

        cursor.close()
        return orders


def count_orders_to_delete():
    """Count how many orders will be deleted"""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 2: Counting orders to delete")
    logger.info("=" * 70)

    with get_pooled_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ordenes_guardadas
            WHERE activo = FALSE AND estado = 'guardada'
        """)

        result = cursor.fetchone()
        count = result['count']

        logger.info(f"Orders to be deleted: {count}")

        cursor.close()
        return count


def delete_soft_deleted_orders():
    """Delete soft-deleted draft orders"""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 3: Deleting soft-deleted orders")
    logger.info("=" * 70)

    with get_pooled_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM ordenes_guardadas
            WHERE activo = FALSE AND estado = 'guardada'
        """)

        conn.commit()
        deleted_count = cursor.rowcount

        logger.info(f"✅ Successfully deleted {deleted_count} order(s)")

        cursor.close()
        return deleted_count


def verify_cleanup():
    """Verify that cleanup was successful"""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 4: Verifying cleanup")
    logger.info("=" * 70)

    with get_pooled_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ordenes_guardadas
            WHERE activo = FALSE
        """)

        result = cursor.fetchone()
        remaining = result['count']

        if remaining == 0:
            logger.info("✅ Verification passed: No soft-deleted orders remaining")
        else:
            logger.warning(f"⚠️ Warning: {remaining} soft-deleted order(s) still remain (these are likely registered orders)")

        cursor.close()
        return remaining


def show_current_folio_usage():
    """Show current folio usage after cleanup"""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 5: Current folio usage")
    logger.info("=" * 70)

    with get_pooled_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                folio_numero,
                estado,
                activo,
                usuario_creador,
                fecha_creacion
            FROM ordenes_guardadas
            ORDER BY folio_numero
        """)

        orders = cursor.fetchall()

        if not orders:
            logger.info("No orders in database")
        else:
            logger.info(f"\nCurrent orders in database ({len(orders)} total):\n")
            for order in orders:
                logger.info(f"  Folio: {order['folio_numero']:06d} | "
                           f"Estado: {order['estado']} | "
                           f"Activo: {order['activo']} | "
                           f"Usuario: {order['usuario_creador']}")

        cursor.close()
        return orders


def show_max_folios():
    """Show maximum folio numbers"""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 6: Maximum folio numbers")
    logger.info("=" * 70)

    with get_pooled_connection() as conn:
        cursor = conn.cursor()

        # Max folio from active orders
        cursor.execute("""
            SELECT MAX(folio_numero) as max_folio
            FROM ordenes_guardadas
            WHERE activo = TRUE
        """)
        result = cursor.fetchone()
        max_orden = result['max_folio'] if result['max_folio'] else 0

        # Max folio from facturas
        cursor.execute("""
            SELECT MAX(folio_numero) as max_folio
            FROM factura
        """)
        result = cursor.fetchone()
        max_factura = result['max_folio'] if result['max_folio'] else 0

        logger.info(f"Max folio in ordenes_guardadas (activo=TRUE): {max_orden}")
        logger.info(f"Max folio in factura: {max_factura}")
        logger.info(f"Next folio will be: {max(max_orden, max_factura) + 1}")

        cursor.close()
        return max_orden, max_factura


def main():
    """Main cleanup process"""
    try:
        logger.info("\n")
        logger.info("╔" + "═" * 68 + "╗")
        logger.info("║" + " " * 10 + "EMERGENCY CLEANUP: Soft-Deleted Orders" + " " * 18 + "║")
        logger.info("╚" + "═" * 68 + "╝")
        logger.info("\n")

        # Step 1: View orders to be deleted
        orders = view_soft_deleted_orders()

        if not orders:
            logger.info("\n✅ Cleanup not needed - no soft-deleted orders found")
            logger.info("You can now create new orders normally")
            return

        # Step 2: Count orders
        count = count_orders_to_delete()

        # Ask for confirmation
        logger.info("\n" + "=" * 70)
        logger.info("⚠️  CONFIRMATION REQUIRED")
        logger.info("=" * 70)
        response = input(f"\nDelete {count} soft-deleted order(s)? (yes/no): ").strip().lower()

        if response != 'yes':
            logger.info("\n❌ Cleanup cancelled by user")
            logger.info("No changes were made to the database")
            return

        # Step 3: Delete orders
        deleted = delete_soft_deleted_orders()

        # Step 4: Verify cleanup
        verify_cleanup()

        # Step 5: Show current state
        show_current_folio_usage()

        # Step 6: Show max folios
        show_max_folios()

        logger.info("\n" + "=" * 70)
        logger.info("✅ CLEANUP COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        logger.info(f"Deleted {deleted} soft-deleted order(s)")
        logger.info("Folios have been freed for reuse")
        logger.info("You can now create new orders normally")
        logger.info("=" * 70 + "\n")

    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error("❌ ERROR DURING CLEANUP")
        logger.error("=" * 70)
        logger.error(f"Error: {e}")
        logger.error("No changes were committed to the database")
        logger.error("=" * 70 + "\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
