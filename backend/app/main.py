# backend/app/main.py

import os
import platform
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

# Importamos los routers existentes
from app.api.v1 import jobs, nodes, queue, auth, notifications, config

app = FastAPI(
    title="Render Queue Manager",
    description="API para gestión de granja de render",
    version="1.0.0"
)

# --- CONFIGURACIÓN CORS ---
# Esto permite que el frontend (Vue.js) se comunique con el backend sin bloqueos
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"  # Permitir todo en modo desarrollo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER PRINCIPAL (API V1) ---
api_router = APIRouter()

# 1. Incluimos los routers funcionales
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
api_router.include_router(queue.router, prefix="/queue", tags=["queue"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(config.router, prefix="/config", tags=["config"])


# 2. Incluimos endpoints de soporte para evitar errores 404 en el Frontend
# Estos endpoints simulan datos del sistema y estadísticas para que el Dashboard no falle

system_router = APIRouter()
stats_router = APIRouter()

@system_router.get("/info")
def get_system_info():
    """Endpoint para evitar el error 404 en /api/v1/system/info"""
    return {
        "platform": platform.system(),
        "node": platform.node(),
        "python_version": platform.python_version(),
        "processor": platform.processor() or "Generic",
        "status": "online",
        "cpu_count": os.cpu_count() or 1,
        "memory_usage": "N/A" # Simulado
    }

@stats_router.get("/dashboard")
def get_dashboard_stats():
    """Endpoint para evitar el error 404 en /api/v1/stats/dashboard"""
    return {
        "active_nodes": 1,
        "total_jobs": 0,
        "completed_jobs": 0,
        "failed_jobs": 0,
        "efficiency": 100,
        "total_render_time": "0h",
        "queue_status": "idle",
        "last_job": None
    }

api_router.include_router(system_router, prefix="/system", tags=["system"])
api_router.include_router(stats_router, prefix="/stats", tags=["stats"])


# --- REGISTRO FINAL DE RUTAS ---
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    """Endpoint básico para verificar que el servidor está vivo"""
    return {"status": "ok", "app": "Render Queue Manager", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    # Configuración para ejecutar directamente con python main.py
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)