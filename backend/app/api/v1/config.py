"""
Endpoints de configuración para Blender y sistema
"""
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

class BlenderConfig(BaseModel):
    """Modelo para configuración de Blender"""
    blender_path: str
    version: Optional[str] = None
    is_valid: bool = False
    auto_detected: bool = False

class SystemInfo(BaseModel):
    """Información del sistema"""
    platform: str
    architecture: str
    python_version: str
    blender_installations: List[Dict[str, Any]]

# Rutas comunes donde Blender suele estar instalado por plataforma
BLENDER_SEARCH_PATHS = {
    "Windows": [
        "C:/Program Files/Blender Foundation",
        "C:/Program Files (x86)/Blender Foundation", 
        "C:/Users/{username}/AppData/Local/Programs/Blender Foundation",
        "C:/blender",
        "D:/Program Files/Blender Foundation",
        "E:/Program Files/Blender Foundation",
    ],
    "Linux": [
        "/usr/bin",
        "/usr/local/bin",
        "/opt/blender",
        "/snap/blender/current/bin",
        "/home/{username}/.local/bin",
        "/home/{username}/blender",
    ],
    "Darwin": [  # macOS
        "/Applications",
        "/Applications/Blender.app/Contents/MacOS",
        "/usr/local/bin",
        "/opt/homebrew/bin",
        "/Users/{username}/Applications",
    ]
}

def get_blender_version(blender_path: str) -> Optional[str]:
    """Obtener versión de Blender ejecutando el comando --version"""
    try:
        # Configuración específica por plataforma
        current_platform = platform.system()
        
        cmd_args = [blender_path, "--version"]
        
        # Configuración para Windows
        if current_platform == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=15,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            # Linux/macOS
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=15
            )
        
        print(f"[DEBUG] Ejecutando: {' '.join(cmd_args)}")
        print(f"[DEBUG] Return code: {result.returncode}")
        print(f"[DEBUG] STDOUT: {result.stdout[:200] if result.stdout else 'None'}")
        print(f"[DEBUG] STDERR: {result.stderr[:200] if result.stderr else 'None'}")
        
        if result.returncode == 0 and result.stdout:
            output = result.stdout.strip()
            lines = output.split('\n')
            
            # Múltiples estrategias para extraer la versión
            version_patterns = [
                # Patrón 1: "Blender 3.6.2"
                r'Blender\s+(\d+\.\d+(?:\.\d+)?)',
                # Patrón 2: "version 3.6.2"
                r'version\s+(\d+\.\d+(?:\.\d+)?)',
                # Patrón 3: Solo números con puntos
                r'(\d+\.\d+\.\d+)',
                # Patrón 4: Versión al inicio de línea
                r'^(\d+\.\d+(?:\.\d+)?)'
            ]
            
            # Buscar en todas las líneas
            for line in lines:
                for pattern in version_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        version = match.group(1)
                        print(f"[DEBUG] Versión encontrada: {version}")
                        return version
            
            # Si no encuentra patrones específicos, intentar primera línea
            if lines and lines[0].strip():
                first_line = lines[0].strip()
                print(f"[DEBUG] Usando primera línea como versión: {first_line}")
                return first_line
                
        elif result.returncode != 0:
            print(f"[DEBUG] Error ejecutando Blender: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"[DEBUG] Timeout ejecutando {blender_path}")
    except FileNotFoundError:
        print(f"[DEBUG] Archivo no encontrado: {blender_path}")
    except Exception as e:
        print(f"[DEBUG] Error general: {str(e)}")
    
    return None

def find_blender_executable(search_path: str) -> Optional[Dict[str, str]]:
    """Buscar ejecutable de Blender en una ruta específica - versión con debug"""
    try:
        path = Path(search_path)
        print(f"[DEBUG] Buscando en: {path}")
        
        if not path.exists():
            print(f"[DEBUG] Ruta no existe: {path}")
            return None
        
        # Nombres de ejecutable por plataforma
        executable_names = {
            "Windows": ["blender.exe", "Blender.exe"],
            "Linux": ["blender", "Blender"],
            "Darwin": ["blender", "Blender"]
        }
        
        current_platform = platform.system()
        exe_names = executable_names.get(current_platform, ["blender"])
        
        print(f"[DEBUG] Buscando ejecutables: {exe_names}")
        
        # Buscar recursivamente pero limitar profundidad para evitar lentitud
        for exe_name in exe_names:
            # Buscar directo en la ruta
            direct_path = path / exe_name
            if direct_path.is_file() and os.access(direct_path, os.X_OK):
                print(f"[DEBUG] Encontrado directo: {direct_path}")
                version = get_blender_version(str(direct_path))
                if version:
                    return {
                        "path": str(direct_path),
                        "version": version,
                        "directory": str(direct_path.parent)
                    }
            
            # Buscar recursivamente (máximo 3 niveles)
            for depth in range(3):
                pattern = "/".join(["*"] * depth + [exe_name])
                for blender_path in path.glob(pattern):
                    if blender_path.is_file() and os.access(blender_path, os.X_OK):
                        print(f"[DEBUG] Encontrado recursivo: {blender_path}")
                        version = get_blender_version(str(blender_path))
                        if version:
                            return {
                                "path": str(blender_path),
                                "version": version,
                                "directory": str(blender_path.parent)
                            }
                        
    except Exception as e:
        print(f"[DEBUG] Error en búsqueda: {str(e)}")
    
    return None

def validate_blender_path(blender_path: str) -> Dict[str, Any]:
    """Validar que una ruta de Blender es válida"""
    try:
        path = Path(blender_path)
        
        if not path.exists():
            return {"is_valid": False, "error": "El archivo no existe"}
        
        if not path.is_file():
            return {"is_valid": False, "error": "La ruta no apunta a un archivo"}
        
        if not os.access(path, os.X_OK):
            return {"is_valid": False, "error": "El archivo no es ejecutable"}
        
        # Intentar obtener versión
        version = get_blender_version(blender_path)
        if not version:
            return {"is_valid": False, "error": "No se pudo verificar que sea Blender"}
        
        return {
            "is_valid": True,
            "version": version,
            "path": blender_path,
            "size_mb": round(path.stat().st_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        return {"is_valid": False, "error": f"Error validando: {str(e)}"}

@router.post("/blender/auto-detect")
async def auto_detect_blender():
    """Auto-detectar instalaciones de Blender en el sistema - versión con debug"""
    try:
        current_platform = platform.system()
        search_paths = BLENDER_SEARCH_PATHS.get(current_platform, [])
        
        print(f"[DEBUG] Plataforma: {current_platform}")
        print(f"[DEBUG] Rutas base de búsqueda: {search_paths}")
        
        # Reemplazar {username} con el nombre de usuario actual
        username = os.getenv("USER") or os.getenv("USERNAME") or "user"
        search_paths = [path.format(username=username) for path in search_paths]
        
        print(f"[DEBUG] Rutas expandidas: {search_paths}")
        
        # Buscar también en PATH
        blender_in_path = shutil.which("blender")
        if blender_in_path:
            print(f"[DEBUG] Blender encontrado en PATH: {blender_in_path}")
            search_paths.append(os.path.dirname(blender_in_path))
        else:
            print("[DEBUG] Blender no encontrado en PATH")
        
        found_installations = []
        
        # Buscar en cada ruta
        for search_path in search_paths:
            print(f"\n[DEBUG] === Buscando en: {search_path} ===")
            installation = find_blender_executable(search_path)
            if installation:
                print(f"[DEBUG] ¡Instalación encontrada!: {installation}")
                # Evitar duplicados
                if not any(inst["path"] == installation["path"] for inst in found_installations):
                    found_installations.append(installation)
                else:
                    print(f"[DEBUG] Duplicado ignorado: {installation['path']}")
        
        # Ordenar por versión (más reciente primero)
        try:
            def version_key(inst):
                version = inst.get("version", "0")
                # Extraer solo números para ordenamiento
                numbers = re.findall(r'\d+', version)
                return tuple(int(n) for n in numbers) if numbers else (0,)
            
            found_installations.sort(key=version_key, reverse=True)
        except Exception as e:
            print(f"[DEBUG] Error ordenando versiones: {e}")
        
        print(f"\n[DEBUG] === RESUMEN ===")
        print(f"Instalaciones encontradas: {len(found_installations)}")
        for inst in found_installations:
            print(f"  - {inst['path']} (v{inst['version']})")
        
        return {
            "success": True,
            "platform": current_platform,
            "searched_paths": search_paths,
            "installations_found": len(found_installations),
            "installations": found_installations,
            "recommended": found_installations[0] if found_installations else None,
            "debug_info": {
                "username": username,
                "blender_in_path": blender_in_path,
                "platform_paths": BLENDER_SEARCH_PATHS.get(current_platform, [])
            }
        }
        
    except Exception as e:
        print(f"[DEBUG] Error general en auto-detect: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante auto-detección: {str(e)}"
        )

@router.post("/blender/test-version")
async def test_blender_version(blender_path: str):
    """Endpoint para probar manualmente la detección de versión de un Blender específico"""
    try:
        print(f"[DEBUG] Probando versión de: {blender_path}")
        
        if not os.path.exists(blender_path):
            return {"error": "El archivo no existe", "path": blender_path}
        
        version = get_blender_version(blender_path)
        validation = validate_blender_path(blender_path)
        
        return {
            "path": blender_path,
            "version_detected": version,
            "validation": validation,
            "file_exists": os.path.exists(blender_path),
            "is_executable": os.access(blender_path, os.X_OK) if os.path.exists(blender_path) else False
        }
        
    except Exception as e:
        print(f"[DEBUG] Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {"error": str(e), "path": blender_path}

@router.get("/blender")
async def get_blender_config():
    """Obtener configuración actual de Blender"""
    # Esta sería la configuración guardada, por ahora retornamos una por defecto
    return {
        "blender_path": "",
        "version": None,
        "is_configured": False,
        "is_valid": False,
        "last_validated": None
    }

@router.post("/blender")
async def set_blender_config(config: BlenderConfig):
    """Configurar ruta de Blender"""
    try:
        validation = validate_blender_path(config.blender_path)
        
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ruta de Blender inválida: {validation['error']}"
            )
        
        # Aquí guardarías la configuración en tu sistema de persistencia
        # Por ahora solo retornamos confirmación
        
        return {
            "success": True,
            "detected": len(found_installations) > 0,
            "available": True,
            "configured": len(found_installations) > 0,
            "blender_path": found_installations[0]["path"] if found_installations else "",
            "blender_version": found_installations[0]["version"] if found_installations else "",
            "platform": current_platform,
            "installations_found": len(found_installations),
            "installations": found_installations,
            "recommended": found_installations[0] if found_installations else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error guardando configuración: {str(e)}"
        )

@router.post("/blender/validate")
async def validate_blender_config(blender_path: str):
    """Validar una ruta específica de Blender"""
    try:
        validation = validate_blender_path(blender_path)
        return validation
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validando Blender: {str(e)}"
        )

@router.get("/queue")
async def get_queue_config():
    """Obtener configuración de cola"""
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
    """Actualizar configuración de cola"""
    try:
        # Validar configuración básica
        allowed_keys = {
            "max_concurrent_jobs", "auto_start_jobs", "priority_enabled",
            "retry_failed_jobs", "max_retries", "cleanup_completed_after_hours",
            "notification_settings"
        }
        
        invalid_keys = set(config.keys()) - allowed_keys
        if invalid_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Claves de configuración inválidas: {invalid_keys}"
            )
        
        # Aquí guardarías la configuración
        # Por ahora solo retornamos confirmación
        
        return {
            "success": True,
            "message": "Configuración de cola actualizada",
            "config": config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando configuración: {str(e)}"
        )