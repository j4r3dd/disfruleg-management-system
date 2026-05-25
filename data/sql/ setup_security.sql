-- Tabla de dispositivos autorizados
CREATE TABLE IF NOT EXISTS dispositivos_autorizados (
    id_dispositivo INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(255),
    device_info TEXT,
    id_usuario INT,
    autorizado BOOLEAN DEFAULT FALSE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_autorizacion DATETIME NULL,
    ultimo_acceso DATETIME NULL,
    activo BOOLEAN DEFAULT TRUE,
    notas TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios_sistema(id_usuario) ON DELETE SET NULL
);

-- Tabla de log de accesos mejorada (si no existe ya)
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