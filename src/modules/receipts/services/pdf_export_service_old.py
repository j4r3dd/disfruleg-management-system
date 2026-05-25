# -*- coding: utf-8 -*-
"""
PDF Export Service - VERSIÓN FINAL
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.colors import HexColor

from src.modules.receipts.services.base_service import BaseService
from src.modules.receipts.components.user_preferences import get_preferences
from src.modules.receipts.logging_config import get_logger, PerformanceLogger, LogContext
from src.modules.receipts.exceptions import (
    PDFGenerationError,
    FileWriteError,
    DirectoryNotFoundError,
)
import logging


logger = get_logger(__name__)


BUSINESS_CONFIG = {
    "name": "DISFRULEG",
    "subtitle": "Comercializadora Castruita",
    "address": "Felipe Páramo #160, Veinte de Noviembre C.P. 58219, Morelia, Michoacán",
    "phone": "Cel. (443) 504 9098",
    "rfc": "CACJ850827UF3",
    "regimen_fiscal": "Régimen Simplificado de Confianza",
}

COLOR_HEADER = HexColor('#8B1A1A')
COLOR_ACCENT = HexColor('#C62828')
COLOR_TOTAL = HexColor('#B71C1C')
COLOR_TEXT_LIGHT = colors.whitesmoke
COLOR_GRAY_LIGHT = HexColor('#F5F5F5')
COLOR_FOLIO_BG = HexColor('#FFD700')


class PDFExportService(BaseService):
    """Service for PDF generation with enhanced customization"""

    def __init__(self):
        super().__init__()
        self.preferences = get_preferences()
        self.company_name = BUSINESS_CONFIG["name"]
        self.logger = logger
        self.perf = PerformanceLogger(logger)

    def _get_export_directory(self) -> str:
        """Get PDF export directory from user preferences"""
        pdf_dir = self.preferences.get_or_prompt_export_path('pdf')

        if not pdf_dir:
            self._log_warning("Usuario canceló selección, usando directorio predeterminado")
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            pdf_dir = os.path.join(project_root, "output", "recibos")

        os.makedirs(pdf_dir, exist_ok=True)
        return pdf_dir

    def _generate_filename(
        self,
        client_name: str,
        folio: Optional[int] = None,
        with_sections: bool = False
    ) -> str:
        """Generate PDF filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folio_suffix = f"_N{folio}" if folio else ""
        section_prefix = "Seccionado_" if with_sections else ""

        safe_name = client_name.replace(' ', '_')
        return f"{section_prefix}{safe_name}{folio_suffix}_{timestamp}.pdf"

    def _get_logo_path(self) -> Optional[str]:
        """Get logo path from assets folder"""
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        
        if os.path.exists(logo_path):
            self.logger.debug(f"Logo encontrado en: {logo_path}")
            return logo_path
        
        self.logger.warning("Logo no encontrado en assets/logo.png")
        return None

    def _create_folio_header(
        self,
        story: List,
        styles: Any,
        folio: Optional[int] = None
    ):
        """Create yellow rectangle header with folio number"""
        # Si no hay folio, generar uno basado en timestamp
        if folio is None:
            folio = int(datetime.now().strftime("%d%H%M%S"))
        
        style_folio_box = ParagraphStyle(
            name='FolioBox',
            parent=styles['Normal'],
            fontSize=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.black,
            spaceAfter=6
        )
        
        folio_data = [[Paragraph(f"FOLIO N° {folio:06d}", style_folio_box)]]
        folio_table = Table(folio_data, colWidths=[520])
        
        folio_style = TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), COLOR_FOLIO_BG),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (0, 0), 20),
            ('RIGHTPADDING', (0, 0), (0, 0), 20),
            ('TOPPADDING', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10),
            ('BORDER', (0, 0), (0, 0), 2, colors.black),
        ])
        folio_table.setStyle(folio_style)
        story.append(folio_table)
        story.append(Spacer(1, 8))

    def _create_compact_header(
        self,
        story: List,
        styles: Any,
        folio: Optional[int] = None
    ):
        """Create compact PDF header with logo and invoice number"""
        
        logo_path = self._get_logo_path()
        
        if logo_path:
            try:
                logo_img = Image(logo_path, width=220, height=60)
                
                company_info = f"""<font size=7>
                <b>{BUSINESS_CONFIG['name']}</b> - {BUSINESS_CONFIG['subtitle']}<br/>
                {BUSINESS_CONFIG['address']}<br/>
                {BUSINESS_CONFIG['phone']} | RFC: {BUSINESS_CONFIG['rfc']}
                </font>"""
                
                if folio:
                    folio_info = f"""<font size=11 color='#C62828'><b>FACTURA N° {folio:06d}</b></font><br/>
                    <font size=8>{datetime.now().strftime('%d-%b-%y')}</font>"""
                    
                    header_data = [[logo_img, Paragraph(company_info, styles['Normal']), 
                                   Paragraph(folio_info, styles['Normal'])]]
                    header_table = Table(header_data, colWidths=[230, 200, 90])
                else:
                    header_data = [[logo_img, Paragraph(company_info, styles['Normal'])]]
                    header_table = Table(header_data, colWidths=[230, 290])
                
                header_style = TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ])
                header_table.setStyle(header_style)
                story.append(header_table)
                story.append(Spacer(1, 4))
                
            except Exception as e:
                self.logger.warning(f"Error al cargar logo: {e}")
                self._create_compact_header_without_logo(story, styles, folio)
        else:
            self._create_compact_header_without_logo(story, styles, folio)

    def _create_compact_header_without_logo(
        self,
        story: List,
        styles: Any,
        folio: Optional[int] = None
    ):
        """Compact header without logo"""
        
        style_title = ParagraphStyle(
            name='CompactTitle',
            parent=styles['h1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=COLOR_HEADER,
            alignment=TA_CENTER,
            spaceAfter=2
        )
        story.append(Paragraph(f"{BUSINESS_CONFIG['name']} - {BUSINESS_CONFIG['subtitle']}", style_title))
        
        style_info = ParagraphStyle(
            name='CompactInfo',
            parent=styles['Normal'],
            fontSize=7,
            alignment=TA_CENTER,
            spaceAfter=1
        )
        story.append(Paragraph(f"{BUSINESS_CONFIG['address']} | {BUSINESS_CONFIG['phone']}", style_info))
        story.append(Paragraph(f"RFC: {BUSINESS_CONFIG['rfc']}", style_info))
        
        if folio:
            style_folio = ParagraphStyle(
                name='FolioStyle',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_CENTER,
                textColor=COLOR_ACCENT,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(f"FACTURA N° {folio:06d} | {datetime.now().strftime('%d-%b-%y')}", style_folio))
        
        story.append(Spacer(1, 4))

    def _create_client_info(
        self,
        story: List,
        styles: Any,
        client_name: str
    ):
        """Create client information section"""
        style_client = ParagraphStyle(
            name='ClientStyle',
            parent=styles['h3'],
            fontSize=10,
            textColor=COLOR_HEADER,
            fontName='Helvetica-Bold',
            spaceAfter=4
        )
        story.append(Paragraph(f"Cliente: {client_name}", style_client))

    def _create_items_table(
        self,
        items: List[List[str]]
    ) -> Table:
        """Create items table with correct column order and unit"""
        
        table_data = [['PRODUCTO', 'CANT.', 'UNIDAD', 'P.UNIT.', 'TOTAL']]
        
        items_reorganizados = []
        for item in items:
            try:
                if len(item) >= 5:
                    producto = str(item[0])
                    cantidad = str(item[1])
                    unidad = str(item[2])
                    precio_unitario = str(item[3])
                    total = str(item[4])
                else:
                    producto = str(item[0]) if len(item) > 0 else ''
                    cantidad = str(item[1]) if len(item) > 1 else ''
                    unidad = str(item[2]) if len(item) > 2 else ''
                    precio_unitario = str(item[3]) if len(item) > 3 else ''
                    total = str(item[4]) if len(item) > 4 else ''
                
                items_reorganizados.append([producto, cantidad, unidad, precio_unitario, total])
            except Exception as e:
                self.logger.warning(f"Error procesando item {item}: {e}")
                continue
        
        table_data.extend(items_reorganizados)
        
        tabla = Table(table_data, colWidths=[270, 35, 50, 60, 65])

        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_HEADER),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_TEXT_LIGHT),
            
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('BACKGROUND', (0, 2), (-1, -2), HexColor('#F8F9FA')),
            
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#DDDDDD')),
            
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            
            ('PADDING', (0, 0), (-1, 0), 3),
            ('PADDING', (0, 1), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        tabla.setStyle(style)
        return tabla

    def _create_compact_total_section(
        self,
        story: List,
        styles: Any,
        total: float
    ):
        """Create compact total section"""
        story.append(Spacer(1, 4))
        
        style_total = ParagraphStyle(
            name='TotalCompact',
            parent=styles['Normal'],
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=COLOR_TOTAL,
            spaceAfter=6
        )
        story.append(Paragraph(f"TOTAL: ${total:,.2f}", style_total))

    def generate_simple_pdf(
        self,
        client_name: str,
        items: List[List[str]],
        total: float,
        folio: Optional[int] = None
    ) -> Optional[str]:
        """Generate compact PDF receipt"""
        operation_name = f"Generate simple PDF | {client_name}"

        with LogContext(self.logger, operation_name, logging.INFO):
            try:
                self.logger.info(
                    f"PDF request | {client_name} | "
                    f"Items: {len(items)} | Total: ${total:.2f}"
                )

                export_dir = self._get_export_directory()
                filename = self._generate_filename(client_name, folio)
                file_path = os.path.join(export_dir, filename)

                doc = SimpleDocTemplate(
                    file_path, 
                    pagesize=letter, 
                    topMargin=20,
                    bottomMargin=20,
                    leftMargin=25,
                    rightMargin=25
                )
                story = []
                styles = getSampleStyleSheet()

                self._create_folio_header(story, styles, folio)
                self._create_compact_header(story, styles, folio)
                self._create_client_info(story, styles, client_name)
                story.append(Spacer(1, 4))

                tabla = self._create_items_table(items)
                story.append(tabla)

                self._create_compact_total_section(story, styles, total)
                
                story.append(Spacer(1, 2))
                
                style_reception = ParagraphStyle(
                    name='ReceptionSec',
                    parent=styles['Normal'],
                    fontName='Helvetica-Bold',
                    fontSize=7,
                    textColor=COLOR_HEADER,
                    spaceAfter=2
                )
                story.append(Paragraph("DATOS DE RECEPCIÓN", style_reception))
                
                reception_data = [
                    ['HORA: _____________', 'RECIBIÓ: ____________________', 'FIRMA: _____________'],
                ]
                
                reception_table = Table(reception_data, colWidths=[110, 210, 110])
                reception_style = TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ])
                reception_table.setStyle(reception_style)
                story.append(reception_table)

                doc.build(story)

                file_size = os.path.getsize(file_path)
                self.logger.info(f"✅ PDF generated | {file_path} | {file_size} bytes")
                return file_path

            except Exception as e:
                self.logger.error(f"PDF generation failed | {client_name}", exc_info=True)
                raise PDFGenerationError(client_name=client_name, reason=str(e))

    def generate_sectioned_pdf(
        self,
        client_name: str,
        sections: Dict[str, Dict[str, Any]],
        total: float,
        folio: Optional[int] = None
    ) -> Optional[str]:
        """Generate compact PDF with sections"""
        operation_name = f"Generate sectioned PDF | {client_name}"

        with LogContext(self.logger, operation_name, logging.INFO):
            try:
                total_items = sum(len(s['items']) for s in sections.values())
                self.logger.info(
                    f"Sectioned PDF | {client_name} | "
                    f"Sections: {len(sections)} | Items: {total_items}"
                )

                export_dir = self._get_export_directory()
                filename = self._generate_filename(client_name, folio, with_sections=True)
                file_path = os.path.join(export_dir, filename)

                doc = SimpleDocTemplate(
                    file_path, 
                    pagesize=letter, 
                    topMargin=20,
                    bottomMargin=20,
                    leftMargin=25,
                    rightMargin=25
                )
                story = []
                styles = getSampleStyleSheet()

                self._create_folio_header(story, styles, folio)
                self._create_compact_header(story, styles, folio)
                self._create_client_info(story, styles, client_name)
                story.append(Spacer(1, 4))

                for idx, (section_name, section_data) in enumerate(sections.items(), 1):
                    self.logger.debug(
                        f"Processing section {idx}/{len(sections)}: {section_name} "
                        f"({len(section_data['items'])} items)"
                    )

                    style_section = ParagraphStyle(
                        name=f'Section{idx}',
                        parent=styles['Normal'],
                        alignment=TA_CENTER,
                        fontName='Helvetica-Bold',
                        fontSize=8,
                        textColor=COLOR_HEADER,
                        backColor=HexColor('#FFE6E6'),
                        borderPadding=3,
                        spaceAfter=3
                    )
                    story.append(Paragraph(f"✦ {section_name.upper()} ✦", style_section))

                    items_section = section_data['items']
                    if items_section:
                        tabla = self._create_items_table(items_section)
                        story.append(tabla)
                        story.append(Spacer(1, 3))

                        subtotal = section_data['subtotal']
                        style_subtotal = ParagraphStyle(
                            name=f'Subtotal{idx}',
                            parent=styles['Normal'],
                            alignment=TA_RIGHT,
                            fontName='Helvetica-Bold',
                            fontSize=8,
                            textColor=HexColor('#444444')
                        )
                        story.append(Paragraph(f"Subtotal {section_name}: ${subtotal:,.2f}", style_subtotal))
                        story.append(Spacer(1, 4))

                story.append(Spacer(1, 2))
                style_total = ParagraphStyle(
                    name='TotalGeneral',
                    parent=styles['Normal'],
                    alignment=TA_RIGHT,
                    textColor=COLOR_TOTAL,
                    fontName='Helvetica-Bold',
                    fontSize=11
                )
                story.append(Paragraph(f"TOTAL GENERAL: ${total:,.2f}", style_total))
                story.append(Spacer(1, 4))
                
                style_reception = ParagraphStyle(
                    name='ReceptionSec',
                    parent=styles['Normal'],
                    fontName='Helvetica-Bold',
                    fontSize=7,
                    textColor=COLOR_HEADER,
                    spaceAfter=2
                )
                story.append(Paragraph("DATOS DE RECEPCIÓN", style_reception))
                
                reception_data = [
                    ['HORA: _____________', 'RECIBIÓ: ____________________', 'FIRMA: _____________'],
                ]
                
                reception_table = Table(reception_data, colWidths=[110, 210, 110])
                reception_style = TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 1),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ])
                reception_table.setStyle(reception_style)
                story.append(reception_table)

                doc.build(story)

                file_size = os.path.getsize(file_path)
                self.logger.info(f"✅ Sectioned PDF | {file_path} | {file_size} bytes")
                return file_path

            except Exception as e:
                self.logger.error(f"Sectioned PDF failed | {client_name}", exc_info=True)
                raise PDFGenerationError(
                    client_name=client_name,
                    reason=f"Sectioned PDF error: {str(e)}"
                )