# app/core/database.py - Base de datos en memoria para el sistema
from typing import Dict, Any, List
from datetime import datetime
import platform
import logging

logger = logging.getLogger(__name__)

# ==================== BASES DE DATOS EN MEMORIA ====================

# Base de datos principal de trabajos de render
jobs_db: Dict[str, Dict[str, Any]] = {}

# Base de datos de nodos (local + distribuidos)
nodes_db: Dict[str, Dict[str, Any]] = {
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

# Registro de nodos distribuidos
nodes_registry: Dict[str, Any] = {}

# Sesiones de upload por chunks
upload_sessions: Dict[str, Dict[str, Any]] = {}

# Cola distribuida de trabajos
distributed_job_queue: List[str] = []

# Asignaciones de trabajos a nodos
job_assignments: Dict[str, Dict[str, Any]] = {}

# Cache de archivos de trabajo
job_files_cache: Dict[str, Dict[str, Any]] = {}

# Estadísticas del sistema
system_stats: Dict[str, Any] = {
    "total_jobs_created": 0,
    "total_jobs_completed": 0,
    "total_jobs_failed": 0,
    "total_render_time": 0,
    "average_render_time": 0,
    "uptime": datetime.now(),
    "last_restart": datetime.now()
}

# ==================== FUNCIONES DE INICIALIZACIÓN ====================

def init_directories():
    """Inicializar directorios necesarios"""
    from app.core.config import settings
    
    directories = [settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.TEMP_DIR]
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Directorio inicializado: {directory}")
        except Exception as e:
            logger.error(f"❌ Error creando directorio {directory}: {e}")

def init_database():
    """Inicializar base de datos en memoria con valores por defecto"""
    global system_stats
    
    # Actualizar estadísticas de inicio
    system_stats["uptime"] = datetime.now()
    system_stats["last_restart"] = datetime.now()
    
    logger.info("🗄️ Base de datos en memoria inicializada")

# ==================== FUNCIONES DE GESTIÓN DE TRABAJOS ====================

def create_job(job_data: Dict[str, Any]) -> str:
    """Crear un nuevo trabajo en la base de datos"""
    import uuid
    
    job_id = str(uuid.uuid4())
    
    job = {
        "id": job_id,
        "name": job_data.get("name", "Trabajo sin nombre"),
        "status": "pending",
        "progress": 0,
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None,
        "file_path": job_data.get("file_path", ""),
        "original_filename": job_data.get("original_filename", ""),
        "output_path": None,
        "frame_start": job_data.get("frame_start", 1),
        "frame_end": job_data.get("frame_end", 1),
        "frames_total": (job_data.get("frame_end", 1) - job_data.get("frame_start", 1)) + 1,
        "frames_rendered": 0,
        "render_engine": job_data.get("render_engine", "CYCLES"),
        "estimated_time": job_data.get("estimated_time"),
        "error_message": None,
        "file_size": job_data.get("file_size", 0),
        "distribution_type": job_data.get("distribution_type", "local"),
        "priority": job_data.get("priority", "normal"),
        "tags": job_data.get("tags", []),
        "user_id": job_data.get("user_id", "default"),
        "render_settings": job_data.get("render_settings", {}),
        "output_files": []
    }
    
    jobs_db[job_id] = job
    system_stats["total_jobs_created"] += 1
    
    logger.info(f"✅ Trabajo creado: {job_id} ({job['name']})")
    return job_id

def get_job(job_id: str) -> Dict[str, Any]:
    """Obtener trabajo por ID"""
    return jobs_db.get(job_id)

def update_job(job_id: str, updates: Dict[str, Any]) -> bool:
    """Actualizar trabajo existente"""
    if job_id in jobs_db:
        jobs_db[job_id].update(updates)
        
        # Actualizar estadísticas globales
        if updates.get("status") == "completed":
            system_stats["total_jobs_completed"] += 1
        elif updates.get("status") == "failed":
            system_stats["total_jobs_failed"] += 1
        
        return True
    return False

def delete_job(job_id: str) -> bool:
    """Eliminar trabajo de la base de datos"""
    if job_id in jobs_db:
        # Limpiar archivos asociados
        import os
        import shutil
        from pathlib import Path
        
        job = jobs_db[job_id]
        
        try:
            # Eliminar archivo .blend
            if job.get("file_path") and os.path.exists(job["file_path"]):
                os.remove(job["file_path"])
            
            # Eliminar directorio de salida
            if job.get("output_path") and os.path.exists(job["output_path"]):
                shutil.rmtree(job["output_path"])
        except Exception as e:
            logger.warning(f"⚠️ Error limpiando archivos del trabajo {job_id}: {e}")
        
        # Remover de asignaciones si existe
        if job_id in job_assignments:
            del job_assignments[job_id]
        
        # Remover de cola distribuida si existe
        if job_id in distributed_job_queue:
            distributed_job_queue.remove(job_id)
        
        # Eliminar trabajo
        del jobs_db[job_id]
        logger.info(f"🗑️ Trabajo eliminado: {job_id}")
        return True
    
    return False

def get_jobs_by_status(status: str) -> List[Dict[str, Any]]:
    """Obtener trabajos por estado"""
    return [job for job in jobs_db.values() if job["status"] == status]

def get_jobs_by_user(user_id: str) -> List[Dict[str, Any]]:
    """Obtener trabajos de un usuario específico"""
    return [job for job in jobs_db.values() if job.get("user_id") == user_id]

# ==================== FUNCIONES DE GESTIÓN DE NODOS ====================

def register_node(node_data: Dict[str, Any]) -> bool:
    """Registrar un nuevo nodo"""
    node_id = node_data["node_id"]
    
    node_info = {
        "node_id": node_id,
        "node_name": node_data.get("node_name", f"Node-{node_id[:8]}"),
        "status": "idle",
        "last_seen": datetime.now(),
        "system_stats": node_data.get("system_stats", {}),
        "active_jobs": 0,
        "capabilities": node_data.get("capabilities", {}),
        "node_info": node_data.get("node_info", {}),
        "registered_at": datetime.now(),
        "total_jobs_completed": 0,
        "total_jobs_failed": 0,
        "total_render_time": 0,
        "tags": node_data.get("tags", [])
    }
    
    nodes_registry[node_id] = node_info
    logger.info(f"🔗 Nodo registrado: {node_id} ({node_info['node_name']})")
    return True

def update_node_heartbeat(node_id: str, heartbeat_data: Dict[str, Any]) -> bool:
    """Actualizar heartbeat de un nodo"""
    if node_id in nodes_registry:
        node_info = nodes_registry[node_id]
        node_info["status"] = heartbeat_data.get("status", "idle")
        node_info["last_seen"] = datetime.now()
        node_info["system_stats"] = heartbeat_data.get("system_stats", {})
        node_info["active_jobs"] = heartbeat_data.get("active_jobs", 0)
        return True
    return False

def get_available_nodes() -> List[Dict[str, Any]]:
    """Obtener nodos disponibles para asignar trabajos"""
    from datetime import timedelta
    
    available_nodes = []
    cutoff_time = datetime.now() - timedelta(seconds=30)
    
    for node_id, node_info in nodes_registry.items():
        if (node_info["status"] in ["idle", "busy"] and 
            node_info["last_seen"] > cutoff_time and
            node_info["active_jobs"] < node_info["capabilities"].get("concurrent_jobs", 1)):
            available_nodes.append(node_info)
    
    return available_nodes

def cleanup_offline_nodes() -> List[str]:
    """Limpiar nodos que están offline"""
    from datetime import timedelta
    
    offline_threshold = datetime.now() - timedelta(minutes=5)
    offline_nodes = []
    
    for node_id, node_info in nodes_registry.items():
        if node_info["last_seen"] < offline_threshold:
            offline_nodes.append(node_id)
    
    # Reasignar trabajos de nodos offline
    for node_id in offline_nodes:
        orphaned_jobs = [job_id for job_id, assignment in job_assignments.items() 
                        if assignment["node_id"] == node_id and assignment["status"] in ["assigned", "downloading", "rendering"]]
        
        for job_id in orphaned_jobs:
            distributed_job_queue.append(job_id)
            if job_id in jobs_db:
                jobs_db[job_id]["status"] = "pending"
            if job_id in job_assignments:
                del job_assignments[job_id]
            logger.info(f"🔄 Trabajo reasignado debido a nodo offline: {job_id}")
        
        # Marcar nodo como offline
        nodes_registry[node_id]["status"] = "offline"
    
    return offline_nodes

# ==================== FUNCIONES DE GESTIÓN DE COLA ====================

def add_job_to_queue(job_id: str, priority: str = "normal") -> bool:
    """Añadir trabajo a la cola distribuida"""
    if priority == "high":
        distributed_job_queue.insert(0, job_id)  # Alta prioridad al frente
    elif priority == "low":
        distributed_job_queue.append(job_id)     # Baja prioridad al final
    else:
        # Prioridad normal - insertar en posición media
        mid_point = len(distributed_job_queue) // 2
        distributed_job_queue.insert(mid_point, job_id)
    
    logger.info(f"📋 Trabajo añadido a cola: {job_id} (prioridad: {priority})")
    return True

def get_next_job_from_queue() -> str:
    """Obtener siguiente trabajo de la cola"""
    if distributed_job_queue:
        job_id = distributed_job_queue.pop(0)
        logger.info(f"📤 Trabajo extraído de cola: {job_id}")
        return job_id
    return None

def assign_job_to_node(job_id: str, node_id: str) -> bool:
    """Asignar trabajo a un nodo específico"""
    assignment = {
        "job_id": job_id,
        "node_id": node_id,
        "assigned_at": datetime.now(),
        "status": "assigned"
    }
    
    job_assignments[job_id] = assignment
    
    # Actualizar estado del trabajo
    if job_id in jobs_db:
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["started_at"] = datetime.now()
    
    # Incrementar contador de trabajos activos del nodo
    if node_id in nodes_registry:
        nodes_registry[node_id]["active_jobs"] += 1
    
    logger.info(f"🎯 Trabajo asignado: {job_id} → {node_id}")
    return True

# ==================== FUNCIONES DE GESTIÓN DE SESIONES ====================

def create_upload_session(session_data: Dict[str, Any]) -> str:
    """Crear sesión de upload por chunks"""
    import uuid
    
    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "filename": session_data["filename"],
        "total_size": session_data["total_size"],
        "total_chunks": session_data["total_chunks"],
        "file_hash": session_data["file_hash"],
        "uploaded_chunks": set(),
        "temp_dir": session_data["temp_dir"],
        "created_at": datetime.now(),
        "last_activity": datetime.now()
    }
    
    upload_sessions[session_id] = session
    logger.info(f"📡 Sesión de upload creada: {session_id}")
    return session_id

def update_upload_session(session_id: str, chunk_number: int) -> bool:
    """Actualizar progreso de sesión de upload"""
    if session_id in upload_sessions:
        session = upload_sessions[session_id]
        session["uploaded_chunks"].add(chunk_number)
        session["last_activity"] = datetime.now()
        return True
    return False

def cleanup_expired_sessions(max_age_hours: int = 1) -> List[str]:
    """Limpiar sesiones expiradas"""
    from datetime import timedelta
    import shutil
    from pathlib import Path
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    expired_sessions = []
    
    for session_id, session in list(upload_sessions.items()):
        if session["last_activity"] < cutoff_time:
            expired_sessions.append(session_id)
            
            # Limpiar archivos temporales
            try:
                temp_dir = Path(session["temp_dir"])
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"⚠️ Error limpiando sesión {session_id}: {e}")
            
            # Remover sesión
            del upload_sessions[session_id]
    
    if expired_sessions:
        logger.info(f"🧹 Sesiones expiradas limpiadas: {len(expired_sessions)}")
    
    return expired_sessions

# ==================== FUNCIONES DE ESTADÍSTICAS ====================

def get_queue_statistics() -> Dict[str, Any]:
    """Obtener estadísticas de la cola de render"""
    jobs = list(jobs_db.values())
    
    total_jobs = len(jobs)
    pending_jobs = len([j for j in jobs if j["status"] == "pending"])
    processing_jobs = len([j for j in jobs if j["status"] == "processing"])
    completed_jobs = len([j for j in jobs if j["status"] == "completed"])
    failed_jobs = len([j for j in jobs if j["status"] == "failed"])
    cancelled_jobs = len([j for j in jobs if j["status"] == "cancelled"])
    
    # Calcular tiempo promedio de render
    completed_with_time = [j for j in jobs if j["status"] == "completed" and j.get("started_at") and j.get("completed_at")]
    avg_render_time = 0
    if completed_with_time:
        total_time = sum([
            (j["completed_at"] - j["started_at"]).total_seconds() 
            for j in completed_with_time
        ])
        avg_render_time = total_time / len(completed_with_time)
    
    return {
        "total_jobs": total_jobs,
        "pending_jobs": pending_jobs,
        "processing_jobs": processing_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "cancelled_jobs": cancelled_jobs,
        "queue_length": len(distributed_job_queue),
        "average_render_time_seconds": avg_render_time,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        "queue_health": "healthy" if failed_jobs < total_jobs * 0.1 else "degraded"
    }

def get_nodes_statistics() -> Dict[str, Any]:
    """Obtener estadísticas de los nodos"""
    nodes = list(nodes_registry.values())
    
    total_nodes = len(nodes)
    online_nodes = len([n for n in nodes if n["status"] in ["idle", "busy"]])
    busy_nodes = len([n for n in nodes if n["status"] == "busy"])
    offline_nodes = len([n for n in nodes if n["status"] == "offline"])
    
    # Capacidad total de rendering
    total_capacity = sum([n["capabilities"].get("concurrent_jobs", 1) for n in nodes if n["status"] in ["idle", "busy"]])
    current_load = sum([n["active_jobs"] for n in nodes])
    
    return {
        "total_nodes": total_nodes,
        "online_nodes": online_nodes,
        "busy_nodes": busy_nodes,
        "offline_nodes": offline_nodes,
        "total_capacity": total_capacity,
        "current_load": current_load,
        "utilization_percent": round((current_load / total_capacity * 100) if total_capacity > 0 else 0, 1),
        "available_slots": max(0, total_capacity - current_load)
    }

def get_system_statistics() -> Dict[str, Any]:
    """Obtener estadísticas generales del sistema"""
    uptime_seconds = (datetime.now() - system_stats["uptime"]).total_seconds()
    
    return {
        "uptime_seconds": uptime_seconds,
        "uptime_human": format_duration(uptime_seconds),
        "last_restart": system_stats["last_restart"],
        "total_jobs_created": system_stats["total_jobs_created"],
        "total_jobs_completed": system_stats["total_jobs_completed"],
        "total_jobs_failed": system_stats["total_jobs_failed"],
        "active_upload_sessions": len(upload_sessions),
        "active_job_assignments": len(job_assignments),
        "queue_length": len(distributed_job_queue)
    }

def format_duration(seconds: float) -> str:
    """Formatear duración en formato legible"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

# ==================== FUNCIONES DE BACKUP Y RESTAURACIÓN ====================

def export_database_state() -> Dict[str, Any]:
    """Exportar estado actual de la base de datos"""
    return {
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "jobs": {job_id: {**job, "created_at": job["created_at"].isoformat() if job["created_at"] else None, 
                         "started_at": job["started_at"].isoformat() if job["started_at"] else None,
                         "completed_at": job["completed_at"].isoformat() if job["completed_at"] else None}
                for job_id, job in jobs_db.items()},
        "nodes_registry": {node_id: {**node, "last_seen": node["last_seen"].isoformat() if node["last_seen"] else None,
                                    "registered_at": node["registered_at"].isoformat() if node["registered_at"] else None}
                          for node_id, node in nodes_registry.items()},
        "distributed_job_queue": distributed_job_queue.copy(),
        "system_stats": {**system_stats, "uptime": system_stats["uptime"].isoformat() if system_stats["uptime"] else None,
                        "last_restart": system_stats["last_restart"].isoformat() if system_stats["last_restart"] else None}
    }

def import_database_state(state_data: Dict[str, Any]) -> bool:
    """Importar estado de la base de datos"""
    try:
        global jobs_db, nodes_registry, distributed_job_queue, system_stats
        
        # Restaurar trabajos
        if "jobs" in state_data:
            jobs_db.clear()
            for job_id, job_data in state_data["jobs"].items():
                # Convertir strings ISO de vuelta a datetime
                if job_data.get("created_at"):
                    job_data["created_at"] = datetime.fromisoformat(job_data["created_at"])
                if job_data.get("started_at"):
                    job_data["started_at"] = datetime.fromisoformat(job_data["started_at"])
                if job_data.get("completed_at"):
                    job_data["completed_at"] = datetime.fromisoformat(job_data["completed_at"])
                
                jobs_db[job_id] = job_data
        
        # Restaurar nodos (excepto el local)
        if "nodes_registry" in state_data:
            for node_id, node_data in state_data["nodes_registry"].items():
                if node_id != "local":  # Mantener nodo local actual
                    if node_data.get("last_seen"):
                        node_data["last_seen"] = datetime.fromisoformat(node_data["last_seen"])
                    if node_data.get("registered_at"):
                        node_data["registered_at"] = datetime.fromisoformat(node_data["registered_at"])
                    
                    nodes_registry[node_id] = node_data
        
        # Restaurar cola
        if "distributed_job_queue" in state_data:
            distributed_job_queue.clear()
            distributed_job_queue.extend(state_data["distributed_job_queue"])
        
        # Restaurar estadísticas
        if "system_stats" in state_data:
            stats = state_data["system_stats"]
            if stats.get("uptime"):
                stats["uptime"] = datetime.fromisoformat(stats["uptime"])
            if stats.get("last_restart"):
                stats["last_restart"] = datetime.fromisoformat(stats["last_restart"])
            
            system_stats.update(stats)
        
        logger.info("✅ Estado de base de datos restaurado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error restaurando estado de base de datos: {e}")
        return False

# ==================== FUNCIONES DE BÚSQUEDA Y FILTRADO ====================

def search_jobs(query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Buscar trabajos por criterios"""
    results = []
    
    for job in jobs_db.values():
        # Búsqueda por texto
        if query.lower() in job["name"].lower() or query.lower() in job.get("original_filename", "").lower():
            # Aplicar filtros adicionales
            if filters:
                if filters.get("status") and job["status"] != filters["status"]:
                    continue
                if filters.get("render_engine") and job["render_engine"] != filters["render_engine"]:
                    continue
                if filters.get("user_id") and job.get("user_id") != filters["user_id"]:
                    continue
            
            results.append(job)
    
    return results

def get_jobs_summary_by_date(days: int = 30) -> Dict[str, Any]:
    """Obtener resumen de trabajos por fecha"""
    from datetime import timedelta
    from collections import defaultdict
    
    cutoff_date = datetime.now() - timedelta(days=days)
    daily_stats = defaultdict(lambda: {"created": 0, "completed": 0, "failed": 0})
    
    for job in jobs_db.values():
        if job["created_at"] and job["created_at"] >= cutoff_date:
            date_key = job["created_at"].date().isoformat()
            daily_stats[date_key]["created"] += 1
            
            if job["status"] == "completed":
                daily_stats[date_key]["completed"] += 1
            elif job["status"] == "failed":
                daily_stats[date_key]["failed"] += 1
    
    return dict(daily_stats)

# ==================== FUNCIONES DE MANTENIMIENTO ====================

def cleanup_old_jobs(days: int = 7) -> List[str]:
    """Limpiar trabajos antiguos completados/fallidos"""
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    cleaned_jobs = []
    
    for job_id, job in list(jobs_db.items()):
        if (job["status"] in ["completed", "failed", "cancelled"] and 
            job.get("completed_at") and 
            job["completed_at"] < cutoff_date):
            
            if delete_job(job_id):
                cleaned_jobs.append(job_id)
    
    logger.info(f"🧹 Trabajos antiguos limpiados: {len(cleaned_jobs)}")
    return cleaned_jobs

def validate_database_integrity() -> Dict[str, Any]:
    """Validar integridad de la base de datos"""
    issues = []
    warnings = []
    
    # Validar trabajos
    for job_id, job in jobs_db.items():
        if not job.get("name"):
            issues.append(f"Trabajo {job_id} sin nombre")
        
        if not job.get("file_path"):
            issues.append(f"Trabajo {job_id} sin archivo")
        
        if job["frames_total"] <= 0:
            issues.append(f"Trabajo {job_id} con frames_total inválido")
    
    # Validar asignaciones huérfanas
    for job_id in job_assignments:
        if job_id not in jobs_db:
            issues.append(f"Asignación huérfana para trabajo inexistente: {job_id}")
    
    # Validar cola
    for job_id in distributed_job_queue:
        if job_id not in jobs_db:
            issues.append(f"Trabajo en cola inexistente: {job_id}")
        elif jobs_db[job_id]["status"] != "pending":
            warnings.append(f"Trabajo en cola con estado incorrecto: {job_id} ({jobs_db[job_id]['status']})")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "total_jobs": len(jobs_db),
        "total_nodes": len(nodes_registry),
        "queue_length": len(distributed_job_queue)
    }

# ==================== FUNCIÓN DE DEPENDENCIA PARA FASTAPI ====================

def get_db():
    """Función de dependencia para FastAPI - retorna el contexto de base de datos"""
    # Como usas base de datos en memoria, puedes retornar un objeto simple
    # que contenga referencias a las bases de datos globales
    return {
        "jobs_db": jobs_db,
        "nodes_db": nodes_db,
        "nodes_registry": nodes_registry,
        "upload_sessions": upload_sessions,
        "distributed_job_queue": distributed_job_queue,
        "job_assignments": job_assignments,
        "job_files_cache": job_files_cache,
        "system_stats": system_stats
    }

# ==================== COMPATIBILIDAD CON SQLALCHEMY ====================
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base para modelos SQLAlchemy (para compatibilidad)
Base = declarative_base()

# Engine para SQLAlchemy (base de datos en memoria SQLite)
engine = create_engine("sqlite:///:memory:", echo=False)

# SessionLocal para crear sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)