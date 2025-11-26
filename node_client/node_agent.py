# node_agent.py - Versión Robusta: Intervalo Seguro, Thread-Safe y Anti-Spam
import asyncio
import aiohttp
import psutil
import platform
import uuid
import json
import re
import os
import subprocess
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
import hashlib
import shutil
from dataclasses import dataclass, asdict, fields
import yaml
import signal
import sys

# IMPORTANTE: Configuración específica para Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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
    temp_dir: str = "./temp_node"
    output_dir: str = "./renders_node"
    blender_path: str = ""
    heartbeat_interval: int = 5  # RESTAURADO A 5s: 15s causaba timeouts en el servidor
    auto_start: bool = True
    gpu_enabled: bool = True
    cpu_cores: int = -1
    tags: list = None
    connection_timeout: int = 30
    request_timeout: int = 300

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class SystemStats:
    """Estadísticas del sistema del nodo"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_total_gb: float = 0.0
    memory_available_gb: float = 0.0
    gpu_count: int = 0
    gpu_memory_used: int = 0
    temperature: Dict[str, float] = None

    def __post_init__(self):
        if self.temperature is None:
            self.temperature = {}

@dataclass
class JobStatus:
    """Estado de un trabajo en el nodo"""
    job_id: str
    status: str
    progress: int = 0
    start_time: Optional[datetime] = None
    frame_current: int = 0
    frame_total: int = 0
    error_message: str = ""

class SystemMonitor:
    """Monitor de recursos del sistema"""
    @staticmethod
    def get_system_stats() -> SystemStats:
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            return SystemStats(
                cpu_percent=cpu,
                memory_percent=mem.percent,
                memory_total_gb=mem.total / (1024**3),
                memory_available_gb=mem.available / (1024**3),
                gpu_count=0
            )
        except Exception as e:
            return SystemStats()

class FileTransferManager:
    """Gestor de transferencia de archivos"""
    
    def __init__(self, temp_dir: str, master_url: str):
        self.temp_dir = Path(temp_dir).resolve()
        self.master_url = master_url
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_job_files(self, job_id: str, session: aiohttp.ClientSession) -> Optional[str]:
        try:
            job_dir = self.temp_dir / job_id
            if job_dir.exists(): shutil.rmtree(job_dir)
            job_dir.mkdir(parents=True, exist_ok=True)
            
            url = f"{self.master_url}/api/v1/jobs/{job_id}/download"
            zip_path = job_dir / f"{job_id}.zip"
            
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Error descarga HTTP {response.status}")
                    return None
                with open(zip_path, 'wb') as f:
                    f.write(await response.read())
            
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(job_dir)
            
            blend_files = list(job_dir.rglob("*.blend"))
            if blend_files: return str(blend_files[0])
            return None
        except Exception as e:
            logger.error(f"Error descargando archivos: {e}")
            return None

    async def upload_single_file(self, job_id: str, file_path: str, session: aiohttp.ClientSession) -> bool:
        if not os.path.exists(file_path): 
            print(f"❌ ERROR: Archivo a subir no existe: {file_path}")
            return False
            
        try:
            url = f"{self.master_url}/api/v1/jobs/{job_id}/upload-result"
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=os.path.basename(file_path))
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        print(f"✅ Subida OK: {os.path.basename(file_path)}")
                        return True
                    else:
                        print(f"⚠️ Fallo subida {response.status}: {await response.text()}")
                        return False
        except Exception as e:
            logger.error(f"Error subiendo archivo: {e}")
            return False

    def cleanup_job_files(self, job_id: str):
        try:
            shutil.rmtree(self.temp_dir / job_id, ignore_errors=True)
        except: pass

class RenderExecutor:
    """Ejecutor de render NO BLOQUEANTE"""
    
    def __init__(self, config: NodeConfig):
        self.config = config
        self.current_process = None

    def create_gpu_script(self, job_dir: Path) -> str:
        script_path = job_dir / "gpu_setup.py"
        code = """
import bpy
try:
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'CUDA'
    for device in cprefs.devices:
        if device.type in {'CUDA', 'OPTIX'}:
            device.use = True
except: pass
"""
        with open(script_path, 'w') as f:
            f.write(code)
        return str(script_path)

    async def execute_render(self, job_id: str, blend_file: str, job_data: Dict, 
                           on_progress=None, on_image_saved=None) -> tuple[bool, list]:
        try:
            blend_path = Path(blend_file).resolve()
            job_dir = blend_path.parent
            output_dir = job_dir / "output"
            output_dir.mkdir(exist_ok=True, parents=True)
            
            start = job_data.get('start_frame', 1)
            end = job_data.get('end_frame', 1)
            total = (end - start) + 1
            
            cmd = [
                self.config.blender_path,
                "-b", str(blend_path),
                "-o", str(output_dir / "frame_####"),
                "-s", str(start),
                "-e", str(end),
                "-a"
            ]
            
            if self.config.gpu_enabled:
                gpu_script = self.create_gpu_script(job_dir)
                cmd.extend(["-P", gpu_script])

            logger.info(f"Ejecutando Blender...")
            self.current_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(job_dir),
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            )
            
            regex_frame = re.compile(r"Fra:(\d+)")
            regex_saved = re.compile(r"Saved: '(.+)'")
            
            async def read_stream(stream, name):
                while True:
                    line = await stream.readline()
                    if not line: break
                    decoded = line.decode('utf-8', errors='replace').strip()
                    if not decoded: continue
                    
                    frame_match = regex_frame.search(decoded)
                    if frame_match and on_progress:
                        current = int(frame_match.group(1))
                        done = max(0, current - start)
                        percent = min(int((done / total) * 100), 99)
                        
                        if asyncio.iscoroutinefunction(on_progress):
                            await on_progress(current, percent)
                        else:
                            on_progress(current, percent)
                        print(f"\r⏳ Renderizando: {percent}% (Frame {current})", end="")
                    
                    saved_match = regex_saved.search(decoded)
                    if saved_match and on_image_saved:
                        raw_path = saved_match.group(1).replace("'", "").replace('"', "").strip()
                        if not os.path.isabs(raw_path):
                            if os.path.basename(raw_path) == raw_path:
                                full_path = output_dir / raw_path
                            else:
                                full_path = (job_dir / raw_path).resolve()
                        else:
                            full_path = Path(raw_path)
                            
                        print(f"\n💾 Detectado: {full_path.name}")
                        if asyncio.iscoroutinefunction(on_image_saved):
                            await on_image_saved(str(full_path))
                        else:
                            on_image_saved(str(full_path))

            await asyncio.gather(
                read_stream(self.current_process.stdout, "stdout"),
                read_stream(self.current_process.stderr, "stderr")
            )
            
            if self.current_process:
                code = await self.current_process.wait()
                self.current_process = None
                return code == 0, [str(f) for f in output_dir.glob("*") if f.is_file()]
            return False, []

        except asyncio.CancelledError:
            if self.current_process:
                self.current_process.kill()
            raise
        except Exception as e:
            logger.error(f"Error crítico en render: {e}")
            return False, []

class RenderNode:
    """Nodo Principal"""
    
    def __init__(self):
        self.config = self._load_config()
        self.node_id = self._generate_id()
        self.status = "online"
        self.current_jobs = {}
        self.jobs_lock = asyncio.Lock() # Lock para proteger current_jobs
        self.registered = False
        self._shutdown = False
        self.last_heartbeat = 0
        self.session = None
        self.last_update_sent_time = 0 
        
        self.system_monitor = SystemMonitor()
        self.file_transfer = FileTransferManager(self.config.temp_dir, self.config.master_url)
        self.render_executor = RenderExecutor(self.config)
        
        Path(self.config.temp_dir).mkdir(exist_ok=True)

    def _load_config(self) -> NodeConfig:
        if os.path.exists("node_config.yaml"):
            try:
                with open("node_config.yaml") as f:
                    data = yaml.safe_load(f)
                    if data:
                        valid_keys = {f.name for f in fields(NodeConfig)}
                        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
                        return NodeConfig(**filtered_data)
            except Exception: pass
        return NodeConfig()

    def _generate_id(self) -> str:
        mac = uuid.getnode()
        return hashlib.md5(f"{platform.node()}-{mac}".encode()).hexdigest()[:16]

    async def register(self):
        if not self.session: return False
        data = {
            "node_id": self.node_id,
            "node_name": self.config.node_name or platform.node(),
            "status": "online",
            "capabilities": {
                "max_concurrent_jobs": self.config.max_concurrent_jobs,
                "gpu_enabled": self.config.gpu_enabled
            },
            "system_info": {"platform": platform.system()}
        }
        try:
            url = f"{self.config.master_url}/api/v1/nodes/register"
            async with self.session.post(url, json=data) as resp:
                if resp.status == 200:
                    self.registered = True
                    logger.info(f"✅ Nodo registrado: {self.node_id}")
                    return True
        except: pass
        return False

    async def send_heartbeat(self, force=False):
        """Envía latido CON INFORMACIÓN DE JOBS Y PROTECCIÓN DE HILOS"""
        if not self.registered or not self.session: return

        now = time.time()
        if not force and (now - self.last_heartbeat) < self.config.heartbeat_interval:
            return
        self.last_heartbeat = now

        job_statuses_payload = {}
        
        # Usamos el Lock para leer current_jobs de forma segura
        async with self.jobs_lock:
            for jid, job in self.current_jobs.items():
                job_statuses_payload[jid] = {
                    "status": job.status,
                    "progress": job.progress,
                    "frame_current": job.frame_current,
                    "frame_total": job.frame_total,
                    "error_message": job.error_message
                }

        stats = asdict(self.system_monitor.get_system_stats())
        data = {
            "node_id": self.node_id,
            "status": self.status,
            "system_stats": stats,
            "job_statuses": job_statuses_payload,
            "timestamp": datetime.now().isoformat()
        }

        try:
            url = f"{self.config.master_url}/api/v1/nodes/heartbeat"
            async with self.session.post(url, json=data) as resp:
                if resp.status != 200:
                    pass
        except Exception as e:
            print(f"⚠️ Error heartbeat: {e}")

    async def update_job_status_on_master(self, job_status: JobStatus, force=False):
        """Envía actualización con Throttling y caché de último estado"""
        if not self.session: return
        
        # Crea una clave única para este job
        cache_key = f"{job_status.job_id}_last_status"
        last_sent = getattr(self, cache_key, None)
        
        # Si el estado no cambió, no envíes update (excepto si es force)
        current_state = (job_status.status, job_status.progress)
        if not force and last_sent == current_state:
            return

        now = time.time()
        if not force and (now - self.last_update_sent_time) < 1.0:
            return
            
        self.last_update_sent_time = now

        try:
            status_data = {
                "status": job_status.status,
                "progress": job_status.progress,
                "error_message": job_status.error_message,
                "frames_rendered": job_status.frame_current
            }
            
            url = f"{self.config.master_url}/api/v1/jobs/{job_status.job_id}/update-status"
            async with self.session.post(url, json=status_data) as resp:
                if resp.status == 200:
                    # Guarda el último estado enviado exitosamente
                    setattr(self, cache_key, current_state)
                    print(f"📡 Update {job_status.status} {job_status.progress}% OK")
                else:
                    text = await resp.text()
                    print(f"❌ Server rechazó update ({resp.status}): {text}")
                    
        except Exception as e:
            logger.error(f"Error enviando update: {e}")

    async def process_job(self, job_data: Dict):
        job_id = job_data['job_id']
        logger.info(f"🎬 Iniciando trabajo {job_id}")
        
        start = job_data.get('start_frame', 1)
        end = job_data.get('end_frame', 1)
        
        job_status = JobStatus(
            job_id=job_id,
            status="rendering", # Marcamos rendering desde el inicio para evitar estados desconocidos
            start_time=datetime.now(),
            frame_total=(end - start) + 1
        )
        
        # Protegemos la escritura en current_jobs
        async with self.jobs_lock:
            self.current_jobs[job_id] = job_status
            
        self.status = "rendering"

        try:
            blend_file = await self.file_transfer.download_job_files(job_id, self.session)
            if not blend_file: raise Exception("Fallo descarga")
            
            async def on_progress(frame, percent):
                job_status.frame_current = frame
                job_status.progress = percent
                job_status.status = "rendering"
                await self.update_job_status_on_master(job_status, force=False)

            async def on_save(path):
                uploaded = await self.file_transfer.upload_single_file(job_id, path, self.session)
                if uploaded:
                    await self.update_job_status_on_master(job_status, force=True)

            success, files = await self.render_executor.execute_render(
                job_id, blend_file, job_data, on_progress, on_save
            )
            
            if success:
                job_status.status = "completed"
                job_status.progress = 100
                logger.info(f"✨ Trabajo {job_id} FINALIZADO")
                await self.update_job_status_on_master(job_status, force=True)
            else:
                raise Exception("Blender error")

        except asyncio.CancelledError:
            logger.info("Trabajo cancelado por cierre del nodo")
        except Exception as e:
            logger.error(f"Fallo trabajo {job_id}: {e}")
            job_status.status = "failed"
            job_status.error_message = str(e)
            await self.update_job_status_on_master(job_status, force=True)
        
        finally:
            await asyncio.sleep(2)
            self.file_transfer.cleanup_job_files(job_id)
            
            # Protegemos el borrado
            async with self.jobs_lock:
                if job_id in self.current_jobs:
                    del self.current_jobs[job_id]
            
            self.status = "online"
            await self.send_heartbeat(force=True)

    async def shutdown(self):
        """Cierre ordenado de recursos y tareas"""
        print("\n🛑 Apagando nodo...")
        self._shutdown = True
        
        # Matar Blender si corre
        if self.render_executor.current_process:
            try:
                self.render_executor.current_process.kill()
            except: pass

        # Cerrar sesión HTTP al final
        if self.session and not self.session.closed:
            await self.session.close()
            
        print("👋 Bye!")

    async def loop(self):
        logger.info("Iniciando nodo...")
        
        timeout = aiohttp.ClientTimeout(total=300)
        connector = aiohttp.TCPConnector(limit=100)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            self.session = session
            
            while not await self.register():
                if self._shutdown: break
                await asyncio.sleep(5)

            async def heartbeat_loop():
                while not self._shutdown:
                    await self.send_heartbeat()
                    await asyncio.sleep(self.config.heartbeat_interval)

            async def polling_loop():
                while not self._shutdown:
                    if len(self.current_jobs) < self.config.max_concurrent_jobs:
                        try:
                            url = f"{self.config.master_url}/api/v1/nodes/{self.node_id}/poll"
                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    if data:
                                        asyncio.create_task(self.process_job(data))
                        except: pass
                    await asyncio.sleep(5)

            # Usamos return_exceptions para que el shutdown no lance error
            await asyncio.gather(heartbeat_loop(), polling_loop(), return_exceptions=True)

if __name__ == "__main__":
    node = RenderNode()
    
    try:
        asyncio.run(node.loop())
    except KeyboardInterrupt:
        pass
    finally:
        # Aseguramos limpieza si asyncio.run aborta
        if node.render_executor.current_process:
             try: node.render_executor.current_process.kill() 
             except: pass
        print("👋 Nodo apagado correctamente.")