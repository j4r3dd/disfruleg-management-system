# -*- coding: utf-8 -*-
"""
PDF Export Service - VERSIÓN OPTIMIZADA PARA 30 PRODUCTOS
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
        """Generate PDF filename: FOLIO_DDMMYY_NOMBRECLIENTE.pdf"""
        fecha = datetime.now().strftime("%d%m%y")
        safe_name = client_name.replace(' ', '_')
        folio_str = f"{folio:06d}_" if folio else ""
        return f"{folio_str}{fecha}_{safe_name}.pdf"

    def _get_logo_path(self) -> Optional[str]:
        """Get logo path from assets folder"""
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        
        if os.path.exists(logo_path):
            self.logger.debug(f"Logo encontrado en: {logo_path}")
            return logo_path
        
        self.logger.warning("Logo no encontrado en assets/logo.png")
        return None

    def _get_dynamic_config(self, num_items: int) -> Dict[str, Any]:
        """
        Calcula configuración dinámica basada en cantidad de productos
        Optimiza tamaños de fuente, padding y márgenes para maximizar densidad
        """
        if num_items <= 15:
            # Configuración estándar para pocos productos
            return {
                'font_size_header': 8,
                'font_size_data': 7,
                'font_size_folio': 14,
                'font_size_folio_num': 12,
                'font_size_company': 8,
                'padding_h': 3,
                'padding_v': 2,
                'spacer_header': 4,
                'spacer_table': 3,
                'top_margin': 25,
                'bottom_margin': 25,
            }
        elif num_items <= 25:
            # Configuración media para cantidad moderada
            return {
                'font_size_header': 7,
                'font_size_data': 6,
                'font_size_folio': 12,
                'font_size_folio_num': 11,
                'font_size_company': 7,
                'padding_h': 2,
                'padding_v': 1,
                'spacer_header': 3,
                'spacer_table': 2,
                'top_margin': 25,
                'bottom_margin': 25,
            }
        else:
            # Configuración ultra-compacta para 26+ productos
            return {
                'font_size_header': 6,
                'font_size_data': 5,
                'font_size_folio': 11,
                'font_size_folio_num': 10,
                'font_size_company': 6,
                'padding_h': 2,
                'padding_v': 1,
                'spacer_header': 2,
                'spacer_table': 1,
                'top_margin': 20,
                'bottom_margin': 20,
            }

    def _add_watermark(self, canvas, doc):
        """Add watermark and page border to each page"""
        from reportlab.lib.pagesizes import letter
        width, height = letter
        
        # Dibujar marco/borde alrededor del contenido
        margin = 15
        canvas.setLineWidth(1.5)
        canvas.rect(
            margin,
            margin,
            width - (margin * 2),
            height - (margin * 2),
            fill=0
        )
        
        # Agregar marca de agua
        logo_path = self._get_logo_path()
        if logo_path:
            try:
                canvas.setFillAlpha(0.1)  # 10% opacidad
                canvas.drawImage(
                    logo_path,
                    x=(width - 300) / 2,
                    y=(height - 300) / 2,
                    width=300,
                    height=300,
                    preserveAspectRatio=True
                )
                canvas.setFillAlpha(1)
            except Exception as e:
                self.logger.warning(f"Could not add watermark: {e}")
    
    def _create_folio_header(
        self,
        story: List,
        styles: Any,
        folio: Optional[int] = None,
        client_name: str = "",
        config: Dict[str, Any] = None
    ):
        """Create compact yellow rectangle header with client name, date and folio"""
        if folio is None:
            return
        
        if config is None:
            config = self._get_dynamic_config(0)
        
        fecha = datetime.now().strftime("%d/%m/%Y")
        
        style_client = ParagraphStyle(
            name='ClientName',
            parent=styles['Normal'],
            fontSize=config['font_size_folio'],
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            textColor=colors.black,
            spaceAfter=0
        )
        
        style_fecha = ParagraphStyle(
            name='FechaStyle',
            parent=styles['Normal'],
            fontSize=config['font_size_folio'] - 4,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            textColor=colors.black,
            spaceAfter=0
        )
        
        style_folio = ParagraphStyle(
            name='FolioStyle',
            parent=styles['Normal'],
            fontSize=config['font_size_folio_num'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.black,
            spaceAfter=0
        )
        
        # Primera fila: nombre (izq) | fecha (der)
        # Segunda fila: folio (centrado)
        folio_data = [
            [Paragraph(f"{client_name}", style_client), Paragraph(f"{fecha}", style_fecha)],
            [Paragraph(f"FOLIO N° {folio:06d}", style_folio)]
        ]
        
        # Tabla con dos columnas para la primera fila, una columna para la segunda
        folio_table = Table(folio_data, colWidths=[260, 260])
        
        folio_style = TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), COLOR_FOLIO_BG),
            ('BACKGROUND', (0, 1), (1, 1), COLOR_FOLIO_BG),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('ALIGN', (0, 1), (1, 1), 'CENTER'),
            ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (1, 1), 8),
            ('RIGHTPADDING', (0, 0), (1, 1), 8),
            ('TOPPADDING', (0, 0), (1, 1), config['padding_v'] + 2),
            ('BOTTOMPADDING', (0, 0), (1, 1), config['padding_v'] + 2),
            ('BORDER', (0, 0), (1, 1), 2, colors.black),
            ('SPAN', (0, 1), (1, 1)),  # Folio span two columns
        ])
        folio_table.setStyle(folio_style)
        story.append(folio_table)
        story.append(Spacer(1, config['spacer_header']))

    def _create_compact_header(
        self,
        story: List,
        styles: Any,
        folio: Optional[int] = None,
        config: Dict[str, Any] = None
    ):
        """Create compact PDF header with logo only (no invoice number)"""
        
        if config is None:
            config = self._get_dynamic_config(0)
        
        logo_path = self._get_logo_path()
        
        if logo_path:
            try:
                logo_img = Image(logo_path, width=180, height=50)
                
                company_info = f"""<font size={config['font_size_company']}>
                <b>{BUSINESS_CONFIG['subtitle']}</b><br/>
                {BUSINESS_CONFIG['address']}<br/>
                {BUSINESS_CONFIG['phone']}
                </font>"""
                
                style_company = ParagraphStyle(
                    name='CompanyInfo',
                    parent=styles['Normal'],
                    fontSize=config['font_size_company'],
                    alignment=TA_RIGHT,
                    leading=config['font_size_company'] + 1,
                    spaceAfter=0
                )
                company_paragraph = Paragraph(company_info, style_company)
                
                header_data = [[logo_img, company_paragraph]]
                header_table = Table(header_data, colWidths=[180, 340])
                
                header_style = TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ])
                header_table.setStyle(header_style)
                story.append(header_table)
                
            except Exception as e:
                self.logger.warning(f"Could not add logo: {e}")
                self._create_text_only_header(story, styles, folio, config)
        else:
            self._create_text_only_header(story, styles, folio, config)

    def _create_text_only_header(
        self,
        story: List,
        styles: Any,
        folio: Optional[int] = None,
        config: Dict[str, Any] = None
    ):
        """Fallback text-only header (no invoice number)"""
        if config is None:
            config = self._get_dynamic_config(0)
        
        style_title = ParagraphStyle(
            name='TitleText',
            parent=styles['Title'],
            fontSize=config['font_size_company'] + 2,
            textColor=COLOR_HEADER,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            spaceAfter=2
        )
        
        style_subtitle = ParagraphStyle(
            name='SubtitleText',
            parent=styles['Normal'],
            fontSize=config['font_size_company'],
            textColor=colors.black,
            alignment=TA_RIGHT,
            spaceAfter=2
        )
        
        story.append(Paragraph(f"<b>{BUSINESS_CONFIG['subtitle']}</b>", style_title))
        story.append(Paragraph(f"{BUSINESS_CONFIG['address']}", style_subtitle))
        story.append(Paragraph(f"{BUSINESS_CONFIG['phone']}", style_subtitle))

    def _create_items_table(self, items: List[List[str]], config: Dict[str, Any] = None) -> Table:
        """Create optimized product table for maximum density"""
        
        if config is None:
            config = self._get_dynamic_config(len(items))
        
        headers = [['PRODUCTO', 'CANT.', 'UNIDAD', 'P.UNIT.', 'TOTAL']]
        
        table_data = headers + items
        
        tabla = Table(
            table_data,
            colWidths=[220, 45, 60, 60, 75],
            repeatRows=1
        )
        
        style = TableStyle([
            # Header styling - más compacto
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_HEADER),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_TEXT_LIGHT),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), config['font_size_header']),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Data rows styling - compacto
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), config['font_size_data']),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # PRODUCTO - izquierda
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # CANT. - centro
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # UNIDAD - centro
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # P.UNIT. - derecha
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # TOTAL - derecha
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Padding mínimo
            ('LEFTPADDING', (0, 0), (-1, -1), config['padding_h']),
            ('RIGHTPADDING', (0, 0), (-1, -1), config['padding_h']),
            ('TOPPADDING', (0, 0), (-1, -1), config['padding_v']),
            ('BOTTOMPADDING', (0, 0), (-1, -1), config['padding_v']),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            
            # Alternating row colors - más sutil
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_GRAY_LIGHT]),
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
        
        style_total = ParagraphStyle(
            name='TotalCompact',
            parent=styles['Normal'],
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=COLOR_TOTAL,
            spaceAfter=0
        )
        
        story.append(Spacer(1, 2))
        story.append(Paragraph(f"<b>TOTAL: ${total:,.2f}</b>", style_total))

    def generate_simple_pdf(
        self,
        client_name: str,
        items: List[List[str]],
        total: float,
        folio: Optional[int] = None
    ) -> Optional[str]:
        """Generate compact PDF receipt optimized for 30 products"""
        operation_name = f"Generate simple PDF | {client_name}"

        with LogContext(self.logger, operation_name, logging.INFO):
            try:
                num_items = len(items)
                self.logger.info(
                    f"PDF request | {client_name} | "
                    f"Items: {num_items} | Total: ${total:.2f}"
                )

                # Obtener configuración dinámica basada en cantidad de productos
                config = self._get_dynamic_config(num_items)

                export_dir = self._get_export_directory()
                filename = self._generate_filename(client_name, folio)
                file_path = os.path.join(export_dir, filename)

                doc = SimpleDocTemplate(
                    file_path, 
                    pagesize=letter, 
                    topMargin=config['top_margin'],
                    bottomMargin=config['bottom_margin'],
                    leftMargin=35,
                    rightMargin=35,
                    onFirstPage=self._add_watermark,
                    onLaterPages=self._add_watermark
                )
                story = []
                styles = getSampleStyleSheet()

                self._create_folio_header(story, styles, folio, client_name, config)
                self._create_compact_header(story, styles, folio, config)
                story.append(Spacer(1, config['spacer_header']))

                tabla = self._create_items_table(items, config)
                story.append(tabla)

                self._create_compact_total_section(story, styles, total)
                
                story.append(Spacer(1, config['spacer_table']))
                
                style_reception = ParagraphStyle(
                    name='ReceptionSec',
                    parent=styles['Normal'],
                    fontName='Helvetica-Bold',
                    fontSize=6,
                    textColor=COLOR_HEADER,
                    spaceAfter=1
                )
                story.append(Paragraph("DATOS DE RECEPCIÓN", style_reception))
                
                reception_data = [
                    ['HORA: _____________', 'RECIBIÓ: ____________________', 'FIRMA: _____________'],
                ]
                
                reception_table = Table(reception_data, colWidths=[110, 210, 110])
                reception_style = TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 6),
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
                self.logger.info(f"✅ PDF generated | {file_path} | {file_size} bytes | Config: {num_items} items")
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
        """Generate compact PDF with sections optimized for 30 products"""
        operation_name = f"Generate sectioned PDF | {client_name}"

        with LogContext(self.logger, operation_name, logging.INFO):
            try:
                total_items = sum(len(s['items']) for s in sections.values())
                self.logger.info(
                    f"Sectioned PDF | {client_name} | "
                    f"Sections: {len(sections)} | Items: {total_items}"
                )

                # Obtener configuración dinámica basada en cantidad total de productos
                config = self._get_dynamic_config(total_items)

                export_dir = self._get_export_directory()
                filename = self._generate_filename(client_name, folio, with_sections=True)
                file_path = os.path.join(export_dir, filename)

                doc = SimpleDocTemplate(
                    file_path, 
                    pagesize=letter, 
                    topMargin=config['top_margin'],
                    bottomMargin=config['bottom_margin'],
                    leftMargin=35,
                    rightMargin=35,
                    onFirstPage=self._add_watermark,
                    onLaterPages=self._add_watermark
                )
                story = []
                styles = getSampleStyleSheet()

                self._create_folio_header(story, styles, folio, client_name, config)
                self._create_compact_header(story, styles, folio, config)
                story.append(Spacer(1, config['spacer_header']))

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
                        fontSize=config['font_size_header'],
                        textColor=COLOR_HEADER,
                        backColor=HexColor('#FFE6E6'),
                        borderPadding=2,
                        spaceAfter=config['spacer_table']
                    )
                    story.append(Paragraph(f"✦ {section_name.upper()} ✦", style_section))

                    items_section = section_data['items']
                    if items_section:
                        tabla = self._create_items_table(items_section, config)
                        story.append(tabla)
                        story.append(Spacer(1, config['spacer_table']))

                        subtotal = section_data['subtotal']
                        style_subtotal = ParagraphStyle(
                            name=f'Subtotal{idx}',
                            parent=styles['Normal'],
                            alignment=TA_RIGHT,
                            fontName='Helvetica-Bold',
                            fontSize=config['font_size_header'],
                            textColor=HexColor('#444444')
                        )
                        story.append(Paragraph(f"Subtotal {section_name}: ${subtotal:,.2f}", style_subtotal))
                        story.append(Spacer(1, config['spacer_table']))

                story.append(Spacer(1, config['spacer_table']))
                style_total = ParagraphStyle(
                    name='TotalGeneral',
                    parent=styles['Normal'],
                    alignment=TA_RIGHT,
                    textColor=COLOR_TOTAL,
                    fontName='Helvetica-Bold',
                    fontSize=10
                )
                story.append(Paragraph(f"TOTAL GENERAL: ${total:,.2f}", style_total))
                story.append(Spacer(1, config['spacer_table']))
                
                style_reception = ParagraphStyle(
                    name='ReceptionSec',
                    parent=styles['Normal'],
                    fontName='Helvetica-Bold',
                    fontSize=6,
                    textColor=COLOR_HEADER,
                    spaceAfter=1
                )
                story.append(Paragraph("DATOS DE RECEPCIÓN", style_reception))
                
                reception_data = [
                    ['HORA: _____________', 'RECIBIÓ: ____________________', 'FIRMA: _____________'],
                ]
                
                reception_table = Table(reception_data, colWidths=[110, 210, 110])
                reception_style = TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 6),
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
                self.logger.info(f"✅ Sectioned PDF | {file_path} | {file_size} bytes | Config: {total_items} items")
                return file_path

            except Exception as e:
                self.logger.error(f"Sectioned PDF failed | {client_name}", exc_info=True)
                raise PDFGenerationError(
                    client_name=client_name,
                    reason=f"Sectioned PDF error: {str(e)}"
                )