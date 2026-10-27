from database.conexion import get_connection, release_connection

def asistencia_hoy(id_terapeuta: int) -> list[dict]:
    """
    Llama a sp_asistencia_hoy en PostgreSQL.
    Retorna las citas del terapeuta para la fecha actual.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_asistencia_hoy(%s);",
                (id_terapeuta,)
            )
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en asistencia_hoy: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)

def control_asistencia(id_terapeuta: int, estado: str) -> int:
    """
    Llama a sp_control_asistencia en PostgreSQL.
    Retorna el id_asistencia generado, o -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_control_asistencia(%s, %s);",
                (id_terapeuta, estado)
            )
            id_asistencia = cursor.fetchone()[0]
            conn.commit()
            return id_asistencia
    except Exception as e:
        print(f"❌ Error en control_asistencia: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)