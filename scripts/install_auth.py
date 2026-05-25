#!/usr/bin/env python3
"""
DISFRULEG authentication installer.

Creates the `usuarios_sistema` and `log_accesos` tables (if missing) and
seeds an initial admin user. All credentials are requested interactively;
no passwords are hardcoded in this repository.
"""

import subprocess
import sys
from datetime import datetime
from getpass import getpass

import bcrypt
import mysql.connector


REQUIRED_PACKAGES = ["bcrypt", "Pillow"]


def install_dependencies() -> bool:
    print("Installing Python dependencies...")
    for pkg in REQUIRED_PACKAGES:
        try:
            print(f"  installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        except subprocess.CalledProcessError:
            print(f"  failed to install {pkg}")
            return False
    print("Dependencies installed.")
    return True


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def ensure_schema(cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios_sistema (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            nombre_completo VARCHAR(100) NOT NULL,
            rol ENUM('admin', 'usuario') DEFAULT 'usuario',
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acceso TIMESTAMP NULL,
            intentos_fallidos INT DEFAULT 0,
            bloqueado_hasta TIMESTAMP NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS log_accesos (
            id_log INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NULL,
            username_intento VARCHAR(50),
            ip_address VARCHAR(45) DEFAULT 'localhost',
            exito BOOLEAN,
            fecha_intento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            detalle VARCHAR(255),
            FOREIGN KEY (id_usuario) REFERENCES usuarios_sistema(id_usuario) ON DELETE SET NULL
        )
        """
    )


def upsert_admin(cursor, username: str, full_name: str, password_hash: str) -> None:
    cursor.execute(
        """
        INSERT INTO usuarios_sistema (username, password_hash, nombre_completo, rol)
        VALUES (%s, %s, %s, 'admin')
        ON DUPLICATE KEY UPDATE
            password_hash = VALUES(password_hash),
            nombre_completo = VALUES(nombre_completo),
            rol = VALUES(rol)
        """,
        (username, password_hash, full_name),
    )


def setup_database() -> bool:
    print("\nConfiguring database...")
    host = input("DB host [localhost]: ").strip() or "localhost"
    db = input("DB name [disfruleg]: ").strip() or "disfruleg"
    admin_user = input("MySQL admin user: ").strip()
    admin_pass = getpass("MySQL admin password: ")

    try:
        conn = mysql.connector.connect(
            host=host, user=admin_user, password=admin_pass, database=db
        )
        cursor = conn.cursor()
        ensure_schema(cursor)

        print("\nSeed an initial application admin user.")
        seed_username = input("App admin username: ").strip()
        seed_full_name = input("Full name: ").strip()
        seed_password = getpass("App admin password: ")
        if not seed_username or not seed_password:
            print("Username and password are required.")
            return False

        upsert_admin(cursor, seed_username, seed_full_name, hash_password(seed_password))
        conn.commit()
        conn.close()
        print("Admin user created/updated.")
        return True
    except mysql.connector.Error as exc:
        print(f"Database error: {exc}")
        return False


def main() -> bool:
    print("=" * 60)
    print("DISFRULEG AUTH INSTALLER")
    print("=" * 60)

    if not install_dependencies():
        return False
    if not setup_database():
        return False

    print(f"\nInstallation completed at {datetime.now().isoformat(timespec='seconds')}.")
    return True


if __name__ == "__main__":
    try:
        ok = main()
        sys.exit(0 if ok else 1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
