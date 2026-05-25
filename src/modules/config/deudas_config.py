# -*- coding: utf-8 -*-
"""
Configuración del Módulo de Deudas
Archivo: config/deudas_config.py

Copia este archivo a: tu_proyecto/config/deudas_config.py
"""

import os
from pathlib import Path

# ==================== PAGOS MÚLTIPLES ====================

# Máximo de deudas por pago múltiple
MAX_PAGOS_POR_BATCH = 20

# Máximo de deudas por cliente permitidas
MAX_DEUDAS_POR_CLIENTE = 100

# Requerir aprobación gerencial para pagos > X cantidad
REQUIERE_APROBACION_GERENCIAL = False
MONTO_APROBACION_GERENCIAL = 5000

# ==================== ACCESO A PDFs ====================

# Ruta donde se almacenan los PDFs
# Usa ~ para home directory
PDF_STORAGE_PATH = os.path.expanduser("~/.disfruleg/pdfs/facturas")

# Habilitar caché de PDFs
PDF_CACHE_ENABLED = True

# Días de expiración de caché
PDF_CACHE_EXPIRY_DAYS = 30

# Permitir regeneración de PDFs si faltan
ALLOW_PDF_REGENERATION = False

# Permitir abrir PDFs en visor externo del sistema
ALLOW_EXTERNAL_VIEWER = True

# ==================== AUDITORÍA ====================

# Registrar descargas de PDFs
AUDIT_PDF_DOWNLOADS = True

# Registrar pagos múltiples
AUDIT_BATCH_PAYMENTS = True

# Nivel de detalle de logs
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# ==================== VALIDACIONES ====================

# Validar montos de pago (prevent accidental overpayment)
VALIDATE_PAYMENT_AMOUNTS = True

# Permitir pagos parciales
ALLOW_PARTIAL_PAYMENTS = True

# Permitir pagos totales
ALLOW_FULL_PAYMENTS = True

# ==================== UI ====================

# Tamaño de ventana de pagos múltiples
BATCH_PAYMENT_WINDOW_WIDTH = 700
BATCH_PAYMENT_WINDOW_HEIGHT = 900

# Tamaño de ventana de búsqueda
INVOICE_SEARCH_WINDOW_WIDTH = 900
INVOICE_SEARCH_WINDOW_HEIGHT = 700

# Resultado máximo por búsqueda
INVOICE_SEARCH_LIMIT = 100

# ==================== FUNCIONALIDADES OPCIONALES ====================

# Permitir comentarios en pagos
ALLOW_PAYMENT_COMMENTS = True

# Permitir cargar comprobante de pago
ALLOW_PAYMENT_RECEIPT = True

# Tipos de archivo permitidos para comprobantes
ALLOWED_RECEIPT_TYPES = ['image/jpeg', 'image/png', 'application/pdf']

# Tamaño máximo de comprobante (MB)
MAX_RECEIPT_SIZE_MB = 10

# ==================== INTEGRACIÓN ====================

# Integración con módulo de recibos (si está disponible)
RECEIPTS_MODULE_ENABLED = True

# Integración con módulo de clientes
CLIENTS_MODULE_ENABLED = True

# ==================== REPORTES ====================

# Incluir en reportes de deudas
INCLUDE_IN_DEBT_REPORTS = True

# Incluir en reportes de pagos
INCLUDE_IN_PAYMENT_REPORTS = True

# ==================== NOTIFICACIONES ====================

# Notificar cuando se registra pago múltiple
NOTIFY_ON_BATCH_PAYMENT = True

# Notificar al cliente
NOTIFY_CLIENT_ON_PAYMENT = False

# Método de notificación (email, sms, etc)
NOTIFICATION_METHOD = "email"  # email, sms, none

# ==================== SEGURIDAD ====================

# Requerir confirmación de usuario antes de pago múltiple
REQUIRE_CONFIRMATION = True

# Requerir contraseña para pagos > X cantidad
REQUIRE_PASSWORD_FOR_LARGE_PAYMENTS = False
PASSWORD_THRESHOLD = 10000

# ==================== UTILIDADES ====================

def get_pdf_storage_path() -> Path:
    """Obtener ruta de almacenamiento de PDFs con validaciones"""
    path = Path(os.path.expanduser(PDF_STORAGE_PATH))
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_config() -> bool:
    """Validar que la configuración sea correcta"""
    
    # Validar rangos
    if MAX_PAGOS_POR_BATCH < 1 or MAX_PAGOS_POR_BATCH > 50:
        print("⚠️  MAX_PAGOS_POR_BATCH debe estar entre 1 y 50")
        return False
    
    if PDF_CACHE_EXPIRY_DAYS < 1:
        print("⚠️  PDF_CACHE_EXPIRY_DAYS debe ser >= 1")
        return False
    
    # Validar que PDF_STORAGE_PATH sea escribible
    try:
        get_pdf_storage_path()
    except Exception as e:
        print(f"⚠️  No se puede acceder a PDF_STORAGE_PATH: {e}")
        return False
    
    return True


# Validar al importar
if __name__ == "__main__":
    if validate_config():
        print("✅ Configuración válida")
    else:
        print("❌ Errores en configuración")
