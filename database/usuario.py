from database.conexion import get_connection, release_connection


def ingresar_sistema(correo: str, password: str) -> bool:
    """
    Llama a la función sp_ingresar_sistema en PostgreSQL.
    Retorna True si el usuario ingresa (1), False si no (0).
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_ingresar_sistema(%s, %s);",
                (correo, password)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado == 1
    except Exception as e:
        print(f"❌ Error en ingresar_sistema: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            release_connection(conn)