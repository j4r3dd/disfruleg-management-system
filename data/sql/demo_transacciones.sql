-- ============================================================
-- DISFRULEG - Datos transaccionales de demostración
--
-- inserts_updated.sql carga el catálogo (clientes, productos,
-- precios) pero no genera movimiento. Sin facturas, los módulos de
-- deudas, analytics y recibos se ven vacíos.
--
-- Este script genera facturas de los últimos meses con sus
-- detalles y deudas asociadas, usando los precios reales de
-- precio_por_grupo para que los totales sean coherentes.
--
-- Solo para desarrollo y demos. No ejecutar en producción.
-- ============================================================
USE disfruleg;

-- Idempotencia: limpiar cualquier corrida previa de este script.
-- El orden respeta las llaves foráneas.
DELETE d FROM deuda d
    JOIN factura f ON d.id_factura = f.id_factura
    WHERE f.folio_numero BETWEEN 9000 AND 9099;
DELETE df FROM detalle_factura df
    JOIN factura f ON df.id_factura = f.id_factura
    WHERE f.folio_numero BETWEEN 9000 AND 9099;
DELETE FROM factura WHERE folio_numero BETWEEN 9000 AND 9099;

-- ------------------------------------------------------------
-- Facturas: 12 repartidas entre clientes y fechas recientes
-- ------------------------------------------------------------
INSERT INTO factura (fecha_factura, id_cliente, folio_numero)
SELECT
    DATE_SUB(CURDATE(), INTERVAL seq.dias DAY),
    c.id_cliente,
    9000 + seq.n
FROM (
    SELECT 1 AS n, 3 AS dias UNION ALL SELECT 2, 8 UNION ALL SELECT 3, 15 UNION ALL
    SELECT 4, 22 UNION ALL SELECT 5, 30 UNION ALL SELECT 6, 38 UNION ALL
    SELECT 7, 45 UNION ALL SELECT 8, 52 UNION ALL SELECT 9, 60 UNION ALL
    SELECT 10, 68 UNION ALL SELECT 11, 75 UNION ALL SELECT 12, 90
) seq
JOIN (
    SELECT id_cliente, ROW_NUMBER() OVER (ORDER BY id_cliente) AS rn
    FROM cliente
) c ON c.rn = ((seq.n - 1) % 12) + 1;

-- ------------------------------------------------------------
-- Detalle: 3 productos por factura, al precio del grupo del cliente
-- ------------------------------------------------------------
INSERT INTO detalle_factura (id_factura, id_producto, cantidad_factura, precio_unitario_venta)
SELECT
    f.id_factura,
    pg.id_producto,
    ROUND(1 + (f.folio_numero + pg.id_producto) % 8, 2) AS cantidad,
    pg.precio_base
FROM factura f
JOIN cliente c ON f.id_cliente = c.id_cliente
JOIN precio_por_grupo pg ON pg.id_grupo = c.id_grupo
JOIN (
    SELECT id_producto, ROW_NUMBER() OVER (ORDER BY id_producto) AS rn
    FROM producto
) p ON p.id_producto = pg.id_producto
WHERE f.folio_numero BETWEEN 9000 AND 9099
  AND p.rn BETWEEN ((f.folio_numero % 5) + 1) AND ((f.folio_numero % 5) + 3);

-- ------------------------------------------------------------
-- Deudas
--
-- No se insertan aquí: el trigger after_detalle_insert_update_deuda
-- ya crea una deuda por factura al registrar cada detalle. Lo que
-- falta es aplicarles el descuento del tipo de cliente y darles
-- estados variados (pagada, parcial, pendiente) para que el módulo
-- de deudas muestre los tres casos.
-- ------------------------------------------------------------
UPDATE deuda d
JOIN factura f ON d.id_factura = f.id_factura
JOIN cliente c ON f.id_cliente = c.id_cliente
JOIN grupo g ON c.id_grupo = g.id_grupo
JOIN tipo_cliente tc ON g.id_tipo_cliente = tc.id_tipo_cliente
SET
    d.monto = ROUND(d.monto * (1 - tc.descuento / 100), 2),
    d.fecha_generada = f.fecha_factura,
    d.descripcion = CONCAT('[DEMO] Venta folio ', f.folio_numero)
WHERE f.folio_numero BETWEEN 9000 AND 9099;

-- Estados: 1 de cada 3 pagada, 1 de cada 3 con abono parcial, el resto pendiente.
-- Se hace en un paso aparte para calcular los pagos sobre el monto ya descontado.
UPDATE deuda d
JOIN factura f ON d.id_factura = f.id_factura
SET
    d.monto_pagado = CASE (f.folio_numero % 3)
        WHEN 0 THEN d.monto                      -- pagada completa
        WHEN 1 THEN ROUND(d.monto * 0.40, 2)     -- abono parcial
        ELSE 0.00                                -- pendiente
    END,
    d.pagado = CASE WHEN (f.folio_numero % 3) = 0 THEN TRUE ELSE FALSE END,
    d.fecha_pago = CASE WHEN (f.folio_numero % 3) = 0
                        THEN DATE_ADD(f.fecha_factura, INTERVAL 5 DAY) END,
    d.metodo_pago = CASE (f.folio_numero % 3)
        WHEN 0 THEN 'Transferencia'
        WHEN 1 THEN 'Efectivo'
        ELSE NULL
    END
WHERE f.folio_numero BETWEEN 9000 AND 9099;
