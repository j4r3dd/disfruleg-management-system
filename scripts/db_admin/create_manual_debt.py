#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual Debt Creation Script
Creates debt records without requiring an invoice
User can later add payment details and images through the debts module
"""

import os
import sys
import mysql.connector
from decimal import Decimal
from datetime import date, datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_connection():
    """Establish database connection"""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'disfruleg')
    )


def search_clients(search_term):
    """Search for clients by name"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT c.id_cliente, c.nombre_cliente, g.clave_grupo
        FROM cliente c
        LEFT JOIN grupo g ON c.id_grupo = g.id_grupo
        WHERE c.nombre_cliente LIKE %s
        ORDER BY c.nombre_cliente
        LIMIT 15
    """

    cursor.execute(query, (f"%{search_term}%",))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results


def get_client_info(id_cliente):
    """Get full client information"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT c.id_cliente, c.nombre_cliente, g.clave_grupo as nombre_grupo
        FROM cliente c
        LEFT JOIN grupo g ON c.id_grupo = g.id_grupo
        WHERE c.id_cliente = %s
    """

    cursor.execute(query, (id_cliente,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result


def get_client_invoices(id_cliente):
    """Get invoices for a client"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id_factura, folio_numero, fecha_factura
        FROM factura
        WHERE id_cliente = %s
        ORDER BY fecha_factura DESC
        LIMIT 20
    """

    cursor.execute(query, (id_cliente,))
    results = cursor.fetchall()
    return results


def get_client_orders(id_cliente):
    """Get registered orders for a client"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT folio_numero, total_estimado, fecha_modificacion
        FROM ordenes_guardadas
        WHERE id_cliente = %s AND estado = 'registrada'
        ORDER BY fecha_modificacion DESC
        LIMIT 20
    """

    cursor.execute(query, (id_cliente,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results


def create_manual_debt(id_cliente, id_factura, nombre_cliente, nombre_grupo, monto_total,
                       fecha_generada, descripcion):
    """
    Create a debt record associated with an invoice

    Args:
        id_cliente: Client ID
        id_factura: Invoice ID
        nombre_cliente: Client name
        nombre_grupo: Group name
        monto_total: Total debt amount
        fecha_generada: Date when debt was generated
        descripcion: Description of the debt

    Returns:
        Debt ID if successful, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert debt without invoice (id_factura = NULL or empty string)
        query = """
            INSERT INTO deudas
            (id_cliente, id_factura, nombre_cliente, nombre_grupo, monto_total,
             monto_pagado, fecha_generada, pagado, descripcion, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, 0.00, %s, 0, %s, NOW(), NOW())
        """

        cursor.execute(query, (
            id_cliente,
            id_factura,
            nombre_cliente,
            nombre_grupo if nombre_grupo else 'Sin grupo',
            monto_total,
            fecha_generada,
            descripcion
        ))

        conn.commit()
        debt_id = cursor.lastrowid

        print(f"\n✅ Debt created successfully!")
        print(f"   Debt ID: {debt_id}")
        print(f"   Client: {nombre_cliente}")
        print(f"   Amount: ${monto_total:.2f}")
        print(f"   Date: {fecha_generada}")
        print(f"\n💡 You can now add payment details and images through the Debts module")

        return debt_id

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error creating debt: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        cursor.close()
        conn.close()


def main():
    print("=" * 60)
    print("     MANUAL DEBT CREATION (No Invoice Required)")
    print("=" * 60)
    print("\nThis script creates debt records without linking to invoices.")
    print("You can later add payment details and images in the Debts module.\n")

    # Step 1: Search and select client
    while True:
        search = input("Enter client name to search (or 'q' to quit): ").strip()

        if search.lower() == 'q':
            print("Cancelled.")
            return

        if not search:
            print("Please enter a search term.")
            continue

        clients = search_clients(search)

        if not clients:
            print(f"No clients found matching '{search}'. Try again.\n")
            continue

        print(f"\n{'ID':<6} {'Client Name':<30} {'Group':<20}")
        print("-" * 60)
        for c in clients:
            group = c['clave_grupo'] if c['clave_grupo'] else 'No group'
            print(f"{c['id_cliente']:<6} {c['nombre_cliente']:<30} {group:<20}")

        try:
            id_cliente = int(input("\nEnter Client ID (or 0 to search again): "))
            if id_cliente == 0:
                print()
                continue

            # Validate client exists in results
            client = next((c for c in clients if c['id_cliente'] == id_cliente), None)
            if not client:
                print("❌ Invalid Client ID. Please select from the list above.\n")
                continue

            break

        except ValueError:
            print("❌ Invalid input. Please enter a number.\n")
            continue

    # Get full client info
    client_info = get_client_info(id_cliente)
    if not client_info:
        print("❌ Error: Could not retrieve client information.")
        return

    print(f"\n✓ Selected: {client_info['nombre_cliente']} ({client_info['nombre_grupo'] or 'No group'})")

    # Step 2: Enter debt details
    print("\n" + "=" * 60)
    print("DEBT DETAILS")
    print("=" * 60)

    try:
        # Amount
        while True:
            monto_str = input("\nDebt Amount (e.g., 1500.50): $").strip()
            try:
                monto_total = float(monto_str)
                if monto_total <= 0:
                    print("❌ Amount must be greater than 0")
                    continue
                break
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")

        # Invoice Selection
        invoices = get_client_invoices(id_cliente)
        orders = get_client_orders(id_cliente)
        
        print(f"\n{'='*70}")
        print(f"{'AVAILABLE INVOICES & PROCESSED ORDERS':^70}")
        print(f"{'='*70}\n")
        
        if not invoices and not orders:
            print("⚠️ No invoices or processed orders found for this client!")
        
        else:
            print(f"{'Type':<10} {'Folio':<8} {'Date':<18} {'Amount':<12} {'Invoice ID':<10}")
            print("-" * 70)
            
            # Show invoices (and match with orders if possible)
            displayed_folios = set()
            
            for inv in invoices:
                folio = inv['folio_numero']
                displayed_folios.add(folio)
                # Try to find matching order details
                order = next((o for o in orders if o['folio_numero'] == folio), None)
                amount = f"${order['total_estimado']:.2f}" if order else "N/A"
                print(f"{'INVOICE':<10} {folio:<8} {str(inv['fecha_factura']):<18} {amount:<12} {inv['id_factura']:<10} ✅ Ready")

            # Show orders that don't have invoices yet
            for order in orders:
                folio = order['folio_numero']
                if folio not in displayed_folios:
                     print(f"{'ORDER':<10} {folio:<8} {str(order['fecha_modificacion'].date()):<18} {f'${order['total_estimado']:.2f}':<12} {'PENDING':<10} ❌ No Invoice")

            print("\n" + "-" * 70)
            print("NOTE: You can ONLY link debts to existing INVOICES (marked with ✅).")
            print("      If an order shows as 'PENDING', it hasn't been invoiced yet.")
        
        print("\nEnter 0 to search again or cancel.")

        while True:
            factura_str = input("Invoice ID: ").strip()
            try:
                id_factura = int(factura_str)
                if id_factura <= 0:
                    print("❌ Invoice ID must be positive")
                    continue
                
                # Check if it's in the list (if list exists)
                if invoices:
                    valid_ids = [inv['id_factura'] for inv in invoices]
                    if id_factura not in valid_ids:
                        print(f"⚠️ Warning: Invoice ID {id_factura} is not in the displayed list.")
                        confirm_inv = input("Use this ID anyway? (y/n): ").lower()
                        if confirm_inv not in ['y', 'yes', 's', 'si']:
                            continue

                break
            except ValueError:
                print("❌ Invalid Invoice ID. Please enter a number.")

        # Date
        while True:
            fecha_str = input("Debt Date (YYYY-MM-DD) or press Enter for today: ").strip()

            if not fecha_str:
                fecha_generada = date.today()
                break

            try:
                fecha_generada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                break
            except ValueError:
                print("❌ Invalid date format. Use YYYY-MM-DD (e.g., 2024-12-09)")

        # Description
        print("\nDescription (what is this debt for?):")
        descripcion = input("> ").strip()

        if not descripcion:
            descripcion = f"Manual debt created on {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        # Confirmation
        print("\n" + "=" * 60)
        print("CONFIRMATION")
        print("=" * 60)
        print(f"Client:      {client_info['nombre_cliente']}")
        print(f"Group:       {client_info['nombre_grupo'] or 'No group'}")
        print(f"Amount:      ${monto_total:.2f}")
        print(f"Invoice ID:  {id_factura}")
        print(f"Date:        {fecha_generada}")
        print(f"Description: {descripcion}")
        print("=" * 60)

        confirm = input("\nCreate this debt? (yes/no): ").strip().lower()

        if confirm in ['yes', 'y', 's', 'si', 'sí']:
            debt_id = create_manual_debt(
                id_cliente=client_info['id_cliente'],
                id_factura=id_factura,
                nombre_cliente=client_info['nombre_cliente'],
                nombre_grupo=client_info['nombre_grupo'],
                monto_total=monto_total,
                fecha_generada=fecha_generada,
                descripcion=descripcion
            )

            if debt_id:
                print("\n✅ SUCCESS! Debt has been created.")
                print(f"   Debt ID: {debt_id}")
                print("\n📝 Next steps:")
                print("   1. Open the Debts module in your application")
                print("   2. Find this debt in the list")
                print("   3. Add payment details and upload receipt images")
        else:
            print("\n❌ Cancelled. No debt was created.")

    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
