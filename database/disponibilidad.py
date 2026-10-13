import json
from database.conexion import get_connection, release_connection


def registrar_disponibilidad(id_terapeuta: int, bloques: list[dict]) -> int:
    """
    Llama a sp_registrar_disponibilidad en PostgreSQL.
    Recibe una lista de bloques: [{"dia_semana": "...", "hora_inicio": "...", "hora_fin": "..."}]
    Retorna la cantidad de bloques insertados, o -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            print(f"🔍 id_terapeuta: {id_terapeuta} (tipo: {type(id_terapeuta)})")
            print(f"🔍 bloques: {bloques}")
            print(f"🔍 bloques (repr): {repr(bloques)}")
            json_str = json.dumps(bloques)
            print(f"🔍 JSON: {json_str}")
            cursor.execute(
                "SELECT sp_registrar_disponibilidad(%s, %s::jsonb);",
                (id_terapeuta, json.dumps(bloques))
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en registrar_disponibilidad: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def actualizar_disponibilidad(id_terapeuta: int, bloques: list[dict]) -> int:
    """
    Llama a sp_actualizar_disponibilidad en PostgreSQL.
    Reemplaza todos los bloques del terapeuta por la nueva lista.
    Retorna la cantidad de bloques insertados, o -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_actualizar_disponibilidad(%s, %s::jsonb);",
                (id_terapeuta, json.dumps(bloques))
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en actualizar_disponibilidad: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def consultar_disponibilidad(id_terapeuta: int) -> list[dict]:
    """
    Llama a sp_consultar_disponibilidad en PostgreSQL.
    Retorna una lista de dicts con los bloques del terapeuta.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_consultar_disponibilidad(%s);",
                (id_terapeuta,)
            )
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en consultar_disponibilidad: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)