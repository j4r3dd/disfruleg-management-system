# -*- coding: utf-8 -*-
"""
Export Controller
Handles PDF and Excel generation
"""

from typing import Optional

from src.modules.receipts.mvc.controllers.base_controller import BaseController
from src.modules.receipts.mvc.controllers.client_selection_controller import ClientSelectionController
from src.modules.receipts.mvc.models.receipt_model import ReciboModel
from src.modules.receipts.mvc.views.receipt_view import ReciboView
from src.modules.receipts.models.cart_model import CartModel
from src.modules.receipts.services.pdf_export_service import PDFExportService
from src.modules.receipts.services.excel_export_service import ExcelExportService
from src.modules.receipts.exceptions import (
    PDFGenerationError,
    ExcelGenerationError,
    FileWriteError,
    DirectoryNotFoundError,
    ClientNotSelectedError,
    EmptyCartError,
)


class ExportController(BaseController):
    """
    Controller for export operations (PDF and Excel)

    Responsibilities:
    - Generate PDFs
    - Generate Excel files
    - Handle export button clicks
    - Validate data before exporting
    """

    def __init__(
        self,
        view: ReciboView,
        model: ReciboModel,
        cart_model: CartModel,
        client_controller: ClientSelectionController
    ):
        super().__init__(view, model, cart_model)
        self.client_controller = client_controller

        # Initialize export services
        self.pdf_service = PDFExportService()
        self.excel_service = ExcelExportService()

    # ==================== EVENT HANDLERS ====================

    def on_generar_pdf(self):
        """
        Handle 'Generar PDF' button click

        Workflow:
        1. Validate client and cart
        2. Generate PDF with current data
        3. Show success message with path
        """
        try:
            self.log_info("Generando PDF")

            # Validate client
            if not self.client_controller.validate_client_selected():
                return

            # Validate cart has items
            if self.cart_model.is_empty():
                self.show_warning(
                    "Carrito Vacío",
                    "No hay productos para generar el PDF."
                )
                return

            # Generate PDF
            folio_numero = self.model.get_folio() if hasattr(self.model, 'get_folio') else None
            ruta_pdf = self.generate_pdf(folio_numero)

            if ruta_pdf:
                self.log_success(f"PDF generado: {ruta_pdf}")
                self.show_success(
                    "PDF Generado",
                    f"PDF generado exitosamente.\n\nRuta: {ruta_pdf}"
                )

        except ClientNotSelectedError as e:
            # Client validation failed
            self.show_warning("Cliente Requerido", str(e))

        except EmptyCartError as e:
            # Cart is empty
            self.show_warning("Carrito Vacío", str(e))

        except PDFGenerationError as e:
            # PDF generation failed
            client_name = e.details.get('client_name', 'Unknown')
            reason = e.details.get('reason', '')
            self.show_error(
                "Error al Generar PDF",
                f"No se pudo generar el PDF para {client_name}\n\n{reason}"
            )
            self.log_error(f"PDF generation failed: {e}")

        except FileWriteError as e:
            # File write failed
            file_path = e.details.get('file_path', 'Unknown')
            reason = e.details.get('reason', '')
            self.show_error(
                "Error de Escritura",
                f"No se pudo escribir el archivo PDF\n\nRuta: {file_path}\n{reason}"
            )
            self.log_error(f"File write failed: {e}")

        except DirectoryNotFoundError as e:
            # Directory not found
            directory = e.details.get('directory_path', 'Unknown')
            self.show_error(
                "Directorio No Encontrado",
                f"No se encontró el directorio:\n\n{directory}"
            )
            self.log_error(f"Directory not found: {e}")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("generar PDF", e)

    def on_generar_excel(self):
        """
        Handle 'Generar Excel' button click

        Workflow:
        1. Validate client and cart
        2. Generate Excel with current data
        3. Show success message with path
        """
        try:
            self.log_info("Generando Excel")

            # Validate client
            if not self.client_controller.validate_client_selected():
                return

            # Validate cart has items
            if self.cart_model.is_empty():
                self.show_warning(
                    "Carrito Vacío",
                    "No hay productos para generar el Excel."
                )
                return

            # Generate Excel
            ruta_excel = self.generate_excel()

            if ruta_excel:
                self.log_success(f"Excel generado: {ruta_excel}")
                self.show_success(
                    "Excel Generado",
                    f"Excel generado exitosamente.\n\nRuta: {ruta_excel}"
                )

        except ClientNotSelectedError as e:
            # Client validation failed
            self.show_warning("Cliente Requerido", str(e))

        except EmptyCartError as e:
            # Cart is empty
            self.show_warning("Carrito Vacío", str(e))

        except ExcelGenerationError as e:
            # Excel generation failed
            client_name = e.details.get('client_name', 'Unknown')
            reason = e.details.get('reason', '')
            self.show_error(
                "Error al Generar Excel",
                f"No se pudo generar el Excel para {client_name}\n\n{reason}"
            )
            self.log_error(f"Excel generation failed: {e}")

        except FileWriteError as e:
            # File write failed
            file_path = e.details.get('file_path', 'Unknown')
            reason = e.details.get('reason', '')
            self.show_error(
                "Error de Escritura",
                f"No se pudo escribir el archivo Excel\n\nRuta: {file_path}\n{reason}"
            )
            self.log_error(f"File write failed: {e}")

        except DirectoryNotFoundError as e:
            # Directory not found
            directory = e.details.get('directory_path', 'Unknown')
            self.show_error(
                "Directorio No Encontrado",
                f"No se encontró el directorio:\n\n{directory}"
            )
            self.log_error(f"Directory not found: {e}")

        except Exception as e:
            # Unexpected error - use global handler
            self.handle_exception("generar Excel", e)

    # ==================== EXPORT OPERATIONS ====================

    def generate_pdf(self, folio_numero: Optional[int] = None) -> Optional[str]:
        """
        Generate PDF for current cart

        Args:
            folio_numero: Optional folio number for the receipt

        Returns:
            Path to generated PDF

        Raises:
            ClientNotSelectedError: If no client is selected
            PDFGenerationError: If PDF generation fails
        """
        cliente = self.client_controller.get_selected_client()
        if not cliente:
            raise ClientNotSelectedError()

        nombre_cliente = cliente.get('nombre_completo', 'Cliente General')
        total = self.cart_model.get_total()

        # Check if we should use sectioned PDF
        if self.cart_model.sectioning_enabled and len(self.cart_model.sections) > 1:
            # Get sectioned items from model
            items_por_seccion = self.cart_model.get_sectioned_items_for_pdf()

            # Filter out empty sections
            items_filtradas = {
                nombre: datos for nombre, datos in items_por_seccion.items()
                if datos['items']
            }

            if len(items_filtradas) > 1:
                ruta_pdf = self.pdf_service.generate_sectioned_pdf(
                    nombre_cliente,
                    items_filtradas,
                    total,
                    folio_numero
                )
            else:
                # Fallback to simple PDF
                items_pdf = self.cart_model.get_items_for_pdf()
                ruta_pdf = self.pdf_service.generate_simple_pdf(
                    nombre_cliente,
                    items_pdf,
                    total,
                    folio_numero
                )
        else:
            # Use simple PDF
            items_pdf = self.cart_model.get_items_for_pdf()
            ruta_pdf = self.pdf_service.generate_simple_pdf(
                nombre_cliente,
                items_pdf,
                total,
                folio_numero
            )

        self.log_success(f"PDF generado: {ruta_pdf}")
        return ruta_pdf

    def generate_excel(self) -> Optional[str]:
        """
        Generate Excel for current cart

        Returns:
            Path to generated Excel

        Raises:
            ClientNotSelectedError: If no client is selected
            ExcelGenerationError: If Excel generation fails
        """
        cliente = self.client_controller.get_selected_client()
        if not cliente:
            raise ClientNotSelectedError()

        nombre_cliente = cliente.get('nombre_completo', 'Cliente General')
        total = self.cart_model.get_total()

        # Check if we should use sectioned Excel
        if self.cart_model.sectioning_enabled and len(self.cart_model.sections) > 1:
            # Get sectioned items from model
            items_por_seccion = self.cart_model.get_sectioned_items_for_excel()

            # Filter out empty sections
            items_filtradas = {
                nombre: datos for nombre, datos in items_por_seccion.items()
                if datos['items']
            }

            if len(items_filtradas) > 1:
                ruta_excel = self.excel_service.generate_sectioned_excel(
                    nombre_cliente,
                    items_filtradas,
                    total
                )
            else:
                # Fallback to simple Excel
                items_excel = self.cart_model.get_items_for_excel()
                ruta_excel = self.excel_service.generate_simple_excel(
                    nombre_cliente,
                    items_excel
                )
        else:
            # Use simple Excel
            items_excel = self.cart_model.get_items_for_excel()
            ruta_excel = self.excel_service.generate_simple_excel(
                nombre_cliente,
                items_excel
                )

        self.log_success(f"Excel generado: {ruta_excel}")
        return ruta_excel