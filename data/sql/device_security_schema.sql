-- ============================================================
-- DISFRULEG - Esquema de seguridad por dispositivo
--
-- Control de acceso: cada equipo que abre la app se registra con
-- un device_id y queda PENDING hasta que un administrador lo
-- autoriza desde el módulo de dispositivos.
--
-- Reemplaza a ` setup_security.sql`, que quedó desactualizado
-- respecto a las columnas que usa el código (estado,
-- fecha_eliminacion, razon_bloqueo).
--
-- Consumido por:
--   src/security/device_manager.py
--   src/services/device_recycle_service.py
--   src/modules/device_admin_module.py
--   src/modules/devices/device_admin.py
-- ============================================================
USE disfruleg;

-- Dispositivos registrados y su estado de autorización
CREATE TABLE IF NOT EXISTS dispositivos_autorizados (
    id_dispositivo INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL UNIQUE,
    device_name VARCHAR(255),
    device_info TEXT,
    id_usuario INT NULL,
    autorizado BOOLEAN NOT NULL DEFAULT FALSE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    estado ENUM('PENDING', 'AUTORIZADO', 'BLOQUEADO', 'EXPIRADO', 'ELIMINADO')
        NOT NULL DEFAULT 'PENDING',
    razon_bloqueo VARCHAR(255) NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_autorizacion DATETIME NULL,
    ultimo_acceso DATETIME NULL,
    fecha_eliminacion DATETIME NULL,   -- borrado lógico; NULL = vigente
    notas TEXT,
    INDEX idx_device (device_id),
    INDEX idx_estado (estado),
    INDEX idx_eliminacion (fecha_eliminacion),
    FOREIGN KEY (id_usuario) REFERENCES usuarios_sistema(id_usuario) ON DELETE SET NULL
);

-- Bitácora de accesos por dispositivo
CREATE TABLE IF NOT EXISTS log_accesos_dispositivos (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(255),
    username VARCHAR(50),
    modulo VARCHAR(100),
    accion VARCHAR(100),
    exito BOOLEAN,
    ip_address VARCHAR(45),
    detalle TEXT,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_device (device_id),
    INDEX idx_username (username),
    INDEX idx_fecha (fecha_hora)
);

-- Historial de cambios de estado (auditoría del reciclaje de dispositivos)
CREATE TABLE IF NOT EXISTS dispositivos_eventos (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    id_dispositivo INT NULL,
    device_id VARCHAR(255),
    estado_anterior VARCHAR(20) NULL,
    estado_nuevo VARCHAR(20) NOT NULL,
    razon VARCHAR(255),
    usuario_admin VARCHAR(100),
    fecha_evento DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dispositivo (id_dispositivo),
    INDEX idx_device (device_id),
    INDEX idx_fecha (fecha_evento)
);
