import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

# Pool de conexiones (mejor rendimiento que abrir/cerrar por request)
try:
    if DATABASE_URL:
        # Producción (Render): usar la URL interna completa
        connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL,
        )
    else:
        # Local: usar variables individuales del .env
        connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
    print("✅ Pool de conexiones creado correctamente")
except Exception as e:
    print(f"❌ Error al crear el pool de conexiones: {e}")
    connection_pool = None


def get_connection():
    """Obtiene una conexión del pool."""
    if connection_pool is None:
        raise Exception("No hay pool de conexiones disponible")
    return connection_pool.getconn()


def release_connection(conn):
    """Devuelve la conexión al pool."""
    if connection_pool and conn:
        connection_pool.putconn(conn)