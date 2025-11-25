from fastapi import APIRouter, HTTPException
import os
import subprocess
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel
import platform # Necesario para una verificación de ruta más robusta

# 🚨 CAMBIO CRÍTICO: Importar el servicio dedicado de Blender
from app.services.blender_service import blender_service 

router = APIRouter()

class BlenderTestRequest(BaseModel):
    blender_path: str

# ----------------- ENDPOINT DE AUTO-DETECCIÓN CORREGIDO -----------------
@router.post("/blender/auto-detect")
async def auto_detect_blender():
    """
    Auto-detectar instalaciones de Blender en el sistema.
    Ahora utiliza el servicio dedicado para una detección robusta y devuelve el formato esperado.
    """
    try:
        # 🚨 CAMBIO CRÍTICO: Llamar a la lógica centralizada del servicio
        blender_installations = blender_service.scan_for_blender()

        # Filtramos las instalaciones válidas para el mensaje
        valid_installations = [
            i for i in blender_installations 
            if i.get("valid", False) or i.get("working", False)
        ]

        # Devolver la respuesta en el formato que espera el frontend
        return {
            "success": True,
            "message": f"Se encontraron {len(valid_installations)} instalación(es) de Blender válidas",
            "installations": blender_installations # Devolvemos la lista completa
        }

    except Exception as e:
        print(f"Error durante la auto-detección: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error durante la auto-detección: {str(e)}")

# ----------------- Endpoint de testeo de ruta (Mantenido del original) -----------------
@router.post("/blender/test-path")
async def test_blender_path(request: BlenderTestRequest):
    """Verificar si la ruta de Blender proporcionada es válida."""
    blender_path = request.blender_path
    
    if not os.path.exists(blender_path):
        raise HTTPException(status_code=400, detail="La ruta de Blender no existe")
        
    is_windows = platform.system() == "Windows"
    
    # Verificación de que apunta al ejecutable
    if is_windows and not blender_path.lower().endswith("blender.exe"):
        raise HTTPException(status_code=400, detail="La ruta debe apuntar al ejecutable blender.exe")
    elif not is_windows and Path(blender_path).is_dir():
         raise HTTPException(status_code=400, detail="La ruta debe apuntar al ejecutable de Blender, no a un directorio.")
    
    try:
        print(f"Probando Blender en: {blender_path}")
        result = subprocess.run(
            [blender_path, "--version"], 
            capture_output=True, 
            text=True, 
            timeout=15
        )
        
        if result.returncode == 0 and "Blender" in result.stdout:
            version_line = result.stdout.split('\n')[0]
            return {
                "success": True,
                "message": "Configuración de Blender válida",
                "path": blender_path,
                "version": version_line.strip()
            }
        else:
            raise HTTPException(status_code=400, detail=f"El ejecutable no es una instalación válida de Blender. Salida: {result.stdout}")
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout al verificar Blender")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar Blender: {str(e)}")

# ----------------- Endpoint de estado (Mantenido del original) -----------------
@router.get("/blender/status")
async def get_blender_status():
    """Obtener el estado actual de la configuración de Blender (simulado)."""
    
    # Esta función requiere lógica de estado guardada, se mantiene la respuesta por defecto
    return {
        "is_configured": False,
        "path": None,
        "version": None,
        "message": "Blender no configurado. Por favor, auto-detecta o ingresa la ruta."
    }

# ----------------- Endpoint de guardado (Inferencia del uso del frontend) -----------------
@router.post("/blender")
async def save_blender_config(request: BlenderTestRequest):
    """Guardar la configuración de Blender y verificar la ruta"""

    # 1. Verificar la ruta
    try:
        verification_result = await test_blender_path(request)
    except HTTPException as e:
        raise e
        
    # 2. Si es válida, guardar (simulado)
    if verification_result["success"]:
        # Aquí se implementaría la lógica de guardar en DB/archivo
        
        return {
            "success": True,
            "message": "✓ Configuración de Blender guardada y verificada",
            "path": verification_result["path"],
            "version": verification_result["version"]
        }
    else:
        raise HTTPException(status_code=500, detail="Fallo inesperado al guardar la configuración.")