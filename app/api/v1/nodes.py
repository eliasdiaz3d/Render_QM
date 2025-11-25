# app/api/v1/nodes.py - Endpoints para gestión de nodos distribuidos
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from app.models.node import (
    NodeRegistration, NodeHeartbeat, NodeResponse, NodeUpdate,
    NodeFilter, NodeSearch, NodesOverview, NodeDiagnostic
)
from app.core.database import (
    nodes_registry, register_node, update_node_heartbeat,
    get_available_nodes, cleanup_offline_nodes, jobs_db,
    job_assignments, distributed_job_queue, get_next_job_from_queue,
    assign_job_to_node
)

router = APIRouter()

# ==================== ENDPOINTS DE REGISTRO ====================

@router.post("/nodes/register")
async def register_node_endpoint(node_data: NodeRegistration):
    """Registrar un nuevo nodo de render"""
    try:
        # Generar ID único para el nodo
        import hashlib
        import platform
        
        # Usar información del nodo para generar ID consistente
        node_string = f"{node_data.node_info.hostname}-{node_data.node_info.processor}"
        node_id = hashlib.md5(node_string.encode()).hexdigest()[:16]
        
        # Preparar datos del nodo
        registration_data = {
            "node_id": node_id,
            "node_name": node_data.node_name or f"Node-{node_id[:8]}",
            "system_stats": node_data.system_stats.dict(),
            "node_info": node_data.node_info.dict(),
            "capabilities": node_data.capabilities.dict(),
            "tags": node_data.tags
        }
        
        # Registrar nodo
        success = register_node(registration_data)
        
        if success:
            return {
                "message": "Nodo registrado exitosamente",
                "node_id": node_id,
                "node_name": registration_data["node_name"],
                "assigned_jobs": 0,
                "server_time": datetime.now().isoformat(),
                "heartbeat_interval": 10,
                "next_heartbeat": (datetime.now() + timedelta(seconds=10)).isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Error consultando trabajo para nodo {node_id}: {str(e)}")

@router.get("/jobs/{job_id}/download-blend")
async def download_blend_file(job_id: str):
    """Descargar archivo .blend de un trabajo para un nodo"""
    from fastapi.responses import FileResponse
    
    try:
        if job_id not in jobs_db:
            raise HTTPException(status_code=404, detail="Trabajo no encontrado")
        
        job = jobs_db[job_id]
        blend_file_path = job["file_path"]
        
        if not os.path.exists(blend_file_path):
            raise HTTPException(status_code=404, detail="Archivo .blend no encontrado")
        
        return FileResponse(
            path=blend_file_path,
            filename=f"{job_id}.blend",
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error descargando .blend para {job_id}: {str(e)}")

@router.post("/jobs/{job_id}/upload-result")
async def upload_result_file(job_id: str, file: UploadFile = File(...)):
    """Subir archivo de resultado de un nodo"""
    from fastapi import UploadFile, File
    from app.core.config import settings
    import shutil
    
    try:
        if job_id not in jobs_db:
            raise HTTPException(status_code=404, detail="Trabajo no encontrado")
        
        job = jobs_db[job_id]
        
        # Crear directorio de resultados si no existe
        output_dir = settings.OUTPUT_DIR / job_id
        output_dir.mkdir(exist_ok=True)
        
        # Guardar archivo subido
        file_path = output_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Añadir a la lista de archivos de salida
        if "output_files" not in job:
            job["output_files"] = []
        job["output_files"].append(str(file_path))
        
        return {
            "message": "Archivo subido exitosamente",
            "filename": file.filename,
            "file_size": file_path.stat().st_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo resultado para {job_id}: {str(e)}")

# ==================== ENDPOINTS DE CONSULTA ====================

@router.get("/nodes/status", response_model=Dict[str, Any])
async def get_all_nodes_status():
    """Obtener estado de todos los nodos registrados"""
    try:
        # Limpiar nodos offline
        cleanup_offline_nodes()
        
        nodes_status = []
        for node_id, node_info in nodes_registry.items():
            # Calcular uptime
            last_seen = node_info.get("last_seen", datetime.now())
            uptime = datetime.now() - last_seen
            
            # Obtener trabajos asignados a este nodo
            assigned_jobs = [job_id for job_id, assignment in job_assignments.items() 
                           if assignment.get("node_id") == node_id]
            
            nodes_status.append({
                "node_id": node_id,
                "node_name": node_info.get("node_name", f"Node-{node_id[:8]}"),
                "status": node_info.get("status", "unknown"),
                "last_seen": last_seen.isoformat(),
                "uptime_seconds": abs(uptime.total_seconds()),
                "system_stats": node_info.get("system_stats", {}),
                "active_jobs": node_info.get("active_jobs", 0),
                "assigned_jobs": assigned_jobs,
                "capabilities": node_info.get("capabilities", {}),
                "node_info": node_info.get("node_info", {}),
                "tags": node_info.get("tags", [])
            })
        
        # Estadísticas generales
        total_nodes = len(nodes_status)
        online_nodes = len([n for n in nodes_status if n["status"] in ["idle", "busy"]])
        busy_nodes = len([n for n in nodes_status if n["status"] == "busy"])
        offline_nodes = len([n for n in nodes_status if n["status"] == "offline"])
        
        return {
            "nodes": nodes_status,
            "summary": {
                "total_nodes": total_nodes,
                "online_nodes": online_nodes,
                "busy_nodes": busy_nodes,
                "idle_nodes": online_nodes - busy_nodes,
                "offline_nodes": offline_nodes,
                "utilization_percent": round((busy_nodes / online_nodes * 100) if online_nodes > 0 else 0, 1)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado de nodos: {str(e)}")

@router.get("/nodes/{node_id}", response_model=NodeResponse)
async def get_node_details(node_id: str):
    """Obtener detalles de un nodo específico"""
    if node_id not in nodes_registry:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    
    node_info = nodes_registry[node_id]
    
    # Calcular estadísticas del nodo
    assigned_jobs = [job_id for job_id, assignment in job_assignments.items() 
                    if assignment.get("node_id") == node_id]
    
    # Calcular eficiencia (simplificado)
    total_completed = node_info.get("total_jobs_completed", 0)
    total_failed = node_info.get("total_jobs_failed", 0)
    efficiency = 100.0
    if total_completed + total_failed > 0:
        efficiency = (total_completed / (total_completed + total_failed)) * 100
    
    return NodeResponse(
        node_id=node_id,
        node_name=node_info.get("node_name", f"Node-{node_id[:8]}"),
        status=node_info.get("status", "unknown"),
        last_seen=node_info.get("last_seen", datetime.now()),
        registered_at=node_info.get("registered_at", datetime.now()),
        system_stats=node_info.get("system_stats", {}),
        node_info=node_info.get("node_info", {}),
        capabilities=node_info.get("capabilities", {}),
        active_jobs=node_info.get("active_jobs", 0),
        total_jobs_completed=total_completed,
        total_jobs_failed=total_failed,
        total_render_time_seconds=node_info.get("total_render_time", 0.0),
        tags=node_info.get("tags", []),
        assigned_jobs=assigned_jobs,
        efficiency_score=efficiency
    )

@router.post("/nodes/search")
async def search_nodes_endpoint(search_params: NodeSearch):
    """Buscar nodos con filtros"""
    try:
        nodes = list(nodes_registry.values())
        
        # Aplicar filtros de búsqueda
        if search_params.query:
            query_lower = search_params.query.lower()
            nodes = [n for n in nodes if 
                    query_lower in n.get("node_name", "").lower() or
                    query_lower in n.get("node_info", {}).get("hostname", "").lower()]
        
        # Aplicar filtros específicos
        if search_params.filters:
            if search_params.filters.status:
                nodes = [n for n in nodes if n.get("status") in search_params.filters.status]
            
            if search_params.filters.tags:
                nodes = [n for n in nodes if 
                        any(tag in n.get("tags", []) for tag in search_params.filters.tags)]
            
            if search_params.filters.gpu_available is not None:
                nodes = [n for n in nodes if 
                        n.get("capabilities", {}).get("gpu_rendering", False) == search_params.filters.gpu_available]
        
        # Filtrar offline si no se especifica incluirlos
        if not search_params.include_offline:
            nodes = [n for n in nodes if n.get("status") != "offline"]
        
        # Ordenar
        reverse = search_params.sort_order == "desc"
        if search_params.sort_by == "efficiency_score":
            nodes.sort(key=lambda x: x.get("efficiency_score", 0), reverse=reverse)
        else:
            nodes.sort(key=lambda x: x.get(search_params.sort_by, ""), reverse=reverse)
        
        return {
            "nodes": nodes,
            "total": len(nodes),
            "filters_applied": search_params.filters is not None,
            "query": search_params.query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando nodos: {str(e)}")

# ==================== ENDPOINTS DE GESTIÓN ====================

@router.put("/nodes/{node_id}")
async def update_node_endpoint(node_id: str, node_update: NodeUpdate):
    """Actualizar configuración de un nodo"""
    if node_id not in nodes_registry:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    
    try:
        node_info = nodes_registry[node_id]
        
        # Aplicar actualizaciones
        updates = node_update.dict(exclude_unset=True)
        
        for key, value in updates.items():
            if key == "capabilities":
                node_info.setdefault("capabilities", {}).update(value)
            else:
                node_info[key] = value
        
        return {
            "message": f"Nodo {node_id} actualizado exitosamente",
            "updated_fields": list(updates.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando nodo: {str(e)}")

@router.delete("/nodes/{node_id}")
async def unregister_node(node_id: str):
    """Des-registrar un nodo"""
    if node_id not in nodes_registry:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    
    try:
        # Reasignar trabajos activos del nodo
        orphaned_jobs = [job_id for job_id, assignment in job_assignments.items() 
                        if assignment.get("node_id") == node_id]
        
        for job_id in orphaned_jobs:
            # Volver a poner en cola
            distributed_job_queue.append(job_id)
            if job_id in jobs_db:
                jobs_db[job_id]["status"] = "pending"
            if job_id in job_assignments:
                del job_assignments[job_id]
        
        # Remover nodo
        node_name = nodes_registry[node_id].get("node_name", f"Node-{node_id[:8]}")
        del nodes_registry[node_id]
        
        return {
            "message": f"Nodo {node_name} des-registrado exitosamente",
            "reassigned_jobs": len(orphaned_jobs),
            "orphaned_job_ids": orphaned_jobs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error des-registrando nodo {node_id}: {str(e)}")

@router.post("/nodes/{node_id}/maintenance")
async def set_node_maintenance(node_id: str, enable: bool = Query(True)):
    """Poner un nodo en modo mantenimiento"""
    if node_id not in nodes_registry:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    
    try:
        node_info = nodes_registry[node_id]
        
        if enable:
            # Activar mantenimiento
            node_info["status"] = "maintenance"
            
            # Reasignar trabajos activos
            orphaned_jobs = [job_id for job_id, assignment in job_assignments.items() 
                            if assignment.get("node_id") == node_id]
            
            for job_id in orphaned_jobs:
                distributed_job_queue.append(job_id)
                if job_id in jobs_db:
                    jobs_db[job_id]["status"] = "pending"
                if job_id in job_assignments:
                    del job_assignments[job_id]
            
            message = f"Nodo {node_id} en modo mantenimiento"
            if orphaned_jobs:
                message += f". {len(orphaned_jobs)} trabajos reasignados"
        
        else:
            # Desactivar mantenimiento
            node_info["status"] = "idle"
            message = f"Nodo {node_id} fuera de mantenimiento"
        
        return {
            "message": message,
            "maintenance_mode": enable,
            "reassigned_jobs": len(orphaned_jobs) if enable else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configurando mantenimiento: {str(e)}")

# ==================== ENDPOINTS DE ESTADÍSTICAS ====================

@router.get("/nodes/overview", response_model=NodesOverview)
async def get_nodes_overview():
    """Obtener vista general de todos los nodos"""
    try:
        cleanup_offline_nodes()
        
        nodes = list(nodes_registry.values())
        
        # Contar por estado
        total_nodes = len(nodes)
        online_nodes = len([n for n in nodes if n.get("status") in ["idle", "busy"]])
        busy_nodes = len([n for n in nodes if n.get("status") == "busy"])
        idle_nodes = online_nodes - busy_nodes
        offline_nodes = len([n for n in nodes if n.get("status") == "offline"])
        error_nodes = len([n for n in nodes if n.get("status") == "error"])
        maintenance_nodes = len([n for n in nodes if n.get("status") == "maintenance"])
        
        # Calcular capacidad
        total_capacity = sum([n.get("capabilities", {}).get("concurrent_jobs", 1) 
                             for n in nodes if n.get("status") in ["idle", "busy"]])
        current_load = sum([n.get("active_jobs", 0) for n in nodes])
        
        # Calcular eficiencia promedio
        efficiencies = []
        for node in nodes:
            completed = node.get("total_jobs_completed", 0)
            failed = node.get("total_jobs_failed", 0)
            if completed + failed > 0:
                efficiency = (completed / (completed + failed)) * 100
                efficiencies.append(efficiency)
        
        average_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else 100.0
        
        return NodesOverview(
            total_nodes=total_nodes,
            online_nodes=online_nodes,
            busy_nodes=busy_nodes,
            idle_nodes=idle_nodes,
            offline_nodes=offline_nodes,
            error_nodes=error_nodes,
            maintenance_nodes=maintenance_nodes,
            total_capacity=total_capacity,
            current_load=current_load,
            utilization_percent=round((current_load / total_capacity * 100) if total_capacity > 0 else 0, 1),
            average_efficiency=round(average_efficiency, 1)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo overview de nodos: {str(e)}")

@router.get("/nodes/{node_id}/diagnostic")
async def diagnose_node(node_id: str):
    """Ejecutar diagnóstico de un nodo específico"""
    if node_id not in nodes_registry:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    
    try:
        node_info = nodes_registry[node_id]
        
        # Realizar checks básicos
        checks = {}
        recommendations = []
        warnings = []
        errors = []
        
        # Check de conectividad
        last_seen = node_info.get("last_seen", datetime.min)
        time_since_last_seen = datetime.now() - last_seen
        
        if time_since_last_seen.total_seconds() > 60:
            checks["connectivity"] = {
                "status": "warning",
                "message": f"No se ha visto en {int(time_since_last_seen.total_seconds())} segundos",
                "last_seen": last_seen.isoformat()
            }
            warnings.append("Conectividad irregular")
        else:
            checks["connectivity"] = {
                "status": "healthy",
                "message": "Conectividad normal",
                "last_seen": last_seen.isoformat()
            }
        
        # Check de recursos
        system_stats = node_info.get("system_stats", {})
        memory_usage = system_stats.get("memory_percent", 0)
        cpu_usage = system_stats.get("cpu_percent", 0)
        
        if memory_usage > 90:
            checks["memory"] = {
                "status": "critical",
                "message": f"Memoria muy alta: {memory_usage}%",
                "value": memory_usage
            }
            errors.append("Memoria crítica")
        elif memory_usage > 80:
            checks["memory"] = {
                "status": "warning", 
                "message": f"Memoria alta: {memory_usage}%",
                "value": memory_usage
            }
            warnings.append("Memoria alta")
        else:
            checks["memory"] = {
                "status": "healthy",
                "message": f"Memoria normal: {memory_usage}%",
                "value": memory_usage
            }
        
        # Check de trabajos
        active_jobs = node_info.get("active_jobs", 0)
        max_jobs = node_info.get("capabilities", {}).get("concurrent_jobs", 1)
        
        if active_jobs >= max_jobs:
            checks["workload"] = {
                "status": "busy",
                "message": f"Carga completa: {active_jobs}/{max_jobs}",
                "active_jobs": active_jobs,
                "max_jobs": max_jobs
            }
        else:
            checks["workload"] = {
                "status": "healthy",
                "message": f"Carga normal: {active_jobs}/{max_jobs}",
                "active_jobs": active_jobs,
                "max_jobs": max_jobs
            }
        
        # Determinar salud general
        if errors:
            overall_health = "critical"
        elif warnings:
            overall_health = "warning"
        else:
            overall_health = "healthy"
        
        # Generar recomendaciones
        if memory_usage > 80:
            recommendations.append("Considerar aumentar memoria RAM o reducir trabajos concurrentes")
        
        if cpu_usage > 90:
            recommendations.append("CPU sobrecargada, considerar reducir carga de trabajo")
        
        if time_since_last_seen.total_seconds() > 300:
            recommendations.append("Verificar conectividad de red del nodo")
        
        return NodeDiagnostic(
            node_id=node_id,
            timestamp=datetime.now(),
            overall_health=overall_health,
            checks=checks,
            recommendations=recommendations,
            warnings=warnings,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error diagnosticando nodo: {str(e)}")

# ==================== ENDPOINTS DE COLA DISTRIBUIDA ====================

@router.get("/queue/distributed-status")
async def get_distributed_queue_status():
    """Obtener estado de la cola distribuida"""
    try:
        from app.core.database import get_queue_statistics, get_nodes_statistics
        
        # Estadísticas de trabajos
        queue_stats = get_queue_statistics()
        
        # Estadísticas de nodos  
        node_stats = get_nodes_statistics()
        
        # Actividad reciente
        recent_jobs = [j for j in jobs_db.values() if 
                      j.get("completed_at") and 
                      (datetime.now() - j["completed_at"]).total_seconds() < 3600]
        
        return {
            "queue_stats": queue_stats,
            "node_stats": node_stats,
            "recent_activity": {
                "jobs_completed_last_hour": len(recent_jobs),
                "queue_length": len(distributed_job_queue),
                "active_assignments": len(job_assignments),
                "efficiency_score": round(queue_stats.get("success_rate", 100), 1)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado de cola distribuida: {str(e)}")

# ==================== ENDPOINTS DE MANTENIMIENTO ====================

@router.post("/nodes/cleanup")
async def cleanup_nodes():
    """Limpiar nodos offline y datos obsoletos"""
    try:
        offline_nodes = cleanup_offline_nodes()
        
        return {
            "message": "Limpieza de nodos completada",
            "offline_nodes_found": len(offline_nodes),
            "offline_node_ids": offline_nodes,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en limpieza de nodos: {str(e)}"="Error registrando nodo")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registrando nodo: {str(e)}")

@router.post("/nodes/heartbeat")
async def node_heartbeat_endpoint(heartbeat_data: NodeHeartbeat):
    """Recibir heartbeat de un nodo"""
    try:
        # Extraer node_id del contexto o parámetros
        # Por ahora, asumimos que viene en el cuerpo de la petición
        node_id = getattr(heartbeat_data, 'node_id', None)
        
        if not node_id:
            raise HTTPException(status_code=400, detail="node_id requerido")
        
        if node_id not in nodes_registry:
            raise HTTPException(status_code=404, detail="Nodo no registrado")
        
        # Preparar datos del heartbeat
        heartbeat_dict = {
            "status": heartbeat_data.status,
            "system_stats": heartbeat_data.system_stats.dict(),
            "active_jobs": heartbeat_data.active_jobs,
            "errors": heartbeat_data.errors,
            "warnings": heartbeat_data.warnings,
            "uptime_seconds": heartbeat_data.uptime_seconds
        }
        
        # Actualizar heartbeat
        success = update_node_heartbeat(node_id, heartbeat_dict)
        
        if success:
            # Procesar estados de trabajos reportados
            job_statuses = heartbeat_data.job_statuses
            for job_id, job_status in job_statuses.items():
                if job_id in jobs_db:
                    # Actualizar estado del trabajo
                    jobs_db[job_id]["status"] = job_status.get("status", "processing")
                    jobs_db[job_id]["progress"] = job_status.get("progress", 0)
                    jobs_db[job_id]["frames_rendered"] = job_status.get("frames_rendered", 0)
                    
                    # Si se completó, manejar finalización
                    if job_status.get("status") == "completed":
                        jobs_db[job_id]["completed_at"] = datetime.now()
                        jobs_db[job_id]["output_files"] = job_status.get("output_files", [])
                        
                        # Remover de asignaciones
                        if job_id in job_assignments:
                            del job_assignments[job_id]
                    
                    elif job_status.get("status") == "failed":
                        jobs_db[job_id]["error_message"] = job_status.get("error_message", "Error desconocido")
                        jobs_db[job_id]["completed_at"] = datetime.now()
                        
                        # Remover de asignaciones
                        if job_id in job_assignments:
                            del job_assignments[job_id]
            
            return {
                "message": "Heartbeat recibido",
                "server_time": datetime.now().isoformat(),
                "next_heartbeat": (datetime.now() + timedelta(seconds=10)).isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Error procesando heartbeat")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando heartbeat: {str(e)}")

# ==================== ENDPOINTS DE ASIGNACIÓN DE TRABAJOS ====================

@router.get("/nodes/{node_id}/poll-job")
async def poll_job_for_node(node_id: str):
    """Consultar si hay trabajos disponibles para un nodo"""
    try:
        if node_id not in nodes_registry:
            raise HTTPException(status_code=404, detail="Nodo no registrado")
        
        node_info = nodes_registry[node_id]
        
        # Verificar si el nodo puede tomar más trabajos
        max_jobs = node_info.get("capabilities", {}).get("concurrent_jobs", 1)
        if node_info.get("active_jobs", 0) >= max_jobs:
            return None  # Nodo ocupado
        
        # Limpiar nodos offline antes de asignar trabajos
        cleanup_offline_nodes()
        
        # Obtener siguiente trabajo de la cola
        job_id = get_next_job_from_queue()
        
        if job_id:
            # Asignar trabajo al nodo
            success = assign_job_to_node(job_id, node_id)
            
            if success:
                job_data = jobs_db.get(job_id)
                return {
                    "job_id": job_id,
                    "job_data": job_data
                }
        
        # No hay trabajos disponibles
        return None
        
    except Exception as e:
        raise HTTPException(status_code=500, detail