-- ============================================================================
-- DATABASE CLEANUP SCRIPT FOR DISFRULEG
-- ============================================================================
-- PURPOSE: Reset all transactional data while preserving structure and users
-- WARNING: This will DELETE all business data (products, clients, invoices, etc.)
-- RECOMMENDATION: Create a backup before running this script!
-- ============================================================================

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- STEP 1: Clean Transactional Tables (in dependency order)
-- ============================================================================

-- Clean invoice-related data (must be first due to foreign keys)
TRUNCATE TABLE detalle_factura;
TRUNCATE TABLE seccion_factura;
TRUNCATE TABLE factura_metadata;
TRUNCATE TABLE deuda;
TRUNCATE TABLE factura;

-- Clean order data
TRUNCATE TABLE ordenes_guardadas;

-- Clean product-related data
TRUNCATE TABLE precio_por_grupo;
TRUNCATE TABLE compra;
TRUNCATE TABLE producto_locks;
TRUNCATE TABLE producto;

-- Clean client-related data
TRUNCATE TABLE cliente;
TRUNCATE TABLE grupo;
TRUNCATE TABLE tipo_cliente;

-- ============================================================================
-- STEP 2: Reset Sequence Generators
-- ============================================================================

-- Reset folio sequence to start from 1
UPDATE folio_sequence SET next_val = 1 WHERE id = 1;

-- Reset invoice sequence to start from 1
UPDATE factura_sequence SET next_val = 1 WHERE id = 1;

-- ============================================================================
-- STEP 3: Clean System Logs (Optional - keeps audit trail clean)
-- ============================================================================

-- Clean application logs (comment out if you want to keep logs)
TRUNCATE TABLE logs_sistema;
TRUNCATE TABLE eventos_sistema;

-- Clean access logs (comment out if you want to keep security audit trail)
TRUNCATE TABLE log_accesos;

-- ============================================================================
-- STEP 4: Reset User Data (OPTIONAL - Uncomment to reset users)
-- ============================================================================

-- WARNING: Uncomment the following lines if you want to reset all users
-- This will require creating new user accounts after cleanup

-- TRUNCATE TABLE usuarios_sistema;

-- If you want to keep ONE admin user, you can do this instead:
-- DELETE FROM usuarios_sistema WHERE rol != 'admin' OR username != 'admin';
-- UPDATE usuarios_sistema SET
--     intentos_fallidos = 0,
--     bloqueado_hasta = NULL,
--     ultimo_acceso = NULL
-- WHERE username = 'admin';

-- ============================================================================
-- STEP 5: Re-enable Foreign Key Checks
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- VERIFICATION QUERIES (Run these to confirm cleanup)
-- ============================================================================

-- Check record counts (should all be 0 or minimal)
SELECT 'producto' as tabla, COUNT(*) as registros FROM producto
UNION ALL
SELECT 'cliente', COUNT(*) FROM cliente
UNION ALL
SELECT 'factura', COUNT(*) FROM factura
UNION ALL
SELECT 'detalle_factura', COUNT(*) FROM detalle_factura
UNION ALL
SELECT 'deuda', COUNT(*) FROM deuda
UNION ALL
SELECT 'ordenes_guardadas', COUNT(*) FROM ordenes_guardadas
UNION ALL
SELECT 'grupo', COUNT(*) FROM grupo
UNION ALL
SELECT 'tipo_cliente', COUNT(*) FROM tipo_cliente
UNION ALL
SELECT 'precio_por_grupo', COUNT(*) FROM precio_por_grupo
UNION ALL
SELECT 'compra', COUNT(*) FROM compra
UNION ALL
SELECT 'usuarios_sistema', COUNT(*) FROM usuarios_sistema;

-- Check sequence values
SELECT 'folio_sequence' as secuencia, next_val FROM folio_sequence
UNION ALL
SELECT 'factura_sequence', next_val FROM factura_sequence;

-- ============================================================================
-- DONE! Database is now clean and ready for production use
-- ============================================================================
