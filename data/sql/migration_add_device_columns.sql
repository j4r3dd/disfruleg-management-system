-- ============================================================================
-- Migration Script: Add Missing Columns to dispositivos_autorizados
-- Date: 2025-11-25
-- Purpose: Fix device authorization issues by adding estado, fecha_eliminacion, razon_bloqueo
-- ============================================================================

USE disfruleg;

-- Verificar que estamos en la base de datos correcta
SELECT DATABASE() as current_database;

-- ============================================================================
-- STEP 1: Add the 'estado' column
-- ============================================================================
ALTER TABLE dispositivos_autorizados
ADD COLUMN IF NOT EXISTS estado ENUM('PENDING', 'AUTORIZADO', 'BLOQUEADO', 'ELIMINADO')
DEFAULT 'PENDING'
AFTER activo;

-- ============================================================================
-- STEP 2: Add the 'razon_bloqueo' column
-- ============================================================================
ALTER TABLE dispositivos_autorizados
ADD COLUMN IF NOT EXISTS razon_bloqueo TEXT
AFTER estado;

-- ============================================================================
-- STEP 3: Add the 'fecha_eliminacion' column
-- ============================================================================
ALTER TABLE dispositivos_autorizados
ADD COLUMN IF NOT EXISTS fecha_eliminacion DATETIME NULL
AFTER razon_bloqueo;

-- ============================================================================
-- STEP 4: Update existing records to have proper estado values
-- ============================================================================
-- Set estado based on current autorizado and activo values
UPDATE dispositivos_autorizados
SET estado = CASE
    WHEN autorizado = TRUE AND activo = TRUE THEN 'AUTORIZADO'
    WHEN autorizado = FALSE AND activo = TRUE THEN 'PENDING'
    WHEN activo = FALSE THEN 'BLOQUEADO'
    ELSE 'PENDING'
END
WHERE estado IS NULL OR estado = 'PENDING';

-- ============================================================================
-- STEP 5: Add index for better query performance
-- ============================================================================
-- Add index on estado for faster lookups
ALTER TABLE dispositivos_autorizados
ADD INDEX IF NOT EXISTS idx_estado (estado);

-- Add index on fecha_eliminacion for soft-delete queries
ALTER TABLE dispositivos_autorizados
ADD INDEX IF NOT EXISTS idx_fecha_eliminacion (fecha_eliminacion);

-- ============================================================================
-- VERIFICATION: Show the updated table structure
-- ============================================================================
DESCRIBE dispositivos_autorizados;

-- ============================================================================
-- VERIFICATION: Show count of devices by estado
-- ============================================================================
SELECT
    estado,
    COUNT(*) as cantidad,
    COUNT(CASE WHEN autorizado = TRUE THEN 1 END) as autorizados,
    COUNT(CASE WHEN activo = TRUE THEN 1 END) as activos
FROM dispositivos_autorizados
WHERE fecha_eliminacion IS NULL
GROUP BY estado;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
SELECT '✓ Migration completed successfully!' as status;
SELECT 'dispositivos_autorizados table updated with estado, razon_bloqueo, fecha_eliminacion columns' as message;
