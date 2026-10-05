from database.conexion import get_connection, release_connection


def registrar_terapeuta(
    nombres: str,
    apellidos: str,
    id_especialidad: int,
) -> int:
    """
    Llama a sp_registrar_terapeuta en PostgreSQL.
    Retorna el id_terapeuta generado, o -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_registrar_terapeuta(%s, %s, %s);",
                (nombres, apellidos, id_especialidad)
            )
            id_terapeuta = cursor.fetchone()[0]
            conn.commit()
            return id_terapeuta
    except Exception as e:
        print(f"❌ Error en registrar_terapeuta: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def actualizar_terapeuta(
    id_terapeuta: int,
    nombres: str,
    apellidos: str,
    id_especialidad: int,
) -> int:
    """
    Llama a sp_actualizar_terapeuta en PostgreSQL.
    Retorna 1 si actualizó, 0 si no existe, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_actualizar_terapeuta(%s, %s, %s, %s);",
                (id_terapeuta, nombres, apellidos, id_especialidad)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en actualizar_terapeuta: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def eliminar_terapeuta(id_terapeuta: int) -> int:
    """
    Llama a sp_eliminar_terapeuta en PostgreSQL (soft delete).
    Retorna 1 si desactivó, 0 si no existe, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_eliminar_terapeuta(%s);",
                (id_terapeuta,)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en eliminar_terapeuta: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def activar_terapeuta(id_terapeuta: int) -> int:
    """
    Llama a sp_activar_terapeuta en PostgreSQL.
    Retorna 1 si activó, 0 si no existe o ya estaba activo, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_activar_terapeuta(%s);",
                (id_terapeuta,)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en activar_terapeuta: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def listar_terapeuta() -> list[dict]:
    """
    Llama a sp_listar_terapeuta en PostgreSQL.
    Retorna una lista de dicts con id_terapeuta, nombres, apellidos,
    especialidad y estado.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sp_listar_terapeuta();")
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en listar_terapeuta: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)


def consultar_terapeuta(id_terapeuta: int) -> dict | None:
    """
    Llama a sp_consultar_terapeuta en PostgreSQL.
    Retorna un dict con los datos del terapeuta, o None si no existe.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_consultar_terapeuta(%s);",
                (id_terapeuta,)
            )
            columnas = [desc[0] for desc in cursor.description]
            fila = cursor.fetchone()
            if fila is None:
                return None
            return dict(zip(columnas, fila))
    except Exception as e:
        print(f"❌ Error en consultar_terapeuta: {e}")
        return None
    finally:
        if conn:
            release_connection(conn)