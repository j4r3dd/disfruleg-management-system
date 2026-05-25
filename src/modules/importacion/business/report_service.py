# -*- coding: utf-8 -*-
"""
Report Service - Business Logic
Handles generation of import reports
NO direct database access - pure business logic!
"""

from typing import List, Optional
from datetime import datetime
from pathlib import Path

from ..domain.models import ExtractedProduct, ProductChange, ImportReport
from ..domain.exceptions import ReportGenerationError


class ReportService:
    """
    Service for generating import reports
    Contains business logic for report generation
    """

    def __init__(self):
        """Initialize report service"""
        self.reportes_dir = Path("reportes_importacion")

    def generate_report(
        self,
        usuario: str,
        nombre_completo: str,
        pdf_path: str,
        cambios: List[ProductChange],
        productos_sin_precio: List[ExtractedProduct],
        total_grupos: int,
        cambios_exitosos: int
    ) -> str:
        """
        Generate detailed import report

        Args:
            usuario: Username
            nombre_completo: Full name
            pdf_path: Path to imported PDF
            cambios: List of changes applied
            productos_sin_precio: Products without price
            total_grupos: Number of affected groups
            cambios_exitosos: Number of successful changes

        Returns:
            Path to generated report file

        Raises:
            ReportGenerationError: If report generation fails
        """
        # Fail fast: Validate inputs
        if not usuario or not usuario.strip():
            raise ValueError("Usuario cannot be empty")

        if not pdf_path:
            raise ValueError("PDF path cannot be empty")

        try:
            # Create reports directory if it doesn't exist
            self.reportes_dir.mkdir(exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.reportes_dir / f"importacion_{timestamp}.txt"

            # Build report content
            contenido = self._build_report_content(
                usuario=usuario,
                nombre_completo=nombre_completo,
                pdf_path=pdf_path,
                cambios=cambios,
                productos_sin_precio=productos_sin_precio,
                total_grupos=total_grupos,
                cambios_exitosos=cambios_exitosos
            )

            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(contenido))

            return str(filename)

        except Exception as e:
            raise ReportGenerationError(f"Error generating report: {e}")

    def _build_report_content(
        self,
        usuario: str,
        nombre_completo: str,
        pdf_path: str,
        cambios: List[ProductChange],
        productos_sin_precio: List[ExtractedProduct],
        total_grupos: int,
        cambios_exitosos: int
    ) -> List[str]:
        """Build report content lines"""
        contenido = []

        # Header
        contenido.append("=" * 70)
        contenido.append("REPORTE DE IMPORTACIÓN DE COTIZACIÓN")
        contenido.append("=" * 70)
        contenido.append(f"\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        contenido.append(f"Usuario: {nombre_completo}")
        contenido.append(f"Archivo: {Path(pdf_path).name}")
        contenido.append("\n" + "=" * 70)

        # Summary
        nuevos = sum(1 for c in cambios if c.tipo == 'nuevo')
        actualizados = sum(1 for c in cambios if c.tipo == 'actualizar')

        contenido.append("\nRESUMEN DE CAMBIOS")
        contenido.append("-" * 70)
        contenido.append(f"Total de productos procesados: {cambios_exitosos}")
        contenido.append(f"  • Productos nuevos: {nuevos}")
        contenido.append(f"  • Productos actualizados: {actualizados}")
        contenido.append(f"  • Grupos afectados: {total_grupos}")

        if productos_sin_precio:
            contenido.append(f"  • Productos sin precio: {len(productos_sin_precio)}")

        # New products detail
        if nuevos > 0:
            contenido.append("\n" + "=" * 70)
            contenido.append("PRODUCTOS NUEVOS")
            contenido.append("-" * 70)
            for c in cambios:
                if c.tipo == 'nuevo':
                    precio_str = (
                        f"${c.precio_nuevo:.2f}"
                        if c.tiene_precio
                        else "SIN PRECIO"
                    )
                    contenido.append(f"  • {c.nombre} ({c.unidad}) - {precio_str}")

        # Updated products detail
        if actualizados > 0:
            contenido.append("\n" + "=" * 70)
            contenido.append("PRODUCTOS ACTUALIZADOS")
            contenido.append("-" * 70)
            for c in cambios:
                if c.tipo == 'actualizar':
                    precio_str = (
                        f"${c.precio_nuevo:.2f}"
                        if c.tiene_precio
                        else "SIN PRECIO"
                    )
                    contenido.append(f"  • {c.nombre} ({c.unidad}) - {precio_str}")

        # Products without price
        if productos_sin_precio:
            contenido.append("\n" + "=" * 70)
            contenido.append("⚠️ PRODUCTOS QUE REQUIEREN ASIGNACIÓN DE PRECIO")
            contenido.append("-" * 70)
            for p in productos_sin_precio:
                contenido.append(f"  • {p.nombre} ({p.unidad})")

        # Footer
        contenido.append("\n" + "=" * 70)
        contenido.append("FIN DEL REPORTE")
        contenido.append("=" * 70)

        return contenido
