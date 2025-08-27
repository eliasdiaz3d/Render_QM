# Agregar estas importaciones al inicio del archivo settings.py (si no están ya)
import os
import subprocess
import winreg
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel

# Modelo para la respuesta de test de Blender
class BlenderTestRequest(BaseModel):
    blender_path: str

# Agregar estos endpoints al router existente en settings.py

@router.post("/config/blender/auto-detect")
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
    
    def verify_blender(blender_path: str) -> Dict:
        """Verificar si un ejecutable de Blender es válido"""
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
        except Exception as e:
            print(f"Error verificando {blender_path}: {str(e)}")
        
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
                            # Evitar duplicados
                            if not any(inst["path"] == blender_info["path"] for inst in blender_installations):
                                blender_installations.append(blender_info)
            except Exception as e:
                print(f"Error buscando en {base_path}: {str(e)}")
                continue
    
    # Buscar en el PATH del sistema
    try:
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        for path_dir in path_dirs:
            blender_path = os.path.join(path_dir, "blender.exe")
            if os.path.exists(blender_path):
                blender_info = verify_blender(blender_path)
                if blender_info:
                    if not any(inst["path"] == blender_info["path"] for inst in blender_installations):
                        blender_installations.append(blender_info)
    except Exception as e:
        print(f"Error buscando en PATH: {str(e)}")
    
    if not blender_installations:
        return {
            "success": False,
            "message": "No se encontraron instalaciones válidas de Blender",
            "installations": [],
            "suggestions": [
                "Verifica que Blender esté instalado correctamente",
                "Asegúrate de que Blender esté en una de las rutas estándar",
                "Configura manualmente la ruta de Blender"
            ]
        }
    
    return {
        "success": True,
        "message": f"Se encontraron {len(blender_installations)} instalación(es) de Blender",
        "installations": blender_installations
    }

@router.post("/config/blender/test")
async def test_blender_path(request: BlenderTestRequest):
    """Probar una ruta específica de Blender"""
    
    blender_path = request.blender_path.strip()
    
    if not os.path.exists(blender_path):
        raise HTTPException(status_code=404, detail="La ruta especificada no existe")
    
    if not blender_path.lower().endswith("blender.exe"):
        raise HTTPException(status_code=400, detail="La ruta debe apuntar al ejecutable blender.exe")
    
    try:
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
            raise HTTPException(status_code=400, detail="El ejecutable no es una instalación válida de Blender")
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout al verificar Blender")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar Blender: {str(e)}")

@router.post("/config/blender/save")
async def save_blender_config(request: BlenderTestRequest):
    """Guardar configuración de Blender"""
    
    # Primero verificar que la ruta sea válida
    test_result = await test_blender_path(request)
    
    if test_result["success"]:
        # Aquí deberías guardar la configuración en tu base de datos o archivo de config
        # Por ejemplo, en un archivo JSON o en la base de datos
        
        # Ejemplo temporal guardando en un archivo JSON
        config_data = {
            "blender_path": request.blender_path,
            "version": test_result["version"],
            "last_updated": "2024-12-19"  # Usar datetime.now() en producción
        }
        
        return {
            "success": True,
            "message": "Configuración de Blender guardada correctamente",
            "config": config_data
        }
    
    return test_result