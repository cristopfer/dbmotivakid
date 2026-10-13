from database.conexion import get_connection, release_connection


def horarios_terapeuta_paciente(
    id_terapeuta: int,
    fecha_lunes: str,     # 'YYYY-MM-DD'
    fecha_domingo: str,   # 'YYYY-MM-DD'
) -> list[dict]:
    """
    Llama a sp_horarios_terapeuta_paciente en PostgreSQL.
    Retorna una lista de dicts con terapeuta, especialidad, paciente,
    fecha, hora_inicio, hora_fin y estado de cada cita del rango.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_horarios_terapeuta_paciente(%s, %s, %s);",
                (id_terapeuta, fecha_lunes, fecha_domingo)
            )
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en horarios_terapeuta_paciente: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)