-- Migración: Agregar campo para imagen de comprobante de pago
-- Fecha: 2025-10-03

ALTER TABLE deuda
ADD COLUMN imagen_comprobante MEDIUMBLOB NULL COMMENT 'Imagen del comprobante de pago en formato binario',
ADD COLUMN nombre_imagen VARCHAR(255) NULL COMMENT 'Nombre original del archivo de imagen';
