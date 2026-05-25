CREATE TABLE IF NOT EXISTS producto_locks (
    id_producto INT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    fecha_bloqueo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS logs_sistema (
    id_log INT PRIMARY KEY AUTO_INCREMENT,
    usuario VARCHAR(50) NOT NULL,
    modulo VARCHAR(100) NOT NULL,
    accion VARCHAR(100) NOT NULL,
    detalles TEXT,
    nivel_log ENUM('INFO', 'WARNING', 'ERROR', 'SUCCESS') DEFAULT 'INFO',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_usuario (usuario),
    INDEX idx_modulo (modulo),
    INDEX idx_fecha (fecha_registro)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS eventos_sistema (
    id_evento INT PRIMARY KEY AUTO_INCREMENT,
    tipo_evento VARCHAR(100) NOT NULL,
    datos_evento JSON,
    usuario VARCHAR(50),
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tipo (tipo_evento),
    INDEX idx_fecha (fecha_evento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;