from database.conexion import get_connection, release_connection


def registrar_especialidad(nombre: str) -> int:
    """
    Llama a sp_registrar_especialidad en PostgreSQL.
    Retorna el id_especialidad generado, o -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_registrar_especialidad(%s);",
                (nombre,)
            )
            id_especialidad = cursor.fetchone()[0]
            conn.commit()
            return id_especialidad
    except Exception as e:
        print(f"❌ Error en registrar_especialidad: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def actualizar_especialidad(id_especialidad: int, nombre: str) -> int:
    """
    Llama a sp_actualizar_especialidad en PostgreSQL.
    Retorna 1 si actualizó, 0 si no existe, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_actualizar_especialidad(%s, %s);",
                (id_especialidad, nombre)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en actualizar_especialidad: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def eliminar_especialidad(id_especialidad: int) -> int:
    """
    Llama a sp_eliminar_especialidad en PostgreSQL (soft delete).
    Retorna 1 si desactivó, 0 si no existe, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_eliminar_especialidad(%s);",
                (id_especialidad,)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en eliminar_especialidad: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def activar_especialidad(id_especialidad: int) -> int:
    """
    Llama a sp_activar_especialidad en PostgreSQL.
    Retorna 1 si activó, 0 si no existe o ya estaba activa, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_activar_especialidad(%s);",
                (id_especialidad,)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en activar_especialidad: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def listar_especialidad() -> list[dict]:
    """
    Llama a sp_listar_especialidad en PostgreSQL.
    Retorna una lista de dicts con id_especialidad, nombre y estado.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sp_listar_especialidad();")
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en listar_especialidad: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)


def consultar_especialidad(id_especialidad: int) -> dict | None:
    """
    Llama a sp_consultar_especialidad en PostgreSQL.
    Retorna un dict con id_especialidad y nombre, o None si no existe.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_consultar_especialidad(%s);",
                (id_especialidad,)
            )
            columnas = [desc[0] for desc in cursor.description]
            fila = cursor.fetchone()
            if fila is None:
                return None
            return dict(zip(columnas, fila))
    except Exception as e:
        print(f"❌ Error en consultar_especialidad: {e}")
        return None
    finally:
        if conn:
            release_connection(conn)