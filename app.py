from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from database.usuario import ingresar_sistema
from database.paciente import (
    registrar_paciente,
    actualizar_paciente,
    eliminar_paciente,
    activar_paciente,
    listar_paciente,
    consultar_paciente, 
)

app = FastAPI(title="API Centro Terapéutico")

# CORS para permitir que React (Vite/Next) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://motivakid.onrender.com",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Modelos Pydantic — Autenticación
# ==========================================
class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str


# ==========================================
# Modelos Pydantic — Paciente
# ==========================================
class PacienteRegistrarRequest(BaseModel):
    nombre: str
    apellido: str
    fecha_nacimiento: date
    diagnostico: str | None = None
    motivo_consulta: str | None = None
    telefono: str | None = None
    nombre_apoderado: str | None = None
    correo: EmailStr | None = None


class PacienteActualizarRequest(BaseModel):
    id_paciente: int
    nombre: str
    apellido: str
    fecha_nacimiento: date
    diagnostico: str | None = None
    motivo_consulta: str | None = None
    telefono: str | None = None
    nombre_apoderado: str | None = None
    correo: EmailStr | None = None


class PacienteResponse(BaseModel):
    success: bool
    message: str
    id_paciente: int | None = None


# ==========================================
# Rutas — Generales
# ==========================================
@app.get("/")
def root():
    return {"mensaje": "API del Centro Terapéutico funcionando ✅"}


# ==========================================
# Rutas — Autenticación
# ==========================================
@app.post("/auth/login", response_model=LoginResponse)
def login(datos: LoginRequest):
    if ingresar_sistema(datos.correo, datos.password):
        return LoginResponse(success=True, message="Ingreso exitoso")
    raise HTTPException(status_code=401, detail="Credenciales inválidas o usuario inactivo")


# ==========================================
# Rutas — Paciente
# ==========================================
@app.post("/pacientes/registrar", response_model=PacienteResponse)
def registrar_paciente_endpoint(datos: PacienteRegistrarRequest):
    id_paciente = registrar_paciente(
        datos.nombre,
        datos.apellido,
        datos.fecha_nacimiento.isoformat(),
        datos.diagnostico,
        datos.motivo_consulta,
        datos.telefono,
        datos.nombre_apoderado,
        datos.correo,
    )

    if id_paciente == -1:
        raise HTTPException(status_code=500, detail="No se pudo registrar el paciente")

    return PacienteResponse(
        success=True,
        id_paciente=id_paciente,
        message="Paciente registrado correctamente",
    )


@app.put("/pacientes/actualizar", response_model=PacienteResponse)
def actualizar_paciente_endpoint(datos: PacienteActualizarRequest):
    resultado = actualizar_paciente(
        datos.id_paciente,
        datos.nombre,
        datos.apellido,
        datos.fecha_nacimiento.isoformat(),
        datos.diagnostico,
        datos.motivo_consulta,
        datos.telefono,
        datos.nombre_apoderado,
        datos.correo,
    )

    if resultado == -1:
        raise HTTPException(status_code=500, detail="Error al actualizar el paciente")
    if resultado == 0:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    return PacienteResponse(
        success=True,
        message="Paciente actualizado correctamente",
    )


@app.delete("/pacientes/eliminar/{id_paciente}", response_model=PacienteResponse)
def eliminar_paciente_endpoint(id_paciente: int):
    resultado = eliminar_paciente(id_paciente)

    if resultado == -1:
        raise HTTPException(status_code=500, detail="Error al eliminar el paciente")
    if resultado == 0:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    return PacienteResponse(
        success=True,
        message="Paciente eliminado (estado = FALSE) correctamente",
    )


@app.put("/pacientes/activar/{id_paciente}", response_model=PacienteResponse)
def activar_paciente_endpoint(id_paciente: int):
    resultado = activar_paciente(id_paciente)

    if resultado == -1:
        raise HTTPException(status_code=500, detail="Error al activar el paciente")
    if resultado == 0:
        raise HTTPException(
            status_code=404,
            detail="Paciente no encontrado o ya está activo",
        )

    return PacienteResponse(
        success=True,
        message="Paciente activado (estado = TRUE) correctamente",
    )


@app.get("/pacientes")
def listar_paciente_endpoint():
    resultados = listar_paciente()
    return {"success": True, "data": resultados}

@app.get("/pacientes/{id_paciente}")     # 👈 nueva ruta al final
def consultar_paciente_endpoint(id_paciente: int):
    paciente = consultar_paciente(id_paciente)
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {"success": True, "data": paciente}

@app.get("/version")
def version():
    return {"version": "cors-fix-v2", "origins": ["http://localhost:5173", "http://localhost:3000", "https://motivakid.onrender.com"]}

# ==========================================
# Ejecución local
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)