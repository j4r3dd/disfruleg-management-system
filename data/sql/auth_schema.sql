-- ============================================================
-- DISFRULEG - Ajustes al esquema de autenticación
--
-- Las tablas usuarios_sistema y log_accesos se crean en
-- disfruleg_schema.sql. Este script agrega las columnas y valores
-- que el código de src/auth/auth_manager.py usa pero que no
-- estaban en la definición original.
--
-- Es idempotente: se puede ejecutar varias veces sin error.
-- Ejecutar DESPUÉS de disfruleg_schema.sql.
-- ============================================================
USE disfruleg;

-- MySQL no soporta ADD COLUMN IF NOT EXISTS, así que se verifica
-- contra information_schema antes de alterar la tabla.
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

-- auth_manager.update_user_avatar_color() / update_user_avatar_imagen()
CALL _add_column_if_missing('usuarios_sistema', 'avatar_color', 'VARCHAR(20) NULL');
CALL _add_column_if_missing('usuarios_sistema', 'avatar_imagen', 'LONGBLOB NULL');

DROP PROCEDURE _add_column_if_missing;

-- auth_manager.create_user() acepta el rol 'supervisor', ausente en el ENUM original
ALTER TABLE usuarios_sistema
    MODIFY COLUMN rol ENUM('admin', 'supervisor', 'usuario') NOT NULL DEFAULT 'usuario';
