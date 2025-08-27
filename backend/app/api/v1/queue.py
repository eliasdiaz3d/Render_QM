"""
API endpoints para gestión de cola de trabajos
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

# Importar funciones específicas de tu base de datos en memoria
from ...core.database import (
    get_queue_statistics,
    get_jobs_by_status,
    distributed_job_queue,
    jobs_db,
    add_job_to_queue,
    get_next_job_from_queue,
    assign_job_to_node,
    get_available_nodes
)

router = APIRouter()

@router.get("/status")
async def get_queue_status():
    """Obtener estado actual de la cola de render"""
    try:
        # Usar tu función existente para obtener estadísticas
        stats = get_queue_statistics()
        
        # Agregar información adicional
        stats.update({
            "queue_items": len(distributed_job_queue),
            "active_jobs": len([job for job in jobs_db.values() if job["status"] == "processing"]),
            "available_nodes": len(get_available_nodes())
        })
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado de cola: {str(e)}"
        )

@router.get("/jobs")
async def get_queue_jobs():
    """Obtener trabajos en la cola"""
    try:
        # Obtener trabajos pendientes
        pending_jobs = get_jobs_by_status("pending")
        processing_jobs = get_jobs_by_status("processing")
        
        return {
            "pending": pending_jobs,
            "processing": processing_jobs,
            "queue_order": distributed_job_queue.copy()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo trabajos: {str(e)}"
        )

@router.post("/jobs/{job_id}/priority")
async def change_job_priority(job_id: str, priority: str):
    """Cambiar prioridad de un trabajo en cola"""
    try:
        if job_id not in jobs_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trabajo no encontrado"
            )
        
        job = jobs_db[job_id]
        if job["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se puede cambiar prioridad de trabajos pendientes"
            )
        
        # Actualizar prioridad en la base de datos
        job["priority"] = priority
        
        # Reorganizar en la cola si está en ella
        if job_id in distributed_job_queue:
            distributed_job_queue.remove(job_id)
            add_job_to_queue(job_id, priority)
        
        return {"message": f"Prioridad cambiada a {priority}", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cambiando prioridad: {str(e)}"
        )

@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancelar trabajo en cola"""
    try:
        if job_id not in jobs_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trabajo no encontrado"
            )
        
        job = jobs_db[job_id]
        
        if job["status"] == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cancelar un trabajo completado"
            )
        
        # Actualizar estado
        job["status"] = "cancelled"
        
        # Remover de cola si está ahí
        if job_id in distributed_job_queue:
            distributed_job_queue.remove(job_id)
        
        return {"message": "Trabajo cancelado", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelando trabajo: {str(e)}"
        )

@router.post("/process")
async def process_queue():
    """Procesar siguiente trabajo en cola"""
    try:
        # Obtener nodos disponibles
        available_nodes = get_available_nodes()
        
        if not available_nodes:
            return {"message": "No hay nodos disponibles", "assigned": False}
        
        # Obtener siguiente trabajo
        job_id = get_next_job_from_queue()
        
        if not job_id:
            return {"message": "No hay trabajos en cola", "assigned": False}
        
        # Asignar al primer nodo disponible
        node = available_nodes[0]
        success = assign_job_to_node(job_id, node["node_id"])
        
        if success:
            return {
                "message": "Trabajo asignado",
                "job_id": job_id,
                "node_id": node["node_id"],
                "assigned": True
            }
        else:
            # Devolver trabajo a cola si falló la asignación
            add_job_to_queue(job_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error asignando trabajo a nodo"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando cola: {str(e)}"
        )

@router.get("/metrics")
async def get_queue_metrics():
    """Obtener métricas detalladas de la cola"""
    try:
        # Obtener estadísticas básicas
        stats = get_queue_statistics()
        
        # Calcular métricas adicionales
        all_jobs = list(jobs_db.values())
        total_jobs_today = len([job for job in all_jobs 
                               if job["created_at"] and 
                               job["created_at"].date() == __import__('datetime').datetime.now().date()])
        
        # Distribución por prioridad
        priority_distribution = {}
        for job in all_jobs:
            priority = job.get("priority", "normal")
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        return {
            **stats,
            "jobs_created_today": total_jobs_today,
            "priority_distribution": priority_distribution,
            "average_queue_wait_time": "N/A",  # Implementar si necesitas
            "estimated_completion_time": "N/A"  # Implementar si necesitas
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo métricas: {str(e)}"
        )

@router.post("/clear")
async def clear_completed_jobs():
    """Limpiar trabajos completados de la cola"""
    try:
        completed_jobs = [job_id for job_id, job in jobs_db.items() 
                         if job["status"] in ["completed", "failed", "cancelled"]]
        
        # En un sistema real, moverías estos a un archivo de historial
        # Por ahora solo los marcamos como archivados
        for job_id in completed_jobs:
            if job_id in jobs_db:
                jobs_db[job_id]["archived"] = True
        
        return {
            "message": f"Se marcaron {len(completed_jobs)} trabajos como archivados",
            "archived_count": len(completed_jobs)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error limpiando cola: {str(e)}"
        )