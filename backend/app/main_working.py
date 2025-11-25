"""
Aplicación principal FastAPI - Versión simplificada
"""
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import subprocess

app = FastAPI(
    title="Render_QM API",
    description="Sistema de gestión de colas de render distribuido",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router para configuración
config_router = APIRouter()

@config_router.post("/blender/auto-detect")
async def auto_detect_blender():
    """Auto-detectar instalaciones de Blender en el sistema Windows"""
    
    blender_installations = []
    
    # Rutas comunes de Blender en Windows
    common_paths = [
        r"C:\Program Files\Blender Foundation",
        r"C:\Program Files (x86)\Blender Foundation",
        fr"C:\Users\{os.getenv('USERNAME')}\AppData\Local\Programs\Blender Foundation",
        r"C:\Program Files\Steam\steamapps\common\Blender",
        r"D:\Program Files\Blender Foundation",
        r"E:\Program Files\Blender Foundation",
    ]
    
    def verify_blender(blender_path):
        try:
            result = subprocess.run(
                [blender_path, "--version"], 
                capture_output=True, 
                text=True, 
                timeout=15,
                shell=False
            )
            
            if result.returncode == 0 and "Blender" in result.stdout:
                version_line = result.stdout.split('\n')[0]
                return {
                    "path": blender_path,
                    "version": version_line.strip(),
                    "valid": True
                }
        except Exception:
            pass
        return None
    
    # Buscar en rutas comunes
    for base_path in common_paths:
        if os.path.exists(base_path):
            try:
                for root, dirs, files in os.walk(base_path):
                    if "blender.exe" in files:
                        blender_path = os.path.join(root, "blender.exe")
                        blender_info = verify_blender(blender_path)
                        
                        if blender_info:
                            if not any(inst["path"] == blender_info["path"] for inst in blender_installations):
                                blender_installations.append(blender_info)
            except Exception:
                continue
    
    if not blender_installations:
        return {
            "success": False,
            "message": "No se encontraron instalaciones válidas de Blender",
            "detected_versions": [],
            "suggestions": [
                "Verifica que Blender esté instalado correctamente",
                "Configura manualmente la ruta de Blender"
            ]
        }
    
    return {
        "success": True,
        "message": f"Se encontraron {len(blender_installations)} instalación(es) de Blender",
        "detected_versions": blender_installations
    }

# Incluir router
app.include_router(config_router, prefix="/api/v1/config", tags=["config"])

@app.get("/")
async def root():
    return {
        "message": "Render_QM API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }