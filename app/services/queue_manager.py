# ========== backend/app/services/queue_manager.py ==========
"""
Gestor principal de la cola de render
"""
import asyncio
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.job import Job, JobStatus
from ..models.node import Node
from ..core.database import SessionLocal

class QueueManager:
    def __init__(self):
        self.is_processing = False
        self.processing_task = None
        self.assigned_jobs = {}  # {job_id: node_id}
    
    async def start_processing(self):
        """Iniciar procesamiento automático de la cola"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.processing_task = asyncio.create_task(self._process_queue_loop())
        print("🚀 Queue Manager iniciado")
    
    async def stop_processing(self):
        """Detener procesamiento de la cola"""
        self.is_processing = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        print("🛑 Queue Manager detenido")
    
    async def _process_queue_loop(self):
        """Loop principal de procesamiento"""
        while self.is_processing:
            try:
                db = SessionLocal()
                try:
                    # Buscar trabajo pendiente
                    job = await self.get_next_job(db)
                    if job:
                        # Buscar nodo disponible
                        node = await self.assign_node(job, db)
                        if node:
                            await self.start_job(job, node, db)
                        else:
                            print("⏳ No hay nodos disponibles")
                    
                    # Verificar trabajos en progreso
                    await self._check_running_jobs(db)
                    
                finally:
                    db.close()
                
                # Esperar antes del siguiente ciclo
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"❌ Error en queue loop: {e}")
                await asyncio.sleep(30)
    
    async def get_next_job(self, db: Session) -> Optional[Job]:
        """Obtener siguiente trabajo de la cola por prioridad"""
        job = db.query(Job).filter(
            Job.status == JobStatus.PENDING
        ).order_by(
            Job.priority.desc(),
            Job.created_at.asc()
        ).first()
        
        return job
    
    async def assign_node(self, job: Job, db: Session) -> Optional[Node]:
        """Asignar nodo disponible a un trabajo"""
        # Buscar nodo con capacidad
        node = db.query(Node).filter(
            Node.is_available == True,
            Node.status == "online",
            Node.current_jobs < Node.max_concurrent_jobs
        ).order_by(
            Node.current_jobs.asc(),  # Preferir nodos con menos carga
            Node.cpu_usage.asc()      # Luego por uso de CPU
        ).first()
        
        if node:
            # Verificar que el nodo soporte el motor de render
            if (job.engine and 
                node.supported_engines and 
                job.engine not in node.supported_engines):
                print(f"⚠️ Nodo {node.name} no soporta motor {job.engine}")
                return None
        
        return node
    
    async def start_job(self, job: Job, node: Node, db: Session):
        """Iniciar trabajo en un nodo"""
        try:
            # Actualizar estado del trabajo
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.assigned_node_id = node.id
            
            # Actualizar estado del nodo
            node.current_jobs += 1
            node.status = "busy" if node.current_jobs >= node.max_concurrent_jobs else "online"
            
            # Guardar en la base de datos
            db.commit()
            
            # Registrar asignación
            self.assigned_jobs[job.id] = node.id
            
            print(f"▶️ Trabajo {job.name} iniciado en nodo {node.name}")
            
            # TODO: Enviar comando al nodo para iniciar render
            # await self._send_render_command(job, node)
            
        except Exception as e:
            print(f"❌ Error al iniciar trabajo {job.id}: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
    
    async def _check_running_jobs(self, db: Session):
        """Verificar estado de trabajos en ejecución"""
        running_jobs = db.query(Job).filter(
            Job.status == JobStatus.RUNNING
        ).all()
        
        for job in running_jobs:
            # TODO: Verificar estado real del trabajo en el nodo
            # Por ahora, simular progreso
            if job.progress < 100:
                job.progress = min(job.progress + 5, 100)
                if job.progress >= 100:
                    await self._complete_job(job, db)
        
        if running_jobs:
            db.commit()
    
    async def _complete_job(self, job: Job, db: Session):
        """Marcar trabajo como completado"""
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.progress = 100
        
        # Liberar nodo
        if job.assigned_node_id:
            node = db.query(Node).filter(Node.id == job.assigned_node_id).first()
            if node:
                node.current_jobs = max(0, node.current_jobs - 1)
                node.total_jobs_completed += 1
                
                # Actualizar tiempo promedio
                if job.started_at and job.completed_at:
                    job_duration = (job.completed_at - job.started_at).total_seconds()
                    if node.average_job_time == 0:
                        node.average_job_time = job_duration
                    else:
                        # Media móvil simple
                        node.average_job_time = (node.average_job_time + job_duration) / 2
                
                if node.current_jobs == 0:
                    node.status = "online"
        
        # Remover de trabajos asignados
        if job.id in self.assigned_jobs:
            del self.assigned_jobs[job.id]
        
        print(f"✅ Trabajo {job.name} completado")
        
        # TODO: Enviar notificación
        # await self._send_completion_notification(job)

        
# Instancia global del queue manager
queue_manager = QueueManager()