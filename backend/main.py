# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from app.services.notification_service import notification_service
import uvicorn
import os
import uuid
import subprocess
import json
import shutil
import hashlib
import tempfile
import asyncio
import platform
import psutil
import sys
import re
import glob
import zipfile
from io import BytesIO
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from pathlib import Path

# Crear instancia de FastAPI
app = FastAPI(
    title="Render Queue Manager API",
    description="API completa para gestión de colas de render de Blender",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de directorios
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "renders"
TEMP_DIR = BASE_DIR / "temp"
CONFIG_FILE = BASE_DIR / "config.json"

# Crear directorios si no existen
for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Servir archivos estáticos
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/renders", StaticFiles(directory=str(OUTPUT_DIR)), name="renders")

# ==================== MODELOS ADICIONALES ====================

class QueueConfig(BaseModel):
    max_concurrent_jobs: int = 2
    max_retries: int = 3
    default_priority: str = "normal"
    auto_cleanup_days: int = 30

class BlenderTestRequest(BaseModel):
    blender_path: str

class BlenderDetectedVersion(BaseModel):
    path: str
    version: Optional[str] = None
    valid: bool = False
    error: Optional[str] = None

class SystemInfo(BaseModel):
    os: str
    arch: str
    total_memory: str
    cpu_cores: int
    python_version: str
    disk_space: str

class UserInfo(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    is_authenticated: bool = True

class BlenderConfigUpdate(BaseModel):
    blender_path: str
    timeout: int = 300
    max_memory_mb: int = 4096
    auto_detect: bool = True

class NodeInfo(BaseModel):
    node_id: str
    node_name: str
    status: str  # idle, busy, offline, error
    last_seen: datetime
    system_stats: Dict
    active_jobs: int
    capabilities: Dict
    node_info: Dict

class JobAssignment(BaseModel):
    job_id: str
    node_id: str
    assigned_at: datetime
    status: str

class NodeRegistration(BaseModel):
    node_id: str
    node_name: str
    ip_address: str
    cpu_cores: int
    memory_gb: float
    platform: str
    blender_version: Optional[str] = None

class JobStatusUpdate(BaseModel):
    status: str
    error_message: Optional[str] = None
    progress: int = 0
    frames_rendered: int = 0

# ==================== CONFIGURACIÓN ====================

# Configuración por defecto
DEFAULT_CONFIG = {
    "blender": {
        "path": None,
        "auto_detect": True,
        "custom_path": None,
        "version": None,
        "last_verified": None
    },
    "render": {
        "default_engine": "CYCLES",
        "max_concurrent_jobs": 3,
        "auto_cleanup": True,
        "default_output_format": "PNG"
    },
    "system": {
        "check_updates": True,
        "telemetry": False
    }
}

def load_config():
    """Cargar configuración desde archivo"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge con configuración por defecto para nuevas opciones
                return merge_configs(DEFAULT_CONFIG, config)
        else:
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Guardar configuración a archivo"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")
        return False

def merge_configs(default, user):
    """Merge configuración del usuario con la por defecto"""
    result = default.copy()
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result

# Cargar configuración al inicio
app_config = load_config()

# ==================== MODELOS DE DATOS ====================

class JobStatus(BaseModel):
    id: str
    name: str
    status: str  # pending, processing, completed, failed, cancelled
    progress: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_path: str
    output_path: Optional[str] = None
    frames_total: int
    frames_rendered: int
    estimated_time: Optional[str] = None
    error_message: Optional[str] = None

class NodeStatus(BaseModel):
    id: str
    name: str
    ip: str
    status: str  # online, offline, rendering
    cpu_usage: int
    memory_usage: int
    current_job: Optional[str] = None
    last_seen: datetime

# ==================== GESTIÓN DE BLENDER ====================

def scan_for_blender() -> List[Dict]:
    """Escanear sistema buscando instalaciones de Blender"""
    
    found_installations = []
    system = platform.system()
    
    possible_paths = []
    
    if system == "Windows":
        base_paths = [
            r"C:\Program Files\Blender Foundation",
            r"C:\Program Files (x86)\Blender Foundation",
            r"C:\Blender",
            os.path.expanduser(r"~\AppData\Local\Programs\Blender Foundation"),
            os.path.expanduser(r"~\Desktop")
        ]
        
        for base_path in base_paths:
            if os.path.exists(base_path):
                try:
                    for item in os.listdir(base_path):
                        if "blender" in item.lower():
                            blender_exe = os.path.join(base_path, item, "blender.exe")
                            if os.path.exists(blender_exe):
                                possible_paths.append(blender_exe)
                except PermissionError:
                    continue
        
        # Rutas específicas adicionales
        specific_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender 4.4\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender 3.6\blender.exe"
        ]
        possible_paths.extend(specific_paths)
        
    elif system == "Darwin":  # macOS
        possible_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/usr/local/bin/blender",
            os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender")
        ]
    elif system == "Linux":
        possible_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender", 
            "/opt/blender/blender",
            "/snap/bin/blender",
            os.path.expanduser("~/blender/blender")
        ]
    
    # Verificar cada path
    for path in set(possible_paths):  # set para eliminar duplicados
        if os.path.exists(path):
            try:
                cmd = [path, "--version"]
                if platform.system() == "Windows":
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True, 
                        encoding="utf-8",
                        errors="replace",
                        timeout=10,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    version_line = result.stdout.strip().split('\n')[0] if result.stdout else ""
                    version = "Desconocida"
                    
                    # Extraer versión con regex
                    version_match = re.search(r'Blender (\d+\.\d+\.\d+)', version_line)
                    if version_match:
                        version = version_match.group(1)
                    
                    found_installations.append({
                        "path": path,
                        "version": version,
                        "full_version_info": version_line,
                        "working": True,
                        "valid": True,
                        "error": None
                    })
                else:
                    found_installations.append({
                        "path": path,
                        "version": "Error",
                        "working": False,
                        "valid": False,
                        "error": f"Error ejecutando: {result.stderr[:100]}"
                    })
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
                found_installations.append({
                    "path": path,
                    "version": "Error",
                    "working": False,
                    "valid": False,
                    "error": f"Error: {str(e)[:100]}"
                })
    
    return found_installations

def get_current_blender_path():
    """Obtener el path actual de Blender según configuración"""
    config = app_config["blender"]
    
    if config["custom_path"] and os.path.exists(config["custom_path"]):
        return config["custom_path"]
    elif config["path"] and os.path.exists(config["path"]):
        return config["path"]
    elif config["auto_detect"]:
        installations = scan_for_blender()
        if installations:
            working_installations = [inst for inst in installations if inst["working"]]
            if working_installations:
                return working_installations[0]["path"]
    
    return None

def verify_blender_path(path: str) -> Dict:
    """Verificar que un path de Blender funciona"""
    if not path or not os.path.exists(path):
        return {
            "valid": False,
            "error": "El archivo no existe",
            "version": None
        }
    
    try:
        # Verificar versión
        cmd = [path, "--version"]
        if platform.system() == "Windows":
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding="utf-8",
                errors="replace",
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return {
                "valid": False,
                "error": "El ejecutable no responde correctamente",
                "version": None
            }
        
        version_line = result.stdout.strip().split('\n')[0] if result.stdout else ""
        version = "Desconocida"
        
        # Extraer versión con regex
        version_match = re.search(r'Blender (\d+\.\d+\.\d+)', version_line)
        if version_match:
            version = version_match.group(1)
        
        # Verificar render básico
        test_cmd = [
            path, "--background", "--python-expr", 
            "import bpy; print('✅ Blender funcional')"
        ]
        
        if platform.system() == "Windows":
            test_result = subprocess.run(
                test_cmd, 
                capture_output=True, 
                text=True,
                encoding="utf-8",
                errors="replace", 
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
        
        render_capable = test_result.returncode == 0
        
        return {
            "valid": True,
            "version": version,
            "full_version": version_line,
            "render_capable": render_capable,
            "error": None if render_capable else "Blender responde pero no puede renderizar"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "error": "Timeout al verificar Blender",
            "version": None
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Error inesperado: {str(e)}",
            "version": None
        }

def get_blend_file_info(blend_file_path: str) -> Dict[str, Any]:
    """Extraer información del archivo .blend usando Blender"""
    try:
        current_blender = get_current_blender_path()
        if not current_blender:
            return {"error": "Blender no está configurado"}

        # --- Script Python que se ejecutará dentro de Blender ---
        python_script = r'''
import bpy, json, os
try:
    scene = bpy.context.scene
    render = scene.render
    output_path = render.filepath
    if output_path.startswith('//'):
        blend_dir = os.path.dirname(bpy.data.filepath)
        output_path = os.path.normpath(os.path.join(blend_dir, output_path[2:]))

    info = {
        "frame_start": int(scene.frame_start),
        "frame_end": int(scene.frame_end),
        "frame_current": int(scene.frame_current),
        "fps": int(scene.render.fps),
        "fps_base": float(scene.render.fps_base),
        "render_engine": scene.render.engine,
        "resolution_x": int(scene.render.resolution_x),
        "resolution_y": int(scene.render.resolution_y),
        "resolution_percentage": int(scene.render.resolution_percentage),
        "file_format": scene.render.image_settings.file_format.lower(),
        "samples": int(getattr(scene.cycles, "samples", 0)) if scene.render.engine == "CYCLES" else 0,
        "scene_name": scene.name,
        "total_frames": int((scene.frame_end - scene.frame_start) + 1),
        "output_path": output_path,
        "output_format": render.image_settings.file_format,
        "color_mode": render.image_settings.color_mode,
        "color_depth": render.image_settings.color_depth,
        "compression": int(getattr(render.image_settings, "compression", 15)),
        "quality": int(getattr(render.image_settings, "quality", 90)),
    }
    print("BLEND_INFO_START")
    print(json.dumps(info, indent=2))
    print("BLEND_INFO_END")
except Exception as e:
    print("BLEND_INFO_START")
    print(json.dumps({"error": f"ERROR_EXTRACTING_INFO: {e}"}))
    print("BLEND_INFO_END")
'''

        # --- Guardar script temporal y ejecutar Blender en background ---
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as sf:
            script_path = sf.name
            sf.write(python_script)

        print(f"🔍 Extrayendo información de: {blend_file_path}")

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env.setdefault("LANG", "C.UTF-8")
        env.setdefault("LC_ALL", "C.UTF-8")

        cmd = [
            current_blender,
            "-b",
            blend_file_path,
            "--python", script_path
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
            env=env,
        )

        stdout = result.stdout.decode("utf-8", "replace")
        stderr = result.stderr.decode("utf-8", "replace")

        # Incluso si returncode != 0, intentamos leer el bloque JSON
        start = stdout.find("BLEND_INFO_START")
        end   = stdout.find("BLEND_INFO_END", start + 1)
        if start == -1 or end == -1:
            # si Blender falló antes de imprimir el bloque
            if result.returncode != 0:
                return {"error": f"Error ejecutando Blender: {stderr or stdout}"}
            return {"error": f"No se encontraron marcadores en la salida.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"}

        payload = stdout[start + len("BLEND_INFO_START"):end].strip()
        try:
            data = json.loads(payload)
        except Exception as e:
            return {"error": f"JSON inválido desde Blender: {e}\nPayload:\n{payload}"}

        # Validaciones mínimas
        if "error" in data:
            return data
        fs, fe = int(data.get("frame_start", 0)), int(data.get("frame_end", 0))
        if fs <= 0 or fe < fs:
            return {"error": f"Rango de frames inválido: {fs}-{fe}"}

        return data

    except subprocess.TimeoutExpired:
        return {"error": "Timeout ejecutando Blender para analizar el .blend"}
    except Exception as e:
        return {"error": f"Error analizando archivo: {e}"}
    finally:
        # limpiar el script temporal si existe
        try:
            if 'script_path' in locals() and os.path.exists(script_path):
                os.remove(script_path)
        except Exception:
            pass

def estimate_render_time(blend_info: Dict) -> str:
    """Estimar tiempo de render basado en configuración"""
    total_frames = blend_info.get("total_frames", 1)
    samples = blend_info.get("samples", 128)
    resolution_x = blend_info.get("resolution_x", 1920)
    resolution_y = blend_info.get("resolution_y", 1080)
    render_engine = blend_info.get("render_engine", "CYCLES")
    
    # Factores de estimación (muy aproximados)
    base_time_per_frame = 30  # segundos base por frame
    
    # Ajustar según motor de render
    if render_engine == "CYCLES":
        base_time_per_frame *= (samples / 128)  # Factor por samples
    elif render_engine == "EEVEE":
        base_time_per_frame *= 0.3  # Eevee es mucho más rápido
    elif render_engine == "WORKBENCH":
        base_time_per_frame *= 0.1  # Workbench es muy rápido
    
    # Ajustar según resolución
    resolution_factor = (resolution_x * resolution_y) / (1920 * 1080)
    base_time_per_frame *= resolution_factor
    
    total_seconds = total_frames * base_time_per_frame
    
    if total_seconds < 60:
        return f"~{int(total_seconds)} segundos"
    elif total_seconds < 3600:
        return f"~{int(total_seconds/60)} minutos"
    else:
        hours = int(total_seconds / 3600)
        minutes = int((total_seconds % 3600) / 60)
        return f"~{hours}h {minutes}m"

def find_blender_executable():
    """Obtener ejecutable de Blender usando configuración"""
    return get_current_blender_path()

# Actualizar variable global al inicio
BLENDER_EXECUTABLE = find_blender_executable()

# ==================== BASE DE DATOS EN MEMORIA ====================

jobs_db = {}

def get_system_stats():
    """Obtener estadísticas actuales del sistema"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        return {
            "cpu_usage": int(cpu_percent),
            "memory_usage": int(memory.percent),
            "memory_available": memory.available,
            "memory_total": memory.total
        }
    except:
        return {
            "cpu_usage": 0,
            "memory_usage": 0,
            "memory_available": 0,
            "memory_total": 0
        }

nodes_db = {}

# Almacén temporal para chunks
upload_sessions: Dict[str, dict] = {}


# ==================== BASE DE DATOS EN MEMORIA EXTENDIDA ====================

# Base de datos de nodos registrados
nodes_registry: Dict[str, NodeInfo] = {}

#

# ==================== FUNCIONES DE RENDER ====================

async def render_job_background(job_id: str):
    """Función para renderizar en background con soporte para animaciones"""
    if job_id not in jobs_db:
        return
    
    job = jobs_db[job_id]
    recipient_email = job.get("notification_email")
    print(f"\n--- PASO 2: Iniciando Render para Job {job_id} ---")
    print(f"📧 Intentando notificar a: '{recipient_email}'")
    
    try:
        # Actualizar estado a procesando
        job["status"] = "processing"
        job["started_at"] = datetime.now()
        job["progress"] = 0
        job["frames_rendered"] = 0
        
        # Actualizar nodo local con estadísticas reales
        system_stats = get_system_stats()
        nodes_db["local"]["status"] = "rendering"
        nodes_db["local"]["current_job"] = job["name"]
        nodes_db["local"]["cpu_usage"] = system_stats["cpu_usage"]
        nodes_db["local"]["memory_usage"] = system_stats["memory_usage"]
        
        blend_file = job["file_path"]
        
        # Verificar que el archivo existe
        if not os.path.exists(blend_file):
            raise Exception(f"Archivo .blend no encontrado: {blend_file}")
        
        # Verificar que Blender está disponible
        current_blender = get_current_blender_path()
        if not current_blender:
            raise Exception("Blender no está configurado o no se encuentra")
        
        # Obtener información del archivo .blend para usar su configuración
        blend_info = get_blend_file_info(blend_file)
        
        frame_start = job.get("frame_start", 1)
        frame_end = job.get("frame_end", 1)
        total_frames = (frame_end - frame_start) + 1
        
        # Decidir dónde guardar los renders
        use_blend_output = blend_info and "output_path" in blend_info and blend_info["output_path"]
        
        if use_blend_output:
            # Usar la configuración de output del archivo .blend
            print(f"📁 Usando output configurado en .blend: {blend_info['output_path']}")
            
            # El comando de Blender usará la configuración interna del archivo
            # No necesitamos especificar -o ya que usará la configuración del .blend
            cmd = [
                current_blender,
                "-b",  # Background mode
                blend_file,
                "-s", str(frame_start),  # Frame inicial
                "-e", str(frame_end),    # Frame final
                "-a"  # Render animación completa
            ]
            
            # Determinar directorio de output para seguimiento
            output_dir = Path(blend_info["output_path"]).parent
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)
            
        else:
            # Fallback: usar nuestro directorio por defecto
            output_dir = OUTPUT_DIR / job_id
            output_dir.mkdir(exist_ok=True)
            output_pattern = str(output_dir / "frame_####")
            
            print(f"📁 Usando output por defecto: {output_pattern}")
            
            cmd = [
                current_blender,
                "-b",  # Background mode
                blend_file,
                "-o", output_pattern,
                "-s", str(frame_start),  # Frame inicial
                "-e", str(frame_end),    # Frame final
                "-a"  # Render animación completa
            ]
        
        job["output_path"] = str(output_dir)
        
        print(f"🎬 Renderizando animación: frames {frame_start}-{frame_end} ({total_frames} frames)")
        print(f"🎬 Ejecutando comando: {' '.join(cmd)}")
        
        # Ejecutar Blender
        if platform.system() == "Windows":
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
        
        # Monitorear progreso en tiempo real
        frames_completed = 0
        last_saved_frame = None
        
        # Leer salida de Blender para obtener progreso real
        while True:
            # Verificar si fue cancelado
            if job["status"] == "cancelled":
                process.terminate()
                print(f"🛑 Render cancelado por el usuario: {job_id}")
                return
            
            # Leer una línea de output
            output_line = process.stdout.readline()
            
            if output_line:
                line = output_line.strip()
                print(f"Blender output: {line}")
                
                # Detectar cuando un frame se ha guardado exitosamente
                if "Saved:" in line:
                    # Extraer información del archivo guardado
                    saved_file_match = re.search(r"'([^']+)'", line)
                    if saved_file_match:
                        saved_file_path = saved_file_match.group(1)
                        print(f"📁 Archivo guardado: {saved_file_path}")
                        
                        # Extraer número de frame del nombre del archivo
                        frame_match = re.search(r'(\d+)\.(?:png|jpg|jpeg|exr|tiff)', saved_file_path, re.IGNORECASE)
                        if frame_match:
                            saved_frame = int(frame_match.group(1))
                            
                            # Solo contar si es un frame nuevo
                            if last_saved_frame is None or saved_frame != last_saved_frame:
                                frames_completed += 1
                                last_saved_frame = saved_frame
                                job["frames_rendered"] = frames_completed
                                
                                # Calcular progreso basado en frames realmente guardados
                                progress = min(int((frames_completed / total_frames) * 100), 99)
                                job["progress"] = progress
                                
                                print(f"📈 Progreso REAL: Frame {frames_completed}/{total_frames} ({progress}%) - Guardado: {os.path.basename(saved_file_path)}")
                
                # Detectar errores críticos
                if "Error:" in line or "EXCEPTION" in line or "Traceback" in line:
                    print(f"❌ Error crítico detectado: {line}")
            
            # Verificar si el proceso terminó
            if process.poll() is not None:
                break
            
            # Pequeña pausa para no sobrecargar CPU
            await asyncio.sleep(0.1)
        
        # Obtener salida final
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            job["status"] = "completed"
            job["completed_at"] = datetime.now()
            print(f"✅ Render COMPLETADO exitosamente para job {job_id}")

            print(f"\n--- PASO 3: Finalización de Job (Éxito) ---")
            if recipient_email:
                print(f"📧 Llamando al servicio de notificación para {recipient_email}...")
                await notification_service.notify_job_completed(
                    job_name=job["name"],
                    output_path=str(job["output_path"]),
                    recipient=recipient_email
                )
            else:
                print("🤷‍♂️ No hay email de notificación configurado para este job.")
        else:
            job["status"] = "failed"
            error_msg = f"Blender terminó con error (código {process.returncode}): {stderr[:500]}"
            job["error_message"] = error_msg
            print(f"❌ Error en render: código {process.returncode}")

            print(f"\n--- PASO 3: Finalización de Job (Fallo) ---")
            if recipient_email:
                print(f"📧 Llamando al servicio de notificación para {recipient_email}...")
                await notification_service.notify_job_failed(
                    job_name=job["name"],
                    error_message=error_msg,
                    recipient=recipient_email
                )
            else:
                print("🤷‍♂️ No hay email de notificación configurado para este job.")

    except Exception as e:
        job["status"] = "failed"
        job["error_message"] = str(e)
        print(f"❌ Error en render: {e}")

        print(f"\n--- PASO 3: Finalización de Job (Excepción) ---")
        if recipient_email:
            print(f"📧 Llamando al servicio de notificación para {recipient_email}...")
            await notification_service.notify_job_failed(
                job_name=job.get("name", "Desconocido"),
                error_message=str(e),
                recipient=recipient_email
            )
        else:
            print("🤷‍♂️ No hay email de notificación configurado para este job.")
    
    finally:
        system_stats = get_system_stats()
        nodes_db["local"]["status"] = "online"
        nodes_db["local"]["current_job"] = None
        nodes_db["local"]["cpu_usage"] = system_stats["cpu_usage"]
        nodes_db["local"]["memory_usage"] = system_stats["memory_usage"]

# ==================== ENDPOINTS PRINCIPALES ====================

@app.post("/api/v1/blend/analyze")
async def analyze_blend_file(file: UploadFile = File(...)):
    """Analizar archivo .blend y extraer información de frames"""
    
    if not file.filename.endswith('.blend'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .blend")
    
    # Guardar archivo temporal
    temp_file_path = TEMP_DIR / f"temp_{uuid.uuid4()}_{file.filename}"
    
    try:
        # Guardar archivo
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extraer información
        blend_info = get_blend_file_info(str(temp_file_path))
        
        if "error" in blend_info:
            raise HTTPException(status_code=400, detail=blend_info["error"])
        
        return {
            "filename": file.filename,
            "file_size": temp_file_path.stat().st_size,
            "blend_info": blend_info,
            "recommended_settings": {
                "frame_start": blend_info["frame_start"],
                "frame_end": blend_info["frame_end"],
                "render_engine": blend_info["render_engine"],
                "total_frames": blend_info["total_frames"],
                "estimated_time": estimate_render_time(blend_info)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analizando archivo: {str(e)}")
    finally:
        # Limpiar archivo temporal
        if temp_file_path.exists():
            os.remove(temp_file_path)

@app.get("/api/v1/jobs/{job_id}/download-result")
async def download_job_result_enhanced(job_id: str, frame: Optional[int] = None):
    """
    Descargar resultado del render - MEJORADO CON MEJOR MANEJO DE ERRORES
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"El trabajo no está completado. Estado actual: {job['status']}, Progreso: {job.get('progress', 0)}%"
        )
    
    # Buscar archivos en múltiples ubicaciones
    possible_dirs = []
    if job.get("output_path"):
        possible_dirs.append(Path(job["output_path"]))
    possible_dirs.append(OUTPUT_DIR / job_id)
    
    image_files = []
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    
    for output_dir in possible_dirs:
        if output_dir.exists():
            for ext in extensions:
                found = list(output_dir.glob(ext))
                image_files.extend(found)
            
            if image_files:
                break  # Encontró archivos, no seguir buscando
    
    image_files = sorted(set(image_files))
    
    if not image_files:
        # Error detallado
        searched_paths = [str(d) for d in possible_dirs]
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron imágenes renderizadas. Búsqueda en: {', '.join(searched_paths)}"
        )
    
    # Si se especifica frame, buscar ese frame
    if frame is not None:
        target_file = None
        for img_file in image_files:
            # Patrones de búsqueda flexibles
            if (f"{frame:04d}" in img_file.name or 
                f"{frame:03d}" in img_file.name or 
                f"{frame:02d}" in img_file.name or 
                f"_{frame}." in img_file.name):
                target_file = img_file
                break
        
        if not target_file:
            raise HTTPException(
                status_code=404, 
                detail=f"Frame {frame} no encontrado. Frames disponibles: {[f.name for f in image_files[:10]]}"
            )
        
        return FileResponse(path=target_file, filename=target_file.name)
    
    # Devolver primer frame
    first_file = image_files[0]
    return FileResponse(path=first_file, filename=first_file.name)


@app.post("/api/v1/jobs/{job_id}/upload-result")
async def upload_job_result(job_id: str, file: UploadFile = File(...)):
    """Subir frame - CON AUTO-COMPLETADO QUE FUNCIONA"""
    try:
        if job_id not in jobs_db:
            raise HTTPException(status_code=404, detail="Trabajo no encontrado")
        
        job = jobs_db[job_id]
        
        # Crear directorio
        job_output_dir = OUTPUT_DIR / job_id
        job_output_dir.mkdir(exist_ok=True)
        
        # Guardar archivo
        file_path = job_output_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Inicializar lista
        if "output_files" not in job:
            job["output_files"] = []
        
        # Evitar duplicados
        if not any(f["filename"] == file.filename for f in job["output_files"]):
            job["output_files"].append({
                "filename": file.filename,
                "path": str(file_path),
                "size": len(content),
                "uploaded_at": datetime.now().isoformat()
            })
        
        # Contar
        total_frames = job.get("frames_total", 0)
        frames_rendered = len(job["output_files"])
        job["frames_rendered"] = frames_rendered
        
        # Progreso
        if total_frames > 0:
            progress = min(int((frames_rendered / total_frames) * 100), 99 if frames_rendered < total_frames else 100)
            job["progress"] = progress
        
        # Output path
        if not job.get("output_path"):
            job["output_path"] = str(job_output_dir)
        
        print(f"📁 Frame {frames_rendered}/{total_frames}: {file.filename} ({job['progress']}%)")
        
        # ===== AUTO-COMPLETAR =====
        if frames_rendered == total_frames and total_frames > 0 and job["status"] != "completed":
            job["status"] = "completed"
            job["completed_at"] = datetime.now()
            job["progress"] = 100
            
            if job.get("started_at"):
                started = job["started_at"] if isinstance(job["started_at"], datetime) else datetime.fromisoformat(job["started_at"])
                job["render_time"] = str(datetime.now() - started).split('.')[0]
            
            print(f"\n{'='*60}")
            print(f"✅ COMPLETADO: {job.get('name')}")
            print(f"   Frames: {frames_rendered}/{total_frames}")
            print(f"   Tiempo: {job.get('render_time', 'N/A')}")
            print(f"{'='*60}\n")
        
        return {
            "message": "Frame subido",
            "filename": file.filename,
            "frames_rendered": frames_rendered,
            "frames_total": total_frames,
            "progress": job["progress"],
            "status": job["status"],
            "is_completed": job["status"] == "completed"
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/jobs/{job_id}/download")
async def download_job_file(job_id: str, format: str = "zip"):
    """Permite descargar archivos - ZIP para nodos, imagen para frontend"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    # Si format=zip o es un nodo, devolver ZIP del .blend
    if format == "zip":
        file_path = Path(job["file_path"])
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        # Crear ZIP en memoria con el archivo .blend
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(file_path, file_path.name)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={job_id}.zip"}
        )
    
    # Si format=image o es el frontend, devolver primera imagen renderizada
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="El trabajo no está completado")
    
    if not job["output_path"]:
        raise HTTPException(status_code=404, detail="No se encontró directorio de salida")
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    common_extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    image_files = []
    
    for ext in common_extensions:
        image_files.extend(list(output_dir.glob(ext)))
        image_files.extend(list(output_dir.glob("**/" + ext)))
    
    image_files = sorted(image_files)
    
    if not image_files:
        raise HTTPException(status_code=404, detail="No se encontraron imágenes renderizadas")
    
    # Devolver primer frame
    first_file = image_files[0]
    
    # Determinar tipo MIME
    mime_type = "image/png"
    if first_file.suffix.lower() in ['.jpg', '.jpeg']:
        mime_type = "image/jpeg"
    elif first_file.suffix.lower() == '.exr':
        mime_type = "image/x-exr"
    elif first_file.suffix.lower() in ['.tiff', '.tif']:
        mime_type = "image/tiff"
    
    return FileResponse(
        path=str(first_file),
        filename=f"preview_{job_id}{first_file.suffix}",
        media_type=mime_type
    )

# Endpoint adicional para limpiar nodos offline
@app.post("/api/v1/nodes/cleanup")
async def cleanup_offline_nodes():
    """Limpiar nodos que no han enviado heartbeat recientemente"""
    try:
        current_time = datetime.now()
        offline_threshold = timedelta(minutes=2)  # 2 minutos sin heartbeat = offline
        
        offline_nodes = []
        
        for node_id, node_info in list(nodes_db.items()):
            last_seen = node_info.get("last_seen")
            if isinstance(last_seen, str):
                last_seen = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
            
            if last_seen and (current_time - last_seen) > offline_threshold:
                offline_nodes.append(node_id)
                
                # Marcar trabajos asignados como pendientes
                for job_id, job in jobs_db.items():
                    if job.get("assigned_node") == node_id and job["status"] == "processing":
                        jobs_db[job_id]["status"] = "pending"
                        jobs_db[job_id]["assigned_node"] = None
                        print(f"🔄 Trabajo {job_id} marcado como pendiente (nodo offline)")
                
                # Eliminar nodo
                del nodes_db[node_id]
                print(f"🗑️ Nodo offline eliminado: {node_id}")
        
        return {
            "message": f"Limpieza completada. {len(offline_nodes)} nodos eliminados",
            "offline_nodes": offline_nodes
        }
        
    except Exception as e:
        print(f"Error limpiando nodos offline: {e}")
        raise HTTPException(status_code=500, detail=f"Error en limpieza: {str(e)}")

# Endpoint para obtener estadísticas detalladas de nodos
@app.get("/api/v1/nodes/stats")
async def get_nodes_statistics():
    """Obtener estadísticas detalladas de todos los nodos"""
    try:
        current_time = datetime.now()
        
        stats = {
            "total_nodes": len(nodes_db),
            "online_nodes": 0,
            "offline_nodes": 0,
            "rendering_nodes": 0,
            "idle_nodes": 0,
            "total_cpu_cores": 0,
            "total_memory_gb": 0,
            "total_active_jobs": 0,
            "nodes_detail": []
        }
        
        for node_id, node_info in nodes_db.items():
            last_seen = node_info.get("last_seen")
            if isinstance(last_seen, str):
                try:
                    last_seen = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                except:
                    last_seen = datetime.now() - timedelta(hours=1)  # Asumir offline
            
            # Determinar estado
            if last_seen and (current_time - last_seen) < timedelta(minutes=2):
                if node_info.get("status") == "rendering":
                    stats["rendering_nodes"] += 1
                    node_status = "rendering"
                else:
                    stats["idle_nodes"] += 1
                    node_status = "idle"
                stats["online_nodes"] += 1
            else:
                stats["offline_nodes"] += 1
                node_status = "offline"
            
            # Sumar recursos
            system_stats = node_info.get("system_stats", {})
            stats["total_cpu_cores"] += system_stats.get("cpu_count", 0)
            stats["total_memory_gb"] += system_stats.get("memory_total_gb", 0)
            stats["total_active_jobs"] += node_info.get("active_jobs", 0)
            
            # Detalle del nodo
            stats["nodes_detail"].append({
                "id": node_id,
                "name": node_info.get("name", "Sin nombre"),
                "status": node_status,
                "last_seen": last_seen.isoformat() if last_seen else None,
                "active_jobs": node_info.get("active_jobs", 0),
                "cpu_usage": system_stats.get("cpu_percent", 0),
                "memory_usage": system_stats.get("memory_percent", 0),
                "capabilities": node_info.get("capabilities", {}),
                "system_info": node_info.get("node_info", {})
            })
        
        return stats
        
    except Exception as e:
        print(f"Error obteniendo estadísticas de nodos: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")
    
@app.get("/api/v1/jobs/{job_id}/frames")
async def get_job_frames(job_id: str):
    """
    Obtener lista de todos los frames renderizados
    MEJORADO: Devuelve URLs correctas para el frontend
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        return {
            "has_frames": False,
            "status": job["status"],
            "message": f"Trabajo en estado: {job['status']}"
        }
    
    # Buscar archivos de imagen
    possible_dirs = []
    if job.get("output_path"):
        possible_dirs.append(Path(job["output_path"]))
    possible_dirs.append(OUTPUT_DIR / job_id)
    
    image_files = []
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    
    for output_dir in possible_dirs:
        if output_dir.exists():
            for ext in extensions:
                image_files.extend(list(output_dir.glob(ext)))
                image_files.extend(list(output_dir.glob(f"**/{ext}")))
    
    image_files = sorted(set(image_files))
    
    if not image_files:
        return {
            "has_frames": False,
            "message": "No se encontraron imágenes renderizadas"
        }
    
    # Extraer números de frame
    import re
    frames = []
    for img_file in image_files:
        try:
            # Extraer número de frame del nombre del archivo
            frame_matches = re.findall(r'(\d+)', img_file.stem)
            if frame_matches:
                frame_num = max(frame_matches, key=len)
                frame_num = int(frame_num)
                
                frames.append({
                    "frame_number": frame_num,
                    "filename": img_file.name,
                    "file_size": img_file.stat().st_size,
                    "download_url": f"/api/v1/jobs/{job_id}/frame/{frame_num}",
                    "static_url": f"/renders/{job_id}/{img_file.name}",
                    "full_path": str(img_file)
                })
        except:
            continue
    
    frames.sort(key=lambda x: x["frame_number"])
    
    return {
        "has_frames": True,
        "total_frames": len(frames),
        "frame_start": job.get("frame_start", 1),
        "frame_end": job.get("frame_end", 1),
        "frames": frames,
        "output_dir": str(possible_dirs[0]) if possible_dirs else None,
        "preview_url": f"/api/v1/jobs/{job_id}/download-result"
    }

@app.get("/api/v1/jobs/{job_id}/frame/{frame_num}")
async def get_specific_frame(job_id: str, frame_num: int):
    """
    Obtener un frame específico
    MEJORADO: Búsqueda más flexible de frames
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="El trabajo no está completado")
    
    # Buscar archivos
    possible_dirs = []
    if job.get("output_path"):
        possible_dirs.append(Path(job["output_path"]))
    possible_dirs.append(OUTPUT_DIR / job_id)
    
    image_files = []
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    
    for output_dir in possible_dirs:
        if output_dir.exists():
            for ext in extensions:
                image_files.extend(list(output_dir.glob(ext)))
                image_files.extend(list(output_dir.glob(f"**/{ext}")))
    
    # Buscar el frame específico
    frame_file = None
    for img_file in image_files:
        # Buscar diferentes patrones de numeración
        frame_patterns = [
            f'{frame_num:04d}',  # 0001
            f'{frame_num:03d}',  # 001
            f'{frame_num:02d}',  # 01
            f'{frame_num}',      # 1
        ]
        
        for pattern in frame_patterns:
            if pattern in img_file.name:
                frame_file = img_file
                break
        if frame_file:
            break
    
    if not frame_file:
        raise HTTPException(
            status_code=404, 
            detail=f"Frame {frame_num} no encontrado. Archivos disponibles: {[f.name for f in image_files[:5]]}"
        )
    
    # Determinar tipo MIME
    mime_type = "image/png"
    if frame_file.suffix.lower() in ['.jpg', '.jpeg']:
        mime_type = "image/jpeg"
    elif frame_file.suffix.lower() == '.exr':
        mime_type = "image/x-exr"
    elif frame_file.suffix.lower() in ['.tiff', '.tif']:
        mime_type = "image/tiff"
    
    return FileResponse(
        path=str(frame_file),
        filename=f"frame_{frame_num:04d}{frame_file.suffix}",
        media_type=mime_type
    )

@app.get("/api/v1/jobs/{job_id}/download-all")
async def download_all_frames(job_id: str):
    """
    Descargar todos los frames como ZIP
    MEJORADO: Maneja errores y proporciona mejor feedback
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"El trabajo no está completado (estado actual: {job['status']})"
        )
    
    # Buscar archivos de imagen
    possible_dirs = []
    if job.get("output_path"):
        possible_dirs.append(Path(job["output_path"]))
    possible_dirs.append(OUTPUT_DIR / job_id)
    
    image_files = []
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    
    for output_dir in possible_dirs:
        if output_dir.exists():
            for ext in extensions:
                image_files.extend(list(output_dir.glob(ext)))
                image_files.extend(list(output_dir.glob(f"**/{ext}")))
    
    image_files = sorted(set(image_files))
    
    if not image_files:
        raise HTTPException(status_code=404, detail="No se encontraron imágenes renderizadas")
    
    try:
        # Crear ZIP en memoria
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img_file in image_files:
                # Usar solo el nombre del archivo en el ZIP
                zip_file.write(img_file, img_file.name)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=render_{job['name'].replace(' ', '_')}_{job_id[:8]}.zip"
            }
        )
    except Exception as e:
        print(f"Error creando ZIP para trabajo {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error creando archivo ZIP: {str(e)}")

# ==================== ENDPOINTS FALTANTES ====================

@app.get("/api/v1/auth/me", response_model=UserInfo)
async def get_current_user():
    """Obtiene información del usuario actual (mock para desarrollo)"""
    return UserInfo(
        id="dev-user-001",
        username="Developer",
        email="dev@example.com",
        is_authenticated=True
    )

@app.get("/api/v1/config/queue", response_model=QueueConfig)
async def get_queue_config():
    """Obtiene la configuración actual de la cola de render"""
    try:
        config_path = BASE_DIR / "queue_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                return QueueConfig(**config_data)
        else:
            # Devolver configuración por defecto
            return QueueConfig()
    except Exception as e:
        print(f"Error loading queue config: {e}")
        return QueueConfig()

@app.post("/api/v1/config/queue", response_model=QueueConfig)
async def save_queue_config(config: QueueConfig):
    """Guarda la configuración de la cola de render"""
    try:
        config_path = BASE_DIR / "queue_config.json"
        with open(config_path, 'w') as f:
            json.dump(config.dict(), f, indent=2)
        
        print(f"Queue configuration saved: {config}")
        return config
    except Exception as e:
        print(f"Error saving queue config: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving configuration: {str(e)}")

@app.get("/api/v1/system/info", response_model=SystemInfo)
async def get_system_info():
    """Obtiene información del sistema"""
    try:
        # Información del sistema operativo
        os_info = f"{platform.system()} {platform.release()}"
        
        # Arquitectura
        arch_info = platform.machine()
        
        # Memoria total
        memory = psutil.virtual_memory()
        total_memory = f"{memory.total // (1024**3)} GB"
        
        # Núcleos de CPU
        cpu_cores = psutil.cpu_count(logical=True)
        
        # Versión de Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Espacio en disco (del directorio actual)
        disk = psutil.disk_usage('.')
        disk_space = f"{disk.free // (1024**3)} GB libre de {disk.total // (1024**3)} GB"
        
        return SystemInfo(
            os=os_info,
            arch=arch_info,
            total_memory=total_memory,
            cpu_cores=cpu_cores,
            python_version=python_version,
            disk_space=disk_space
        )
    except Exception as e:
        print(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting system information: {str(e)}")

@app.get("/api/v1/jobs/{job_id}/download-first-frame")
async def download_first_frame(job_id: str):
    """Descargar primer frame para preview"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="El trabajo no está completado")
    
    if not job["output_path"]:
        raise HTTPException(status_code=404, detail="No se encontró directorio de salida")
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    common_extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    image_files = []
    
    for ext in common_extensions:
        image_files.extend(list(output_dir.glob(ext)))
        image_files.extend(list(output_dir.glob("**/" + ext)))
    
    image_files = sorted(image_files)
    
    if not image_files:
        raise HTTPException(status_code=404, detail="No se encontraron imágenes renderizadas")
    
    # Devolver primer frame
    first_file = image_files[0]
    
    # Determinar tipo MIME
    mime_type = "image/png"
    if first_file.suffix.lower() in ['.jpg', '.jpeg']:
        mime_type = "image/jpeg"
    elif first_file.suffix.lower() == '.exr':
        mime_type = "image/x-exr"
    elif first_file.suffix.lower() in ['.tiff', '.tif']:
        mime_type = "image/tiff"
    
    return FileResponse(
        path=str(first_file),
        filename=f"preview_{job_id}{first_file.suffix}",
        media_type=mime_type
    )


@app.post("/api/v1/config/blender/test")
async def test_blender_config(request: BlenderTestRequest):
    """Prueba la configuración de Blender sin guardarla"""
    try:
        blender_path = request.blender_path.strip()
        
        if not blender_path:
            raise HTTPException(status_code=400, detail="Blender path is required")
        
        verification = verify_blender_path(blender_path)
        
        return {
            "blender_path": blender_path,
            "verification": verification
        }
            
    except Exception as e:
        print(f"Error testing Blender config: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing Blender configuration: {str(e)}")

@app.post("/api/v1/config/blender/auto-detect")
async def auto_detect_blender():
    """Auto-detecta instalaciones de Blender, recomienda la más reciente y devuelve la lista completa."""
    try:
        detected_versions = scan_for_blender()
        
        if not detected_versions:
            return {
                "detected_versions": [],
                "blender_path": None,
                "verification": {
                    "valid": False,
                    "error": "No se encontraron instalaciones de Blender",
                    "version": None
                }
            }
        
        # Filtrar solo versiones que son válidas y tienen un número de versión parseable
        valid_versions = [
            v for v in detected_versions 
            if v.get("valid", False) and re.match(r'^\d+\.\d+\.\d+', v.get("version", ""))
        ]
        
        if not valid_versions:
            return {
                "detected_versions": detected_versions,
                "blender_path": None,
                "verification": {
                    "valid": False,
                    "error": "No se encontraron versiones válidas de Blender",
                    "version": None
                }
            }
        
        # Encontrar la versión más reciente comparando los números de versión
        # Convierte "4.5.2" a una tupla (4, 5, 2) para una comparación precisa
        most_recent_version = max(
            valid_versions, 
            key=lambda v: tuple(map(int, v['version'].split('.')))
        )
        
        return {
            "detected_versions": detected_versions,
            "blender_path": most_recent_version["path"],
            "verification": {
                "valid": True,
                "version": most_recent_version["version"],
                "error": None,
                "message": f"Se recomienda la versión más reciente. Se encontraron {len(valid_versions)} versiones válidas."
            }
        }
            
    except Exception as e:
        print(f"Error auto-detecting Blender: {e}")
        raise HTTPException(status_code=500, detail=f"Error auto-detecting Blender: {str(e)}")

@app.post("/api/v1/config/blender")
async def save_blender_config(config: BlenderConfigUpdate):
    """Guardar configuración de Blender"""
    global app_config, BLENDER_EXECUTABLE
    
    try:
        # Verificar path si se proporciona
        verification = verify_blender_path(config.blender_path)
        
        if not verification["valid"]:
            return {
                "blender_path": config.blender_path,
                "verification": verification
            }
        
        # Actualizar configuración
        app_config["blender"]["auto_detect"] = config.auto_detect
        app_config["blender"]["custom_path"] = config.blender_path
        app_config["blender"]["path"] = config.blender_path
        app_config["blender"]["version"] = verification["version"]
        app_config["blender"]["last_verified"] = datetime.now().isoformat()
        
        # Guardar configuración
        save_config(app_config)
        
        # Actualizar variable global
        BLENDER_EXECUTABLE = get_current_blender_path()
        
        return {
            "blender_path": config.blender_path,
            "verification": verification
        }
        
    except Exception as e:
        print(f"Error saving Blender config: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving Blender configuration: {str(e)}")

# ==================== ENDPOINTS DE NODOS DISTRIBUIDOS ====================

@app.post("/api/v1/nodes/{node_id}/heartbeat")
async def node_heartbeat_by_id(node_id: str, heartbeat_data: Dict[str, Any]):
    """Recibe heartbeat de un nodo específico"""
    try:
        if node_id not in nodes_db:
            raise HTTPException(
                status_code=404, 
                detail="Nodo no registrado. Por favor, regístrese de nuevo."
            )
        
        # Actualizar información del nodo
        nodes_db[node_id]["last_seen"] = datetime.now()
        nodes_db[node_id]["status"] = heartbeat_data.get("status", "online")
        
        # Actualizar estadísticas del sistema
        if "system_stats" in heartbeat_data:
            nodes_db[node_id]["system_stats"] = heartbeat_data["system_stats"]
        
        # Actualizar trabajos activos
        if "job_statuses" in heartbeat_data:
            job_statuses = heartbeat_data["job_statuses"]
            for job_id, job_status in job_statuses.items():
                if job_id in jobs_db:
                    # Actualizar estado del trabajo
                    jobs_db[job_id]["status"] = job_status.get("status", "processing")
                    jobs_db[job_id]["progress"] = job_status.get("progress", 0)
                    jobs_db[job_id]["frame_current"] = job_status.get("frame_current", 0)
                    jobs_db[job_id]["frame_total"] = job_status.get("frame_total", 0)
                    
                    # Si se completó, manejar finalización
                    if job_status.get("status") == "completed":
                        jobs_db[job_id]["status"] = "completed"
                        jobs_db[job_id]["completed_at"] = datetime.now()
                        jobs_db[job_id]["progress"] = 100
                        
                        # Actualizar contador del nodo
                        if "active_jobs" in nodes_db[node_id]:
                            nodes_db[node_id]["active_jobs"] = max(0, nodes_db[node_id]["active_jobs"] - 1)
                        
                        print(f"✅ Trabajo {job_id} completado por nodo {node_id}")
                    
                    elif job_status.get("status") == "failed":
                        jobs_db[job_id]["status"] = "failed"
                        jobs_db[job_id]["error_message"] = job_status.get("error_message", "Error desconocido")
                        jobs_db[job_id]["completed_at"] = datetime.now()
                        
                        # Actualizar contador del nodo
                        if "active_jobs" in nodes_db[node_id]:
                            nodes_db[node_id]["active_jobs"] = max(0, nodes_db[node_id]["active_jobs"] - 1)
                        
                        print(f"❌ Trabajo {job_id} falló en nodo {node_id}: {job_status.get('error_message', 'Error desconocido')}")
        
        return {
            "message": "Heartbeat recibido",
            "server_time": datetime.now().isoformat(),
            "next_heartbeat": (datetime.now() + timedelta(seconds=15)).isoformat()
        }
        
    except Exception as e:
        print(f"Error procesando heartbeat de nodo {node_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando heartbeat: {str(e)}")

@app.get("/api/v1/nodes/{node_id}/poll")
async def poll_job_for_node(node_id: str):
    """Consultar si hay trabajos disponibles para un nodo específico"""
    try:
        if node_id not in nodes_db:
            raise HTTPException(
                status_code=404, 
                detail="Nodo no registrado"
            )
        
        node_info = nodes_db[node_id]
        
        # Verificar si el nodo puede tomar más trabajos
        max_jobs = node_info.get("capabilities", {}).get("max_concurrent_jobs", 1)
        current_jobs = node_info.get("active_jobs", 0)
        
        if current_jobs >= max_jobs:
            # Nodo ocupado - devolver 204 No Content
            return Response(status_code=204)
        
        # Buscar trabajos pendientes
        pending_jobs = [
            job for job in jobs_db.values() 
            if job["status"] == "pending"
        ]
        
        if not pending_jobs:
            # No hay trabajos disponibles - devolver 204 No Content
            return Response(status_code=204)
        
        # Obtener el primer trabajo pendiente
        job = pending_jobs[0]
        job_id = job["id"]
        
        # Asignar trabajo al nodo
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["started_at"] = datetime.now()
        jobs_db[job_id]["assigned_node"] = node_id
        
        # Actualizar contador de trabajos activos del nodo
        if "active_jobs" not in nodes_db[node_id]:
            nodes_db[node_id]["active_jobs"] = 0
        nodes_db[node_id]["active_jobs"] += 1
        nodes_db[node_id]["status"] = "rendering"
        
        print(f"🎬 Trabajo {job_id} asignado a nodo {node_id} ({node_info.get('name', 'Sin nombre')})")
        
        # Preparar datos del trabajo para el nodo
        job_data = {
            "job_id": job_id,
            "name": job["name"],
            "start_frame": job.get("frame_start", 1),
            "end_frame": job.get("frame_end", 1),
            "output_format": job.get("output_format", "PNG"),
            "engine": job.get("engine", "CYCLES"),
            "samples": job.get("samples", 128),
            "created_at": job["created_at"].isoformat() if isinstance(job["created_at"], datetime) else str(job["created_at"])
        }
        
        return job_data
        
    except Exception as e:
        print(f"Error polling trabajo para nodo {node_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error consultando trabajo: {str(e)}")

# ==================== RUTAS PRINCIPALES ====================

@app.get("/")
async def root():
    """Ruta raíz con información del sistema de render"""
    current_blender = get_current_blender_path()
    return {
        "message": "🎬 Render Queue Manager API v2.0",
        "version": "2.0.0",
        "status": "running",
        "features": ["file_upload", "real_rendering", "queue_management", "blender_config"],
        "blender_available": current_blender is not None,
        "blender_path": current_blender,
        "timestamp": datetime.now(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check con información detallada del sistema"""
    current_blender = get_current_blender_path()
    blender_verification = verify_blender_path(current_blender) if current_blender else None
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "Render Queue Manager",
        "version": "2.0.0",
        "blender_available": current_blender is not None,
        "blender_functional": blender_verification.get("render_capable", False) if blender_verification else False,
        "blender_path": current_blender,
        "blender_version": blender_verification.get("version") if blender_verification else None,
        "active_jobs": len([j for j in jobs_db.values() if j["status"] in ["processing", "pending"]]),
        "completed_jobs": len([j for j in jobs_db.values() if j["status"] == "completed"]),
        "storage": {
            "uploads": len(list(UPLOAD_DIR.glob("*"))),
            "renders": len(list(OUTPUT_DIR.glob("*")))
        }
    }

# ==================== RUTAS DE CONFIGURACIÓN ====================

@app.get("/api/v1/config/blender")
async def get_blender_config():
    """Obtener configuración actual de Blender"""
    config = app_config["blender"]
    current_path = get_current_blender_path()
    
    return {
        "blender_path": current_path,
        "timeout": 300,
        "max_memory_mb": 4096,
        "auto_detect": config.get("auto_detect", True),
        "current_config": config,
        "current_path": current_path,
        "is_working": current_path is not None,
        "verification": verify_blender_path(current_path) if current_path else None
    }

@app.post("/api/v1/config/blender/scan")
async def scan_blender_installations():
    """Escanear sistema buscando instalaciones de Blender"""
    installations = scan_for_blender()
    
    return {
        "installations": installations,
        "count": len(installations),
        "working_count": len([inst for inst in installations if inst["working"]]),
        "system": platform.system()
    }

@app.post("/api/v1/config/blender/verify")
async def verify_blender_installation(path: str = Form(...)):
    """Verificar una instalación específica de Blender"""
    verification = verify_blender_path(path)
    
    return {
        "path": path,
        "verification": verification
    }

@app.post("/api/v1/config/blender/set")
async def set_blender_config(
    path: str = Form(None),
    auto_detect: bool = Form(True),
    save_as_default: bool = Form(False)
):
    """Configurar path de Blender"""
    
    global app_config, BLENDER_EXECUTABLE
    
    # Verificar path si se proporciona
    verification = None
    if path:
        verification = verify_blender_path(path)
        if not verification["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Path de Blender no válido: {verification['error']}"
            )
    
    # Actualizar configuración
    app_config["blender"]["auto_detect"] = auto_detect
    
    if path:
        app_config["blender"]["custom_path"] = path
        app_config["blender"]["path"] = path
        app_config["blender"]["version"] = verification["version"] if verification else None
        app_config["blender"]["last_verified"] = datetime.now().isoformat()
    
    # Guardar si se solicita
    if save_as_default:
        if not save_config(app_config):
            raise HTTPException(status_code=500, detail="Error guardando configuración")
    
    # Actualizar variable global
    BLENDER_EXECUTABLE = get_current_blender_path()
    
    return {
        "message": "Configuración de Blender actualizada",
        "current_path": BLENDER_EXECUTABLE,
        "verification": verification,
        "saved": save_as_default
    }

@app.get("/api/v1/config/blender/reset")
async def reset_blender_config():
    """Resetear configuración de Blender a valores por defecto"""
    
    global app_config, BLENDER_EXECUTABLE
    
    app_config["blender"] = DEFAULT_CONFIG["blender"].copy()
    save_config(app_config)
    
    # Intentar auto-detección
    BLENDER_EXECUTABLE = get_current_blender_path()
    
    return {
        "message": "Configuración de Blender reseteada",
        "current_path": BLENDER_EXECUTABLE,
        "auto_detect_result": BLENDER_EXECUTABLE is not None
    }

# ==================== RUTAS DE UPLOAD ====================

@app.post("/api/v1/jobs/upload")
async def upload_and_create_job(file: UploadFile = File(...), name: str = Form(...), frame_start: int = Form(1), frame_end: int = Form(1), notification_email: Optional[str] = Form(None)):
    if not file.filename.endswith('.blend'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .blend")
    
    job_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    job = {
        "id": job_id, "name": name, "status": "pending", "progress": 0,
        "created_at": datetime.now(), "started_at": None, "completed_at": None,
        "file_path": str(file_path), "original_filename": file.filename,
        "output_path": str(OUTPUT_DIR / job_id), "frame_start": frame_start, "frame_end": frame_end,
        "frames_total": (frame_end - frame_start) + 1, "frames_rendered": 0,
        "notification_email": notification_email
    }
    
    jobs_db[job_id] = job
    return {"message": "Trabajo creado exitosamente", "job_id": job_id, "job": job}

# ==================== RUTAS DE UPLOAD POR CHUNKS ====================

@app.post("/api/v1/upload/start")
async def start_chunked_upload(
    filename: str = Form(...),
    total_size: int = Form(...),
    total_chunks: int = Form(...),
    file_hash: str = Form(...)
):
    """Iniciar upload por chunks para archivos grandes"""
    
    # Validar tamaño (hasta 5GB)
    if total_size > 5 * 1024 * 1024 * 1024:  # 5GB
        raise HTTPException(status_code=400, detail="Archivo demasiado grande. Máximo 5GB")
    
    # Validar tipo de archivo
    if not filename.endswith('.blend'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .blend")
    
    # Generar ID de sesión
    session_id = str(uuid.uuid4())
    
    # Crear directorio temporal para chunks
    temp_dir = TEMP_DIR / session_id
    temp_dir.mkdir(exist_ok=True)
    
    # Guardar información de la sesión
    upload_sessions[session_id] = {
        "filename": filename,
        "total_size": total_size,
        "total_chunks": total_chunks,
        "file_hash": file_hash,
        "uploaded_chunks": set(),
        "temp_dir": str(temp_dir),
        "created_at": datetime.now()
    }
    
    return {
        "session_id": session_id,
        "message": "Sesión de upload iniciada",
        "chunk_size": 10 * 1024 * 1024  # 10MB por chunk
    }

@app.post("/api/v1/upload/chunk/{session_id}")
async def upload_chunk(
    session_id: str,
    chunk_number: int = Form(...),
    chunk: UploadFile = File(...)
):
    """Subir un chunk específico"""
    
    if session_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = upload_sessions[session_id]
    temp_dir = Path(session["temp_dir"])
    
    # Guardar chunk
    chunk_path = temp_dir / f"chunk_{chunk_number:06d}"
    
    try:
        with open(chunk_path, "wb") as buffer:
            shutil.copyfileobj(chunk.file, buffer)
        
        # Marcar chunk como subido
        session["uploaded_chunks"].add(chunk_number)
        
        # Calcular progreso
        progress = len(session["uploaded_chunks"]) / session["total_chunks"] * 100
        
        return {
            "message": f"Chunk {chunk_number} subido",
            "progress": round(progress, 2),
            "uploaded_chunks": len(session["uploaded_chunks"]),
            "total_chunks": session["total_chunks"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando chunk: {e}")

@app.post("/api/v1/upload/complete/{session_id}")
async def complete_chunked_upload(
    session_id: str,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    frame_start: int = Form(1),
    frame_end: int = Form(1),
    render_engine: str = Form("CYCLES")
):
    """Completar upload combinando todos los chunks"""
    
    if session_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = upload_sessions[session_id]
    temp_dir = Path(session["temp_dir"])
    
    # Verificar que todos los chunks están presentes
    expected_chunks = set(range(session["total_chunks"]))
    if session["uploaded_chunks"] != expected_chunks:
        missing = expected_chunks - session["uploaded_chunks"]
        raise HTTPException(
            status_code=400, 
            detail=f"Chunks faltantes: {sorted(missing)}"
        )
    
    try:
        # Generar ID de trabajo
        job_id = str(uuid.uuid4())
        final_path = UPLOAD_DIR / f"{job_id}_{session['filename']}"
        
        # Combinar chunks en orden
        with open(final_path, "wb") as output_file:
            for chunk_num in range(session["total_chunks"]):
                chunk_path = temp_dir / f"chunk_{chunk_num:06d}"
                if chunk_path.exists():
                    with open(chunk_path, "rb") as chunk_file:
                        shutil.copyfileobj(chunk_file, output_file)
        
        # Verificar integridad del archivo
        with open(final_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
            if file_hash != session["file_hash"]:
                os.remove(final_path)
                raise HTTPException(status_code=400, detail="Error de integridad del archivo")
        
        # Crear trabajo
        job = {
            "id": job_id,
            "name": name,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "file_path": str(final_path),
            "original_filename": session["filename"],
            "output_path": None,
            "frame_start": frame_start,
            "frame_end": frame_end,
            "frames_total": (frame_end - frame_start) + 1,
            "frames_rendered": 0,
            "render_engine": render_engine,
            "estimated_time": None,
            "error_message": None,
            "file_size": session["total_size"]
        }
        
        jobs_db[job_id] = job
        
        # Limpiar archivos temporales
        shutil.rmtree(temp_dir, ignore_errors=True)
        del upload_sessions[session_id]
        
        # Iniciar render
        # background_tasks.add_task(render_job_background, job_id)
        print(f"✅ Trabajo {job_id} creado y en espera de un nodo.")

        return {
            "message": "Upload completado exitosamente",
            "job_id": job_id,
            "job": job
        }
        
    except Exception as e:
        # Limpiar en caso de error
        if 'final_path' in locals() and final_path.exists():
            os.remove(final_path)
        shutil.rmtree(temp_dir, ignore_errors=True)
        if session_id in upload_sessions:
            del upload_sessions[session_id]
        
        raise HTTPException(status_code=500, detail=f"Error completando upload: {e}")

@app.delete("/api/v1/upload/cancel/{session_id}")
async def cancel_chunked_upload(session_id: str):
    """Cancelar upload por chunks"""
    
    if session_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = upload_sessions[session_id]
    temp_dir = Path(session["temp_dir"])
    
    # Limpiar archivos temporales
    shutil.rmtree(temp_dir, ignore_errors=True)
    del upload_sessions[session_id]
    
    return {"message": "Upload cancelado y archivos temporales eliminados"}

# ==================== RUTAS DE TRABAJOS ====================

@app.get("/api/v1/jobs", response_model=List[dict])
async def get_jobs():
    """Obtener todos los trabajos - SERIALIZACIÓN PERFECTA"""
    jobs = []
    
    for job in jobs_db.values():
        # Serializar cada trabajo
        serialized = {}
        for key, value in job.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, Path):
                serialized[key] = str(value)
            elif key == "status":
                serialized[key] = str(value)
            else:
                serialized[key] = value
        
        # Campos por defecto
        serialized.setdefault("status", "unknown")
        serialized.setdefault("progress", 0)
        serialized.setdefault("frames_rendered", 0)
        serialized.setdefault("frames_total", 0)
        
        # Flags booleanos para frontend
        serialized["is_completed"] = serialized["status"] == "completed"
        serialized["is_processing"] = serialized["status"] == "processing"
        serialized["is_pending"] = serialized["status"] == "pending"
        serialized["is_failed"] = serialized["status"] == "failed"
        
        # Verificar resultados
        has_results = False
        if serialized.get("output_path"):
            output_dir = Path(serialized["output_path"])
            if output_dir.exists():
                files = list(output_dir.glob("*.png")) + list(output_dir.glob("*.jpg"))
                has_results = len(files) > 0
        
        serialized["has_downloadable_results"] = has_results
        
        jobs.append(serialized)
    
    # Ordenar por fecha (más recientes primero)
    jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return jobs

@app.get("/api/v1/jobs/{job_id}/full-status")
async def get_job_full_status(job_id: str):
    """Diagnóstico completo del estado del trabajo"""
    if job_id not in jobs_db:
        return {
            "error": "Trabajo no encontrado",
            "job_id": job_id,
            "available_jobs": list(jobs_db.keys())[:10]
        }
    
    job = jobs_db[job_id]
    
    # Contar archivos en disco
    output_dir = OUTPUT_DIR / job_id
    files_on_disk = 0
    disk_files = []
    if output_dir.exists():
        disk_files = list(output_dir.glob("*.png")) + list(output_dir.glob("*.jpg"))
        files_on_disk = len(disk_files)
    
    # Info de archivos registrados
    output_files = job.get("output_files", [])
    
    return {
        "job_id": job_id,
        "name": job.get("name"),
        "status": job["status"],
        "status_type": type(job["status"]).__name__,
        "progress": job.get("progress"),
        "frames_rendered": job.get("frames_rendered"),
        "frames_total": job.get("frames_total"),
        "completion_check": {
            "frames_match": job.get("frames_rendered") == job.get("frames_total"),
            "is_completed_status": job["status"] == "completed",
            "should_be_completed": job.get("frames_rendered") == job.get("frames_total") and job.get("frames_total", 0) > 0
        },
        "files": {
            "registered_count": len(output_files),
            "on_disk_count": files_on_disk,
            "match": len(output_files) == files_on_disk,
            "registered_files": [f["filename"] for f in output_files][:10],
            "disk_files": [f.name for f in disk_files][:10]
        },
        "paths": {
            "output_path": str(job.get("output_path")),
            "output_dir_exists": output_dir.exists()
        },
        "timing": {
            "created_at": str(job.get("created_at")),
            "started_at": str(job.get("started_at")),
            "completed_at": str(job.get("completed_at")),
            "render_time": job.get("render_time")
        },
        "frontend_flags": {
            "is_completed": job["status"] == "completed",
            "has_downloadable_results": files_on_disk > 0
        }
    }


print("✅ Solución completa aplicada - Backend optimizado para frontend reactivo")

@app.get("/api/v1/jobs/{job_id}/debug")
async def debug_job_status(job_id: str):
    """Debug: Ver estado real del trabajo en memoria"""
    if job_id not in jobs_db:
        # Mostrar trabajos disponibles
        available_ids = list(jobs_db.keys())
        return {
            "error": "Trabajo no encontrado",
            "job_id_searched": job_id,
            "available_jobs": available_ids[:10],  # Primeros 10
            "total_jobs": len(available_ids)
        }
    
    job = jobs_db[job_id]
    
    # Info detallada del estado
    debug = {
        "job_id": job_id,
        "status": job.get("status"),
        "status_type": type(job.get("status")).__name__,
        "progress": job.get("progress"),
        "frames_rendered": job.get("frames_rendered"),
        "frames_total": job.get("frames_total"),
        "completed_at": str(job.get("completed_at")),
        "output_path": str(job.get("output_path")),
        "all_keys": list(job.keys())
    }
    
    # Verificar archivos de output
    output_path = job.get("output_path")
    if output_path:
        output_dir = Path(output_path)
        if output_dir.exists():
            files = list(output_dir.glob("*.*"))
            debug["output_files_found"] = len(files)
            debug["output_files_sample"] = [f.name for f in files[:5]]
        else:
            debug["output_dir_exists"] = False
    
    return debug

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    """Obtener trabajo - SERIALIZACIÓN PERFECTA"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    # Serializar TODO correctamente
    result = {}
    for key, value in job.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, Path):
            result[key] = str(value)
        elif key == "status":
            # CRÍTICO: Asegurar que status es string
            result[key] = str(value)
        else:
            result[key] = value
    
    # Asegurar campos críticos existen
    result.setdefault("status", "unknown")
    result.setdefault("progress", 0)
    result.setdefault("frames_rendered", 0)
    result.setdefault("frames_total", 0)
    
    # ===== CRÍTICO para el frontend =====
    # Agregar flag booleano explícito para el frontend
    result["is_completed"] = result["status"] == "completed"
    result["is_processing"] = result["status"] == "processing"
    result["is_pending"] = result["status"] == "pending"
    result["is_failed"] = result["status"] == "failed"
    
    # Verificar si tiene resultados descargables
    has_results = False
    if result.get("output_path"):
        output_dir = Path(result["output_path"])
        if output_dir.exists():
            files = list(output_dir.glob("*.png")) + list(output_dir.glob("*.jpg"))
            has_results = len(files) > 0
    
    result["has_downloadable_results"] = has_results
    
    return result


@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: str):
    """Eliminar un trabajo"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    # Marcar como cancelado si está en progreso
    if job["status"] in ["pending", "processing"]:
        job["status"] = "cancelled"
    
    # Eliminar archivos
    try:
        if os.path.exists(job["file_path"]):
            os.remove(job["file_path"])
        
        if job["output_path"] and os.path.exists(job["output_path"]):
            shutil.rmtree(job["output_path"])
    except Exception as e:
        print(f"Error eliminando archivos: {e}")
    
    # Eliminar de la base de datos
    del jobs_db[job_id]
    
    return {"message": f"Trabajo {job_id} eliminado"}

@app.post("/api/v1/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancelar un trabajo"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] in ["pending", "processing"]:
        job["status"] = "cancelled"
        return {"message": f"Trabajo {job_id} cancelado"}
    else:
        raise HTTPException(status_code=400, detail="El trabajo no se puede cancelar")

@app.get("/api/v1/jobs/{job_id}/preview")
async def get_job_preview_enhanced(job_id: str):
    """
    Obtener preview del render - MEJORADO
    Asegura que siempre devuelva info útil
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    # Información básica siempre disponible
    base_info = {
        "job_id": job_id,
        "name": job.get("name", "Sin nombre"),
        "status": job["status"],
        "progress": job.get("progress", 0),
        "frames_rendered": job.get("frames_rendered", 0),
        "frames_total": job.get("frames_total", 0),
        "render_time": job.get("render_time"),
        "created_at": job.get("created_at").isoformat() if isinstance(job.get("created_at"), datetime) else job.get("created_at"),
        "started_at": job.get("started_at").isoformat() if isinstance(job.get("started_at"), datetime) else job.get("started_at"),
        "completed_at": job.get("completed_at").isoformat() if isinstance(job.get("completed_at"), datetime) else job.get("completed_at"),
    }
    
    # Si no está completado, devolver info básica
    if job["status"] != "completed":
        return {
            **base_info,
            "has_preview": False,
            "message": f"Trabajo en estado: {job['status']}"
        }
    
    # Buscar archivos de imagen
    possible_dirs = []
    if job.get("output_path"):
        possible_dirs.append(Path(job["output_path"]))
    possible_dirs.append(OUTPUT_DIR / job_id)
    
    image_files = []
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    
    output_dir_found = None
    for output_dir in possible_dirs:
        if output_dir.exists():
            output_dir_found = output_dir
            for ext in extensions:
                image_files.extend(list(output_dir.glob(ext)))
            if image_files:
                break
    
    image_files = sorted(set(image_files))
    
    if not image_files:
        return {
            **base_info,
            "has_preview": False,
            "message": "No se encontraron imágenes renderizadas",
            "searched_in": [str(d) for d in possible_dirs if d.exists()]
        }
    
    # Información del primer archivo
    first_image = image_files[0]
    
    return {
        **base_info,
        "has_preview": True,
        "preview_url": f"/api/v1/jobs/{job_id}/download-result",
        "frames_url": f"/api/v1/jobs/{job_id}/frames",
        "download_all_url": f"/api/v1/jobs/{job_id}/download-all",
        "first_frame_filename": first_image.name,
        "first_frame_size": first_image.stat().st_size,
        "total_frames_available": len(image_files),
        "output_dir": str(output_dir_found),
        "all_frames": [
            {
                "filename": f.name,
                "size": f.stat().st_size,
                "url": f"/api/v1/jobs/{job_id}/download-result?frame={i+1}"
            }
            for i, f in enumerate(image_files[:5])  # Primeros 5 para preview
        ]
    }



@app.get("/api/v1/jobs/{job_id}/download-blend")
async def download_blend_file(job_id: str):
    """Descargar archivo .blend del trabajo"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    file_path = Path(job["file_path"])
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo .blend no encontrado")
        
    return FileResponse(
        path=file_path, 
        filename=file_path.name,
        media_type="application/octet-stream"
    )

@app.get("/api/v1/jobs/{job_id}/debug")
async def debug_job_status(job_id: str):
    """Debug: Ver estado real del trabajo en memoria"""
    if job_id not in jobs_db:
        # Mostrar trabajos disponibles
        available_ids = list(jobs_db.keys())
        return {
            "error": "Trabajo no encontrado",
            "job_id_searched": job_id,
            "available_jobs": available_ids[:10],  # Primeros 10
            "total_jobs": len(available_ids)
        }
    
    job = jobs_db[job_id]
    
    # Info detallada del estado
    debug = {
        "job_id": job_id,
        "status": job.get("status"),
        "status_type": type(job.get("status")).__name__,
        "progress": job.get("progress"),
        "frames_rendered": job.get("frames_rendered"),
        "frames_total": job.get("frames_total"),
        "completed_at": str(job.get("completed_at")),
        "output_path": str(job.get("output_path")),
        "all_keys": list(job.keys())
    }
    
    # Verificar archivos de output
    output_path = job.get("output_path")
    if output_path:
        output_dir = Path(output_path)
        if output_dir.exists():
            files = list(output_dir.glob("*.*"))
            debug["output_files_found"] = len(files)
            debug["output_files_sample"] = [f.name for f in files[:5]]
        else:
            debug["output_dir_exists"] = False
    
    return debug


@app.post("/api/v1/jobs/{job_id}/update-status")
async def update_job_status_from_node(job_id: str, status_update: JobStatusUpdate):
    """Actualizar estado - PROTECCIÓN contra sobrescritura"""
    if job_id not in jobs_db:
        return {"message": "Trabajo no encontrado"}

    job = jobs_db[job_id]
    
    # ⚠️ PROTECCIÓN: NO sobrescribir si ya está completado
    if job.get("status") == "completed":
        print(f"ℹ️ Ignorando actualización: trabajo ya completado {job_id}")
        return {"message": "Trabajo ya completado", "status": "completed"}
    
    # Actualizar progreso
    if status_update.progress is not None:
        job["progress"] = status_update.progress
    
    if status_update.frames_rendered is not None:
        job["frames_rendered"] = status_update.frames_rendered
    
    # Solo actualizar estado si NO es "failed" sin mensaje
    new_status = status_update.status
    error_msg = status_update.error_message
    
    if new_status == "failed":
        if error_msg and len(str(error_msg).strip()) > 0:
            job["status"] = "failed"
            job["completed_at"] = datetime.now()
            job["error_message"] = error_msg
            print(f"❌ Trabajo {job_id} FALLIDO: {error_msg}")
    elif new_status == "completed":
        job["status"] = "completed"
        job["completed_at"] = datetime.now()
        job["progress"] = 100
    elif new_status in ["rendering", "processing", "in_progress"]:
        if job["status"] not in ["completed", "failed", "cancelled"]:
            job["status"] = "processing"
    
    return {"message": "Actualizado", "status": job["status"]}


print("✅ Fix de emergencia aplicado - Reinicia el backend")


@app.post("/api/v1/nodes/heartbeat")
async def node_heartbeat(heartbeat_data: Dict[str, Any]):
    """Recibe heartbeat de un nodo"""
    try:
        node_id = heartbeat_data.get("node_id")
        if not node_id:
            raise HTTPException(status_code=400, detail="Falta node_id")
            
        if node_id not in nodes_db:
            raise HTTPException(
                status_code=404, 
                detail="Nodo no registrado. Regístrese de nuevo."
            )
        
        # Actualizar
        nodes_db[node_id]["last_seen"] = datetime.now()
        nodes_db[node_id]["status"] = heartbeat_data.get("status", "online")
        
        if "system_stats" in heartbeat_data:
            nodes_db[node_id]["system_stats"] = heartbeat_data["system_stats"]
        
        return {
            "message": "Heartbeat recibido",
            "server_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error en heartbeat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUTAS DE GESTIÓN DE NODOS ====================

@app.post("/api/v1/jobs/{job_id}/force-complete")
async def force_complete_job(job_id: str):
    """Forzar completado de un trabajo atascado"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    frames_rendered = job.get("frames_rendered", 0)
    frames_total = job.get("frames_total", 0)
    
    print(f"🔧 Forzando completado de trabajo {job_id}")
    print(f"   Estado actual: {job['status']}")
    print(f"   Frames: {frames_rendered}/{frames_total}")
    print(f"   Progreso: {job.get('progress')}%")
    
    # Verificar que realmente está completo
    if frames_rendered != frames_total:
        raise HTTPException(
            status_code=400,
            detail=f"El trabajo no está completo. Frames: {frames_rendered}/{frames_total}"
        )
    
    # Forzar completado
    job["status"] = "completed"
    job["progress"] = 100
    
    if not job.get("completed_at"):
        job["completed_at"] = datetime.now()
    
    # Calcular tiempo si falta
    if job.get("started_at") and not job.get("render_time"):
        started = job["started_at"]
        if isinstance(started, str):
            started = datetime.fromisoformat(started)
        completed = job["completed_at"]
        if isinstance(completed, str):
            completed = datetime.fromisoformat(completed)
        duration = completed - started
        job["render_time"] = str(duration).split('.')[0]
    
    print(f"✅ Trabajo {job_id} forzado a COMPLETADO")
    print(f"   Tiempo de render: {job.get('render_time')}")
    
    return {
        "message": "Trabajo marcado como completado",
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "frames": f"{frames_rendered}/{frames_total}",
        "render_time": job.get("render_time")
    }


@app.post("/api/v1/nodes/register")
async def register_node(node_data: Dict[str, Any]):
    """Permite que un nuevo nodo se registre en el sistema."""
    try:
        node_id = node_data.get("node_id")
        if not node_id:
            raise HTTPException(status_code=400, detail="Falta node_id")

        node_name = node_data.get("node_name", "Nodo sin nombre")
        
        if node_id in nodes_db:
            print(f"🖥️ Nodo {node_name} ({node_id[:8]}) se ha reconectado.")
        else:
            print(f"✅ Nuevo nodo registrado: {node_name} ({node_id[:8]})")
        
        # Procesar datos del nodo de forma segura
        node_info = node_data.get("node_info", {})
        system_stats = node_data.get("system_stats", {})
        capabilities = node_data.get("capabilities", {})
        
        # Guardar información del nodo
        nodes_db[node_id] = {
            "id": node_id,
            "name": node_name,
            "ip": node_info.get("hostname", "N/A"),
            "status": "idle", 
            "last_seen": datetime.now(),
            "node_info": node_info,
            "system_stats": system_stats,
            "config": node_data.get("config", {}),
            "capabilities": capabilities,
            "current_job": None,
            "active_jobs": 0  # Añadir contador de trabajos activos
        }
        
        return {
            "message": "Nodo registrado exitosamente", 
            "node_id": node_id,
            "server_time": datetime.now().isoformat(),
            "heartbeat_interval": 15,
            "next_heartbeat": (datetime.now() + timedelta(seconds=15)).isoformat()
        }
        
    except Exception as e:
        print(f"Error registrando nodo: {e}")
        raise HTTPException(status_code=500, detail=f"Error registrando nodo: {str(e)}")

@app.post("/api/v1/nodes/heartbeat")
async def node_heartbeat(heartbeat_data: Dict[str, Any]):
    """Recibe un heartbeat de un nodo."""
    try:
        node_id = heartbeat_data.get("node_id")
        if not node_id:
            raise HTTPException(status_code=400, detail="Falta node_id en heartbeat")
            
        if node_id not in nodes_db:
            # Si el nodo no está registrado, pedirle que se registre de nuevo
            raise HTTPException(
                status_code=404, 
                detail="Nodo no registrado. Por favor, regístrese de nuevo."
            )
        
        # Actualizar información del nodo de forma segura
        nodes_db[node_id]["last_seen"] = datetime.now()
        
        # Actualizar status si está presente
        if "status" in heartbeat_data:
            nodes_db[node_id]["status"] = heartbeat_data["status"]
        
        # Actualizar estadísticas del sistema si están presentes
        if "system_stats" in heartbeat_data:
            nodes_db[node_id]["system_stats"] = heartbeat_data["system_stats"]
        
        # Procesar información de trabajos si está presente
        if "job_statuses" in heartbeat_data:
            job_statuses = heartbeat_data["job_statuses"]
            for job_id, job_status in job_statuses.items():
                if job_id in jobs_db:
                    # Actualizar estado del trabajo de forma segura
                    if "status" in job_status:
                        jobs_db[job_id]["status"] = job_status["status"]
                    if "progress" in job_status:
                        jobs_db[job_id]["progress"] = job_status["progress"]
                    if "frame_current" in job_status:
                        jobs_db[job_id]["frame_current"] = job_status["frame_current"]
                    if "frame_total" in job_status:
                        jobs_db[job_id]["frame_total"] = job_status["frame_total"]
                    
                    # Manejar finalización de trabajo
                    if job_status.get("status") == "completed":
                        jobs_db[job_id]["status"] = "completed"
                        jobs_db[job_id]["completed_at"] = datetime.now()
                        jobs_db[job_id]["progress"] = 100
                        
                        # Actualizar contador del nodo
                        if "active_jobs" in nodes_db[node_id]:
                            nodes_db[node_id]["active_jobs"] = max(0, nodes_db[node_id]["active_jobs"] - 1)
                        
                        print(f"✅ Trabajo {job_id} completado por nodo {node_id}")
                    
                    elif job_status.get("status") == "failed":
                        jobs_db[job_id]["status"] = "failed"
                        jobs_db[job_id]["error_message"] = job_status.get("error_message", "Error desconocido")
                        jobs_db[job_id]["completed_at"] = datetime.now()
                        
                        # Actualizar contador del nodo
                        if "active_jobs" in nodes_db[node_id]:
                            nodes_db[node_id]["active_jobs"] = max(0, nodes_db[node_id]["active_jobs"] - 1)
                        
                        print(f"❌ Trabajo {job_id} falló en nodo {node_id}: {job_status.get('error_message', 'Error desconocido')}")
        
        return {
            "message": "Heartbeat recibido",
            "server_time": datetime.now().isoformat(),
            "next_heartbeat": (datetime.now() + timedelta(seconds=15)).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error procesando heartbeat de nodo {heartbeat_data.get('node_id', 'unknown')}: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando heartbeat: {str(e)}")


@app.get("/api/v1/nodes/{node_id}/poll")
async def poll_job_for_node(node_id: str):
    """Consultar si hay trabajos disponibles para un nodo específico"""
    try:
        if node_id not in nodes_db:
            raise HTTPException(
                status_code=404, 
                detail="Nodo no registrado"
            )
        
        node_info = nodes_db[node_id]
        
        # Verificar si el nodo puede tomar más trabajos
        max_jobs = node_info.get("capabilities", {}).get("max_concurrent_jobs", 1)
        current_jobs = node_info.get("active_jobs", 0)
        
        if current_jobs >= max_jobs:
            # Nodo ocupado - devolver 204 No Content
            return Response(status_code=204)
        
        # Buscar trabajos pendientes (ordenados por fecha de creación)
        pending_jobs = [
            job for job in jobs_db.values() 
            if job["status"] == "pending"
        ]
        
        if not pending_jobs:
            # No hay trabajos disponibles - devolver 204 No Content
            return Response(status_code=204)
        
        # Ordenar por fecha de creación y tomar el más antiguo
        pending_jobs.sort(key=lambda x: x.get("created_at", datetime.min))
        job = pending_jobs[0]
        job_id = job["id"]
        
        # Asignar trabajo al nodo
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["started_at"] = datetime.now()
        jobs_db[job_id]["assigned_node"] = node_id
        
        # Actualizar contador de trabajos activos del nodo
        if "active_jobs" not in nodes_db[node_id]:
            nodes_db[node_id]["active_jobs"] = 0
        nodes_db[node_id]["active_jobs"] += 1
        nodes_db[node_id]["status"] = "rendering"
        
        print(f"🎬 Trabajo {job_id} asignado a nodo {node_id} ({node_info.get('name', 'Sin nombre')})")
        
        # Preparar datos del trabajo para el nodo (compatible con node_agent.py)
        job_data = {
            "job_id": job_id,  # Usar job_id en lugar de id
            "name": job["name"],
            "start_frame": job.get("frame_start", 1),
            "end_frame": job.get("frame_end", 1),
            "output_format": job.get("output_format", "PNG"),
            "engine": job.get("engine", "CYCLES"),
            "samples": job.get("samples", 128),
            "created_at": job["created_at"].isoformat() if isinstance(job["created_at"], datetime) else str(job["created_at"]),
            "file_path": job.get("file_path", ""),
            "original_filename": job.get("original_filename", "")
        }
        
        return job_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error polling trabajo para nodo {node_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error consultando trabajo: {str(e)}")

# Endpoint alternativo para compatibilidad
@app.get("/api/v1/nodes/{node_id}/poll-job")
async def poll_for_job_alt(node_id: str):
    """Alias para compatibilidad con diferentes versiones del cliente"""
    return await poll_job_for_node(node_id)


# ==================== RUTAS DE ESTADO ====================

@app.get("/api/v1/queue/status")
async def get_queue_status():
    """Obtener estado general de la cola"""
    jobs = list(jobs_db.values())
    total = len(jobs)
    pending = len([j for j in jobs if j["status"] == "pending"])
    processing = len([j for j in jobs if j["status"] == "processing"])
    completed = len([j for j in jobs if j["status"] == "completed"])
    failed = len([j for j in jobs if j["status"] == "failed"])
    cancelled = len([j for j in jobs if j["status"] == "cancelled"])
    
    return {
        "total_jobs": total,
        "pending_jobs": pending,
        "processing_jobs": processing,
        "completed_jobs": completed,
        "failed_jobs": failed,
        "cancelled_jobs": cancelled,
        "queue_health": "healthy" if failed < total * 0.1 else "degraded"
    }

@app.get("/api/v1/nodes", response_model=List[dict])
async def get_nodes():
    """Obtener lista de todos los nodos registrados"""
    # Ya no intentamos actualizar 'local' porque no existe.
    # Solo devolvemos los nodos que se han registrado (como tu worker).
    return list(nodes_db.values())

@app.get("/api/v1/stats/dashboard")
async def get_dashboard_stats():
    """Estadísticas del dashboard - MEJORADO"""
    jobs = list(jobs_db.values())
    nodes = list(nodes_db.values())
    
    # Contar por estado
    pending = sum(1 for j in jobs if j.get("status") == "pending")
    processing = sum(1 for j in jobs if j.get("status") == "processing")
    completed = sum(1 for j in jobs if j.get("status") == "completed")
    failed = sum(1 for j in jobs if j.get("status") == "failed")
    
    # Nodos activos
    current_time = datetime.now()
    active_nodes = 0
    for node in nodes:
        last_seen = node.get("last_seen")
        if isinstance(last_seen, str):
            try:
                last_seen = datetime.fromisoformat(last_seen)
            except:
                continue
        if last_seen and (current_time - last_seen).total_seconds() < 120:
            active_nodes += 1
    
    return {
        "total_jobs": len(jobs),
        "active_jobs": pending + processing,
        "completed_today": completed,
        "failed_jobs": failed,
        "total_nodes": len(nodes),
        "active_nodes": active_nodes,
        "total_render_time": "N/A",
        "queue_efficiency": 95 if completed > 0 else 0,
        "blender_available": get_current_blender_path() is not None
    }

print("✅ Fixes aplicados exitosamente")

@app.get("/api/v1/system/blender-info")
async def get_blender_info():
    """Obtener información detallada de Blender"""
    
    current_path = get_current_blender_path()
    
    if not current_path:
        return {
            "available": False,
            "path": None,
            "version": None,
            "error": "Blender no encontrado",
            "suggestions": [
                "Instalar Blender desde https://www.blender.org/download/",
                "Configurar ruta en Settings → Blender",
                "Usar auto-detección en la configuración"
            ]
        }
    
    verification = verify_blender_path(current_path)
    
    return {
        "available": True,
        "path": current_path,
        "version": verification.get("version"),
        "functional": verification.get("render_capable", False),
        "system": platform.system(),
        "verification": verification,
        "config": app_config["blender"]
    }

# ==================== MANEJO DE ERRORES ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Recurso no encontrado", "error": "NOT_FOUND"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Error interno del servidor", "error": "INTERNAL_ERROR"}
    )

# ==================== EVENTOS DE CICLO DE VIDA ====================

@app.on_event("startup")
async def startup_event():
    """Eventos de inicio de la aplicación"""
    
    print("🚀 Render Queue Manager API v2.0 iniciada")
    print(f"📁 Directorio de uploads: {UPLOAD_DIR}")
    print(f"🎬 Directorio de renders: {OUTPUT_DIR}")
    print(f"⚙️ Archivo de configuración: {CONFIG_FILE}")
    
    current_blender = get_current_blender_path()
    if current_blender:
        verification = verify_blender_path(current_blender)
        print(f"🔧 Blender encontrado: {current_blender}")
        print(f"📋 Versión: {verification.get('version', 'Desconocida')}")
        print(f"✅ Funcional: {'Sí' if verification.get('render_capable', False) else 'No'}")
    else:
        print("❌ Blender no configurado - Configure en Settings → Blender")
    
    print("📖 Documentación disponible en: http://localhost:8000/docs")
    print("❤️  Health check en: http://localhost:8000/health")
    print("⚙️  Configuración de Blender: http://localhost:8000/api/v1/config/blender")
    
    # Iniciar tarea de limpieza automática
    asyncio.create_task(cleanup_old_sessions())

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de cierre de la aplicación"""
    print("🛑 Render Queue Manager API detenida")
    
    # Limpiar sesiones de upload activas
    for session_id, session in upload_sessions.items():
        temp_dir = Path(session["temp_dir"])
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("🧹 Archivos temporales limpiados")

# ==================== TAREAS DE LIMPIEZA ====================

async def cleanup_old_sessions():
    """Limpiar sesiones antiguas automáticamente"""
    while True:
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session in upload_sessions.items():
                # Eliminar sesiones de más de 1 hora
                if (current_time - session["created_at"]).seconds > 3600:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                try:
                    session = upload_sessions[session_id]
                    temp_dir = Path(session["temp_dir"])
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    del upload_sessions[session_id]
                    print(f"🧹 Sesión expirada eliminada: {session_id}")
                except Exception as e:
                    print(f"Error limpiando sesión {session_id}: {e}")
            
            # Ejecutar cada 30 minutos
            await asyncio.sleep(1800)
            
        except Exception as e:
            print(f"Error en tarea de limpieza: {e}")
            await asyncio.sleep(300)  # Reintentar en 5 minutos si hay error


@app.get("/api/v1/jobs/{job_id}/has-results")
async def check_job_has_results(job_id: str):
    """
    Verificar si un trabajo tiene resultados disponibles
    Usado por el frontend para mostrar/ocultar botones
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    # Verificar si hay archivos de output
    has_files = False
    file_count = 0
    output_dir_path = None
    
    # Intentar encontrar directorio de output
    possible_dirs = []
    if job.get("output_path"):
        possible_dirs.append(Path(job["output_path"]))
    possible_dirs.append(OUTPUT_DIR / job_id)
    
    for output_dir in possible_dirs:
        if output_dir.exists():
            output_dir_path = str(output_dir)
            # Buscar archivos de imagen
            extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
            for ext in extensions:
                files = list(output_dir.glob(ext))
                file_count += len(files)
            
            if file_count > 0:
                has_files = True
                break
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "has_results": has_files,
        "file_count": file_count,
        "output_dir": output_dir_path,
        "frames_rendered": job.get("frames_rendered", 0),
        "frames_total": job.get("frames_total", 0),
        "progress": job.get("progress", 0),
        "can_download": has_files,
        "can_view_frames": has_files and file_count > 0,
        "can_delete": True,
        "is_completed": job["status"] == "completed"
    }

@app.get("/api/v1/jobs/{job_id}/debug-status")
async def debug_job_status_detailed(job_id: str):
    """Ver estado detallado de un trabajo para debugging"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    # Contar archivos en disco
    output_dir = OUTPUT_DIR / job_id
    files_on_disk = 0
    if output_dir.exists():
        files_on_disk = len(list(output_dir.glob("*.png"))) + len(list(output_dir.glob("*.jpg")))
    
    # Listar archivos registrados
    output_files = job.get("output_files", [])
    registered_filenames = [f["filename"] for f in output_files]
    
    return {
        "job_id": job_id,
        "name": job.get("name"),
        "status": job["status"],
        "progress": job.get("progress"),
        "frames_rendered": job.get("frames_rendered"),
        "frames_total": job.get("frames_total"),
        "output_files_count": len(output_files),
        "files_on_disk": files_on_disk,
        "match": len(output_files) == files_on_disk,
        "registered_files": registered_filenames[:10],  # Primeros 10
        "output_path": job.get("output_path"),
        "started_at": str(job.get("started_at")),
        "completed_at": str(job.get("completed_at")),
        "render_time": job.get("render_time")
    }


print("✅ Fix definitivo de upload-result aplicado")

# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
