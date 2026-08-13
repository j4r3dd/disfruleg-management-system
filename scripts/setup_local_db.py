#!/usr/bin/env python3
"""
DISFRULEG - Configuración de base de datos local para desarrollo/demo.

Crea la base `disfruleg` en un MySQL local, ejecuta el esquema completo,
carga datos de ejemplo y crea un usuario administrador para el login.

Uso:
    python scripts/setup_local_db.py                 # usa valores de .env
    python scripts/setup_local_db.py --reset         # borra la BD y la recrea

Requiere en .env (o variables de entorno):
    DB_MODE=local
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
"""
import argparse
import getpass
import os
import re
import sys
from pathlib import Path

# Permitir ejecutar el script directamente desde la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import pymysql
    import bcrypt
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[ERROR] Falta una dependencia: {e.name}")
    print("        Instala los requisitos con: pip install -r requirements.txt")
    sys.exit(1)

SQL_DIR = PROJECT_ROOT / 'data' / 'sql'

# Orden de ejecución: el esquema primero, luego ajustes, vistas, triggers y datos.
SQL_FILES = [
    'disfruleg_schema.sql',
    'compat_schema.sql',
    'auth_schema.sql',
    'device_security_schema.sql',
    'sistema_mejorado.sql',
    '00_SCRIPT_SQL_MEJORAS.sql',
    'disfruleg_views.sql',
    'disfruleg_triggers.sql',
    'inserts_updated.sql',
    'demo_transacciones.sql',
]

DEFAULT_ADMIN_USER = 'admin'
DEFAULT_ADMIN_NAME = 'Administrador Demo'


def _strip_inline_comment(line):
    """
    Elimina un comentario `--` al final de la línea, ignorando los que
    aparecen dentro de cadenas entrecomilladas.
    """
    quote = None
    i = 0
    while i < len(line):
        ch = line[i]

        if quote:
            # Dentro de una cadena: saltar escapes y detectar el cierre
            if ch == '\\':
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in ("'", '"', '`'):
            quote = ch
        elif ch == '-' and line[i:i + 2] == '--':
            # MySQL exige espacio (o fin de línea) tras `--` para que sea comentario
            rest = line[i + 2:]
            if rest == '' or rest[0].isspace():
                return line[:i]

        i += 1

    return line


def split_statements(sql_text):
    """
    Divide un script SQL en sentencias, respetando bloques DELIMITER
    (necesario para procedimientos y triggers).
    """
    statements = []
    delimiter = ';'
    buffer = ''

    for line in sql_text.splitlines():
        stripped = line.strip()

        # Ignorar comentarios de línea completa
        if stripped.startswith('--') or not stripped:
            continue

        # Cambio de delimitador
        match = re.match(r'^DELIMITER\s+(\S+)', stripped, re.IGNORECASE)
        if match:
            if buffer.strip():
                statements.append(buffer.strip())
                buffer = ''
            delimiter = match.group(1)
            continue

        # Quitar comentarios al final de la línea: un `;` dentro de un comentario
        # partiría la sentencia en dos. Se respetan los `--` que estén dentro de
        # una cadena entrecomillada.
        line = _strip_inline_comment(line)
        if not line.strip():
            continue

        buffer += line + '\n'

        while delimiter in buffer:
            stmt, _, rest = buffer.partition(delimiter)
            if stmt.strip():
                statements.append(stmt.strip())
            buffer = rest

    if buffer.strip():
        statements.append(buffer.strip())

    return statements


def run_sql_file(cursor, path):
    """Ejecuta un archivo SQL sentencia por sentencia."""
    if not path.exists():
        print(f"  [SKIP] {path.name} (no encontrado)")
        return 0, 0

    sql_text = path.read_text(encoding='utf-8', errors='replace')
    statements = split_statements(sql_text)

    ok = 0
    failed = 0
    for stmt in statements:
        try:
            cursor.execute(stmt)
            ok += 1
        except Exception as e:
            failed += 1
            preview = ' '.join(stmt.split())[:70]
            print(f"  [WARN] {type(e).__name__}: {e}")
            print(f"         en: {preview}...")

    status = 'OK' if failed == 0 else f'{failed} con error'
    print(f"  [{status}] {path.name}: {ok} sentencias aplicadas")
    return ok, failed


def create_admin_user(cursor, username, password, nombre_completo):
    """Crea o actualiza el usuario administrador con hash bcrypt."""
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')

    cursor.execute(
        "SELECT id_usuario FROM usuarios_sistema WHERE username = %s",
        (username,)
    )

    if cursor.fetchone():
        cursor.execute("""
            UPDATE usuarios_sistema
            SET password_hash = %s,
                nombre_completo = %s,
                rol = 'admin',
                activo = TRUE,
                intentos_fallidos = 0,
                bloqueado_hasta = NULL
            WHERE username = %s
        """, (password_hash, nombre_completo, username))
        print(f"  [OK] Usuario '{username}' actualizado")
    else:
        cursor.execute("""
            INSERT INTO usuarios_sistema
                (username, password_hash, nombre_completo, rol, activo)
            VALUES (%s, %s, %s, 'admin', TRUE)
        """, (username, password_hash, nombre_completo))
        print(f"  [OK] Usuario '{username}' creado")


def authorize_current_device(cursor, username):
    """
    Registra el equipo actual como dispositivo autorizado.

    Sin esto la app pide autorización de un administrador desde otro equipo,
    lo que deja el primer arranque bloqueado en una demo local.
    """
    try:
        from src.security.device_manager import DeviceManager
    except Exception as e:
        print(f"  [SKIP] No se pudo cargar DeviceManager: {e}")
        return

    dm = DeviceManager()
    device_id = dm.device_id
    device_name = None
    for getter in ('get_device_name', '_get_device_name'):
        if hasattr(dm, getter):
            try:
                device_name = getattr(dm, getter)()
                break
            except Exception:
                pass
    device_name = device_name or os.environ.get('COMPUTERNAME', 'Equipo local')

    # El cursor de este script es de tuplas (no DictCursor)
    cursor.execute(
        "SELECT id_usuario FROM usuarios_sistema WHERE username = %s", (username,)
    )
    row = cursor.fetchone()
    id_usuario = row[0] if row else None

    cursor.execute("""
        INSERT INTO dispositivos_autorizados
            (device_id, device_name, device_info, id_usuario,
             autorizado, estado, activo, fecha_autorizacion)
        VALUES (%s, %s, %s, %s, TRUE, 'AUTORIZADO', TRUE, NOW())
        ON DUPLICATE KEY UPDATE
            autorizado = TRUE,
            estado = 'AUTORIZADO',
            activo = TRUE,
            fecha_eliminacion = NULL,
            razon_bloqueo = NULL,
            fecha_autorizacion = NOW()
    """, (device_id, device_name, 'Registrado por setup_local_db.py', id_usuario))

    print(f"  [OK] Equipo autorizado: {device_name} ({device_id[:12]}...)")


def main():
    parser = argparse.ArgumentParser(
        description="Configura la base de datos local de DISFRULEG"
    )
    parser.add_argument(
        '--reset', action='store_true',
        help="Elimina la base de datos existente antes de crearla"
    )
    parser.add_argument(
        '--admin-user', default=DEFAULT_ADMIN_USER,
        help=f"Usuario administrador a crear (default: {DEFAULT_ADMIN_USER})"
    )
    parser.add_argument(
        '--admin-password',
        help="Contraseña del administrador (si se omite, se pide interactivamente)"
    )
    parser.add_argument(
        '--skip-device', action='store_true',
        help="No autorizar automáticamente este equipo (útil para probar el flujo de autorización)"
    )
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / '.env')

    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME', 'disfruleg')

    if not user:
        print("[ERROR] DB_USER no está definido. Copia .env.example a .env y complétalo.")
        sys.exit(1)

    if password is None:
        password = getpass.getpass(f"Contraseña de MySQL para '{user}': ")

    admin_password = args.admin_password
    if not admin_password:
        admin_password = getpass.getpass(
            f"Contraseña para el usuario '{args.admin_user}' de la app: "
        )
        if not admin_password:
            print("[ERROR] La contraseña del administrador no puede estar vacía.")
            sys.exit(1)

    print(f"\n=== DISFRULEG :: setup de base de datos local ===")
    print(f"Servidor: {host}:{port}")
    print(f"Base de datos: {db_name}\n")

    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password,
            charset='utf8mb4', autocommit=True
        )
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MySQL: {e}")
        print("        Verifica que el servicio MySQL esté corriendo y que")
        print("        DB_USER/DB_PASSWORD en .env sean correctos.")
        sys.exit(1)

    total_failed = 0

    try:
        with conn.cursor() as cursor:
            if args.reset:
                print(f"[1/4] Eliminando base de datos '{db_name}'...")
                cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
            else:
                print("[1/4] Conservando base de datos existente (usa --reset para recrear)")

            print(f"[2/4] Creando base de datos '{db_name}'...")
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.execute(f"USE `{db_name}`")

            print("[3/4] Ejecutando scripts SQL...")
            for filename in SQL_FILES:
                _, failed = run_sql_file(cursor, SQL_DIR / filename)
                total_failed += failed

            print("[4/5] Creando usuario administrador...")
            create_admin_user(
                cursor, args.admin_user, admin_password, DEFAULT_ADMIN_NAME
            )

            print("[5/5] Autorizando este equipo...")
            if args.skip_device:
                print("  [SKIP] Omitido por --skip-device")
            else:
                authorize_current_device(cursor, args.admin_user)

            cursor.execute("SHOW TABLES")
            table_count = len(cursor.fetchall())

    finally:
        conn.close()

    print(f"\n=== Listo: {table_count} tablas en '{db_name}' ===")
    if total_failed:
        print(f"[NOTA] {total_failed} sentencias fallaron. Suelen ser objetos que ya")
        print("       existían o vistas dependientes de datos; revisa los avisos")
        print("       de arriba si algún módulo no carga.")
    print(f"\nInicia la app con:  python main.py")
    print(f"Usuario: {args.admin_user}")


if __name__ == '__main__':
    main()
