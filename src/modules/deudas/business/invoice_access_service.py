# -*- coding: utf-8 -*-
"""
Invoice Access Service - Business Logic Layer
Handles invoice document retrieval and PDF access
NEW FILE: deudas/business/invoice_access_service.py
"""

from typing import Optional, List
from pathlib import Path
from datetime import datetime, date
import logging

from ..data.repositories import IDebtRepository
from ..domain.exceptions import DebtNotFoundError

logger = logging.getLogger(__name__)


class InvoiceAccessService:
    """
    Service for accessing and retrieving invoice documents
    Handles PDF storage, retrieval, regeneration, and audit logging
    """

    def __init__(
        self,
        storage_path: str,
        debt_repo: IDebtRepository,
        audit_enabled: bool = True
    ):
        """
        Initialize invoice access service

        Args:
            storage_path: Path where PDFs are stored
            debt_repo: Debt repository for queries
            audit_enabled: Enable audit logging of PDF access
        """
        self.storage_path = Path(storage_path)
        self.debt_repo = debt_repo
        self.audit_enabled = audit_enabled
        
        # Create storage directory if needed
        self.storage_path.mkdir(parents=True, exist_ok=True)

    # ==================== PDF RETRIEVAL ====================

    def get_invoice_pdf(self, id_factura: int) -> Optional[bytes]:
        """
        Retrieve PDF bytes for an invoice
        First tries cached PDF, then attempts to regenerate

        Args:
            id_factura: Invoice ID

        Returns:
            PDF file bytes or None if not found/cannot regenerate
        """
        try:
            # Option 1: Try cached PDF
            pdf_path = self._get_pdf_path(id_factura)
            
            if pdf_path.exists():
                logger.info(f"Retrieved cached PDF for invoice {id_factura}")
                with open(pdf_path, 'rb') as f:
                    return f.read()
            
            # Option 2: Try to regenerate (optional)
            # This would call the receipts module to regenerate
            # For now, return None if not cached
            logger.warning(f"PDF not found for invoice {id_factura}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving PDF for invoice {id_factura}: {e}")
            return None

    def get_invoices_by_search(
        self,
        query: str,
        id_cliente: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        incluir_pagadas: bool = True
    ) -> List[dict]:
        """
        Search invoices with PDF availability info

        Args:
            query: Search term (invoice #, client name, reference)
            id_cliente: Optional client ID filter
            fecha_inicio: Optional start date
            fecha_fin: Optional end date
            incluir_pagadas: Include paid invoices

        Returns:
            List of invoice search results with PDF info
        """
        try:
            # Query database for invoices
            results = self.debt_repo.search_invoices(
                query=query,
                id_cliente=id_cliente,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                incluir_pagadas=incluir_pagadas
            )
            
            # Enrich with PDF availability
            enriched_results = []
            for result in results:
                enriched = dict(result)
                
                # Check if PDF exists
                pdf_path = self._get_pdf_path(result['id_factura'])
                enriched['tiene_pdf'] = pdf_path.exists()
                enriched['ruta_pdf'] = str(pdf_path) if pdf_path.exists() else None
                
                enriched_results.append(enriched)
            
            logger.info(f"Found {len(enriched_results)} invoices matching '{query}'")
            return enriched_results
            
        except Exception as e:
            logger.error(f"Error searching invoices: {e}")
            return []

    # ==================== PDF MANAGEMENT ====================

    def cache_pdf(self, id_factura: int, pdf_bytes: bytes) -> bool:
        """
        Cache PDF locally for quick retrieval

        Args:
            id_factura: Invoice ID
            pdf_bytes: PDF file bytes

        Returns:
            True if cached successfully, False otherwise
        """
        try:
            pdf_path = self._get_pdf_path(id_factura)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            logger.info(f"Cached PDF for invoice {id_factura} ({len(pdf_bytes)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching PDF for invoice {id_factura}: {e}")
            return False

    def delete_cached_pdf(self, id_factura: int) -> bool:
        """
        Delete cached PDF

        Args:
            id_factura: Invoice ID

        Returns:
            True if deleted, False if didn't exist or error
        """
        try:
            pdf_path = self._get_pdf_path(id_factura)
            
            if pdf_path.exists():
                pdf_path.unlink()
                logger.info(f"Deleted cached PDF for invoice {id_factura}")
                return True
            else:
                logger.warning(f"PDF not found for invoice {id_factura}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting PDF for invoice {id_factura}: {e}")
            return False

    def clear_old_cache(self, days_old: int = 30) -> int:
        """
        Clear cached PDFs older than specified days

        Args:
            days_old: Age threshold in days

        Returns:
            Number of files deleted
        """
        try:
            import time
            current_time = time.time()
            deleted_count = 0
            
            for pdf_file in self.storage_path.glob("**/*.pdf"):
                file_age = current_time - pdf_file.stat().st_mtime
                file_age_days = file_age / (24 * 3600)
                
                if file_age_days > days_old:
                    try:
                        pdf_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Could not delete {pdf_file}: {e}")
            
            logger.info(f"Cleared {deleted_count} old PDF cache files (older than {days_old} days)")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing PDF cache: {e}")
            return 0

    # ==================== AVAILABILITY CHECKS ====================

    def check_pdf_exists(self, id_factura: int) -> bool:
        """
        Check if PDF is cached and available

        Args:
            id_factura: Invoice ID

        Returns:
            True if PDF exists
        """
        pdf_path = self._get_pdf_path(id_factura)
        return pdf_path.exists()

    def get_pdf_info(self, id_factura: int) -> Optional[dict]:
        """
        Get information about a cached PDF

        Args:
            id_factura: Invoice ID

        Returns:
            Dictionary with PDF info or None
        """
        try:
            pdf_path = self._get_pdf_path(id_factura)
            
            if not pdf_path.exists():
                return None
            
            stat = pdf_path.stat()
            return {
                'id_factura': id_factura,
                'ruta': str(pdf_path),
                'tamaño_bytes': stat.st_size,
                'fecha_creacion': datetime.fromtimestamp(stat.st_ctime),
                'fecha_modificacion': datetime.fromtimestamp(stat.st_mtime)
            }
            
        except Exception as e:
            logger.error(f"Error getting PDF info for invoice {id_factura}: {e}")
            return None

    # ==================== AUDIT LOGGING ====================

    def log_pdf_access(
        self,
        id_factura: int,
        usuario: str,
        accion: str = 'descarga'
    ):
        """
        Log PDF access for audit purposes

        Args:
            id_factura: Invoice ID
            usuario: Username who accessed
            accion: Action performed (descarga, vista, regeneracion, etc.)
        """
        if not self.audit_enabled:
            return
        
        try:
            # Could log to database or file
            # For now, just log to file
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'id_factura': id_factura,
                'usuario': usuario,
                'accion': accion
            }
            
            logger.info(f"PDF Access: {log_entry}")
            
        except Exception as e:
            logger.error(f"Error logging PDF access: {e}")

    def log_pdf_error(
        self,
        id_factura: int,
        usuario: str,
        error_message: str
    ):
        """
        Log PDF access errors for debugging

        Args:
            id_factura: Invoice ID
            usuario: Username who attempted access
            error_message: Error details
        """
        if not self.audit_enabled:
            return
        
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'id_factura': id_factura,
                'usuario': usuario,
                'error': error_message
            }
            
            logger.error(f"PDF Error: {log_entry}")
            
        except Exception as e:
            logger.error(f"Error logging PDF error: {e}")

    # ==================== HELPER METHODS ====================

    def _get_pdf_path(self, id_factura: int) -> Path:
        """
        Get the file system path for an invoice PDF

        Args:
            id_factura: Invoice ID

        Returns:
            Path object for the PDF file
        """
        # Organize by year/month/id.pdf
        # This keeps the directory structure manageable
        from datetime import datetime
        
        year = datetime.now().year
        month = datetime.now().month
        
        return self.storage_path / f"{year}" / f"{month:02d}" / f"{id_factura}.pdf"

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache info
        """
        try:
            pdf_files = list(self.storage_path.glob("**/*.pdf"))
            total_size = sum(f.stat().st_size for f in pdf_files)
            
            return {
                'total_pdfs': len(pdf_files),
                'total_size_mb': total_size / (1024 * 1024),
                'storage_path': str(self.storage_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


# ==================== INTEGRATION WITH DebtService ====================

# Add this method to DebtService class:

def search_invoice_history(
    self,
    query: str,
    id_cliente: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    incluir_pagadas: bool = True
) -> List[dict]:
    """
    Search invoice history with PDF availability

    Args:
        query: Search term
        id_cliente: Optional client filter
        fecha_inicio: Optional start date
        fecha_fin: Optional end date
        incluir_pagadas: Include paid invoices

    Returns:
        List of invoices with PDF info
    """
    results = self.invoice_access_service.get_invoices_by_search(
        query=query,
        id_cliente=id_cliente,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        incluir_pagadas=incluir_pagadas
    )
    
    return results
