#!/usr/bin/env python3
"""
Database Cleanup Script v3 for Disfruleg
========================================
Refactored following Clean Architecture principles:
- Domain Layer: Models and entities
- Data Layer: Repository interfaces and implementations
- Business Layer: Service logic
- UI Layer: Presentation and user interaction

Author: Disfruleg Development Team
Date: 2025-01-24
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Protocol, Optional, List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# DOMAIN LAYER - Models and Entities
# ============================================================================

class CleanupStatus(Enum):
    """Status of cleanup operations"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    EMPTY = "empty"


@dataclass
class TableInfo:
    """Domain model for table information"""
    name: str
    display_name: str
    category: str
    description: str = ""


@dataclass
class CleanupResult:
    """Domain model for cleanup operation result"""
    table_name: str
    status: CleanupStatus
    records_deleted: int
    error_message: Optional[str] = None


@dataclass
class DatabaseStats:
    """Domain model for database statistics"""
    table_name: str
    display_name: str
    record_count: int


class BusinessLogicError(Exception):
    """Custom exception for business logic errors"""
    pass


# ============================================================================
# DATA LAYER - Repository Interfaces (Protocols)
# ============================================================================

class IDatabaseConnection(Protocol):
    """Protocol for database connection"""
    def cursor(self): ...
    def commit(self): ...
    def rollback(self): ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...


class ICleanupRepository(Protocol):
    """Repository interface for database cleanup operations"""

    def count_records(self, table_name: str) -> int:
        """Count records in a table"""
        ...

    def delete_all_records(self, table_name: str) -> int:
        """Delete all records from a table, returns count deleted"""
        ...

    def set_foreign_key_checks(self, enabled: bool) -> None:
        """Enable or disable foreign key checks"""
        ...

    def reset_sequence(self, table_name: str, sequence_id: int) -> None:
        """Reset auto-increment sequence"""
        ...

    def reset_user_login_attempts(self) -> int:
        """Reset user login attempts, returns affected rows"""
        ...

    def get_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        ...


# ============================================================================
# DATA LAYER - Repository Implementation
# ============================================================================

class MySQLCleanupRepository:
    """MySQL implementation of cleanup repository"""

    def __init__(self, connection_factory):
        """
        Initialize repository with connection factory

        Args:
            connection_factory: Callable that returns a database connection
        """
        if not callable(connection_factory):
            raise BusinessLogicError("connection_factory must be callable")
        self._get_connection = connection_factory

    def count_records(self, table_name: str) -> int:
        """Count records in a table"""
        if not table_name or not isinstance(table_name, str):
            raise BusinessLogicError("table_name must be a non-empty string")

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Use parameterized query pattern (table name is validated above)
                query = f"SELECT COUNT(*) as count FROM {table_name}"
                cursor.execute(query)
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            raise BusinessLogicError(f"Error counting records in {table_name}: {e}")

    def delete_all_records(self, table_name: str) -> int:
        """Delete all records from a table"""
        if not table_name or not isinstance(table_name, str):
            raise BusinessLogicError("table_name must be a non-empty string")

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = f"DELETE FROM {table_name}"
                cursor.execute(query)
                affected = cursor.rowcount
                conn.commit()
                return affected
        except Exception as e:
            raise BusinessLogicError(f"Error deleting from {table_name}: {e}")

    def set_foreign_key_checks(self, enabled: bool) -> None:
        """Enable or disable foreign key checks"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                value = 1 if enabled else 0
                cursor.execute(f"SET FOREIGN_KEY_CHECKS = {value}")
                conn.commit()
        except Exception as e:
            raise BusinessLogicError(f"Error setting foreign key checks: {e}")

    def reset_sequence(self, table_name: str, sequence_id: int) -> None:
        """Reset auto-increment sequence"""
        if not table_name or not isinstance(table_name, str):
            raise BusinessLogicError("table_name must be a non-empty string")
        if not isinstance(sequence_id, int) or sequence_id < 1:
            raise BusinessLogicError("sequence_id must be a positive integer")

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE {table_name} SET next_val = 1 WHERE id = %s",
                    (sequence_id,)
                )
                conn.commit()
        except Exception as e:
            raise BusinessLogicError(f"Error resetting sequence {table_name}: {e}")

    def reset_user_login_attempts(self) -> int:
        """Reset user login attempts"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE usuarios_sistema
                    SET intentos_fallidos = 0, bloqueado_hasta = NULL
                    WHERE intentos_fallidos > 0 OR bloqueado_hasta IS NOT NULL
                """)
                affected = cursor.rowcount
                conn.commit()
                return affected
        except Exception as e:
            raise BusinessLogicError(f"Error resetting login attempts: {e}")

    def get_table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        if not table_name or not isinstance(table_name, str):
            raise BusinessLogicError("table_name must be a non-empty string")

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) as count FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() AND table_name = %s",
                    (table_name,)
                )
                result = cursor.fetchone()
                return result['count'] > 0 if result else False
        except Exception as e:
            raise BusinessLogicError(f"Error checking table existence: {e}")


# ============================================================================
# BUSINESS LAYER - Service
# ============================================================================

class CleanupService:
    """Business logic for database cleanup operations"""

    # Define cleanup order and table groupings
    CLEANUP_GROUPS = {
        'debts_and_payments': [
            TableInfo('aplicacion_credito', 'Aplicaciones de Crédito', 'debts', 'aplicaciones de crédito a deudas'),
            TableInfo('pago_registrado', 'Pagos Registrados', 'debts', 'pagos individuales'),
            TableInfo('credito_cliente', 'Créditos de Cliente', 'debts', 'créditos/saldos a favor'),
            TableInfo('deudas', 'Deudas', 'debts', 'deudas de clientes'),
        ],
        'invoices': [
            TableInfo('detalle_factura', 'Detalles de Factura', 'invoices', 'líneas de productos'),
            TableInfo('seccion_factura', 'Secciones de Factura', 'invoices', 'secciones'),
            TableInfo('factura_metadata', 'Metadata de Factura', 'invoices', 'metadata'),
            TableInfo('factura', 'Facturas', 'invoices', 'facturas'),
        ],
        'orders': [
            TableInfo('ordenes_guardadas', 'Órdenes Guardadas', 'orders', 'órdenes en borrador'),
        ],
        'products': [
            TableInfo('precio_por_grupo', 'Precios por Grupo', 'products', 'precios específicos por grupo'),
            TableInfo('compra', 'Compras', 'products', 'historial de compras'),
            TableInfo('producto_locks', 'Locks de Producto', 'products', 'locks de edición'),
            TableInfo('producto_ids_reciclados', 'IDs Reciclados', 'products', 'IDs disponibles para reusar'),
            TableInfo('producto', 'Productos', 'products', 'catálogo de productos'),
        ],
        'clients': [
            TableInfo('cliente', 'Clientes', 'clients', 'clientes'),
            TableInfo('grupo', 'Grupos', 'clients', 'grupos de clientes'),
            TableInfo('tipo_cliente', 'Tipos de Cliente', 'clients', 'tipos con descuentos'),
        ],
        'ubicuoai': [
            TableInfo('ubicuoai_learning', 'UbicuoAI Learning', 'ubicuoai', 'datos de aprendizaje IA'),
        ],
        'audit_logs': [
            TableInfo('pagos_multiples_audit', 'Auditoría Pagos Múltiples', 'audit', 'auditoría de pagos masivos'),
            TableInfo('pdf_access_audit', 'Auditoría Acceso PDF', 'audit', 'auditoría de acceso a PDFs'),
            TableInfo('auditoria_pago', 'Auditoría de Pagos', 'audit', 'auditoría de cambios en pagos'),
        ],
        'system_logs': [
            TableInfo('logs_sistema', 'Logs del Sistema', 'logs', 'logs de aplicación'),
            TableInfo('eventos_sistema', 'Eventos del Sistema', 'logs', 'eventos del sistema'),
            TableInfo('log_accesos', 'Log de Accesos', 'logs', 'intentos de login'),
            TableInfo('log_accesos_dispositivos', 'Log Accesos Dispositivos', 'logs', 'accesos por dispositivo'),
        ],
    }

    STATS_TABLES = [
        ('producto', 'Productos'),
        ('cliente', 'Clientes'),
        ('grupo', 'Grupos'),
        ('tipo_cliente', 'Tipos de Cliente'),
        ('factura', 'Facturas'),
        ('detalle_factura', 'Detalles de Factura'),
        ('deudas', 'Deudas'),
        ('pago_registrado', 'Pagos Registrados'),
        ('credito_cliente', 'Créditos Cliente'),
        ('ordenes_guardadas', 'Órdenes Guardadas'),
        ('precio_por_grupo', 'Precios por Grupo'),
        ('compra', 'Compras'),
        ('usuarios_sistema', 'Usuarios'),
    ]

    def __init__(self, repository: ICleanupRepository):
        """
        Initialize service with repository

        Args:
            repository: Implementation of ICleanupRepository
        """
        if not repository:
            raise BusinessLogicError("repository is required")
        self.repository = repository

    def get_database_stats(self) -> List[DatabaseStats]:
        """Get current database statistics"""
        stats = []
        for table_name, display_name in self.STATS_TABLES:
            try:
                count = self.repository.count_records(table_name)
                stats.append(DatabaseStats(
                    table_name=table_name,
                    display_name=display_name,
                    record_count=count
                ))
            except BusinessLogicError as e:
                # Table might not exist, skip it
                continue

        return stats

    def cleanup_table(self, table_info: TableInfo) -> CleanupResult:
        """
        Clean up a single table

        Args:
            table_info: Information about the table to clean

        Returns:
            CleanupResult with operation details
        """
        if not table_info or not table_info.name:
            raise BusinessLogicError("table_info with name is required")

        try:
            # Check if table exists
            if not self.repository.get_table_exists(table_info.name):
                return CleanupResult(
                    table_name=table_info.name,
                    status=CleanupStatus.SKIPPED,
                    records_deleted=0,
                    error_message="Table does not exist"
                )

            # Count records
            count = self.repository.count_records(table_info.name)

            if count == 0:
                return CleanupResult(
                    table_name=table_info.name,
                    status=CleanupStatus.EMPTY,
                    records_deleted=0
                )

            # Delete records
            deleted = self.repository.delete_all_records(table_info.name)

            return CleanupResult(
                table_name=table_info.name,
                status=CleanupStatus.SUCCESS,
                records_deleted=deleted
            )

        except BusinessLogicError as e:
            return CleanupResult(
                table_name=table_info.name,
                status=CleanupStatus.FAILED,
                records_deleted=0,
                error_message=str(e)
            )

    def execute_full_cleanup(
        self,
        keep_logs: bool = False,
        keep_audit: bool = False
    ) -> Tuple[bool, List[CleanupResult]]:
        """
        Execute complete database cleanup

        Args:
            keep_logs: If True, preserve system logs
            keep_audit: If True, preserve audit logs

        Returns:
            Tuple of (success: bool, results: List[CleanupResult])
        """
        results = []

        try:
            # Disable foreign key checks
            self.repository.set_foreign_key_checks(False)

            # Clean each group in order
            for group_name, tables in self.CLEANUP_GROUPS.items():
                # Skip groups based on options
                if group_name == 'system_logs' and keep_logs:
                    continue
                if group_name == 'audit_logs' and keep_audit:
                    continue

                # Clean each table in the group
                for table_info in tables:
                    result = self.cleanup_table(table_info)
                    results.append(result)

            # Reset sequences
            try:
                self.repository.reset_sequence('folio_sequence', 1)
                self.repository.reset_sequence('factura_sequence', 1)
            except BusinessLogicError:
                # Sequences might not exist, continue
                pass

            # Reset user login attempts
            try:
                self.repository.reset_user_login_attempts()
            except BusinessLogicError:
                # Continue even if this fails
                pass

            # Re-enable foreign key checks
            self.repository.set_foreign_key_checks(True)

            # Check if any critical operations failed
            critical_failures = [
                r for r in results
                if r.status == CleanupStatus.FAILED and r.table_name in [
                    'factura', 'deudas', 'producto', 'cliente'
                ]
            ]

            success = len(critical_failures) == 0
            return success, results

        except Exception as e:
            # Try to re-enable foreign keys
            try:
                self.repository.set_foreign_key_checks(True)
            except:
                pass

            raise BusinessLogicError(f"Cleanup failed: {e}")


# ============================================================================
# UI LAYER - Presentation and User Interaction
# ============================================================================

class CleanupPresenter:
    """Handles presentation and user interaction"""

    def __init__(self, service: CleanupService):
        """
        Initialize presenter with service

        Args:
            service: CleanupService instance
        """
        if not service:
            raise BusinessLogicError("service is required")
        self.service = service

    def show_header(self):
        """Display application header"""
        print("\n" + "="*70)
        print("DATABASE CLEANUP TOOL V3 - DISFRULEG".center(70))
        print("="*70)
        print("\n⚠️  WARNING: This will DELETE business data!")
        print("\n✅  This will PRESERVE:")
        print("   - Database structure")
        print("   - ALL user accounts")
        print("   - Device authorizations")
        print("="*70)

    def show_stats(self):
        """Display current database statistics"""
        print("\n" + "="*70)
        print("ESTADÍSTICAS ACTUALES".center(70))
        print("="*70)
        print(f"{'Tabla':<35} {'Registros':>20}")
        print("-"*70)

        try:
            stats = self.service.get_database_stats()
            total = sum(s.record_count for s in stats)

            for stat in stats:
                print(f"{stat.display_name:<35} {stat.record_count:>20,}")

            print("-"*70)
            print(f"{'TOTAL':<35} {total:>20,}")
            print("="*70)

        except Exception as e:
            print(f"⚠️  Error obteniendo estadísticas: {e}")

    def confirm_action(self, message: str) -> bool:
        """
        Ask user for confirmation

        Args:
            message: Question to ask user

        Returns:
            True if user confirms, False otherwise
        """
        while True:
            response = input(f"\n{message} (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Por favor responde 'yes' o 'no'")

    def show_cleanup_progress(self, results: List[CleanupResult]):
        """Display cleanup progress and results"""
        print("\n" + "="*70)
        print("RESULTADOS DE LIMPIEZA".center(70))
        print("="*70)

        # Group results by category
        current_category = None

        for result in results:
            # Get category from table info
            category_emoji = {
                'debts': '💰',
                'invoices': '📋',
                'orders': '📦',
                'products': '🏷️',
                'clients': '👥',
                'ubicuoai': '🤖',
                'audit': '📊',
                'logs': '📝',
            }

            # Find table info
            table_info = None
            for group_name, tables in CleanupService.CLEANUP_GROUPS.items():
                for ti in tables:
                    if ti.name == result.table_name:
                        table_info = ti
                        break
                if table_info:
                    break

            if table_info and table_info.category != current_category:
                current_category = table_info.category
                category_name = group_name.replace('_', ' ').title()
                emoji = category_emoji.get(table_info.category, '📁')
                print(f"\n{emoji} {category_name}:")

            # Display result
            if result.status == CleanupStatus.SUCCESS:
                desc = table_info.description if table_info else ""
                print(f"  ✅ {result.table_name}: {result.records_deleted:,} registros eliminados ({desc})")
            elif result.status == CleanupStatus.EMPTY:
                print(f"  ⚪ {result.table_name}: ya está vacía")
            elif result.status == CleanupStatus.SKIPPED:
                print(f"  ⏭️  {result.table_name}: omitida ({result.error_message})")
            elif result.status == CleanupStatus.FAILED:
                print(f"  ❌ {result.table_name}: ERROR - {result.error_message}")

        print("\n" + "="*70)

    def run(self):
        """Main execution flow"""
        self.show_header()

        # Show current stats
        print("\n📊 Obteniendo estadísticas actuales...")
        self.show_stats()

        # Get user confirmation
        if not self.confirm_action("🚨 ¿Estás SEGURO que quieres eliminar datos?"):
            print("\n✅ Cancelado. No se realizaron cambios.")
            return

        # Ask about logs and audit
        keep_logs = self.confirm_action("📝 ¿Deseas mantener los logs del sistema?")
        keep_audit = self.confirm_action("📊 ¿Deseas mantener los logs de auditoría?")

        # Execute cleanup
        print("\n🧹 INICIANDO LIMPIEZA...")

        try:
            success, results = self.service.execute_full_cleanup(
                keep_logs=keep_logs,
                keep_audit=keep_audit
            )

            # Show results
            self.show_cleanup_progress(results)

            if success:
                print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
                print("="*70)

                # Show verification
                print("\n📊 Verificando base de datos limpia...")
                self.show_stats()
                print("\n✅ Base de datos lista para uso!\n")
            else:
                print("⚠️  LIMPIEZA COMPLETADA CON ADVERTENCIAS")
                print("="*70)
                print("\nAlgunas operaciones fallaron. Revisa los resultados.\n")

        except BusinessLogicError as e:
            print(f"\n❌ ERROR DURANTE LA LIMPIEZA: {e}")
            import traceback
            traceback.print_exc()


# ============================================================================
# MAIN - Dependency Injection Setup
# ============================================================================

def main():
    """Main entry point with dependency injection"""
    try:
        # Import connection factory
        from src.modules.receipts.database.connection_pool import get_connection

        # Build dependency chain (Dependency Injection)
        repository = MySQLCleanupRepository(connection_factory=get_connection)
        service = CleanupService(repository=repository)
        presenter = CleanupPresenter(service=service)

        # Run application
        presenter.run()

    except ImportError as e:
        print(f"❌ Error importando dependencias: {e}")
        print("Asegúrate de que el módulo de conexión esté disponible.")
        sys.exit(1)
    except BusinessLogicError as e:
        print(f"❌ Error de lógica de negocio: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
