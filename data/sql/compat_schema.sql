-- ============================================================
-- DISFRULEG - Compatibilidad entre el esquema base y los módulos
--
-- Los módulos de clientes y deudas esperan estructuras que no
-- estaban en disfruleg_schema.sql. Este script las agrega.
--
-- Ejecutar DESPUÉS de disfruleg_schema.sql.
-- ============================================================
USE disfruleg;

-- ------------------------------------------------------------
-- 1. Campos fiscales y administrativos en `cliente`
--
-- src/modules/clients/data/mysql_repositories.py consulta e inserta
-- estas columnas (facturación CFDI), pero la tabla original solo
-- tenía nombre, teléfono, correo y grupo.
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS _add_column_if_missing;
DELIMITER $$
CREATE PROCEDURE _add_column_if_missing(
    IN p_table VARCHAR(64),
    IN p_column VARCHAR(64),
    IN p_definition VARCHAR(255)
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = p_table
          AND COLUMN_NAME = p_column
    ) THEN
        SET @ddl = CONCAT('ALTER TABLE `', p_table, '` ADD COLUMN `', p_column, '` ', p_definition);
        PREPARE stmt FROM @ddl;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

CALL _add_column_if_missing('cliente', 'rfc', 'VARCHAR(13) NULL');
CALL _add_column_if_missing('cliente', 'razon_social', 'VARCHAR(255) NULL');
CALL _add_column_if_missing('cliente', 'regimen_fiscal', 'VARCHAR(100) NULL');
CALL _add_column_if_missing('cliente', 'codigo_postal', 'VARCHAR(10) NULL');
CALL _add_column_if_missing('cliente', 'direccion_fiscal', 'TEXT NULL');
CALL _add_column_if_missing('cliente', 'notas', 'TEXT NULL');
CALL _add_column_if_missing('cliente', 'activo', 'BOOLEAN NOT NULL DEFAULT TRUE');

DROP PROCEDURE _add_column_if_missing;

-- ------------------------------------------------------------
-- 2. Vista `deudas`
--
-- El módulo de deudas y el de analytics consultan `deudas` (plural)
-- esperando los datos del cliente y su grupo ya resueltos, y el monto
-- bajo el nombre `monto_total`. La tabla base `deuda` (singular) solo
-- guarda los ids y la columna se llama `monto`.
--
-- Se expone como vista en lugar de renombrar la tabla para no tocar
-- las claves foráneas ni el resto de los módulos que sí usan `deuda`.
--
-- Nota: es una vista de solo lectura para efectos prácticos. Las
-- escrituras de los módulos van contra la tabla `deuda`.
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW deudas AS
SELECT
    d.id_deuda,
    d.id_cliente,
    d.id_factura,
    c.nombre_cliente,
    g.clave_grupo AS nombre_grupo,
    d.monto,
    d.monto AS monto_total,
    d.monto_pagado,
    (d.monto - d.monto_pagado) AS saldo_pendiente,
    d.fecha_generada,
    d.pagado,
    d.fecha_pago,
    d.descripcion,
    d.metodo_pago,
    d.referencia_pago
FROM deuda d
JOIN cliente c ON d.id_cliente = c.id_cliente
JOIN grupo g ON c.id_grupo = g.id_grupo;
