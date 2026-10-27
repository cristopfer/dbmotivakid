from database.conexion import get_connection, release_connection


def agendar_cita(
    id_paciente: int,
    id_terapeuta: int,
    fecha: str,           # 'YYYY-MM-DD'
    hora_inicio: str,     # 'HH:MM'
    hora_fin: str,        # 'HH:MM'
) -> int:
    """
    Llama a sp_agendar_cita en PostgreSQL.
    Retorna el id_cita generado, o -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_agendar_cita(%s, %s, %s, %s, %s);",
                (id_paciente, id_terapeuta, fecha, hora_inicio, hora_fin)
            )
            id_cita = cursor.fetchone()[0]
            conn.commit()
            return id_cita
    except Exception as e:
        print(f"❌ Error en agendar_cita: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)

def cita_disponibilidad_terapeuta(id_terapeuta: int, fecha: str) -> list[dict]:
    """
    Llama a sp_cita_disponibilidad_terapeuta en PostgreSQL.
    Retorna los bloques de disponibilidad de un terapeuta en una fecha,
    con el nombre del paciente si el bloque está ocupado.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_cita_disponibilidad_terapeuta(%s, %s);",
                (id_terapeuta, fecha)
            )
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en cita_disponibilidad_terapeuta: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)

def reservar_cita(id_cita: int) -> int:
    """
    Llama a sp_reservar_cita en PostgreSQL para liberar el bloque.
    Retorna 1 si canceló, 0 si no existe/ya estaba cancelada, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_reservar_cita(%s);",
                (id_cita,)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en reservar_cita: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)