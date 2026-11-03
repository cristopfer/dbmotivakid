from database.conexion import get_connection, release_connection

def reporte_pacientes(id_paciente: int) -> list[dict]:
    """
    Llama a sp_reporte_pacientes en PostgreSQL.
    Retorna el historial de pagos y citas del paciente.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sp_reporte_pacientes(%s);", (id_paciente,))
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en reporte_pacientes: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)

def reporte_terapeutas(id_terapeuta: int) -> list[dict]:
    """
    Llama a sp_reporte_terapeutas en PostgreSQL.
    Retorna el historial de ingresos y citas del terapeuta.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sp_reporte_terapeutas(%s);", (id_terapeuta,))
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en reporte_terapeutas: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)

# reporte.py
def datos_estadisticos() -> dict:
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sp_datos_estadisticos();")
            columnas = [desc[0] for desc in cursor.description]
            fila = cursor.fetchone()
            if fila is None:
                return {}
            # dict(zip) mapea dinámicamente las 9 columnas de salida
            return dict(zip(columnas, fila)) 
    except Exception as e:
        print(f"❌ Error en datos_estadisticos: {e}")
        return {}
    finally:
        if conn:
            release_connection(conn)