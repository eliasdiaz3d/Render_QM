# node_agent.py - Agente principal del nodo de render
import asyncio
import aiohttp
import psutil
import platform
import uuid
import json
import os
import subprocess
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
import hashlib
import shutil
from dataclasses import dataclass, asdict
import yaml

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RenderNode")

@dataclass
class NodeConfig:
    """Configuración del nodo de render"""
    node_name: str = ""
    master_url: str = "http://localhost:8000"
    node_port: int = 8001
    max_concurrent_jobs: int = 1
    temp_dir: str = "./temp"
    output_dir: str = "./renders"
    blender_path: str = ""
    heartbeat_interval: int = 10
    auto_start: bool = True
    gpu_enabled: bool = True
    cpu_cores: int = -1  # -1 = usar todos
    max_memory_gb: int = 8
    priority_weight: float = 1.0
    tags: list = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class SystemStats:
    """Estadísticas del sistema del nodo"""
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    memory_total_gb: float
    disk_free_gb: float
    disk_total_gb: float
    gpu_count: int
    gpu_memory_total: int = 0
    gpu_memory_used: int = 0
    temperature: Dict[str, float] = None
    load_average: float = 0.0

    def __post_init__(self):
        if self.temperature is None:
            self.temperature = {}

@dataclass
class JobStatus:
    """Estado de un trabajo en el nodo"""
    job_id: str
    status: str  # downloading, rendering, uploading, completed, failed
    progress: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    frame_current: int = 0
    frame_total: int = 0
    error_message: str = ""
    output_files: list = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []

class SystemMonitor:
    """Monitor de recursos del sistema"""
    
    @staticmethod
    def get_system_stats() -> SystemStats:
        """Obtener estadísticas actuales del sistema"""
        try:
            # CPU y Memoria
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            # GPU (si está disponible)
            gpu_count = 0
            gpu_memory_total = 0
            gpu_memory_used = 0
            
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                gpu_count = len(gpus)
                if gpus:
                    gpu_memory_total = sum(gpu.memoryTotal for gpu in gpus)
                    gpu_memory_used = sum(gpu.memoryUsed for gpu in gpus)
            except ImportError:
                logger.warning("GPUtil no disponible - monitoreo GPU deshabilitado")
            
            # Temperatura (si está disponible)
            temperature = {}
            try:
                temps = psutil.sensors_temperatures()
                for name, entries in temps.items():
                    if entries:
                        temperature[name] = entries[0].current
            except:
                pass
            
            # Load average (Unix/Linux)
            load_avg = 0.0
            try:
                if hasattr(os, 'getloadavg'):
                    load_avg = os.getloadavg()[0]
            except:
                pass
            
            return SystemStats(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_gb=memory.available / (1024**3),
                memory_total_gb=memory.total / (1024**3),
                disk_free_gb=disk.free / (1024**3),
                disk_total_gb=disk.total / (1024**3),
                gpu_count=gpu_count,
                gpu_memory_total=gpu_memory_total,
                gpu_memory_used=gpu_memory_used,
                temperature=temperature,
                load_average=load_avg
            )
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del sistema: {e}")
            return SystemStats(
                cpu_percent=0, memory_percent=0, memory_available_gb=0,
                memory_total_gb=0, disk_free_gb=0, disk_total_gb=0, gpu_count=0
            )

    @staticmethod
    def get_node_info() -> Dict[str, Any]:
        """Obtener información estática del nodo"""
        return {
            "hostname": platform.node(),
            "platform": platform.system(),
            "platform_version": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cpu_cores_physical": psutil.cpu_count(logical=False),
            "cpu_cores_logical": psutil.cpu_count(logical=True),
            "python_version": platform.python_version(),
            "node_agent_version": "1.0.0"
        }

class FileTransferManager:
    """Gestor de transferencia de archivos"""
    
    def __init__(self, temp_dir: str, master_url: str):
        self.temp_dir = Path(temp_dir)
        self.master_url = master_url
        self.temp_dir.mkdir(exist_ok=True)
        
    async def download_job_files(self, job_id: str, job_data: Dict) -> str:
        """Descargar archivos necesarios para el trabajo"""
        try:
            logger.info(f"Descargando archivos para trabajo {job_id}")
            
            # Crear directorio específico para este trabajo
            job_dir = self.temp_dir / job_id
            job_dir.mkdir(exist_ok=True)
            
            # Descargar archivo .blend principal
            blend_url = f"{self.master_url}/api/v1/jobs/{job_id}/download-blend"
            blend_path = job_dir / f"{job_id}.blend"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(blend_url) as response:
                    if response.status == 200:
                        with open(blend_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        logger.info(f"Archivo .blend descargado: {blend_path}")
                    else:
                        raise Exception(f"Error descargando .blend: HTTP {response.status}")
            
            # TODO: Descargar assets adicionales si es necesario
            # - Texturas
            # - Cachés
            # - Referencias externas
            
            return str(blend_path)
            
        except Exception as e:
            logger.error(f"Error descargando archivos para {job_id}: {e}")
            raise
    
    async def upload_results(self, job_id: str, output_files: list) -> bool:
        """Subir resultados del render al master"""
        try:
            logger.info(f"Subiendo resultados para trabajo {job_id}")
            
            async with aiohttp.ClientSession() as session:
                for file_path in output_files:
                    if not os.path.exists(file_path):
                        continue
                        
                    file_name = os.path.basename(file_path)
                    upload_url = f"{self.master_url}/api/v1/jobs/{job_id}/upload-result"
                    
                    with open(file_path, 'rb') as f:
                        data = aiohttp.FormData()
                        data.add_field('file', f, filename=file_name)
                        
                        async with session.post(upload_url, data=data) as response:
                            if response.status == 200:
                                logger.info(f"Archivo subido: {file_name}")
                            else:
                                logger.error(f"Error subiendo {file_name}: HTTP {response.status}")
                                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error subiendo resultados para {job_id}: {e}")
            return False
    
    def cleanup_job_files(self, job_id: str):
        """Limpiar archivos temporales del trabajo"""
        try:
            job_dir = self.temp_dir / job_id
            if job_dir.exists():
                shutil.rmtree(job_dir)
                logger.info(f"Archivos temporales limpiados para {job_id}")
        except Exception as e:
            logger.error(f"Error limpiando archivos para {job_id}: {e}")

class RenderExecutor:
    """Ejecutor de renders usando Blender"""
    
    def __init__(self, config: NodeConfig):
        self.config = config
        self.current_process = None
        
    async def execute_render(self, job_id: str, blend_file: str, job_data: Dict, 
                           progress_callback=None) -> tuple[bool, list]:
        """Ejecutar render de un trabajo"""
        output_files = []
        
        try:
            logger.info(f"Iniciando render del trabajo {job_id}")
            
            # Configurar parámetros de render
            frame_start = job_data.get("frame_start", 1)
            frame_end = job_data.get("frame_end", 1) 
            render_engine = job_data.get("render_engine", "CYCLES")
            
            # Directorio de salida
            output_dir = Path(self.config.output_dir) / job_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Patrón de archivo de salida
            output_pattern = str(output_dir / "frame_####")
            
            # Construir comando de Blender
            cmd = [
                self.config.blender_path,
                "-b",  # Background mode
                blend_file,
                "-o", output_pattern,
                "-s", str(frame_start),
                "-e", str(frame_end),
                "-a"  # Render animation
            ]
            
            # Añadir configuraciones específicas
            if render_engine == "CYCLES":
                if self.config.gpu_enabled:
                    cmd.extend(["-P", self._create_gpu_script()])
            
            logger.info(f"Ejecutando comando: {' '.join(cmd)}")
            
            # Ejecutar Blender
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Monitorear progreso
            frame_count = (frame_end - frame_start) + 1
            frames_completed = 0
            
            while True:
                # Leer output de Blender
                output_line = self.current_process.stdout.readline()
                
                if output_line:
                    line = output_line.strip()
                    logger.debug(f"Blender: {line}")
                    
                    # Detectar frame completado
                    if "Saved:" in line:
                        frames_completed += 1
                        progress = int((frames_completed / frame_count) * 100)
                        
                        if progress_callback:
                            await progress_callback(progress, frames_completed, frame_count)
                        
                        # Extraer archivo guardado
                        if "'" in line:
                            saved_file = line.split("'")[1]
                            if os.path.exists(saved_file):
                                output_files.append(saved_file)
                
                # Verificar si el proceso terminó
                if self.current_process.poll() is not None:
                    break
                
                await asyncio.sleep(0.1)
            
            # Obtener código de salida
            return_code = self.current_process.returncode
            
            if return_code == 0:
                logger.info(f"Render completado exitosamente: {job_id}")
                return True, output_files
            else:
                stderr_output = self.current_process.stderr.read()
                logger.error(f"Render falló: {stderr_output}")
                return False, []
                
        except Exception as e:
            logger.error(f"Error ejecutando render {job_id}: {e}")
            return False, []
        finally:
            self.current_process = None
    
    def _create_gpu_script(self) -> str:
        """Crear script para habilitar GPU en Cycles"""
        gpu_script = """
import bpy
import cycles

# Habilitar GPU para Cycles
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'

# Configurar dispositivos
cycles.init()
prefs = bpy.context.preferences
cprefs = prefs.addons['cycles'].preferences

# Habilitar todos los dispositivos GPU disponibles
for device in cprefs.devices:
    if device.type == 'CUDA' or device.type == 'OPENCL' or device.type == 'OPTIX':
        device.use = True
        print(f"GPU habilitada: {device.name}")
"""
        
        script_path = self.config.temp_dir / "gpu_setup.py"
        with open(script_path, 'w') as f:
            f.write(gpu_script)
        
        return str(script_path)
    
    def cancel_current_render(self):
        """Cancelar render actual"""
        if self.current_process:
            logger.info("Cancelando render actual")
            self.current_process.terminate()
            self.current_process = None

class RenderNode:
    """Nodo de render principal"""
    
    def __init__(self, config_path: str = "node_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.node_id = self._generate_node_id()
        self.status = "offline"
        self.current_jobs = {}
        self.registered = False
        
        # Inicializar componentes
        self.system_monitor = SystemMonitor()
        self.file_transfer = FileTransferManager(self.config.temp_dir, self.config.master_url)
        self.render_executor = RenderExecutor(self.config)
        
        # Crear directorios necesarios
        os.makedirs(self.config.temp_dir, exist_ok=True)
        os.makedirs(self.config.output_dir, exist_ok=True)
    
    def _load_config(self) -> NodeConfig:
        """Cargar configuración del archivo YAML"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_dict = yaml.safe_load(f)
                    return NodeConfig(**config_dict)
            else:
                # Crear configuración por defecto
                config = NodeConfig()
                self._save_config(config)
                return config
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return NodeConfig()
    
    def _save_config(self, config: NodeConfig):
        """Guardar configuración al archivo YAML"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(asdict(config), f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def _generate_node_id(self) -> str:
        """Generar ID único para este nodo"""
        # Usar hostname + MAC address para generar ID consistente
        hostname = platform.node()
        try:
            import uuid
            mac = uuid.getnode()
            node_string = f"{hostname}-{mac}"
            return hashlib.md5(node_string.encode()).hexdigest()[:16]
        except:
            return str(uuid.uuid4())[:16]
    
    async def register_with_master(self) -> bool:
        """Registrar este nodo con el servidor master"""
        try:
            node_info = self.system_monitor.get_node_info()
            system_stats = self.system_monitor.get_system_stats()
            
            registration_data = {
                "node_id": self.node_id,
                "node_name": self.config.node_name or f"Node-{self.node_id[:8]}",
                "node_info": node_info,
                "system_stats": asdict(system_stats),
                "config": {
                    "max_concurrent_jobs": self.config.max_concurrent_jobs,
                    "gpu_enabled": self.config.gpu_enabled,
                    "cpu_cores": self.config.cpu_cores,
                    "max_memory_gb": self.config.max_memory_gb,
                    "tags": self.config.tags
                },
                "capabilities": {
                    "blender_available": os.path.exists(self.config.blender_path),
                    "gpu_rendering": self.config.gpu_enabled and system_stats.gpu_count > 0,
                    "concurrent_jobs": self.config.max_concurrent_jobs
                }
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.master_url}/api/v1/nodes/register"
                async with session.post(url, json=registration_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Nodo registrado exitosamente: {result}")
                        self.registered = True
                        self.status = "idle"
                        return True
                    else:
                        logger.error(f"Error registrando nodo: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error registrando con master: {e}")
            return False
    
    async def send_heartbeat(self):
        """Enviar heartbeat al master"""
        if not self.registered:
            return
            
        try:
            system_stats = self.system_monitor.get_system_stats()
            
            heartbeat_data = {
                "node_id": self.node_id,
                "status": self.status,
                "system_stats": asdict(system_stats),
                "active_jobs": len(self.current_jobs),
                "job_statuses": {job_id: asdict(job_status) 
                               for job_id, job_status in self.current_jobs.items()},
                "timestamp": datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.master_url}/api/v1/nodes/heartbeat"
                async with session.post(url, json=heartbeat_data) as response:
                    if response.status != 200:
                        logger.warning(f"Error enviando heartbeat: HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Error enviando heartbeat: {e}")
    
    async def poll_for_jobs(self):
        """Consultar por nuevos trabajos"""
        if not self.registered or len(self.current_jobs) >= self.config.max_concurrent_jobs:
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.master_url}/api/v1/nodes/{self.node_id}/poll-job"
                async with session.get(url) as response:
                    if response.status == 200:
                        job_data = await response.json()
                        if job_data:
                            await self._process_new_job(job_data)
                    elif response.status != 204:  # 204 = No jobs available
                        logger.warning(f"Error consultando trabajos: HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Error consultando trabajos: {e}")
    
    async def _process_new_job(self, job_data: Dict):
        """Procesar un nuevo trabajo asignado"""
        job_id = job_data["job_id"]
        logger.info(f"Nuevo trabajo asignado: {job_id}")
        
        # Crear estado del trabajo
        job_status = JobStatus(
            job_id=job_id,
            status="downloading",
            start_time=datetime.now()
        )
        self.current_jobs[job_id] = job_status
        
        # Ejecutar trabajo en background
        asyncio.create_task(self._execute_job_workflow(job_id, job_data))
    
    async def _execute_job_workflow(self, job_id: str, job_data: Dict):
        """Ejecutar workflow completo de un trabajo"""
        job_status = self.current_jobs[job_id]
        
        try:
            # Fase 1: Descargar archivos
            job_status.status = "downloading"
            blend_file = await self.file_transfer.download_job_files(job_id, job_data)
            
            # Fase 2: Renderizar
            job_status.status = "rendering"
            
            async def progress_callback(progress, frame_current, frame_total):
                job_status.progress = progress
                job_status.frame_current = frame_current
                job_status.frame_total = frame_total
            
            success, output_files = await self.render_executor.execute_render(
                job_id, blend_file, job_data, progress_callback
            )
            
            if success:
                # Fase 3: Subir resultados
                job_status.status = "uploading"
                upload_success = await self.file_transfer.upload_results(job_id, output_files)
                
                if upload_success:
                    job_status.status = "completed"
                    job_status.progress = 100
                    job_status.output_files = output_files
                else:
                    job_status.status = "failed"
                    job_status.error_message = "Error subiendo resultados"
            else:
                job_status.status = "failed"
                job_status.error_message = "Error durante el render"
            
        except Exception as e:
            logger.error(f"Error ejecutando trabajo {job_id}: {e}")
            job_status.status = "failed"
            job_status.error_message = str(e)
        
        finally:
            job_status.end_time = datetime.now()
            
            # Limpiar archivos temporales después de un tiempo
            await asyncio.sleep(300)  # 5 minutos
            self.file_transfer.cleanup_job_files(job_id)
            
            # Remover trabajo de la lista activa
            if job_id in self.current_jobs:
                del self.current_jobs[job_id]
    
    async def start(self):
        """Iniciar el nodo de render"""
        logger.info("Iniciando nodo de render...")
        
        # Verificar configuración
        if not os.path.exists(self.config.blender_path):
            logger.error(f"Blender no encontrado en: {self.config.blender_path}")
            return
        
        # Registrar con master
        logger.info("Registrando con servidor master...")
        max_retries = 5
        for attempt in range(max_retries):
            if await self.register_with_master():
                break
            logger.warning(f"Intento {attempt + 1}/{max_retries} fallido, reintentando en 10s...")
            await asyncio.sleep(10)
        else:
            logger.error("No se pudo registrar con el servidor master")
            return
        
        logger.info(f"Nodo iniciado exitosamente: {self.node_id}")
        
        # Loops principales
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        job_polling_task = asyncio.create_task(self._job_polling_loop())
        
        try:
            await asyncio.gather(heartbeat_task, job_polling_task)
        except KeyboardInterrupt:
            logger.info("Deteniendo nodo...")
            heartbeat_task.cancel()
            job_polling_task.cancel()
    
    async def _heartbeat_loop(self):
        """Loop de heartbeat"""
        while True:
            try:
                await self.send_heartbeat()
                await asyncio.sleep(self.config.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en heartbeat loop: {e}")
                await asyncio.sleep(5)
    
    async def _job_polling_loop(self):
        """Loop de consulta de trabajos"""
        while True:
            try:
                await self.poll_for_jobs()
                await asyncio.sleep(5)  # Consultar cada 5 segundos
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en job polling loop: {e}")
                await asyncio.sleep(10)

# Configuración de ejemplo
def create_sample_config():
    """Crear configuración de ejemplo"""
    config = NodeConfig(
        node_name="RenderNode-001",
        master_url="http://192.168.1.100:8000",
        node_port=8001,
        max_concurrent_jobs=1,
        temp_dir="./temp_renders",
        output_dir="./completed_renders",
        blender_path="/usr/bin/blender",  # Ajustar según OS
        heartbeat_interval=10,
        auto_start=True,
        gpu_enabled=True,
        cpu_cores=-1,
        max_memory_gb=8,
        priority_weight=1.0,
        tags=["gpu", "cycles", "production"]
    )
    
    with open("node_config.yaml", "w") as f:
        yaml.dump(asdict(config), f, default_flow_style=False)
    
    print("Configuración de ejemplo creada en node_config.yaml")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Nodo de Render Distribuido")
    parser.add_argument("--config", default="node_config.yaml", help="Archivo de configuración")
    parser.add_argument("--create-config", action="store_true", help="Crear configuración de ejemplo")
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
    else:
        # Iniciar nodo
        node = RenderNode(args.config)
        asyncio.run(node.start())