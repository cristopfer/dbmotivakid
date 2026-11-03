from database.conexion import get_connection, release_connection

def listar_terapeutas_mes(periodo: str = None, id_terapeuta: int = None) -> list[dict]:
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_listar_terapeutas_mes(%s, %s);",
                (periodo, id_terapeuta)
            )
            columnas = [desc[0] for desc in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    except Exception as e:
        print(f"❌ Error en listar_terapeutas_mes: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)

def generar_control_pago_terapeutas(periodo: str) -> int:
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_generar_control_pago_terapeutas(%s);",
                (periodo,)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en generar_control_pago_terapeutas: {e}")
        if conn: conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)

def guardar_pagos_terapeutas(
    id_pago_terapeuta: int,
    id_terapeuta: int,
    periodo: str,
    modalidad_pago: str,
    monto_base: float,
    descuento: float,
    fecha_pago: str
) -> int:
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT sp_guardar_pagos_terapeutas(%s, %s, %s, %s, %s, %s, %s);",
                (id_pago_terapeuta, id_terapeuta, periodo, modalidad_pago, monto_base, descuento, fecha_pago)
            )
            resultado = cursor.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        print(f"❌ Error en guardar_pagos_terapeutas: {e}")
        if conn: conn.rollback()
        return -1
    finally:
        if conn:
            release_connection(conn)