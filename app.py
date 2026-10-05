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

from database.especialidad import (
    registrar_especialidad,
    actualizar_especialidad,
    eliminar_especialidad,
    activar_especialidad,
    listar_especialidad,
    consultar_especialidad,
)

from database.terapeuta import (
    registrar_terapeuta,
    actualizar_terapeuta,
    eliminar_terapeuta,
    activar_terapeuta,
    listar_terapeuta,
    consultar_terapeuta,
)

app = FastAPI(title="API Centro Terapéutico")

# CORS para permitir que React (Vite/Next) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://motivakid.onrender.com",],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
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
# Modelos Pydantic — Especialidad
# ==========================================
class EspecialidadRegistrarRequest(BaseModel):
    nombre: str


class EspecialidadActualizarRequest(BaseModel):
    id_especialidad: int
    nombre: str


class EspecialidadResponse(BaseModel):
    success: bool
    message: str
    id_especialidad: int | None = None

# ==========================================
# Modelos Pydantic — Terapeuta
# ==========================================
class TerapeutaRegistrarRequest(BaseModel):
    nombres: str
    apellidos: str
    id_especialidad: int


class TerapeutaActualizarRequest(BaseModel):
    id_terapeuta: int
    nombres: str
    apellidos: str
    id_especialidad: int


class TerapeutaResponse(BaseModel):
    success: bool
    message: str
    id_terapeuta: int | None = None

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

# ==========================================
# Rutas — Especialidad
# ==========================================
@app.post("/especialidades/registrar", response_model=EspecialidadResponse)
def registrar_especialidad_endpoint(datos: EspecialidadRegistrarRequest):
    id_especialidad = registrar_especialidad(datos.nombre)

    if id_especialidad == -1:
        raise HTTPException(status_code=500, detail="No se pudo registrar la especialidad")

    return EspecialidadResponse(
        success=True,
        id_especialidad=id_especialidad,
        message="Especialidad registrada correctamente",
    )


@app.put("/especialidades/actualizar", response_model=EspecialidadResponse)
def actualizar_especialidad_endpoint(datos: EspecialidadActualizarRequest):
    resultado = actualizar_especialidad(datos.id_especialidad, datos.nombre)

    if resultado == -1:
        raise HTTPException(status_code=500, detail="Error al actualizar la especialidad")
    if resultado == 0:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")

    return EspecialidadResponse(
        success=True,
        message="Especialidad actualizada correctamente",
    )


@app.delete("/especialidades/eliminar/{id_especialidad}", response_model=EspecialidadResponse)
def eliminar_especialidad_endpoint(id_especialidad: int):
    resultado = eliminar_especialidad(id_especialidad)

    if resultado == -1:
        raise HTTPException(status_code=500, detail="Error al eliminar la especialidad")
    if resultado == 0:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")

    return EspecialidadResponse(
        success=True,
        message="Especialidad eliminada (estado = FALSE) correctamente",
    )


@app.put("/especialidades/activar/{id_especialidad}", response_model=EspecialidadResponse)
def activar_especialidad_endpoint(id_especialidad: int):
    resultado = activar_especialidad(id_especialidad)

    if resultado == -1:
        raise HTTPException(status_code=500, detail="Error al activar la especialidad")
    if resultado == 0:
        raise HTTPException(
            status_code=404,
            detail="Especialidad no encontrada o ya está activa",
        )

    return EspecialidadResponse(
        success=True,
        message="Especialidad activada (estado = TRUE) correctamente",
    )


@app.get("/especialidades")
def listar_especialidad_endpoint():
    resultados = listar_especialidad()
    return {"success": True, "data": resultados}


@app.get("/especialidades/{id_especialidad}")
def consultar_especialidad_endpoint(id_especialidad: int):
    especialidad = consultar_especialidad(id_especialidad)
    if especialidad is None:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")
    return {"success": True, "data": especialidad}

# ==========================================
# Rutas — Terapeuta
# ==========================================
@app.post("/terapeutas/registrar", response_model=TerapeutaResponse)
def registrar_terapeuta_endpoint(datos: TerapeutaRegistrarRequest):
    id_terapeuta = registrar_terapeuta(
        datos.nombres,
        datos.apellidos,
        datos.id_especialidad,
    )

    if id_terapeuta == -1:
        raise HTTPException(status_code=500, detail="No se pudo registrar el terapeuta")

    return TerapeutaResponse(
        success=True,
        id_terapeuta=id_terapeuta,
        message="Terapeuta registrado correctamente",
    )


@app.put("/terapeutas/actualizar", response_model=TerapeutaResponse)
def actualizar_terapeuta_endpoint(datos: TerapeutaActualizarRequest):
    resultado = actualizar_terapeuta(
        datos.id_terapeuta,
        datos.nombres,
        datos.apellidos,
        datos.id_especialidad,
    )

    if resultado == -1:
        raise HTTPException(status_code=500, detail="Error al actualizar el terapeuta")
    if resultado == 0:
        raise HTTPException(status_code=404, detail="Terapeuta no encontrado")

    return TerapeutaResponse(
        success=True,
        message="Terapeuta actualizado correctamente",
    )


@app.delete("/terapeutas/eliminar/{id_terapeuta}", response_model=TerapeutaResponse)
def eliminar_terapeuta_endpoint(id_terapeuta: int):
    resultado = eliminar_terapeuta(id_terapeuta)

    if resultado == -1:
        raise HTTPException(status_code=500, detail="Error al eliminar el terapeuta")
    if resultado == 0:
        raise HTTPException(status_code=404, detail="Terapeuta no encontrado")

    return TerapeutaResponse(
        success=True,
        message="Terapeuta eliminado (estado = FALSE) correctamente",
    )


@app.put("/terapeutas/activar/{id_terapeuta}", response_model=TerapeutaResponse)
def activar_terapeuta_endpoint(id_terapeuta: int):
    resultado = activar_terapeuta(id_terapeuta)

    if resultado == -1:
        raise HTTPException(status_code=500, detail="Error al activar el terapeuta")
    if resultado == 0:
        raise HTTPException(
            status_code=404,
            detail="Terapeuta no encontrado o ya está activo",
        )

    return TerapeutaResponse(
        success=True,
        message="Terapeuta activado (estado = TRUE) correctamente",
    )


@app.get("/terapeutas")
def listar_terapeuta_endpoint():
    resultados = listar_terapeuta()
    return {"success": True, "data": resultados}


@app.get("/terapeutas/{id_terapeuta}")
def consultar_terapeuta_endpoint(id_terapeuta: int):
    terapeuta = consultar_terapeuta(id_terapeuta)
    if terapeuta is None:
        raise HTTPException(status_code=404, detail="Terapeuta no encontrado")
    return {"success": True, "data": terapeuta}

@app.get("/version")
def version():
    return {"version": "cors-fix-v2", "origins": ["http://localhost:5173", "http://localhost:3000", "https://motivakid.onrender.com"]}

# ==========================================
# Ejecución local
# ==========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)