import os
from dotenv import load_dotenv
import pymysql.cursors
from src.utils.resource_path import get_resource_path

# Cargar variables de entorno
load_dotenv()

# Modo de base de datos: 'local' (MySQL/MariaDB) o 'cloud' (Cloud SQL Connector)
DB_MODE = os.getenv('DB_MODE', 'cloud').strip().lower()

# Connection name de Cloud SQL
CLOUD_SQL_CONNECTION_NAME = os.getenv(
    'CLOUD_SQL_CONNECTION_NAME',
    "automatizacion-468918:northamerica-south1:bodega-disfruleg-dev"
)

# Configuración de base de datos
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME', 'disfruleg')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))

# El conector de Cloud SQL solo se inicializa en modo cloud: importarlo requiere
# credenciales de Google y no tiene sentido en una instalación local.
connector = None

if DB_MODE == 'local':
    print(f"[OK] Modo LOCAL: conectando a MySQL en {DB_HOST}:{DB_PORT}/{DB_NAME}")
else:
    from google.cloud.sql.connector import Connector

    # Configurar credenciales del Service Account
    credentials_path = get_resource_path('credentials.json')
    if credentials_path.exists():
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)
        print(f"[OK] Usando Service Account: {credentials_path}")
    else:
        print(f"[WARNING] Archivo credentials.json no encontrado en: {credentials_path}")
        print("  Usando credenciales de gcloud auth application-default login")

    # Inicializar el conector (solo una vez)
    connector = Connector()


def create_connection():
    """
    Crea una conexión nueva a la base de datos según el modo configurado.

    Returns:
        Conexión pymysql lista para usar.
    """
    if DB_MODE == 'local':
        return pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    return connector.connect(
        CLOUD_SQL_CONNECTION_NAME,
        "pymysql",
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


def get_db_config():
    """Retorna configuración básica como diccionario"""
    return {
        'user': DB_USER,
        'password': DB_PASSWORD,
        'database': DB_NAME,
        'charset': 'utf8mb4'
    }

def is_cloud_sql():
    """Indica si la aplicación está usando Cloud SQL"""
    return DB_MODE != 'local'
