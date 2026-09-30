from database.conexion import get_connection, release_connection


def registrar_paciente(
    nombre: str,
    apellido: str,
    fecha_nacimiento: str,   # 'YYYY-MM-DD'
    diagnostico: str,
    motivo_consulta: str,
    telefono: str,
    nombre_apoderado: str,
    correo: str,
) -> int:
    """
    Llama a sp_registrar_paciente en PostgreSQL.
    Retorna el id_paciente generado, o -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_registrar_paciente(%s, %s, %s, %s, %s, %s, %s, %s);",
                (
                    nombre,
                    apellido,
                    fecha_nacimiento,
                    diagnostico,
                    motivo_consulta,
                    telefono,
                    nombre_apoderado,
                    correo,
                )
            )
            id_paciente = cursor.fetchone()[0]
            conn.commit()
            return id_paciente
    except Exception as e:
        print(f"❌ Error en registrar_paciente: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def actualizar_paciente(
    id_paciente: int,
    nombre: str,
    apellido: str,
    fecha_nacimiento: str,   # 'YYYY-MM-DD'
    diagnostico: str,
    motivo_consulta: str,
    telefono: str,
    nombre_apoderado: str,
    correo: str,
) -> int:
    """
    Llama a sp_actualizar_paciente en PostgreSQL.
    Retorna 1 si actualizó, 0 si no existe, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT sp_actualizar_paciente(
                       %s, %s, %s, %s, %s, %s, %s, %s, %s
                   );""",
                (
                    id_paciente,
                    nombre,
                    apellido,
                    fecha_nacimiento,
                    diagnostico,
                    motivo_consulta,
                    telefono,
                    nombre_apoderado,
                    correo,
                )
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en actualizar_paciente: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def eliminar_paciente(id_paciente: int) -> int:
    """
    Llama a sp_eliminar_paciente en PostgreSQL (soft delete).
    Retorna 1 si desactivó, 0 si no existe, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_eliminar_paciente(%s);",
                (id_paciente,)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en eliminar_paciente: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def activar_paciente(id_paciente: int) -> int:
    """
    Llama a sp_activar_paciente en PostgreSQL.
    Retorna 1 si activó, 0 si no existe o ya estaba activo, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_activar_paciente(%s);",
                (id_paciente,)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en activar_paciente: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)


def listar_paciente() -> list[dict]:
    """
    Llama a sp_listar_paciente en PostgreSQL.
    Retorna una lista de dicts con los datos del paciente.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sp_listar_paciente();")
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en listar_paciente: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)

def consultar_paciente(id_paciente: int) -> dict | None:
    """
    Llama a sp_consultar_paciente en PostgreSQL.
    Retorna un dict con los datos del paciente, o None si no existe.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_consultar_paciente(%s);",
                (id_paciente,)
            )
            columnas = [desc[0] for desc in cursor.description]
            fila = cursor.fetchone()
            if fila is None:
                return None
            return dict(zip(columnas, fila))
    except Exception as e:
        print(f"❌ Error en consultar_paciente: {e}")
        return None
    finally:
        if conn:
            release_connection(conn)