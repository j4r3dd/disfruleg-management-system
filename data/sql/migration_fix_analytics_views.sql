-- ============================================================================
-- MIGRATION: Fix Analytics Views to Use Actual Prices
-- ============================================================================
-- Date: 2025-12-09
-- Purpose: Update all analytics views to use actual precio_unitario_venta
--          from detalle_factura instead of recalculating from base prices.
--
-- Background: The old views used vista_detalle_factura_con_descuento which
--            recalculated prices using: precio_base * (1 - descuento%)
--            But the system now stores the actual final prices directly in
--            detalle_factura.precio_unitario_venta with discounts already applied.
--
-- IMPORTANT: Run this script on your database to fix the "Total Vendido" KPI
--           and all analytics calculations.
-- ============================================================================

USE disfruleg;

-- ============================================================================
-- STEP 1: Update vista_ganancias_por_cliente
-- ============================================================================
DROP VIEW IF EXISTS vista_ganancias_por_cliente;

CREATE VIEW vista_ganancias_por_cliente AS
SELECT
    c.id_cliente,
    c.nombre_cliente,
    g.clave_grupo,
    tc.nombre_tipo AS tipo_cliente,
    tc.descuento AS porcentaje_descuento,
    SUM(df.cantidad_factura * df.precio_unitario_venta) AS total_ventas,
    COUNT(DISTINCT f.id_factura) AS cantidad_facturas,
    MAX(f.fecha_factura) AS ultima_compra,
    SUM(CASE WHEN d.pagado = FALSE THEN d.monto_total - d.monto_pagado ELSE 0 END) AS saldo_pendiente
FROM cliente c
JOIN factura f ON c.id_cliente = f.id_cliente
JOIN detalle_factura df ON f.id_factura = df.id_factura
JOIN grupo g ON c.id_grupo = g.id_grupo
JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
LEFT JOIN deudas d ON f.id_factura = d.id_factura
GROUP BY c.id_cliente, c.nombre_cliente, g.clave_grupo, tc.nombre_tipo, tc.descuento;

-- ============================================================================
-- STEP 2: Update vista_ganancias_por_grupo
-- ============================================================================
DROP VIEW IF EXISTS vista_ganancias_por_grupo;

CREATE VIEW vista_ganancias_por_grupo AS
SELECT
    g.id_grupo,
    g.clave_grupo,
    tc.nombre_tipo AS tipo_cliente,
    COUNT(DISTINCT c.id_cliente) AS cantidad_clientes,
    SUM(df.cantidad_factura * df.precio_unitario_venta) AS total_ventas,
    COUNT(DISTINCT f.id_factura) AS cantidad_facturas,
    tc.descuento AS descuento_aplicado,
    ROUND(AVG(df.cantidad_factura * df.precio_unitario_venta), 2) AS ticket_promedio
FROM grupo g
LEFT JOIN cliente c ON g.id_grupo = c.id_grupo
LEFT JOIN factura f ON c.id_cliente = f.id_cliente
LEFT JOIN detalle_factura df ON f.id_factura = df.id_factura
LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
GROUP BY g.id_grupo, g.clave_grupo, tc.nombre_tipo, tc.descuento;

-- ============================================================================
-- STEP 3: Update vista_ganancias_por_producto_grupo
-- ============================================================================
DROP VIEW IF EXISTS vista_ganancias_por_producto_grupo;

CREATE VIEW vista_ganancias_por_producto_grupo AS
SELECT
    p.id_producto,
    p.nombre_producto,
    g.id_grupo,
    g.clave_grupo,
    tc.nombre_tipo AS tipo_cliente,
    SUM(df.cantidad_factura) AS cantidad_vendida,
    SUM(df.cantidad_factura * df.precio_unitario_venta) AS ingresos_totales,
    ROUND(SUM(df.cantidad_factura * df.precio_unitario_venta) / NULLIF(SUM(df.cantidad_factura), 0), 2) AS precio_promedio,
    COALESCE(SUM(c.cantidad_compra), 0) AS cantidad_comprada,
    COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) AS costos_totales,
    SUM(df.cantidad_factura * df.precio_unitario_venta) - COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) AS ganancia_total,
    CASE
        WHEN COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) = 0 THEN 0
        ELSE ROUND(((SUM(df.cantidad_factura * df.precio_unitario_venta) -
                    COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0)) /
                    COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0)) * 100, 2)
    END AS margen_ganancia_porcentaje
FROM producto p
LEFT JOIN detalle_factura df ON p.id_producto = df.id_producto
LEFT JOIN factura f ON df.id_factura = f.id_factura
LEFT JOIN cliente cl ON f.id_cliente = cl.id_cliente
LEFT JOIN grupo g ON cl.id_grupo = g.id_grupo
LEFT JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
LEFT JOIN compra c ON p.id_producto = c.id_producto
GROUP BY p.id_producto, p.nombre_producto, g.id_grupo, g.clave_grupo, tc.nombre_tipo;

-- ============================================================================
-- STEP 4: Update vista_ganancias_por_producto (with additional fields)
-- ============================================================================
DROP VIEW IF EXISTS vista_ganancias_por_producto;

CREATE VIEW vista_ganancias_por_producto AS
SELECT
    p.id_producto,
    p.nombre_producto,
    p.unidad_producto,
    SUM(df.cantidad_factura) AS cantidad_vendida,
    SUM(df.cantidad_factura * df.precio_unitario_venta) AS ingresos_totales,
    ROUND(SUM(df.cantidad_factura * df.precio_unitario_venta) / NULLIF(SUM(df.cantidad_factura), 0), 2) AS precio_venta_promedio,
    COALESCE(SUM(c.cantidad_compra), 0) AS cantidad_comprada,
    COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) AS costos_totales,
    ROUND(COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) / NULLIF(COALESCE(SUM(c.cantidad_compra), 0), 0), 2) AS costo_unitario_promedio,
    SUM(df.cantidad_factura * df.precio_unitario_venta) - COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) AS ganancia_total,
    ROUND((SUM(df.cantidad_factura * df.precio_unitario_venta) - COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0)) / NULLIF(SUM(df.cantidad_factura), 0), 2) AS ganancia_por_unidad,
    CASE
        WHEN COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0) = 0 THEN 0
        ELSE ROUND(((SUM(df.cantidad_factura * df.precio_unitario_venta) -
                    COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0)) /
                    COALESCE(SUM(c.cantidad_compra * c.precio_unitario_compra), 0)) * 100, 2)
    END AS margen_ganancia_porcentaje,
    p.stock,
    ROUND(p.stock / NULLIF(AVG(df.cantidad_factura), 0), 1) AS meses_inventario
FROM producto p
LEFT JOIN detalle_factura df ON p.id_producto = df.id_producto
LEFT JOIN compra c ON p.id_producto = c.id_producto
GROUP BY p.id_producto, p.nombre_producto, p.unidad_producto, p.stock;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Test the updated views
SELECT 'Testing vista_ganancias_por_cliente...' AS status;
SELECT COUNT(*) AS total_clients FROM vista_ganancias_por_cliente;

SELECT 'Testing vista_ganancias_por_grupo...' AS status;
SELECT COUNT(*) AS total_groups FROM vista_ganancias_por_grupo;

SELECT 'Testing vista_ganancias_por_producto...' AS status;
SELECT COUNT(*) AS total_products FROM vista_ganancias_por_producto WHERE cantidad_vendida > 0;

SELECT 'Testing vista_ganancias_por_producto_grupo...' AS status;
SELECT COUNT(*) AS total_product_groups FROM vista_ganancias_por_producto_grupo;

-- Check total sales calculation
SELECT 'Total Vendido (should match your actual sales)...' AS status;
SELECT SUM(cantidad_factura * precio_unitario_venta) AS total_vendido
FROM detalle_factura;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
SELECT '✓ Migration completed successfully!' AS status;
SELECT 'Analytics views now use actual prices from detalle_factura.precio_unitario_venta' AS info;
