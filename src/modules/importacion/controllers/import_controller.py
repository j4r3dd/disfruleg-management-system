# -*- coding: utf-8 -*-
"""
Import Controller - Controller Layer
Orchestrates workflow between UI and business services
Handles business logic flow and decision making
NO direct UI code - returns data to UI for presentation
"""

from typing import List, Tuple, Optional, Dict, Any, Callable
from decimal import Decimal
from pathlib import Path

from ..business.import_service import ImportService
from ..business.pdf_extractor_service import PDFExtractorService
from ..business.report_service import ReportService
from ..data.repositories import IPriceRepository
from ..domain.models import ExtractedProduct, ProductChange, SystemIntegrityCheck
from ..domain.exceptions import (
    PDFExtractionError,
    PriceApplicationError,
    ReportGenerationError,
    SystemIntegrityError
)


class ImportController:
    """
    Controller for import workflow
    Orchestrates between UI and business services
    Handles workflow logic, validations, and confirmations

    ✅ Follows Clean Architecture:
    - Depends on service interfaces (IProductRepository, etc.)
    - NO direct UI dependencies
    - Returns data structures for UI to present
    - Handles business workflow orchestration
    """

    def __init__(
        self,
        import_service: ImportService,
        pdf_extractor: PDFExtractorService,
        report_service: ReportService,
        price_repo: IPriceRepository
    ):
        """
        Initialize controller with injected dependencies

        Args:
            import_service: Service for import operations
            pdf_extractor: Service for PDF extraction
            report_service: Service for report generation
            price_repo: Repository for price/group data access
        """
        # Fail fast: Validate dependencies
        if import_service is None:
            raise ValueError("import_service cannot be None")
        if pdf_extractor is None:
            raise ValueError("pdf_extractor cannot be None")
        if report_service is None:
            raise ValueError("report_service cannot be None")
        if price_repo is None:
            raise ValueError("price_repo cannot be None")

        self.import_service = import_service
        self.pdf_extractor = pdf_extractor
        self.report_service = report_service
        self.price_repo = price_repo

    def validate_system_integrity(self) -> Tuple[bool, Optional[str]]:
        """
        Validate system integrity before allowing import

        Returns:
            Tuple of (is_valid, warning_message)
            - is_valid: True if no warnings or user accepted them
            - warning_message: Warning message to show user (None if no warnings)

        Raises:
            SystemIntegrityError: If integrity check fails
        """
        try:
            integrity_check = self.import_service.validate_system_integrity()

            if integrity_check.tiene_advertencias:
                mensaje = integrity_check.get_mensaje_advertencias()
                return (False, mensaje)

            return (True, None)

        except Exception as e:
            raise SystemIntegrityError(f"System integrity validation failed: {e}")

    def load_groups(self) -> List[Dict[str, Any]]:
        """
        Load available groups from database

        Returns:
            List of group dictionaries with keys: id, clave, descuento

        Raises:
            Exception: If loading fails
        """
        try:
            grupos = self.price_repo.get_all_groups_with_discounts()

            if not grupos:
                return []

            # Normalize to dict format
            grupos_normalizados = [
                {
                    'id': g['id_grupo'] if isinstance(g, dict) else g[0],
                    'clave': g['clave_grupo'] if isinstance(g, dict) else g[1],
                    'descuento': g['descuento'] if isinstance(g, dict) else g[2]
                }
                for g in grupos
            ]

            return grupos_normalizados

        except Exception as e:
            raise Exception(f"Error loading groups: {e}")

    def process_pdf(
        self,
        pdf_path: str,
        actualizar_existentes: bool,
        agregar_nuevos: bool,
        progress_callback: Optional[Callable[[float, str, str], None]] = None
    ) -> Tuple[List[ProductChange], List[ExtractedProduct], Dict[str, int]]:
        """
        Extract data from PDF and generate proposed changes

        Args:
            pdf_path: Path to PDF file
            actualizar_existentes: Whether to update existing products
            agregar_nuevos: Whether to add new products
            progress_callback: Optional callback(progress, status, detail) for progress updates

        Returns:
            Tuple of (cambios_propuestos, productos_sin_precio, statistics)
            - cambios_propuestos: List of proposed changes
            - productos_sin_precio: List of products without price
            - statistics: Dict with keys: total, nuevos, actualizados

        Raises:
            PDFExtractionError: If PDF extraction fails
            ValueError: If validation fails
        """
        # Fail fast: Validate inputs
        if not pdf_path:
            raise ValueError("PDF path cannot be empty")

        if not Path(pdf_path).exists():
            raise ValueError(f"PDF file not found: {pdf_path}")

        try:
            # Step 1: Extract products from PDF
            if progress_callback:
                progress_callback(0.2, "Extrayendo productos del PDF...", "Analizando documento")

            productos_extraidos = self.pdf_extractor.extract_products(pdf_path)

            if not productos_extraidos:
                raise PDFExtractionError("No se pudieron extraer productos del PDF")

            # Step 2: Generate proposed changes
            if progress_callback:
                progress_callback(
                    0.5,
                    "Analizando cambios...",
                    f"{len(productos_extraidos)} productos encontrados"
                )

            cambios_propuestos, productos_sin_precio = self.import_service.generate_changes(
                productos_extraidos,
                actualizar_existentes,
                agregar_nuevos
            )

            # Step 3: Calculate statistics
            if progress_callback:
                progress_callback(0.8, "Generando estadísticas...", "Casi listo")

            total, nuevos, actualizados = self.import_service.get_statistics(cambios_propuestos)

            statistics = {
                'total': total,
                'nuevos': nuevos,
                'actualizados': actualizados
            }

            # Step 4: Complete
            if progress_callback:
                progress_callback(1.0, "¡Completado!", "")

            return cambios_propuestos, productos_sin_precio, statistics

        except PDFExtractionError:
            raise
        except Exception as e:
            raise PDFExtractionError(f"Error processing PDF: {e}")

    def validate_apply_changes(
        self,
        cambios_propuestos: List[ProductChange],
        productos_sin_precio: List[ExtractedProduct],
        selected_group_id: Optional[int],
        grupos_disponibles: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate that changes can be applied

        Args:
            cambios_propuestos: List of proposed changes
            productos_sin_precio: List of products without price
            selected_group_id: ID of selected group
            grupos_disponibles: List of available groups

        Returns:
            Tuple of (is_valid, error_message, selected_group)
            - is_valid: True if validation passes
            - error_message: Error message if validation fails (None if valid)
            - selected_group: Selected group dict (None if validation fails)
        """
        # Validate there are changes
        if not cambios_propuestos:
            return (False, "No hay cambios para aplicar", None)

        # Validate group selection
        if selected_group_id is None:
            return (
                False,
                "Debes seleccionar un grupo de precios antes de aplicar los cambios.",
                None
            )

        # Find selected group
        selected_group = next(
            (g for g in grupos_disponibles if g['id'] == selected_group_id),
            None
        )

        if not selected_group:
            return (False, "Grupo seleccionado no válido", None)

        return (True, None, selected_group)

    def build_confirmation_message(
        self,
        cambios_propuestos: List[ProductChange],
        productos_sin_precio: List[ExtractedProduct],
        selected_group: Dict[str, Any]
    ) -> str:
        """
        Build confirmation message for user

        Args:
            cambios_propuestos: List of proposed changes
            productos_sin_precio: List of products without price
            selected_group: Selected group dict

        Returns:
            Formatted confirmation message
        """
        total, nuevos, actualizados = self.import_service.get_statistics(cambios_propuestos)
        sin_precio = len(productos_sin_precio)

        mensaje = f"📊 RESUMEN DE CAMBIOS\n\n"
        mensaje += f"• {nuevos} productos nuevos\n"
        mensaje += f"• {actualizados} productos actualizados\n"
        if sin_precio > 0:
            mensaje += f"• {sin_precio} productos sin precio\n"
        mensaje += f"\n⚠️ El stock NO será modificado\n\n"
        mensaje += f"🎯 Grupo seleccionado: {selected_group['clave']}\n"
        mensaje += f"   (Descuento del tipo: {selected_group['descuento']}%)\n\n"
        mensaje += f"✅ Los precios se aplicarán SOLO al grupo seleccionado\n"
        mensaje += f"   Los demás grupos NO serán afectados"

        return mensaje

    def apply_changes(
        self,
        cambios_propuestos: List[ProductChange],
        productos_sin_precio: List[ExtractedProduct],
        selected_group_id: int,
        selected_group: Dict[str, Any],
        usuario: str,
        nombre_completo: str,
        pdf_path: str,
        db_commit_callback: Callable[[], None],
        db_rollback_callback: Callable[[], None]
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Apply changes to database and generate report

        Args:
            cambios_propuestos: List of proposed changes
            productos_sin_precio: List of products without price
            selected_group_id: ID of selected group
            selected_group: Selected group dict
            usuario: Username
            nombre_completo: User full name
            pdf_path: Path to PDF file
            db_commit_callback: Callback to commit database transaction
            db_rollback_callback: Callback to rollback database transaction

        Returns:
            Tuple of (success, error_message, success_message)
            - success: True if operation succeeded
            - error_message: Error message if failed (None if success)
            - success_message: Success message with details (None if failed)

        Raises:
            PriceApplicationError: If changes application fails
            ReportGenerationError: If report generation fails (non-critical)
        """
        try:
            # Apply changes to selected group only
            cambios_exitosos, productos_creados = self.import_service.apply_changes(
                cambios_propuestos,
                usuario,
                selected_group_id
            )

            # Commit transaction
            db_commit_callback()

            # Generate report (non-critical - errors are caught)
            archivo_reporte = None
            report_warning = False

            try:
                archivo_reporte = self.report_service.generate_report(
                    usuario=usuario,
                    nombre_completo=nombre_completo,
                    pdf_path=pdf_path,
                    cambios=cambios_propuestos,
                    productos_sin_precio=productos_sin_precio,
                    total_grupos=1,  # Only one group affected
                    cambios_exitosos=cambios_exitosos
                )
            except ReportGenerationError as e:
                print(f"Warning: Error generating report: {e}")
                report_warning = True

            # Build success message
            mensaje_exito = f"✅ IMPORTACIÓN EXITOSA\n\n"
            mensaje_exito += f"• {cambios_exitosos} productos procesados\n"
            mensaje_exito += f"• Precios aplicados al grupo: {selected_group['clave']}\n"

            if productos_sin_precio:
                mensaje_exito += f"\n⚠️ {len(productos_sin_precio)} productos sin precio\n"

            if archivo_reporte:
                mensaje_exito += f"\n\n📄 Reporte guardado en:\n{archivo_reporte}"
            elif report_warning:
                mensaje_exito += f"\n\n⚠️ No se pudo generar el reporte (importación exitosa)"

            return (True, None, mensaje_exito)

        except PriceApplicationError as e:
            db_rollback_callback()
            error_msg = f"Error aplicando cambios:\n{str(e)}"
            return (False, error_msg, None)

        except Exception as e:
            db_rollback_callback()
            error_msg = f"Error aplicando cambios:\n{str(e)}"
            return (False, error_msg, None)

    def get_statistics(
        self,
        cambios_propuestos: List[ProductChange]
    ) -> Tuple[int, int, int]:
        """
        Get statistics about proposed changes

        Args:
            cambios_propuestos: List of proposed changes

        Returns:
            Tuple of (total, nuevos, actualizados)
        """
        return self.import_service.get_statistics(cambios_propuestos)
