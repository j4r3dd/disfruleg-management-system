-- ========================================
-- MEJORA DEL MÓDULO DE DEUDAS
-- Script SQL para soportar Overpayments y Abonos
-- VERSIÓN CORREGIDA PARA MYSQL 5.7+
-- ========================================

-- ========== TABLA: pago_registrado ==========
CREATE TABLE IF NOT EXISTS pago_registrado (
    id_pago INT PRIMARY KEY AUTO_INCREMENT,
    id_deuda INT NOT NULL,
    monto_pagado DECIMAL(15, 2) NOT NULL,
    fecha_pago DATE NOT NULL,
    metodo_pago VARCHAR(50) NOT NULL,
    referencia_pago VARCHAR(200),
    estado_pago ENUM('PROCESSED', 'REVERSED', 'ADJUSTED') DEFAULT 'PROCESSED',
    imagen_comprobante LONGBLOB,
    nombre_imagen VARCHAR(255),
    usuario_registro VARCHAR(100) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    notas TEXT,
    
    FOREIGN KEY (id_deuda) REFERENCES deuda(id_deuda),
    KEY idx_deuda (id_deuda),
    KEY idx_fecha (fecha_pago),
    KEY idx_estado (estado_pago),
    KEY idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========== TABLA: credito_cliente ==========
CREATE TABLE IF NOT EXISTS credito_cliente (
    id_credito INT PRIMARY KEY AUTO_INCREMENT,
    id_cliente INT NOT NULL,
    monto_total DECIMAL(15, 2) NOT NULL,
    monto_usado DECIMAL(15, 2) DEFAULT 0,
    fecha_creacion DATE NOT NULL,
    origen ENUM('OVERPAYMENT', 'ADJUSTMENT', 'REFUND') NOT NULL,
    id_deuda_origen INT,
    estado ENUM('ACTIVO', 'PARCIALMENTE_USADO', 'AGOTADO', 'EXPIRADO') DEFAULT 'ACTIVO',
    notas TEXT,
    
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    FOREIGN KEY (id_deuda_origen) REFERENCES deuda(id_deuda),
    KEY idx_cliente (id_cliente),
    KEY idx_estado (estado),
    KEY idx_fecha (fecha_creacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========== TABLA: aplicacion_credito ==========
CREATE TABLE IF NOT EXISTS aplicacion_credito (
    id_aplicacion INT PRIMARY KEY AUTO_INCREMENT,
    id_credito INT NOT NULL,
    id_deuda INT NOT NULL,
    monto_aplicado DECIMAL(15, 2) NOT NULL,
    fecha_aplicacion DATE NOT NULL,
    usuario VARCHAR(100) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    notas TEXT,
    
    FOREIGN KEY (id_credito) REFERENCES credito_cliente(id_credito),
    FOREIGN KEY (id_deuda) REFERENCES deuda(id_deuda),
    KEY idx_credito (id_credito),
    KEY idx_deuda (id_deuda),
    KEY idx_fecha (fecha_aplicacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========== TABLA: auditoria_pago ==========
CREATE TABLE IF NOT EXISTS auditoria_pago (
    id_auditoria INT PRIMARY KEY AUTO_INCREMENT,
    id_pago INT NOT NULL,
    accion VARCHAR(100) NOT NULL,
    usuario VARCHAR(100) NOT NULL,
    cambios JSON,
    descripcion TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_pago) REFERENCES pago_registrado(id_pago),
    KEY idx_pago (id_pago),
    KEY idx_accion (accion),
    KEY idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========== MODIFICACIONES A TABLA: deuda ==========
-- Verificar si columnas existen antes de agregar
ALTER TABLE deuda ADD COLUMN cantidad_pagos_registrados INT DEFAULT 0;
ALTER TABLE deuda ADD COLUMN fecha_ultimo_pago DATETIME;

-- ========== ÍNDICES ==========
CREATE INDEX idx_pagado ON deuda(pagado);
CREATE INDEX idx_cliente_pagado ON deuda(id_cliente, pagado);
CREATE INDEX idx_pago_deuda_fecha ON pago_registrado(id_deuda, fecha_pago);
CREATE INDEX idx_credito_cliente_estado ON credito_cliente(id_cliente, estado);
CREATE INDEX idx_auditoria_pago_accion ON auditoria_pago(id_pago, accion);

-- ========== VISTA: vista_pagos_por_deuda ==========
CREATE OR REPLACE VIEW vista_pagos_por_deuda AS
SELECT 
    d.id_deuda,
    d.id_cliente,
    d.monto AS monto_total,
    d.monto_pagado,
    COUNT(pr.id_pago) AS cantidad_pagos,
    SUM(CASE WHEN pr.estado_pago = 'PROCESSED' THEN pr.monto_pagado ELSE 0 END) 
        AS monto_pagado_verificado,
    MAX(pr.fecha_pago) AS ultimo_pago,
    (d.monto - d.monto_pagado) AS saldo_pendiente,
    CASE 
        WHEN d.pagado THEN 'PAGADA'
        WHEN d.monto_pagado > 0 THEN 'PARCIALMENTE_PAGADA'
        ELSE 'PENDIENTE'
    END AS estado_deuda
FROM deuda d
LEFT JOIN pago_registrado pr ON d.id_deuda = pr.id_deuda
GROUP BY d.id_deuda, d.id_cliente, d.monto, d.monto_pagado, d.pagado;

-- ========== VISTA: vista_creditos_cliente ==========
CREATE OR REPLACE VIEW vista_creditos_cliente AS
SELECT 
    cc.id_cliente,
    c.nombre_cliente,
    COUNT(cc.id_credito) AS cantidad_creditos,
    SUM(cc.monto_total) AS monto_total_creditos,
    SUM(cc.monto_usado) AS monto_total_usado,
    SUM(cc.monto_total - cc.monto_usado) AS monto_disponible,
    SUM(CASE WHEN cc.estado = 'ACTIVO' THEN 1 ELSE 0 END) AS creditos_activos,
    MAX(cc.fecha_creacion) AS ultimo_credito
FROM credito_cliente cc
JOIN cliente c ON cc.id_cliente = c.id_cliente
GROUP BY cc.id_cliente, c.nombre_cliente;

-- ========== VISTA: vista_deudas_con_pagos ==========
CREATE OR REPLACE VIEW vista_deudas_con_pagos AS
SELECT 
    d.id_deuda,
    d.id_cliente,
    d.id_factura,
    c.nombre_cliente,
    g.clave_grupo AS nombre_grupo,
    d.monto AS monto_total,
    d.monto_pagado,
    (d.monto - d.monto_pagado) AS saldo_pendiente,
    d.fecha_generada,
    d.pagado,
    d.fecha_pago,
    d.descripcion,
    COUNT(DISTINCT pr.id_pago) AS cantidad_pagos_registrados,
    MAX(pr.fecha_pago) AS fecha_ultimo_pago,
    COALESCE(SUM(cc.monto_total - cc.monto_usado), 0) AS saldo_credito_disponible,
    COUNT(DISTINCT cc.id_credito) AS cantidad_creditos
FROM deuda d
JOIN cliente c ON d.id_cliente = c.id_cliente
JOIN grupo g ON c.id_grupo = g.id_grupo
LEFT JOIN pago_registrado pr ON d.id_deuda = pr.id_deuda
    AND pr.estado_pago = 'PROCESSED'
LEFT JOIN credito_cliente cc ON d.id_cliente = cc.id_cliente
    AND cc.estado IN ('ACTIVO', 'PARCIALMENTE_USADO')
GROUP BY d.id_deuda, d.id_cliente, d.id_factura, c.nombre_cliente,
         g.clave_grupo, d.monto, d.monto_pagado, d.fecha_generada,
         d.pagado, d.fecha_pago, d.descripcion;

-- ========== PROCEDIMIENTO: calcular_monto_pagado_verificado ==========
DROP PROCEDURE IF EXISTS calcular_monto_pagado_verificado;
DELIMITER $$

CREATE PROCEDURE calcular_monto_pagado_verificado(
    IN p_id_deuda INT,
    OUT p_monto_verificado DECIMAL(15, 2)
)
READS SQL DATA
BEGIN
    SELECT COALESCE(SUM(monto_pagado), 0)
    INTO p_monto_verificado
    FROM pago_registrado
    WHERE id_deuda = p_id_deuda 
    AND estado_pago = 'PROCESSED';
END $$

DELIMITER ;

-- ========== PROCEDIMIENTO: crear_abono_por_overpayment ==========
DROP PROCEDURE IF EXISTS crear_abono_por_overpayment;
DELIMITER $$

CREATE PROCEDURE crear_abono_por_overpayment(
    IN p_id_deuda INT,
    IN p_monto_exceso DECIMAL(15, 2),
    IN p_usuario VARCHAR(100)
)
MODIFIES SQL DATA
BEGIN
    DECLARE v_id_cliente INT;
    
    SELECT id_cliente INTO v_id_cliente FROM deuda WHERE id_deuda = p_id_deuda;
    
    INSERT INTO credito_cliente (
        id_cliente,
        monto_total,
        monto_usado,
        fecha_creacion,
        origen,
        id_deuda_origen,
        estado,
        notas
    ) VALUES (
        v_id_cliente,
        p_monto_exceso,
        0,
        CURDATE(),
        'OVERPAYMENT',
        p_id_deuda,
        'ACTIVO',
        CONCAT('Abono por sobrepago en deuda ', p_id_deuda)
    );
END $$

DELIMITER ;

-- ========== PROCEDIMIENTO: registrar_pago_con_overpayment ==========
DROP PROCEDURE IF EXISTS registrar_pago_con_overpayment;
DELIMITER $$

CREATE PROCEDURE registrar_pago_con_overpayment(
    IN p_id_deuda INT,
    IN p_monto DECIMAL(15, 2),
    IN p_metodo_pago VARCHAR(50),
    IN p_usuario VARCHAR(100),
    IN p_referencia VARCHAR(200),
    OUT p_id_pago INT,
    OUT p_id_credito INT,
    OUT p_monto_exceso DECIMAL(15, 2)
)
MODIFIES SQL DATA
BEGIN
    DECLARE v_id_cliente INT;
    DECLARE v_monto_total DECIMAL(15, 2);
    DECLARE v_nuevo_monto_pagado DECIMAL(15, 2);
    DECLARE v_saldo_pendiente DECIMAL(15, 2);
    
    SELECT id_cliente, monto, (monto - monto_pagado) INTO v_id_cliente, v_monto_total, v_saldo_pendiente
    FROM deuda
    WHERE id_deuda = p_id_deuda;
    
    SET v_nuevo_monto_pagado = (
        SELECT monto_pagado + p_monto FROM deuda WHERE id_deuda = p_id_deuda
    );
    
    SET p_monto_exceso = GREATEST(0, v_nuevo_monto_pagado - v_monto_total);
    
    INSERT INTO pago_registrado (
        id_deuda,
        monto_pagado,
        fecha_pago,
        metodo_pago,
        referencia_pago,
        usuario_registro
    ) VALUES (
        p_id_deuda,
        p_monto,
        CURDATE(),
        p_metodo_pago,
        p_referencia,
        p_usuario
    );
    
    SET p_id_pago = LAST_INSERT_ID();
    
    IF p_monto_exceso > 0 THEN
        INSERT INTO credito_cliente (
            id_cliente,
            monto_total,
            fecha_creacion,
            origen,
            id_deuda_origen
        ) VALUES (
            v_id_cliente,
            p_monto_exceso,
            CURDATE(),
            'OVERPAYMENT',
            p_id_deuda
        );
        
        SET p_id_credito = LAST_INSERT_ID();
    ELSE
        SET p_id_credito = NULL;
    END IF;
    
    INSERT INTO auditoria_pago (
        id_pago,
        accion,
        usuario,
        cambios,
        descripcion
    ) VALUES (
        p_id_pago,
        IF(p_monto_exceso > 0, 'OVERPAYMENT_PROCESSED', 'PAYMENT_PROCESSED'),
        p_usuario,
        JSON_OBJECT('monto_exceso', p_monto_exceso, 'id_credito', COALESCE(p_id_credito, 0)),
        CONCAT('Pago de $', p_monto, ' registrado por ', p_usuario)
    );
END $$

DELIMITER ;

-- ========== CONFIRMACIÓN ==========
SELECT 'Mejora del módulo de deudas instalada correctamente' AS mensaje;