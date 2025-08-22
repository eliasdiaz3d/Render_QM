from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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
from datetime import datetime
from typing import List, Optional, Dict
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

nodes_db = {
    "local": {
        "id": "local",
        "name": f"Local Machine ({platform.node()})",
        "ip": "127.0.0.1",
        "status": "online",
        "cpu_usage": 0,
        "memory_usage": 0,
        "current_job": None,
        "last_seen": datetime.now(),
        "platform": platform.system(),
        "blender_available": False
    }
}

# Almacén temporal para chunks
upload_sessions: Dict[str, dict] = {}

# ==================== FUNCIONES DE RENDER ====================

async def render_job_background(job_id: str):
    """Función para renderizar en background con soporte para animaciones"""
    if job_id not in jobs_db:
        return
    
    job = jobs_db[job_id]
    
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
        output_dir = OUTPUT_DIR / job_id
        output_dir.mkdir(exist_ok=True)
        
        # Verificar que el archivo existe
        if not os.path.exists(blend_file):
            raise Exception(f"Archivo .blend no encontrado: {blend_file}")
        
        # Verificar que Blender está disponible
        current_blender = get_current_blender_path()
        if not current_blender:
            raise Exception("Blender no está configurado o no se encuentra")
        
        # Configurar comando de Blender para animación
        output_pattern = str(output_dir / "frame_####")
        frame_start = job.get("frame_start", 1)
        frame_end = job.get("frame_end", 1)
        total_frames = (frame_end - frame_start) + 1
        
        print(f"🎬 Renderizando animación: frames {frame_start}-{frame_end} ({total_frames} frames)")
        
        # Comando para renderizar animación completa
        cmd = [
            current_blender,
            "-b",  # Background mode
            blend_file,
            "-o", output_pattern,
            "-s", str(frame_start),  # Frame inicial
            "-e", str(frame_end),    # Frame final
            "-a"  # Render animación completa
        ]
        
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
        
        # Leer salida de Blender para obtener progreso real
        while True:
            # Verificar si fue cancelado
            if job["status"] == "cancelled":
                process.terminate()
                return
            
            # Leer una línea de output
            output_line = process.stdout.readline()
            
            if output_line:
                print(f"Blender output: {output_line.strip()}")
                
                # Buscar indicadores de progreso de frame
                if "Saved:" in output_line or "Time:" in output_line:
                    frames_completed += 1
                    job["frames_rendered"] = frames_completed
                    progress = min(int((frames_completed / total_frames) * 100), 99)
                    job["progress"] = progress
                    
                    print(f"📈 Progreso: Frame {frames_completed}/{total_frames} ({progress}%)")
                
                # Detectar errores
                if "Error:" in output_line or "EXCEPTION" in output_line:
                    print(f"❌ Error detectado en Blender: {output_line.strip()}")
            
            # Verificar si el proceso terminó
            if process.poll() is not None:
                break
            
            # Pequeña pausa para no sobrecargar
            await asyncio.sleep(0.1)
        
        # Obtener salida final
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            # Verificar que se renderizaron los frames
            rendered_files = list(output_dir.glob("frame_*.png")) + list(output_dir.glob("frame_*.jpg")) + list(output_dir.glob("frame_*.exr"))
            actual_frames = len(rendered_files)
            
            # Éxito
            job["status"] = "completed"
            job["progress"] = 100
            job["frames_rendered"] = actual_frames
            job["completed_at"] = datetime.now()
            job["output_path"] = str(output_dir)
            
            # Actualizar estadísticas
            duration = job["completed_at"] - job["started_at"]
            job["render_time"] = str(duration).split('.')[0]  # Sin microsegundos
            
            print(f"✅ Render completado para job {job_id}")
            print(f"📊 Frames renderizados: {actual_frames}/{total_frames}")
            print(f"⏱️ Tiempo total: {job['render_time']}")
            
        else:
            # Error
            job["status"] = "failed"
            job["error_message"] = f"Blender error (code {process.returncode}): {stderr}"
            print(f"❌ Error en render: {stderr}")
    
    except subprocess.TimeoutExpired:
        job["status"] = "failed"
        job["error_message"] = "Timeout: El render tardó demasiado tiempo"
        if 'process' in locals():
            process.kill()
    
    except Exception as e:
        job["status"] = "failed"
        job["error_message"] = str(e)
        print(f"❌ Error en render: {e}")
    
    finally:
        # Liberar nodo con estadísticas actualizadas
        system_stats = get_system_stats()
        nodes_db["local"]["status"] = "online"
        nodes_db["local"]["current_job"] = None
        nodes_db["local"]["cpu_usage"] = system_stats["cpu_usage"]
        nodes_db["local"]["memory_usage"] = system_stats["memory_usage"]

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
    """Auto-detecta instalaciones de Blender en el sistema"""
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
        
        # Si solo hay una versión válida, devolverla como seleccionada
        valid_versions = [v for v in detected_versions if v.get("valid", False)]
        
        if len(valid_versions) == 1:
            selected = valid_versions[0]
            return {
                "detected_versions": detected_versions,
                "blender_path": selected["path"],
                "verification": {
                    "valid": True,
                    "version": selected["version"],
                    "error": None
                }
            }
        else:
            # Múltiples versiones o ninguna válida
            return {
                "detected_versions": detected_versions,
                "blender_path": None,
                "verification": {
                    "valid": False,
                    "error": f"Se encontraron {len(valid_versions)} versiones válidas" if valid_versions else "No se encontraron versiones válidas",
                    "version": None
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
async def upload_and_create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    frame_start: int = Form(1),
    frame_end: int = Form(1),
    render_engine: str = Form("CYCLES")
):
    """Subir archivo .blend y crear trabajo de render"""
    
    # Validar archivo
    if not file.filename.endswith('.blend'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .blend")
    
    # Generar ID único
    job_id = str(uuid.uuid4())
    
    # Guardar archivo
    file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {e}")
    
    # Crear trabajo en la base de datos
    job = {
        "id": job_id,
        "name": name,
        "status": "pending",
        "progress": 0,
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None,
        "file_path": str(file_path),
        "original_filename": file.filename,
        "output_path": None,
        "frame_start": frame_start,
        "frame_end": frame_end,
        "frames_total": (frame_end - frame_start) + 1,
        "frames_rendered": 0,
        "render_engine": render_engine,
        "estimated_time": None,
        "error_message": None,
        "file_size": file.size if hasattr(file, 'size') else 0
    }
    
    jobs_db[job_id] = job
    
    # Iniciar render en background
    background_tasks.add_task(render_job_background, job_id)
    
    return {
        "message": "Archivo subido y trabajo creado exitosamente",
        "job_id": job_id,
        "job": job
    }

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
        background_tasks.add_task(render_job_background, job_id)
        
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
    """Obtener lista de todos los trabajos"""
    jobs = list(jobs_db.values())
    # Ordenar por fecha de creación (más recientes primero)
    jobs.sort(key=lambda x: x["created_at"], reverse=True)
    return jobs

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    """Obtener detalles de un trabajo específico"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return jobs_db[job_id]

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

@app.get("/api/v1/jobs/{job_id}/download")
async def download_result(job_id: str, frame: Optional[int] = None):
    """Descargar resultado del render - frame específico o primer frame"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="El trabajo no está completado")
    
    if not job["output_path"]:
        raise HTTPException(status_code=404, detail="No se encontró resultado")
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    image_files = sorted(list(output_dir.glob("frame_*.png")) + list(output_dir.glob("frame_*.jpg")) + list(output_dir.glob("frame_*.exr")))
    
    if not image_files:
        raise HTTPException(status_code=404, detail="No se encontraron imágenes renderizadas")
    
    # Si se especifica un frame, buscar ese frame específico
    if frame is not None:
        frame_file = None
        for img_file in image_files:
            if f"frame_{frame:04d}" in img_file.name:
                frame_file = img_file
                break
        
        if not frame_file:
            raise HTTPException(status_code=404, detail=f"Frame {frame} no encontrado")
        
        return FileResponse(
            path=str(frame_file),
            filename=f"render_{job_id}_frame_{frame:04d}.png",
            media_type="image/png"
        )
    
    # Si no se especifica frame, devolver el primer frame
    return FileResponse(
        path=str(image_files[0]),
        filename=f"render_{job_id}_preview.png",
        media_type="image/png"
    )

@app.get("/api/v1/jobs/{job_id}/frames")
async def get_job_frames(job_id: str):
    """Obtener lista de todos los frames renderizados"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        return {
            "has_frames": False,
            "status": job["status"],
            "message": f"Trabajo en estado: {job['status']}"
        }
    
    if not job["output_path"]:
        return {
            "has_frames": False,
            "message": "No se encontró directorio de salida"
        }
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    image_files = sorted(list(output_dir.glob("frame_*.png")) + list(output_dir.glob("frame_*.jpg")) + list(output_dir.glob("frame_*.exr")))
    
    if not image_files:
        return {
            "has_frames": False,
            "message": "No se encontraron imágenes renderizadas"
        }
    
    # Extraer números de frame
    frames = []
    for img_file in image_files:
        try:
            # Extraer número de frame del nombre del archivo
            import re
            frame_match = re.search(r'frame_(\d+)', img_file.name)
            if frame_match:
                frame_num = int(frame_match.group(1))
                frames.append({
                    "frame_number": frame_num,
                    "filename": img_file.name,
                    "file_size": img_file.stat().st_size,
                    "download_url": f"/api/v1/jobs/{job_id}/download?frame={frame_num}"
                })
        except:
            continue
    
    return {
        "has_frames": True,
        "total_frames": len(frames),
        "frame_start": job.get("frame_start", 1),
        "frame_end": job.get("frame_end", 1),
        "frames": frames,
        "output_dir": str(output_dir),
        "preview_url": f"/api/v1/jobs/{job_id}/download"  # Primer frame como preview
    }

@app.get("/api/v1/jobs/{job_id}/download-all")
async def download_all_frames(job_id: str):
    """Descargar todos los frames como ZIP"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="El trabajo no está completado")
    
    if not job["output_path"]:
        raise HTTPException(status_code=404, detail="No se encontró resultado")
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    image_files = list(output_dir.glob("frame_*.png")) + list(output_dir.glob("frame_*.jpg")) + list(output_dir.glob("frame_*.exr"))
    
    if not image_files:
        raise HTTPException(status_code=404, detail="No se encontraron imágenes renderizadas")
    
    # Crear ZIP en memoria
    import zipfile
    from io import BytesIO
    
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for img_file in sorted(image_files):
            zip_file.write(img_file, img_file.name)
    
    zip_buffer.seek(0)
    
    # Devolver ZIP como respuesta
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=render_{job_id}_all_frames.zip"}
    )

@app.get("/api/v1/jobs/{job_id}/preview")
async def get_job_preview(job_id: str):
    """Obtener preview del render (para mostrar en la interfaz)"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = jobs_db[job_id]
    
    if job["status"] != "completed":
        return {
            "has_preview": False,
            "status": job["status"],
            "message": f"Trabajo en estado: {job['status']}"
        }
    
    if not job["output_path"]:
        return {
            "has_preview": False,
            "message": "No se encontró directorio de salida"
        }
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    image_files = list(output_dir.glob("*.png")) + list(output_dir.glob("*.jpg")) + list(output_dir.glob("*.exr"))
    
    if not image_files:
        return {
            "has_preview": False,
            "message": "No se encontraron imágenes renderizadas"
        }
    
    # Devolver información del primer archivo
    first_image = image_files[0]
    return {
        "has_preview": True,
        "preview_url": f"/api/v1/jobs/{job_id}/download",
        "filename": first_image.name,
        "file_size": first_image.stat().st_size,
        "total_frames": len(image_files),
        "output_dir": str(output_dir)
    }

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
    """Obtener lista de todos los nodos con información actualizada"""
    
    # Actualizar información del nodo local
    system_stats = get_system_stats()
    current_blender = get_current_blender_path()
    
    nodes_db["local"].update({
        "name": f"Local Machine ({platform.node()})",
        "last_seen": datetime.now(),
        "cpu_usage": system_stats["cpu_usage"],
        "memory_usage": system_stats["memory_usage"],
        "platform": platform.system(),
        "blender_available": current_blender is not None,
        "blender_version": verify_blender_path(current_blender).get("version") if current_blender else None,
        "system_info": {
            "cpu_cores": psutil.cpu_count(),
            "memory_total_gb": round(system_stats["memory_total"] / (1024**3), 1),
            "memory_available_gb": round(system_stats["memory_available"] / (1024**3), 1)
        }
    })
    
    nodes = list(nodes_db.values())
    return nodes

@app.get("/api/v1/stats/dashboard")
async def get_dashboard_stats():
    """Obtener estadísticas para el dashboard"""
    jobs = list(jobs_db.values())
    nodes = list(nodes_db.values())
    
    # Calcular estadísticas
    completed_jobs = [j for j in jobs if j["status"] == "completed"]
    total_render_time = 0
    
    for job in completed_jobs:
        if job.get("render_time"):
            # Calcular tiempo en segundos (aproximado)
            total_render_time += 60  # Placeholder
    
    return {
        "total_jobs": len(jobs),
        "active_jobs": len([j for j in jobs if j["status"] in ["processing", "pending"]]),
        "completed_today": len([j for j in jobs if j["status"] == "completed"]),
        "failed_jobs": len([j for j in jobs if j["status"] == "failed"]),
        "total_nodes": len(nodes),
        "active_nodes": len([n for n in nodes if n["status"] == "online"]),
        "total_render_time": f"{total_render_time // 3600}h {(total_render_time % 3600) // 60}m",
        "queue_efficiency": 95 if completed_jobs else 0,
        "blender_available": get_current_blender_path() is not None
    }

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

# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )