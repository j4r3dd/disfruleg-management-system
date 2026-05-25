# -*- coding: utf-8 -*-
"""
Importacion Module - Clean Architecture
Sistema BodegaDisfruleg

ARCHITECTURE:
    UI Layer (Controllers/Views)
        ↓ depends on
    Business Layer (Services)
        ↓ depends on
    Data Layer (Repositories)
        ↓ depends on
    Domain Layer (Models/Entities)

FEATURES:
- Import quotations from PDF files
- Automatic price updates across all groups
- Support for products without prices
- Integrity validation before import
- Report generation

USAGE:
    from modules.importacion import abrir_importador_cotizaciones

    # Open from dashboard
    abrir_importador_cotizaciones(parent_window, db_connection, user_info)
"""

# Public API
from .ui import CotizacionImporter, abrir_importador_cotizaciones

__all__ = [
    'CotizacionImporter',
    'abrir_importador_cotizaciones',
]

__version__ = '2.0.0'
__author__ = 'BodegaDisfruleg'
