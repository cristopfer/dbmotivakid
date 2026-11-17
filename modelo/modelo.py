# modelo/modelo.py
"""
Módulo de inferencia para el modelo de predicción de citas.
Carga modelo_prediccion.pkl y expone una función predecir() que recibe
los datos de entrada (features) y devuelve el número de citas estimado.
"""

from pathlib import Path
from datetime import date, datetime
from typing import Optional

import joblib
import numpy as np
import pandas as pd

# Ruta al modelo (mismo directorio que este archivo)
MODEL_PATH = Path(__file__).parent / "modelo_prediccion.pkl"

# Cargar una sola vez al importar el módulo
try:
    _modelo = joblib.load(MODEL_PATH)
except Exception as e:
    _modelo = None
    _error_carga = str(e)
else:
    _error_carga = None


# Columnas que espera el modelo (según data_completa.csv)
FEATURES = [
    "dia_semana",
    "mes",
    "anio",
    "semana_del_anio",
    "especialidad",
    "citas_dia_anterior",
    "citas_semana_anterior",
    "promedio_7_dias",
    "promedio_30_dias",
    "mes_sin", "mes_cos",
    "dia_sin", "dia_cos",
    "sem_sin", "sem_cos",
]


def _construir_features(
    fecha: date,
    especialidad: str,
    citas_dia_anterior: float,
    citas_semana_anterior: float,
    promedio_7_dias: float,
    promedio_30_dias: float,
) -> pd.DataFrame:
    """Arma el DataFrame de una sola fila con las features que espera el modelo."""
    dia = fecha.weekday()                  
    mes = fecha.month 
    semana = fecha.isocalendar().week
    return pd.DataFrame(
        [{
            "dia_semana": fecha.weekday(),           # 0=lunes ... 5=sábado
            "mes": fecha.month,
            "anio": fecha.year,
            "semana_del_anio": semana,
            "especialidad": especialidad,
            "citas_dia_anterior": citas_dia_anterior,
            "citas_semana_anterior": citas_semana_anterior,
            "promedio_7_dias": promedio_7_dias,
            "promedio_30_dias": promedio_30_dias,
            "mes_sin": np.sin(2 * np.pi * mes / 12),
            "mes_cos": np.cos(2 * np.pi * mes / 12),
            "dia_sin": np.sin(2 * np.pi * dia / 7),
            "dia_cos": np.cos(2 * np.pi * dia / 7),
            "sem_sin": np.sin(2 * np.pi * semana / 52),
            "sem_cos": np.cos(2 * np.pi * semana / 52),
        }],
        columns=FEATURES,
    )


def predecir(
    fecha: date,
    especialidad: str,
    citas_dia_anterior: float = 0.0,
    citas_semana_anterior: float = 0.0,
    promedio_7_dias: float = 0.0,
    promedio_30_dias: float = 0.0,
) -> dict:
    """
    Devuelve un dict con la predicción de total_citas para la fecha/especialidad dada.

    Si el .pkl contiene un Pipeline (con preprocesamiento de categóricas incluido),
    esta función funciona directamente. Si el .pkl es solo el estimador y no
    acepta la columna 'especialidad' como string, hay que hacer encoding manual
    (ver nota al final).
    """
    if _modelo is None:
        raise RuntimeError(f"No se pudo cargar el modelo: {_error_carga}")

    X = _construir_features(
        fecha=fecha,
        especialidad=especialidad,
        citas_dia_anterior=citas_dia_anterior,
        citas_semana_anterior=citas_semana_anterior,
        promedio_7_dias=promedio_7_dias,
        promedio_30_dias=promedio_30_dias,
    )

    try:
        pred = _modelo.predict(X)
    except Exception as e:
        # Fallback: si el modelo no acepta string en 'especialidad',
        # intentamos codificarla como 0/1 (Lenguaje=0, Psicología=1).
        # Ajusta este mapeo según cómo la hayas codificado al entrenar.
        X["especialidad"] = X["especialidad"].map(
            {"Lenguaje": 0, "Psicología": 1}
        ).fillna(0).astype(int)
        pred = _modelo.predict(X)

    valor = float(np.clip(pred[0], 0, None))  # no negativos
    return {
        "prediccion_total_citas": round(valor, 2),
        "fecha": fecha.isoformat(),
        "especialidad": especialidad,
        "features_usadas": X.iloc[0].to_dict(),
    }


def modelo_disponible() -> bool:
    return _modelo is not None


def info_modelo() -> dict:
    if _modelo is None:
        return {"disponible": False, "error": _error_carga}
    return {
        "disponible": True,
        "tipo": type(_modelo).__name__,
        "features": FEATURES,
    }

def predecir_fila(features: dict) -> float:
    """
    Recibe un dict con los features calculados por Postgres y devuelve la predicción.
    """
    if _modelo is None:
        raise RuntimeError("Modelo no cargado")

    from datetime import date as dt_date

    fecha = features["fecha"]
    if isinstance(fecha, str):
        fecha = dt_date.fromisoformat(fecha)

    dia = fecha.weekday()
    mes = fecha.month
    semana = fecha.isocalendar().week

    # Construimos el DataFrame con exactamente las columnas que usó el entrenamiento
    fila = {
        "dia_semana": int(features["dia_semana"]),
        "mes": int(features["mes"]),
        "anio": int(features["anio"]),
        "semana_del_anio": int(features["semana_del_anio"]),
        "especialidad": features["especialidad"],   # string
        "citas_dia_anterior": float(features["citas_dia_anterior"] or 0),
        "citas_semana_anterior": float(features["citas_semana_anterior"] or 0),
        "promedio_7_dias": float(features["promedio_7_dias"] or 0),
        "promedio_30_dias": float(features["promedio_30_dias"] or 0),
        "mes_sin": np.sin(2 * np.pi * mes / 12),
        "mes_cos": np.cos(2 * np.pi * mes / 12),
        "dia_sin": np.sin(2 * np.pi * dia / 7),
        "dia_cos": np.cos(2 * np.pi * dia / 7),
        "sem_sin": np.sin(2 * np.pi * semana / 52),
        "sem_cos": np.cos(2 * np.pi * semana / 52),
    }

    X = pd.DataFrame([fila], columns=FEATURES)
    pred = float(np.clip(_modelo.predict(X)[0], 0, None))
    return pred