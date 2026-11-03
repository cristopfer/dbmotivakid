from database.conexion import get_connection, release_connection

def actualizar_registro_pago_paciente() -> int:
    """
    Llama a sp_actualizar_registro_pago_paciente en PostgreSQL.
    Retorna la cantidad de pagos generados, o -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT sp_actualizar_registro_pago_paciente();")
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en actualizar_registro_pago_paciente: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)

def guardar_pago(
    id_pago_paciente: int,
    monto: float,
    forma_pago: str,
    fecha_pago: str  # Formato 'YYYY-MM-DD'
) -> int:
    """
    Llama a sp_guardar_pago en PostgreSQL.
    Retorna 1 si actualizó, 0 si no existe, -1 si hubo error.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_guardar_pago(%s, %s, %s, %s);",
                (id_pago_paciente, monto, forma_pago, fecha_pago)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en guardar_pago: {e}")
        if conn:
            conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)

def lista_pagos_pacientes(
    id_paciente: int = None,
    estado: str = None,
    forma_pago: str = None
) -> list[dict]:
    """
    Llama a sp_lista_pagos_pacientes en PostgreSQL.
    Los parámetros son opcionales para filtrar la lista.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_lista_pagos_pacientes(%s, %s, %s);",
                (id_paciente, estado, forma_pago)
            )
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error en lista_pagos_pacientes: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)