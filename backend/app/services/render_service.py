# app/services/render_service.py - Servicio de renderización
import asyncio
import subprocess
import os
import re
import logging
import platform
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable

from app.core.database import jobs_db, nodes_db, update_job
from app.services.blender_service import blender_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class RenderService:
    """Servicio principal de renderización"""
    
    def __init__(self):
        self.active_processes = {}  # job_id -> subprocess
        self.render_callbacks = {}  # job_id -> callback function
    
    async def render_job_background(self, job_id: str, progress_callback: Optional[Callable] = None):
        """Función principal para renderizar en background con soporte para animaciones"""
        if job_id not in jobs_db:
            logger.error(f"❌ Trabajo no encontrado: {job_id}")
            return False
        
        job = jobs_db[job_id]
        
        try:
            # Actualizar estado inicial
            await self._update_job_status(job_id, {
                "status": "processing",
                "started_at": datetime.now(),
                "progress": 0,
                "frames_rendered": 0
            })
            
            # Actualizar estadísticas del nodo local
            await self._update_local_node_stats(job, "rendering")
            
            # Verificar archivo .blend
            blend_file = job["file_path"]
            if not os.path.exists(blend_file):
                raise Exception(f"Archivo .blend no encontrado: {blend_file}")
            
            # Verificar Blender
            current_blender = blender_service.get_current_blender_path()
            if not current_blender:
                raise Exception("Blender no está configurado o no se encuentra")
            
            logger.info(f"🎬 Iniciando render: {job_id} ({job['name']})")
            
            # Obtener información del archivo para optimizar configuración
            blend_info = blender_service.get_blend_file_info(blend_file)
            
            # Configurar parámetros de render
            render_config = self._prepare_render_config(job, blend_info)
            
            # Ejecutar render
            success = await self._execute_blender_render(
                job_id, 
                blend_file, 
                render_config,
                progress_callback
            )
            
            if success:
                await self._finalize_successful_render(job_id, render_config["output_dir"])
            else:
                await self._finalize_failed_render(job_id, "Render process failed")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error en render {job_id}: {e}")
            await self._finalize_failed_render(job_id, str(e))
            return False
        
        finally:
            # Limpiar proceso activo
            if job_id in self.active_processes:
                del self.active_processes[job_id]
            
            # Liberar nodo local
            await self._update_local_node_stats(job, "online")
    
    def _prepare_render_config(self, job: Dict[str, Any], blend_info: Dict[str, Any]) -> Dict[str, Any]:
        """Preparar configuración de render optimizada"""
        frame_start = job.get("frame_start", 1)
        frame_end = job.get("frame_end", 1)
        total_frames = (frame_end - frame_start) + 1
        
        # Decidir estrategia de output
        use_blend_output = (
            blend_info and 
            not blend_info.get("error") and 
            blend_info.get("output_path") and 
            blend_info["output_path"].strip()
        )
        
        if use_blend_output:
            # Usar configuración del archivo .blend
            output_dir = Path(blend_info["output_path"]).parent
            output_pattern = blend_info["output_path"]
            logger.info(f"📁 Usando output configurado en .blend: {output_pattern}")
        else:
            # Usar configuración por defecto
            output_dir = settings.OUTPUT_DIR / job["id"]
            output_pattern = str(output_dir / "frame_####")
            logger.info(f"📁 Usando output por defecto: {output_pattern}")
        
        # Asegurar que el directorio existe
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "frame_start": frame_start,
            "frame_end": frame_end,
            "total_frames": total_frames,
            "output_dir": output_dir,
            "output_pattern": output_pattern,
            "use_blend_output": use_blend_output,
            "render_engine": job.get("render_engine", "CYCLES"),
            "blend_info": blend_info
        }
    
    async def _execute_blender_render(
        self,
        job_id: str,
        blend_file: str,
        config: Dict[str, Any],
        progress_callback: Optional[Callable] = None,
    ) -> bool:
        """Ejecutar el proceso de render de Blender"""

        current_blender = blender_service.get_current_blender_path()

        # Construir comando de Blender
        if config["use_blend_output"]:
            # Usar configuración interna del .blend
            cmd = [
                current_blender,
                "-b",
                blend_file,
                "-s", str(config["frame_start"]),
                "-e", str(config["frame_end"]),
                "-a",
            ]
        else:
            # Especificar output pattern
            cmd = [
                current_blender,
                "-b",
                blend_file,
                "-o", config["output_pattern"],
                "-s", str(config["frame_start"]),
                "-e", str(config["frame_end"]),
                "-a",
            ]

        # Añadir configuraciones adicionales según el motor
        cmd.extend(self._get_engine_specific_args(config))

        # Entorno y carpeta de trabajo (importante para rutas relativas)
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        cwd = os.path.dirname(blend_file) or None

        logger.info(f"🎬 Ejecutando: {' '.join(cmd)}")
        logger.debug(f"cwd={cwd}")

        try:
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=cwd,
                    env=env,
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=cwd,
                    env=env,
                )

            # Guardar proceso para posible cancelación
            self.active_processes[job_id] = process

            # Monitorear progreso en tiempo real
            success = await self._monitor_render_progress(
                job_id,
                process,
                config,
                progress_callback,
            )
            return success

        except Exception as e:
            logger.error(f"❌ Error ejecutando Blender para {job_id}: {e}")
            return False

        finally:
            # Limpieza de la referencia del proceso
            try:
                self.active_processes.pop(job_id, None)
            except Exception:
                pass

    
    def _get_engine_specific_args(self, config: Dict[str, Any]) -> list:
        """Obtener argumentos específicos del motor de render"""
        args = []
        render_engine = config.get("render_engine", "CYCLES")
        
        # Configuraciones específicas según el motor
        if render_engine == "CYCLES":
            # Habilitar GPU si está disponible
            blend_info = config.get("blend_info", {})
            if blend_info.get("engine_settings", {}).get("use_gpu", False):
                args.extend(["-E", "CYCLES"])
                # Nota: La configuración GPU se maneja mejor desde dentro del archivo .blend
        
        return args
    
    async def _monitor_render_progress(
        self, 
        job_id: str, 
        process: subprocess.Popen,
        config: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Monitorear progreso del render en tiempo real"""
        
        total_frames = config["total_frames"]
        frames_completed = 0
        last_saved_frame = None
        errors = []
        
        logger.info(f"📊 Monitoreando progreso: {total_frames} frames total")
        
        try:
            while True:
                # Verificar si el trabajo fue cancelado
                if job_id in jobs_db and jobs_db[job_id]["status"] == "cancelled":
                    logger.info(f"🛑 Render cancelado por usuario: {job_id}")
                    process.terminate()
                    return False
                
                # Leer salida de Blender
                output_line = process.stdout.readline()
                
                if output_line:
                    line = output_line.strip()
                    
                    # Log del output para debugging
                    if line and not line.startswith('Fra:') and 'Mem:' not in line:
                        logger.debug(f"Blender: {line}")
                    
                    # Detectar frame completado
                    if "Saved:" in line or "Time:" in line:
                        frame_info = self._parse_frame_completion(line)
                        if frame_info:
                            saved_frame = frame_info.get("frame_number")
                            if saved_frame and (last_saved_frame is None or saved_frame != last_saved_frame):
                                frames_completed += 1
                                last_saved_frame = saved_frame
                                
                                # Calcular progreso
                                progress = min(int((frames_completed / total_frames) * 100), 99)
                                
                                # Actualizar estado del trabajo
                                await self._update_job_status(job_id, {
                                    "progress": progress,
                                    "frames_rendered": frames_completed
                                })
                                
                                # Llamar callback si existe
                                if progress_callback:
                                    await progress_callback(job_id, progress, frames_completed, total_frames)
                                
                                logger.info(f"📈 Progreso: Frame {frames_completed}/{total_frames} ({progress}%)")
                    
                    # Detectar errores críticos
                    if any(error_keyword in line for error_keyword in ["Error:", "EXCEPTION", "Traceback", "Segmentation fault"]):
                        errors.append(line)
                        logger.warning(f"⚠️ Error detectado: {line}")
                    
                    # Detectar warnings importantes
                    if any(warning_keyword in line for warning_keyword in ["Warning:", "Cannot find", "Missing"]):
                        logger.warning(f"⚠️ Warning: {line}")
                
                # Verificar si el proceso terminó
                if process.poll() is not None:
                    break
                
                # Pequeña pausa para no sobrecargar CPU
                await asyncio.sleep(0.1)
            
            # Obtener salida final
            stdout, stderr = process.communicate()
            
            # Evaluar resultado final
            return self._evaluate_render_result(job_id, process.returncode, config, errors)
            
        except Exception as e:
            logger.error(f"❌ Error monitoreando progreso de {job_id}: {e}")
            return False
    
    def _parse_frame_completion(self, line: str) -> Optional[Dict[str, Any]]:
        """Parsear línea de output para extraer información de frame completado"""
        frame_info = {}
        
        # Patrón para "Saved: 'path/frame_0001.png'"
        saved_match = re.search(r"Saved:\s*['\"]([^'\"]+)['\"]", line)
        if saved_match:
            saved_file = saved_match.group(1)
            frame_info["saved_file"] = saved_file
            
            # Extraer número de frame
            frame_match = re.search(r'(\d+)\.(?:png|jpg|jpeg|exr|tiff|tif)', saved_file, re.IGNORECASE)
            if frame_match:
                frame_info["frame_number"] = int(frame_match.group(1))
        
        # Patrón para líneas de tiempo "Fra:1 Mem:... Time:..."
        time_match = re.search(r"Fra:(\d+).*?Time:([0-9:.]+)", line)
        if time_match:
            frame_info["frame_number"] = int(time_match.group(1))
            frame_info["render_time"] = time_match.group(2)
        
        return frame_info if frame_info else None
    
    def _evaluate_render_result(
        self, 
        job_id: str, 
        return_code: int, 
        config: Dict[str, Any], 
        errors: list
    ) -> bool:
        """Evaluar el resultado final del render"""
        
        output_dir = config["output_dir"]
        total_frames = config["total_frames"]
        
        # Buscar archivos renderizados
        rendered_files = self._find_rendered_files(output_dir)
        actual_frames = len(rendered_files)
        
        logger.info(f"📊 Resultado del render {job_id}:")
        logger.info(f"   - Código de salida: {return_code}")
        logger.info(f"   - Frames esperados: {total_frames}")
        logger.info(f"   - Frames encontrados: {actual_frames}")
        logger.info(f"   - Directorio: {output_dir}")
        
        # Determinar éxito basado en múltiples factores
        success = (
            return_code == 0 and 
            actual_frames > 0 and
            actual_frames >= total_frames * 0.8  # Al menos 80% de los frames
        )
        
        if success:
            logger.info(f"✅ Render exitoso: {job_id}")
        else:
            logger.warning(f"❌ Render falló o incompleto: {job_id}")
            if errors:
                logger.error(f"   - Errores: {'; '.join(errors[:3])}")  # Mostrar solo los primeros 3
        
        return success
    
    def _find_rendered_files(self, output_dir: Path) -> list:
        """Encontrar archivos renderizados en el directorio de output"""
        if not output_dir.exists():
            return []
        
        # Extensiones de imagen soportadas
        extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif", "*.bmp"]
        rendered_files = []
        
        for ext in extensions:
            # Búsqueda en directorio principal
            rendered_files.extend(list(output_dir.glob(ext)))
            # Búsqueda recursiva en subdirectorios
            rendered_files.extend(list(output_dir.glob(f"**/{ext}")))
        
        return sorted(rendered_files)
    
    async def _update_job_status(self, job_id: str, updates: Dict[str, Any]):
        """Actualizar estado del trabajo de forma thread-safe"""
        if job_id in jobs_db:
            jobs_db[job_id].update(updates)
    
    async def _update_local_node_stats(self, job: Dict[str, Any], status: str):
        """Actualizar estadísticas del nodo local"""
        from app.utils.system_monitor import system_monitor
        
        try:
            system_stats = system_monitor.get_system_stats()
            nodes_db["local"].update({
                "status": status,
                "current_job": job["name"] if status == "rendering" else None,
                "cpu_usage": system_stats["cpu_usage"],
                "memory_usage": system_stats["memory_usage"],
                "last_seen": datetime.now()
            })
        except Exception as e:
            logger.warning(f"⚠️ Error actualizando stats del nodo local: {e}")
    
    async def _finalize_successful_render(self, job_id: str, output_dir: Path):
        """Finalizar render exitoso"""
        rendered_files = self._find_rendered_files(output_dir)
        
        # Calcular tiempo de render
        job = jobs_db[job_id]
        started_at = job.get("started_at")
        render_duration = datetime.now() - started_at if started_at else timedelta(0)
        
        # Actualizar trabajo
        await self._update_job_status(job_id, {
            "status": "completed",
            "progress": 100,
            "completed_at": datetime.now(),
            "frames_rendered": len(rendered_files),
            "output_path": str(output_dir),
            "output_files": [str(f) for f in rendered_files],
            "render_time": str(render_duration).split('.')[0]  # Sin microsegundos
        })
        
        logger.info(f"✅ Render completado: {job_id}")
        logger.info(f"   - {len(rendered_files)} archivos generados")
        logger.info(f"   - Tiempo total: {render_duration}")
        
        # TODO: Generar notificación de completado
        # await self._send_completion_notification(job_id)
    
    async def _finalize_failed_render(self, job_id: str, error_message: str):
        """Finalizar render fallido"""
        job = jobs_db[job_id]
        started_at = job.get("started_at")
        render_duration = datetime.now() - started_at if started_at else timedelta(0)
        
        await self._update_job_status(job_id, {
            "status": "failed",
            "completed_at": datetime.now(),
            "error_message": error_message,
            "render_time": str(render_duration).split('.')[0]
        })
        
        logger.error(f"❌ Render falló: {job_id} - {error_message}")
        
        # TODO: Generar notificación de fallo
        # await self._send_failure_notification(job_id, error_message)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancelar trabajo activo"""
        if job_id in self.active_processes:
            try:
                process = self.active_processes[job_id]
                process.terminate()
                
                # Actualizar estado
                if job_id in jobs_db:
                    jobs_db[job_id].update({
                        "status": "cancelled",
                        "completed_at": datetime.now(),
                        "error_message": "Cancelado por el usuario"
                    })
                
                logger.info(f"🛑 Trabajo cancelado: {job_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error cancelando trabajo {job_id}: {e}")
                return False
        
        return False
    
    def get_active_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Obtener trabajos actualmente renderizando"""
        active_jobs = {}
        
        for job_id, process in self.active_processes.items():
            if process.poll() is None:  # Proceso aún activo
                job = jobs_db.get(job_id)
                if job:
                    active_jobs[job_id] = {
                        "job": job,
                        "pid": process.pid,
                        "started_at": job.get("started_at"),
                        "progress": job.get("progress", 0)
                    }
        
        return active_jobs
    
    def get_render_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de renderizado"""
        total_jobs = len(jobs_db)
        completed_jobs = len([j for j in jobs_db.values() if j["status"] == "completed"])
        failed_jobs = len([j for j in jobs_db.values() if j["status"] == "failed"])
        active_jobs = len(self.active_processes)
        
        # Calcular tiempo total de render
        total_render_time = 0
        for job in jobs_db.values():
            if job.get("render_time"):
                # Parsear formato "HH:MM:SS"
                try:
                    time_parts = job["render_time"].split(":")
                    if len(time_parts) == 3:
                        hours, minutes, seconds = map(int, time_parts)
                        total_render_time += hours * 3600 + minutes * 60 + seconds
                except:
                    pass
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "active_jobs": active_jobs,
            "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            "total_render_time_seconds": total_render_time,
            "average_render_time": total_render_time / completed_jobs if completed_jobs > 0 else 0
        }
    
    def cleanup_old_renders(self, days: int = 7) -> int:
        """Limpiar renders antiguos del disco"""
        from datetime import timedelta
        import shutil
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        for job in list(jobs_db.values()):
            if (job["status"] in ["completed", "failed"] and 
                job.get("completed_at") and 
                job["completed_at"] < cutoff_date and
                job.get("output_path")):
                
                try:
                    output_path = Path(job["output_path"])
                    if output_path.exists():
                        shutil.rmtree(output_path)
                        cleaned_count += 1
                        logger.info(f"🧹 Directorio de render limpiado: {output_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Error limpiando {job['output_path']}: {e}")
        
        return cleaned_count
    
    async def estimate_queue_time(self, job_data: Dict[str, Any]) -> str:
        """Estimar tiempo de espera en cola para un nuevo trabajo"""
        # Obtener trabajos pendientes
        pending_jobs = [j for j in jobs_db.values() if j["status"] == "pending"]
        active_jobs = len(self.active_processes)
        
        if not pending_jobs and active_jobs == 0:
            return "Inmediato"
        
        # Estimar tiempo basado en trabajos en cola
        total_estimated_time = 0
        
        for job in pending_jobs:
            # Usar estimación o tiempo promedio
            if job.get("estimated_time"):
                # TODO: Parsear estimated_time string a segundos
                total_estimated_time += 1800  # 30 min por defecto
            else:
                total_estimated_time += 1800  # 30 min por defecto
        
        # Considerar trabajos activos
        for job_id in self.active_processes:
            job = jobs_db.get(job_id)
            if job:
                # Estimar tiempo restante basado en progreso
                progress = job.get("progress", 0)
                if progress > 0:
                    elapsed = datetime.now() - job.get("started_at", datetime.now())
                    estimated_total = elapsed.total_seconds() * (100 / progress)
                    remaining = max(0, estimated_total - elapsed.total_seconds())
                    total_estimated_time += remaining
                else:
                    total_estimated_time += 1800  # 30 min si no hay progreso
        
        # Formatear tiempo estimado
        if total_estimated_time < 3600:
            return f"~{int(total_estimated_time/60)} minutos"
        elif total_estimated_time < 86400:
            hours = int(total_estimated_time / 3600)
            return f"~{hours} horas"
        else:
            days = int(total_estimated_time / 86400)
            return f"~{days} días"

# Instancia singleton del servicio
render_service = RenderService()