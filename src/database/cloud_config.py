import os
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector
import pymysql.cursors
from src.utils.resource_path import get_resource_path

# Cargar variables de entorno
load_dotenv()

# Configurar credenciales del Service Account
credentials_path = get_resource_path('credentials.json')
if credentials_path.exists():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path)
    print(f"[OK] Usando Service Account: {credentials_path}")
else:
    print(f"[WARNING] Archivo credentials.json no encontrado en: {credentials_path}")
    print("  Usando credenciales de gcloud auth application-default login")

# Connection name de Cloud SQL
CLOUD_SQL_CONNECTION_NAME = "automatizacion-468918:northamerica-south1:bodega-disfruleg-dev"

# Configuración de base de datos
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME', 'disfruleg')

# Inicializar el conector (solo una vez)
connector = Connector()

def get_db_config():
    """Retorna configuración básica como diccionario"""
    return {
        'user': DB_USER,
        'password': DB_PASSWORD,
        'database': DB_NAME,
        'charset': 'utf8mb4'
    }

def is_cloud_sql():
    """Siempre usamos Cloud SQL con Auth Proxy"""
    return True