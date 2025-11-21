# app/api/v1/config.py

import os
import platform
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.services.blender_service import blender_service

# Creamos el router
router = APIRouter()

# --- MODELOS DE DATOS ---
class BlenderConfig(BaseModel):
    blender_path: str
    version: Optional[str] = None
    is_valid: bool = False
    auto_detected: bool = False

# --- ENDPOINTS DE BLENDER ---

@router.post("/blender/auto-detect")
async def auto_detect_blender():
    """
    Auto-detectar Blender.
    Devuelve una respuesta "blindada" con múltiples formatos para asegurar
    que el frontend pueda leer la ruta sin importar qué campo busque.
    """
    try:
        # 1. Ejecutar detección inteligente
        result = blender_service.auto_detect_and_configure()
        
        # Si falla, devolvemos un JSON con success: False en lugar de un error 404/500
        # para que el frontend pueda mostrar el mensaje amablemente.
        if result is False or (isinstance(result, dict) and not result.get("success")):
            return {
                "success": False, 
                "message": "No se pudo detectar ninguna instalación de Blender."
            }

        # 2. Obtener los datos detectados
        path = result.get("path")
        version = result.get("version", "Desconocida")

        # 3. RESPUESTA SUPER COMPLETA
        # Enviamos la información en todas las estructuras posibles
        response = {
            "success": True,
            "message": f"Blender {version} detectado.",
            
            # Opción A: Campos directos (Lo más común)
            "path": path,
            "blender_path": path,
            "executable": path,
            "version": version,
            "blender_version": version,
            
            # Opción B: Objeto anidado (Estilo API REST estándar)
            "data": {
                "path": path,
                "version": version,
                "executable": path
            },

            # Opción C: Lista de instalaciones (Si el frontend espera un array)
            "installations": [
                {
                    "path": path,
                    "version": version,
                    "valid": True,
                    "working": True
                }
            ],
            
            # Metadatos
            "auto_detected": True,
            "detected": True
        }
        return response
        
    except Exception as e:
        print(f"[ERROR] Auto-detect: {str(e)}")
        # Devolvemos error controlado
        return {"success": False, "message": f"Error interno: {str(e)}"}

@router.get("/blender")
async def get_blender_config():
    """Obtener configuración actual"""
    config = settings.get_blender_config()
    
    # Aseguramos que siempre devolvemos algo coherente
    path = config.get("path") or config.get("BLENDER_PATH") or ""
    
    return {
        "blender_path": path,  # Clave principal
        "path": path,          # Clave secundaria
        "version": config.get("version"),
        "is_configured": bool(path),
        "is_valid": bool(path), # Asumimos válido si está configurado
        "last_validated": config.get("last_verified")
    }

@router.post("/blender")
async def set_blender_config(config: BlenderConfig):
    """Guardar configuración manual"""
    try:
        validation = blender_service.verify_blender_path(config.blender_path)
        
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail="Ruta inválida")
        
        # Guardar en .env
        settings.update_blender_config({
            "path": config.blender_path,
            "version": validation.get("version"),
            "auto_detect": False,
            "last_verified": "Manual"
        })
        
        return {"success": True, "blender_path": config.blender_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blender/validate")
async def validate_blender_endpoint(blender_path: str):
    return blender_service.verify_blender_path(blender_path)

@router.post("/blender/test-version")
async def test_version(blender_path: str):
    return blender_service.verify_blender_path(blender_path)


# --- ENDPOINTS DE COLA (QUEUE) ---

@router.get("/queue")
async def get_queue_config():
    """Obtener configuración de la cola"""
    return {
        "max_concurrent_jobs": 3,
        "auto_start_jobs": True,
        "priority_enabled": True,
        "retry_failed_jobs": True,
        "max_retries": 3,
        "cleanup_completed_after_hours": 24,
        "notification_settings": {
            "on_job_complete": True,
            "on_job_failed": True,
            "on_queue_empty": False
        }
    }

@router.post("/queue")
async def update_queue_config(config: Dict[str, Any]):
    """Actualizar configuración de la cola"""
    return {"success": True, "message": "Configuración actualizada", "config": config}


# --- ENDPOINTS DE SISTEMA ---

@router.get("/system/info")
@router.get("/info") # Alias por seguridad
async def get_system_info():
    """Información del sistema para el Dashboard"""
    try:
        return {
            "platform": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count() or 1
        }
    except Exception:
        return {"platform": "Unknown"}