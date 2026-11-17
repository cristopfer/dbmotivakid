from datetime import date
from database.conexion import get_connection, release_connection
from modelo.modelo import predecir_fila


def obtener_features_prediccion(
    fecha_desde: date,
    fecha_hasta: date,
    id_especialidad: int | None = None,
    id_terapeuta: int | None = None,
) -> list[dict]:
    """Llama a sp_features_para_prediccion en PostgreSQL."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_features_para_prediccion(%s, %s, %s, %s);",
                (fecha_desde, fecha_hasta, id_especialidad, id_terapeuta)
            )
            columnas = [d[0] for d in cursor.description]
            return [dict(zip(columnas, r)) for r in cursor.fetchall()]
    except Exception as e:
        print(f"❌ Error en obtener_features_prediccion: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)


def obtener_datos_reales(
    fecha_desde: date,
    fecha_hasta: date,
    id_especialidad: int | None = None,
    id_terapeuta: int | None = None,
) -> list[dict]:
    """Llama a sp_obtener_datos_reales en PostgreSQL."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sp_obtener_datos_reales(%s, %s, %s, %s);",
                (fecha_desde, fecha_hasta, id_especialidad, id_terapeuta)
            )
            columnas = [d[0] for d in cursor.description]
            return [dict(zip(columnas, r)) for r in cursor.fetchall()]
    except Exception as e:
        print(f"❌ Error en obtener_datos_reales: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)


def predecir_rango(
    fecha_desde: date,
    fecha_hasta: date,
    id_especialidad: int | None = None,
    id_terapeuta: int | None = None,
) -> list[dict]:
    """Itera sobre las features y usa el modelo ML para predecir."""
    features = obtener_features_prediccion(
        fecha_desde, fecha_hasta, id_especialidad, id_terapeuta
    )
    resultados = []
    for f in features:
        try:
            pred = predecir_fila(f)
        except Exception as e:
            print(f"❌ Error al predecir {f}: {e}")
            pred = 0.0

        resultados.append({
            "fecha": str(f["fecha"]),
            "id_especialidad": f["id_especialidad"],
            "especialidad": f["especialidad"],
            "prediccion": round(float(pred), 2),
        })
    return resultados


def demanda_agregada(
    fecha_desde: date,
    fecha_hasta: date,
    id_especialidad: int | None = None,
    id_terapeuta: int | None = None,
) -> dict:
    """Combina predicciones y datos reales en el JSON que consume el frontend."""
    predicciones = predecir_rango(fecha_desde, fecha_hasta, id_especialidad, id_terapeuta)
    reales = obtener_datos_reales(fecha_desde, fecha_hasta, id_especialidad, id_terapeuta)

    reales_map = {
        (str(r["fecha"]), r["id_especialidad"]): {
            "real": int(r["total_real"]),
            "pacientes": int(r["pacientes"]),
        }
        for r in reales
    }

    # Serie diaria
    serie = []
    for p in predicciones:
        key = (p["fecha"], p["id_especialidad"])
        r = reales_map.get(key, {"real": 0, "pacientes": 0})
        serie.append({
            "fecha": p["fecha"],
            "id_especialidad": p["id_especialidad"],
            "especialidad": p["especialidad"],
            "pronosticadas": p["prediccion"],
            "realizadas": r["real"],
        })

    # KPIs
    total_sesiones = sum(p["prediccion"] for p in predicciones)
    dias = sorted({p["fecha"] for p in predicciones})
    demanda_promedio = total_sesiones / len(dias) if dias else 0

    por_fecha = {}
    for p in predicciones:
        por_fecha[p["fecha"]] = por_fecha.get(p["fecha"], 0) + p["prediccion"]
    top_dias = sorted(por_fecha.items(), key=lambda x: -x[1])[:2]

    nombres_dia = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dias_mayor = [
        f"{nombres_dia[date.fromisoformat(d).weekday()]} ({round(v)} sesiones)"
        for d, v in top_dias
    ]

    total_pacientes = sum(r["pacientes"] for r in reales)

    # Detalle por especialidad
    detalle = {}
    for p in predicciones:
        key = p["id_especialidad"]
        detalle.setdefault(key, {
            "id_especialidad": key,
            "especialidad": p["especialidad"],
            "estimadas": 0,
            "realizadas": 0,
            "pacientes": 0,
        })
        detalle[key]["estimadas"] += p["prediccion"]

    for r in reales:
        key = r["id_especialidad"]
        if key in detalle:
            detalle[key]["realizadas"] += int(r["total_real"])
            detalle[key]["pacientes"] += int(r["pacientes"])

    detalle_lista = []
    for d in detalle.values():
        cumpl = (d["realizadas"] / d["estimadas"] * 100) if d["estimadas"] > 0 else 0
        detalle_lista.append({
            "id_especialidad": d["id_especialidad"],
            "especialidad": d["especialidad"],
            "pacientes_estimados": d["pacientes"],
            "sesiones_estimadas": round(d["estimadas"], 0),
            "sesiones_realizadas": d["realizadas"],
            "cumplimiento": round(cumpl, 1),
        })

    return {
        "rango": {"desde": str(fecha_desde), "hasta": str(fecha_hasta)},
        "kpis": {
            "total_pacientes": total_pacientes,
            "sesiones_pronosticadas": round(total_sesiones, 0),
            "demanda_promedio_diaria": round(demanda_promedio, 1),
            "dias_mayor_demanda": dias_mayor,
        },
        "serie": serie,
        "detalle_especialidad": detalle_lista,
    }